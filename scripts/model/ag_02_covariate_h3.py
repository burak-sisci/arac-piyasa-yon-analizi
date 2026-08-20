"""IP-3: medium-quality h=3 validation with lag-3 known covariates.

Three feature tiers are evaluated without touching the reserved test origins.
Every future covariate value comes from a source timestamp at or before the
forecast origin.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "birlesik_target_setleri"
    / "target_3ay_hiz_tum_featurelar_final.csv"
)
IP2_PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "autogluon"
    / "ip2_medium"
    / "ip2_h3_tahminler.csv"
)
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "autogluon" / "ip3_medium"
MODEL_ROOT = OUTPUT_DIR / "ag_models"
PREDICTIONS_PATH = OUTPUT_DIR / "ip3_h3_tahminler.csv"
RANKING_PATH = OUTPUT_DIR / "ip3_h3_model_siralama.csv"
COMPARISON_PATH = OUTPUT_DIR / "ip3_t0_karsilastirma.csv"
LAG_AUDIT_PATH = OUTPUT_DIR / "ip3_lag_denetimi.txt"
FFILL_LOG_PATH = OUTPUT_DIR / "ip3_ffill_log.txt"
FIT_LOG_PATH = OUTPUT_DIR / "ip3_fit_log.txt"

ITEM_ID = "TR_otomobil"
TARGET = "target_3ay_hiz"
FREQ = "MS"
PREDICTION_LENGTH = 3
PRESET = "medium_quality"
TIME_LIMIT_PER_ORIGIN = 300
VALIDATION_START = pd.Timestamp("2024-04-01")
VALIDATION_END = pd.Timestamp("2025-03-01")
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
T3 = T2 + [
    "betam_dom_gun",
    "betam_talep_aylik_pct",
    "betam_satis_orani_pct",
    "arabam_ortalama_ilan_fiyati_tl",
]
FEATURE_TIERS = {"T1": T1, "T2": T2, "T3": T3}
FFILL_FEATURES = {
    "betam_dom_gun",
    "betam_talep_aylik_pct",
    "betam_satis_orani_pct",
    "arabam_ortalama_ilan_fiyati_tl",
}
INVARIANT_MODELS = [
    "Chronos2",
    "Toto2",
    "ETS",
    "Theta",
    "SeasonalNaive",
]


def write_log(path: Path, message: str) -> None:
    print(message, flush=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(message + "\n")


def load_and_validate() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    required = {"referans_ayi", TARGET, *T3}
    missing = required.difference(data.columns)
    if missing:
        raise KeyError(f"Eksik zorunlu sütunlar: {sorted(missing)}")

    data["referans_ayi"] = pd.to_datetime(
        data["referans_ayi"], errors="raise"
    )
    for column in [TARGET, *T3]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.sort_values("referans_ayi").reset_index(drop=True)

    assert data["referans_ayi"].is_monotonic_increasing
    assert not data["referans_ayi"].duplicated().any()
    expected = pd.date_range(
        data["referans_ayi"].min(), data["referans_ayi"].max(), freq=FREQ
    )
    assert len(expected) == len(data)
    assert data["referans_ayi"].equals(
        pd.Series(expected, name="referans_ayi")
    )
    assert data[TARGET].notna().all()
    assert np.isfinite(data[TARGET].to_numpy()).all()
    assert len(data) == 97
    assert data[T1].notna().all().all()
    assert data[T2[3:]].loc[data["referans_ayi"] >= "2023-01-01"].notna().all().all()
    return data


def causal_feature_table(data: pd.DataFrame, tier: str) -> tuple[pd.DataFrame, dict]:
    features = FEATURE_TIERS[tier]
    table = data[["referans_ayi", *features]].copy().set_index("referans_ayi")
    fill_counts = {}
    for feature in features:
        before = table[feature].copy()
        if feature in FFILL_FEATURES:
            table[feature] = table[feature].ffill()
        filled = int((before.isna() & table[feature].notna()).sum())
        fill_counts[feature] = filled
    if tier in {"T1", "T2"}:
        assert sum(fill_counts.values()) == 0

    lagged = table.shift(PREDICTION_LENGTH)
    lagged.columns = [f"{column}_lag3" for column in lagged.columns]
    return lagged, fill_counts


def make_train_tsdf(
    data: pd.DataFrame,
    lagged: pd.DataFrame,
    origin: pd.Timestamp,
) -> TimeSeriesDataFrame:
    target = data.set_index("referans_ayi")[[TARGET]].loc[:origin]
    combined = target.join(lagged.loc[:origin], how="left").reset_index()
    combined = combined.rename(columns={"referans_ayi": "timestamp"})
    combined.insert(0, "item_id", ITEM_ID)
    tsdf = TimeSeriesDataFrame.from_data_frame(
        combined, id_column="item_id", timestamp_column="timestamp"
    )
    assert tsdf.freq == FREQ
    assert tsdf.index.get_level_values("timestamp").max() == origin
    return tsdf


def make_future_known_covariates(
    lagged: pd.DataFrame,
    origin: pd.Timestamp,
) -> TimeSeriesDataFrame:
    future_months = pd.date_range(
        origin + pd.DateOffset(months=1), periods=PREDICTION_LENGTH, freq=FREQ
    )
    future = lagged.loc[future_months].copy()
    assert not future.isna().any().any(), (
        f"{origin:%Y-%m}: tahmin ufku known covariate içinde NaN var."
    )

    # Each lag-3 value at horizon month H comes from H-3, never after origin T.
    for horizon_month in future_months:
        source_month = horizon_month - pd.DateOffset(months=PREDICTION_LENGTH)
        assert source_month <= origin

    # Selecting with a standalone DatetimeIndex can drop the original index
    # name in some pandas versions.  Name the timestamp column explicitly.
    future = future.reset_index(names="timestamp")
    future.insert(0, "item_id", ITEM_ID)
    return TimeSeriesDataFrame.from_data_frame(
        future, id_column="item_id", timestamp_column="timestamp"
    )


def median_prediction(prediction: TimeSeriesDataFrame, month: pd.Timestamp) -> float:
    median_column = "0.5" if "0.5" in prediction.columns else 0.5
    if median_column not in prediction.columns:
        raise KeyError(f"Medyan sütunu yok: {prediction.columns.tolist()}")
    return float(prediction.loc[(ITEM_ID, month), median_column])


def direct_tabular_lags(predictor: TimeSeriesPredictor) -> list[int] | None:
    try:
        outer_model = predictor._trainer.load_model("DirectTabular")
        inner_model = outer_model.most_recent_model
        lags = getattr(inner_model, "_target_lags", None)
        if lags is None:
            return None
        return [int(value) for value in np.asarray(lags).tolist()]
    except Exception:
        return None


def model_summary(predictor: TimeSeriesPredictor) -> dict:
    info = predictor.info()
    result = {}
    for name, details in info.get("model_info", {}).items():
        result[name] = {
            key: details.get(key)
            for key in ["fit_time", "predict_time", "val_score", "model_weights"]
            if key in details
        }
    return result


def run_validation(data: pd.DataFrame) -> pd.DataFrame:
    target_by_month = data.set_index("referans_ayi")[TARGET]
    origins = pd.date_range(VALIDATION_START, VALIDATION_END, freq=FREQ)
    assert len(origins) == 12
    assert origins.max() == VALIDATION_END
    assert origins.max() < TEST_START
    records = []

    for tier, features in FEATURE_TIERS.items():
        lagged, total_fill_counts = causal_feature_table(data, tier)
        known_names = lagged.columns.tolist()
        write_log(
            FFILL_LOG_PATH,
            f"{tier} FULL_SERIES_FILL_COUNTS="
            + json.dumps(total_fill_counts, ensure_ascii=False),
        )

        for origin_number, origin in enumerate(origins, start=1):
            assert not (TEST_START <= origin <= TEST_END)
            train = make_train_tsdf(data, lagged, origin)
            future_covariates = make_future_known_covariates(lagged, origin)
            target_month = origin + pd.DateOffset(months=PREDICTION_LENGTH)
            actual = float(target_by_month.loc[target_month])
            model_path = MODEL_ROOT / tier / f"origin_{origin:%Y%m}"
            if model_path.exists():
                raise FileExistsError(f"Model dizini zaten var: {model_path}")

            historical_mask = data["referans_ayi"] <= origin
            origin_fill_counts = {}
            for feature in features:
                source = data.loc[historical_mask, feature]
                filled = source.ffill() if feature in FFILL_FEATURES else source
                origin_fill_counts[feature] = int(
                    (source.isna() & filled.notna()).sum()
                )
            if tier in {"T1", "T2"}:
                assert sum(origin_fill_counts.values()) == 0
            write_log(
                FFILL_LOG_PATH,
                f"{tier} {origin:%Y-%m}="
                + json.dumps(origin_fill_counts, ensure_ascii=False),
            )

            write_log(
                FIT_LOG_PATH,
                f"{tier} ORIGIN {origin_number:02d}/12 {origin:%Y-%m} | "
                f"train_n={len(train)} | target={target_month:%Y-%m} | "
                f"known={known_names}",
            )
            started = time.perf_counter()
            predictor = TimeSeriesPredictor(
                prediction_length=PREDICTION_LENGTH,
                freq=FREQ,
                target=TARGET,
                known_covariates_names=known_names,
                eval_metric="MAE",
                eval_metric_seasonal_period=1,
                path=model_path,
                verbosity=1,
                log_to_file=True,
            )
            predictor.fit(
                train_data=train,
                presets=PRESET,
                time_limit=TIME_LIMIT_PER_ORIGIN,
                random_seed=42,
                verbosity=1,
            )
            elapsed = time.perf_counter() - started
            models = predictor.model_names()
            write_log(
                FIT_LOG_PATH,
                f"{tier} FIT_DONE {origin:%Y-%m} | seconds={elapsed:.2f} | "
                f"models={models} | info="
                + json.dumps(model_summary(predictor), default=str),
            )

            lags = direct_tabular_lags(predictor)
            write_log(
                LAG_AUDIT_PATH,
                f"{tier} {origin:%Y-%m} DirectTabular_target_lags="
                + (json.dumps(lags) if lags is not None else "tespit_edilemedi"),
            )

            for model_name in models:
                prediction = predictor.predict(
                    train,
                    known_covariates=future_covariates,
                    model=model_name,
                    random_seed=42,
                )
                records.append(
                    {
                        "kol": tier,
                        "origin": origin,
                        "model": model_name,
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": median_prediction(prediction, target_month),
                    }
                )

            history = target_by_month.loc[:origin]
            records.extend(
                [
                    {
                        "kol": tier,
                        "origin": origin,
                        "model": "sifir",
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": 0.0,
                    },
                    {
                        "kol": tier,
                        "origin": origin,
                        "model": "son12_ortalama",
                        "hedef_ay": target_month,
                        "y_true": actual,
                        "y_pred_q50": float(history.iloc[-12:].mean()),
                    },
                ]
            )
            pd.DataFrame(records).to_csv(
                PREDICTIONS_PATH, index=False, encoding="utf-8-sig"
            )

    result = pd.DataFrame(records)
    assert result["origin"].max() == VALIDATION_END
    assert not (
        (result["origin"] >= TEST_START) & (result["origin"] <= TEST_END)
    ).any()
    return result


def score(predictions: pd.DataFrame) -> pd.DataFrame:
    scored = predictions.copy()
    scored["absolute_error"] = np.abs(scored["y_true"] - scored["y_pred_q50"])
    scored["squared_error"] = (scored["y_true"] - scored["y_pred_q50"]) ** 2
    scored["direction_correct"] = (
        (scored["y_true"] != 0)
        & (np.sign(scored["y_true"]) == np.sign(scored["y_pred_q50"]))
    ).astype(float)
    scored["inverse_direction_correct"] = (
        (scored["y_true"] != 0)
        & (np.sign(scored["y_true"]) == np.sign(-scored["y_pred_q50"]))
    ).astype(float)

    ranking = (
        scored.groupby(["kol", "model"])
        .agg(
            n=("y_true", "size"),
            MAE=("absolute_error", "mean"),
            RMSE=("squared_error", lambda values: np.sqrt(values.mean())),
            DA=("direction_correct", "mean"),
            DA_ters=("inverse_direction_correct", "mean"),
        )
        .reset_index()
    )
    ranking["DA_yuzde"] = 100 * ranking["DA"]
    ranking["DA_ters_yuzde"] = 100 * ranking["DA_ters"]

    for tier in FEATURE_TIERS:
        tier_rows = ranking[ranking["kol"].eq(tier)]
        zero_mae = float(tier_rows.loc[tier_rows["model"].eq("sifir"), "MAE"].iloc[0])
        mean12_mae = float(
            tier_rows.loc[tier_rows["model"].eq("son12_ortalama"), "MAE"].iloc[0]
        )
        assert round(zero_mae, 6) == round(10.330937, 6)
        assert round(mean12_mae, 6) == round(13.461028, 6)
        ranking.loc[ranking["kol"].eq(tier), "MASE_h3_vs_sifir"] = (
            ranking.loc[ranking["kol"].eq(tier), "MAE"] / zero_mae
        )

    return ranking[
        [
            "kol",
            "model",
            "n",
            "MAE",
            "RMSE",
            "DA_yuzde",
            "DA_ters_yuzde",
            "MASE_h3_vs_sifir",
        ]
    ].sort_values(["kol", "MAE"])


def compare_with_t0(predictions: pd.DataFrame) -> pd.DataFrame:
    t0 = pd.read_csv(IP2_PREDICTIONS_PATH, parse_dates=["origin", "hedef_ay"])
    t0 = t0[t0["model"].eq("DirectTabular")][
        ["origin", "hedef_ay", "y_true", "y_pred_q50"]
    ].rename(columns={"y_pred_q50": "T0_tahmin"})
    t0["T0_mutlak_hata"] = np.abs(t0["y_true"] - t0["T0_tahmin"])
    comparison = t0.copy()

    for tier in FEATURE_TIERS:
        tier_predictions = predictions[
            predictions["kol"].eq(tier)
            & predictions["model"].eq("DirectTabular")
        ][["origin", "y_pred_q50"]].rename(
            columns={"y_pred_q50": f"{tier}_tahmin"}
        )
        comparison = comparison.merge(
            tier_predictions, on="origin", how="left", validate="one_to_one"
        )
        comparison[f"{tier}_mutlak_hata"] = np.abs(
            comparison["y_true"] - comparison[f"{tier}_tahmin"]
        )
        comparison[f"{tier}_eksi_T0_hata"] = (
            comparison[f"{tier}_mutlak_hata"] - comparison["T0_mutlak_hata"]
        )
        comparison[f"{tier}_T0dan_iyi"] = (
            comparison[f"{tier}_mutlak_hata"] < comparison["T0_mutlak_hata"]
        )
    return comparison


def invariant_check(predictions: pd.DataFrame) -> pd.DataFrame:
    ip2 = pd.read_csv(IP2_PREDICTIONS_PATH, parse_dates=["origin", "hedef_ay"])
    audit = []
    for model in INVARIANT_MODELS:
        reference = ip2[ip2["model"].eq(model)].set_index("origin")["y_pred_q50"]
        for tier in FEATURE_TIERS:
            current = predictions[
                predictions["kol"].eq(tier) & predictions["model"].eq(model)
            ].set_index("origin")["y_pred_q50"]
            aligned = pd.concat([reference, current], axis=1).dropna()
            max_difference = float(np.abs(aligned.iloc[:, 0] - aligned.iloc[:, 1]).max())
            audit.append(
                {
                    "model": model,
                    "kol": tier,
                    "n": len(aligned),
                    "max_abs_prediction_difference": max_difference,
                    "pass": bool(max_difference <= 1e-8),
                }
            )
    result = pd.DataFrame(audit)
    result.to_csv(
        OUTPUT_DIR / "ip3_k4_tutarlilik.csv", index=False, encoding="utf-8-sig"
    )
    return result


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    protected_outputs = [
        PREDICTIONS_PATH,
        RANKING_PATH,
        COMPARISON_PATH,
        LAG_AUDIT_PATH,
        FFILL_LOG_PATH,
        FIT_LOG_PATH,
    ]
    if any(path.exists() for path in protected_outputs):
        raise FileExistsError("IP-3 çıktıları zaten mevcut; üzerine yazılmadı.")

    data = load_and_validate()
    print("IP3 VERI SOZLESMESI ASSERTLERI GECTI", flush=True)
    predictions = run_validation(data)
    ranking = score(predictions)
    comparison = compare_with_t0(predictions)
    k4 = invariant_check(predictions)

    predictions.to_csv(PREDICTIONS_PATH, index=False, encoding="utf-8-sig")
    ranking.to_csv(RANKING_PATH, index=False, encoding="utf-8-sig")
    comparison.to_csv(COMPARISON_PATH, index=False, encoding="utf-8-sig")

    print("\nIP3 MODEL SIRALAMASI")
    print(ranking.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nT0 ESLESTIRMESI")
    print(comparison.to_string(index=False))
    print("\nK4 TUTARLILIK")
    print(k4.to_string(index=False))
    print("\nTEST BLOKUNA DOKUNULMADI.")


if __name__ == "__main__":
    main()
