"""IP-5: 60-origin T0/T1 validation with resumable checkpoints."""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "birlesik_target_setleri" / "target_3ay_hiz_tum_featurelar_final.csv"
IP4_PATH = ROOT / "outputs" / "autogluon" / "ip4_genis" / "ip4_h3_tahminler.csv"
OUT = ROOT / "outputs" / "autogluon" / "ip5_uzun"
MODELS = OUT / "ag_models"
PRED_PATH = OUT / "ip5_h3_tahminler.csv"
RANK_PATH = OUT / "ip5_h3_siralama.csv"
PAIRED_PATH = OUT / "ip5_paired_uclu.csv"
MCNEMAR_PATH = OUT / "ip5_mcnemar.csv"
REPRO_PATH = OUT / "ip5_reprodüksiyon.txt"
FIT_LOG = OUT / "ip5_fit_log.txt"
DECISION_PATH = OUT / "ip5_karar.txt"

TARGET = "target_3ay_hiz"
ITEM_ID = "TR_otomobil"
FREQ = "MS"
PRESET = "medium_quality"
TIME_LIMIT = 150
ORIGIN_START = pd.Timestamp("2020-04-01")
ORIGIN_END = pd.Timestamp("2025-03-01")
TEST_START = pd.Timestamp("2025-04-01")
TEST_END = pd.Timestamp("2026-03-01")
SHOCK_END = pd.Timestamp("2022-12-01")

T1 = ["noter_devir_otomobil_adet", "osd_binek_adet", "otv_event_ay_mi"]
TIERS = {"T0": [], "T1": T1}
EXPECTED_MODELS = {
    "SeasonalNaive",
    "RecursiveTabular",
    "DirectTabular",
    "ETS",
    "Theta",
    "Chronos2",
    "Toto2",
    "WeightedEnsemble",
    "sifir",
    "son12_ortalama",
}


def emit(message: str) -> None:
    print(message, flush=True)
    with FIT_LOG.open("a", encoding="utf-8") as file:
        file.write(message + "\n")


def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    required = {"referans_ayi", TARGET, *T1}
    if missing := required.difference(data.columns):
        raise KeyError(f"Eksik sütunlar: {sorted(missing)}")
    data["referans_ayi"] = pd.to_datetime(data["referans_ayi"], errors="raise")
    for column in [TARGET, *T1]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_values("referans_ayi").reset_index(drop=True)
    expected = pd.date_range(data.referans_ayi.min(), data.referans_ayi.max(), freq=FREQ)
    assert data.referans_ayi.equals(pd.Series(expected, name="referans_ayi"))
    assert len(data) == 97
    assert data[TARGET].notna().all() and np.isfinite(data[TARGET]).all()
    assert data[T1].notna().all().all()
    return data


def regime(origin: pd.Timestamp) -> str:
    return "SOK_2020_04_2022_12" if origin <= SHOCK_END else "NORMAL_2023_01_2025_03"


def lagged_features(data: pd.DataFrame, features: list[str]) -> pd.DataFrame | None:
    if not features:
        return None
    result = data.set_index("referans_ayi")[features].shift(3)
    result.columns = [f"{column}_lag3" for column in result.columns]
    return result


def train_tsdf(data: pd.DataFrame, lagged: pd.DataFrame | None, origin: pd.Timestamp) -> TimeSeriesDataFrame:
    frame = data.set_index("referans_ayi")[[TARGET]].loc[:origin]
    if lagged is not None:
        frame = frame.join(lagged.loc[:origin], how="left")
    frame = frame.reset_index().rename(columns={"referans_ayi": "timestamp"})
    frame.insert(0, "item_id", ITEM_ID)
    result = TimeSeriesDataFrame.from_data_frame(frame, id_column="item_id", timestamp_column="timestamp")
    assert result.freq == FREQ
    assert result.index.get_level_values("timestamp").max() == origin
    return result


def future_tsdf(lagged: pd.DataFrame | None, origin: pd.Timestamp) -> TimeSeriesDataFrame | None:
    if lagged is None:
        return None
    months = pd.date_range(origin + pd.DateOffset(months=1), periods=3, freq=FREQ)
    frame = lagged.loc[months].copy()
    assert not frame.isna().any().any()
    for month in months:
        assert month - pd.DateOffset(months=3) <= origin
    frame = frame.reset_index(names="timestamp")
    frame.insert(0, "item_id", ITEM_ID)
    return TimeSeriesDataFrame.from_data_frame(frame, id_column="item_id", timestamp_column="timestamp")


