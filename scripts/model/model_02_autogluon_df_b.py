"""
MODEL 02 — AutoGluon TimeSeries, DF-B (2024-2026, zengin/dar pencere) ile
model_01'deki AYNI kurulum ve AYNI duzeltilmis dogrulama yontemi.

Proje sahibinin "ikisini de dene, karsilastir" talimatinin DF-B ayagi.

KARARLAR (model_01 ile TUTARLI):
- Target: noter_devir_otomobil_adet (HAM SEVIYE).
- Zaman penceresi: 2024-01-01 -> 2026-06-30 (target bu araligin disinda
  NaN - 2026-07'den itibaren henuz yayimlanmadi, model_01'deki AYNI
  yapisal gecikme).
- Satir granulerligi: GUNLUK (proje sahibinin tercihi, model_01 ile
  tutarli).
- noter_devir_toplam_adet COVARIATE'LERDEN CIKARILDI (sizinti riski,
  model_01 ile AYNI gerekce).
- Dogrulama: num_val_windows=4, val_step_size=15 - model_01'de
  bulunan "tek pencere yanlislikla tam bir takvim ayina denk geliyor"
  hatasindan kacinmak icin AYNI duzeltme.

Girdi: data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
Cikti: data/processed/model/model_02_leaderboard.csv
       data/processed/model/model_02_tahmin.csv
"""
from pathlib import Path

import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"

KAYNAK_CSV = DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv"
TARGET = "noter_devir_otomobil_adet"
COVARIATE_SUTUNLARI = [
    "tufe_aylik_degisim", "tufe_yillik_degisim", "enag_aylik_degisim",
    "odmd_hta_adet", "osd_binek_adet", "otomobil_satinalma_ihtimali_endeksi",
    "proxy_dom_gun", "proxy_satis_orani_pct", "proxy_nominal_yillik_pct",
    "proxy_talep_aylik_pct", "proxy_reel_aylik_log_degisim",
    "tasit_kredisi_faiz_lag4ay", "politika_faizi_lag5ay",
]
# noter_devir_toplam_adet BILINCLI OLARAK DISLANDI - sizinti riski (model_01 ile ayni)

PREDICTION_LENGTH = 30
TIME_LIMIT_SANIYE = 1200  # high_quality (DeepAR, Chronos2 ince-ayar) icin 20 dakika ust sinir
NUM_VAL_WINDOWS = 4
VAL_STEP_SIZE = 15


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(KAYNAK_CSV, parse_dates=["tarih"])
    df = df[(df["tarih"] >= "2024-01-01") & (df["tarih"] <= "2026-06-30")].reset_index(drop=True)

    for kolon in COVARIATE_SUTUNLARI:
        df[kolon] = df[kolon].ffill().bfill()

    assert df[TARGET].notna().all(), "Target'ta hala NaN var - beklenmiyordu"

    df["item_id"] = "TR_arac_piyasasi"
    kolonlar = ["item_id", "tarih", TARGET] + COVARIATE_SUTUNLARI
    veri = df[kolonlar].rename(columns={"tarih": "timestamp"})

    tsdf = TimeSeriesDataFrame.from_data_frame(veri, id_column="item_id", timestamp_column="timestamp")

    print(f"TimeSeriesDataFrame: {tsdf.shape[0]} satir, {tsdf.num_items} seri, "
          f"{tsdf.index.get_level_values('timestamp').min()} -> {tsdf.index.get_level_values('timestamp').max()}")

    predictor = TimeSeriesPredictor(
        target=TARGET,
        prediction_length=PREDICTION_LENGTH,
        freq="D",
        eval_metric="MASE",
        eval_metric_seasonal_period=30,  # 7 (haftalik) yerine 30 (aylik) - model_01 ile tutarli
        path=str(MODEL_DIR / "autogluon_model_02"),
    )
    predictor.fit(
        tsdf,
        presets="high_quality",
        time_limit=TIME_LIMIT_SANIYE,
        num_val_windows=NUM_VAL_WINDOWS,
        val_step_size=VAL_STEP_SIZE,
    )

    leaderboard = predictor.leaderboard(tsdf)
    print("\n=== LEADERBOARD ===")
    print(leaderboard.to_string(index=False))
    leaderboard.to_csv(MODEL_DIR / "model_02_leaderboard.csv", index=False, encoding="utf-8-sig")

    tahmin = predictor.predict(tsdf)
    print("\n=== TAHMIN (ilk 10 satir) ===")
    print(tahmin.head(10).to_string())
    tahmin.reset_index().to_csv(MODEL_DIR / "model_02_tahmin.csv", index=False, encoding="utf-8-sig")

    print(f"\nCikti: {MODEL_DIR / 'model_02_leaderboard.csv'}")
    print(f"Cikti: {MODEL_DIR / 'model_02_tahmin.csv'}")


if __name__ == "__main__":
    main()
