"""
GENIŞLETME AŞAMA 25c — Karışık-frekans (mixed-frequency) günlük tablo kurulumu.

(prompts/veri/25_gunluk_eur_altin_karisik_frekans_prompt.md, Görev 4)

TASARIM İLKESİ (proje sahibi onayladı, KESİN KURAL): Bu tablo AYLIK
kaynakları GÜNLÜK GÖRÜNÜME GETİRMEK İÇİN forward-fill KULLANMAZ. Günlük
tarih ekseninde (2015-01-01 -> bugün, her takvim günü bir satır) yalnızca:
  - DOĞASI GEREĞİ GÜNLÜK kaynaklar (USD/TRY, EUR/TRY) HER GÜNE gerçek
    değerle sahiptir.
  - AYLIK/ÇEYREKLİK/OLAY-BAZLI kaynaklar yalnızca kendi AS-OF (yayımlanma/
    gerçekleşme) gününde doludur, diğer tüm günlerde bilinçli olarak NaN
    kalır. Her aylık kaynak grubunun kendi "..._referans_ay" yardımcı
    sütunu vardır (hangi aya ait olduğunu gösterir).
Bu, tek bir tabloda iki farklı granülerliğin bilinçli biçimde bir arada
durduğu YAPISAL bir tasarımdır - hata değildir.

AS-OF TARİH VARSAYIMI (ÖNEMLİ, PM onayı gerekebilir - bkz. PM raporu):
Çoğu aylık kaynağın GERÇEK yayım günü bu projede kayıtlı değil (yalnızca
TÜFE'nin kendi yayim_tarihi sütunu var, ÖTV olaylarının kendi gerçek
olay tarihi var). Diğer TÜM aylık kaynaklar için AS-OF DİSİPLİNİNİ
KORUYAN, MUHAFAZAKAR (asla gerçek yayımdan daha ERKEN olmayan) tek bir
varsayım kullanıldı: referans ayın BİR SONRAKİ ayının 1. günü. Bu, gerçek
yayım tarihinden birkaç gün daha GERİYE düşebilir (ör. ODMD bültenleri
genelde ayın ilk haftasında çıkıyor, "1. gün" bunun biraz öncesinde kalır)
ama HİÇBİR ZAMAN gerçek yayımdan önce bir tarihe veri koymaz - yani
look-ahead (ileriye bakma) riski YOKTUR, yalnızca hafif bir gecikme riski
vardır (bu, as-of disiplini için güvenli tarafta kalan bir tercih).
proxy_fiyat (BETAM) için kaynağın kendi `yayim_ayi` sütunu (raporun hangi
ay başlığı altında çıktığı) kullanıldı - o ayın 1. günü.

Girdi: data/raw/{usdtry,eurtry,altintry,tufe,enag,noter_devir,odmd,osd,
tuketici_guveni,proxy_fiyat,alim_gucu,otv,faiz}
Çıktı: data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv
"""
import json
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw"
OUT_DIR = REPO_KOKU / "data" / "processed" / "dataframes"

BASLANGIC = "2015-01-01"

# ÖTV olaylarinin GERCEK (yaklastirilmamis) yururluk tarihleri - kaynak:
# scripts/veri/genisletme_4_otv_olaylari.py OLAYLAR listesi.
OTV_GERCEK_TARIHLER = {
    "2016-11": "2016-11-25", "2018-09": "2018-09-24", "2018-10": "2018-10-31",
    "2018-12": "2018-12-31", "2019-05": "2019-05-01", "2020-08": "2020-08-30",
    "2021-08": "2021-08-13", "2022-11": "2022-11-24", "2023-07": "2023-07-15",
    "2023-11": "2023-11-18", "2025-07": "2025-07-24",
}


def _ay_sonrasi_ilk_gun(referans_ayi: pd.Series) -> pd.Series:
    """referans_ayi 'YYYY-MM' -> o ayin bir SONRAKI ayinin 1. gunu (Timestamp)."""
    per = pd.PeriodIndex(referans_ayi, freq="M")
    return (per + 1).to_timestamp(how="start")


