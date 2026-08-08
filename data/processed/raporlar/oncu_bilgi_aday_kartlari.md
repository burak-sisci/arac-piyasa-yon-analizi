# Öncü Bilgi Aday Kartları — Masa Başı Kapsam Taraması

**Tarih:** 2026-08-08

**Durum:** Masa başı tarama tamamlandı; veri erişimi/toplama başlatılmadı

**Karar:** Seçenek 2 — hedef ve üç sınıf korunarak bilgi kümesini genişlet

**Kapsam sınırı:** En fazla üç aday; kamuya açık sayfa okuması dışında erişim yok

## Sonuç özeti

| Aday | Kapatılan gerçek boşluk | Ön hüküm | Ana neden |
|---|---|---|---|
| BDDK haftalık taşıt kredisi bakiyesi ve değişimi | Finansmana fiili erişim/kullanım | **Koşullu devam** | 2014'ten beri haftalık kapsam ve ilan edilmiş yayın takvimi var; fakat seri onay/başvuru değil bakiye vekilidir ve ilk-yayım vintajları doğrulanmalıdır. |
| BETAM–sahibindex ilan arzı ve ilan yaşı göstergeleri | İlan arzı, stok ve ilan yaşı | **Bu protokol için elendi** | İlk kamuya açık rapor Aralık 2023'tür; raporda geriye doldurulan üç yıl bulunmasına rağmen gerçek zamanlı vintaj geçmişi rolling-origin için kısa kalır. |
| Google Trends araç-alım arama ilgisi | Gerçek zamanlı işlem niyeti | **Geriye dönük test için elendi** | UI örneklenmiş ve sorgu penceresine göre 0–100 yeniden ölçeklidir; tutarlı API yalnız sınırlı alpha erişiminde ve beş yıllık kayan pencere sunar. |

Bu hükümler performans hükmü değildir. “Koşullu devam”, yalnız bir sonraki veri
erişimi fizibilite aşamasında sınanmaya değer demektir.

## Aday kartı 1 — BDDK haftalık taşıt kredisi bakiyesi ve değişimi

| Alan | Kayıt |
|---|---|
| `aday_adi` | BDDK haftalık bankacılık sektörü — tüketici taşıt kredileri toplam bakiyesi ve haftalık/ay-içi değişimi |
| `kaynak_sahibi` | Bankacılık Düzenleme ve Denetleme Kurumu (BDDK) |
| `ham_frekans` | Haftalık |
| `ilk_tarih` | Ocak 2014; haftalık metaverinin verdiği başlangıç. İlk kesin hafta bu masa başı aşamada doğrulanmadı. |
| `yayin_gecikmesi_gun` | **Doğrulanmadı.** 2026 takvimi haftalık kesin yayın tarih/saatlerini verir; referans haftası–yayım tarihi eşlemesi gerçek erişim aşamasında satır bazında doğrulanmalı. |
| `M_eksi_2_aninda_erisim` | **Evet, takvim düzeyinde.** Haftalık yayımlanan bir değer iki ay sonraki kesimde kamuya çıkmış olur; ancak kullanılacak vintajın ilk-yayım değeri olduğu ayrıca kanıtlanmalı. |
| `revizyon_politikasi` | Rutin ve ana revizyon mümkündür. BDDK, dönemsel verinin takip eden yayınlarda değişebileceğini ve tabloları güncelleyebileceğini açıklar. Bu nedenle ilk-yayım vintajı veya revizyon etkisi tutulmadan as-of kapısı geçilmiş sayılmaz. |
| `kapatilan_bilgi_boslugu` | Finansmana fiili erişim/onay ailesinin **kullanım/bakiye vekili**. Faiz oranından farklıdır; doğrudan onay oranı değildir. |
| `mekanizma_bir_cumle` | Reel ve mevsimsel etkilerden arındırılmış net taşıt kredisi bakiye akışı, krediyle finanse edilen araç alımlarındaki gerçekleşmiş finansman kullanımının yönünü kısmen taşıyabilir. |
| `mevcut_featuredan_neden_farkli` | Mevcut `tasit_kredi_faizi_lag2`, kredinin fiyatını ölçer; bu aday bankacılık sistemindeki gerçekleşmiş kredi bakiyesini ve değişimini ölçer. |
| `hukuki/erişim_riski` | Kamuya açık ve toplulaştırılmış resmi istatistik. Otomatik erişim biçimi, dosya lisansı ve ilk-yayım arşivinin korunup korunmadığı veri erişimi aşamasında doğrulanmadı. |
| `as_of_vintage_riski` | **Orta–yüksek.** Seri revize olabilir; yalnız güncel tarihsel seri kullanılırsa geçmiş originlere sonradan düzeltilmiş değer sızabilir. |
| `on_hukum` | **Koşullu devam.** Sonraki küçük aşama yalnız erişim/vintaj fizibilitesi olmalı; henüz feature üretimi veya modelleme yapılmamalı. |

