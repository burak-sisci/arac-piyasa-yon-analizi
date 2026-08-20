"""IP-6: target_1ay_hiz, h=1, 64-origin resumable validation."""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "birlesik_target_setleri" / "target_1ay_hiz_tum_featurelar_final.csv"
OUT = ROOT / "outputs" / "autogluon" / "ip6_1ay"
MODEL_ROOT = OUT / "ag_models"
PRED_PATH = OUT / "ip6_h1_tahminler.csv"
RANK_PATH = OUT / "ip6_h1_siralama.csv"
PAIRED_PATH = OUT / "ip6_paired.csv"
MCNEMAR_PATH = OUT / "ip6_mcnemar.csv"
SELECTION_PATH = OUT / "ip6_secim.txt"
DECISION_PATH = OUT / "ip6_karar.txt"
LEAKAGE_PATH = OUT / "ip6_leakage_denetimi.txt"
FIT_LOG = OUT / "ip6_fit_log.txt"

TARGET = "target_1ay_hiz"
ITEM_ID = "TR_otomobil"
FREQ = "MS"
PREDICTION_LENGTH = 1
PRESET = "medium_quality"
TIME_LIMIT = 150

ORIGIN_START = pd.Timestamp("2020-02-01")
ORIGIN_END = pd.Timestamp("2025-05-01")
SHOCK_END = pd.Timestamp("2022-12-01")
TEST_ORIGIN_START = pd.Timestamp("2025-06-01")
TEST_ORIGIN_END = pd.Timestamp("2026-05-01")

T1 = [
    "noter_devir_otomobil_adet",
    "tufe_aylik_degisim",
    "osd_kamyonet_adet",
    "osd_binek_kamyonet_toplam_adet",
    "odmd_hta_adet",
]
TIERS = {"T0": [], "T1": T1}
BASELINES = {"sifir", "naive", "mevsimsel_naive", "son12_ortalama"}
EXPECTED_AG_MODELS = {
    "SeasonalNaive",
    "RecursiveTabular",
    "DirectTabular",
    "ETS",
    "Theta",
    "Chronos2",
    "Toto2",
    "WeightedEnsemble",
}
EXPECTED_MODELS = EXPECTED_AG_MODELS | BASELINES


def emit(message: str) -> None:
    print(message, flush=True)
    with FIT_LOG.open("a", encoding="utf-8") as file:
        file.write(message + "\n")


def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    required = {"referans_ayi", TARGET, *T1}
    if missing := required.difference(data.columns):
        raise KeyError(f"Eksik zorunlu sütunlar: {sorted(missing)}")
    data["referans_ayi"] = pd.to_datetime(data["referans_ayi"], errors="raise")
    for column in [TARGET, *T1]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_values("referans_ayi").reset_index(drop=True)

    expected = pd.date_range("2018-02-01", "2026-06-01", freq=FREQ)
    assert len(data) == 101
    assert data.referans_ayi.equals(pd.Series(expected, name="referans_ayi"))
    assert not data.referans_ayi.duplicated().any()
    assert data[TARGET].notna().all() and np.isfinite(data[TARGET]).all()
    assert data[[column for column in T1 if column != "odmd_hta_adet"]].notna().all().all()
    assert int(data.odmd_hta_adet.isna().sum()) <= 1
    return data


def regime(origin: pd.Timestamp) -> str:
    return "SOK" if origin <= SHOCK_END else "NORMAL"


def block(origin: pd.Timestamp) -> str:
    return "SELECT" if origin <= SHOCK_END else "CONFIRM"


def causal_source_table(data: pd.DataFrame, features: list[str]) -> tuple[pd.DataFrame | None, int]:
    if not features:
        return None, 0
    source = data.set_index("referans_ayi")[features].copy()
    before = source.odmd_hta_adet.copy()
    source["odmd_hta_adet"] = source.odmd_hta_adet.ffill()
    filled = int((before.isna() & source.odmd_hta_adet.notna()).sum())
    assert filled <= 1
    return source, filled


