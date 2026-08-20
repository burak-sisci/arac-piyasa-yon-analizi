from pathlib import Path

import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "outputs" / "autogluon" / "ip7_devir_orani" / "ag_model"
DATA_FILE = ROOT / "data" / "birlesik_target_setleri" / "target_devir_orani_model_final.csv"
OUTPUT = Path(__file__).with_name("recursive_tabular_feature_importance.csv")

DATE = "referans_ayi"
TARGET = "target_devir_orani"
ITEM_ID = "TR_otomobil"
MODEL = "RecursiveTabular"

frame = pd.read_csv(DATA_FILE, parse_dates=[DATE])
features = [column for column in frame.columns if column not in {DATE, TARGET}]
predictor = TimeSeriesPredictor.load(MODEL_DIR)


def to_tsdf(data: pd.DataFrame) -> TimeSeriesDataFrame:
    prepared = data[[DATE, TARGET, *features]].rename(columns={DATE: "timestamp"}).copy()
    prepared.insert(0, "item_id", ITEM_ID)
    return TimeSeriesDataFrame.from_data_frame(
        prepared,
        id_column="item_id",
        timestamp_column="timestamp",
    )


test_months = pd.date_range("2026-01-01", "2026-06-01", freq="MS")
monthly_results = []

for month_number, month in enumerate(test_months, start=1):
    # Son satır gerçek hedef olarak AutoGluon tarafından holdout edilir.
    evaluation_data = frame.loc[frame[DATE].le(month)].copy()
    importance = predictor.feature_importance(
        data=to_tsdf(evaluation_data),
        model=MODEL,
        metric="MASE",
        features=features,
        method="permutation",
        num_iterations=10,
        random_seed=42 + month_number,
        relative_scores=False,
        include_confidence_band=True,
        confidence_level=0.95,
    ).reset_index().rename(columns={"index": "feature"})
    importance.insert(0, "test_ayi", month.strftime("%Y-%m"))
    monthly_results.append(importance)
    print(f"Tamamlandı: {month:%Y-%m}")

monthly = pd.concat(monthly_results, ignore_index=True)
monthly.to_csv(Path(__file__).with_name("recursive_tabular_feature_importance_aylik.csv"), index=False, encoding="utf-8-sig")

summary = (
    monthly.groupby("feature", as_index=False)
    .agg(
        importance=("importance", "mean"),
        importance_stddev=("importance", "std"),
        pozitif_ay_sayisi=("importance", lambda values: int((values > 0).sum())),
        negatif_ay_sayisi=("importance", lambda values: int((values < 0).sum())),
        test_ayi_sayisi=("importance", "size"),
    )
    .sort_values("importance", ascending=False)
    .reset_index(drop=True)
)
summary.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

print(OUTPUT)
print(summary.to_string(index=False))
