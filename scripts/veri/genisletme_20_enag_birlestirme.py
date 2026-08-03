"""
GENIŞLETME AŞAMA 20 — ENAG E-TÜFE tek/kapsamlı seri: 2021-01 -> 2026-06.

NEDEN: ENAG verisi iki ayrı görevde toplanmıştı — genisletme_12_enag_cekme.py
(2024-01 -> 2026-06, "ana" görev) ve 2018'e geriye genişletme denemesi
(2021-01 -> 2023-12, "genisletme" görev, prompts/veri/20_enag_2018_genisletme_
prompt.md). Proje sahibi bu iki parçalı çıktının TEK dosyada birleştirilmesini
istedi (2026-08-03). Bu script o birleştirmeyi kod olarak sabitler; elle
düzenlenmiş CSV'nin tekrar üretilebilir olmasını sağlar.

KAPSAM UYARISI (birleştirilse de kalite tek düzey DEĞİL — bkz. veri_donemi ve
cift_dogrulama sütunları):
  - genisletme_2021_2023: 2021 Ocak-Ağustos'ta gerçek yıllık (12 aylık) rakam
    yok (ENAG'ın o tarihte henüz 12 aylık geçmişi yoktu, bkz.
    pm_rapor_enag_2018_genisletme.md Bölüm 2) -> enag_yillik_degisim boş.
    2021-02 hiç bulunamadı (satır yok, uydurulmadı).
  - ana_2024_2026: yalnızca 5 ay (2024-01, 2024-07, 2025-01, 2025-07, 2026-01)
    bağımsız ikinci arama ile çapraz doğrulandı; kalanı tek kaynaklı
    (cift_dogrulama=hayır) ama B/C seviyesi kaynaklıdır, "bulunamadı" değildir.
  - 2018-2019: ENAG henüz kurulmamıştı (2020'de kuruldu) -> hiç veri yok, bu
    dosyada da yer almaz.
  - 2020: proje sahibi onayıyla hiç aranmadı (2021 trendindeki düşük getiri
    beklentisi nedeniyle) -> bu dosyada yer almaz.

TÜİK TÜFE ile BİRLEŞTİRME YAPILMADI (K1 kararı: TÜFE ana deflatör, ENAG
kontrol serisi, ayrı sütun/dosya kalır).

Çıktı: data/raw/enag/enag_aylik_2021_2026.csv
Kolonlar: referans_ayi, enag_aylik_degisim, enag_yillik_degisim, enag_endeks,
  kaynak_url, kaynak_seviyesi (A-D), cift_dogrulama (evet/hayır),
  veri_donemi (genisletme_2021_2023 / ana_2024_2026 — hangi görevde
  toplandığının izlenebilirliği için).
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
ENAG_RAW_DIR = REPO_KOKU / "data" / "raw" / "enag"

# --- Bölüm 1: genisletme_2021_2023 (2018 genişletme denemesinden, kısmi) ---
# Ocak-Ağustos 2021: enag_yillik_degisim yok (henüz 12 aylık geçmiş yoktu).
# 2021-02: hiç yok (bulunamadı, satır eklenmedi).
GENISLETME_2021_2023 = [
    dict(referans_ayi="2021-01", enag_aylik_degisim=2.99, enag_yillik_degisim=None, kaynak_url="https://tr.euronews.com/2021/02/03/enag-n-ac-klad-g-ocak-ay-enflasyon-rakam-tuik-verilerinden-1-8-kat-daha-fazla", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-03", enag_aylik_degisim=3.36, enag_yillik_degisim=None, kaynak_url="https://turkish.aawsat.com/home/article/2900951", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-04", enag_aylik_degisim=2.62, enag_yillik_degisim=None, kaynak_url="https://www.gazeteduvar.com.tr/enflasyon-yuzde-kac-nisan-2021-haber-1521113", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-05", enag_aylik_degisim=3.94, enag_yillik_degisim=None, kaynak_url="https://t24.com.tr/haber/enag-mayis-ayi-enflasyonunu-aylik-bazda-yuzde-3-94-olarak-acikladi,956627", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-06", enag_aylik_degisim=3.28, enag_yillik_degisim=None, kaynak_url="https://www.halktv.com.tr/gundem/enaga-gore-enflasyon-yuzde-3-28-artti-6-aylik-enflasyon-rakami-bile-tuiki-gecti-463843h", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-07", enag_aylik_degisim=4.89, enag_yillik_degisim=None, kaynak_url="https://www.paraanaliz.com/2021/ekonomi/enag-temmuz-enflasyonu-aylik-yuzde-489-yillik-yuzde-50ye-dayandi-g-10189", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-08", enag_aylik_degisim=4.06, enag_yillik_degisim=None, kaynak_url="https://t24.com.tr/haber/enag-enflasyon-agustosta-aylik-yuzde-4-6-artti,976369", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-09", enag_aylik_degisim=2.89, enag_yillik_degisim=44.70, kaynak_url="https://www.diken.com.tr/enaga-gore-enflasyon-yuzde-1958-degil-yuzde-447", kaynak_seviyesi="C", cift_dogrulama="hayır"),
    dict(referans_ayi="2021-10", enag_aylik_degisim=6.90, enag_yillik_degisim=49.87, kaynak_url="https://www.evrensel.net/haber/enag-ekim-ayi-enflasyonunu-acikladi", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2021-11", enag_aylik_degisim=9.91, enag_yillik_degisim=58.65, kaynak_url="https://www.evrensel.net/haber/449359/enflasyon-kasimda-tuike-gore-yuzde-21-31-enaga-gore-yuzde-58-65-oldu", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2021-12", enag_aylik_degisim=19.35, enag_yillik_degisim=82.81, kaynak_url="https://t24.com.tr/haber/enag-12-aylik-enflasyon-artisi-yuzde-82-81-oldu,1005303", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-01", enag_aylik_degisim=15.52, enag_yillik_degisim=114.87, kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/son-dakika--enag-enflasyon-verilerini-uc-haneli-acikladi-1904832", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-02", enag_aylik_degisim=5.44, enag_yillik_degisim=123.80, kaynak_url="https://medyascope.tv/2022/03/03/enflasyon-verileri-aciklandi-tuike-gore-yillik-enflasyon-yuzde-54-enaga-gore-yuzde-123/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-03", enag_aylik_degisim=11.93, enag_yillik_degisim=142.63, kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/son-dakika-enag-mart-ayi-enflasyon-raporunu-acikladi-1922373", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-04", enag_aylik_degisim=8.68, enag_yillik_degisim=156.86, kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/son-dakika-enag-nisan-ayi-enflasyon-raporunu-acikladi-1932774", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-05", enag_aylik_degisim=5.46, enag_yillik_degisim=160.76, kaynak_url="https://www.evrensel.net/haber/462928/enaga-gore-mayista-12-aylik-enflasyon-yuzde-160-76-oldu", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-06", enag_aylik_degisim=8.31, enag_yillik_degisim=175.55, kaynak_url="https://tr.euronews.com/2022/07/04/turkiyede-haziranda-yillik-enflasyon-tuike-gore-yuzde-7862-enaga-gore-yuzde-17555", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-07", enag_aylik_degisim=5.03, enag_yillik_degisim=176.04, kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/son-dakika-enag-temmuz-ayi-enflasyonunu-acikladi-1964925", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-08", enag_aylik_degisim=5.86, enag_yillik_degisim=181.37, kaynak_url="https://medyascope.tv/2022/09/05/aylik-enflasyon-tuike-gore-yuzde-146-enaga-gore-yuzde-586/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-09", enag_aylik_degisim=5.30, enag_yillik_degisim=186.27, kaynak_url="https://medyascope.tv/2022/10/03/eylul-enflasyonu-tuike-gore-yuzde-83-enaga-gore-yuzde-186/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-10", enag_aylik_degisim=7.18, enag_yillik_degisim=185.34, kaynak_url="https://medyascope.tv/2022/11/03/ekimde-aylik-enflasyon-tuike-gore-yuzde-35-enaga-gore-yuzde-72/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-11", enag_aylik_degisim=4.24, enag_yillik_degisim=170.70, kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/son-dakika-enag-ve-tuik-kasim-ayi-enflasyon-verilerini-acikladi-2009010", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2022-12", enag_aylik_degisim=5.18, enag_yillik_degisim=137.55, kaynak_url="https://www.diken.com.tr/enag-yillik-enflasyon-yuzde-1375/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-01", enag_aylik_degisim=9.26, enag_yillik_degisim=121.62, kaynak_url="https://www.brandingturkiye.com/enag-ocak-2023-enflasyonunu-acikladi/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-02", enag_aylik_degisim=7.21, enag_yillik_degisim=126.91, kaynak_url="https://www.brandingturkiye.com/enag-subat-2023-enflasyonunu-acikladi/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-03", enag_aylik_degisim=5.08, enag_yillik_degisim=112.51, kaynak_url="https://www.brandingturkiye.com/enag-mart-2023-enflasyonunu-acikladi/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-04", enag_aylik_degisim=4.86, enag_yillik_degisim=105.19, kaynak_url="https://tr.euronews.com/2023/05/03/nisan-ayi-enflasyonu-tuik-239-enagrup-486-olarak-acikladi", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-05", enag_aylik_degisim=7.35, enag_yillik_degisim=109.01, kaynak_url="https://www.brandingturkiye.com/enag-mayis-2023-enflasyonunu-acikladi/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-06", enag_aylik_degisim=8.54, enag_yillik_degisim=108.58, kaynak_url="https://www.rudaw.net/turkish/business/030720231", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-07", enag_aylik_degisim=13.18, enag_yillik_degisim=122.88, kaynak_url="https://tr.euronews.com/2023/08/03/enag-temmuz-ayi-enflasyon-oranlarini-acikladi-yillik-yuzde-12288-aylik-1318", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-08", enag_aylik_degisim=8.59, enag_yillik_degisim=128.05, kaynak_url="https://tr.euronews.com/business/2023/09/04/agustos-ayinda-enflasyon-tuike-gore-yuzde-589-enaga-gore-yuzde-128", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-09", enag_aylik_degisim=6.24, enag_yillik_degisim=130.13, kaynak_url="https://www.brandingturkiye.com/enag-eylul-2023-enflasyonunu-acikladi/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-10", enag_aylik_degisim=5.09, enag_yillik_degisim=126.18, kaynak_url="https://twitter.com/ENAGRUP/status/1720323181532057907", kaynak_seviyesi="B", cift_dogrulama="evet"),
    dict(referans_ayi="2023-11", enag_aylik_degisim=5.58, enag_yillik_degisim=129.27, kaynak_url="https://medyascope.tv/2023/12/04/enflasyon-tuike-gore-yuzde-6198-enaga-gore-yuzde-12927/", kaynak_seviyesi="C", cift_dogrulama="evet"),
    dict(referans_ayi="2023-12", enag_aylik_degisim=4.12, enag_yillik_degisim=127.21, kaynak_url="https://www.brandingturkiye.com/enag-aralik-2023-enflasyonunu-acikladi/", kaynak_seviyesi="C", cift_dogrulama="evet"),
]

# --- Bölüm 2: ana_2024_2026 (genisletme_12_enag_cekme.py ile toplanan, aynen) ---
# cift_dogrulama yalnızca bağımsız ikinci aramayla teyit edilen 5 ay için "evet".
CAPRAZ_DOGRULANAN_AYLAR_2024_2026 = {"2024-01", "2024-07", "2025-01", "2025-07", "2026-01"}
ANA_2024_2026 = [
    dict(referans_ayi="2024-01", enag_aylik_degisim=9.38, enag_yillik_degisim=129.11, kaynak_url="https://www.brandingturkiye.com/enag-ocak-2024-enflasyonunu-acikladi/", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-02", enag_aylik_degisim=4.32, enag_yillik_degisim=121.98, kaynak_url="https://www.brandingturkiye.com/enag-subat-2024-enflasyonunu-acikladi/", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-03", enag_aylik_degisim=5.68, enag_yillik_degisim=124.63, kaynak_url="https://www.brandingturkiye.com/enag-mart-2024-enflasyonunu-acikladi/", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-04", enag_aylik_degisim=5.02, enag_yillik_degisim=124.35, kaynak_url="https://www.brandingturkiye.com/enag-nisan-2024-enflasyonunu-acikladi/", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-05", enag_aylik_degisim=5.66, enag_yillik_degisim=120.66, kaynak_url="https://www.brandingturkiye.com/enag-mayis-2024-enflasyonunu-acikladi/", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-06", enag_aylik_degisim=4.27, enag_yillik_degisim=113.08, kaynak_url="https://www.dunya.com/ekonomi/son-dakika-enflasyon-verisi-enag-enflasyon-rakamlarini-acikladi-enag-enflasyon-orani-haziran-2024-haberi-734991", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-07", enag_aylik_degisim=5.91, enag_yillik_degisim=100.88, kaynak_url="https://www.dunya.com/ekonomi/son-dakika-enflasyon-rakamlari-enag-enflasyon-verilerini-duyurdu-enag-enflasyon-orani-temmuz-2024-haberi-739877", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-08", enag_aylik_degisim=3.47, enag_yillik_degisim=90.35, kaynak_url="https://x.com/ENAGRUP/status/1830852128165761448", kaynak_seviyesi="B"),
    dict(referans_ayi="2024-09", enag_aylik_degisim=5.34, enag_yillik_degisim=88.63, kaynak_url="https://www.brandingturkiye.com/enag-eylul-2024-enflasyonunu-acikladi/", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-10", enag_aylik_degisim=5.57, enag_yillik_degisim=89.77, kaynak_url="https://x.com/ENAGRUP/status/1853331678254465533", kaynak_seviyesi="B"),
    dict(referans_ayi="2024-11", enag_aylik_degisim=4.06, enag_yillik_degisim=86.76, kaynak_url="https://tr.euronews.com/2024/12/03/kasim-ayi-enflasyonu-yillik-bazda-4709-olarak-aciklandi", kaynak_seviyesi="C"),
    dict(referans_ayi="2024-12", enag_aylik_degisim=2.34, enag_yillik_degisim=83.40, kaynak_url="https://x.com/ENAGRUP/status/1875063179904237709", kaynak_seviyesi="B"),
    dict(referans_ayi="2025-01", enag_aylik_degisim=8.22, enag_yillik_degisim=81.01, kaynak_url="https://tr.euronews.com/business/2025/02/03/ocak-ayinda-yillik-enflasyon-tuike-gore-yuzde-4212-enaga-gore-8101", kaynak_seviyesi="C"),
    dict(referans_ayi="2025-02", enag_aylik_degisim=3.37, enag_yillik_degisim=79.51, kaynak_url="https://tr.euronews.com/2025/03/03/subat-ayinda-yillik-enflasyon-tuike-gore-yuzde-3905-enaga-gore-7951", kaynak_seviyesi="C"),
    dict(referans_ayi="2025-03", enag_aylik_degisim=3.91, enag_yillik_degisim=75.20, kaynak_url="https://tr.euronews.com/2025/04/03/tuike-gore-mart-ayinda-yillik-enflasyon-yuzde-3810-enaga-gore-7520-kira-artis-orani-5126-o", kaynak_seviyesi="C"),
    dict(referans_ayi="2025-04", enag_aylik_degisim=4.46, enag_yillik_degisim=73.88, kaynak_url="https://x.com/ENAGRUP/status/1919274592599687588", kaynak_seviyesi="B"),
    dict(referans_ayi="2025-05", enag_aylik_degisim=3.66, enag_yillik_degisim=71.23, kaynak_url="https://x.com/ENAGRUP/status/1929783523218530778", kaynak_seviyesi="B"),
    dict(referans_ayi="2025-06", enag_aylik_degisim=3.05, enag_yillik_degisim=68.68, kaynak_url="https://tr.euronews.com/business/2025/07/03/haziranda-yillik-enflasyon-tuik-yuzde-3505-enag-ise-yuzde-6868-acikladi", kaynak_seviyesi="C"),
    dict(referans_ayi="2025-07", enag_aylik_degisim=3.75, enag_yillik_degisim=65.15, kaynak_url="https://tr.euronews.com/2025/08/04/temmuzda-yillik-enflasyon-tuik-yuzde-3352-enag-ise-yuzde-6515-acikladi", kaynak_seviyesi="C"),
    dict(referans_ayi="2025-08", enag_aylik_degisim=3.23, enag_yillik_degisim=65.49, kaynak_url="https://x.com/ENAGRUP/status/1963123701089530034", kaynak_seviyesi="B"),
    dict(referans_ayi="2025-09", enag_aylik_degisim=3.79, enag_yillik_degisim=63.23, kaynak_url="https://tr.euronews.com/business/2025/10/03/eylul-ayinda-yillik-enflasyon-tuik-yuzde-3329-enag-ise-yuzde-6323-acikladi", kaynak_seviyesi="C"),
    dict(referans_ayi="2025-10", enag_aylik_degisim=3.74, enag_yillik_degisim=60.00, kaynak_url="https://x.com/ENAGRUP/status/1985229202124427767", kaynak_seviyesi="B"),
    dict(referans_ayi="2025-11", enag_aylik_degisim=2.13, enag_yillik_degisim=56.82, kaynak_url="https://x.com/ENAGRUP/status/1996101595629846658", kaynak_seviyesi="B"),
    dict(referans_ayi="2025-12", enag_aylik_degisim=2.11, enag_yillik_degisim=56.14, kaynak_url="https://x.com/ENAGRUP/status/2008059692640063583", kaynak_seviyesi="B"),
    dict(referans_ayi="2026-01", enag_aylik_degisim=6.32, enag_yillik_degisim=53.42, kaynak_url="https://tr.euronews.com/2026/02/03/ocakta-yillik-enflasyon-tuik-yuzde-3065-enag-ise-yuzde-5342-acikladi", kaynak_seviyesi="C"),
    dict(referans_ayi="2026-02", enag_aylik_degisim=4.01, enag_yillik_degisim=54.14, kaynak_url="https://tr.euronews.com/2026/03/03/subatta-yillik-enflasyon-tuik-yuzde-3153-enag-ise-yuzde-5414-acikladi", kaynak_seviyesi="C"),
    dict(referans_ayi="2026-03", enag_aylik_degisim=4.10, enag_yillik_degisim=54.62, kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/enag-mart-ayi-enflasyon-verilerini-acikladi-2491771", kaynak_seviyesi="C"),
    dict(referans_ayi="2026-04", enag_aylik_degisim=5.07, enag_yillik_degisim=55.38, kaynak_url="https://www.ensonolay.com.tr/ekonomi/enag-nisan-2026-enflasyon-rakamlarini-acikladi-aylik-enflasyon-orani-yuzde-kac/47108", kaynak_seviyesi="C"),
    dict(referans_ayi="2026-05", enag_aylik_degisim=2.16, enag_yillik_degisim=53.13, kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/enag-mayis-ayi-enflasyon-verilerini-acikladi-2508647", kaynak_seviyesi="C"),
    dict(referans_ayi="2026-06", enag_aylik_degisim=1.94, enag_yillik_degisim=51.49, kaynak_url="https://www.24saatgazetesi.com/enag-haziran-2026-enflasyon-verilerini-acikladi-yillik-artis-yuzde-5149", kaynak_seviyesi="C"),
]


def main():
    ENAG_RAW_DIR.mkdir(parents=True, exist_ok=True)

    genisletme = pd.DataFrame(GENISLETME_2021_2023)
    genisletme["veri_donemi"] = "genisletme_2021_2023"

    ana = pd.DataFrame(ANA_2024_2026)
    ana["cift_dogrulama"] = ana["referans_ayi"].apply(
        lambda ay: "evet" if ay in CAPRAZ_DOGRULANAN_AYLAR_2024_2026 else "hayır"
    )
    ana["veri_donemi"] = "ana_2024_2026"

    birlesik = pd.concat([genisletme, ana], ignore_index=True).sort_values("referans_ayi")
    birlesik["enag_endeks"] = None
    birlesik = birlesik[[
        "referans_ayi", "enag_aylik_degisim", "enag_yillik_degisim", "enag_endeks",
        "kaynak_url", "kaynak_seviyesi", "cift_dogrulama", "veri_donemi",
    ]].reset_index(drop=True)

    assert birlesik["referans_ayi"].is_unique, "Tekrar eden ay bulundu"

    cikti_csv = ENAG_RAW_DIR / "enag_aylik_2021_2026.csv"
    birlesik.to_csv(cikti_csv, index=False, encoding="utf-8-sig")

    print("=== GENISLETME 20 - ENAG TEK/KAPSAMLI SERI OZETI ===\n")
    print(f"Kapsanan donem: {birlesik['referans_ayi'].min()} -> {birlesik['referans_ayi'].max()}")
    print(f"Toplam ay: {len(birlesik)} (35 genisletme_2021_2023 + 30 ana_2024_2026)")
    print(f"veri_donemi dagilimi:\n{birlesik['veri_donemi'].value_counts()}")
    print(f"kaynak_seviyesi dagilimi:\n{birlesik['kaynak_seviyesi'].value_counts()}")
    print(f"cift_dogrulama dagilimi:\n{birlesik['cift_dogrulama'].value_counts()}")
    print(f"\nCikti: {cikti_csv}")


if __name__ == "__main__":
    main()
