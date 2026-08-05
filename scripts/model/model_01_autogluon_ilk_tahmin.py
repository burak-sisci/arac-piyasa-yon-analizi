"""
MODEL 01 — AutoGluon TimeSeries ile ilk deneme tahmini.

Modelleme fazi, proje sahibinin adim adim yonlendirmesiyle. Bu script
"scripts/veri" degil "scripts/model" altinda - artik veri muhendisligi
degil modelleme fazindayiz.

KARARLAR (proje sahibiyle netlestirildi):
- Target: noter_devir_otomobil_adet (HAM SEVIYE, log-degisim degil).
- Kaynak veri seti: DF-A (df_a_v3_noter_penceresi_2015_bugun.csv) -
  daha uzun gecmis oldugu icin ilk deneme bu setle yapiliyor.
- Zaman penceresi: 2018-01-01 -> 2026-06-30 (target bu araligin
  disinda hep NaN - 2018 oncesi kaynak yok, 2026-07'den itibaren henuz
  yayimlanmadi, bu son kisim TAHMIN edilecek kisim).
- Satir granulerligi: GUNLUK (takvim-genisletilmis) - proje sahibinin
  acik tercihi, riskleri (pseudo-replikasyon, mevsimsellik yanilgisi)
  bilerek kabul edildi.
- COVARIATE'LARDAN noter_devir_toplam_adet CIKARILDI - target'in
  neredeyse birebir bir ust-kategorisi (r~0.98), dahil edilirse model
  bunu "kopyalayarak" sahte basari gosterir (veri sizintisi riski).
- Diger covariate'lar (usdtry_orta, tufe_aylik/yillik_degisim,
  odmd_otomobil_adet, tuketici_guven_endeksi,
  tasit_kredisi_faiz_lag12ay) hicbiri GELECEK icin bilinmiyor - bu
  yuzden "known_covariates" olarak degil, yalnizca GECMISE-AIT
  (past-only) covariate olarak taniniyor.
- usdtry_orta'daki hafta sonu/tatil bosluklari (NaN), yalnizca
  covariate oldugu icin ileri-doldurma (ffill) ile dolduruldu - target
  DEGIL, bu bir onceki gunun son bilinen kur degerini tasimak anlamina
  gelir, kabul edilebilir bir yaklasim (target'a HICBIR ffill
  uygulanmadi).

Girdi: data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
Cikti: data/processed/model/model_01_leaderboard.csv
       data/processed/model/model_01_tahmin.csv
"""
from pathlib import Path

import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"

KAYNAK_CSV = DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv"
TARGET = "noter_devir_otomobil_adet"
COVARIATE_SUTUNLARI = [
    "usdtry_orta", "tufe_aylik_degisim", "tufe_yillik_degisim",
    "odmd_otomobil_adet", "tuketici_guven_endeksi", "tasit_kredisi_faiz_lag12ay",
]
# noter_devir_toplam_adet BILINCLI OLARAK DISLANDI - sizinti riski (bkz. docstring)

PREDICTION_LENGTH = 30  # gun (~1 ay - kaynagin gercek guncelleme sikligi)
TIME_LIMIT_SANIYE = 600  # ilk deneme icin 10 dakika ust sinir

# DUZELTME (2026-08-05): tek dogrulama penceresi (varsayilan num_val_windows=1)
# tesadufen tam bir takvim ayina denk gelip (2026-06-01..06-30, target'in TEK
# deger tasidigi bir pencere) yapay olarak "kolay" bir sinav yaratti - herhangi
# bir model "dunku degeri kopyala" stratejisiyle bu pencerede neredeyse sifir
# hata yapardi, bu GERCEK bir tahmin basarisi degildi. Cozum: BIRDEN FAZLA
# dogrulama penceresi (farkli baslangic noktalarindan) kullanmak - bu sekilde
# bazi pencereler kesinlikle bir ay gecisi icerecek (kodla dogrulandi: 4
# pencereden 2'si ay gecisi iceriyor), tek sansli/sanssiz pencereye baglı
# kalinmaz, ortalama skor daha durust olur.
NUM_VAL_WINDOWS = 4
VAL_STEP_SIZE = 15


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(KAYNAK_CSV, parse_dates=["tarih"])
    df = df[(df["tarih"] >= "2018-01-01") & (df["tarih"] <= "2026-06-30")].reset_index(drop=True)

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
        path=str(MODEL_DIR / "autogluon_model_01"),
    )
    predictor.fit(
        tsdf,
        presets="medium_quality",
        time_limit=TIME_LIMIT_SANIYE,
        num_val_windows=NUM_VAL_WINDOWS,
        val_step_size=VAL_STEP_SIZE,
    )

    leaderboard = predictor.leaderboard(tsdf)
    print("\n=== LEADERBOARD ===")
    print(leaderboard.to_string(index=False))
    leaderboard.to_csv(MODEL_DIR / "model_01_leaderboard.csv", index=False, encoding="utf-8-sig")

    tahmin = predictor.predict(tsdf)
    print("\n=== TAHMIN (ilk 10 satir) ===")
    print(tahmin.head(10).to_string())
    tahmin.reset_index().to_csv(MODEL_DIR / "model_01_tahmin.csv", index=False, encoding="utf-8-sig")

    print(f"\nCikti: {MODEL_DIR / 'model_01_leaderboard.csv'}")
    print(f"Cikti: {MODEL_DIR / 'model_01_tahmin.csv'}")


if __name__ == "__main__":
    main()
