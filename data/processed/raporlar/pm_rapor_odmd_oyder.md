---
başlık: PM Raporu — ODMD/OYDER/Indicata "İkinci El Online Sektör Raporu" Derinlemesine Tarama
tarih: 2026-07-30
kapsam: Yalnızca veri toplama/kapsam netleştirme. Hedef/model değiştirilmedi,
  ODMD/OYDER verisi BETAM ile birleştirilmedi.
prompt_arşivi: prompts/veri/15_odmd_oyder_aylik_bulten_prompt.md
kaynak_kod: scripts/veri/genisletme_15_odmd_oyder.py
durum: tamamlandı (kullanıcı kararıyla sınırlı kapsamda — "mevcut kanıtla devam et")
---

## Önemli çerçeve notu

Bu tur, oturum içinde kullanıcıya sorulan bir ara-durum sorusu sonrası
**"mevcut kanıtla devam et"** kararıyla sonlandırıldı. 2021-2023 arası
**36 ayın tamamı tek tek taranmadı** — bu bir NİHAİ/TAM tarama değil,
**temsili bir örneklemdir**. Aşağıdaki bulgular bu sınırla okunmalıdır.

## 1) Ne yapıldı

ODMD'nin resmi sitesi (odmd.org.tr), OYDER'in arşiv sayfası (oyder-tr.org)
ve — araştırma sırasında ortaya çıkan asıl kaynak — Indicata'nın kendi sitesi
(indicata.com.tr) tarandı. Amaç: "İkinci El Online Sektör Raporu"nun
2021-2023 için gerçekten aylık mı yoksa yalnızca yıllık mı yayımlandığını
netleştirmek. 10 ay için gerçek veri veya mevcudiyet kanıtı bulundu, 2 tam
yıl toplamı (2021, 2022) ve 1 kümülatif dönem (2023 Ocak-Ekim) elde edildi.

## 2) EN KRİTİK SONUÇ — 2021-2023 için gerçek kapsam nedir

**Bulgu YARI YARIYA doğrulandı, YARI YARIYA çürütüldü — ayrıntı önemli:**

- **ODMD'nin KENDİ resmi listesi** (`odmd.org.tr/web_2837_1/neuralnetwork.aspx?type=90`)
  gerçekten yalnızca **Aralık (yıl-sonu özet)** sürümünü yayımlıyor —
  2020, 2021, 2022, 2023, 2024, 2025 için birer Aralık bülteni + 2026
  Haziran. Bu, önceki "yılda bir" bulgusunu **ODMD'nin kendi sitesi için
  doğruluyor**.
- **AMA asıl kaynak OYDER değil, Indicata'nın kendi sitesidir**
  (indicata.com.tr, "haberler-ve-medya" bölümü). Bu sitenin eski makale
  ID sırası (74=Şubat 2021, 87=Aralık 2021, 99=Eylül 2022, 103=Aralık 2022,
  115=Ekim 2023, 122=Ocak 2024...) **aylık yayın deseninin gerçekten var
  olduğuna dair güçlü DOLAYLI kanıt** sunuyor — ID'ler arası fark, aylık
  artışla tutarlı.
- **SORUN:** indicata.com.tr yakın zamanda yeniden yapılandırılmış — eski
  URL'lerin TAMAMI artık 404 veriyor. Bu yüzden "aylık yayımlanıyordu"
  iddiası kanıtlanabilir ama "aylık VERİYİ bu turda çıkardık" iddiası
  **çoğu ay için doğru değil**.

**Somut sayılar (bu turun ulaştığı kapsam):**

| Yıl | Gerçek veriyle bulunan ay | Yalnızca mevcudiyeti doğrulanan ay | Bulunamayan/taranmayan ay | Tam yıl toplamı var mı |
|---|---|---|---|---|
| 2021 | **0/12** | 2/12 (Şubat, Aralık) | 10/12 | **EVET** (AA kaynaklı, 3.540.937 ilan / 1.652.710 satış) |
| 2022 | **2/12** (Eylül, Aralık) | 1/12 (Temmuz) | 9/12 | **EVET** (AA kaynaklı, 3.949.259 ilan / 1.811.498 satış) |
| 2023 | **2/12** (Haziran, Ağustos) | 1/12 (Ekim) | 9/12 | **HAYIR** (yalnızca Ocak-Ekim kümülatif %değişim: ilan +%6, satış +%10) |