def median(prediction: TimeSeriesDataFrame, month: pd.Timestamp) -> float:
    column = "0.5" if "0.5" in prediction.columns else 0.5
    return float(prediction.loc[(ITEM_ID, month), column])


def checkpoint_rows() -> pd.DataFrame:
    if not PRED_PATH.exists():
        return pd.DataFrame()
    result = pd.read_csv(PRED_PATH, parse_dates=["origin", "hedef_ay"])
    if result.empty:
        return result
    assert not result.duplicated(["kol", "origin", "model"]).any()
    return result


def completed_pairs(checkpoint: pd.DataFrame) -> set[tuple[str, pd.Timestamp]]:
    if checkpoint.empty:
        return set()
    completed = set()
    for (tier, origin), group in checkpoint.groupby(["kol", "origin"]):
        if set(group.model) == EXPECTED_MODELS:
            completed.add((tier, pd.Timestamp(origin)))
    return completed


def append_checkpoint(rows: list[dict]) -> None:
    frame = pd.DataFrame(rows)
    frame.to_csv(
        PRED_PATH,
        mode="a",
        header=not PRED_PATH.exists(),
        index=False,
        encoding="utf-8-sig",
    )


def run(data: pd.DataFrame, resume: bool) -> pd.DataFrame:
    origins = pd.date_range(ORIGIN_START, ORIGIN_END, freq=FREQ)
    assert len(origins) == 60 and origins.max() < TEST_START
    checkpoint = checkpoint_rows()
    if not resume and not checkpoint.empty:
        raise FileExistsError("Checkpoint var. Devam etmek için --resume kullanın.")
    done = completed_pairs(checkpoint) if resume else set()
    truth = data.set_index("referans_ayi")[TARGET]

    for tier, features in TIERS.items():
        lagged = lagged_features(data, features)
        known = [] if lagged is None else lagged.columns.tolist()
        for number, origin in enumerate(origins, 1):
            if (tier, origin) in done:
                emit(f"RESUME_SKIP {tier} {origin:%Y-%m}")
                continue
            assert not TEST_START <= origin <= TEST_END
            train = train_tsdf(data, lagged, origin)
            future = future_tsdf(lagged, origin)
            target_month = origin + pd.DateOffset(months=3)
            model_path = MODELS / tier / f"origin_{origin:%Y%m}"
            predictor: TimeSeriesPredictor
            if resume and model_path.exists():
                predictor = TimeSeriesPredictor.load(model_path)
                emit(f"RESUME_LOAD {tier} {origin:%Y-%m} path={model_path}")
            else:
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
                if known:
                    kwargs["known_covariates_names"] = known
                predictor = TimeSeriesPredictor(**kwargs)
                emit(f"{tier} ORIGIN {number:02d}/60 {origin:%Y-%m} rejim={regime(origin)} known={known}")
                started = time.perf_counter()
                predictor.fit(
                    train_data=train,
                    presets=PRESET,
                    time_limit=TIME_LIMIT,
                    random_seed=42,
                    verbosity=1,
                )
                emit(f"{tier} FIT_DONE {origin:%Y-%m} seconds={time.perf_counter()-started:.2f}")

            rows = []
            actual = float(truth.loc[target_month])
            for model in predictor.model_names():
                prediction = predictor.predict(
                    train,
                    known_covariates=future,
                    model=model,
                    random_seed=42,
                )
                rows.append(
                    {
                        "kol": tier,
                        "rejim": regime(origin),
                        "origin": origin,
                        "model": model,
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": median(prediction, target_month),
                    }
                )
            history = truth.loc[:origin]
            rows.extend(
                [
                    {"kol": tier, "rejim": regime(origin), "origin": origin, "model": "sifir", "hedef_ay": target_month, "y_true": actual, "y_pred_q50": 0.0},
                    {"kol": tier, "rejim": regime(origin), "origin": origin, "model": "son12_ortalama", "hedef_ay": target_month, "y_true": actual, "y_pred_q50": float(history.iloc[-12:].mean())},
                ]
            )
            assert set(pd.DataFrame(rows).model) == EXPECTED_MODELS
            append_checkpoint(rows)

    predictions = checkpoint_rows()
    assert predictions.origin.min() == ORIGIN_START
    assert predictions.origin.max() == ORIGIN_END
    assert predictions.groupby(["kol", "origin"]).size().eq(len(EXPECTED_MODELS)).all()
    assert predictions.groupby(["kol", "model"]).size().eq(60).all()
    assert len(predictions[predictions.origin.between(TEST_START, TEST_END)]) == 0
    return predictions


