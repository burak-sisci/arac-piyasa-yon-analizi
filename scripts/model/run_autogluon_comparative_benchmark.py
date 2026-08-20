# -*- coding: utf-8 -*-
"""AutoGluon TimeSeries ile 4 Araç Piyasası Hedef Değişkeninin Karşılaştırmalı Modellenmesi.

Bu betik:
1. 'data/birlesik_veri_seti/arac_piyasasi_master_veri_seti.csv' dosyasını okur.
2. Aşağıdaki 4 hedef değişken için modelleri ayrı ayrı eğitir ve test eder:
   - target_betam_dom_gun (Days on Market / Ortalama ilan kalış süresi - Gün)
   - target_indicata_satis_ilan_orani_pct (İkinci El Satış / İlan Dönüşüm Oranı - %)
   - target_devir_orani (Noter Devri / Trafikteki Araç Parkı Devir Oranı)
   - target_1ay_hiz (Noter Devir Hacmi Aylık Log Büyüme Hızı - %)
3. Takvim (mevsimsellik) ve sızıntısız gecikmeli makro göstergeleri kovaryat olarak kullanır.
4. Her target için AutoGluon TimeSeries modellerini koşturur.
5. Karşılaştırmalı liderlik tablolarını, tahmin metriklerini (MAE, RMSE, MAPE, R²) ve grafikleri 'outputs/autogluon_target_karsilastirma/' dizinine kaydeder.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

# Windows console encoding fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "birlesik_veri_seti" / "arac_piyasasi_master_veri_seti.csv"
OUT_DIR = PROJECT_ROOT / "outputs" / "autogluon_target_karsilastirma"
DATE_COL = "referans_ayi"
PREDICTION_LENGTH = 3
FREQ = "MS"

TARGET_CONFIGS = [
    {
        "name": "target_betam_dom_gun",
        "display_name": "Days on Market (BETAM DOM - Gun)",
        "unit": "Gun",
        "eval_metric": "MAE",
        "time_limit": 90,
    },
    {
        "name": "target_indicata_satis_ilan_orani_pct",
        "display_name": "Satis / Ilan Orani (Indicata %)",
        "unit": "%",
        "eval_metric": "MAE",
        "time_limit": 90,
    },
    {
        "name": "target_devir_orani",
        "display_name": "Piyasa Devir Orani (Noter / Park)",
        "unit": "Oran",
        "eval_metric": "MAE",
        "time_limit": 120,
    },
    {
        "name": "target_1ay_hiz",
        "display_name": "1 Aylik Hacim Buyume Hizi (% Log)",
        "unit": "%",
        "eval_metric": "MAE",
        "time_limit": 120,
    },
]


def prepare_target_data(df: pd.DataFrame, target_name: str) -> tuple[pd.DataFrame, list[str]]:
    """İlgili target için temizlenmiş, sızıntısız ve kovaryatları hazırlanmış DataFrame üretir."""
    sub = df.dropna(subset=[target_name]).copy()
    sub[DATE_COL] = pd.to_datetime(sub[DATE_COL])
    sub = sub.sort_values(DATE_COL).reset_index(drop=True)

    # 1. Takvim ve Mevsimsellik Özellikleri (Bilinen gelecek / bilinen takvim)
    sub["sin_ay"] = np.sin(2 * np.pi * sub[DATE_COL].dt.month / 12.0)
    sub["cos_ay"] = np.cos(2 * np.pi * sub[DATE_COL].dt.month / 12.0)
    sub["ay"] = sub[DATE_COL].dt.month
    sub["ceyrek"] = sub[DATE_COL].dt.quarter

    covariates = ["sin_ay", "cos_ay", "ay", "ceyrek"]

    # 2. Makro Göstergeler (Sızıntıyı önlemek için 1 ay gecikmeli lag-1 kullanılır)
    macro_cols = [
        "tasit_kredisi_faiz",
        "tufe_aylik_degisim",
        "usdtry_ortalama",
        "tuketici_guven_endeksi",
        "otv_event_ay_mi",
    ]
    for col in macro_cols:
        if col in sub.columns:
            lag_name = f"{col}_lag1"
            sub[lag_name] = sub[col].shift(1)
            covariates.append(lag_name)

    # İlk satırda lag kaynaklı NaN oluşursa bfill yap
    sub = sub.bfill().ffill()

    # Model DataFrame
    keep_cols = [DATE_COL, target_name, *covariates]
    clean_df = sub[keep_cols].copy()
    clean_df["item_id"] = "TR_otomobil"
    return clean_df, covariates


def evaluate_target(config: dict, master_df: pd.DataFrame) -> dict:
    """Tek bir target için AutoGluon TimeSeries eğitim ve test sürecini yürütür."""
    target_name = config["name"]
    display_name = config["display_name"]
    unit = config["unit"]
    eval_metric = config["eval_metric"]
    time_limit = config["time_limit"]

    print(f"\n=======================================================")
    print(f"[*] MODEL EGITIMI: {display_name}")
    print(f"=======================================================")

    clean_df, covariates = prepare_target_data(master_df, target_name)
    total_len = len(clean_df)
    train_len = total_len - PREDICTION_LENGTH

    print(f"Toplam Gozlem: {total_len} ay ({clean_df[DATE_COL].min().strftime('%Y-%m')} -> {clean_df[DATE_COL].max().strftime('%Y-%m')})")
    print(f"Egitim Seti: {train_len} ay | Test Seti: {PREDICTION_LENGTH} ay")
    print(f"Kovaryatlar ({len(covariates)}): {covariates}")

    # AutoGluon TimeSeriesDataFrame
    ts_df = TimeSeriesDataFrame.from_data_frame(
        clean_df,
        id_column="item_id",
        timestamp_column=DATE_COL,
    )

    train_data = ts_df.slice_by_timestep(None, -PREDICTION_LENGTH)
    test_data = ts_df

    model_dir = OUT_DIR / "ag_models" / target_name
    if model_dir.exists():
        shutil.rmtree(model_dir, ignore_errors=True)

    predictor = TimeSeriesPredictor(
        target=target_name,
        prediction_length=PREDICTION_LENGTH,
        eval_metric=eval_metric,
        freq=FREQ,
        path=str(model_dir),
    )

    predictor.fit(
        train_data=train_data,
        presets="medium_quality",
        time_limit=time_limit,
    )

    # Test Tahmini
    predictions = predictor.predict(train_data)
    pred_df = predictions.loc["TR_otomobil"].reset_index()
    pred_df[DATE_COL] = pd.to_datetime(pred_df["timestamp"])

    # Test gerçek değerleri
    actual_test_df = clean_df.iloc[-PREDICTION_LENGTH:].copy()
    merged_test = actual_test_df[[DATE_COL, target_name]].merge(
        pred_df[[DATE_COL, "mean", "0.1", "0.9"]],
        on=DATE_COL,
        how="inner",
    )

    # Hata Metrikleri
    y_true = merged_test[target_name].values
    y_pred = merged_test["mean"].values
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mape = float(np.mean(np.abs((y_true - y_pred) / (y_true + 1e-6)))) * 100.0
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    ss_res = np.sum((y_true - y_pred) ** 2)
    r2 = float(1.0 - (ss_res / (ss_tot + 1e-6)))

    # Leaderboard
    leaderboard = predictor.leaderboard(test_data, silent=True)
    best_model_name = predictor.model_best

    print(f"\n[OK] {display_name} - Test Sonuclari:")
    print(f"En Iyi Model: {best_model_name}")
    print(f"MAE: {mae:.4f} {unit} | RMSE: {rmse:.4f} {unit} | MAPE: {mape:.2f}% | R2: {r2:.4f}")

    # Leaderboard kaydet
    target_out_dir = OUT_DIR / target_name
    target_out_dir.mkdir(parents=True, exist_ok=True)
    leaderboard.to_csv(target_out_dir / "leaderboard.csv", index=False)
    merged_test.to_csv(target_out_dir / "test_tahminleri_karsilastirma.csv", index=False)

    # Tahmin Grafiği Çiz ve Kaydet
    plt.figure(figsize=(10, 5))
    history_plot_len = min(24, len(clean_df))
    hist_df = clean_df.iloc[-history_plot_len:]
    plt.plot(hist_df[DATE_COL], hist_df[target_name], label="Gercek Degerler", color="#1f77b4", marker="o", linewidth=2)
    plt.plot(merged_test[DATE_COL], merged_test["mean"], label=f"Tahmin ({best_model_name})", color="#d62728", marker="s", linestyle="--", linewidth=2)
    plt.fill_between(
        merged_test[DATE_COL],
        merged_test["0.1"],
        merged_test["0.9"],
        color="#d62728",
        alpha=0.2,
        label="%80 Guven Araligi (p10-p90)",
    )
    plt.title(f"{display_name} - Gercek vs AutoGluon Tahmini (h=3)")
    plt.xlabel("Tarih")
    plt.ylabel(f"Deger ({unit})")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plot_path = target_out_dir / "gercek_vs_tahmin_grafigi.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()

    return {
        "target_name": target_name,
        "display_name": display_name,
        "unit": unit,
        "gozlem_sayisi": total_len,
        "egitim_ayi": train_len,
        "test_ayi": PREDICTION_LENGTH,
        "tarih_araligi": f"{clean_df[DATE_COL].min().strftime('%Y-%m')} -> {clean_df[DATE_COL].max().strftime('%Y-%m')}",
        "en_iyi_model": best_model_name,
        "test_mae": mae,
        "test_rmse": rmse,
        "test_mape_pct": mape,
        "test_r2": r2,
        "test_aylari": [d.strftime("%Y-%m") for d in merged_test[DATE_COL]],
        "gercek_degerler": [round(float(v), 4) for v in y_true],
        "tahmin_degerleri": [round(float(v), 4) for v in y_pred],
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    master_df = pd.read_csv(DATA_PATH)

    summary_results = []
    for config in TARGET_CONFIGS:
        try:
            res = evaluate_target(config, master_df)
            summary_results.append(res)
        except Exception as e:
            print(f"[ERR] {config['display_name']} icin hata olustu: {e}")

    # Karşılaştırma Özeti Tablosu
    summary_df = pd.DataFrame(
        [
            {
                "Hedef Degisken": r["display_name"],
                "Birim": r["unit"],
                "Gozlem Sayisi": r["gozlem_sayisi"],
                "Tarih Araligi": r["tarih_araligi"],
                "En Iyi Model": r["en_iyi_model"],
                "Test MAE": round(r["test_mae"], 4),
                "Test RMSE": round(r["test_rmse"], 4),
                "Test MAPE (%)": round(r["test_mape_pct"], 2),
                "Test R2": round(r["test_r2"], 4),
            }
            for r in summary_results
        ]
    )

    summary_csv = OUT_DIR / "target_karsilastirma_ozeti.csv"
    summary_xlsx = OUT_DIR / "target_karsilastirma_ozeti.xlsx"
    summary_json = OUT_DIR / "target_karsilastirma_detay.json"

    summary_df.to_csv(summary_csv, index=False, encoding="utf-8-sig")
    summary_df.to_excel(summary_xlsx, index=False)
    summary_json.write_text(json.dumps(summary_results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=======================================================")
    print("[SUMMARY] TUM HEDEF DEGISKENLER ICIN KARSILASTIRMA OZETI")
    print("=======================================================")
    print(summary_df.to_string(index=False))
    print(f"\nSonuclar kaydedildi:\n - CSV: {summary_csv}\n - Excel: {summary_xlsx}\n - JSON: {summary_json}")


if __name__ == "__main__":
    main()
