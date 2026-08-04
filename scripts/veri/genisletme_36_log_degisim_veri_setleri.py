"""
GENIŞLETME AŞAMA 36 — DF-A ve DF-B'den, TREND ARINDIRILMIŞ (log-değişim)
iki YENİ veri seti kurar: df_a_log_degisim, df_b_log_degisim.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla)

TASARIM: DF-A/DF-B'nin kendisi DEĞİŞTİRİLMEZ - bu YENİ ve AYRI iki dosya.
Her yeni veri setinde:
- TARGET (noter_devir_toplam_adet) log-değişime çevrilir
  (noter_devir_toplam_adet_log_degisim) - HAM SEVIYE target DAHIL EDİLMEZ.
- Trend tasiyan (seviye) feature'lar log-degisime cevrilir (<ad>_log_degisim).
- Zaten trend tasimayan (yuzde/log-degisim) feature'lar OLDUGU GIBI kopyalanir.
- Zaten kendi log-degisim/yuzde-degisim karsiligi olan seviye sutunlar
  (tufe_endeks, proxy_fiyat_cari_tl) YENIDEN log-degisime cevrilmez,
  DOGRUDAN DISLANIR - onlarin var olan degisim karsiliklari zaten
  "trend tasimayan" grupta kopyalanacak.

LOG-DEGISIM HESAPLAMA YONTEMI (netlestirildi 2026-08-04 - satir yapisi
HER ZAMAN gunluk kaldi/kalacak, 4234/947 satir - bu asla degismedi):
- GERCEK GUNLUK kaynaklar (usdtry_orta, eurtry_orta): GUNLUK log-degisim
  ln(x_t/x_{t-1}), dogrudan gunluk seri uzerinde (tarih sirali).
- AYLIK-KADANSLI kaynaklar (TUFE, noter devri, ODMD, OSD, tuketici
  guveni, faiz, alim gucu - target dahil): once takvim ayina COLLAPSE
  edilir (df['tarih'].dt.strftime('%Y-%m') ile, referans_ay sutunlari
  artik yok ama takvim-ayi hizalama tasarimi geregi her gunun kendi ayi
  = degerin referans ayi), AYLIK log-degisim ln(x_t/x_{t-1}) (bir onceki
  AY'a gore) hesaplanir, sonra takvim gunune GERI YAYILIR (ayni ayin tum
  gunlerine ayni deger - adim/step fonksiyonu). SATIR SAYISI DEGISMEZ,
  yalnizca DEGER o ay icinde sabit kalir, ay degisince guncellenir.

Girdi: data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
       data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
       (SADECE OKUNUR, degistirilmez)
Cikti: data/processed/dataframes/df_a_log_degisim_2015_bugun.csv
       data/processed/dataframes/df_b_log_degisim_2024_bugun.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"

TARGET = "noter_devir_toplam_adet"

GUNLUK_LOG_DEGISIM_SUTUNLARI = ["usdtry_orta", "eurtry_orta"]

# Seviye/trend tasiyan, YENI log-degisim gereken sutunlar (target haric)
AYLIK_LOG_DEGISIM_SUTUNLARI = {
    "DF-A": [
        "altin_gram_try", "noter_devir_otomobil_adet",
        "odmd_toplam_adet", "odmd_otomobil_adet", "odmd_hta_adet",
        "osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet",
        "tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi",
        "tasit_kredisi_faiz", "politika_faizi",
    ],
    "DF-B": [
        "altin_gram_try", "noter_devir_otomobil_adet",
        "odmd_toplam_adet", "odmd_otomobil_adet", "odmd_hta_adet",
        "osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet",
        "tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi",
        "tasit_kredisi_faiz", "politika_faizi",
        "brut_ucret_maas_endeksi_2021_100",
    ],
}

# Zaten trend tasimayan, OLDUGU GIBI kopyalanan sutunlar
TREND_TASIMAYAN_SUTUNLAR = {
    "DF-A": ["tufe_aylik_degisim", "tufe_yillik_degisim"],
    "DF-B": [
        "tufe_aylik_degisim", "tufe_yillik_degisim",
        "enag_aylik_degisim", "enag_yillik_degisim",
        "proxy_dom_gun", "proxy_satis_orani_pct",
        "proxy_reel_aylik_pct", "proxy_nominal_yillik_pct", "proxy_talep_aylik_pct",
        "proxy_nominal_aylik_pct", "proxy_aylik_log_degisim", "proxy_reel_aylik_log_degisim",
    ],
}

DOSYALAR = {
    "DF-A": (DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv", DF_DIR / "df_a_log_degisim_2015_bugun.csv"),
    "DF-B": (DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv", DF_DIR / "df_b_log_degisim_2024_bugun.csv"),
}


def _gunluk_log_degisim(df: pd.DataFrame, kolon: str) -> pd.Series:
    seri = df.sort_values("tarih")[kolon]
    return np.log(seri / seri.shift(1))


def _aylik_log_degisim_takvime_yay(df: pd.DataFrame, kolon: str) -> pd.Series:
    """Aylik-kadansli bir sutunu once takvim ayina collapse edip AYLIK
    log-degisim hesaplar, sonra SATIR SAYISINI DEGISTIRMEDEN (df ile ayni
    uzunlukta) o ayin tum gunlerine geri yayar (step/adim fonksiyonu)."""
    calisma = df[["tarih", kolon]].copy()
    calisma["_ay_str"] = calisma["tarih"].dt.strftime("%Y-%m")
    aylik = calisma.dropna(subset=[kolon]).drop_duplicates(subset="_ay_str").sort_values("_ay_str").reset_index(drop=True)
    aylik["_log_degisim"] = np.log(aylik[kolon] / aylik[kolon].shift(1))
    esleme = calisma.merge(aylik[["_ay_str", "_log_degisim"]], on="_ay_str", how="left")
    return esleme["_log_degisim"]


def main():
    for df_adi, (kaynak_yol, hedef_yol) in DOSYALAR.items():
        print(f"\n=== {df_adi} ===")
        df = pd.read_csv(kaynak_yol, parse_dates=["tarih"])
        df = df.sort_values("tarih").reset_index(drop=True)

        yeni = pd.DataFrame({"tarih": df["tarih"]})

        target_kolon = f"{TARGET}_log_degisim"
        yeni[target_kolon] = _aylik_log_degisim_takvime_yay(df, TARGET)
        print(f"  {target_kolon} (TARGET, aylik log-degisim): dolu {yeni[target_kolon].notna().sum()}/{len(yeni)}")

        for kolon in GUNLUK_LOG_DEGISIM_SUTUNLARI:
            yeni_ad = f"{kolon}_log_degisim"
            yeni[yeni_ad] = _gunluk_log_degisim(df, kolon)
            print(f"  {yeni_ad} (gunluk log-degisim): dolu {yeni[yeni_ad].notna().sum()}/{len(yeni)}")

        for kolon in AYLIK_LOG_DEGISIM_SUTUNLARI[df_adi]:
            yeni_ad = f"{kolon}_log_degisim"
            yeni[yeni_ad] = _aylik_log_degisim_takvime_yay(df, kolon)
            print(f"  {yeni_ad} (aylik log-degisim): dolu {yeni[yeni_ad].notna().sum()}/{len(yeni)}")

        for kolon in TREND_TASIMAYAN_SUTUNLAR[df_adi]:
            yeni[kolon] = df[kolon]
            print(f"  {kolon} (degismeden kopyalandi): dolu {yeni[kolon].notna().sum()}/{len(yeni)}")

        yeni.to_csv(hedef_yol, index=False, encoding="utf-8-sig")
        print(f"\n  Cikti: {hedef_yol} ({yeni.shape[0]} satir x {yeni.shape[1]} sutun)")


if __name__ == "__main__":
    main()