def lagged_table(source: pd.DataFrame | None) -> pd.DataFrame | None:
    if source is None:
        return None
    lagged = source.shift(1)
    lagged.columns = [f"{column}_lag1" for column in lagged.columns]
    assert all(column.endswith("_lag1") for column in lagged.columns)
    assert not set(T1).intersection(lagged.columns)
    return lagged


def train_tsdf(data: pd.DataFrame, lagged: pd.DataFrame | None, origin: pd.Timestamp) -> TimeSeriesDataFrame:
    frame = data.set_index("referans_ayi")[[TARGET]].loc[:origin]
    if lagged is not None:
        frame = frame.join(lagged.loc[:origin], how="left")
    frame = frame.reset_index().rename(columns={"referans_ayi": "timestamp"})
    frame.insert(0, "item_id", ITEM_ID)
    result = TimeSeriesDataFrame.from_data_frame(frame, id_column="item_id", timestamp_column="timestamp")
    assert result.freq == FREQ
    assert result.num_items == 1
    assert result.index.get_level_values("timestamp").max() == origin
    return result


def future_tsdf(
    source: pd.DataFrame | None,
    lagged: pd.DataFrame | None,
    origin: pd.Timestamp,
) -> tuple[TimeSeriesDataFrame | None, list[str]]:
    if lagged is None or source is None:
        return None, []
    target_month = origin + pd.DateOffset(months=1)
    future = lagged.loc[[target_month]].copy()
    assert not future.isna().any().any()
    assert all(column.endswith("_lag1") for column in future.columns)
    audit = []
    for original in T1:
        lag_name = f"{original}_lag1"
        source_month = target_month - pd.DateOffset(months=1)
        assert source_month == origin
        actual_source = float(source.loc[source_month, original])
        supplied = float(future.loc[target_month, lag_name])
        assert np.isclose(supplied, actual_source, rtol=0, atol=1e-12)
        audit.append(
            f"origin={origin:%Y-%m} target={target_month:%Y-%m} covariate={lag_name} "
            f"source={source_month:%Y-%m} source_le_origin={source_month <= origin} value_match=True"
        )
    assert np.isclose(
        future.loc[target_month, "noter_devir_otomobil_adet_lag1"],
        source.loc[origin, "noter_devir_otomobil_adet"],
        rtol=0,
        atol=1e-12,
    )
    frame = future.reset_index(names="timestamp")
    frame.insert(0, "item_id", ITEM_ID)
    result = TimeSeriesDataFrame.from_data_frame(frame, id_column="item_id", timestamp_column="timestamp")
    assert len(result) == 1
    return result, audit


def q50(prediction: TimeSeriesDataFrame, month: pd.Timestamp) -> float:
    column = "0.5" if "0.5" in prediction.columns else 0.5
    if column not in prediction.columns:
        raise KeyError(f"Medyan sütunu bulunamadı: {prediction.columns.tolist()}")
    assert len(prediction) == 1
    return float(prediction.loc[(ITEM_ID, month), column])


def read_checkpoint() -> pd.DataFrame:
    if not PRED_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(PRED_PATH, parse_dates=["origin", "hedef_ay"])
    if not frame.empty:
        assert not frame.duplicated(["kol", "origin", "model"]).any()
    return frame


def completed_pairs(frame: pd.DataFrame) -> set[tuple[str, pd.Timestamp]]:
    if frame.empty:
        return set()
    result = set()
    for (tier, origin), group in frame.groupby(["kol", "origin"]):
        if set(group.model) == EXPECTED_MODELS:
            result.add((tier, pd.Timestamp(origin)))
    return result


