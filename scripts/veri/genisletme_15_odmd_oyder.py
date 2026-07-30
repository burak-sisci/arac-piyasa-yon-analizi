"""
GENIŞLETME AŞAMA 15 — ODMD/OYDER/Indicata "İkinci El Online Sektör Raporu"
derinlemesine tarama, 2021-2023 kapsam netleştirmesi.

NEDEN: Önceki bir taramada bu kaynağın 2021-2023 için yalnızca YILDA BİR
(Aralık) yayımlandığı sanılmıştı. Bu turda OYDER'in arşivinde 2024 için
aylık bültenler bulunması üzerine, kaynağın gerçek kapsamı yeniden
araştırıldı.

BULGU (ÖZET, ayrıntı için pm_rapor_odmd_oyder.md): Asıl aylık kaynak
OYDER değil, INDICATA'nın kendi sitesidir (indicata.com.tr,
"haberler-ve-medya" bölümü) — ODMD'nin resmi listesi
(neuralnetwork.aspx?type=90) yalnızca bu raporun YIL-SONU (Aralık) özet
sürümünü yayımlıyor, INDICATA'nın kendi sitesi ise (arşiv verisine göre)
AYLIK yayımlıyordu. SORUN: indicata.com.tr yakın zamanda yeniden
yapılandırılmış - eski makale/PDF URL'leri artık 404 veriyor (canlı
erişilemiyor), Wayback Machine bu oturumda erişime kapalıydı. Bu yüzden
kapsam kanıtı İKİ TÜRDE: (a) WebSearch'ün önbelleğe alınmış özetinden
çıkarılan GERÇEK rakamlar (birkaç ay için), (b) eski makale ID sırasının
(74=Şub2021, 87=Ara2021, 99=Eyl2022, 103=Ara2022, 115=Eki2023...) aylık
yayın deseninin var olduğuna işaret eden DOLAYLI kanıt (içerik yok, yalnızca
mevcudiyet).

KULLANICI KARARI: Bu tur "mevcut kanıtla devam et" seçeneğiyle sonlandırıldı
- 36 ayın (2021-2023) tamamı tek tek taranmadı (bkz. rapor Bölüm 5). Bu bir
NİHAİ/TAM tarama değil, temsili bir örneklemdir.

Çıktı:
  - data/raw/odmd_oyder/odmd_oyder_bultenler_ham.csv
  - data/processed/analiz/odmd_oyder_kapsam_ozeti.csv
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "odmd_oyder"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"

AY_ADLARI = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
             "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

BULUNAMADI = dict(ilan_sayisi=None, satis_adedi=None, fiyat_degisim_pct=None,
                   segment_dagilimi=None, yas_grubu_dagilimi=None, yakit_tipi_dagilimi=None,
                   kaynak_url=None, kaynak_turu=None,
                   bulunabilirlik_durumu="bulunamadı", not_="Bu turda WebSearch ile arandı, sonuç çıkmadı.")

# Her yıl-ay için varsayılan "bulunamadı" ile başlat, sonra bulunanları üzerine yaz.
KAYITLAR = {}
for yil in (2021, 2022, 2023):
    for ay_no in range(1, 13):
        ref = f"{yil}-{ay_no:02d}"
        KAYITLAR[ref] = dict(referans_ayi=ref, **BULUNAMADI)

# --- 2021 ---
KAYITLAR["2021-02"].update(
    bulunabilirlik_durumu="mevcudiyet_dogrulandi_icerik_yok",
    kaynak_url="https://www.indicata.com.tr/hakkimizda/haberler-ve-medya/74-subat-2021-turkiye-otomotiv-2-el-online-pazar-trend-raporu",
    kaynak_turu="indicata_dogrudan (canli erisilemiyor - 404, yalnizca WebSearch indeksinde basligi/varligi tespit edildi)",
    not_="Icerik cikarilamadi (sayfa canli erisimde 404 veriyor).",
)
KAYITLAR["2021-12"].update(
    bulunabilirlik_durumu="mevcudiyet_dogrulandi_icerik_yok",
    kaynak_url="https://www.indicata.com.tr/hakkimizda/haberler-ve-medya/87-aralik-2021-turkiye-otomotiv-2-el-online-pazar-trend-raporu",
    kaynak_turu="indicata_dogrudan (canli erisilemiyor - 404, yalnizca WebSearch indeksinde basligi/varligi tespit edildi)",
    not_="Icerik cikarilamadi (sayfa canli erisimde 404 veriyor).",
)

# --- 2022 ---
KAYITLAR["2022-07"].update(
    bulunabilirlik_durumu="mevcudiyet_dogrulandi_icerik_yok",
    kaynak_url="https://www.indicata.com.tr/download/Temmuz2022_Turkiye_Otomotiv_2el_Online_Pazar_Analiz_Raporu.pdf",
    kaynak_turu="indicata_dogrudan_pdf (canli erisilemiyor - 404, yalnizca WebSearch indeksinde basligi/URL'i tespit edildi)",
    not_="PDF linki bulundu ama indirilemedi (404).",
)
KAYITLAR["2022-09"].update(
    ilan_sayisi=342067,
    bulunabilirlik_durumu="bulundu_arama_ozetinden",
    kaynak_url="https://www.indicata.com.tr/hakkimizda/haberler-ve-medya/99-eylul-2022-turkiye-otomotiv-2-el-online-pazar-analiz-raporu",
    kaynak_turu="indicata_dogrudan (WebSearch'un onbellege alinmis ozetinden - sayfanin kendisi canli erisilemiyor)",
    not_="Yalnizca ilan sayisi cikarilabildi; satis adedi/fiyat/segment ozet metninde yoktu.",
)
KAYITLAR["2022-12"].update(
    ilan_sayisi=348056, satis_adedi=215466,
    bulunabilirlik_durumu="bulundu_arama_ozetinden",
    kaynak_url="https://www.indicata.com.tr/hakkimizda/haberler-ve-medya/103-aralik-2022-turkiye-otomotiv-2-el-online-pazar-analiz-raporu",
    kaynak_turu="indicata_dogrudan (WebSearch'un onbellege alinmis ozetinden - sayfanin kendisi canli erisilemiyor)",
    not_="Ilan sayisi ve satis adedi cikarildi; fiyat/segment/yas ozet metninde yoktu.",
)

# --- 2023 ---
KAYITLAR["2023-06"].update(
    ilan_sayisi=298004, satis_adedi=180748,
    segment_dagilimi="binek: 148.868 satis; hafif ticari: 31.880 satis",
    bulunabilirlik_durumu="bulundu_dogrulanmis",
    kaynak_url="https://tr.linkedin.com/pulse/indicata-t%C3%BCrkiye-haziran-ay%C4%B1-2-el-online-pazar-analiz-raporu",
    kaynak_turu="haber_aktarimi (LinkedIn, dogrudan WebFetch ile ICERIGI OKUNDU - 14 Temmuz 2023 yayimli)",
    not_="YoY: ilan sayisi -%15, satis -%3. Ocak-Haziran 2023 kumulatif satis +%9 YoY. Fiyat degisimi %, yas/yakit dagilimi bu kaynakta YOK.",
)
KAYITLAR["2023-08"].update(
    ilan_sayisi=360445, satis_adedi=125935,
    bulunabilirlik_durumu="bulundu_arama_ozetinden",
    kaynak_url=None,
    kaynak_turu="belirsiz_ikincil_kaynak (WebSearch ozet metninde acik URL verilmedi - kaynak_url bilinmiyor, UYDURULMADI)",
    not_="Satis oraninin %35 oldugu da belirtildi (125.935/360.445). Kaynak URL'i arama sonucunda acikca gorunmedigi icin bos birakildi.",
)
KAYITLAR["2023-10"].update(
    bulunabilirlik_durumu="mevcudiyet_dogrulandi_icerik_yok",
    kaynak_url="https://www.indicata.com.tr/hakkimizda/haberler-ve-medya/115-ekim-2023-turkiye-otomotiv-2-el-online-pazar-analiz-raporu",
    kaynak_turu="indicata_dogrudan (canli erisilemiyor - 404, yalnizca WebSearch indeksinde basligi/varligi tespit edildi)",
    not_="Icerik cikarilamadi.",
)

# --- Yillik ozet satirlari (AYRI, aylik hucrelerle KARISTIRILMAMASI icin referans_ayi = "YYYY-YIL") ---
YILLIK_OZET_SATIRLARI = [
    dict(referans_ayi="2021-YIL", ilan_sayisi=3540937, satis_adedi=1652710, fiyat_degisim_pct=None,
         segment_dagilimi=None, yas_grubu_dagilimi=None, yakit_tipi_dagilimi=None,
         kaynak_url="https://www.aa.com.tr/tr/ekonomi/ikinci-el-online-oto-pazarinda-2022de-1-8-milyon-arac-satildi/2793472",
         kaynak_turu="haber_aktarimi (AA - Anadolu Ajansi, 2022 haberinde 2021 karsilastirma rakami olarak verildi)",
         bulunabilirlik_durumu="bulundu_dogrulanmis (YILLIK TOPLAM, aylik degil)",
         not_="2020 ilan sayisi da ayni haberde gecti: 3.370.369 (yalnizca ilan, satis verilmedi).")
    ,
    dict(referans_ayi="2022-YIL", ilan_sayisi=3949259, satis_adedi=1811498, fiyat_degisim_pct=None,
         segment_dagilimi=None, yas_grubu_dagilimi=None, yakit_tipi_dagilimi=None,
         kaynak_url="https://www.aa.com.tr/tr/ekonomi/ikinci-el-online-oto-pazarinda-2022de-1-8-milyon-arac-satildi/2793472",
         kaynak_turu="haber_aktarimi (AA - Anadolu Ajansi)",
         bulunabilirlik_durumu="bulundu_dogrulanmis (YILLIK TOPLAM, aylik degil)",
         not_="Satis orani %46 (ilan basina). 2021'e gore satislarda %10 artis.")
    ,
    dict(referans_ayi="2023-OCAK_EKIM_KUMULATIF", ilan_sayisi=None, satis_adedi=None, fiyat_degisim_pct=None,
         segment_dagilimi=None, yas_grubu_dagilimi=None, yakit_tipi_dagilimi=None, kaynak_url=None,
         kaynak_turu="belirsiz_ikincil_kaynak (WebSearch ozet metninde acik URL verilmedi)",
         bulunabilirlik_durumu="bulundu_arama_ozetinden (KUMULATIF DONEM, tek ay degil)",
         not_="Ocak-Ekim 2023 donemi: ilan sayisi onceki yila gore +%6, satis +%10 (mutlak rakam verilmedi, yalnizca % degisim).")
    ,
]


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)

    aylik_satirlar = list(KAYITLAR.values()) + YILLIK_OZET_SATIRLARI
    ham = pd.DataFrame(aylik_satirlar).rename(columns={"not_": "not"})
    ham_csv = RAW_DIR / "odmd_oyder_bultenler_ham.csv"
    ham.to_csv(ham_csv, index=False, encoding="utf-8-sig")

    # --- kapsam ozeti (yalnizca gercek aylik hucreler, YIL/KUMULATIF satirlari haric) ---
    satirlar = []
    for yil in (2021, 2022, 2023):
        alt = ham[ham["referans_ayi"].str.startswith(f"{yil}-") & ~ham["referans_ayi"].str.contains("YIL|KUMULATIF")]
        veri_ile = (alt["bulunabilirlik_durumu"] == "bulundu_arama_ozetinden").sum() + (alt["bulunabilirlik_durumu"] == "bulundu_dogrulanmis").sum()
        sadece_mevcudiyet = (alt["bulunabilirlik_durumu"] == "mevcudiyet_dogrulandi_icerik_yok").sum()
        bulunamadi = (alt["bulunabilirlik_durumu"] == "bulunamadı").sum()
        satirlar.append(dict(
            yil=yil, toplam_ay=12,
            ay_sayisi_gercek_veriyle=int(veri_ile),
            ay_sayisi_yalnizca_mevcudiyet_dogrulandi=int(sadece_mevcudiyet),
            ay_sayisi_bulunamadi=int(bulunamadi),
            yillik_toplam_veri_var_mi="EVET" if yil in (2021, 2022) else "HAYIR (yalnizca Ocak-Ekim kumulatif % degisim var)",
            not_="Bu tur 36 ayin TAMAMINI tek tek taramadi (kullanici karariyla 'mevcut kanitla devam et' secildi) - temsili orneklem, kesin/tam tarama degil.",
        ))
    kapsam = pd.DataFrame(satirlar).rename(columns={"not_": "not"})
    kapsam_csv = ANALIZ_DIR / "odmd_oyder_kapsam_ozeti.csv"
    kapsam.to_csv(kapsam_csv, index=False, encoding="utf-8-sig")

    print("=== GENISLETME 15 - ODMD/OYDER/INDICATA KAPSAM OZETI ===\n")
    print(kapsam.to_string(index=False))
    print()
    print(f"Cikti: {ham_csv} ({len(ham)} satir)")
    print(f"Cikti: {kapsam_csv}")


if __name__ == "__main__":
    main()
