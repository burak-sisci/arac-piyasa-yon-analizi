# -*- coding: utf-8 -*-
"""target_betam_dom_gun (Days on Market) Yön ve Seviye Modelleme Betiği.

Bu betik:
1. 'data/birlesik_veri_seti/arac_piyasasi_master_veri_seti.csv' dosyasını okur.
2. Aday feature'ları gecikmeli (lag-1) olarak hazırlar.
3. Kullanıcının belirttiği 2 filtre kuralını uygular:
   - Target ile korelasyonu |r| < 0.10 olanları siler.
   - Kendi aralarında |r| > 0.90 olanlardan target ile korelasyonu en yüksek olanı seçip diğerlerini siler.
4. AutoGluon TimeSeries ile modelleri eğitir.
5. Her model için metrikleri hesaplar:
   - YoY Yön Doğruluğu (Geçen yılın aynı ayına göre yön doğruluğu %)
   - MoM Yön Doğruluğu (Önceki aya göre yön doğruluğu %)
   - MAE (Ortalama Mutlak Hata - Gün)
   - RMSE (Karesel Ortalama Hata - Gün)
   - MASE (Mevsimsel Naife Göre Ölçekli Hata)
   - Bias (Ortalama Sapma / Yanlılık - Gün)
6. Her model için ayrı ayrı görsel çıktı (.png) ve toplu karşılaştırma paneli üretir.
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
OUT_DIR = PROJECT_ROOT / "outputs" / "betam_dom_yon_analizi"
TARGET = "target_betam_dom_gun"
DATE_COL = "referans_ayi"
PREDICTION_LENGTH = 3
FREQ = "MS"

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"


def prepare_and_filter_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Kullanıcının belirlediği 2 korelasyon kuralına göre feature seçimi yapar."""
    # 2024-01 ile 2026-06 arasındaki dönemi al
    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    sub = df[(df[DATE_COL] >= "2024-01-01") & (df[DATE_COL] <= "2026-06-01")].copy()
    sub = sub.sort_values(DATE_COL).reset_index(drop=True)

    # İç kısımdaki eksik ayları (2024-05, 2025-02) doğrusal enterpolasyonla tamamla
    sub[TARGET] = sub[TARGET].interpolate(method="linear")

    # 1. Aday Feature Havuzu (Takvim + 1 Ay Gecikmeli Makro/Piyasa Göstergeleri)
    candidate_df = pd.DataFrame({DATE_COL: sub[DATE_COL], TARGET: sub[TARGET]})
    candidate_df["ay"] = sub[DATE_COL].dt.month
    candidate_df["ceyrek"] = sub[DATE_COL].dt.quarter
    candidate_df["sin_ay"] = np.sin(2 * np.pi * candidate_df["ay"] / 12.0)
    candidate_df["cos_ay"] = np.cos(2 * np.pi * candidate_df["ay"] / 12.0)

    lag_candidates = [
        "noter_devir_otomobil_adet",
        "odmd_otomobil_adet",
        "osd_binek_adet",
        "tufe_aylik_degisim",
        "tufe_yillik_degisim",
        "enag_aylik_degisim",
        "enag_yillik_degisim",
        "tasit_kredisi_faiz",
        "politika_faizi",
        "usdtry_ortalama",
        "eurtry_ortalama",
        "altin_gram_try",
        "tuketici_guven_endeksi",
        "otomobil_satinalma_ihtimali_endeksi",
        "indicata_ilan_yayinlanan_adet",
        "indicata_satisa_donen_adet",
        "indicata_satis_ilan_orani_pct",
        "arabam_ortalama_ilan_fiyati_tl",
        "arabam_reel_aylik_degisim_pct",
        "betam_ortalama_ilan_fiyati_tl",
        "betam_talep_aylik_pct",
        "betam_satis_orani_pct",
        "otv_event_ay_mi",
    ]

    for col in lag_candidates:
        if col in sub.columns:
            # Sızıntı önleme: 1 ay gecikmeli değer
            candidate_df[f"{col}_lag1"] = sub[col].shift(1)

    candidate_df = candidate_df.bfill().ffill()

    # Feature listesi
    all_feature_cols = [c for c in candidate_df.columns if c not in [DATE_COL, TARGET]]

    # 2. Korelasyon Matrisi ve Filtre 1: |r(feature, target)| >= 0.10
    target_corrs = {}
    for f in all_feature_cols:
        r = candidate_df[f].corr(candidate_df[TARGET])
        target_corrs[f] = r if not np.isnan(r) else 0.0

    corr_series = pd.Series(target_corrs)
    passed_rule1 = corr_series[corr_series.abs() >= 0.10].index.tolist()
    dropped_rule1 = corr_series[corr_series.abs() < 0.10].index.tolist()

    print(f"\n[1] Toplam Aday Feature: {len(all_feature_cols)}")
    print(f"[-] Kural 1 (|r| < 0.10) ile Elenenler ({len(dropped_rule1)}): {dropped_rule1}")
    print(f"[+] Kural 1'i Gecenler ({len(passed_rule1)}): {passed_rule1}")

    # 3. Filtre 2: Çoklu Doğrusal Bağlantı (|r(f_i, f_j)| > 0.90)
    # Kendi aralarında 0.90'dan yüksek korelasyona sahip olanlardan target ile korelasyonu yüksek olan tutulur.
    feat_corr_matrix = candidate_df[passed_rule1].corr().abs()
    
    # Target korelasyon mutlak değerine göre azalan sırada sırala
    sorted_features = corr_series.loc[passed_rule1].abs().sort_values(ascending=False).index.tolist()
    
    selected_features = []
    dropped_rule2 = {}

    for feat in sorted_features:
        # Daha önce seçilenlerden biriyle korelasyonu > 0.90 mı?
        is_redundant = False
        for kept in selected_features:
            if feat_corr_matrix.loc[feat, kept] > 0.90:
                is_redundant = True
                dropped_rule2[feat] = (kept, feat_corr_matrix.loc[feat, kept])
                break
        if not is_redundant:
            selected_features.append(feat)

    print(f"\n[-] Kural 2 (|r_ij| > 0.90 Coklu Dogrusal Baglanti) ile Elenenler ({len(dropped_rule2)}):")
    for dropped_f, (kept_f, r_val) in dropped_rule2.items():
        print(f"   * {dropped_f} (r={r_val:.3f} ile {kept_f}'e bagli, elendi)")

    print(f"\n[+] NIHAI SECILEN FEATURELAR ({len(selected_features)}): {selected_features}")

    # Feature seçim raporu DataFrame'i
    selection_report = []
    for f in all_feature_cols:
        r_target = corr_series[f]
        if f in dropped_rule1:
            durum = "Elendi (Kural 1: |r| < 0.10)"
            aciklama = f"Target korelasyonu {r_target:.3f} < 0.10"
        elif f in dropped_rule2:
            durum = "Elendi (Kural 2: |r_ij| > 0.90)"
            kept_pair, pair_r = dropped_rule2[f]
            aciklama = f"{kept_pair} ile r={pair_r:.3f} > 0.90"
        else:
            durum = "SECILDI (Modele Girdi)"
            aciklama = f"Target korelasyonu r={r_target:.3f}"

        selection_report.append({
            "Feature": f,
            "Target Korelasyonu (r)": round(r_target, 4),
            "Mutlak Korelasyon (|r|)": round(abs(r_target), 4),
            "Durum": durum,
            "Aciklama": aciklama
        })

    report_df = pd.DataFrame(selection_report).sort_values(by="Mutlak Korelasyon (|r|)", ascending=False).reset_index(drop=True)

    clean_model_df = candidate_df[[DATE_COL, TARGET, *selected_features]].copy()
    clean_model_df["item_id"] = "TR_otomobil"

    return clean_model_df, report_df, selected_features


