"""IP-4: 24-origin, select/confirm AutoGluon validation for target_3ay_hiz.

The reserved test origins are never scored.  Models are selected mechanically
on the first 12 origins and only then evaluated on the next 12 origins.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "birlesik_target_setleri" / "target_3ay_hiz_tum_featurelar_final.csv"
IP2_PATH = ROOT / "outputs" / "autogluon" / "ip2_medium" / "ip2_h3_tahminler.csv"
IP3_PATH = ROOT / "outputs" / "autogluon" / "ip3_medium" / "ip3_h3_tahminler.csv"
OUTPUT_DIR = ROOT / "outputs" / "autogluon" / "ip4_genis"
MODEL_ROOT = OUTPUT_DIR / "ag_models"

PREDICTIONS_PATH = OUTPUT_DIR / "ip4_h3_tahminler.csv"
RANKING_PATH = OUTPUT_DIR / "ip4_h3_siralama.csv"
PAIRED_PATH = OUTPUT_DIR / "ip4_paired_vs_t0.csv"
MCNEMAR_PATH = OUTPUT_DIR / "ip4_mcnemar_da.csv"
SELECTION_PATH = OUTPUT_DIR / "ip4_secim.txt"
DIAGNOSTIC_PATH = OUTPUT_DIR / "ip4_directtabular_tani.txt"
REPRO_PATH = OUTPUT_DIR / "ip4_reprodüksiyon.txt"
FIT_LOG_PATH = OUTPUT_DIR / "ip4_fit_log.txt"

ITEM_ID = "TR_otomobil"
TARGET = "target_3ay_hiz"
FREQ = "MS"
PREDICTION_LENGTH = 3
PRESET = "medium_quality"
TIME_LIMIT = 180

SELECT_START = pd.Timestamp("2023-04-01")
SELECT_END = pd.Timestamp("2024-03-01")
CONFIRM_START = pd.Timestamp("2024-04-01")
CONFIRM_END = pd.Timestamp("2025-03-01")
TEST_START = pd.Timestamp("2025-04-01")
TEST_END = pd.Timestamp("2026-03-01")

T1 = [
    "noter_devir_otomobil_adet",
    "osd_binek_adet",
    "otv_event_ay_mi",
]
T2 = T1 + [
    "indicata_satisa_donen_adet",
    "indicata_satis_ilan_orani_pct",
]
TIERS = {"T0": [], "T1": T1, "T2": T2}
BASELINES = {"sifir", "son12_ortalama"}


def log(message: str) -> None:
    print(message, flush=True)
    with FIT_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(message + "\n")


def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    required = {"referans_ayi", TARGET, *T2}
    missing = required.difference(data.columns)
    if missing:
        raise KeyError(f"Eksik zorunlu sütunlar: {sorted(missing)}")
    data["referans_ayi"] = pd.to_datetime(data["referans_ayi"], errors="raise")
    for column in [TARGET, *T2]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_values("referans_ayi").reset_index(drop=True)

    expected = pd.date_range(data.referans_ayi.min(), data.referans_ayi.max(), freq=FREQ)
    assert data.referans_ayi.equals(pd.Series(expected, name="referans_ayi"))
    assert not data.referans_ayi.duplicated().any()
    assert data[TARGET].notna().all()
    assert np.isfinite(data[TARGET].to_numpy()).all()
    assert len(data) == 97
    assert data[T1].notna().all().all()
    available = data.referans_ayi.ge("2023-01-01")
    assert data.loc[available, T2[3:]].notna().all().all()
    return data


def block_of(origin: pd.Timestamp) -> str:
    if SELECT_START <= origin <= SELECT_END:
        return "SELECT"
    if CONFIRM_START <= origin <= CONFIRM_END:
        return "CONFIRM"
    raise ValueError(f"Origin tanımlı blokta değil: {origin}")


def lagged_covariates(data: pd.DataFrame, features: list[str]) -> pd.DataFrame | None:
    if not features:
        return None
    table = data.set_index("referans_ayi")[features].copy()
    # T1/T2 contain no gaps over the period in which their lagged values are used.
    assert table.loc["2023-01-01":].notna().all().all()
    lagged = table.shift(PREDICTION_LENGTH)
    lagged.columns = [f"{name}_lag3" for name in lagged.columns]
    return lagged


def train_frame(
    data: pd.DataFrame,
    lagged: pd.DataFrame | None,
    origin: pd.Timestamp,
) -> TimeSeriesDataFrame:
    frame = data.set_index("referans_ayi")[[TARGET]].loc[:origin]
    if lagged is not None:
        frame = frame.join(lagged.loc[:origin], how="left")
    frame = frame.reset_index().rename(columns={"referans_ayi": "timestamp"})
    frame.insert(0, "item_id", ITEM_ID)
    tsdf = TimeSeriesDataFrame.from_data_frame(
        frame, id_column="item_id", timestamp_column="timestamp"
    )
    assert tsdf.freq == FREQ
    assert tsdf.index.get_level_values("timestamp").max() == origin
    return tsdf


def future_covariates(
    lagged: pd.DataFrame | None,
    origin: pd.Timestamp,
) -> TimeSeriesDataFrame | None:
    if lagged is None:
        return None
    months = pd.date_range(origin + pd.DateOffset(months=1), periods=3, freq=FREQ)
    future = lagged.loc[months].copy()
    assert not future.isna().any().any()
    for month in months:
        source_month = month - pd.DateOffset(months=3)
        assert source_month <= origin
        assert source_month >= pd.Timestamp("2023-01-01")
    future = future.reset_index(names="timestamp")
    future.insert(0, "item_id", ITEM_ID)
    return TimeSeriesDataFrame.from_data_frame(
        future, id_column="item_id", timestamp_column="timestamp"
    )


def q50(prediction: TimeSeriesDataFrame, month: pd.Timestamp) -> float:
    column = "0.5" if "0.5" in prediction.columns else 0.5
    if column not in prediction.columns:
        raise KeyError(f"Medyan tahmin sütunu yok: {prediction.columns.tolist()}")
    return float(prediction.loc[(ITEM_ID, month), column])


def run(data: pd.DataFrame) -> pd.DataFrame:
    origins = pd.date_range(SELECT_START, CONFIRM_END, freq=FREQ)
    assert len(origins) == 24
    assert origins[:12].min() == SELECT_START and origins[:12].max() == SELECT_END
    assert origins[12:].min() == CONFIRM_START and origins[12:].max() == CONFIRM_END
    assert origins.max() < TEST_START
    truth = data.set_index("referans_ayi")[TARGET]
    records: list[dict] = []

    for tier, features in TIERS.items():
        lagged = lagged_covariates(data, features)
        known_names = [] if lagged is None else lagged.columns.tolist()
        for number, origin in enumerate(origins, start=1):
            assert not TEST_START <= origin <= TEST_END
            target_month = origin + pd.DateOffset(months=3)
            train = train_frame(data, lagged, origin)
            future = future_covariates(lagged, origin)
            model_path = MODEL_ROOT / tier / f"origin_{origin:%Y%m}"
            if model_path.exists():
                raise FileExistsError(f"Model dizini zaten var: {model_path}")

            kwargs = dict(
                prediction_length=3,
                freq=FREQ,
                target=TARGET,
                eval_metric="MAE",
                eval_metric_seasonal_period=1,
                path=model_path,
                verbosity=1,
                log_to_file=True,
            )
            if known_names:
                kwargs["known_covariates_names"] = known_names
            predictor = TimeSeriesPredictor(**kwargs)
            log(
                f"{tier} {block_of(origin)} ORIGIN {number:02d}/24 {origin:%Y-%m} "
                f"target={target_month:%Y-%m} train_n={len(train)} known={known_names}"
            )
            started = time.perf_counter()
            predictor.fit(
                train_data=train,
                presets=PRESET,
                time_limit=TIME_LIMIT,
                random_seed=42,
                verbosity=1,
            )
            log(
                f"{tier} FIT_DONE {origin:%Y-%m} seconds="
                f"{time.perf_counter() - started:.2f} models={predictor.model_names()}"
            )
            actual = float(truth.loc[target_month])
            for model in predictor.model_names():
                prediction = predictor.predict(
                    train,
                    known_covariates=future,
                    model=model,
                    random_seed=42,
                )
                records.append(
                    {
                        "kol": tier,
                        "blok": block_of(origin),
                        "origin": origin,
                        "model": model,
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": q50(prediction, target_month),
                    }
                )
            history = truth.loc[:origin]
            for model, value in {
                "sifir": 0.0,
                "son12_ortalama": float(history.iloc[-12:].mean()),
            }.items():
                records.append(
                    {
                        "kol": tier,
                        "blok": block_of(origin),
                        "origin": origin,
                        "model": model,
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": value,
                    }
                )
            pd.DataFrame(records).to_csv(PREDICTIONS_PATH, index=False, encoding="utf-8-sig")

    predictions = pd.DataFrame(records)
    assert predictions.origin.min() == SELECT_START
    assert predictions.origin.max() == CONFIRM_END
    assert len(predictions.query("@TEST_START <= origin <= @TEST_END")) == 0
    assert predictions.groupby(["kol", "blok", "model"]).size().eq(12).all()
    return predictions


def add_errors(frame: pd.DataFrame) -> pd.DataFrame:
    scored = frame.copy()
    scored["abs_error"] = (scored.y_true - scored.y_pred_q50).abs()
    scored["sq_error"] = (scored.y_true - scored.y_pred_q50) ** 2
    scored["direction_correct"] = (
        scored.y_true.ne(0) & np.sign(scored.y_true).eq(np.sign(scored.y_pred_q50))
    ).astype(int)
    return scored


def ranking(scored: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for block, subset in [
        ("SELECT", scored[scored.blok.eq("SELECT")]),
        ("CONFIRM", scored[scored.blok.eq("CONFIRM")]),
        ("ALL", scored),
    ]:
        table = (
            subset.groupby(["kol", "model"])
            .agg(
                n=("y_true", "size"),
                MAE=("abs_error", "mean"),
                RMSE=("sq_error", lambda x: float(np.sqrt(x.mean()))),
                DA_yuzde=("direction_correct", lambda x: 100 * x.mean()),
            )
            .reset_index()
        )
        table.insert(1, "blok", block)
        frames.append(table)
    return pd.concat(frames, ignore_index=True).sort_values(["blok", "MAE", "kol", "model"])


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / (2**n)
    return min(1.0, 2 * tail)


def paired_and_mcnemar(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    reference = scored[
        scored.kol.eq("T0") & scored.model.eq("DirectTabular")
    ][["origin", "blok", "abs_error", "direction_correct"]].rename(
        columns={
            "abs_error": "T0_abs_error",
            "direction_correct": "T0_direction_correct",
        }
    )
    paired_rows, mcnemar_rows = [], []
    for block in ["SELECT", "CONFIRM", "ALL"]:
        source = scored if block == "ALL" else scored[scored.blok.eq(block)]
        for (tier, model), candidate in source.groupby(["kol", "model"]):
            candidate = candidate[["origin", "abs_error", "direction_correct"]].rename(
                columns={
                    "abs_error": "candidate_abs_error",
                    "direction_correct": "candidate_direction_correct",
                }
            )
            ref = reference if block == "ALL" else reference[reference.blok.eq(block)]
            joined = ref.merge(candidate, on="origin", validate="one_to_one")
            gain = joined.T0_abs_error - joined.candidate_abs_error
            remove_origins = gain.nlargest(min(2, len(gain))).index
            robust_gain = gain.drop(index=remove_origins)
            paired_rows.append(
                {
                    "blok": block,
                    "kol": tier,
                    "model": model,
                    "n": len(joined),
                    "paired_win": int((gain > 0).sum()),
                    "paired_tie": int((gain == 0).sum()),
                    "T0_MAE": float(joined.T0_abs_error.mean()),
                    "candidate_MAE": float(joined.candidate_abs_error.mean()),
                    "T0_eksi_candidate_MAE": float(gain.mean()),
                    "en_buyuk_2_kazanc_cikarilinca_net_fark": float(robust_gain.sum()),
                }
            )
            b = int(
                (
                    joined.candidate_direction_correct.eq(1)
                    & joined.T0_direction_correct.eq(0)
                ).sum()
            )
            c = int(
                (
                    joined.candidate_direction_correct.eq(0)
                    & joined.T0_direction_correct.eq(1)
                ).sum()
            )
            mcnemar_rows.append(
                {
                    "blok": block,
                    "kol": tier,
                    "model": model,
                    "n": len(joined),
                    "b_candidate_dogru_T0_yanlis": b,
                    "c_candidate_yanlis_T0_dogru": c,
                    "mcnemar_exact_p": exact_mcnemar_p(b, c),
                }
            )
    return pd.DataFrame(paired_rows), pd.DataFrame(mcnemar_rows)


def reproduce(predictions: pd.DataFrame) -> str:
    checks = []
    sources = {
        "T0_vs_IP2": ("T0", pd.read_csv(IP2_PATH, parse_dates=["origin", "hedef_ay"])),
        "T1_vs_IP3": ("T1", pd.read_csv(IP3_PATH, parse_dates=["origin", "hedef_ay"])),
        "T2_vs_IP3": ("T2", pd.read_csv(IP3_PATH, parse_dates=["origin", "hedef_ay"])),
    }
    for label, (tier, old) in sources.items():
        if "kol" in old.columns:
            old = old[old.kol.eq(tier)]
        old = old[old.origin.between(CONFIRM_START, CONFIRM_END)]
        current = predictions[
            predictions.kol.eq(tier) & predictions.origin.between(CONFIRM_START, CONFIRM_END)
        ]
        joined = current.merge(
            old[["origin", "model", "y_pred_q50"]],
            on=["origin", "model"],
            suffixes=("_ip4", "_old"),
            validate="one_to_one",
        )
        diff = (joined.y_pred_q50_ip4 - joined.y_pred_q50_old).abs()
        checks.append(
            f"{label}: n={len(joined)}, max_abs_fark={diff.max():.12g}, "
            f"exact_1e-8_pass={bool(diff.max() <= 1e-8)}"
        )
    return "\n".join(checks)


def direct_tabular_diagnostic() -> str:
    lines = []
    for tier in ["T0", "T1"]:
        path = MODEL_ROOT / tier / "origin_202503"
        try:
            predictor = TimeSeriesPredictor.load(path)
            model = predictor._trainer.load_model("DirectTabular").most_recent_model
            features = list(model.get_tabular_model().feature_pipeline.features_in)
            declared = list(model.covariate_metadata.known_covariates_real)
            present = [name for name in declared if name in features]
            lines.extend(
                [
                    f"{tier}_declared_known_covariates={json.dumps(declared, ensure_ascii=False)}",
                    f"{tier}_tabular_features={json.dumps(features, ensure_ascii=False)}",
                    f"{tier}_declared_and_present={json.dumps(present, ensure_ascii=False)}",
                    f"{tier}_all_declared_present={set(declared).issubset(features)}",
                ]
            )
            log_path = path / "logs" / "predictor_log.txt"
            warning_lines = []
            if log_path.exists():
                for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
                    low = line.lower()
                    if "covariate" in low and any(word in low for word in ["drop", "ignore", "remove", "warn"]):
                        warning_lines.append(line)
            lines.append(f"{tier}_covariate_drop_warnings={json.dumps(warning_lines, ensure_ascii=False)}")
        except Exception as error:
            lines.append(f"{tier}=tespit edilemedi: {error!r}")
    return "\n".join(lines)


def selection_report(
    ranks: pd.DataFrame,
    paired: pd.DataFrame,
    mcnemar: pd.DataFrame,
) -> str:
    selectable = ranks[
        ranks.blok.eq("SELECT") & ~ranks.model.isin(BASELINES)
    ].sort_values(["MAE", "RMSE", "kol", "model"])
    chosen = selectable.iloc[0]
    confirm = ranks[
        ranks.blok.eq("CONFIRM")
        & ranks.kol.eq(chosen.kol)
        & ranks.model.eq(chosen.model)
    ].iloc[0]
    all_pair = paired[
        paired.blok.eq("ALL")
        & paired.kol.eq(chosen.kol)
        & paired.model.eq(chosen.model)
    ].iloc[0]
    all_mc = mcnemar[
        mcnemar.blok.eq("ALL")
        & mcnemar.kol.eq(chosen.kol)
        & mcnemar.model.eq(chosen.model)
    ].iloc[0]
    criteria = {
        "mae_24_en_az_yuzde5_iyi": bool(all_pair.candidate_MAE <= 0.95 * all_pair.T0_MAE),
        "paired_win_en_az_17": bool(all_pair.paired_win >= 17),
        "mcnemar_p_altinda_005": bool(all_mc.mcnemar_exact_p < 0.05),
        "en_buyuk_2_cikarilinca_net_pozitif": bool(
            all_pair.en_buyuk_2_kazanc_cikarilinca_net_fark > 0
        ),
    }
    accepted = all(criteria.values())
    return "\n".join(
        [
            f"SELECT_SECILEN_KOL={chosen.kol}",
            f"SELECT_SECILEN_MODEL={chosen.model}",
            f"SELECT_MAE={chosen.MAE:.6f}",
            f"SELECT_RMSE={chosen.RMSE:.6f}",
            f"SELECT_DA_YUZDE={chosen.DA_yuzde:.6f}",
            f"CONFIRM_MAE={confirm.MAE:.6f}",
            f"CONFIRM_RMSE={confirm.RMSE:.6f}",
            f"CONFIRM_DA_YUZDE={confirm.DA_yuzde:.6f}",
            f"ALL_PAIRED_WIN={int(all_pair.paired_win)}/24",
            f"ALL_MCNEMAR_P={all_mc.mcnemar_exact_p:.8f}",
            f"KRITERLER={json.dumps(criteria, ensure_ascii=False)}",
            f"KOVARYAT_KABUL={accepted}",
            "NOT=Model yalnız SELECT bloğunda mekanik olarak seçildi; CONFIRM sonucuna göre değiştirilmedi.",
        ]
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    protected = [
        PREDICTIONS_PATH,
        RANKING_PATH,
        PAIRED_PATH,
        MCNEMAR_PATH,
        SELECTION_PATH,
        DIAGNOSTIC_PATH,
        REPRO_PATH,
        FIT_LOG_PATH,
    ]
    if any(path.exists() for path in protected):
        raise FileExistsError("IP-4 çıktıları zaten mevcut; üzerine yazılmadı.")

    data = load_data()
    print("IP4 VERI VE ZAMAN SOZLESMESI ASSERTLERI GECTI", flush=True)
    predictions = run(data)
    scored = add_errors(predictions)
    ranks = ranking(scored)
    paired, mcnemar = paired_and_mcnemar(scored)
    repro = reproduce(predictions)
    diagnostic = direct_tabular_diagnostic()
    selection = selection_report(ranks, paired, mcnemar)

    predictions.to_csv(PREDICTIONS_PATH, index=False, encoding="utf-8-sig")
    ranks.to_csv(RANKING_PATH, index=False, encoding="utf-8-sig")
    paired.to_csv(PAIRED_PATH, index=False, encoding="utf-8-sig")
    mcnemar.to_csv(MCNEMAR_PATH, index=False, encoding="utf-8-sig")
    SELECTION_PATH.write_text(selection + "\n", encoding="utf-8")
    DIAGNOSTIC_PATH.write_text(diagnostic + "\n", encoding="utf-8")
    REPRO_PATH.write_text(repro + "\n", encoding="utf-8")

    print("\nIP4 SECIM\n" + selection)
    print("\nIP4 DIRECTTABULAR TANI\n" + diagnostic)
    print("\nIP4 REPRODUKSIYON\n" + repro)
    print("\nASSERT max_origin=2025-03-01 test_rows=0")
    print("TEST BLOKUNA DOKUNULMADI.")


if __name__ == "__main__":
    main()
