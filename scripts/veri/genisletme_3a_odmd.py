"""
GENIŞLETME AŞAMA 3a — ODMD sıfır araç (otomobil + hafif ticari) satış adetleri,
2015-01 -> bugün (kaynak seviyesi C — resmi dernek basın bülteni PDF'i).

2015-01'E GENİŞLETME (2018 sonrası): AYNI 3 Aralık 2024 bülteni (aşağıda
zaten bilinen kaynak) 500 DPI'da yeniden açılıp Ek 1/Ek 2 tablolarının
2015-2017 satırları okundu — YENİ bir PDF aramaya gerek kalmadı, tablo
zaten 2010'a kadar gidiyordu. Üç yılın (2015, 2016, 2017) hem Ek 1 hem Ek 2
aylık toplamları yayımlanan yıllık "Toplam" sütunuyla tek tek toplanıp
BİREBİR eşleştiği doğrulandı (2015: 968.017/725.596, 2016: 983.720/756.938,
2017: 956.194/722.759 — hepsi tutuyor).

YÖNTEM NOTU: ODMD basın bülteni PDF'leri Claude'un PDF-sayfa-goruntu
okuyucusuyla (Read araci, PDF sayfalarini goruntu olarak isler) okundu; ayrica
yerel pypdf metin çıkarımıyla da doğrulandı (WebFetch aracı bu PDF'leri ham
stream olarak döndürüyor, o yüzden kullanılmadı). Her bulten, ekinde
("Ek 1/2/3") **2010'dan itibaren TÜM yillarin TAMAMLANMIŞ aylik satirlarini**
iceren bir "10 Yıllık Ortalama" tablosu yayimliyor — bu, ilk yazımda
varsayılandan da geniş: 2018-2023 arası TAMAMEN bu ayni 2 bültenin ayni Ek 1/
Ek 2 tablolarında hazır bulundu, ayrıca 3'üncü bir PDF aramaya GEREK KALMADI.
Iki bültenin 2010-2023 satırları birebir aynı (çapraz-doğrulama: iki farklı
tarihte yayımlanmış PDF, aynı 14 yıllık tarihçeyi tekrarlıyor) ve satır
toplamları (Ocak..Aralık) yayımlanan "Toplam" sütunuyla manuel olarak
tutuyor (bkz. asağıdaki dogrulama).

Kaynaklar (Ek 1: Otomobil+HTA toplamı, Ek 2: yalnız Otomobil):
- ODMD Basın Bülteni 3 Aralık 2024, sayfa 7 (Ek 1) ve sayfa 8 (Ek 2)
  https://www.odmd.org.tr/folders/2837/categorial1docs/4791/ODMD%20Bas%C4%B1n%20Bulteni%203%20Aral%C4%B1k%202024.pdf
  -> tarihçe tablosu 2010-2024 (2024 satırı bu bültende henüz Ocak-Kasım,
     çünkü bülten 3 Aralık 2024'te yayımlanmış — Aralık verisi eksik).
- ODMD Basın Bülteni 2 Haziran 2026, sayfa 8 (Ek 1) ve sayfa 9 (Ek 2)
  https://www.odmd.org.tr/folders/2837/categorial1docs/6111/ODMD%20Bas%C4%B1n%20Bulteni%202%20Haziran%202026.docx.pdf
  -> tarihçe tablosu 2010-2026 (2024 TAMAMLANMIŞ — çapraz-doğrulama için
     kullanıldı —, 2025 TAMAMLANMIŞ, 2026 Ocak-Mayıs).
- Haziran 2026 TOPLAM rakamı ayrı bir kaynaktan (haber, web araması):
  alomaliye.com, "Otomotiv Pazarı İlk Yarıda Yüzde 8,19 Daraldı" (2 Temmuz 2026)
  -> yalnızca TOPLAM (Otomobil+HTA) verilmiş, otomobil-yalnız kırılımı YOK.

2018-2023 DOĞRULAMA: Her iki bültendeki Ek 1/Ek 2 tablolarının 2018-2023
satırları (aylık + "Toplam" sütunu) birebir aynı ve aylık değerlerin toplamı
yayımlanan yıllık "Toplam" değerine eşit (örn. Ek 1 2018: 35.076+47.009+
76.345+71.126+72.755+51.037+52.734+34.346+23.028+21.571+58.204+77.706 =
620.937 = yayımlanan Toplam). PDF sayfaları ayrıca Read araciyla (goruntu
modu) tekrar açılıp gözle teyit edildi.

BİLİNEN SINIR: Haziran 2026 için yalnızca toplam (105.041 adet) var,
otomobil-yalnız kırılımı bu turda bulunamadı (haber metninde yok) - NaN.
KAPSAM: Bu iki PDF'in tarihçe eki 2010'a kadar gidiyor; talep edilen 2018-01
başlangıcı bu iki kaynaktan tamamen (ek PDF aramadan) karşılandı.
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "odmd"

# Ek 1 (Otomobil + Hafif Ticari Araç toplamı) — "3 Aralık 2024" ve
# "2 Haziran 2026" bültenlerinin Ek-1 tablolarından birebir okunmuştur.
# 2018-2023: ayni Ek-1 "10 yillik tarihce" tablosunun tamamlanmis yillik
# satirlari (iki bultende birebir ayni, aylik toplamlar Toplam sutunuyla
# tutuyor).
ODMD_TOPLAM = {
    # 2015-2017: AYNI iki bultenin (3 Aralik 2024) Ek-1 "10 yillik tarihce"
    # tablosunun tamamlanmis satirlari (500 DPI'da tekrar okunmus, yayimlanan
    # yillik Toplam sutunuyla capraz dogrulandi - 2015: 968.017, 2016: 983.720,
    # 2017: 956.194, ucu de birebir tutuyor).
    "2015-01": 34615, "2015-02": 55331, "2015-03": 83302, "2015-04": 91602,
    "2015-05": 81542, "2015-06": 86158, "2015-07": 83836, "2015-08": 82577,
    "2015-09": 64025, "2015-10": 64255, "2015-11": 84601, "2015-12": 156173,
    "2016-01": 32713, "2016-02": 52825, "2016-03": 82948, "2016-04": 84887,
    "2016-05": 93904, "2016-06": 91540, "2016-07": 58533, "2016-08": 71556,
    "2016-09": 67593, "2016-10": 83000, "2016-11": 122309, "2016-12": 141912,
    "2017-01": 35323, "2017-02": 46965, "2017-03": 73802, "2017-04": 75988,
    "2017-05": 85422, "2017-06": 83658, "2017-07": 82297, "2017-08": 72536,
    "2017-09": 71352, "2017-10": 91752, "2017-11": 100859, "2017-12": 136240,
    "2018-01": 35076, "2018-02": 47009, "2018-03": 76345, "2018-04": 71126,
    "2018-05": 72755, "2018-06": 51037, "2018-07": 52734, "2018-08": 34346,
    "2018-09": 23028, "2018-10": 21571, "2018-11": 58204, "2018-12": 77706,
    "2019-01": 14373, "2019-02": 24875, "2019-03": 49221, "2019-04": 30971,
    "2019-05": 33016, "2019-06": 42688, "2019-07": 17927, "2019-08": 26246,
    "2019-09": 41992, "2019-10": 49075, "2019-11": 58176, "2019-12": 90500,
    "2020-01": 27273, "2020-02": 47122, "2020-03": 50008, "2020-04": 26457,
    "2020-05": 32235, "2020-06": 70973, "2020-07": 87401, "2020-08": 61533,
    "2020-09": 90619, "2020-10": 94733, "2020-11": 80141, "2020-12": 104293,
    "2021-01": 43728, "2021-02": 58504, "2021-03": 96428, "2021-04": 61488,
    "2021-05": 54734, "2021-06": 79819, "2021-07": 47849, "2021-08": 58454,
    "2021-09": 57141, "2021-10": 56746, "2021-11": 60216, "2021-12": 62243,
    "2022-01": 38131, "2022-02": 49652, "2022-03": 64267, "2022-04": 60035,
    "2022-05": 65167, "2022-06": 80652, "2022-07": 52206, "2022-08": 48336,
    "2022-09": 62084, "2022-10": 65222, "2022-11": 82311, "2022-12": 115220,
    "2023-01": 50894, "2023-02": 81148, "2023-03": 103929, "2023-04": 97679,
    "2023-05": 111556, "2023-06": 112163, "2023-07": 113959, "2023-08": 89454,
    "2023-09": 96793, "2023-10": 101367, "2023-11": 115040, "2023-12": 158653,
    "2024-01": 79701, "2024-02": 105990, "2024-03": 109828, "2024-04": 75919,
    "2024-05": 100305, "2024-06": 106238, "2024-07": 94037, "2024-08": 90134,
    "2024-09": 87740, "2024-10": 97274, "2024-11": 121094, "2024-12": 170249,
    "2025-01": 68654, "2025-02": 90730, "2025-03": 116900, "2025-04": 105352,
    "2025-05": 107730, "2025-06": 118611, "2025-07": 107718, "2025-08": 101650,
    "2025-09": 110302, "2025-10": 116149, "2025-11": 132984, "2025-12": 191620,
    "2026-01": 75362, "2026-02": 88039, "2026-03": 101997, "2026-04": 104298,
    "2026-05": 83442,
    "2026-06": 105041,  # alomaliye.com haberinden (yalnızca toplam)
}

# Ek 2 (yalnız Otomobil) — ayni iki bultenin Ek-2 tablosundan.
# 2018-2023: ayni Ek-2 "10 yillik tarihce" tablosunun tamamlanmis yillik
# satirlari (iki bultende birebir ayni).
ODMD_OTOMOBIL = {
    # 2015-2017: ayni bultenin Ek-2 tablosu, ayni yontemle capraz dogrulandi
    # (yillik Toplam: 2015: 725.596, 2016: 756.938, 2017: 722.759, ucu de tutuyor).
    "2015-01": 24498, "2015-02": 40817, "2015-03": 61676, "2015-04": 70211,
    "2015-05": 62878, "2015-06": 67766, "2015-07": 64218, "2015-08": 61753,
    "2015-09": 47088, "2015-10": 47954, "2015-11": 62397, "2015-12": 114340,
    "2016-01": 23358, "2016-02": 40588, "2016-03": 63975, "2016-04": 65618,
    "2016-05": 73832, "2016-06": 71111, "2016-07": 45566, "2016-08": 53977,
    "2016-09": 51340, "2016-10": 63746, "2016-11": 95783, "2016-12": 108044,
    "2017-01": 25689, "2017-02": 34658, "2017-03": 55616, "2017-04": 57998,
    "2017-05": 65799, "2017-06": 66164, "2017-07": 62384, "2017-08": 54890,
    "2017-09": 53423, "2017-10": 70488, "2017-11": 75956, "2017-12": 99694,
    "2018-01": 26611, "2018-02": 35901, "2018-03": 59798, "2018-04": 55108,
    "2018-05": 57227, "2018-06": 41225, "2018-07": 42024, "2018-08": 26976,
    "2018-09": 17595, "2018-10": 16809, "2018-11": 46204, "2018-12": 60843,
    "2019-01": 10979, "2019-02": 19205, "2019-03": 38628, "2019-04": 24416,
    "2019-05": 27126, "2019-06": 36024, "2019-07": 15398, "2019-08": 21544,
    "2019-09": 35308, "2019-10": 39996, "2019-11": 47803, "2019-12": 70829,
    "2020-01": 22016, "2020-02": 37727, "2020-03": 39887, "2020-04": 21825,
    "2020-05": 25073, "2020-06": 57067, "2020-07": 69427, "2020-08": 44372,
    "2020-09": 71296, "2020-10": 76341, "2020-11": 64357, "2020-12": 80721,
    "2021-01": 35358, "2021-02": 44749, "2021-03": 76357, "2021-04": 48375,
    "2021-05": 43138, "2021-06": 62348, "2021-07": 36311, "2021-08": 44756,
    "2021-09": 43408, "2021-10": 40512, "2021-11": 42982, "2021-12": 43559,
    "2022-01": 29020, "2022-02": 37641, "2022-03": 50173, "2022-04": 45564,
    "2022-05": 51750, "2022-06": 64134, "2022-07": 41031, "2022-08": 35230,
    "2022-09": 44681, "2022-10": 47440, "2022-11": 59222, "2022-12": 86774,
    "2023-01": 37288, "2023-02": 58907, "2023-03": 79226, "2023-04": 77398,
    "2023-05": 87418, "2023-06": 91135, "2023-07": 87416, "2023-08": 69131,
    "2023-09": 78971, "2023-10": 82611, "2023-11": 91424, "2023-12": 126416,
    "2024-01": 64041, "2024-02": 82277, "2024-03": 87071, "2024-04": 61448,
    "2024-05": 80260, "2024-06": 87858, "2024-07": 73396, "2024-08": 69288,
    "2024-09": 69634, "2024-10": 75662, "2024-11": 94595, "2024-12": 134811,
    "2025-01": 55944, "2025-02": 76021, "2025-03": 91828, "2025-04": 85411,
    "2025-05": 85123, "2025-06": 93676, "2025-07": 84195, "2025-08": 82215,
    "2025-09": 88274, "2025-10": 90695, "2025-11": 104795, "2025-12": 146319,
    "2026-01": 61055, "2026-02": 69776, "2026-03": 79857, "2026-04": 80182,
    "2026-05": 65386,
    # 2026-06: BİLİNMİYOR (haber yalnızca toplamı verdi) -> NaN
}


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    aylar = sorted(ODMD_TOPLAM.keys())
    df = pd.DataFrame({
        "referans_ayi": aylar,
        "odmd_toplam_adet": [ODMD_TOPLAM[a] for a in aylar],
        "odmd_otomobil_adet": [ODMD_OTOMOBIL.get(a) for a in aylar],
    })
    df["odmd_hta_adet"] = df["odmd_toplam_adet"] - df["odmd_otomobil_adet"]

    csv_yolu = RAW_DIR / "odmd_2015_bugun_aylik.csv"
    xlsx_yolu = RAW_DIR / "odmd_2015_bugun_aylik.xlsx"
    df.to_csv(csv_yolu, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_yolu, index=False, sheet_name="odmd_aylik")

    print("=== GENISLETME 3a - ODMD SIFIR ARAC SATISI OZET ===")
    print(f"Kaynak seviyesi: C (ODMD basın bülteni PDF, Ek 1/2 tabloları)")
    print(f"Kapsam: {aylar[0]} .. {aylar[-1]} ({len(aylar)} ay)")
    print(f"odmd_otomobil_adet eksik ay: {df[df['odmd_otomobil_adet'].isna()]['referans_ayi'].tolist()}")
    print()
    print(df.to_string(index=False))
    print(f"\nCikti: {csv_yolu} , {xlsx_yolu}")


if __name__ == "__main__":
    main()