def evaluate_directional_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_yoy: np.ndarray, y_prev: np.ndarray) -> dict:
    """YoY ve MoM Yön Doğruluğu, MAE, RMSE, MASE ve Bias hesaplar."""
    # Hata metrikleri
    errors = y_pred - y_true
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    bias = float(np.mean(errors))  # Sistemik aşırı/eksik tahmin eğilimi

    # YoY (Geçen Yılın Aynı Ayına Göre) Yön Analizi
    actual_dir_yoy = np.sign(y_true - y_yoy)
    pred_dir_yoy = np.sign(y_pred - y_yoy)
    yoy_matches = (actual_dir_yoy == pred_dir_yoy)
    yoy_accuracy = float(np.mean(yoy_matches)) * 100.0

    # MoM (Önceki Aya Göre) Yön Analizi
    actual_dir_mom = np.sign(y_true - y_prev)
    pred_dir_mom = np.sign(y_pred - y_prev)
    mom_matches = (actual_dir_mom == pred_dir_mom)
    mom_accuracy = float(np.mean(mom_matches)) * 100.0

    # MASE Hesabı (YoY mevsimsel naif farklarına göre)
    mase_denominator = np.mean(np.abs(y_true - y_yoy)) + 1e-6
    mase = float(mae / mase_denominator)

    return {
        "mae": mae,
        "rmse": rmse,
        "bias": bias,
        "mase": mase,
        "yoy_accuracy": yoy_accuracy,
        "mom_accuracy": mom_accuracy,
        "yoy_matches": yoy_matches.tolist(),
        "actual_dir_yoy": actual_dir_yoy.tolist(),
        "pred_dir_yoy": pred_dir_yoy.tolist(),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "modeller").mkdir(parents=True, exist_ok=True)

    master_df = pd.read_csv(DATA_PATH)
    clean_df, report_df, selected_features = prepare_and_filter_features(master_df)

    # Feature seçim raporunu kaydet
    report_df.to_csv(OUT_DIR / "feature_secim_ve_korelasyon_ozeti.csv", index=False, encoding="utf-8-sig")

    # TimeSeriesDataFrame
    ts_df = TimeSeriesDataFrame.from_data_frame(
        clean_df,
        id_column="item_id",
        timestamp_column=DATE_COL,
    )

    train_data = ts_df.slice_by_timestep(None, -PREDICTION_LENGTH)
    test_data = ts_df

    print(f"\n=======================================================")
    print(f"[*] AUTOGLUON TIME SERIES EGITIMI BASLIYOR")
    print(f"Toplam Ay: {len(clean_df)} | Egitim: {len(clean_df) - PREDICTION_LENGTH} | Test: {PREDICTION_LENGTH}")
    print(f"=======================================================")

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
        train_data=train_data,
        presets="medium_quality",
        time_limit=150,
    )

    # Test değerleri ve referanslar
    test_indices = clean_df.iloc[-PREDICTION_LENGTH:].index
    test_dates = clean_df.loc[test_indices, DATE_COL].values
    y_true = clean_df.loc[test_indices, TARGET].values

    # Geçen yılın aynı ayı (YoY: t-12)
    yoy_indices = test_indices - 12
    y_yoy = clean_df.loc[yoy_indices, TARGET].values

    # Önceki ay (MoM: t-1)
    prev_indices = test_indices - 1
    y_prev = clean_df.loc[prev_indices, TARGET].values

    leaderboard = predictor.leaderboard(test_data, silent=True)
    leaderboard.to_csv(OUT_DIR / "leaderboard.csv", index=False)

    all_models = predictor.model_names()
    model_eval_results = []

    print("\n=======================================================")
    print("📊 MODEL BAZLI YÖN VE HATA DEĞERLENDİRME SONUÇLARI")
    print("=======================================================")

    for model_name in all_models:
        try:
            pred_ts = predictor.predict(train_data, model=model_name)
            pred_vals = pred_ts.loc["TR_otomobil", "mean"].values

            metrics = evaluate_directional_metrics(y_true, pred_vals, y_yoy, y_prev)

            model_eval_results.append({
                "Model": model_name,
                "YoY Yön Doğruluğu (%)": round(metrics["yoy_accuracy"], 1),
                "MoM Yön Doğruluğu (%)": round(metrics["mom_accuracy"], 1),
                "MAE (Gün)": round(metrics["mae"], 3),
                "RMSE (Gün)": round(metrics["rmse"], 3),
                "MASE": round(metrics["mase"], 3),
                "Bias (Sapma Gün)": round(metrics["bias"], 3),
                "Tahminler": [round(float(v), 2) for v in pred_vals],
                "Gerçekler": [round(float(v), 2) for v in y_true],
                "YoY_Referans": [round(float(v), 2) for v in y_yoy],
            })

            # Model bazında görsel oluştur
            fig, ax = plt.subplots(figsize=(10, 5.5))
            
            # Geçmiş veriler (son 18 ay)
            hist_df = clean_df.iloc[-18:]
            ax.plot(hist_df[DATE_COL], hist_df[TARGET], label="Gerçekleşen Days on Market (DOM)", color="#1f77b4", marker="o", linewidth=2.2)
            
            # Test penceresi gerçek
            test_plot_dates = pd.to_datetime(test_dates)
            ax.plot(test_plot_dates, y_true, label="Test Gerçek Değer", color="#1f77b4", marker="o", markersize=8, linewidth=3)
            
            # Geçen yılın aynı ayı referansı (YoY t-12)
            ax.plot(test_plot_dates, y_yoy, label="Geçen Yılın Aynı Ayı Referansı (t-12)", color="#7f7f7f", marker="^", linestyle=":", linewidth=2)
            
            # Model Tahmini
            ax.plot(test_plot_dates, pred_vals, label=f"Model Tahmini ({model_name})", color="#d62728", marker="s", linestyle="--", linewidth=2.5)

            # Yön açıklamaları metin kutusu
            yoy_match_str = " / ".join(["Doğru (✓)" if m else "Yanlış (✗)" for m in metrics["yoy_matches"]])
            info_text = (
                f"Model: {model_name}\n"
                f"• YoY Yön Doğruluğu: %{metrics['yoy_accuracy']:.1f}\n"
                f"• MoM Yön Doğruluğu: %{metrics['mom_accuracy']:.1f}\n"
                f"• MAE: {metrics['mae']:.2f} Gün\n"
                f"• RMSE: {metrics['rmse']:.2f} Gün\n"
                f"• MASE: {metrics['mase']:.2f}\n"
                f"• Bias (Sapma): {metrics['bias']:+.2f} Gün\n"
                f"YoY Eşleşme: [{yoy_match_str}]"
            )
            ax.text(
                0.02, 0.96, info_text,
                transform=ax.transAxes,
                verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#ced4da", alpha=0.92),
                fontsize=10,
            )

            ax.set_title(f"Days on Market: Gerçek vs {model_name} Tahmini ve Geçen Yıl Kıyaslaması", fontsize=12, fontweight="bold")
            ax.set_xlabel("Referans Ayı")
            ax.set_ylabel("İlan Satış Süresi (Gün)")
            ax.legend(loc="lower left")
            plt.tight_layout()

            model_fig_path = OUT_DIR / "modeller" / f"{model_name}_tahmin_grafigi.png"
            plt.savefig(model_fig_path, dpi=150)
            plt.close()

        except Exception as e:
            print(f"[ERR] {model_name} değerlendirilirken hata: {e}")

    # Karşılaştırma Tablosu
    eval_df = pd.DataFrame(model_eval_results).sort_values(by=["YoY Yön Doğruluğu (%)", "MAE (Gün)"], ascending=[False, True]).reset_index(drop=True)
    eval_df.to_csv(OUT_DIR / "model_yon_ve_hata_metrikleri_karsilastirma.csv", index=False, encoding="utf-8-sig")
    eval_df.to_excel(OUT_DIR / "model_yon_ve_hata_metrikleri_karsilastirma.xlsx", index=False)

    print(eval_df[["Model", "YoY Yön Doğruluğu (%)", "MoM Yön Doğruluğu (%)", "MAE (Gün)", "RMSE (Gün)", "MASE", "Bias (Sapma Gün)"]].to_string(index=False))

    # Toplu Karşılaştırma Dashboard Görseli
    n_models = len(eval_df)
    n_cols = 3
    n_rows = int(np.ceil(n_models / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
    axes = axes.flatten()

    for idx, row in eval_df.iterrows():
        ax = axes[idx]
        m_name = row["Model"]
        preds = row["Tahminler"]
        g_degerler = row["Gerçekler"]
        yoy_ref = row["YoY_Referans"]
        test_m_labels = [pd.to_datetime(d).strftime("%Y-%m") for d in test_dates]

        ax.plot(test_m_labels, g_degerler, label="Gerçek DOM", color="#1f77b4", marker="o", linewidth=2.5)
        ax.plot(test_m_labels, yoy_ref, label="Geçen Yıl (t-12)", color="#7f7f7f", marker="^", linestyle=":", linewidth=1.8)
        ax.plot(test_m_labels, preds, label=f"Tahmin", color="#d62728", marker="s", linestyle="--", linewidth=2.2)

        ax.set_title(f"{m_name} (YoY: %{row['YoY Yön Doğruluğu (%)']:.0f} | MAE: {row['MAE (Gün)']:.2f}g)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Gün")
        ax.legend(fontsize=9)

    # Kalan boş subplotları kapat
    for j in range(len(eval_df), len(axes)):
        fig.delaxes(axes[j])

    plt.suptitle("AutoGluon TimeSeries - Tüm Modellerin Days on Market Seviye ve YoY Yön Tahminleri", fontsize=14, fontweight="bold", y=0.995)
    plt.tight_layout()

    dashboard_path = OUT_DIR / "tum_modeller_yon_ve_seviye_dashboard.png"
    plt.savefig(dashboard_path, dpi=160)
    plt.close()

    print(f"\n[OK] Tum islemler basariyla tamamlandi!")
    print(f"Ciktilar:\n - {OUT_DIR / 'feature_secim_ve_korelasyon_ozeti.csv'}\n - {OUT_DIR / 'model_yon_ve_hata_metrikleri_karsilastirma.csv'}\n - {dashboard_path}")


if __name__ == "__main__":
    main()
