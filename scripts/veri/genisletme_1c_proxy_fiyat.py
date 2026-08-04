"""
GENIŞLETME AŞAMA 1c — Proxy fiyat serisi, 2024-01 -> 2026-06 (kaynak seviyesi C).

MVP scriptinden (asama3_proxy_fiyat.py, yalnizca 2025) FARKLI ciktilara yazar;
2025 KAYITLARI BURADA TEKRAR KULLANILMIŞTIR (ayni degerler, tek kaynaktan
yonetim icin). MVP ciktilarinin uzerine YAZILMAZ.

Kapsam sinirlamasi: BETAM'in en guncel raporu "Temmuz 2026" (yayimlandigi ay);
bu rapor bir onceki ayin (Haziran 2026) verisini icerir. Bu yuzden proxy fiyat
serisi 2026-06'da BITER - "bugune kadar" (2026-07) degil, cunku kaynagin kendi
1-aylik yayim gecikmesi bunu yapisal olarak engeller (Temmuz 2026 verisi ancak
"Agustos 2026" raporuyla gelir, o rapor henuz yayimlanmamis).

IKI GERCEK BOSLUK (BETAM hic rapor yayimlamamis, dogrulanmis, uydurulmadi):
- 2024-05 (Mayis 2024): "Haziran 2024" basligiyla rapor YOK (Mayis->Temmuz
  atlanmis). arabam.com'dan referans deger alindi (913.190 TL).
- 2025-02 (Subat 2025): "Mart 2025" basligiyla rapor YOK (Subat->Nisan
  atlanmis). arabam.com'dan referans deger alindi (888.689 TL, MVP asamasinda
  da kullanilmisti).
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "proxy_fiyat"

# Her kayit WebFetch ile ilgili BETAM/arabam.com sayfasindan CEKILEN ve
# dogrulanan degerlerdir. "kaynak_alinti" = sayfadaki birebir cumle.
KAYITLAR = [
    # --- 2024 ---
    dict(referans_ayi="2024-01", proxy_fiyat_cari_tl=860443, proxy_reel_aylik_pct=-6.0,
         proxy_nominal_yillik_pct=50.9, proxy_talep_aylik_pct=5.6, proxy_satis_orani_pct=17.7,
         proxy_dom_gun=25.1, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Şubat 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/03/sahibindex-otomobil-piyasasi-gorunumu-subat-2024/",
         yayim_ayi="2024-03",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın ocak ayına göre "
                        "yüzde 50,9 artmış, aralığa kıyasla ise değişmemiştir."),
    dict(referans_ayi="2024-02", proxy_fiyat_cari_tl=855781, proxy_reel_aylik_pct=-5.0,
         proxy_nominal_yillik_pct=39.3, proxy_talep_aylik_pct=4.0, proxy_satis_orani_pct=19.0,
         proxy_dom_gun=23.3, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Mart 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/03/sahibindex-otomobil-piyasasi-gorunumu-mart-2024/",
         yayim_ayi="2024-03",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın şubat ayına göre "
                        "yüzde 39,3 artmıştır. Şubat ayında ortalama otomobil fiyatı 855 bin "
                        "781 TL olmuştur."),
    dict(referans_ayi="2024-03", proxy_fiyat_cari_tl=859035, proxy_reel_aylik_pct=-2.7,
         proxy_nominal_yillik_pct=31.8, proxy_talep_aylik_pct=3.9, proxy_satis_orani_pct=19.0,
         proxy_dom_gun=22.5, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Nisan 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/05/sahibindex-otomobil-piyasasi-gorunumu-nisan-2024/",
         yayim_ayi="2024-05",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın mart ayına göre "
                        "yüzde 31,8 artmıştır. Mart ayında ortalama otomobil fiyatı 859 bin "
                        "35 TL olmuştur."),
    dict(referans_ayi="2024-04", proxy_fiyat_cari_tl=867813, proxy_reel_aylik_pct=-2.1,
         proxy_nominal_yillik_pct=23.3, proxy_talep_aylik_pct=-12.0, proxy_satis_orani_pct=17.1,
         proxy_dom_gun=24.5, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Mayıs 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/05/sahibindex-otomobil-piyasasi-gorunumu-mayis-2024/",
         yayim_ayi="2024-05",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın nisan ayına göre "
                        "yüzde 23,3 artmıştır."),
    dict(referans_ayi="2024-05", proxy_fiyat_cari_tl=None, proxy_reel_aylik_pct=-1.56,
         proxy_nominal_yillik_pct=None, proxy_talep_aylik_pct=None, proxy_satis_orani_pct=None,
         proxy_dom_gun=None,
         kaynak="arabam.com (ALTERNATİF - BETAM bu ay için rapor yayımlamadı)",
         kaynak_rapor_basligi="arabam.com mayıs ayı ikinci el ilan verilerini paylaştı",
         kaynak_url="https://www.aa.com.tr/tr/isdunyasi/otomotiv/arabamcom-mayis-ayi-ikinci-el-ilan-verilerini-paylasti/702807",
         yayim_ayi="2024-06 (tahmini)",
         kaynak_alinti="nisan ayında 912 bin 45 lira olan ilan fiyatları mayıs ayında ortalama "
                        "913 bin 190 lira oldu. Enflasyondan arındırılmış reel fiyatlar bir "
                        "önceki aya göre yüzde 1,56 düşüş gösterdi.",
         proxy_fiyat_arabamcom_referans_tl=913190),
    dict(referans_ayi="2024-06", proxy_fiyat_cari_tl=871156, proxy_reel_aylik_pct=-2.2,
         proxy_nominal_yillik_pct=0.6, proxy_talep_aylik_pct=-13.8, proxy_satis_orani_pct=14.9,
         proxy_dom_gun=23.7, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Temmuz 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/07/sahibindex-otomobil-piyasasi-gorunumu-temmuz-2024/",
         yayim_ayi="2024-07",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın haziran ayına göre "
                        "yüzde 0,6 artmıştır."),
    dict(referans_ayi="2024-07", proxy_fiyat_cari_tl=862232, proxy_reel_aylik_pct=-4.1,
         proxy_nominal_yillik_pct=-4.6, proxy_talep_aylik_pct=30.9, proxy_satis_orani_pct=19.5,
         proxy_dom_gun=25.6, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Ağustos 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/08/sahibindex-otomobil-piyasasi-gorunumu-agustos-2024/",
         yayim_ayi="2024-08",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın temmuz ayına göre "
                        "yüzde 4,6 azalmıştır. Temmuz ayında ortalama otomobil fiyatı 862 bin "
                        "232 TL olmuştur."),
    dict(referans_ayi="2024-08", proxy_fiyat_cari_tl=865433, proxy_reel_aylik_pct=-2.1,
         proxy_nominal_yillik_pct=-4.2, proxy_talep_aylik_pct=5.9, proxy_satis_orani_pct=20.3,
         proxy_dom_gun=23.0, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Eylül 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/09/sahibindex-otomobil-piyasasi-gorunumu-eylul-2024/",
         yayim_ayi="2024-09",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın ağustos ayına göre "
                        "yüzde 4,2 azalmıştır. Ağustosta ortalama otomobil fiyatı 865 bin "
                        "433 TL olmuştur."),
    dict(referans_ayi="2024-09", proxy_fiyat_cari_tl=880318, proxy_reel_aylik_pct=-1.2,
         proxy_nominal_yillik_pct=-3.8, proxy_talep_aylik_pct=-0.4, proxy_satis_orani_pct=21.1,
         proxy_dom_gun=22.0, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Ekim 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/10/sahibindex-otomobil-piyasasi-gorunumu-ekim-2024/",
         yayim_ayi="2024-10",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın eylül ayına göre "
                        "yüzde 3,8 azalmıştır. Eylülde ortalama otomobil fiyatı 880 bin "
                        "318 TL olmuştur."),
    dict(referans_ayi="2024-10", proxy_fiyat_cari_tl=888907, proxy_reel_aylik_pct=-1.9,
         proxy_nominal_yillik_pct=-1.4, proxy_talep_aylik_pct=1.7, proxy_satis_orani_pct=22.0,
         proxy_dom_gun=20.2, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Kasım 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/11/sahibindex-otomobil-piyasasi-gorunumu-kasim-2024/",
         yayim_ayi="2024-11",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın ekim ayına göre "
                        "yüzde 1,4 azalmıştır. Ekimde ortalama otomobil fiyatı 888 bin "
                        "907 TL olmuştur."),
    dict(referans_ayi="2024-11", proxy_fiyat_cari_tl=899940, proxy_reel_aylik_pct=-1.0,
         proxy_nominal_yillik_pct=1.2, proxy_talep_aylik_pct=-6.3, proxy_satis_orani_pct=21.3,
         proxy_dom_gun=19.9, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Aralık 2024",
         kaynak_url="https://betam.bahcesehir.edu.tr/2024/12/sahibindex-otomobil-piyasasi-gorunumu-aralik-2024/",
         yayim_ayi="2024-12",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın kasım ayına göre "
                        "yüzde 1,2 artmıştır. Kasımda ortalama otomobil fiyatı 899 bin "
                        "940 TL olmuştur."),
    dict(referans_ayi="2024-12", proxy_fiyat_cari_tl=908588, proxy_reel_aylik_pct=-0.1,
         proxy_nominal_yillik_pct=5.6, proxy_talep_aylik_pct=-1.7, proxy_satis_orani_pct=21.7,
         proxy_dom_gun=20.2, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Ocak 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/01/sahibindex-otomobil-piyasasi-gorunumu-ocak-2025/",
         yayim_ayi="2025-01",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın aralık ayına göre "
                        "yüzde 5,6 artmıştır. Aralıkta ortalama otomobil fiyatı 908 bin "
                        "588 TL olmuştur."),
    # --- 2025 (MVP asamasindan aynen tasindi - ayni kaynak/deger) ---
    dict(referans_ayi="2025-01", proxy_fiyat_cari_tl=935136, proxy_reel_aylik_pct=-2.0,
         proxy_nominal_yillik_pct=8.7, proxy_talep_aylik_pct=0.0, proxy_satis_orani_pct=20.3,
         proxy_dom_gun=21.1, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Şubat 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/02/sahibindex-otomobil-piyasasi-gorunumu-subat-2025/",
         yayim_ayi="2025-02", kaynak_alinti="Ocakta ortalama otomobil fiyatı 935 bin 136 TL olmuştur."),
    dict(referans_ayi="2025-02", proxy_fiyat_cari_tl=None, proxy_reel_aylik_pct=-1.58,
         proxy_nominal_yillik_pct=None, proxy_talep_aylik_pct=None, proxy_satis_orani_pct=None,
         proxy_dom_gun=None,
         kaynak="arabam.com (ALTERNATİF - BETAM bu ay için rapor yayımlamadı)",
         kaynak_rapor_basligi="İkinci El Otomobilde Neler Oluyor? Şubat Verileri Açıklandı",
         kaynak_url="https://www.arabam.com/blog/genel/ikinci-el-otomobilde-neler-oluyor-subat-verileri-aciklandi/",
         yayim_ayi="2025-02",
         kaynak_alinti="ocak ayında 877.029 TL olan ilan fiyatları şubat ayında ortalama "
                        "888.689 TL oldu.", proxy_fiyat_arabamcom_referans_tl=888689),
    dict(referans_ayi="2025-03", proxy_fiyat_cari_tl=950515, proxy_reel_aylik_pct=-2.1,
         proxy_nominal_yillik_pct=10.6, proxy_talep_aylik_pct=11.8, proxy_satis_orani_pct=21.3,
         proxy_dom_gun=21.3, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Nisan 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/04/sahibindex-otomobil-piyasasi-gorunumu-nisan-2025/",
         yayim_ayi="2025-04", kaynak_alinti="Mart'ta ortalama otomobil fiyatı 950 bin 515 TL olmuştur."),
    dict(referans_ayi="2025-04", proxy_fiyat_cari_tl=947790, proxy_reel_aylik_pct=-3.2,
         proxy_nominal_yillik_pct=9.2, proxy_talep_aylik_pct=12.4, proxy_satis_orani_pct=22.4,
         proxy_dom_gun=23.0, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Mayıs 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/05/sahibindex-otomobil-piyasasi-gorunumu-mayis-2025/",
         yayim_ayi="2025-05", kaynak_alinti="nisanda ortalama otomobil fiyatı 947 bin 790 TL olmuştur."),
    dict(referans_ayi="2025-05", proxy_fiyat_cari_tl=962726, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=9.9, proxy_talep_aylik_pct=-2.2, proxy_satis_orani_pct=21.7,
         proxy_dom_gun=20.8, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Haziran 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/06/sahibindex-otomobil-piyasasi-gorunumu-haziran-2025/",
         yayim_ayi="2025-06", kaynak_alinti="mayısta ortalama otomobil fiyatı 962 bin 726 TL olmuştur."),
    dict(referans_ayi="2025-06", proxy_fiyat_cari_tl=968926, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=11.2, proxy_talep_aylik_pct=-11.3, proxy_satis_orani_pct=21.4,
         proxy_dom_gun=22.4, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Temmuz 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/07/sahibindex-otomobil-piyasasi-gorunumu-temmuz-2025/",
         yayim_ayi="2025-07", kaynak_alinti="haziranda ortalama otomobil fiyatı 968 bin 926 TL olmuştur."),
    dict(referans_ayi="2025-07", proxy_fiyat_cari_tl=990751, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=14.9, proxy_talep_aylik_pct=19.1, proxy_satis_orani_pct=25.5,
         proxy_dom_gun=22.9, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Ağustos 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/08/sahibindex-otomobil-piyasasi-gorunumu-agustos-2025/",
         yayim_ayi="2025-08", kaynak_alinti="temmuzda ortalama otomobil fiyatı 990 bin 751 TL olmuştur."),
    dict(referans_ayi="2025-08", proxy_fiyat_cari_tl=1022000, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=18.2, proxy_talep_aylik_pct=0.7, proxy_satis_orani_pct=24.9,
         proxy_dom_gun=19.8, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Eylül 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/09/sahibindex-otomobil-piyasasi-gorunumu-eylul-2025/",
         yayim_ayi="2025-09", kaynak_alinti="ortalama otomobil fiyatı 1 milyon 22 bin TL olmuştur."),
    dict(referans_ayi="2025-09", proxy_fiyat_cari_tl=1058000, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=20.3, proxy_talep_aylik_pct=-7.2, proxy_satis_orani_pct=24.0,
         proxy_dom_gun=19.1, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Ekim 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/10/sahibindex-otomobil-piyasasi-gorunumu-ekim-2025/",
         yayim_ayi="2025-10", kaynak_alinti="ortalama otomobil fiyatı 1 milyon 58 bin TL olmuştur."),
    dict(referans_ayi="2025-10", proxy_fiyat_cari_tl=1086000, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=22.2, proxy_talep_aylik_pct=-2.9, proxy_satis_orani_pct=23.0,
         proxy_dom_gun=20.0, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Kasım 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/11/sahibindex-otomobil-piyasasi-gorunumu-kasim-2025/",
         yayim_ayi="2025-11", kaynak_alinti="ortalama otomobil fiyatı 1 milyon 86 bin TL olmuştur."),
    dict(referans_ayi="2025-11", proxy_fiyat_cari_tl=1101000, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=22.4, proxy_talep_aylik_pct=-7.1, proxy_satis_orani_pct=21.2,
         proxy_dom_gun=20.7, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Aralık 2025",
         kaynak_url="https://betam.bahcesehir.edu.tr/2025/12/sahibindex-otomobil-piyasasi-gorunumu-aralik-2025/",
         yayim_ayi="2025-12", kaynak_alinti="ortalama otomobil fiyatı 1 milyon 101 bin TL olmuştur."),
    dict(referans_ayi="2025-12", proxy_fiyat_cari_tl=1108000, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=22.0, proxy_talep_aylik_pct=10.0, proxy_satis_orani_pct=25.2,
         proxy_dom_gun=21.6, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Ocak 2026",
         kaynak_url="https://betam.bahcesehir.edu.tr/2026/01/sahibindex-otomobil-piyasasi-gorunumu-ocak-2026/",
         yayim_ayi="2026-01", kaynak_alinti="ortalama otomobil fiyatı 1 milyon 108 bin TL olmuştur."),
    # --- 2026 ---
    dict(referans_ayi="2026-01", proxy_fiyat_cari_tl=1149000, proxy_reel_aylik_pct=-5.9,
         proxy_nominal_yillik_pct=22.9, proxy_talep_aylik_pct=-4.5, proxy_satis_orani_pct=22.3,
         proxy_dom_gun=22.9, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Şubat 2026",
         kaynak_url="https://betam.bahcesehir.edu.tr/2026/02/sahibindex-otomobil-piyasasi-gorunumu-subat-2026-2/",
         yayim_ayi="2026-02",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın ocak ayına kıyasla "
                        "yüzde 22,9 artmış ve ortalama otomobil fiyatı 1 milyon 149 bin TL "
                        "olmuştur."),
    dict(referans_ayi="2026-02", proxy_fiyat_cari_tl=1159000, proxy_reel_aylik_pct=-6.9,
         proxy_nominal_yillik_pct=22.5, proxy_talep_aylik_pct=-8.1, proxy_satis_orani_pct=21.3,
         proxy_dom_gun=21.3, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Mart 2026",
         kaynak_url="https://betam.bahcesehir.edu.tr/2026/03/sahibindex-otomobil-piyasasi-gorunumu-mart-2026/",
         yayim_ayi="2026-03",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı geçen yılın şubat ayına kıyasla "
                        "yüzde 22,5 artmış ve ortalama otomobil fiyatı 1 milyon 159 bin TL "
                        "olmuştur."),
    dict(referans_ayi="2026-03", proxy_fiyat_cari_tl=1160000, proxy_reel_aylik_pct=-6.7,
         proxy_nominal_yillik_pct=22.0, proxy_talep_aylik_pct=7.1, proxy_satis_orani_pct=20.9,
         proxy_dom_gun=22.0, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Nisan 2026",
         kaynak_url="https://betam.bahcesehir.edu.tr/2026/04/sahibindex-otomobil-piyasasi-gorunumu-nisan-2026/",
         yayim_ayi="2026-04",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatı mart ayında önceki aya kıyasla "
                        "sabit kalırken geçen yılın mart ayına kıyasla yüzde 22 artmış ve "
                        "ortalama otomobil fiyatı 1 milyon 160 bin TL olmuştur."),
    dict(referans_ayi="2026-04", proxy_fiyat_cari_tl=1168000, proxy_reel_aylik_pct=-6.8,
         proxy_nominal_yillik_pct=23.3, proxy_talep_aylik_pct=-6.4, proxy_satis_orani_pct=20.5,
         proxy_dom_gun=22.2, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Mayıs 2026",
         kaynak_url="https://betam.bahcesehir.edu.tr/2026/05/sahibindex-otomobil-piyasasi-gorunumu-mayis-2026/",
         yayim_ayi="2026-05",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatındaki değişim bir önceki aya "
                        "kıyasla yüzde 0,8, bir önceki yılın aynı ayına kıyasla ise yüzde "
                        "23,3'tür. [nisan 2026 verisi]"),
    dict(referans_ayi="2026-05", proxy_fiyat_cari_tl=1175000, proxy_reel_aylik_pct=None,
         proxy_nominal_yillik_pct=22.1, proxy_talep_aylik_pct=-2.8, proxy_satis_orani_pct=19.4,
         proxy_dom_gun=23.8, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Haziran 2026",
         kaynak_url="https://betam.bahcesehir.edu.tr/2026/06/sahibindex-otomobil-piyasasi-gorunumu-haziran-2026/",
         yayim_ayi="2026-06",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatındaki değişim bir önceki aya "
                        "kıyasla yüzde 0,6, bir önceki yılın aynı ayına kıyasla ise yüzde "
                        "22,1'dir. [mayıs 2026 verisi]"),
    dict(referans_ayi="2026-06", proxy_fiyat_cari_tl=1169000, proxy_reel_aylik_pct=-8.6,
         proxy_nominal_yillik_pct=20.7, proxy_talep_aylik_pct=2.8, proxy_satis_orani_pct=19.5,
         proxy_dom_gun=25.2, kaynak="BETAM sahibindex", kaynak_rapor_basligi="Temmuz 2026",
         kaynak_url="https://betam.bahcesehir.edu.tr/2026/07/sahibindex-otomobil-piyasasi-gorunumu-temmuz-2026/",
         yayim_ayi="2026-07",
         kaynak_alinti="Ortalama satılık otomobil cari fiyatındaki değişim bir önceki aya "
                        "kıyasla yüzde -0,5, bir önceki yılın aynı ayına kıyasla ise yüzde "
                        "20,7'dir. [haziran 2026 verisi]"),
]


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(KAYITLAR)
    if "proxy_fiyat_arabamcom_referans_tl" not in df.columns:
        df["proxy_fiyat_arabamcom_referans_tl"] = None
    # NOT (2026-08-04): "proxy_ilan_sayisi" sutunu KALDIRILDI - hicbir ay
    # icin mutlak ilan sayisi hic yayimlanmadi, sutun bastan sona bostu
    # (0/30 dolu). Proje sahibinin talebiyle tamamen silindi.
    df = df.sort_values("referans_ayi").reset_index(drop=True)

    ham_csv = RAW_DIR / "proxy_fiyat_2024_bugun_raw.csv"
    ham_xlsx = RAW_DIR / "proxy_fiyat_2024_bugun_raw.xlsx"
    df.to_csv(ham_csv, index=False, encoding="utf-8-sig")
    df.to_excel(ham_xlsx, index=False, sheet_name="proxy_fiyat_raw")

    beklenen_aylar = pd.period_range("2024-01", "2026-06", freq="M").astype(str).tolist()
    gelen_aylar = df["referans_ayi"].tolist()
    eksik_aylar = [ay for ay in beklenen_aylar if ay not in gelen_aylar]
    betam_eksik = df[df["proxy_fiyat_cari_tl"].isna()]["referans_ayi"].tolist()

    print("=== GENISLETME 1c - PROXY FIYAT SERISI OZET ===")
    print("Kaynak seviyesi: C (BETAM sahibindex, 28 ay) + D/alternatif (arabam.com, 2 ay: 2024-05, 2025-02)")
    print("Kapsam: 2024-01 .. 2026-06 (BETAM'in kendi 1-aylik yayim gecikmesi nedeniyle 2026-07 HENUZ YOK)")
    print(f"Toplam satir: {len(df)} / beklenen {len(beklenen_aylar)}")
    print(f"Tamamen eksik ay: {eksik_aylar if eksik_aylar else 'yok'}")
    print(f"BETAM cari fiyati eksik (arabam.com'a dusulen) aylar: {betam_eksik}")
    print()
    print(df[["referans_ayi", "proxy_fiyat_cari_tl", "proxy_fiyat_arabamcom_referans_tl", "kaynak_rapor_basligi"]].to_string(index=False))
    print()
    print(f"Cikti: {ham_csv} , {ham_xlsx}")


if __name__ == "__main__":
    main()