def append_rows(rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(
        PRED_PATH,
        mode="a",
        header=not PRED_PATH.exists(),
        index=False,
        encoding="utf-8-sig",
    )


def run(data: pd.DataFrame, resume: bool) -> pd.DataFrame:
    origins = pd.date_range(ORIGIN_START, ORIGIN_END, freq=FREQ)
    assert len(origins) == 64
    assert origins.max() == ORIGIN_END and origins.max() < TEST_ORIGIN_START
    checkpoint = read_checkpoint()
    if not resume and not checkpoint.empty:
        raise FileExistsError("Checkpoint mevcut. Devam etmek için --resume kullanın.")
    done = completed_pairs(checkpoint) if resume else set()
    truth = data.set_index("referans_ayi")[TARGET]
    leakage_lines = []

    for tier, features in TIERS.items():
        source, fill_count = causal_source_table(data, features)
        lagged = lagged_table(source)
        known = [] if lagged is None else lagged.columns.tolist()
        assert fill_count <= 1
        for number, origin in enumerate(origins, start=1):
            if (tier, origin) in done:
                emit(f"RESUME_SKIP {tier} {origin:%Y-%m}")
                continue
            assert not TEST_ORIGIN_START <= origin <= TEST_ORIGIN_END
            train = train_tsdf(data, lagged, origin)
            future, audits = future_tsdf(source, lagged, origin)
            leakage_lines.extend(f"{tier} {line}" for line in audits)
            target_month = origin + pd.DateOffset(months=1)
            assert target_month == train.index.get_level_values("timestamp").max() + pd.DateOffset(months=1)
            model_path = MODEL_ROOT / tier / f"origin_{origin:%Y%m}"

            if resume and model_path.exists():
                predictor = TimeSeriesPredictor.load(model_path)
                emit(f"RESUME_LOAD {tier} {origin:%Y-%m}")
            else:
                kwargs = dict(
                    prediction_length=PREDICTION_LENGTH,
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
                assert predictor.prediction_length == 1
                emit(
                    f"{tier} ORIGIN {number:02d}/64 {origin:%Y-%m} "
                    f"rejim={regime(origin)} blok={block(origin)} known={known}"
                )
                started = time.perf_counter()
                predictor.fit(
                    train_data=train,
                    presets=PRESET,
                    time_limit=TIME_LIMIT,
                    random_seed=42,
                    verbosity=1,
                )
                emit(f"{tier} FIT_DONE {origin:%Y-%m} seconds={time.perf_counter()-started:.2f}")

            actual = float(truth.loc[target_month])
            rows = []
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
                        "blok": block(origin),
                        "origin": origin,
                        "model": model,
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": q50(prediction, target_month),
                    }
                )
            history = truth.loc[:origin]
            baseline_values = {
                "sifir": 0.0,
                "naive": float(history.iloc[-1]),
                "mevsimsel_naive": float(truth.loc[origin - pd.DateOffset(months=11)]),
                "son12_ortalama": float(history.iloc[-12:].mean()),
            }
            for model, value in baseline_values.items():
                rows.append(
                    {
                        "kol": tier,
                        "rejim": regime(origin),
                        "blok": block(origin),
                        "origin": origin,
                        "model": model,
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": value,
                    }
                )
            assert set(pd.DataFrame(rows).model) == EXPECTED_MODELS
            append_rows(rows)
            if leakage_lines:
                LEAKAGE_PATH.write_text(
                    "A7_A8_PASS=True\n" + f"odmd_ffill_toplam={fill_count}\n" + "\n".join(leakage_lines) + "\n",
                    encoding="utf-8",
                )

    predictions = read_checkpoint()
    assert predictions.origin.min() == ORIGIN_START
    assert predictions.origin.max() == ORIGIN_END
    assert predictions.groupby(["kol", "origin"]).size().eq(len(EXPECTED_MODELS)).all()
    assert predictions.groupby(["kol", "model"]).size().eq(64).all()
    assert predictions.hedef_ay.eq(predictions.origin + pd.DateOffset(months=1)).all()
    assert len(predictions[predictions.origin.ge(TEST_ORIGIN_START)]) == 0
    assert predictions.y_pred_q50.notna().all() and np.isfinite(predictions.y_pred_q50).all()
    return predictions


