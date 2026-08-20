"""
MODEL 04 — YON DOGRULUGU (directional accuracy) ile baseline modelin
degerlendirilmesi: 3 sinif (up / stable / down).

Proje sahibinin tanimladigi kural:
- Bir ayin TAHMINI, bir ONCEKI ayin GERCEK degeriyle karsilastirilir.
  (Ornek: Haziran gercek=920.000, Temmuz tahmini=950.000 -> "up")
- 3 sinif, esik +-%5 (proje sahibi karari, veri dagilimina bakilarak
  secildi: up %40 / stable %26 / down %35 tarihsel dagilim).

YONTEM: Her ayin SON gununde kesim yapilir; model o tarihe kadarki
veriyle 30 gunluk tahmin uretir. Tahmin gunlerinden SADECE bir sonraki
takvim ayina dusenler alinip ortalanir -> "gelecek ayin tahmini".
Bu, tablonun takvim-ayi hizali oldugu (ay ici tum gunler ayni degeri
tasiyor) tasariminin dogal bir sonucu.

Modeller YENIDEN EGITILMEZ - baseline (high_quality, m=30) kayitli
modelleri yuklenir.

Girdi: data/processed/model/autogluon_model_0{1,2}_baseline_m30/
Cikti: data/processed/model/yon_dogrulugu_df_{a,b}.csv
       data/processed/model/gorseller/yon_dogrulugu_*.png
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

TARGET = "noter_devir_otomobil_adet"
PREDICTION_LENGTH = 30
MODEL_ADI = "WeightedEnsemble"
ESIK_YUZDE = 5.0  # proje sahibi karari: +-%5 -> "stable"

SETLER = {
    "DF-A": dict(
        kaynak_csv=DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
        model_yolu=MODEL_DIR / "autogluon_model_01_baseline_m30",
        baslangic="2018-01-01", bitis="2026-06-30",
        covariate_sutunlari=["usdtry_orta", "tufe_aylik_degisim", "tufe_yillik_degisim",
                              "odmd_otomobil_adet", "tuketici_guven_endeksi", "tasit_kredisi_faiz_lag12ay"],
        ilk_kesim_ayi="2019-06",
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
        ilk_kesim_ayi="2024-07",
    ),
}


def _yon_etiketi(yuzde_degisim: float) -> str:
    if yuzde_degisim > ESIK_YUZDE:
        return "up"
    if yuzde_degisim < -ESIK_YUZDE:
        return "down"
    return "stable"


def main():
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    for set_adi, ayar in SETLER.items():
        print(f"\n=== {set_adi} ===")
        df = pd.read_csv(ayar["kaynak_csv"], parse_dates=["tarih"])
        df = df[(df["tarih"] >= ayar["baslangic"]) & (df["tarih"] <= ayar["bitis"])].reset_index(drop=True)
        for kolon in ayar["covariate_sutunlari"]:
            df[kolon] = df[kolon].ffill().bfill()
        df["item_id"] = "TR_arac_piyasasi"
        df["_ay"] = df["tarih"].dt.to_period("M")

        # her ayin GERCEK degeri (takvim-ayi hizali oldugu icin ay icinde sabit)
        aylik_gercek = df.dropna(subset=[TARGET]).groupby("_ay")[TARGET].first()

        predictor = TimeSeriesPredictor.load(str(ayar["model_yolu"]))

        ilk_ay = pd.Period(ayar["ilk_kesim_ayi"], freq="M")
        son_ay = df["_ay"].max()
        kesim_aylari = [a for a in aylik_gercek.index if ilk_ay <= a < son_ay and (a + 1) in aylik_gercek.index]

        sonuclar = []
        for kesim_ayi in kesim_aylari:
            hedef_ay = kesim_ayi + 1
            kesim_tarihi = kesim_ayi.to_timestamp(how="end").normalize()

            gecmis = df[df["tarih"] <= kesim_tarihi]
            kolonlar = ["item_id", "tarih", TARGET] + ayar["covariate_sutunlari"]
            veri = gecmis[kolonlar].rename(columns={"tarih": "timestamp"})
            tsdf = TimeSeriesDataFrame.from_data_frame(veri, id_column="item_id", timestamp_column="timestamp")

            tahmin = predictor.predict(tsdf, model=MODEL_ADI).reset_index()
            tahmin["_ay"] = tahmin["timestamp"].dt.to_period("M")
            hedef_ay_tahminleri = tahmin[tahmin["_ay"] == hedef_ay]["mean"]
            if len(hedef_ay_tahminleri) == 0:
                continue
            tahmin_degeri = hedef_ay_tahminleri.mean()

            onceki_gercek = aylik_gercek[kesim_ayi]
            hedef_gercek = aylik_gercek[hedef_ay]

            tahmin_yuzde = (tahmin_degeri - onceki_gercek) / onceki_gercek * 100
            gercek_yuzde = (hedef_gercek - onceki_gercek) / onceki_gercek * 100

            tahmin_yon = _yon_etiketi(tahmin_yuzde)
            gercek_yon = _yon_etiketi(gercek_yuzde)

            sonuclar.append({
                "kesim_ayi": str(kesim_ayi), "hedef_ay": str(hedef_ay),
                "onceki_gercek": onceki_gercek, "hedef_gercek": hedef_gercek,
                "tahmin_deger": tahmin_degeri,
                "gercek_yuzde": gercek_yuzde, "tahmin_yuzde": tahmin_yuzde,
                "gercek_yon": gercek_yon, "tahmin_yon": tahmin_yon,
                "dogru_mu": int(gercek_yon == tahmin_yon),
            })
            print(f"  {hedef_ay}: gercek={gercek_yon} ({gercek_yuzde:+.1f}%) | tahmin={tahmin_yon} ({tahmin_yuzde:+.1f}%) "
                  f"{'DOGRU' if gercek_yon == tahmin_yon else 'YANLIS'}")

        sonuc_df = pd.DataFrame(sonuclar)
        cikti_csv = MODEL_DIR / f"yon_dogrulugu_{set_adi.lower().replace('-', '_')}.csv"
        sonuc_df.to_csv(cikti_csv, index=False, encoding="utf-8-sig")

        dogruluk = sonuc_df["dogru_mu"].mean() * 100
        print(f"\n  YON DOGRULUGU: {sonuc_df['dogru_mu'].sum()}/{len(sonuc_df)} = %{dogruluk:.1f}")
        print(f"  (rastgele tahmin ~%33, hep-en-sik-sinif tahmini ~%{sonuc_df['gercek_yon'].value_counts(normalize=True).max()*100:.1f})")
        print("\n  Sinif bazinda:")
        for sinif in ["up", "stable", "down"]:
            alt = sonuc_df[sonuc_df["gercek_yon"] == sinif]
            if len(alt):
                print(f"    gercek={sinif}: {alt['dogru_mu'].sum()}/{len(alt)} dogru (%{alt['dogru_mu'].mean()*100:.0f})")

        # karisiklik matrisi
        siniflar = ["down", "stable", "up"]
        matris = pd.crosstab(sonuc_df["gercek_yon"], sonuc_df["tahmin_yon"]).reindex(index=siniflar, columns=siniflar, fill_value=0)
        print("\n  Karisiklik matrisi (satir=gercek, sutun=tahmin):")
        print(matris.to_string())

        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(matris.values, cmap="Blues")
        ax.set_xticks(range(3)); ax.set_xticklabels(siniflar)
        ax.set_yticks(range(3)); ax.set_yticklabels(siniflar)
        ax.set_xlabel("Tahmin"); ax.set_ylabel("Gercek")
        ax.set_title(f"{set_adi} — Yon Dogrulugu %{dogruluk:.1f} (n={len(sonuc_df)}, esik +-%{ESIK_YUZDE:.0f})")
        for i in range(3):
            for j in range(3):
                deger = matris.values[i, j]
                ax.text(j, i, str(deger), ha="center", va="center",
                        color="white" if deger > matris.values.max() * 0.6 else "black", fontsize=13)
        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        cikti_png = GORSEL_DIR / f"yon_dogrulugu_{set_adi.lower().replace('-', '_')}.png"
        fig.savefig(cikti_png, dpi=150)
        plt.close(fig)
        print(f"\n  Cikti: {cikti_csv}\n  Gorsel: {cikti_png}")


if __name__ == "__main__":
    main()
