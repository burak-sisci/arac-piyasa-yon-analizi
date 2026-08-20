"""
MODEL 03 — Kaydedilmis baseline modellerin (high_quality, m=30,
WeightedEnsemble) GERIYE DONUK (walk-forward backtest) performansini
inceler: hangi donemlerde iyi, hangilerinde zorlaniyor?

Proje sahibinin talebiyle: model_01/model_02'nin egitilmis modelleri
(data/processed/model/autogluon_model_0X_baseline_m30/) YENIDEN
EGITILMEDEN yuklenir. Gecmiste bircok farkli "kesim tarihi" (cutoff)
secilir; her birinde o tarihe kadarki veriyle 30 gunluk bir tahmin
uretilir ve GERCEK (bilinen) degerlerle karsilastirilir.

Girdi: data/processed/model/autogluon_model_0{1,2}_baseline_m30/
       data/processed/dataframes/df_a_v3_..., df_b_v3_...
Cikti: data/processed/model/backtest_df_a.csv, backtest_df_b.csv
       data/processed/model/gorseller/backtest_*.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
GORSEL_DIR = MODEL_DIR / "gorseller"

PREDICTION_LENGTH = 30
MODEL_ADI = "WeightedEnsemble"

SETLER = {
    "DF-A": dict(
        kaynak_csv=DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
        model_yolu=MODEL_DIR / "autogluon_model_01_baseline_m30",
        baslangic="2018-01-01", bitis="2026-06-30",
        covariate_sutunlari=["usdtry_orta", "tufe_aylik_degisim", "tufe_yillik_degisim",
                              "odmd_otomobil_adet", "tuketici_guven_endeksi", "tasit_kredisi_faiz_lag12ay"],
        ilk_kesim="2019-06-01", adim_gun=60,
    ),
    "DF-B": dict(
        kaynak_csv=DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
        model_yolu=MODEL_DIR / "autogluon_model_02_baseline_m30",
        baslangic="2024-01-01", bitis="2026-06-30",
        covariate_sutunlari=["tufe_aylik_degisim", "tufe_yillik_degisim", "enag_aylik_degisim",
                              "odmd_hta_adet", "osd_binek_adet", "otomobil_satinalma_ihtimali_endeksi",
                              "proxy_dom_gun", "proxy_satis_orani_pct", "proxy_nominal_yillik_pct",
                              "proxy_talep_aylik_pct", "proxy_reel_aylik_log_degisim",
                              "tasit_kredisi_faiz_lag4ay", "politika_faizi_lag5ay"],
        ilk_kesim="2024-07-01", adim_gun=30,
    ),
}

TARGET = "noter_devir_otomobil_adet"


def main():
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    for set_adi, ayar in SETLER.items():
        print(f"\n=== {set_adi} ===")
        df = pd.read_csv(ayar["kaynak_csv"], parse_dates=["tarih"])
        df = df[(df["tarih"] >= ayar["baslangic"]) & (df["tarih"] <= ayar["bitis"])].reset_index(drop=True)
        for kolon in ayar["covariate_sutunlari"]:
            df[kolon] = df[kolon].ffill().bfill()
        df["item_id"] = "TR_arac_piyasasi"

        predictor = TimeSeriesPredictor.load(str(ayar["model_yolu"]))

        kesim_tarihleri = pd.date_range(ayar["ilk_kesim"], ayar["bitis"], freq=f"{ayar['adim_gun']}D")
        # son kesimden itibaren 30 gun gercek veri olmasi gerekiyor
        kesim_tarihleri = [t for t in kesim_tarihleri if t + pd.Timedelta(days=PREDICTION_LENGTH) <= pd.Timestamp(ayar["bitis"])]

        sonuclar = []
        for kesim in kesim_tarihleri:
            gecmis = df[df["tarih"] <= kesim]
            if len(gecmis) < 180:
                continue
            kolonlar = ["item_id", "tarih", TARGET] + ayar["covariate_sutunlari"]
            veri = gecmis[kolonlar].rename(columns={"tarih": "timestamp"})
            tsdf = TimeSeriesDataFrame.from_data_frame(veri, id_column="item_id", timestamp_column="timestamp")

            tahmin = predictor.predict(tsdf, model=MODEL_ADI)
            tahmin_degerleri = tahmin["mean"].values

            gercek = df[(df["tarih"] > kesim) & (df["tarih"] <= kesim + pd.Timedelta(days=PREDICTION_LENGTH))]
            gercek_degerleri = gercek[TARGET].values

            n = min(len(tahmin_degerleri), len(gercek_degerleri))
            if n == 0:
                continue
            hata = np.abs(tahmin_degerleri[:n] - gercek_degerleri[:n])
            yuzde_hata = hata / np.abs(gercek_degerleri[:n]) * 100

            sonuclar.append({
                "kesim_tarihi": kesim,
                "ortalama_mutlak_hata": hata.mean(),
                "ortalama_yuzde_hata": yuzde_hata.mean(),
                "gercek_ortalama": gercek_degerleri[:n].mean(),
                "tahmin_ortalama": tahmin_degerleri[:n].mean(),
            })
            print(f"  {kesim.date()}: ort.%hata={yuzde_hata.mean():.2f}  gercek~{gercek_degerleri[:n].mean():.0f}  tahmin~{tahmin_degerleri[:n].mean():.0f}")

        sonuc_df = pd.DataFrame(sonuclar)
        cikti_csv = MODEL_DIR / f"backtest_{set_adi.lower().replace('-', '_')}.csv"
        sonuc_df.to_csv(cikti_csv, index=False, encoding="utf-8-sig")
        print(f"  Cikti: {cikti_csv}")
        print(f"  Genel ortalama yuzde hata: {sonuc_df['ortalama_yuzde_hata'].mean():.2f}%")

        fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
        axes[0].plot(sonuc_df["kesim_tarihi"], sonuc_df["gercek_ortalama"], marker="o", label="Gercek", color="black")
        axes[0].plot(sonuc_df["kesim_tarihi"], sonuc_df["tahmin_ortalama"], marker="o", label="Tahmin (30 gunluk ort.)", color="orange")
        axes[0].set_ylabel(TARGET)
        axes[0].set_title(f"{set_adi} - Geriye Donuk Test: Gercek vs Tahmin")
        axes[0].legend()
        axes[0].grid(alpha=0.3)

        axes[1].bar(sonuc_df["kesim_tarihi"], sonuc_df["ortalama_yuzde_hata"], width=ayar["adim_gun"] * 0.8, color="crimson")
        axes[1].set_ylabel("Ortalama % hata")
        axes[1].set_xlabel("Kesim tarihi (bu tarihten itibaren 30 gun tahmin edildi)")
        axes[1].grid(alpha=0.3)

        fig.tight_layout()
        cikti_png = GORSEL_DIR / f"backtest_{set_adi.lower().replace('-', '_')}.png"
        fig.savefig(cikti_png, dpi=150)
        plt.close(fig)
        print(f"  Gorsel: {cikti_png}")


if __name__ == "__main__":
    main()
