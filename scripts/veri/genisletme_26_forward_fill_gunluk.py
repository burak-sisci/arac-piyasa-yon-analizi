"""
GENIŞLETME AŞAMA 26 — Forward-fill'li günlük tablo (25 numaralı gorevin
as-of/sizintisiz tablosuna EK, onun YERINE DEGIL).

(prompts/veri/26_forward_fill_gunluk_tablo_prompt.md, Gorev 1-2)

TASARIM ILKESI: 25 numarali gorevin cikardigi
df_gunluk_karisik_frekans_2015_bugun.csv DEGISTIRILMEDEN OKUNUR; bu script
onun YANINA, forward-fill uygulanmis AYRI bir dosya (
df_gunluk_forward_fill_2015_bugun.csv) uretir. Iki tablo da ayri ayri var
olmaya devam eder.

FORWARD-FILL MANTIGI: Her aylik/ceyreklik kaynak sutunu zaten yalnizca
kendi as-of gununde dolu, digerlerinde NaN (25 nolu gorevin ciktisi). Bir
sutuna dogrudan .ffill() uygulamak, bu deseni TAM istenen sekilde
genisletir: bir sonraki gercek as-of deger gelene kadar en son gercek
degeri ileri tasir, ay degisince (yeni as-of deger geldiginde) otomatik
guncellenir - onceki ayin degeri asla ATLANMAZ/karismaz. Ilk as-of
degerinden ONCEKI gunler NaN kalir (geriye doldurma yok - .ffill()
zaten bunu dogal olarak yapar).

Her forward-fill edilen DEGER sutunu icin "<sutun>_gercek_mi" bayragi
eklenir: 1 = o gun GERCEK as-of gunu (orijinal tabloda da doluydu),
0 = ya onceki ayin tasinan degeri ya da henuz hic veri gelmemis donem
(ikisi de "o gun gercekten acmiklanmadi" anlaminda 0'dir).

DOKUNULMAYANLAR: usdtry_*/eurtry_* (zaten gunluk), otv_* (olay-bazli,
forward-fill anlamsiz - YAPMA listesine gore), takvim sutunlari
(yil/ay/gun/ceyrek/haftanin_gunu/yilin_gunu), tarih.

Referans_ay yardimci sutunlari (orn. noter_referans_ay) da forward-fill
edildi (hangi ayin degerinin o gun gosterildigini okunur kilmak icin) -
bu, gorev talimatinda acikca istenmedi ama forward-fill tablosunun
kullanilabilirligi icin gerekli bir yorumlayici karar; PM raporunda
belirtilir.

Girdi: data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv
Cikti: data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
KAYNAK_CSV = DF_DIR / "df_gunluk_karisik_frekans_2015_bugun.csv"
HEDEF_CSV = DF_DIR / "df_gunluk_forward_fill_2015_bugun.csv"

# grup_adi -> (referans_ay_sutunu, [deger_sutunlari])
AYLIK_CEYREKLIK_GRUPLAR = {
    "altin": ("altin_referans_ay", ["altin_gram_try"]),
    "tufe": ("tufe_referans_ay", ["tufe_endeks", "tufe_aylik_degisim", "tufe_yillik_degisim"]),
    "enag": ("enag_referans_ay", ["enag_aylik_degisim", "enag_yillik_degisim"]),
    "noter": ("noter_referans_ay", ["noter_devir_toplam_adet", "noter_devir_otomobil_adet"]),
    "odmd": ("odmd_referans_ay", ["odmd_toplam_adet", "odmd_otomobil_adet", "odmd_hta_adet"]),
    "osd": ("osd_referans_ay", ["osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet"]),
    "tuketici": ("tuketici_referans_ay", ["tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi"]),
    "proxy": ("proxy_referans_ay", ["proxy_fiyat_cari_tl", "proxy_dom_gun", "proxy_satis_orani_pct"]),
    "alim_gucu": ("alim_gucu_referans_ay", ["brut_ucret_maas_endeksi_2021_100"]),
    "faiz": ("faiz_referans_ay", ["tasit_kredisi_faiz", "politika_faizi"]),
}


def main():
    df = pd.read_csv(KAYNAK_CSV, parse_dates=["tarih"])
    df = df.sort_values("tarih").reset_index(drop=True)

    eski_doluluk = {c: df[c].notna().sum() for c in df.columns if c != "tarih"}

    for grup, (referans_ay_col, deger_kolonlari) in AYLIK_CEYREKLIK_GRUPLAR.items():
        df[referans_ay_col] = df[referans_ay_col].ffill()
        for kolon in deger_kolonlari:
            bayrak = f"{kolon}_gercek_mi"
            df[bayrak] = df[kolon].notna().astype(int)
            df[kolon] = df[kolon].ffill()

    # otv_*, usdtry_*, eurtry_*, takvim sutunlari: DOKUNULMADI (kaynaktan aynen geldi)

    df.to_csv(HEDEF_CSV, index=False, encoding="utf-8-sig")

    print("=== GENISLETME 26 - FORWARD-FILL GUNLUK TABLO ===")
    print(f"Boyut: {df.shape[0]} satir x {df.shape[1]} sutun")
    print(f"Tarih araligi: {df['tarih'].min().date()} .. {df['tarih'].max().date()}")
    print()
    print("Sutun basina ESKI -> YENI doluluk (yalnizca degisen sutunlar):")
    for grup, (referans_ay_col, deger_kolonlari) in AYLIK_CEYREKLIK_GRUPLAR.items():
        for kolon in deger_kolonlari:
            yeni = df[kolon].notna().sum()
            print(f"  {kolon}: {eski_doluluk[kolon]}/{len(df)} -> {yeni}/{len(df)}")
    print(f"\nCikti: {HEDEF_CSV}")


if __name__ == "__main__":
    main()