def scored(predictions: pd.DataFrame) -> pd.DataFrame:
    frame = predictions.copy()
    frame["abs_error"] = (frame.y_true - frame.y_pred_q50).abs()
    frame["sq_error"] = (frame.y_true - frame.y_pred_q50) ** 2
    frame["direction_correct"] = (
        frame.y_true.ne(0) & np.sign(frame.y_true).eq(np.sign(frame.y_pred_q50))
    ).astype(int)
    return frame


def subsets(frame: pd.DataFrame):
    yield "SOK", frame[frame.rejim.eq("SOK")]
    yield "NORMAL", frame[frame.rejim.eq("NORMAL")]
    yield "TUM", frame


def binomial_upper_p(k: int, n: int, p: float = 0.5) -> float:
    return min(1.0, sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def exact_mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2**n
    return min(1.0, 2 * tail)


def ranking(frame: pd.DataFrame) -> pd.DataFrame:
    tables = []
    for name, subset in subsets(frame):
        actual = subset.drop_duplicates("origin").y_true
        positive = int((actual > 0).sum())
        negative = int((actual < 0).sum())
        majority = 100 * max(positive, negative) / len(actual)
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
        table["gercek_pozitif"] = positive
        table["gercek_negatif"] = negative
        table["cogunluk_taban_yuzde"] = majority
        table["DA_binom_p_vs_0_5"] = [binomial_upper_p(int(k), int(n)) for k, n in zip(table.DA_adet, table.n)]
        tables.append(table)
    return pd.concat(tables, ignore_index=True).sort_values(["rejim", "MAE", "kol", "model"])


def select_model(ranks: pd.DataFrame) -> tuple[str, str]:
    candidates = ranks[
        ranks.rejim.eq("SOK") & ranks.kol.eq("T1") & ~ranks.model.isin(BASELINES)
    ].sort_values(["MAE", "RMSE", "model"])
    row = candidates.iloc[0]
    return str(row.kol), str(row.model)


def paired_tables(frame: pd.DataFrame, chosen_model: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    specs = [
        ("T1_best_vs_sifir", "T1", chosen_model, "T0", "sifir"),
        ("T1_best_vs_naive", "T1", chosen_model, "T0", "naive"),
        ("T1_best_vs_ayni_model_T0", "T1", chosen_model, "T0", chosen_model),
    ]
    paired_rows, mcnemar_rows = [], []
    for regime_name, subset in subsets(frame):
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
            if name == "T1_best_vs_naive":
                b = int((joined.candidate_direction.eq(1) & joined.reference_direction.eq(0)).sum())
                c = int((joined.candidate_direction.eq(0) & joined.reference_direction.eq(1)).sum())
                mcnemar_rows.append(
                    {
                        "rejim": regime_name,
                        "candidate": f"T1_{chosen_model}",
                        "reference": "naive",
                        "n": len(joined),
                        "b_candidate_dogru_naive_yanlis": b,
                        "c_candidate_yanlis_naive_dogru": c,
                        "mcnemar_exact_p": exact_mcnemar_p(b, c),
                    }
                )
    return pd.DataFrame(paired_rows), pd.DataFrame(mcnemar_rows)


def selection_text(ranks: pd.DataFrame, model: str) -> str:
    shock = ranks[ranks.rejim.eq("SOK") & ranks.kol.eq("T1") & ranks.model.eq(model)].iloc[0]
    normal = ranks[ranks.rejim.eq("NORMAL") & ranks.kol.eq("T1") & ranks.model.eq(model)].iloc[0]
    return "\n".join(
        [
            "SECIM_BLOKU=SOK_2020-02_2022-12",
            "SECILEN_KOL=T1",
            f"SECILEN_MODEL={model}",
            f"SOK_MAE={shock.MAE:.6f}",
            f"SOK_DA={int(shock.DA_adet)}/{int(shock.n)}",
            f"NORMAL_MAE={normal.MAE:.6f}",
            f"NORMAL_DA={int(normal.DA_adet)}/{int(normal.n)}",
            "NORMAL_SONUCA_BAKILARAK_MODEL_DEGISTIRILMEDI=True",
        ]
    ) + "\n"


def decision_text(ranks: pd.DataFrame, paired: pd.DataFrame, mcnemar: pd.DataFrame, model: str) -> str:
    all_rank = ranks[ranks.rejim.eq("TUM") & ranks.kol.eq("T1") & ranks.model.eq(model)].iloc[0]
    all_zero = paired[paired.rejim.eq("TUM") & paired.karsilastirma.eq("T1_best_vs_sifir")].iloc[0]
    normal_zero = paired[paired.rejim.eq("NORMAL") & paired.karsilastirma.eq("T1_best_vs_sifir")].iloc[0]
    all_mc = mcnemar[mcnemar.rejim.eq("TUM")].iloc[0]
    criteria = {
        "sifir_paired_win_en_az_40": bool(all_zero.paired_win >= 40),
        "sifira_gore_mae_en_az_yuzde10_iyi": bool(all_zero.candidate_MAE <= 0.90 * all_zero.reference_MAE),
        "en_buyuk_2_cikarilinca_net_pozitif": bool(all_zero.en_buyuk_2_kazanc_cikarilinca_net_fark > 0),
        "DA_en_az_40": bool(all_rank.DA_adet >= 40),
        "naive_McNemar_p_altinda_005": bool(all_mc.mcnemar_exact_p < 0.05),
        "normal_MAE_farki_pozitif": bool(normal_zero.reference_eksi_candidate_MAE > 0),
        "normal_paired_win_en_az_15": bool(normal_zero.paired_win >= 15),
    }
    return "\n".join(
        [
            f"SECILEN=T1_{model}",
            f"TUM_MAE={all_rank.MAE:.6f}",
            f"TUM_DA={int(all_rank.DA_adet)}/{int(all_rank.n)} ({all_rank.DA_yuzde:.4f}%)",
            f"TUM_DA_BINOM_P={all_rank.DA_binom_p_vs_0_5:.8f}",
            f"TUM_SIFIR_PAIRED_WIN={int(all_zero.paired_win)}/64",
            f"NORMAL_SIFIR_PAIRED_WIN={int(normal_zero.paired_win)}/29",
            f"NAIVE_MCNEMAR_P={all_mc.mcnemar_exact_p:.8f}",
            "KRITERLER=" + repr(criteria),
            f"IP6_KABUL={all(criteria.values())}",
        ]
    ) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    if not args.resume:
        protected = [PRED_PATH, RANK_PATH, PAIRED_PATH, MCNEMAR_PATH, SELECTION_PATH, DECISION_PATH, LEAKAGE_PATH, FIT_LOG]
        if any(path.exists() for path in protected):
            raise FileExistsError("IP-6 çıktısı mevcut; --resume kullanın.")

    data = load_data()
    print("IP6 A1_A2 VERI ASSERTLERI GECTI", flush=True)
    predictions = run(data, resume=args.resume)
    frame = scored(predictions)
    ranks = ranking(frame)
    _, chosen_model = select_model(ranks)
    paired, mcnemar = paired_tables(frame, chosen_model)
    selection = selection_text(ranks, chosen_model)
    decision = decision_text(ranks, paired, mcnemar, chosen_model)

    ranks.to_csv(RANK_PATH, index=False, encoding="utf-8-sig")
    paired.to_csv(PAIRED_PATH, index=False, encoding="utf-8-sig")
    mcnemar.to_csv(MCNEMAR_PATH, index=False, encoding="utf-8-sig")
    SELECTION_PATH.write_text(selection, encoding="utf-8")
    DECISION_PATH.write_text(decision, encoding="utf-8")

    naive = ranks[ranks.model.eq("naive")][["rejim", "DA_adet", "n", "DA_yuzde"]]
    print("\nIP6 SECIM\n" + selection)
    print("IP6 KARAR\n" + decision)
    print("NAIVE_DA_SOK_NORMAL_TUM")
    print(naive.drop_duplicates("rejim").sort_values("rejim").to_string(index=False))
    print("ASSERT max_origin=2025-05-01 test_rows=0 prediction_length=1")
    print("TEST BLOKUNA DOKUNULMADI.")


if __name__ == "__main__":
    main()