Kaynaklar:

- BDDK, [Haftalık Bülten ana sayfası](https://www.bddk.org.tr/Veri/Detay/158):
  verinin BVTS üzerinden derlendiğini ve Resmî İstatistik Programı kapsamında
  olduğunu açıklar.
- BDDK, [Haftalık Bülten gelişmiş gösterim](https://www.bddk.org.tr/BultenHaftalik/tr/Gelismis):
  “Taşıt” kalemini haftalık kredi tablosunda gösterir.
- BDDK, [Haftalık Bülten metaverisi](https://www.bddk.org.tr/BultenDosyalari/Home/Index/Haftalik-MetaVeri):
  haftalık zaman serisinin Ocak 2014'ten başladığını belirtir.
- BDDK, [Veri yayımlama takvimi](https://www.bddk.org.tr/Veri/Detay/71):
  haftalık yayınların tarih ve saatlerini önceden listeler.
- BDDK, [Veri yayınları SSS](https://www.bddk.org.tr/Sss/Liste/110): revizyonların
  takip eden dönemlerde veriyi değiştirebileceğini açıklar.

## Aday kartı 2 — BETAM–sahibindex ilan arzı ve ilan yaşı

| Alan | Kayıt |
|---|---|
| `aday_adi` | sahibindex satılık ilan sayısı, kapatılan ilan sayısı, satılan/satılık oranı ve kapatılan ilan yaşı |
| `kaynak_sahibi` | sahibinden.com veri havuzu; Bahçeşehir Üniversitesi BETAM raporlaması |
| `ham_frekans` | Aylık rapor; platformdaki ham olay frekansı kamuya açık raporda belirtilmiyor |
| `ilk_tarih` | İlk kamuya açık seri raporu Aralık 2023 ve Kasım 2023 görünümünü verir. Aynı rapor geçmiş üç yılı geriye dönük özetler; 2023 öncesi değerler gerçek zamanlı ilk-yayım vintajı değildir. |
| `yayin_gecikmesi_gun` | Bir önceki ayın verisi izleyen ay raporlanır; kesin ve sabit gün sayısı **doğrulanmadı**. |
| `M_eksi_2_aninda_erisim` | **Cari kullanımda muhtemelen evet**, çünkü önceki ay izleyen ay yayımlanır; fakat geçmiş rolling-origin vintajı yalnız 2023 sonundan itibaren gözlenebilir. |
| `revizyon_politikasi` | Kamuya açık sayfalarda açık bir revizyon/vintaj politikası **doğrulanmadı**. |
| `kapatilan_bilgi_boslugu` | İlan arzı, stok ve ilan yaşı; ayrıca satışa dönüşüm için kapatılan/satılık oranına yakın bir platform göstergesi. |
| `mekanizma_bir_cumle` | İlan stokunun büyümesi, kapanma hızının ve ilan yaşının değişmesi ikinci el piyasanın arz sıkılığı ile alıcı-satıcı eşleşme hızını doğrudan yansıtabilir. |
| `mevcut_featuredan_neden_farkli` | Kur, faiz, takvim ve hedef gecikmelerinden farklı olarak platform içi stok ve eşleşme davranışını ölçer. |
| `hukuki/erişim_riski` | Yayın metinleri açık olsa da ham seri sahibinden.com mülkiyetindedir; makinece okunabilir tam tarihsel seri ve yeniden kullanım koşulları doğrulanmadı. |
| `as_of_vintage_riski` | **Yüksek.** İlk rapordaki geçmiş üç yıl sonradan geriye doldurulmuştur; o dönemlerde bilinen ilk-yayım değerleri değildir. |
| `on_hukum` | **Bu protokol için elendi.** 50-origin benzeri geriye dönük değerlendirme için as-of kapsam yetersiz. Yalnız ileriye dönük gölge izleme ayrı bir kullanıcı kararıyla düşünülebilir. |

Kaynaklar:

- BETAM, [sahibindex Otomobil Piyasası Görünümü: Aralık 2023](https://betam.bahcesehir.edu.tr/2023/12/sahibindex-otomobil-piyasasi-gorunumu/):
  ilk rapor olduğunu, son üç yılı ele aldığını ve bundan sonra aylık olarak önceki
  ay verileriyle güncelleneceğini açıklar.
- BETAM, [sahibindex Otomobil Piyasası Görünümü: Temmuz 2026](https://betam.bahcesehir.edu.tr/2026/07/sahibindex-otomobil-piyasasi-gorunumu-temmuz-2026/):
  ilan sayısı, kapatılan ilan sayısı, satılan/satılık oranı ve ilanda kalma
  süresinin aylık raporda birlikte yayımlandığını gösterir.
- BETAM, [Otomotiv Piyasası Görünümü arşivi](https://betam.bahcesehir.edu.tr/kategori/ekonomik-arastirmalar/yayinlar/otomotiv-piyasasi-gorunumu/):
  kamuya açık rapor dizisini listeler.

## Aday kartı 3 — Google Trends araç-alım arama ilgisi

| Alan | Kayıt |
|---|---|
| `aday_adi` | Türkiye için otomobil satın alma niyetine yakın sorgu/konu sepetinin Google arama ilgisi |
| `kaynak_sahibi` | Google Trends |
| `ham_frekans` | UI'da sorgu aralığına bağlı günlük/haftalık; alpha API günlük, haftalık, aylık ve yıllık toplulaştırma sunacağını belirtir |
| `ilk_tarih` | UI tarihsel veri 2004'e uzanabilir; tutarlı ölçekli alpha API yalnız kayan son 1.800 günü (yaklaşık beş yıl) kapsar. |
| `yayin_gecikmesi_gun` | Alpha API dokümanı verinin yaklaşık iki gün öncesine kadar geldiğini söyler; genel UI için sabit SLA **doğrulanmadı**. |
| `M_eksi_2_aninda_erisim` | **Cari kullanım için evet**, ancak geriye dönük aynı vintajı yeniden kurmak mümkün olduğuna dair kanıt yok. |
| `revizyon_politikasi` | UI verisi örneklenir, istatistiksel gürültü içerir ve her sorgunun zaman/coğrafya penceresinde 0–100 ölçeklenir. Sabit geçmiş ilk-yayım arşivi doğrulanmadı. |
| `kapatilan_bilgi_boslugu` | Gerçek zamanlı işlem niyeti için arama davranışı vekili. |
| `mekanizma_bir_cumle` | Araç alma, kredi ve ikinci el ilan sorgularındaki geniş tabanlı ilgi artışı, işlemler gerçekleşmeden önce araştırma niyetini kısmen yansıtabilir. |
| `mevcut_featuredan_neden_farkli` | Ekonomik koşulu değil doğrudan kullanıcı arama davranışını ölçmeyi amaçlar. |
| `hukuki/erişim_riski` | UI kamuya açık; tutarlı ölçekli API 2026-08-08 itibarıyla sınırlı alpha erişimindedir. Sorgu sepeti seçimi ciddi araştırmacı serbestlik derecesi yaratır. |
| `as_of_vintage_riski` | **Çok yüksek.** Örnekleme, gürültü ve yeniden ölçekleme geçmiş değeri çekim zamanına/sorgu penceresine bağımlı kılabilir. |
| `on_hukum` | **Geriye dönük test için elendi.** Ancak bugün başlanacak değişmez sorgu sepeti ve çekim-vintaj arşiviyle yalnız ileriye dönük gölge aday olabilir. |

Kaynaklar:

- Google, [FAQ about Google Trends data](https://support.google.com/trends/answer/4365533?hl=en):
  verinin örneklenmiş, normalize edilmiş, 0–100 ölçekli ve istatistiksel gürültü
  içerebilen bir arama ilgisi göstergesi olduğunu açıklar.
- Google Search Central, [Introducing the Google Trends API (alpha)](https://developers.google.com/search/blog/2025/07/trends-api):
  sınırlı alpha erişimini, tutarlı ölçeği, 1.800 günlük pencereyi, frekansları ve
  yaklaşık iki günlük güncelliği açıklar.

## Ön-kayıt sonucu

1. **BDDK adayı** gerçek bir boşluğu kapatır ve tarih kapsamı açısından sonraki
   erişim fizibilitesine taşınabilir; henüz as-of kapısını geçmiş değildir.
2. **BETAM–sahibindex** ekonomik olarak daha doğrudan olsa da kamuya açık
   ilk-yayım geçmişi mevcut rolling-origin tasarımı için kısa kalır.
3. **Google Trends** niyet açısından caziptir; fakat geçmiş vintajın yeniden
   kurulabilirliği kanıtlanmadan geriye dönük model girdisi olamaz.
4. Oracle `null95 + 0,15` tavan kapısı aynen korunur. Hiçbir aday için bu aşamada
   oracle veya performans hesabı yapılmamıştır.
