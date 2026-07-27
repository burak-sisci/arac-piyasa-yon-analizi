"""
GENIŞLETME AŞAMA 2a — Noter devir adedi (el değiştiren araç sayısı),
2018-01 -> 2026-06 (kaynak seviyesi B — resmi TÜİK indirilebilir tablosu).

ONCEKI DENEME (pm_rapor_genisletme_asama2_5.md, Bolum 3.1): TÜİK veri portali
(veriportali.tuik.gov.tr) WebFetch ile okunamiyordu (JS-render SPA) - HATA
LISTESINE birakilmisti. AYRICA: WebSearch ile toplanan birkac aylik veride
CIDDI BIR YIL-KARISMASI HATASI tespit edildi (2024 sorgulari 2025/2026
verisi donduruyordu) - bu yuzden o veriler KULLANILMADI, TAMAMEN YENIDEN
COZULDU.

COZUM (2024-01 -> 2026-06 turu): TÜİK veri portali, JS render eden bir
tarayici araciyla gezilerek OKUNABILDI (WebFetch'in aksine). Her "Motorlu
Kara Taşıtları" aylik bulteninin "Tablolar" bolumunde "Aylara göre devri
yapılan motorlu kara taşıtları sayısı" adinda DOGRUDAN INDIRILEBILIR bir
.xls dosyasi var (TÜİK'in kendi resmi API'si, /api/tr/data/downloads?...
formatinda). Bu tablo HER ZAMAN "cari yil + bir onceki yil" karsilastirmasi
seklinde (ODMD'nin aksine, TUM tarihceyi degil yalnizca 2 yili icerir) - bu
yuzden HER 2 YIL icin AYRI bir Aralik bulteni gerekti:
- "Motorlu Kara Taşıtları - Aralık 2025" bulteni (Sayi 54047, yayim 16 Ocak
  2026) -> 2024 (tam yil) + 2025 (tam yil) tablosu.
- "Motorlu Kara Taşıtları - Haziran 2026" bulteni (Sayi 58043, yayim 17
  Temmuz 2026) -> 2025 (tam yil, capraz-dogrulama) + 2026 Ocak-Haziran
  (kismi yil) tablosu.
2025 degerleri HER IKI bultende de BIREBIR AYNI cikti (capraz-dogrulandi).

GENISLETME (2018-01 -> 2023-12 turu, geriye donuk): Kullanicinin istegi
uzerine, ayni "Aylara göre devri..." tablosu 3 EK ESKI ARALIK BULTENI
kullanilarak 2018'e kadar geriye genisletildi (TÜİK veri portalindaki
"Önceki Bültenler" zincirinden, aydan aya geriye navigasyonla bulundu -
site 7 aylik parcalar halinde geriye link veriyor, dogrudan bir arsiv/arama
sayfasi yok):
- "Motorlu Kara Taşıtları - Aralık 2023" bulteni (Sayi 49432, yayim 23 Ocak
  2024, https://veriportali.tuik.gov.tr/tr/press/49432) -> 2022 (tam yil) +
  2023 (tam yil) tablosu.
- "Motorlu Kara Taşıtları - Aralık 2021" bulteni (Sayi 45703, yayim 26 Ocak
  2022, https://veriportali.tuik.gov.tr/tr/press/45703) -> 2020 (tam yil) +
  2021 (tam yil) tablosu.
- "Motorlu Kara Taşıtları - Aralık 2019" bulteni (Sayi 33648, yayim 30 Ocak
  2020, https://veriportali.tuik.gov.tr/tr/press/33648) -> 2018 (tam yil) +
  2019 (tam yil) tablosu.
Her uc bulten de dogrudan indirilebilir ayni turden .xls tablosunu
iceriyordu (OLE2/BIFF8 formatinda, gercek TÜİK API yaniti - HTML degil,
binary dogrulandi). Rastgele secilen birkac deger (ör. Aralik 2019=1.022.892,
Aralik 2021=906.917, Mart 2020=720.025, Ekim 2020=833.754, Mayis 2021=457.001,
Mart 2022=762.321, Ekim 2022=762.921, Mayis 2023=1.104.572, Aralik 2023=
838.871) ilgili bultenin "Aralik ayinda X adet taşıtın devri yapıldı" metin
cumlesiyle BIREBIR karsilastirilarak dogrulandi - tamami eslesti. 2022 ve
2020 degerleri de (cakisan yillar) iki komsu bultende birebir ayni cikti.
Boylece 2018-01 -> 2023-12 arasi 72 ay, 0 eksik, tamamen resmi kaynaktan
(kaynak seviyesi B) tamamlandi.

YIL-KARISMASI DUZELTMESI (onemli, izlenebilirlik icin): Onceki turda
WebSearch'ten toplanan bazi degerler bu resmi tabloyla KARSILASTIRILDI:
- "Subat 2024 = 762.109" (eski, WebSearch) YANLIS - bu aslinda Subat 2025'in
  degeri. Dogru Subat 2024 = 847.861.
- "Mayis 2024 = 752.150" (eski, WebSearch) YANLIS - bu aslinda Mayis 2026'nin
  degeri. Dogru Mayis 2024 = 920.604.
- "Ocak 2024 = 782.589" ve "Mart 2024 = 865.144" (eski, WebSearch) DOGRU
  cikti - bu resmi tabloyla birebir eslesiyor.
Bu, projenin genel bir uyarisi olarak not edilmeli: WebSearch'ten toplanan
TÜİK istatistikleri (ozellikle yil bilgisi iceren) DOGRULANMADAN
kullanilmamalidir.
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "noter_devir"

# Her deger, ilgili TÜİK bülteninin "Aylara göre devri yapılan motorlu kara
# taşıtları sayısı" adlı resmi .xls tablosundan (Toplam, Otomobil sütunları)
# birebir okunmuştur.
KAYITLAR = [
    # --- 2018 (kaynak: "Aralık 2019" bülteni, Sayı 33648) ---
    dict(referans_ayi="2018-01", noter_devir_toplam_adet=631823, noter_devir_otomobil_adet=445255),
    dict(referans_ayi="2018-02", noter_devir_toplam_adet=597953, noter_devir_otomobil_adet=419533),
    dict(referans_ayi="2018-03", noter_devir_toplam_adet=681359, noter_devir_otomobil_adet=478648),
    dict(referans_ayi="2018-04", noter_devir_toplam_adet=684291, noter_devir_otomobil_adet=479866),
    dict(referans_ayi="2018-05", noter_devir_toplam_adet=672053, noter_devir_otomobil_adet=472478),
    dict(referans_ayi="2018-06", noter_devir_toplam_adet=617217, noter_devir_otomobil_adet=443151),
    dict(referans_ayi="2018-07", noter_devir_toplam_adet=748935, noter_devir_otomobil_adet=541226),
    dict(referans_ayi="2018-08", noter_devir_toplam_adet=600922, noter_devir_otomobil_adet=429606),
    dict(referans_ayi="2018-09", noter_devir_toplam_adet=641574, noter_devir_otomobil_adet=438784),
    dict(referans_ayi="2018-10", noter_devir_toplam_adet=632321, noter_devir_otomobil_adet=432074),
    dict(referans_ayi="2018-11", noter_devir_toplam_adet=603776, noter_devir_otomobil_adet=427626),
    dict(referans_ayi="2018-12", noter_devir_toplam_adet=620504, noter_devir_otomobil_adet=435240),
    # --- 2019 (kaynak: "Aralık 2019" bülteni, Sayı 33648) ---
    dict(referans_ayi="2019-01", noter_devir_toplam_adet=507017, noter_devir_otomobil_adet=357926),
    dict(referans_ayi="2019-02", noter_devir_toplam_adet=535037, noter_devir_otomobil_adet=375577),
    dict(referans_ayi="2019-03", noter_devir_toplam_adet=643356, noter_devir_otomobil_adet=456674),
    dict(referans_ayi="2019-04", noter_devir_toplam_adet=661504, noter_devir_otomobil_adet=468217),
    dict(referans_ayi="2019-05", noter_devir_toplam_adet=721196, noter_devir_otomobil_adet=518368),
    dict(referans_ayi="2019-06", noter_devir_toplam_adet=565596, noter_devir_otomobil_adet=399916),
    dict(referans_ayi="2019-07", noter_devir_toplam_adet=731426, noter_devir_otomobil_adet=516730),
    dict(referans_ayi="2019-08", noter_devir_toplam_adet=624936, noter_devir_otomobil_adet=444290),
    dict(referans_ayi="2019-09", noter_devir_toplam_adet=821147, noter_devir_otomobil_adet=586534),
    dict(referans_ayi="2019-10", noter_devir_toplam_adet=919501, noter_devir_otomobil_adet=674379),
    dict(referans_ayi="2019-11", noter_devir_toplam_adet=921379, noter_devir_otomobil_adet=679150),
    dict(referans_ayi="2019-12", noter_devir_toplam_adet=1022892, noter_devir_otomobil_adet=749700),
    # --- 2020 (kaynak: "Aralık 2021" bülteni, Sayı 45703) ---
    dict(referans_ayi="2020-01", noter_devir_toplam_adet=856697, noter_devir_otomobil_adet=628765),
    dict(referans_ayi="2020-02", noter_devir_toplam_adet=843550, noter_devir_otomobil_adet=611314),
    dict(referans_ayi="2020-03", noter_devir_toplam_adet=720025, noter_devir_otomobil_adet=501921),
    dict(referans_ayi="2020-04", noter_devir_toplam_adet=348678, noter_devir_otomobil_adet=231977),
    dict(referans_ayi="2020-05", noter_devir_toplam_adet=561375, noter_devir_otomobil_adet=381708),
    dict(referans_ayi="2020-06", noter_devir_toplam_adet=1097112, noter_devir_otomobil_adet=773260),
    dict(referans_ayi="2020-07", noter_devir_toplam_adet=995755, noter_devir_otomobil_adet=721519),
    dict(referans_ayi="2020-08", noter_devir_toplam_adet=833749, noter_devir_otomobil_adet=589426),
    dict(referans_ayi="2020-09", noter_devir_toplam_adet=916048, noter_devir_otomobil_adet=647573),
    dict(referans_ayi="2020-10", noter_devir_toplam_adet=833754, noter_devir_otomobil_adet=583983),
    dict(referans_ayi="2020-11", noter_devir_toplam_adet=663614, noter_devir_otomobil_adet=456110),
    dict(referans_ayi="2020-12", noter_devir_toplam_adet=544583, noter_devir_otomobil_adet=349599),
    # --- 2021 (kaynak: "Aralık 2021" bülteni, Sayı 45703) ---
    dict(referans_ayi="2021-01", noter_devir_toplam_adet=462753, noter_devir_otomobil_adet=295756),
    dict(referans_ayi="2021-02", noter_devir_toplam_adet=497153, noter_devir_otomobil_adet=316722),
    dict(referans_ayi="2021-03", noter_devir_toplam_adet=690994, noter_devir_otomobil_adet=451956),
    dict(referans_ayi="2021-04", noter_devir_toplam_adet=610094, noter_devir_otomobil_adet=405351),
    dict(referans_ayi="2021-05", noter_devir_toplam_adet=457001, noter_devir_otomobil_adet=302320),
    dict(referans_ayi="2021-06", noter_devir_toplam_adet=842050, noter_devir_otomobil_adet=575336),
    dict(referans_ayi="2021-07", noter_devir_toplam_adet=666610, noter_devir_otomobil_adet=465721),
    dict(referans_ayi="2021-08", noter_devir_toplam_adet=799556, noter_devir_otomobil_adet=549004),
    dict(referans_ayi="2021-09", noter_devir_toplam_adet=863167, noter_devir_otomobil_adet=596395),
    dict(referans_ayi="2021-10", noter_devir_toplam_adet=884090, noter_devir_otomobil_adet=631072),
    dict(referans_ayi="2021-11", noter_devir_toplam_adet=1135228, noter_devir_otomobil_adet=813548),
    dict(referans_ayi="2021-12", noter_devir_toplam_adet=906917, noter_devir_otomobil_adet=611862),
    # --- 2022 (kaynak: "Aralık 2023" bülteni, Sayı 49432) ---
    dict(referans_ayi="2022-01", noter_devir_toplam_adet=467240, noter_devir_otomobil_adet=303354),
    dict(referans_ayi="2022-02", noter_devir_toplam_adet=571505, noter_devir_otomobil_adet=372156),
    dict(referans_ayi="2022-03", noter_devir_toplam_adet=762321, noter_devir_otomobil_adet=503040),
    dict(referans_ayi="2022-04", noter_devir_toplam_adet=888543, noter_devir_otomobil_adet=605162),
    dict(referans_ayi="2022-05", noter_devir_toplam_adet=969308, noter_devir_otomobil_adet=673167),
    dict(referans_ayi="2022-06", noter_devir_toplam_adet=1030671, noter_devir_otomobil_adet=710088),
    dict(referans_ayi="2022-07", noter_devir_toplam_adet=647472, noter_devir_otomobil_adet=429378),
    dict(referans_ayi="2022-08", noter_devir_toplam_adet=748879, noter_devir_otomobil_adet=478053),
    dict(referans_ayi="2022-09", noter_devir_toplam_adet=740861, noter_devir_otomobil_adet=476502),
    dict(referans_ayi="2022-10", noter_devir_toplam_adet=762921, noter_devir_otomobil_adet=500691),
    dict(referans_ayi="2022-11", noter_devir_toplam_adet=868001, noter_devir_otomobil_adet=580271),
    dict(referans_ayi="2022-12", noter_devir_toplam_adet=1106203, noter_devir_otomobil_adet=764329),
    # --- 2023 (kaynak: "Aralık 2023" bülteni, Sayı 49432) ---
    dict(referans_ayi="2023-01", noter_devir_toplam_adet=921387, noter_devir_otomobil_adet=647852),
    dict(referans_ayi="2023-02", noter_devir_toplam_adet=704954, noter_devir_otomobil_adet=492985),
    dict(referans_ayi="2023-03", noter_devir_toplam_adet=1066442, noter_devir_otomobil_adet=737443),
    dict(referans_ayi="2023-04", noter_devir_toplam_adet=1025170, noter_devir_otomobil_adet=715113),
    dict(referans_ayi="2023-05", noter_devir_toplam_adet=1104572, noter_devir_otomobil_adet=741828),
    dict(referans_ayi="2023-06", noter_devir_toplam_adet=892197, noter_devir_otomobil_adet=583627),
    dict(referans_ayi="2023-07", noter_devir_toplam_adet=901725, noter_devir_otomobil_adet=567274),
    dict(referans_ayi="2023-08", noter_devir_toplam_adet=893913, noter_devir_otomobil_adet=551474),
    dict(referans_ayi="2023-09", noter_devir_toplam_adet=774507, noter_devir_otomobil_adet=474248),
    dict(referans_ayi="2023-10", noter_devir_toplam_adet=723001, noter_devir_otomobil_adet=449265),
    dict(referans_ayi="2023-11", noter_devir_toplam_adet=705023, noter_devir_otomobil_adet=452347),
    dict(referans_ayi="2023-12", noter_devir_toplam_adet=838871, noter_devir_otomobil_adet=551244),
    # --- 2024 (kaynak: "Aralık 2025" bülteni, Sayı 54047) ---
    dict(referans_ayi="2024-01", noter_devir_toplam_adet=782589, noter_devir_otomobil_adet=530744),
    dict(referans_ayi="2024-02", noter_devir_toplam_adet=847861, noter_devir_otomobil_adet=573508),
    dict(referans_ayi="2024-03", noter_devir_toplam_adet=865144, noter_devir_otomobil_adet=580492),
    dict(referans_ayi="2024-04", noter_devir_toplam_adet=801439, noter_devir_otomobil_adet=515415),
    dict(referans_ayi="2024-05", noter_devir_toplam_adet=920604, noter_devir_otomobil_adet=588886),
    dict(referans_ayi="2024-06", noter_devir_toplam_adet=676083, noter_devir_otomobil_adet=435828),
    dict(referans_ayi="2024-07", noter_devir_toplam_adet=957920, noter_devir_otomobil_adet=621748),
    dict(referans_ayi="2024-08", noter_devir_toplam_adet=935945, noter_devir_otomobil_adet=613752),
    dict(referans_ayi="2024-09", noter_devir_toplam_adet=992171, noter_devir_otomobil_adet=658566),
    dict(referans_ayi="2024-10", noter_devir_toplam_adet=1006009, noter_devir_otomobil_adet=680849),
    dict(referans_ayi="2024-11", noter_devir_toplam_adet=917715, noter_devir_otomobil_adet=630035),
    dict(referans_ayi="2024-12", noter_devir_toplam_adet=985633, noter_devir_otomobil_adet=673727),
    # --- 2025 (kaynak: "Aralık 2025" bülteni; "Haziran 2026" bülteniyle capraz-dogrulandi) ---
    dict(referans_ayi="2025-01", noter_devir_toplam_adet=813093, noter_devir_otomobil_adet=551610),
    dict(referans_ayi="2025-02", noter_devir_toplam_adet=762109, noter_devir_otomobil_adet=520697),
    dict(referans_ayi="2025-03", noter_devir_toplam_adet=821238, noter_devir_otomobil_adet=555093),
    dict(referans_ayi="2025-04", noter_devir_toplam_adet=957499, noter_devir_otomobil_adet=644473),
    dict(referans_ayi="2025-05", noter_devir_toplam_adet=960640, noter_devir_otomobil_adet=645718),
    dict(referans_ayi="2025-06", noter_devir_toplam_adet=840022, noter_devir_otomobil_adet=559842),
    dict(referans_ayi="2025-07", noter_devir_toplam_adet=1015974, noter_devir_otomobil_adet=680114),
    dict(referans_ayi="2025-08", noter_devir_toplam_adet=985244, noter_devir_otomobil_adet=659915),
    dict(referans_ayi="2025-09", noter_devir_toplam_adet=1019994, noter_devir_otomobil_adet=680684),
    dict(referans_ayi="2025-10", noter_devir_toplam_adet=981225, noter_devir_otomobil_adet=666842),
    dict(referans_ayi="2025-11", noter_devir_toplam_adet=897877, noter_devir_otomobil_adet=608924),
    dict(referans_ayi="2025-12", noter_devir_toplam_adet=1158490, noter_devir_otomobil_adet=798616),
    # --- 2026 (kaynak: "Haziran 2026" bülteni, Sayı 58043) ---
    dict(referans_ayi="2026-01", noter_devir_toplam_adet=827673, noter_devir_otomobil_adet=582180),
    dict(referans_ayi="2026-02", noter_devir_toplam_adet=806588, noter_devir_otomobil_adet=556805),
    dict(referans_ayi="2026-03", noter_devir_toplam_adet=870992, noter_devir_otomobil_adet=597104),
    dict(referans_ayi="2026-04", noter_devir_toplam_adet=919896, noter_devir_otomobil_adet=605480),
    dict(referans_ayi="2026-05", noter_devir_toplam_adet=752150, noter_devir_otomobil_adet=503057),
    dict(referans_ayi="2026-06", noter_devir_toplam_adet=941964, noter_devir_otomobil_adet=608484),
]

KAYNAK_URL_2018_2019 = "https://veriportali.tuik.gov.tr/tr/press/33648"  # Motorlu Kara Taşıtları - Aralık 2019
KAYNAK_URL_2020_2021 = "https://veriportali.tuik.gov.tr/tr/press/45703"  # Motorlu Kara Taşıtları - Aralık 2021
KAYNAK_URL_2022_2023 = "https://veriportali.tuik.gov.tr/tr/press/49432"  # Motorlu Kara Taşıtları - Aralık 2023
KAYNAK_URL_2024_2025 = "https://veriportali.tuik.gov.tr/tr/press/54047"  # Motorlu Kara Taşıtları - Aralık 2025
KAYNAK_URL_2025_2026 = "https://veriportali.tuik.gov.tr/tr/press/58043"  # Motorlu Kara Taşıtları - Haziran 2026


def _kaynak_url(ay: str) -> str:
    if ay < "2020-01":
        return KAYNAK_URL_2018_2019
    if ay < "2022-01":
        return KAYNAK_URL_2020_2021
    if ay < "2024-01":
        return KAYNAK_URL_2022_2023
    if ay < "2026-01":
        return KAYNAK_URL_2024_2025
    return KAYNAK_URL_2025_2026


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(KAYITLAR).sort_values("referans_ayi").reset_index(drop=True)
    df["kaynak_url"] = df["referans_ayi"].apply(_kaynak_url)

    hedef_csv = RAW_DIR / "noter_devir_2024_bugun_aylik.csv"
    hedef_xlsx = RAW_DIR / "noter_devir_2024_bugun_aylik.xlsx"
    df.to_csv(hedef_csv, index=False, encoding="utf-8-sig")
    df.to_excel(hedef_xlsx, index=False, sheet_name="noter_devir_aylik")

    beklenen_aylar = pd.period_range("2018-01", "2026-06", freq="M").astype(str).tolist()
    gelen_aylar = df["referans_ayi"].tolist()
    eksik_aylar = [ay for ay in beklenen_aylar if ay not in gelen_aylar]

    print("=== GENISLETME 2a - NOTER DEVIR ADEDI OZETI ===")
    print("Kaynak seviyesi: B (resmi TÜİK indirilebilir .xls tablosu, 5 bülten)")
    print(f"Kapsam: 2018-01 .. 2026-06 ({len(df)} satir)")
    print(f"Eksik ay: {eksik_aylar if eksik_aylar else 'yok'}")
    print()
    print(df[["referans_ayi", "noter_devir_toplam_adet", "noter_devir_otomobil_adet"]].to_string(index=False))
    print(f"\nCikti: {hedef_csv} , {hedef_xlsx}")
    print(f"\nNot: cikti dosya adi tarihsel nedenlerle '_2024_bugun_' iceriyor ancak")
    print(f"artik 2018-01'den itibaren tam tarihceyi kapsiyor (genisletme_5_birlestir.py")
    print(f"bu dosyayi ayni adla okuyor, dosya adi degistirilmedi).")


if __name__ == "__main__":
    main()
