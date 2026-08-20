# -*- coding: utf-8 -*-
"""Tum sayisal feature'lar + iki target adayi (target_1ay_hiz, target_3ay_hiz)
icin korelasyon matrisi ve isi haritasi uretir."""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="white", context="notebook")

PROJE_KOKU = Path(__file__).resolve().parent.parent
DATA_DIR = PROJE_KOKU / "data"
CIKTI_DIR = PROJE_KOKU / "outputs" / "korelasyon_matrisi_sade"
CIKTI_DIR.mkdir(parents=True, exist_ok=True)


def oku_aylik(goreli_yol, sutunlar, tarih_sutunu="referans_ayi", yeni_adlar=None):
    tablo = pd.read_csv(DATA_DIR / goreli_yol)
    tablo = tablo[[tarih_sutunu, *sutunlar]].copy()
    tablo[tarih_sutunu] = (
        pd.to_datetime(tablo[tarih_sutunu], errors="coerce")
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    tablo = tablo.dropna(subset=[tarih_sutunu])
    for sutun in sutunlar:
        tablo[sutun] = pd.to_numeric(tablo[sutun], errors="coerce")
    if yeni_adlar:
        tablo = tablo.rename(columns=yeni_adlar)
    tarih_adi = yeni_adlar.get(tarih_sutunu, tarih_sutunu) if yeni_adlar else tarih_sutunu
    return tablo.sort_values(tarih_adi).drop_duplicates(tarih_adi, keep="last").reset_index(drop=True)


kaynak_tablolari = [
    oku_aylik("noter_devir/noter_devir_2015_bugun_aylik.csv",
              ["noter_devir_toplam_adet", "noter_devir_otomobil_adet"]),
    oku_aylik("odmd/odmd_2015_bugun_aylik.csv",
              ["odmd_toplam_adet", "odmd_otomobil_adet", "odmd_hta_adet"]),
    oku_aylik("osd/osd_2024_bugun_aylik.csv",
              ["osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet"]),
    oku_aylik("tufe/tufe_2024_bugun_aylik.csv", ["tufe_endeks", "tufe_aylik_degisim"]),
    oku_aylik("tuketici_guveni/tuketici_guveni_2024_bugun_aylik.csv",
              ["tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi"]),
    oku_aylik("faiz/faizler_2024_bugun_aylik.csv", ["tasit_kredisi_faiz", "politika_faizi"]),
    oku_aylik("usdtry/usdtry_2015_bugun_aylik.csv",
              ["usdtry_aysonu_alis", "usdtry_aysonu_satis", "usdtry_aysonu",
               "usdtry_ortalama_alis", "usdtry_ortalama_satis", "usdtry_ortalama"]),
    oku_aylik("altintry/altintry_aylik_2015_bugun.csv", ["altin_gram_try"]),
    oku_aylik("alim_gucu/alim_gucu_2018_bugun_aylik.csv", ["brut_ucret_maas_endeksi_2021_100"]),
    oku_aylik("indicata/indicata_aylik.csv",
              ["ilan_yayinlanan_adet", "satisa_donen_adet", "satis_ilan_orani_pct",
               "ortalama_satis_hizi_gun", "perakende_fiyat_aylik_pct", "toptan_fiyat_aylik_pct"],
              yeni_adlar={
                  "ilan_yayinlanan_adet": "indicata_ilan_yayinlanan_adet",
                  "satisa_donen_adet": "indicata_satisa_donen_adet",
                  "satis_ilan_orani_pct": "indicata_satis_ilan_orani_pct",
                  "ortalama_satis_hizi_gun": "indicata_ortalama_satis_hizi_gun",
                  "perakende_fiyat_aylik_pct": "indicata_perakende_fiyat_aylik_pct",
                  "toptan_fiyat_aylik_pct": "indicata_toptan_fiyat_aylik_pct"}),
    oku_aylik("arabamcom/arabamcom_aylik_fiyat.csv",
              ["ortalama_ilan_fiyati_tl", "reel_aylik_degisim_pct"],
              yeni_adlar={"ortalama_ilan_fiyati_tl": "arabam_ortalama_ilan_fiyati_tl",
                          "reel_aylik_degisim_pct": "arabam_reel_aylik_degisim_pct"}),
    oku_aylik("proxy_fiyat/proxy_fiyat_2024_bugun_raw.csv",
              ["proxy_fiyat_cari_tl", "proxy_talep_aylik_pct", "proxy_satis_orani_pct", "proxy_dom_gun"],
              yeni_adlar={"proxy_fiyat_cari_tl": "betam_ortalama_ilan_fiyati_tl",
                          "proxy_talep_aylik_pct": "betam_talep_aylik_pct",
                          "proxy_satis_orani_pct": "betam_satis_orani_pct",
                          "proxy_dom_gun": "betam_dom_gun"}),
    oku_aylik("otv/otv_olaylari_2015_bugun_aylik.csv", ["otv_event_ay_mi"]),
]

# EUR/TRY gunluk -> aylik ortalama + ay sonu
eur = pd.read_csv(DATA_DIR / "eurtry/eurtry_gunluk_2015_bugun.csv")
eur["tarih"] = pd.to_datetime(eur["tarih"], errors="coerce")
eur["eurtry_orta"] = pd.to_numeric(eur["eurtry_orta"], errors="coerce")
eur = eur.dropna(subset=["tarih", "eurtry_orta"]).sort_values("tarih")
eur["referans_ayi"] = eur["tarih"].dt.to_period("M").dt.to_timestamp()
kaynak_tablolari.append(
    eur.groupby("referans_ayi", as_index=False)
       .agg(eurtry_ortalama=("eurtry_orta", "mean"), eurtry_aysonu=("eurtry_orta", "last")))

# BETAM fiyatini 2023 tamamlayici ile geriye uzat
betam_2023 = oku_aylik("betam/betam_2023_eksik_tamamlayici.csv",
                       ["ortalama_ilan_fiyati_tl"],
                       yeni_adlar={"ortalama_ilan_fiyati_tl": "betam_ortalama_ilan_fiyati_tl"})
idx = next(i for i, t in enumerate(kaynak_tablolari) if "betam_ortalama_ilan_fiyati_tl" in t.columns)
kaynak_tablolari[idx] = (pd.concat([betam_2023, kaynak_tablolari[idx]], ignore_index=True)
                         .sort_values("referans_ayi").drop_duplicates("referans_ayi", keep="last"))

# Ana takvim: noter otomobil devrinin gecerli oldugu donem
noter = kaynak_tablolari[0]
gecerli = noter.loc[noter["noter_devir_otomobil_adet"].notna(), "referans_ayi"]
veri = pd.DataFrame({"referans_ayi": pd.date_range(gecerli.min(), gecerli.max(), freq="MS")})
for tablo in kaynak_tablolari:
    yeni = [c for c in tablo.columns if c != "referans_ayi" and c not in veri.columns]
    if yeni:
        veri = veri.merge(tablo[["referans_ayi", *yeni]], on="referans_ayi", how="left")
veri = veri.sort_values("referans_ayi").reset_index(drop=True)

# Iki target adayi
V = veri["noter_devir_otomobil_adet"]
Q3 = V.rolling(3, min_periods=3).sum()
veri["target_1ay_hiz"] = 100 * np.log(V / V.shift(1))
veri["target_3ay_hiz"] = 100 * np.log(Q3 / Q3.shift(3))

sutunlar = [c for c in veri.columns if c != "referans_ayi"]
matris = veri[sutunlar]

corr = matris.corr(method="pearson", min_periods=12)
ortak = matris.notna().astype(int).T.dot(matris.notna().astype(int))

corr.to_csv(CIKTI_DIR / "tum_feature_iki_target_korelasyon_matrisi.csv")
ortak.to_csv(CIKTI_DIR / "tum_feature_iki_target_ortak_gozlem.csv")

# Isi haritasi (alt ucgen)
maske = np.triu(np.ones_like(corr, dtype=bool), k=1)
n = len(corr.columns)
fig, ax = plt.subplots(figsize=(max(14, 0.5 * n), max(13, 0.48 * n)))
sns.heatmap(corr, mask=maske, cmap="vlag", center=0, vmin=-1, vmax=1,
            annot=False, linewidths=0.25, linecolor="white",
            square=True, cbar_kws={"label": "Pearson korelasyonu", "shrink": 0.6}, ax=ax)
ax.set_title("Tum sayisal feature'lar + target_1ay_hiz + target_3ay_hiz", pad=18, fontsize=14)
ax.tick_params(axis="x", rotation=80, labelsize=8)
ax.tick_params(axis="y", rotation=0, labelsize=8)
plt.tight_layout()
fig.savefig(CIKTI_DIR / "tum_feature_iki_target_korelasyon_isiharitasi.png", dpi=200, bbox_inches="tight")

# Isi haritasi (alt ucgen) - degerler yazili tam matris
fig1b, ax1b = plt.subplots(figsize=(max(20, 0.62 * n), max(19, 0.6 * n)))
sns.heatmap(corr, mask=maske, cmap="vlag", center=0, vmin=-1, vmax=1,
            annot=True, fmt=".2f", annot_kws={"size": 6},
            linewidths=0.25, linecolor="white",
            square=True, cbar_kws={"label": "Pearson korelasyonu", "shrink": 0.6}, ax=ax1b)
ax1b.set_title("Tum sayisal feature'lar + target_1ay_hiz + target_3ay_hiz (degerler yazili)", pad=18, fontsize=14)
ax1b.tick_params(axis="x", rotation=80, labelsize=8)
ax1b.tick_params(axis="y", rotation=0, labelsize=8)
plt.tight_layout()
fig1b.savefig(CIKTI_DIR / "tum_feature_iki_target_korelasyon_isiharitasi_degerli.png", dpi=200, bbox_inches="tight")

# Sadece iki target'in tum feature'larla korelasyonu (dikdortgen)
hedefler = ["target_1ay_hiz", "target_3ay_hiz"]
feat = [c for c in sutunlar if c not in hedefler]
ft = corr.loc[feat, hedefler].sort_values("target_3ay_hiz")
fig2, ax2 = plt.subplots(figsize=(6, max(9, 0.34 * len(feat))))
sns.heatmap(ft, cmap="vlag", center=0, vmin=-1, vmax=1, annot=True, fmt=".2f",
            linewidths=0.3, linecolor="white",
            cbar_kws={"label": "Pearson korelasyonu"}, ax=ax2)
ax2.set_title("Feature -> iki target korelasyonu", pad=14, fontsize=12)
ax2.tick_params(axis="x", rotation=0, labelsize=9)
ax2.tick_params(axis="y", rotation=0, labelsize=8)
plt.tight_layout()
fig2.savefig(CIKTI_DIR / "feature_target_korelasyon_isiharitasi.png", dpi=200, bbox_inches="tight")

ft.to_csv(CIKTI_DIR / "feature_target_korelasyonlari.csv")

print(f"Veri: {veri.shape[0]} ay, {len(sutunlar)} sutun ({len(feat)} feature + 2 target)")
print(veri['referans_ayi'].min().strftime('%Y-%m'), '->', veri['referans_ayi'].max().strftime('%Y-%m'))
print("target_1ay_hiz gecerli:", int(veri['target_1ay_hiz'].notna().sum()))
print("target_3ay_hiz gecerli:", int(veri['target_3ay_hiz'].notna().sum()))
print("Cikti:", CIKTI_DIR)
