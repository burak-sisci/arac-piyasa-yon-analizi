# -*- coding: utf-8 -*-
"""1 Aylık (h=1) Days on Market Yön ve Seviye Modelleme Betiği.

Bu betik:
1. 18 seçilmiş filtrelenmiş feature ile veriyi hazırlar.
2. 6 ay validasyon + 6 ay test kurgusu ile AutoGluon TimeSeries modellerini eğitir (prediction_length=1).
3. 2026-01 ile 2026-06 arasındaki 6 test ayı için her ay 1 adım ileri rolling tahmin üretir.
4. "Gelecek ay piyasa satış süresi artacak mı (yavaşlama), düşecek mi (hızlanma)?" yön sınıflandırmasını değerlendirir.
5. Her model için:
   - Doğru Yön Tahmin Sayısı (X/6) ve Yüzdesi (%)
   - MAE, RMSE, MASE, Bias metrikleri
   - Özel görsel tahmin ve yön grafikleri üretir.
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
OUT_DIR = PROJECT_ROOT / "outputs" / "betam_dom_h1_aylik"
TARGET = "target_betam_dom_gun"
DATE_COL = "referans_ayi"
PREDICTION_LENGTH = 1
NUM_VAL_WINDOWS = 6
TEST_MONTHS_COUNT = 6
FREQ = "MS"

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Veriyi hazırlar ve 18 seçilmiş feature'ı üretir."""
    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    sub = df[(df[DATE_COL] >= "2024-01-01") & (df[DATE_COL] <= "2026-06-01")].copy()
    sub = sub.sort_values(DATE_COL).reset_index(drop=True)

    # Eksik ayları enterpolasyonla tamamla
    sub[TARGET] = sub[TARGET].interpolate(method="linear")

    # 18 Seçilmiş Feature
    model_df = pd.DataFrame({DATE_COL: sub[DATE_COL], TARGET: sub[TARGET]})
    model_df["ay"] = sub[DATE_COL].dt.month
    model_df["sin_ay"] = np.sin(2 * np.pi * model_df["ay"] / 12.0)
    model_df["cos_ay"] = np.cos(2 * np.pi * model_df["ay"] / 12.0)

    lag_cols = [
        "betam_satis_orani_pct",
        "noter_devir_otomobil_adet",
        "arabam_reel_aylik_degisim_pct",
        "tufe_yillik_degisim",
        "indicata_satisa_donen_adet",
        "otv_event_ay_mi",
        "otomobil_satinalma_ihtimali_endeksi",
        "indicata_ilan_yayinlanan_adet",
        "usdtry_ortalama",
        "enag_aylik_degisim",
        "tasit_kredisi_faiz",
        "betam_talep_aylik_pct",
        "indicata_satis_ilan_orani_pct",
        "tuketici_guven_endeksi",
        "odmd_otomobil_adet",
    ]

    for col in lag_cols:
        if col in sub.columns:
            model_df[f"{col}_lag1"] = sub[col].shift(1)

    model_df = model_df.bfill().ffill()
    feature_cols = [c for c in model_df.columns if c not in [DATE_COL, TARGET]]
    model_df["item_id"] = "TR_otomobil"
    return model_df, feature_cols


