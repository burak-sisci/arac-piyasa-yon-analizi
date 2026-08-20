"""IP-2: covariance-free AutoGluon h=3 rolling-origin validation.

The target is indexed by its realization month. Only the third forecast step is
scored. The reserved 2025-04..2026-03 test origins are never evaluated here.
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
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "autogluon" / "ip2_medium"
MODEL_ROOT = OUTPUT_DIR / "ag_models"
PREDICTIONS_PATH = OUTPUT_DIR / "ip2_h3_tahminler.csv"
RANKING_PATH = OUTPUT_DIR / "ip2_h3_model_siralama.csv"
FIT_LOG_PATH = OUTPUT_DIR / "ip2_fit_log.txt"

ITEM_ID = "TR_otomobil"
TARGET = "target_3ay_hiz"
FREQ = "MS"
PREDICTION_LENGTH = 3
VALIDATION_START = pd.Timestamp("2024-04-01")
VALIDATION_END = pd.Timestamp("2025-03-01")
TEST_START = pd.Timestamp("2025-04-01")
TEST_END = pd.Timestamp("2026-03-01")
TIME_LIMIT_PER_ORIGIN = 300
MIN_MODELS_PER_ORIGIN = 4
PRESET = "medium_quality"


def append_log(message: str) -> None:
    print(message, flush=True)
    with FIT_LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


def load_and_validate() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    required = {"referans_ayi", TARGET}
    missing = required.difference(data.columns)
    if missing:
        raise KeyError(f"Eksik zorunlu sütunlar: {sorted(missing)}")

    data["referans_ayi"] = pd.to_datetime(
        data["referans_ayi"], errors="raise"
    )
    data[TARGET] = pd.to_numeric(data[TARGET], errors="raise")
    data = data.sort_values("referans_ayi").reset_index(drop=True)

    # IP-1 contract assertions, repeated deliberately.
    assert data["referans_ayi"].is_monotonic_increasing
    assert not data["referans_ayi"].duplicated().any()
    expected_months = pd.date_range(
        data["referans_ayi"].min(),
        data["referans_ayi"].max(),
        freq=FREQ,
    )
    assert len(expected_months) == len(data)
    assert data["referans_ayi"].equals(
        pd.Series(expected_months, name="referans_ayi")
    )
    assert data[TARGET].notna().all()
    assert np.isfinite(data[TARGET].to_numpy()).all()
    return data


def to_tsdf(data: pd.DataFrame) -> TimeSeriesDataFrame:
    univariate = data[["referans_ayi", TARGET]].rename(
        columns={"referans_ayi": "timestamp"}
    )
    univariate.insert(0, "item_id", ITEM_ID)
    tsdf = TimeSeriesDataFrame.from_data_frame(
        univariate,
        id_column="item_id",
        timestamp_column="timestamp",
    )
    assert tsdf.freq == FREQ, f"Beklenen freq={FREQ}, bulunan={tsdf.freq}"
    assert len(tsdf) == 97, f"Beklenen 97 satır, bulunan {len(tsdf)}"
    return tsdf


def median_prediction(prediction: TimeSeriesDataFrame, target_month: pd.Timestamp) -> float:
    median_column = "0.5" if "0.5" in prediction.columns else 0.5
    if median_column not in prediction.columns:
        raise KeyError(
            f"Medyan tahmin sütunu yok. Sütunlar: {prediction.columns.tolist()}"
        )
    key = (ITEM_ID, target_month)
    if key not in prediction.index:
        raise KeyError(f"Tahminde hedef ay bulunamadı: {key}")
    return float(prediction.loc[key, median_column])


def compact_model_info(predictor: TimeSeriesPredictor) -> dict:
    info = predictor.info()
    model_info = info.get("model_info", {}) if isinstance(info, dict) else {}
    compact = {}
    for model_name, details in model_info.items():
        if not isinstance(details, dict):
            compact[model_name] = str(details)
            continue
        compact[model_name] = {
            key: details.get(key)
            for key in [
                "model_type",
                "fit_time",
                "predict_time",
                "val_score",
                "hyperparameters",
                "model_weights",
            ]
            if key in details
        }
    return compact


def build_validation_predictions(
    data: pd.DataFrame, tsdf: TimeSeriesDataFrame
) -> pd.DataFrame:
    target_by_month = data.set_index("referans_ayi")[TARGET]
    origins = pd.date_range(VALIDATION_START, VALIDATION_END, freq=FREQ)
    assert len(origins) == 12
    assert origins.max() == VALIDATION_END
    assert origins.max() < TEST_START

    records: list[dict] = []
    for origin_number, origin in enumerate(origins, start=1):
        model_path = MODEL_ROOT / f"origin_{origin:%Y%m}"
        if model_path.exists():
            raise FileExistsError(
                f"Model dizini zaten var; yanlışlıkla üzerine yazılmayacak: {model_path}"
            )

        train = tsdf.loc[
            tsdf.index.get_level_values("timestamp") <= origin
        ]
        train_max = train.index.get_level_values("timestamp").max()
        assert train_max == origin
        target_month = origin + pd.DateOffset(months=PREDICTION_LENGTH)
        assert target_month in target_by_month.index
        assert not (TEST_START <= origin <= TEST_END)

        append_log(
            f"ORIGIN {origin_number:02d}/12 {origin:%Y-%m} | "
            f"train_n={len(train)} | target={target_month:%Y-%m}"
        )
        start_time = time.perf_counter()
        predictor = TimeSeriesPredictor(
            prediction_length=PREDICTION_LENGTH,
            freq=FREQ,
            target=TARGET,
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
        elapsed = time.perf_counter() - start_time
        model_names = predictor.model_names()
        append_log(
            f"FIT_DONE {origin:%Y-%m} | seconds={elapsed:.2f} | "
            f"models={len(model_names)} | names={model_names}"
        )

        if len(model_names) < MIN_MODELS_PER_ORIGIN:
            raise RuntimeError(
                f"{origin:%Y-%m}: yalnız {len(model_names)} model eğitildi; "
                f"en az {MIN_MODELS_PER_ORIGIN} gerekli."
            )

        model_info = compact_model_info(predictor)
        append_log(
            "MODEL_INFO "
            + origin.strftime("%Y-%m")
            + " | "
            + json.dumps(model_info, ensure_ascii=False, default=str)
        )

        actual = float(target_by_month.loc[target_month])
        for model_name in model_names:
            try:
                prediction = predictor.predict(
                    train,
                    model=model_name,
                    random_seed=42,
                )
                predicted = median_prediction(prediction, target_month)
            except Exception as error:
                append_log(
                    f"PREDICT_ERROR {origin:%Y-%m} | {model_name} | "
                    f"{type(error).__name__}: {error}"
                )
                continue
            records.append(
                {
                    "origin": origin,
                    "model": model_name,
                    "hedef_ay": target_month,
                    "y_true": actual,
                    "y_pred_q50": predicted,
                }
            )

        history = target_by_month.loc[:origin]
        records.extend(
            [
                {
                    "origin": origin,
                    "model": "sifir",
                    "hedef_ay": target_month,
                    "y_true": actual,
                    "y_pred_q50": 0.0,
                },
                {
                    "origin": origin,
                    "model": "son12_ortalama",
                    "hedef_ay": target_month,
                    "y_true": actual,
                    "y_pred_q50": float(history.iloc[-12:].mean()),
                },
            ]
        )

        # Persist after every origin so a later failure leaves an audit trail.
        partial = pd.DataFrame(records)
        partial.to_csv(PREDICTIONS_PATH, index=False, encoding="utf-8-sig")

    predictions = pd.DataFrame(records)
    assert predictions["origin"].max() == VALIDATION_END
    assert not (
        (predictions["origin"] >= TEST_START)
        & (predictions["origin"] <= TEST_END)
    ).any()
    return predictions


def score_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    predictions = predictions.copy()
    predictions["absolute_error"] = np.abs(
        predictions["y_true"] - predictions["y_pred_q50"]
    )
    predictions["squared_error"] = (
        predictions["y_true"] - predictions["y_pred_q50"]
    ) ** 2
    nonzero_actual = predictions["y_true"] != 0
    predictions["direction_correct"] = (
        nonzero_actual
        & (
            np.sign(predictions["y_pred_q50"])
            == np.sign(predictions["y_true"])
        )
    ).astype(float)
    predictions["inverse_direction_correct"] = (
        nonzero_actual
        & (
            np.sign(-predictions["y_pred_q50"])
            == np.sign(predictions["y_true"])
        )
    ).astype(float)

    ranking = (
        predictions.groupby("model")
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

    zero_mae = float(ranking.loc[ranking["model"].eq("sifir"), "MAE"].iloc[0])
    mean12_mae = float(
        ranking.loc[ranking["model"].eq("son12_ortalama"), "MAE"].iloc[0]
    )
    assert round(zero_mae, 4) == 10.3309, (
        f"Sıfır baseline IP-1 ile eşleşmedi: {zero_mae:.6f}"
    )
    assert round(mean12_mae, 4) == 13.4610, (
        f"Son12 baseline IP-1 ile eşleşmedi: {mean12_mae:.6f}"
    )

    ranking["MASE_h3_vs_sifir"] = ranking["MAE"] / zero_mae
    ranking = ranking.sort_values(["MAE", "model"]).reset_index(drop=True)
    return ranking[
        [
            "model",
            "n",
            "MAE",
            "RMSE",
            "DA_yuzde",
            "DA_ters_yuzde",
            "MASE_h3_vs_sifir",
        ]
    ]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_ROOT.mkdir(parents=True, exist_ok=True)
    if FIT_LOG_PATH.exists() or PREDICTIONS_PATH.exists() or RANKING_PATH.exists():
        raise FileExistsError(
            "IP-2 çıktı dosyaları zaten mevcut; denetlenebilirliği korumak için "
            "otomatik üzerine yazılmadı."
        )

    data = load_and_validate()
    tsdf = to_tsdf(data)
    append_log("SOZLESME ASSERTLERI 8/8 GECTI")
    append_log(
        "PRESET=medium_quality; EXPLICIT_HYPERPARAMETERS=False; "
        "KNOWN_COVARIATES=False"
    )
    predictions = build_validation_predictions(data, tsdf)
    ranking = score_predictions(predictions)
    predictions.to_csv(PREDICTIONS_PATH, index=False, encoding="utf-8-sig")
    ranking.to_csv(RANKING_PATH, index=False, encoding="utf-8-sig")

    print("\nIP2 H3 MODEL SIRALAMASI")
    print(ranking.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nTEST BLOKUNA DOKUNULMADI.")
    print("Tahminler:", PREDICTIONS_PATH)
    print("Sıralama:", RANKING_PATH)
    print("Fit log:", FIT_LOG_PATH)


if __name__ == "__main__":
    main()
