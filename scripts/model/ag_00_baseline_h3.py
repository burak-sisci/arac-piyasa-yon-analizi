"""Leakage-safe h=3 baselines for the realization-index target_3ay_hiz.

This script deliberately does not train AutoGluon and never evaluates the
reserved test origins. It establishes the validation threshold that later
models must beat.
"""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "birlesik_target_setleri"
    / "target_3ay_hiz_tum_featurelar_final.csv"
)
TARGET = "target_3ay_hiz"
HORIZON = 3
VALIDATION_START = pd.Timestamp("2024-04-01")
VALIDATION_END = pd.Timestamp("2025-03-01")
TEST_START = pd.Timestamp("2025-04-01")
TEST_END = pd.Timestamp("2026-03-01")


def load_and_validate():
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

    # Kavanoz'un istediği beş sözleşme kontrolü.
    assert data["referans_ayi"].is_monotonic_increasing, (
        "referans_ayi kronolojik artmıyor."
    )
    assert not data["referans_ayi"].duplicated().any(), (
        "Yinelenen referans_ayi bulundu."
    )
    expected_months = pd.date_range(
        data["referans_ayi"].min(),
        data["referans_ayi"].max(),
        freq="MS",
    )
    assert len(expected_months) == len(data) and data[
        "referans_ayi"
    ].equals(pd.Series(expected_months, name="referans_ayi")), (
        "Aylık zaman ekseninde boşluk bulundu."
    )
    assert data[TARGET].notna().all(), "Target içinde NaN bulundu."
    assert np.isfinite(data[TARGET].to_numpy()).all(), (
        "Target içinde sonsuz değer bulundu."
    )
    return data


def mase_scale(history):
    """Period-1 in-sample naive error, using only information at origin T."""
    differences = np.abs(np.diff(np.asarray(history, dtype=float)))
    if len(differences) == 0 or not np.isfinite(differences.mean()):
        raise ValueError("MASE ölçeği hesaplanamadı.")
    return float(differences.mean())


def build_origin_records(data):
    series = data.set_index("referans_ayi")[TARGET]
    records = []

    # All four baselines need at least twelve realized target observations.
    for origin_position in range(11, len(data)):
        origin = data.loc[origin_position, "referans_ayi"]
        outcome_month = origin + pd.DateOffset(months=HORIZON)
        if outcome_month not in series.index:
            continue

        # The reserved test block must never be evaluated by this script.
        if TEST_START <= origin <= TEST_END:
            continue
        if origin > VALIDATION_END:
            continue

        history = series.loc[:origin]
        actual = float(series.loc[outcome_month])
        scale = mase_scale(history)
        seasonal_reference = outcome_month - pd.DateOffset(months=12)
        if seasonal_reference not in series.index:
            continue

        predictions = {
            "naive_son_deger": float(history.iloc[-1]),
            "sifir": 0.0,
            "mevsimsel_naive": float(series.loc[seasonal_reference]),
            "son12_ortalama": float(history.iloc[-12:].mean()),
        }
        block = "VALIDASYON" if VALIDATION_START <= origin else "GECMIS"

        for model, prediction in predictions.items():
            error = actual - prediction
            # Zero is intentionally treated as no directional claim.
            direction_correct = (
                np.nan
                if prediction == 0
                else float(np.sign(prediction) == np.sign(actual))
            )
            records.append(
                {
                    "blok": block,
                    "origin": origin,
                    "gerceklesme_ayi": outcome_month,
                    "model": model,
                    "gercek": actual,
                    "tahmin": prediction,
                    "hata": error,
                    "mutlak_hata": abs(error),
                    "kare_hata": error**2,
                    "mase_hata": abs(error) / scale,
                    "yon_dogru": direction_correct,
                }
            )

    result = pd.DataFrame(records)
    assert not result.empty, "Değerlendirilebilir origin bulunamadı."
    assert not (
        (result["origin"] >= TEST_START) & (result["origin"] <= TEST_END)
    ).any(), "Dokunulmaz test originleri yanlışlıkla değerlendirildi."
    return result


def summarize(records):
    summary = (
        records.groupby(["blok", "model"], sort=False)
        .agg(
            n=("gercek", "size"),
            MAE=("mutlak_hata", "mean"),
            RMSE=("kare_hata", lambda values: np.sqrt(values.mean())),
            DA=("yon_dogru", "mean"),
            MASE_h3=("mase_hata", "mean"),
        )
        .reset_index()
    )
    summary["DA_yuzde"] = 100 * summary["DA"]
    return summary[["blok", "model", "n", "MAE", "RMSE", "DA_yuzde", "MASE_h3"]]


def validation_direction_base_rate(records):
    validation_actual = (
        records.loc[records["blok"].eq("VALIDASYON"), ["origin", "gercek"]]
        .drop_duplicates("origin")
        .set_index("origin")["gercek"]
    )
    positive = int((validation_actual > 0).sum())
    negative = int((validation_actual < 0).sum())
    zero = int((validation_actual == 0).sum())
    directional_n = positive + negative
    majority_rate = (
        100 * max(positive, negative) / directional_n
        if directional_n
        else np.nan
    )
    return positive, negative, zero, majority_rate


def main():
    data = load_and_validate()
    records = build_origin_records(data)
    summary = summarize(records)
    positive, negative, zero, majority_rate = validation_direction_base_rate(
        records
    )

    print("VERI SOZLESMESI: 5/5 ASSERT GECTI")
    print("Dosya:", DATA_PATH)
    print(
        "Target realization araligi:",
        data["referans_ayi"].min().strftime("%Y-%m"),
        "->",
        data["referans_ayi"].max().strftime("%Y-%m"),
    )
    print("Tahmin ufku: h=3")
    print("\nBASELINE SONUCLARI (TEST HARIC)")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("\nVALIDASYON YON TABAN ORANI")
    print(
        f"Pozitif={positive}, Negatif={negative}, Sifir={zero}, "
        f"Cogunluk_sinifi_orani={majority_rate:.2f}%"
    )
    print("\nTEST BLOKUNA AIT HICBIR METRIK HESAPLANMADI.")


if __name__ == "__main__":
    main()