def _gunluk_evds_json_oku(json_yolu: Path, deger_alanlari: dict) -> pd.DataFrame:
    with open(json_yolu, encoding="utf-8") as f:
        payload = json.load(f)
    df = pd.DataFrame(payload["items"])
    df = df.rename(columns=deger_alanlari)
    df = df.drop(columns=["UNIXTIME"], errors="ignore")
    df["tarih"] = pd.to_datetime(df["Tarih"], format="%d-%m-%Y")
    df = df.drop(columns=["Tarih"])
    for c in deger_alanlari.values():
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.sort_values("tarih").reset_index(drop=True)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    bugun = pd.Timestamp.today().normalize()
    gunluk_eksen = pd.date_range(BASLANGIC, bugun, freq="D")
    df = pd.DataFrame({"tarih": gunluk_eksen})

    # ================= GUNLUK KAYNAKLAR (gercek gunluk deger) =================
    usdtry = _gunluk_evds_json_oku(
        RAW_DIR / "usdtry" / "usdtry_2015_bugun_raw.json",
        {"TP_DK_USD_A": "usdtry_alis", "TP_DK_USD_S": "usdtry_satis"},
    )
    usdtry["usdtry_orta"] = (usdtry["usdtry_alis"] + usdtry["usdtry_satis"]) / 2
    df = df.merge(usdtry, on="tarih", how="left")

    eurtry = _gunluk_evds_json_oku(
        RAW_DIR / "eurtry" / "eurtry_2015_bugun_raw.json",
        {"TP_DK_EUR_A": "eurtry_alis", "TP_DK_EUR_S": "eurtry_satis"},
    )
    eurtry["eurtry_orta"] = (eurtry["eurtry_alis"] + eurtry["eurtry_satis"]) / 2
    df = df.merge(eurtry, on="tarih", how="left")

    # ================= AYLIK KAYNAKLAR (yalnizca as-of gununde dolu) =================

    # --- Altin (aylik - Gorev 1 bulgusu, gunluk DEGIL) - as-of: kendi ay-sonu ankoru ---
    altin = pd.read_csv(RAW_DIR / "altintry" / "altintry_aylik_2015_bugun.csv")
    altin["tarih"] = _ay_sonrasi_ilk_gun(altin["referans_ayi"])
    altin["altin_referans_ay"] = altin["referans_ayi"]
    altin = altin[["tarih", "altin_referans_ay", "altin_gram_try"]]
    df = df.merge(altin, on="tarih", how="left")

    # --- TUFE - as-of: KENDI GERCEK yayim_tarihi sutunu ---
    tufe = pd.read_csv(RAW_DIR / "tufe" / "tufe_2024_bugun_aylik.csv")
    tufe["tarih"] = pd.to_datetime(tufe["yayim_tarihi"], errors="coerce")
    tufe["tufe_referans_ay"] = tufe["referans_ayi"]
    tufe = tufe[["tarih", "tufe_referans_ay", "tufe_endeks", "tufe_aylik_degisim", "tufe_yillik_degisim"]]
    df = df.merge(tufe, on="tarih", how="left")

    # --- ENAG - as-of: sonraki ayin 1. gunu (gercek yayim tarihi kayitli degil) ---
    # NOT: kaynak dosyada "enag_endeks" sutunu VAR ama tamamen bos (0/65 dolu) -
    # ENAG yalnizca aylik/yillik YUZDE DEGISIM yayimliyor, endeks SEVIYESI
    # yayimlamiyor. Bu bir birlestirme hatasi degil, kaynagin kendi dogasi -
    # bu yuzden bos sutun tabloya tasinmiyor (bkz. PM raporu).
    enag = pd.read_csv(RAW_DIR / "enag" / "enag_aylik_2021_2026.csv")
    enag["tarih"] = _ay_sonrasi_ilk_gun(enag["referans_ayi"])
    enag["enag_referans_ay"] = enag["referans_ayi"]
    enag = enag[["tarih", "enag_referans_ay", "enag_aylik_degisim", "enag_yillik_degisim"]]
    df = df.merge(enag, on="tarih", how="left")

    # --- Noter devri - as-of: sonraki ayin 1. gunu ---
    noter = pd.read_csv(RAW_DIR / "noter_devir" / "noter_devir_2015_bugun_aylik.csv")
    noter["tarih"] = _ay_sonrasi_ilk_gun(noter["referans_ayi"])
    noter["noter_referans_ay"] = noter["referans_ayi"]
    noter = noter[["tarih", "noter_referans_ay", "noter_devir_toplam_adet", "noter_devir_otomobil_adet"]]
    df = df.merge(noter, on="tarih", how="left")

    # --- ODMD - as-of: sonraki ayin 1. gunu ---
    odmd = pd.read_csv(RAW_DIR / "odmd" / "odmd_2015_bugun_aylik.csv")
    odmd["tarih"] = _ay_sonrasi_ilk_gun(odmd["referans_ayi"])
    odmd["odmd_referans_ay"] = odmd["referans_ayi"]
    odmd = odmd[["tarih", "odmd_referans_ay", "odmd_toplam_adet", "odmd_otomobil_adet", "odmd_hta_adet"]]
    df = df.merge(odmd, on="tarih", how="left")

    # --- OSD - as-of: sonraki ayin 1. gunu ---
    osd = pd.read_csv(RAW_DIR / "osd" / "osd_2024_bugun_aylik.csv")
    osd["tarih"] = _ay_sonrasi_ilk_gun(osd["referans_ayi"])
    osd["osd_referans_ay"] = osd["referans_ayi"]
    osd = osd[["tarih", "osd_referans_ay", "osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet"]]
    df = df.merge(osd, on="tarih", how="left")

    # --- Tuketici guveni - as-of: sonraki ayin 1. gunu ---
    tuketici = pd.read_csv(RAW_DIR / "tuketici_guveni" / "tuketici_guveni_2024_bugun_aylik.csv")
    tuketici["tarih"] = _ay_sonrasi_ilk_gun(tuketici["referans_ayi"])
    tuketici["tuketici_referans_ay"] = tuketici["referans_ayi"]
    tuketici = tuketici[["tarih", "tuketici_referans_ay", "tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi"]]
    df = df.merge(tuketici, on="tarih", how="left")

    # --- Proxy fiyat (BETAM) - as-of: kaynagin KENDI yayim_ayi'nin 1. gunu ---
    # ONEMLI BULGU (proaktif bildirim, bkz. PM raporu): BETAM zaman zaman IKI
    # referans ayini AYNI yayim_ayi'nda birlikte yayimliyor (ornegin 2024-01 ve
    # 2024-02 ikisi de yayim_ayi=2024-03'te cikmis) - bu, ayni as-of gune IKI
    # farkli referans_ayi satirinin dusmesine, dolayisiyla satir "fan-out"una
    # (satir COGALMASINA, tum tablodaki diger sutunlari da bozarak) yol aciyordu
    # - noter_referans_ay'da 3 fazla satir olarak tespit edildi. Cozum: ayni
    # as-of gune dusen catismalarda GERCEK VERISI OLAN ve en GUNCEL (en son)
    # referans_ayi'na ait satir tutulur (bkz. asagidaki siralama/drop_duplicates).
    proxy = pd.read_csv(RAW_DIR / "proxy_fiyat" / "proxy_fiyat_2024_bugun_raw.csv")
    proxy["tarih"] = pd.to_datetime(proxy["yayim_ayi"] + "-01", errors="coerce")
    proxy["proxy_referans_ay"] = proxy["referans_ayi"]
    proxy["_veri_var_mi"] = proxy["proxy_fiyat_cari_tl"].notna()
    proxy = proxy.sort_values(["tarih", "_veri_var_mi", "proxy_referans_ay"])
    proxy = proxy.drop_duplicates(subset="tarih", keep="last")
    proxy = proxy[["tarih", "proxy_referans_ay", "proxy_fiyat_cari_tl", "proxy_dom_gun", "proxy_satis_orani_pct"]]
    df = df.merge(proxy, on="tarih", how="left")

    # --- Alim gucu (ceyreklik -> aylik kopyalanmis kaynak) - as-of: sonraki ayin 1. gunu ---
    alim_gucu = pd.read_csv(RAW_DIR / "alim_gucu" / "alim_gucu_2018_bugun_aylik.csv")
    alim_gucu["tarih"] = _ay_sonrasi_ilk_gun(alim_gucu["referans_ayi"])
    alim_gucu["alim_gucu_referans_ay"] = alim_gucu["referans_ayi"]
    alim_gucu = alim_gucu[["tarih", "alim_gucu_referans_ay", "brut_ucret_maas_endeksi_2021_100"]]
    df = df.merge(alim_gucu, on="tarih", how="left")

    # --- Tasit kredisi + politika faizi - proje TASARIMI GEREGI aylik ortalama olarak
    # tutuluyor (kaynagi gunluk/haftalik olsa da, EVDS'ten cekilirken yerelde aylik
    # ortalamaya indirgeniyor - bkz. genisletme_3c_faiz.py). Bu gorev talimati yalniz
    # EUR/Altin'i gunluge cekmeyi istedi, faiz metodolojisini DEGISTIRMEDI - as-of:
    # sonraki ayin 1. gunu (digerleriyle tutarli).
    faiz = pd.read_csv(RAW_DIR / "faiz" / "faizler_2024_bugun_aylik.csv")
    faiz["tarih"] = _ay_sonrasi_ilk_gun(faiz["referans_ayi"])
    faiz["faiz_referans_ay"] = faiz["referans_ayi"]
    faiz = faiz[["tarih", "faiz_referans_ay", "tasit_kredisi_faiz", "politika_faizi"]]
    df = df.merge(faiz, on="tarih", how="left")

    # --- OTV olaylari - OLAY BAZLI, GERCEK tarihte isaretlenir (varsayim degil) ---
    otv = pd.read_csv(RAW_DIR / "otv" / "otv_olaylari_2015_bugun_aylik.csv")
    otv_olaylar = otv[otv["otv_event_ay_mi"] == 1].copy()
    otv_olaylar["tarih"] = otv_olaylar["referans_ayi"].map(OTV_GERCEK_TARIHLER)
    otv_olaylar["tarih"] = pd.to_datetime(otv_olaylar["tarih"])
    otv_olaylar["otv_referans_ay"] = otv_olaylar["referans_ayi"]
    otv_olaylar = otv_olaylar[["tarih", "otv_referans_ay", "otv_aciklama"]]
    otv_olaylar["otv_event_gunu_mu"] = 1
    df = df.merge(otv_olaylar, on="tarih", how="left")
    df["otv_event_gunu_mu"] = df["otv_event_gunu_mu"].fillna(0).astype(int)

    # ================= TAKVIM SUTUNLARI (turetilmis, tarih SILINMEZ) =================
    df["yil"] = df["tarih"].dt.year
    df["ay"] = df["tarih"].dt.month
    df["gun"] = df["tarih"].dt.day
    df["ceyrek"] = df["tarih"].dt.quarter
    df["haftanin_gunu"] = df["tarih"].dt.dayofweek  # 0=Pazartesi ... 6=Pazar
    df["yilin_gunu"] = df["tarih"].dt.dayofyear

    df = df.sort_values("tarih").reset_index(drop=True)

    hedef_csv = OUT_DIR / "df_gunluk_karisik_frekans_2015_bugun.csv"
    df.to_csv(hedef_csv, index=False, encoding="utf-8-sig")

    print("=== GENISLETME 25c - KARISIK FREKANS TABLOSU ===")
    print(f"Boyut: {df.shape[0]} satir x {df.shape[1]} sutun")
    print(f"Tarih araligi: {df['tarih'].min().date()} .. {df['tarih'].max().date()}")
    print()
    print("Sutun basina dolu/eksik ozet:")
    for c in df.columns:
        if c == "tarih":
            continue
        dolu = df[c].notna().sum()
        print(f"  {c}: {dolu}/{len(df)} dolu")
    print(f"\nCikti: {hedef_csv}")


if __name__ == "__main__":
    main()