def run_h1_rolling_evaluation():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "modeller").mkdir(parents=True, exist_ok=True)

    master_df = pd.read_csv(DATA_PATH)
    clean_df, feature_cols = prepare_data(master_df)

    total_months = len(clean_df)  # 30 ay
    train_val_len = total_months - TEST_MONTHS_COUNT  # 24 ay (2024-01 -> 2025-12)

    print(f"=======================================================")
    print(f"[*] 1 AYLIK (h=1) ROLLING TAHMIN VE YON ANALIZI")
    print(f"Toplam Veri: {total_months} ay | Egitim+Validasyon: {train_val_len} ay | Test: {TEST_MONTHS_COUNT} ay")
    print(f"Validasyon Penceresi: {NUM_VAL_WINDOWS} ay | Secilen Feature Sayisi: {len(feature_cols)}")
    print(f"=======================================================")

    # TimeSeriesDataFrame
    ts_df = TimeSeriesDataFrame.from_data_frame(
        clean_df,
        id_column="item_id",
        timestamp_column=DATE_COL,
    )

    # Model eğitimi için ilk 24 ayı kullan (2025-07..2025-12 arası 6 validasyon penceresi)
    train_val_data = ts_df.slice_by_timestep(None, -TEST_MONTHS_COUNT)

    model_dir = OUT_DIR / "ag_model"
    if model_dir.exists():
        shutil.rmtree(model_dir, ignore_errors=True)

    predictor = TimeSeriesPredictor(
        target=TARGET,
        prediction_length=PREDICTION_LENGTH,
        eval_metric="MAE",
        freq=FREQ,
        path=str(model_dir),
    )

    predictor.fit(
        train_data=train_val_data,
        presets="medium_quality",
        time_limit=180,
        num_val_windows=NUM_VAL_WINDOWS,
    )

    all_models = predictor.model_names()
    print(f"\nEgitilen Modeller: {all_models}")

    # 6 Test Ayı İçin Rolling 1-Adım İleri Tahminler
    # Test ayları: 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06
    test_indices = list(range(train_val_len, total_months))
    test_dates = [clean_df.loc[i, DATE_COL] for i in test_indices]
    actual_values = [clean_df.loc[i, TARGET] for i in test_indices]
    prev_values = [clean_df.loc[i - 1, TARGET] for i in test_indices]

    # Gerçek yönler: sign(actual - prev)
    actual_directions = [
        "YUKARI (Yavaslama)" if act > prv else ("ASAGI (Hizlanma)" if act < prv else "SABIT")
        for act, prv in zip(actual_values, prev_values)
    ]

    model_summaries = []
    detailed_predictions = []

    for model_name in all_models:
        preds_for_model = []
        pred_directions = []
        is_correct_list = []

        # 6 adım için rolling tahmin
        for step_idx, t_idx in enumerate(test_indices):
            # t_idx anındaki ayı tahmin etmek için 0..t_idx-1 arasındaki veriyi ver
            cutoff_ts_data = ts_df.slice_by_timestep(None, -(total_months - t_idx))
            pred_step = predictor.predict(cutoff_ts_data, model=model_name)
            pred_val = float(pred_step.loc["TR_otomobil", "mean"].iloc[0])
            preds_for_model.append(pred_val)

            # Tahmin edilen yön: sign(pred_val - prev_val)
            prv = prev_values[step_idx]
            act = actual_values[step_idx]
            act_dir = actual_directions[step_idx]

            pred_dir = (
                "YUKARI (Yavaslama)" if pred_val > prv else ("ASAGI (Hizlanma)" if pred_val < prv else "SABIT")
            )
            pred_directions.append(pred_dir)

            # Yön doğru mu?
            correct = (
                (pred_val > prv and act > prv) or
                (pred_val < prv and act < prv) or
                (abs(pred_val - prv) < 1e-4 and abs(act - prv) < 1e-4)
            )
            is_correct_list.append(correct)

            detailed_predictions.append({
                "Model": model_name,
                "Referans_Ayi": test_dates[step_idx].strftime("%Y-%m"),
                "Onceki_Ay_DOM": round(prv, 2),
                "Gercek_DOM": round(act, 2),
                "Tahmin_DOM": round(pred_val, 2),
                "Mutlak_Hata": round(abs(act - pred_val), 3),
                "Gercek_Yon": act_dir,
                "Tahmin_Yon": pred_dir,
                "Yon_Dogru_Mu": "DOGRU (1)" if correct else "YANLIS (0)",
            })

        # Metrikler
        y_true_arr = np.array(actual_values)
        y_pred_arr = np.array(preds_for_model)
        y_prev_arr = np.array(prev_values)

        errors = y_pred_arr - y_true_arr
        mae = float(np.mean(np.abs(errors)))
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        bias = float(np.mean(errors))
        correct_count = sum(is_correct_list)
        direction_accuracy = float(correct_count / TEST_MONTHS_COUNT) * 100.0

        # MASE (önceki aya göre naif değişim baz alınarak)
        mase_denom = np.mean(np.abs(y_true_arr - y_prev_arr)) + 1e-6
        mase = float(mae / mase_denom)

        model_summaries.append({
            "Model": model_name,
            "Dogru_Yon_Sayisi": f"{correct_count}/{TEST_MONTHS_COUNT}",
            "Yon_Dogrulugu_Pct": round(direction_accuracy, 1),
            "MAE_Gun": round(mae, 3),
            "RMSE_Gun": round(rmse, 3),
            "MASE": round(mase, 3),
            "Bias_Gun": round(bias, 3),
            "Tahminler": [round(v, 2) for v in preds_for_model],
            "Gercekler": [round(v, 2) for v in actual_values],
            "Onceki_Ay": [round(v, 2) for v in prev_values],
            "Yon_Sonuclari": ["✓" if c else "✗" for c in is_correct_list],
        })

        # Model Bazlı Görsel Oluştur
        fig, ax = plt.subplots(figsize=(11, 5.5))
        test_labels = [d.strftime("%Y-%m") for d in test_dates]
        x_coords = np.arange(len(test_labels))

        ax.plot(x_coords, actual_values, label="Gerçekleşen DOM (Gün)", color="#1f77b4", marker="o", markersize=9, linewidth=2.5)
        ax.plot(x_coords, preds_for_model, label=f"1 Aylık Tahmin ({model_name})", color="#d62728", marker="s", markersize=8, linestyle="--", linewidth=2.2)
        ax.plot(x_coords, prev_values, label="Önceki Ay Referansı (t-1)", color="#7f7f7f", marker="^", linestyle=":", linewidth=1.8)

        # Noktaların üzerine yön ikonları
        for i, (act, pred, prv, is_corr) in enumerate(zip(actual_values, preds_for_model, prev_values, is_correct_list)):
            symbol = "✓ DOGRU" if is_corr else "✗ YANLIS"
            color_box = "#d4edda" if is_corr else "#f8d7da"
            edge_color = "#28a745" if is_corr else "#dc3545"
            ax.annotate(
                f"{symbol}\n(G:{act:.1f} / T:{pred:.1f})",
                (x_coords[i], max(act, pred) + 0.35),
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color_box, edgecolor=edge_color, alpha=0.9),
            )

        info_box = (
            f"Model: {model_name}\n"
            f"🎯 1 Aylık Yön Doğruluğu: %{direction_accuracy:.1f} ({correct_count}/{TEST_MONTHS_COUNT} Ay Doğru)\n"
            f"• MAE: {mae:.2f} Gün | RMSE: {rmse:.2f} Gün\n"
            f"• MASE: {mase:.2f} | Bias: {bias:+.2f} Gün"
        )
        ax.text(
            0.02, 0.96, info_box,
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#333333", alpha=0.95),
            fontsize=10.5,
        )

        ax.set_xticks(x_coords)
        ax.set_xticklabels(test_labels, fontsize=11, fontweight="bold")
        ax.set_title(f"1 Aylık (h=1) Days on Market Tahmini ve Gelecek Ay Yön Başarısı: {model_name}", fontsize=12, fontweight="bold", pad=15)
        ax.set_xlabel("Tahmin Edilen Gelecek Ay", fontsize=11)
        ax.set_ylabel("İlan Satış Süresi (Gün)", fontsize=11)
        ax.set_ylim(min(min(actual_values), min(preds_for_model)) - 1.5, max(max(actual_values), max(preds_for_model)) + 2.5)
        ax.legend(loc="lower right", fontsize=10)
        plt.tight_layout()

        model_plot_path = OUT_DIR / "modeller" / f"{model_name}_h1_yon_grafigi.png"
        plt.savefig(model_plot_path, dpi=150)
        plt.close()

    # Karşılaştırma Tablosunu Kaydet
    summary_df = pd.DataFrame(model_summaries).sort_values(by=["Yon_Dogrulugu_Pct", "MAE_Gun"], ascending=[False, True]).reset_index(drop=True)
    summary_df.to_csv(OUT_DIR / "h1_model_yon_ve_metrik_karsilastirma.csv", index=False, encoding="utf-8-sig")
    summary_df.to_excel(OUT_DIR / "h1_model_yon_ve_metrik_karsilastirma.xlsx", index=False)

    detailed_df = pd.DataFrame(detailed_predictions)
    detailed_df.to_csv(OUT_DIR / "h1_6ay_test_detayli_tahminler.csv", index=False, encoding="utf-8-sig")
    detailed_df.to_excel(OUT_DIR / "h1_6ay_test_detayli_tahminler.xlsx", index=False)

    # Toplu Dashboard Görseli
    n_models = len(summary_df)
    fig, axes = plt.subplots(int(np.ceil(n_models / 2)), 2, figsize=(18, 4.5 * int(np.ceil(n_models / 2))))
    axes = axes.flatten()

    for idx, row in summary_df.iterrows():
        ax = axes[idx]
        m_name = row["Model"]
        preds = row["Tahminler"]
        actuals = row["Gercekler"]
        prevs = row["Onceki_Ay"]
        checks = row["Yon_Sonuclari"]
        pct = row["Yon_Dogrulugu_Pct"]
        cnt = row["Dogru_Yon_Sayisi"]
        mae_v = row["MAE_Gun"]

        x_coords = np.arange(len(test_dates))
        ax.plot(x_coords, actuals, label="Gerçek DOM", color="#1f77b4", marker="o", linewidth=2.2)
        ax.plot(x_coords, preds, label=f"Tahmin", color="#d62728", marker="s", linestyle="--", linewidth=2.2)
        ax.plot(x_coords, prevs, label="Önceki Ay", color="#7f7f7f", marker="^", linestyle=":", linewidth=1.5)

        for i, (act, pred, c) in enumerate(zip(actuals, preds, checks)):
            c_color = "#28a745" if c == "✓" else "#dc3545"
            ax.annotate(c, (x_coords[i], max(act, pred) + 0.3), ha="center", fontsize=11, fontweight="bold", color=c_color)

        ax.set_title(f"{m_name} — Yön Başarısı: %{pct:.1f} ({cnt} Ay Doğru) | MAE: {mae_v:.2f}g", fontsize=11, fontweight="bold")
        ax.set_xticks(x_coords)
        ax.set_xticklabels([d.strftime("%Y-%m") for d in test_dates], fontsize=9)
        ax.set_ylabel("Gün")
        ax.set_ylim(min(actuals) - 1.2, max(actuals) + 1.8)
        ax.legend(fontsize=8.5, loc="lower right")

    for j in range(len(summary_df), len(axes)):
        fig.delaxes(axes[j])

    plt.suptitle("1 Aylık (h=1) Rolling Tahmin — Tüm Modellerin Gelecek Ay Yön Doğruluğu (% ve X/6)", fontsize=13, fontweight="bold", y=0.995)
    plt.tight_layout()

    dashboard_path = OUT_DIR / "h1_tum_modeller_yon_basari_dashboard.png"
    plt.savefig(dashboard_path, dpi=160)
    plt.close()

    print("\n=======================================================")
    print("🏆 1 AYLIK (h=1) ROLLING YÖN VE METRİK SONUÇLARI (SON 6 AY)")
    print("=======================================================")
    print(summary_df[["Model", "Dogru_Yon_Sayisi", "Yon_Dogrulugu_Pct", "MAE_Gun", "RMSE_Gun", "MASE", "Bias_Gun"]].to_string(index=False))


if __name__ == "__main__":
    run_h1_rolling_evaluation()
