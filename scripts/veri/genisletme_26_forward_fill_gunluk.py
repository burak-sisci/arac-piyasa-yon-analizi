"""
GENIŞLETME AŞAMA 26 — Takvim-ayi bazli genisletilmis gunluk tablo (25 nolu
gorevin as-of/sizintisiz tablosuna EK, onun YERINE DEGIL).

(prompts/veri/26_forward_fill_gunluk_tablo_prompt.md, Gorev 1-2 -
proje sahibinin 2026-08-04 duzeltmesiyle guncellendi)

TASARIM ILKESI (proje sahibinin netlestirdigi hali): 25 numarali gorevin
df_gunluk_karisik_frekans_2015_bugun.csv ciktisi DEGISTIRILMEDEN durur.
Bu script onun YANINA, AYRI bir dosya uretir
(df_gunluk_forward_fill_2015_bugun.csv).

ONEMLI DUZELTME (ilk versiyondan farkli): "forward-fill" burada YAYIM/
AS-OF TARIHINDEN ITIBAREN ileri tasima DEGIL - dogrudan REFERANS AYININ
KENDI TAKVIM GUNLERINE yazma anlamina geliyor. Yani Mayis ayina ait bir
deger, Mayis'in 1'inden 31'ine kadar TUM gunlere yazilir - yayimlandigi
gun (as-of tarihi) hangi ay olursa olsun bu ONEMSIZDIR, tabloya hic
dahil edilmez. Her kaynak, KENDI ham (data/raw/...) dosyasindan referans_
ayi -> deger eslemesiyle dogrudan okunur (25 nolu gorevin as-of/yayim
tarihi mantigi bu tabloda KULLANILMAZ).

Bu tasarim, 25 nolu gorevde BETAM (proxy_fiyat) icin yasanan "iki
referans ayi ayni yayim gununde cakisiyor" sorununu da yapisal olarak
ORTADAN KALDIRIR: artik yayim tarihine hic bakilmadigi icin cakisma
imkansizdir - her referans ay kendi bagimsiz takvim bloguna yazilir.
Bunun sonucu: 25 nolu gorevde as-of cakismasi yuzunden ELENEN 2024-01 ve
2024-03 referans aylarinin KENDI degerleri bu tabloda GERI KAZANILDI
(bkz. PM raporu, proaktif bulgu).

BAYRAK SUTUNU YOK: ilk versiyonda eklenen "_gercek_mi" bayraklari, proje
sahibinin talebiyle KALDIRILDI (korelasyon hazirligina uygun degil).

DOKUNULMAYANLAR (aynen kopyalanir): usdtry_*/eurtry_* (zaten gunluk),
otv_* (olay-bazli, forward-fill anlamsiz), takvim sutunlari (yil/ay/gun/
ceyrek/haftanin_gunu/yilin_gunu), tarih.

Girdi: data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv
  (yalnizca GUNLUK/OTV/takvim sutunlari icin - degistirilmez)
  + data/raw/{altintry,tufe,enag,noter_devir,odmd,osd,tuketici_guveni,
  proxy_fiyat,alim_gucu,faiz} (aylik/ceyreklik kaynaklarin KENDI referans_
  ayi -> deger eslemesi icin)
Cikti: data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw"
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
KAYNAK_CSV = DF_DIR / "df_gunluk_karisik_frekans_2015_bugun.csv"
HEDEF_CSV = DF_DIR / "df_gunluk_forward_fill_2015_bugun.csv"

# grup_adi -> (ham_dosya_yolu, [deger_sutunlari])
AYLIK_CEYREKLIK_KAYNAKLAR = {
    "altin": (RAW_DIR / "altintry" / "altintry_aylik_2015_bugun.csv", ["altin_gram_try"]),
    "tufe": (RAW_DIR / "tufe" / "tufe_2024_bugun_aylik.csv", ["tufe_endeks", "tufe_aylik_degisim", "tufe_yillik_degisim"]),
    "enag": (RAW_DIR / "enag" / "enag_aylik_2021_2026.csv", ["enag_aylik_degisim", "enag_yillik_degisim"]),
    "noter": (RAW_DIR / "noter_devir" / "noter_devir_2015_bugun_aylik.csv", ["noter_devir_toplam_adet", "noter_devir_otomobil_adet"]),
    "odmd": (RAW_DIR / "odmd" / "odmd_2015_bugun_aylik.csv", ["odmd_toplam_adet", "odmd_otomobil_adet", "odmd_hta_adet"]),
    "osd": (RAW_DIR / "osd" / "osd_2024_bugun_aylik.csv", ["osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet"]),
    "tuketici": (RAW_DIR / "tuketici_guveni" / "tuketici_guveni_2024_bugun_aylik.csv", ["tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi"]),
    "proxy": (RAW_DIR / "proxy_fiyat" / "proxy_fiyat_2024_bugun_raw.csv", ["proxy_fiyat_cari_tl", "proxy_dom_gun", "proxy_satis_orani_pct"]),
    "alim_gucu": (RAW_DIR / "alim_gucu" / "alim_gucu_2018_bugun_aylik.csv", ["brut_ucret_maas_endeksi_2021_100"]),
    "faiz": (RAW_DIR / "faiz" / "faizler_2024_bugun_aylik.csv", ["tasit_kredisi_faiz", "politika_faizi"]),
}

# GUNLUK/OTV/takvim disindaki 25 nolu gorev sutunlari - bunlar bu scriptte
# YENIDEN URETILIR (ham kaynaktan), o yuzden kaynak tablodan ALINMAZLAR.
YENIDEN_URETILEN_SUTUNLAR = {"referans_ay", "gercek_mi"}  # isim parcasi kontrolu icin


def main():
    kaynak = pd.read_csv(KAYNAK_CSV, parse_dates=["tarih"])
    kaynak = kaynak.sort_values("tarih").reset_index(drop=True)

    # Dokunulmayan sutunlar: gunluk kurlar, OTV, takvim, tarih.
    dokunulmayan_kolonlar = [
        "tarih",
        "usdtry_alis", "usdtry_satis", "usdtry_orta",
        "eurtry_alis", "eurtry_satis", "eurtry_orta",
        "otv_referans_ay", "otv_aciklama", "otv_event_gunu_mu",
        "yil", "ay", "gun", "ceyrek", "haftanin_gunu", "yilin_gunu",
    ]
    df = kaynak[dokunulmayan_kolonlar].copy()

    # Eslestirme anahtari: her gunun ait oldugu takvim ayi ("YYYY-MM").
    df["_ay_str"] = df["tarih"].dt.strftime("%Y-%m")

    eski_doluluk = {
        c: kaynak[c].notna().sum()
        for c in kaynak.columns
        if c not in dokunulmayan_kolonlar
    }

    for grup, (ham_yol, deger_kolonlari) in AYLIK_CEYREKLIK_KAYNAKLAR.items():
        ham = pd.read_csv(ham_yol)
        referans_ay_col = f"{grup}_referans_ay"
        ham = ham.rename(columns={"referans_ayi": referans_ay_col})
        ham = ham[[referans_ay_col] + deger_kolonlari].drop_duplicates(subset=referans_ay_col)

        df = df.merge(ham, left_on="_ay_str", right_on=referans_ay_col, how="left")
        # NOT: merge sonrasi referans_ay_col zaten esleyen satirlarda "_ay_str" ile
        # ayni (referans_ayi == _ay_str oldugu icin), eslesmeyenlerde NaN - ek islem gerekmez.

    df = df.drop(columns=["_ay_str"])
    # kaynak tabloyla ayni sutun sirasi (okunabilirlik/karsilastirma icin)
    df = df[[c for c in kaynak.columns if c in df.columns]]

    df.to_csv(HEDEF_CSV, index=False, encoding="utf-8-sig")

    print("=== GENISLETME 26 - TAKVIM-AYI BAZLI GENISLETILMIS GUNLUK TABLO ===")
    print(f"Boyut: {df.shape[0]} satir x {df.shape[1]} sutun")
    print(f"Tarih araligi: {df['tarih'].min().date()} .. {df['tarih'].max().date()}")
    print()
    print("Sutun basina ESKI (as-of-tek-gun) -> YENI (takvim-ayi) doluluk:")
    for grup, (ham_yol, deger_kolonlari) in AYLIK_CEYREKLIK_KAYNAKLAR.items():
        for kolon in deger_kolonlari:
            yeni = df[kolon].notna().sum()
            print(f"  {kolon}: {eski_doluluk[kolon]}/{len(df)} -> {yeni}/{len(df)}")
    print(f"\nCikti: {HEDEF_CSV}")


if __name__ == "__main__":
    main()