def score(predictions: pd.DataFrame) -> pd.DataFrame:
    scored = predictions.copy()
    scored["abs_error"] = (scored.y_true - scored.y_pred_q50).abs()
    scored["sq_error"] = (scored.y_true - scored.y_pred_q50) ** 2
    scored["direction_correct"] = (
        scored.y_true.ne(0) & np.sign(scored.y_true).eq(np.sign(scored.y_pred_q50))
    ).astype(int)
    return scored


def subsets(scored: pd.DataFrame):
    yield "SOK_2020_04_2022_12", scored[scored.origin.le(SHOCK_END)]
    yield "NORMAL_2023_01_2025_03", scored[scored.origin.gt(SHOCK_END)]
    yield "TUM", scored


def make_ranking(scored: pd.DataFrame) -> pd.DataFrame:
    tables = []
    for name, subset in subsets(scored):
        table = (
            subset.groupby(["kol", "model"])
            .agg(
                n=("y_true", "size"),
                MAE=("abs_error", "mean"),
                RMSE=("sq_error", lambda x: float(np.sqrt(x.mean()))),
                DA_adet=("direction_correct", "sum"),
                DA_yuzde=("direction_correct", lambda x: 100 * x.mean()),
            )
            .reset_index()
        )
        table.insert(0, "rejim", name)
        tables.append(table)
    return pd.concat(tables, ignore_index=True).sort_values(["rejim", "MAE", "kol", "model"])


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2**n
    return min(1.0, 2 * tail)