## 3) Bulunan bültenlerin içerik zenginliği

- **En zengin: Haziran 2023** (tek doğrudan doğrulanmış kaynak — LinkedIn
  makalesi WebFetch ile tam okundu): ilan sayısı, satış adedi, segment
  kırılımı (binek vs hafif ticari), YoY karşılaştırma, 6 aylık kümülatif
  toplam.
- **Orta: Eylül/Aralık 2022, Ağustos 2023** — yalnızca ilan sayısı
  (Eylül 2022) veya ilan sayısı + satış adedi (Aralık 2022, Ağustos 2023).
- **HİÇBİR ayda bulunamayan alanlar (Görev 3'ün istediği 6 alandan 4'ü hiç
  çıkarılamadı):** fiyat değişimi % (perakende/toptan), segment (A/B/C/D)
  sınıf dağılımı, yaş grubu dağılımı, yakıt tipi dağılımı. **Not:** daha
  sonraki bir örnekte (2025 Aralık haberinde, bu turun asıl kapsamı
  dışında rastlantısal görülen) yaş grubu kırılımının rapor formatında
  GENELDE var olduğu görüldü — yani alan muhtemelen raporun kendisinde
  mevcut, yalnızca bizim erişebildiğimiz özetlerde yoktu.
- **2021 en zayıf yıl:** hiçbir ay için gerçek rakam çıkarılamadı, yalnızca
  2 ayın (başlık düzeyinde) var olduğu teyit edildi.

## 4) Kaynak güvenilirliği

10 "bulundu" kaydından (yıl toplamları ve kümülatif dahil, 13 satır):
- **1 doğrudan doğrulanmış** (Haziran 2023, LinkedIn makalesi WebFetch ile
  tam okundu).
- **2 yüksek-güvenilir haber ajansı** (AA — Anadolu Ajansı, 2021 ve 2022
  yıllık toplamları).
- **2 arama-özeti, kaynağı belli** (Eylül/Aralık 2022 — indicata.com.tr'nin
  kendi sayfası ama yalnızca WebSearch'ün önbelleğe alınmış özetinden,
  sayfanın kendisi canlı erişilemiyor).
- **2 mevcudiyet-yalnızca** (Şubat/Aralık 2021 — sayfa başlığı/URL'i
  tespit edildi ama içerik çıkarılamadı).
- **1 mevcudiyet-yalnızca PDF** (Temmuz 2022).
- **1 mevcudiyet-yalnızca** (Ekim 2023).
- **1 arama-özeti, kaynak URL'i belirsiz** (Ağustos 2023 — WebSearch özet
  metninde rakam vardı ama net bir URL verilmedi, **UYDURULMADI**, boş
  bırakıldı).
- **1 arama-özeti, kaynak URL'i belirsiz** (2023 Ocak-Ekim kümülatif).

**Çapraz doğrulama bu turda YAPILAMADI** (ENAG turundaki gibi 2 bağımsız
kaynaktan teyit) — kaynak sayfalarının çoğu ölü olduğu için bağımsız ikinci
kaynak bulma fırsatı çok sınırlıydı. Bu, ENAG turuna göre daha düşük bir
metodolojik güvenilirlik seviyesidir, açıkça not edilir.

## 5) Karşılaşılan sorunlar

1. **indicata.com.tr yakın zamanda yeniden yapılandırılmış** (muhtemelen
   2025'te, WordPress'e geçiş) — eski `haberler-ve-medya/{id}-{slug}` ve
   `/download/{Ay}{Yıl}_..._Raporu.pdf` URL kalıpları TAMAMEN 404 veriyor;
   yalnızca yeni `wp-content/uploads/{yıl}/{ay}/...` kalıbı (2025 sonrası
   içerikler için) çalışıyor durumda (test edildi, Eylül 2025 PDF'i
   indirildi ama içeriği bu tur için okunmadı).
2. **Bare domain (indicata.com.tr) uluslararası Autorola/Indicata kurumsal
   sitesine yönlendiriyor** — Türkçe "haberler-ve-medya" navigasyon menüsü
   artık sitede görünmüyor.
3. **Wayback Machine (web.archive.org) bu oturumda erişime kapalıydı**
   (hem WebFetch hem tarayıcı aracı için) — eski sayfaları arşivden
   kurtarma denenemedi.
