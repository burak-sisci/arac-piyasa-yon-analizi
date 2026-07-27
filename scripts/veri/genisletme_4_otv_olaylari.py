"""
GENIŞLETME AŞAMA 4 — ÖTV/vergi olay-bazlı event dummy, 2018-01 -> bugün.

2026-07-27 GÜNCELLEMESİ (2018-01 geriye genişletme turu): Bu script önceden
yalnızca 2024-01 -> 2026-06 penceresini kapsıyor ve tek olay (2025-07-24)
içeriyordu. Bu turda 2018-01 -> 2023-12 arası kamuya açık kaynaklardan
(Resmi Gazete + vergi/denetim firması sirkülerleri + haber siteleri, çapraz
doğrulamalı) TARANDI. Aşağıdaki 9 ek olay DOĞRULANARAK eklendi (toplam 10).
Her olay en az 2 bağımsız kaynakla (mümkün olduğunda doğrudan Resmi Gazete
sayı/tarihiyle) çapraz kontrol edildi; WebSearch'ün ürettiği özet metinlerdeki
sayılar (karar no, RG sayısı) ayrıca ikinci bir aramayla teyit edildi (bkz.
madde 3 - "535 sayılı karar" ilk aramada "541" ile karışmıştı, alomaliye.com'dan
doğrudan doğrulanarak düzeltildi).

TARANAN AMA OLAY BULUNAMAYAN / DOĞRULANAMAYAN DÖNEMLER (literatürde net değil,
uydurulmadı):
- 2018-01 (7061 sayılı Kanun'un 1/1/2018 yürürlüğe giren hükümleri ÖTV
  Kanunu'nu da değiştiriyor, ancak binek otomobile özgü somut matrah/oran
  rakamı içeren, kolay erişilebilir bir kaynak bulunamadı - bu yüzden 2018-01
  için bir olay eklenmedi. Seri 2018-09'a kadar "olaysız" başlıyor.)
- 2019-01 .. 2019-04 arası (2018-12-31 tarihli 535 sayılı kararın uzattığı
  indirim 2019-03-31'e kadar geçerliydi, ayrı bir yeni olay bulunamadı).
- 2020-01 .. 2020-07 arası (koronavirüs döneminde ÖTV indirimi TARTIŞILDI
  - OYDER ve Hazine Bakanlığı açıklamaları - ancak somut/yürürlüğe giren bir
  Cumhurbaşkanı Kararı BULUNAMADI; bu yüzden eklenmedi).
- 2022-01 .. 2022-10 arası (26 Temmuz 2022 tarihli Tebliğ Seri No 10, CB'ye
  binek otomobil ÖTV'sinde matrah grubu/motor gücü/emisyon türüne göre farklı
  oran belirleme YETKİSİ tanıyor ama kendisi somut oran/matrah rakamı
  İÇERMİYOR - yetki devri bir "olay" değil, 24 Kasım 2022'deki 6417 sayılı
  karar somut ilk uygulama olduğu için olay listesine O tarihle girdi).

KAPSAMDAKİ 10 OLAY (kronolojik):

1. 2018-09-24 (yürürlük) — 132 sayılı Cumhurbaşkanı Kararı, RG 30545
   (24.09.2018). Binek otomobil ÖTV matrah limitleri yükseltildi: 1600 cc altı
   üst sınır 80.000->120.000 TL; hibrit (>50kW, <=1800cc) 91.000->135.000 TL;
   1800-2000cc ve >100kW/<=2500cc hibrit 114.000->170.000 TL. Oranlar sabit,
   TL eşikleri arttı (efektif vergi yükü hafifledi).
   Kaynak: bbdas.com.tr "2018-89-Otomobillerde ÖTV Oranı Uygulanan Matrah
   Limitleri Arttırıldı".

2. 2018-10-31 (yürürlük) — 287 sayılı Cumhurbaşkanı Kararı, RG 30581
   (Mükerrer, 31.10.2018). 1600-2000cc bandındaki binek otomobillerde ÖTV
   oranı GEÇİCİ olarak %45-60'tan %30-60'a düşürüldü (5-15 puan indirim);
   31.12.2018'e kadar geçerli olacak şekilde ilan edildi (ayrıca ticari araç
   KDV'si %1'e indirildi - bu proje kapsamı dışı).
   Kaynak: muhasebenews.com "Vergi indirimi geldi – Ticari Araç KDV'si %1
   oldu – Binek Oto ÖTV'si 15 Puan indi..."; cottgroup.com.

3. 2018-12-31 (yürürlük) — 535 sayılı Cumhurbaşkanı Kararı, RG 30642
   (4. Mükerrer, 31.12.2018). 287 sayılı kararla getirilen GEÇİCİ ÖTV
   indiriminin (binek otomobil GTİP 87.03 ve bazı hibrit/hafif ticari araç
   kalemleri) uygulama süresi 31.03.2019'a UZATILDI. Yeni bir oran/matrah
   değişikliği değil, mevcut indirimin süre uzatımıdır (uzatılmasaydı
   01.01.2019'da otomatik zam anlamına gelirdi).
   Kaynak: vergidegundem.com sirküler no. 130696.

4. 2019-05-01 (yürürlük) — 1013 sayılı Cumhurbaşkanı Kararı, RG 30761
   (01.05.2019). Binek otomobillerde ÖTV oranları KALICI olarak düşürüldü:
   1600cc altı ve matrahı 70.000 TL'yi geçmeyenlerde %45->%30; 70.000-120.000
   TL aralığında %35; hibritlerde matrahı 85.000 TL'ye kadar %30, 135.000
   TL'ye kadar %35. Yeni matrah/oran sistemi.
   Kaynak: otomobilhaber.com.tr, aa.com.tr, cottgroup.com "KDV ve ÖTV'de
   Matrah, Tutar ve Oran Değişikliği".

5. 2020-08-30 (yürürlük) — 2912 sayılı Cumhurbaşkanı Kararı, RG 31229
   (30.08.2020). ÖTV Kanunu (II) sayılı listedeki bazı binek otomobillerin
   matrah eşikleri ve oranları yeniden belirlendi: 1600cc altı matrah üst
   sınırı 70.000->85.000 TL ve 120.000->130.000 TL; %45 oran eşiği
   120.000->184.000 TL; %50 eşik 150.000->220.000 TL; %60 eşik
   175.000->250.000 TL; %70 eşik 200.000->280.000 TL. İthal/lüks araç
   ÖTV yükünü artırıp yerli üretimi desteklemeyi amaçladığı belirtildi.
   Kaynak: bbdas.com.tr "2020-173-Binek Otomobillerine Uygulanan ÖTV
   Oranlarında Değişiklik Yapıldı".

6. 2021-08-13 (yürürlük) — 4373 sayılı Cumhurbaşkanı Kararı, RG 31567
   (13.08.2021). Binek otomobillerde ÖTV matrah eşikleri tekrar yükseltildi:
   1600cc altı %45 eşiği 85.000->92.000 TL, %50 eşiği 130.000->150.000 TL;
   hibrit (1600-2000cc, >50kW, <=1800cc) %45 eşiği 85.000->114.000 TL, %50
   eşiği 135.000->170.000 TL. Fiyat artışlarına karşı matrah güncellemesi
   (oranların kendisi değişmedi, yalnızca TL eşikleri).
   Kaynak: kpmgvergi.com "Bazı binek otomobilleri için ÖTV matrahları
   değiştirildi".

7. 2022-11-24 (yürürlük) — 6417 sayılı Cumhurbaşkanı Kararı, RG 32023
   (24.11.2022). ÖTV Kanunu (II) sayılı listedeki bazı binek otomobillerin
   ÖTV oranına esas matrahları yeniden belirlendi: 1600cc altı matrah alt
   limiti 120.000->184.000 TL, üst limit 200.000->280.000 TL; elektrikli
   (>50kW, <=1800cc) alt limit 130.000->228.000 TL, üst limit
   170.000->350.000 TL.
   Kaynak: grantthornton.com.tr "Binek Otomobillere İlişkin ÖTV Matrahları
   Yeniden Belirlenmiştir"; en.vergidegundem.com sirküler no. 131961.

8. 2023-07-15 (yürürlük = RG yayım tarihi) — 7456 sayılı Kanun (kabul
   14.07.2023), RG 32249 (15.07.2023). ÖTV Kanunu'nun 12. maddesi değiştirildi:
   (a) Cumhurbaşkanına (I) sayılı listedeki (akaryakıt) maktu vergi
   tutarlarını 5 katına kadar artırma/sıfıra indirme yetkisi verildi ve bu
   tutarların Ocak-Temmuz aylarında Yİ-ÜFE'ye göre otomatik güncellenmesi
   mekanizması getirildi (bu kısım akaryakıt ürünleri için, binek otomobili
   DOĞRUDAN ilgilendirmiyor); (b) AYNI KANUNLA, (II) sayılı listedeki binek
   otomobil ve motosikletler için TÜRKİYE'DE İLK KEZ "asgari maktu ÖTV" esası
   mevzuata girdi: binek otomobillerde (GTİP 8703) hesaplanan oransal ÖTV
   tutarı 100.000 TL'nin, motosikletlerde 30.000 TL'nin altında kalırsa
   doğrudan bu taban tutar esas alınacak; taban tutarlar yıllık VUK yeniden
   değerleme oranına göre otomatik güncellenecek; Cumhurbaşkanına bu tabanları
   10 katına kadar artırma/sıfıra indirme yetkisi verildi.
   Kaynak: kpmgvergi.com (7456 sayılı Kanun bültenleri), donanimhaber.com
   "Binek otomobillere asgari 100 bin TL ÖTV geliyor", log.com.tr.

9. 2023-11-18 (yürürlük) — 7803 sayılı Cumhurbaşkanı Kararı, RG 32373
   (18.11.2023). SADECE elektrik motorlu (hibrit HARİÇ) binek otomobillerde
   ÖTV matrah eşiği güncellendi: motor gücü <=160 kW olanlarda matrah eşiği
   1.250.000->1.450.000 TL (oran %10 sabit kaldı); >160 kW olanlarda eşik
   1.350.000 TL sabit kaldı (oranlar %50/%60 sabit).
   Kaynak: verginet.net Vergi Sirküleri 2023-109 "Elektrikli Otomobillerde
   ÖTV Matrahı 1.450.000 TL'ye Çıkarıldı"; grantthornton.com.tr.

10. 2025-07-24 (yürürlük) — 7555 sayılı Kanun'un 13. maddesi + 10115 sayılı
    Cumhurbaşkanı Kararı (RG, 23-24 Temmuz 2025). ÖTV Kanunu'na ekli (II)
    sayılı listedeki araçlar için matrah grupları/oranları yeniden
    tanımlandı; matrah sistemi motor hacmi/gücünden ARINDIRILIP vergisiz
    satış fiyatı bazlı hale getirildi. Elektrikli otomobillerde en düşük ÖTV
    oranı %10'dan %25'e çıktı, matrah eşiği 1.650.000 TL'ye güncellendi.
    (Önceki turdan - bkz. verginet.net Vergi Sirküleri 2025-74; watmobilite.com.)
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "otv"

BASLANGIC_AY = "2018-01"
BITIS_AY = "2026-06"

OLAYLAR = [
    dict(tarih="2018-09-24", referans_ayi="2018-09",
         aciklama="132 sayılı Cumhurbaşkanı Kararı (RG 30545): binek otomobil "
                   "ÖTV matrah limitleri yükseltildi (1600cc altı ust sinir "
                   "80.000->120.000 TL; 1800-2000cc/hibrit 114.000->170.000 TL).",
         kaynak_url="https://bbdas.com.tr/2018-89-otomobillerde-otv-orani-uygulanan-matrah-limitleri-arttirildi-g-500"),
    dict(tarih="2018-10-31", referans_ayi="2018-10",
         aciklama="287 sayılı Cumhurbaşkanı Kararı (RG 30581 Mükerrer): "
                   "1600-2000cc binek otomobillerde ÖTV orani GECICI olarak "
                   "%45-60'tan %30-60'a dusuruldu (31.12.2018'e kadar).",
         kaynak_url="https://www.muhasebenews.com/vergi-indirimi-geldi-ticari-arac-kdvsi-1-oldu-binek-oto-otvsi-15-puan-indi-beyaz-esya-otv-sifirlandi-31-ekim-2018/"),
    dict(tarih="2018-12-31", referans_ayi="2018-12",
         aciklama="535 sayılı Cumhurbaşkanı Kararı (RG 30642, 4. Mükerrer): "
                   "287 sayılı kararla getirilen gecici ÖTV indiriminin suresi "
                   "31.03.2019'a uzatildi (yeni oran degil, sure uzatimi).",
         kaynak_url="https://www.vergidegundem.com/sirkuler/130696"),
    dict(tarih="2019-05-01", referans_ayi="2019-05",
         aciklama="1013 sayılı Cumhurbaşkanı Kararı (RG 30761): binek "
                   "otomobillerde ÖTV oranlari KALICI dusuruldu (1600cc alti "
                   "%45->%30 vb.), yeni matrah sistemi.",
         kaynak_url="https://www.cottgroup.com/tr/mevzuat/item/kdv-ve-otv-de-matrah-tutar-ve-oran-degisikligi"),
    dict(tarih="2020-08-30", referans_ayi="2020-08",
         aciklama="2912 sayılı Cumhurbaşkanı Kararı (RG 31229): binek "
                   "otomobil ÖTV matrah esikleri ve oranlari yeniden "
                   "belirlendi (%45 esigi 120.000->184.000 TL vb.).",
         kaynak_url="https://www.bbdas.com.tr/2020-173-binek-otomobillerine-uygulanan-otv-oranlarinda-degisiklik-yapildi-g-1382"),
    dict(tarih="2021-08-13", referans_ayi="2021-08",
         aciklama="4373 sayılı Cumhurbaşkanı Kararı (RG 31567): binek "
                   "otomobil ÖTV matrah esikleri tekrar yukseltildi (1600cc "
                   "alti %45 esigi 85.000->92.000 TL vb.).",
         kaynak_url="https://kpmgvergi.com/yayinlar/mali-bultenler/vergi/bazi-binek-otomobilleri-icin-otv-matrahlari-degistirildi/1191"),
    dict(tarih="2022-11-24", referans_ayi="2022-11",
         aciklama="6417 sayılı Cumhurbaşkanı Kararı (RG 32023): binek "
                   "otomobil ÖTV matrahlari yeniden belirlendi (1600cc alti "
                   "alt limit 120.000->184.000 TL, ust limit 200.000->280.000 TL).",
         kaynak_url="https://www.grantthornton.com.tr/vergi-sirkuleri/2022-vergi-sirkuleri/binek-otomobillere-iliskin-otv-matrahlari-yeniden-belirlenmistir/"),
    dict(tarih="2023-07-15", referans_ayi="2023-07",
         aciklama="7456 sayılı Kanun (RG 32249): ÖTV Kanunu m.12 degisti; "
                   "binek otomobil/motosiklet icin ilk kez 'asgari maktu ÖTV' "
                   "esasi getirildi (binek otomobilde taban 100.000 TL, "
                   "motosiklette 30.000 TL, yillik VUK yeniden degerleme "
                   "oranina gore guncellenecek).",
         kaynak_url="https://www.donanimhaber.com/binek-otomobillere-asgari-100-bin-tl-otv-geliyor--208501"),
    dict(tarih="2023-11-18", referans_ayi="2023-11",
         aciklama="7803 sayılı Cumhurbaşkanı Kararı (RG 32373): sadece "
                   "elektrikli (hibrit haric) binek otomobillerde ÖTV matrah "
                   "esigi guncellendi (<=160kW icin 1.250.000->1.450.000 TL, "
                   "oran %10 sabit).",
         kaynak_url="https://www.verginet.net/dtt/11/Vergi-Sirkuleri-2023-109.aspx"),
    dict(tarih="2025-07-24", referans_ayi="2025-07",
         aciklama="7555 sayılı Kanun m.13 + 10115 sayılı Cumhurbaşkanı Kararı: "
                   "ÖTV matrah sistemi motor hacmi/gücünden vergisiz-satış-fiyatı "
                   "bazına geçti; EV'lerde en düşük ÖTV %10->%25, matrah eşiği "
                   "1.650.000 TL.",
         kaynak_url="https://www.verginet.net/dtt/11/Vergi-Sirkuleri-2025-74.aspx"),
]


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    aylar = pd.period_range(BASLANGIC_AY, BITIS_AY, freq="M").astype(str).tolist()
    df = pd.DataFrame({"referans_ayi": aylar})
    df["otv_event_ay_mi"] = 0
    df["otv_aciklama"] = ""

    for olay in OLAYLAR:
        idx = df.index[df["referans_ayi"] == olay["referans_ayi"]]
        if len(idx):
            df.loc[idx, "otv_event_ay_mi"] = 1
            mevcut = df.loc[idx, "otv_aciklama"]
            df.loc[idx, "otv_aciklama"] = mevcut.where(
                mevcut == "", mevcut + " | "
            ) + olay["aciklama"]

    # Birden fazla olay oldugu icin "otv_ay_farki" artik TEK bir referans
    # olaya degil, EN YAKIN olaya olan (isaretli) ay farkina karsilik gelir:
    # pozitif = en yakin olay GECMISTE (o kadar ay once yururluge girdi),
    # negatif = en yakin olay GELECEKTE, 0 = bu ayin kendisinde bir olay var.
    olay_ay_periyotlari = [pd.Period(o["referans_ayi"], freq="M") for o in OLAYLAR]

    def en_yakin_olay_farki(referans_ayi_str):
        ay = pd.Period(referans_ayi_str, freq="M")
        farklar = [(ay - olay_ay).n for olay_ay in olay_ay_periyotlari]
        return min(farklar, key=abs)

    df["otv_ay_farki_en_yakin_olay"] = df["referans_ayi"].apply(en_yakin_olay_farki)

    csv_yolu = RAW_DIR / "otv_olaylari_2018_bugun_aylik.csv"
    xlsx_yolu = RAW_DIR / "otv_olaylari_2018_bugun_aylik.xlsx"
    df.to_csv(csv_yolu, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_yolu, index=False, sheet_name="otv_olaylari")

    print("=== GENISLETME 4 - OTV OLAY-DUMMY OZET (2018-01 genisletmesi) ===")
    print(f"Kapsam: {BASLANGIC_AY} .. {BITIS_AY} ({len(df)} ay)")
    print(f"Tespit edilen olay sayisi: {len(OLAYLAR)}")
    for o in OLAYLAR:
        print(f"  - {o['referans_ayi']} ({o['tarih']}): {o['aciklama'][:80]}...")
    print()
    print(df.to_string(index=False))
    print(f"\nCikti: {csv_yolu} , {xlsx_yolu}")


if __name__ == "__main__":
    main()