def comparisons(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    specs = [
        ("ABLASYON_T1_CHRONOS2_vs_T0_CHRONOS2", "T1", "Chronos2", "T0", "Chronos2"),
        ("IS_ESIGI_T1_CHRONOS2_vs_SIFIR", "T1", "Chronos2", "T0", "sifir"),
        ("KONTROL_T1_CHRONOS2_vs_TOTO2", "T1", "Chronos2", "T0", "Toto2"),
    ]
    paired_rows, mc_rows = [], []
    for regime_name, subset in subsets(scored):
        for name, ct, cm, rt, rm in specs:
            candidate = subset[subset.kol.eq(ct) & subset.model.eq(cm)][
                ["origin", "abs_error", "direction_correct"]
            ].rename(columns={"abs_error": "candidate_error", "direction_correct": "candidate_direction"})
            reference = subset[subset.kol.eq(rt) & subset.model.eq(rm)][
                ["origin", "abs_error", "direction_correct"]
            ].rename(columns={"abs_error": "reference_error", "direction_correct": "reference_direction"})
            joined = candidate.merge(reference, on="origin", validate="one_to_one")
            gain = joined.reference_error - joined.candidate_error
            robust = gain.drop(index=gain.nlargest(min(2, len(gain))).index)
            paired_rows.append(
                {
                    "rejim": regime_name,
                    "karsilastirma": name,
                    "n": len(joined),
                    "paired_win": int((gain > 0).sum()),
                    "paired_tie": int((gain == 0).sum()),
                    "candidate_MAE": float(joined.candidate_error.mean()),
                    "reference_MAE": float(joined.reference_error.mean()),
                    "reference_eksi_candidate_MAE": float(gain.mean()),
                    "net_hata_kazanci": float(gain.sum()),
                    "en_buyuk_2_kazanc_cikarilinca_net_fark": float(robust.sum()),
                }
            )
            b = int((joined.candidate_direction.eq(1) & joined.reference_direction.eq(0)).sum())
            c = int((joined.candidate_direction.eq(0) & joined.reference_direction.eq(1)).sum())
            mc_rows.append(
                {
                    "rejim": regime_name,
                    "karsilastirma": name,
                    "n": len(joined),
                    "b_candidate_dogru_reference_yanlis": b,
                    "c_candidate_yanlis_reference_dogru": c,
                    "mcnemar_exact_p": exact_mcnemar_p(b, c),
                }
            )
    return pd.DataFrame(paired_rows), pd.DataFrame(mc_rows)


def reproduction(predictions: pd.DataFrame) -> str:
    old = pd.read_csv(IP4_PATH, parse_dates=["origin", "hedef_ay"])
    old = old[old.kol.isin(["T0", "T1"])]
    current = predictions[predictions.origin.between("2023-04-01", "2025-03-01")]
    joined = current.merge(
        old[["kol", "origin", "model", "y_pred_q50"]],
        on=["kol", "origin", "model"],
        suffixes=("_ip5", "_ip4"),
        validate="one_to_one",
    )
    diff = (joined.y_pred_q50_ip5 - joined.y_pred_q50_ip4).abs()
    return (
        f"n={len(joined)}\nmax_abs_fark={diff.max():.12g}\n"
        f"exact_1e-8_pass={bool(diff.max() <= 1e-8)}\n"
    )


def decision(ranks: pd.DataFrame, paired: pd.DataFrame) -> str:
    overall = ranks[(ranks.rejim.eq("TUM")) & (ranks.kol.eq("T1")) & (ranks.model.eq("Chronos2"))].iloc[0]
    ablation = paired[(paired.rejim.eq("TUM")) & paired.karsilastirma.str.startswith("ABLASYON")].iloc[0]
    zero = paired[(paired.rejim.eq("TUM")) & paired.karsilastirma.str.startswith("IS_ESIGI")].iloc[0]
    regime_ablation = paired[paired.karsilastirma.str.startswith("ABLASYON") & ~paired.rejim.eq("TUM")]
    criteria = {
        "ablasyon_paired_win_en_az_37": bool(ablation.paired_win >= 37),
        "sifir_paired_win_en_az_37": bool(zero.paired_win >= 37),
        "sifira_gore_mae_en_az_yuzde10_iyi": bool(zero.candidate_MAE <= 0.90 * zero.reference_MAE),
        "yon_dogru_en_az_38": bool(overall.DA_adet >= 38),
        "iki_rejimde_de_mae_farki_pozitif": bool((regime_ablation.reference_eksi_candidate_MAE > 0).all()),
    }
    return "\n".join(
        [
            f"T1_CHRONOS2_MAE_60={overall.MAE:.6f}",
            f"T1_CHRONOS2_DA={int(overall.DA_adet)}/60 ({overall.DA_yuzde:.4f}%)",
            f"ABLASYON_PAIRED_WIN={int(ablation.paired_win)}/60",
            f"SIFIR_PAIRED_WIN={int(zero.paired_win)}/60",
            "KRITERLER=" + repr(criteria),
            f"IP5_KABUL={all(criteria.values())}",
        ]
    ) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    MODELS.mkdir(parents=True, exist_ok=True)
    if not args.resume:
        protected = [PRED_PATH, RANK_PATH, PAIRED_PATH, MCNEMAR_PATH, REPRO_PATH, FIT_LOG, DECISION_PATH]
        if any(path.exists() for path in protected):
            raise FileExistsError("IP-5 çıktısı var; --resume kullanın veya yeni bir çıktı klasörü seçin.")

    data = load_data()
    print("IP5 VERI VE ZAMAN SOZLESMESI ASSERTLERI GECTI", flush=True)
    predictions = run(data, resume=args.resume)
    scored = score(predictions)
    ranks = make_ranking(scored)
    paired, mcnemar = comparisons(scored)
    repro = reproduction(predictions)
    verdict = decision(ranks, paired)

    ranks.to_csv(RANK_PATH, index=False, encoding="utf-8-sig")
    paired.to_csv(PAIRED_PATH, index=False, encoding="utf-8-sig")
    mcnemar.to_csv(MCNEMAR_PATH, index=False, encoding="utf-8-sig")
    REPRO_PATH.write_text(repro, encoding="utf-8")
    DECISION_PATH.write_text(verdict, encoding="utf-8")
    print("\nIP5 KARAR\n" + verdict)
    print("IP5 REPRODUKSIYON\n" + repro)
    print("ASSERT max_origin=2025-03-01 test_rows=0")
    print("TEST BLOKUNA DOKUNULMADI.")


if __name__ == "__main__":
    main()