4. **OYDER'in `raporlar/7` ("ODMD") kategorisi YANLIŞ kategori çıktı** —
   bu, ODMD'nin ANA (sıfır araç) satış bültenlerini içeriyor, "İkinci El
   Online Sektör Raporu"nu DEĞİL. Kullanıcının öncül gözlemi ("OYDER
   arşivinde 2024 için aylık bültenler bulundu") muhtemelen farklı bir
   kategori/arama sonucuna dayanıyordu — bu turda o spesifik OYDER kategorisi
   bulunamadı, açık soru olarak Bölüm 7'de bırakıldı.
5. **WebSearch'ün AI-özetleri birden fazla kez bozuk/kırpılmış rakam
   döndürdü** (bu projenin daha önce kanıtladığı bir risk, ör. "9,11"
   yerine "129,11"nin kırpılmış hali gibi örüntüler). Hiçbiri doğrudan
   kullanılmadı; yalnızca net/tutarlı görünen rakamlar kaydedildi.

## 6) Veri örneği (odmd_oyder_bultenler_ham.csv)

```
referans_ayi,ilan_sayisi,satis_adedi,bulunabilirlik_durumu
2021-01,,,bulunamadı
2021-02,,,mevcudiyet_dogrulandi_icerik_yok
2022-09,342067,,bulundu_arama_ozetinden
2022-12,348056,215466,bulundu_arama_ozetinden
2023-06,298004,180748,bulundu_dogrulanmis
2023-08,360445,125935,bulundu_arama_ozetinden
2021-YIL,3540937,1652710,bulundu_dogrulanmis (YILLIK TOPLAM)
2022-YIL,3949259,1811498,bulundu_dogrulanmis (YILLIK TOPLAM)
```

(Tam dosya 39 satır — 36 ay + 2 yıllık toplam + 1 kümülatif dönem —
`data/raw/odmd_oyder/odmd_oyder_bultenler_ham.csv` içinde mevcuttur.)

## 7) Açık sorular / PM onayı gerekenler

**Asıl soru — "Bu kaynak BETAM'ın 2021-2023 açığını kapatmaya yeter mi?"**
(kanıt, karar değil):

**HAYIR, şu anki haliyle YETMEZ.** Kanıt:
- 2021 için **SIFIR ay** gerçek veri var (yalnızca yıllık toplam) — aylık
  bir seri kurulamaz.
- 2022 ve 2023 için yalnızca **2'şer ay** (12 ayın %17'si) gerçek veri var
  — bir aylık zaman serisi için ciddi ölçüde yetersiz.
- **En kritik eksik:** hiçbir ayda BETAM'ın sunduğu "proxy_fiyat_cari_tl"
  (TL cinsinden fiyat) ile karşılaştırılabilir bir **fiyat değişimi %**
  alanı BULUNAMADI — bu turda yalnızca HACİM (ilan sayısı/satış adedi)
  verisi çıkarılabildi. Bu, kaynağın BETAM'ın **fiyat serisi** rolünü
  ALAMAYACAĞI, olsa olsa **hacim/aktivite göstergesi** olarak (ODMD'nin
  zaten sağladığı sıfır-araç hacmine benzer şekilde) tamamlayıcı
  olabileceği anlamına geliyor.

**Diğer açık sorular:**

1. Bu turda taranmayan **26 ay** var (36 aydan 10'u ele alındı). Daha
   derin bir tarama (ör. paralel ajan/Workflow izniyle) kalan ayları
   kısmen doldurabilir, ama indicata.com.tr'nin eski sayfalarının ölü
   olması nedeniyle tam 36/36 kapsam garantisi verilemez.
2. indicata.com.tr'nin GÜNCEL (2025 sonrası) `wp-content/uploads` yapısı
   çalışıyor — ileride bu yapı üzerinden 2021-2023 arşivinin bir
   kopyasının orada barındırılıp barındırılmadığı ayrıca kontrol
   edilebilir (bu turda denenmedi, kapsam dışı bırakıldı).
3. OYDER'in gerçekte hangi kategori/sayfasında 2024 aylık bültenlerin
   bulunduğu netleştirilemedi — kullanıcının orijinal gözleminin kaynağı
   bu turda tespit edilemedi.
4. Wayback Machine erişimi bu oturumda kapalıydı — başka bir oturumda/
   araçla denenirse eski sayfaların önemli bir kısmı kurtarılabilir.
