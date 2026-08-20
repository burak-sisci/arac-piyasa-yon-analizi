# TOKKDER filo/kiralama sektörü – ikinci ele araç elden çıkarma hızı

TOKKDER (Tüm Oto Kiralama ve Mobilite Kuruluşları Derneği; eski adıyla Tüm Oto Kiralama Kuruluşları Derneği), bağımsız araştırma şirketi **NielsenIQ** ile birlikte, araç kiralama sektörünü iki ayrı segmentte **çeyreklik** olarak raporluyor:

1. **Operasyonel (uzun dönem) kiralama sektörü** — filo kiralama şirketlerinin kurumsal müşterilere 6 ay ve üzeri sürelerle kiraladığı araçlar. Bu raporda **"Satılan Araç (2.El) Sayısı"** adlı ayrı bir kalem var — filodan ikinci el pazara doğrudan satılan araç adedidir. Bu, görevin aradığı "elden çıkarma hızı/adedi" göstergesine en doğrudan karşılık gelen TOKKDER kalemidir.
2. **Kısa dönem (günlük) kiralama sektörü** — 2025 1. çeyreğinden itibaren yayımlanmaya başlayan, daha yeni bir rapor serisi. Burada **"Toplam Filo Çıkış"** adedi ve **"ortalama araç yaşı (ay)"** yayımlanıyor; ikincisi filonun ne kadar sürede döndüğünün dolaylı bir göstergesi.

Her iki rapor da TOKKDER'in ikişer ayda bir çıkan **filoverentacar** dergisinin "ARAŞTIRMA" bölümünde, ayrıca bazı çeyreklerde bağımsız bir NielsenIQ sunum PDF'i olarak yayımlanıyor. Dergiler resmi TOKKDER sitesinde (`tokkder.org/wp-content/uploads/...`) barındırılıyor; WebSearch indeksinde başlıkları görünse de çoğu dergi PDF'i tarayıcıdan doğrudan metne çevrilemiyor (ikili/encoded döndürüyor) — bu satırlardaki veriler PDF sayfaları görsel olarak açılıp (multimodal okuma) tablodan **elle doğrulanarak** çıkarılmıştır.

## Dosyalar

### `tokkder_operasyonel_ikinciel_satis_ceyreklik.csv`

Operasyonel (uzun dönem) kiralama sektörünün çeyreklik "Satılan Araç (2.El) Sayısı" ve ilgili filo akış kalemleri. İki veri türü ayrı satırlar halinde tutulur:

- `katilimci_ham_veri`: sadece ankete/araştırmaya doğrudan katılan firmaların gerçek toplam rakamları (sektörün tamamını temsil etmez, alt sınır niteliğindedir).
- `sektor_tahmini`: NielsenIQ'nun katılımcı verisinden tüm sektöre ekstrapole ettiği tahmini rakam (ana kullanılabilir seri budur).

Bulunan iki çeyrek: **2025 Ç2** (satılan araç 2.el = 18.500 adet, sektör tahmini) ve **2026 Ç1** (17.500 adet). Ara çeyrekler (2025 Ç3, Ç4) için aynı formatta bir infografik bu turda web'de bulunamadı; dergi Sayı 143 ve 145 sadece kısa dönem (günlük) raporuna odaklanmış görünüyor — bu ay/çeyrekleri **bilerek boş bıraktık**, uydurmadık.

### `tokkder_gunluk_kisa_donem_filo_cikis_ceyreklik.csv`

Kısa dönem (günlük) kiralama sektörünün çeyreklik "Toplam Filo Çıkış" adedi, filo büyüklüğü, ortalama araç yaşı, doluluk oranı ve kontrat verileri. Bu rapor serisi TOKKDER tarafından **ilk kez 2025 1. çeyrek verileriyle** (Temmuz-Ağustos 2025 sayısında) yayımlandı — öncesi için bu formatta veri yoktur ve TOKKDER'in kendisi de bunu "Türkiye günlük kiralama sektörüne ilişkin ilk ve tek geniş kapsamlı pazar araştırması" olarak tanımlıyor.

En dikkat çekici satır **2025 Ç3**: `toplam_filo_cikis_000 = 23.4` (23.400 araç filodan çıktı) ve `ortalama_arac_yasi_ay = 19` — yani rapora katılan günlük kiralama firmalarının filolarındaki araçların ortalama yaşı 19 ay. Bu ikinci rakam, aylık/çeyreklik zaman serisi hâlinde takip edilebilirse "araçlar ne kadar hızlı elden çıkıyor" sorusuna dolaylı ama düzenli yayımlanan bir yanıt verir.

## Metodoloji notları / kırılmalar

- Kısa dönem (günlük) rapor serisi 2025 Ç1'de başladı; **2024 ve öncesi için bu segmentte hiç veri yok.**
- Operasyonel kiralama raporu çok daha eski (dergi arşivinde en az 2018'e kadar gidiyor, `data/tokkder` klasörü bu turda sadece "Satılan Araç (2.El)" kalemi net biçimde tablo halinde bulunan iki çeyreği içeriyor; geçmiş çeyrekler için dergi arşivinin taranması gerekir).
- "Sektör Tahmini" ile "Katılımcılar" (ham anket) rakamları karıştırılmamalı — sektör tahmini NielsenIQ'nun ekstrapolasyonudur, katılımcı verisi ise anket kapsamındaki firmaların ham toplamıdır (genelde sektörün ~%70-75'i).
- 2026 Ç1 sayısında günlük kiralama segmenti için "27,9 milyar TL çeyreklik araç yatırımı" rakamı operasyonel kiralama segmentiyle birebir aynı basılmış; bu satırda kasıtlı olarak **boş bırakıldı** çünkü kaynakta bu çakışmanın gerçek mi yoksa dergi metnindeki bir tekrar mı olduğu doğrulanamadı (bkz. CSV'deki `not` sütunu).
- Aylık veri YOK — TOKKDER bu raporları yalnızca **çeyreklik** yayımlıyor. Model için ay bazlı bir seri gerekiyorsa bu kaynak ancak çeyreklik forward-fill/interpolasyon ile ay serisine indirgenebilir; ham veri çeyrekliktir ve öyle kalmalıdır.

## Doğrulanmış birincil kaynaklar

- https://tokkder.org/wp-content/uploads/2025/08/filoverac141.pdf (filoverentacar, Sayı 141, Temmuz-Ağustos 2025) — sayfa 8: 2025 Ç1 günlük kiralama sektör tahmini.
- https://tokkder.org/wp-content/uploads/2025/12/filoverac143.pdf (filoverentacar, Sayı 143, Kasım-Aralık 2025) — sayfa 8 ve 10: 2025 Ç3 günlük kiralama sektör tahmini + Ç2/Ç3 metinsel karşılaştırma + çeyreklik filo/yatırım grafikleri (2024 Ç4 – 2025 Ç3).
- https://tokkder.org/wp-content/uploads/2025/11/filoverac142-DERGI-WEB.pdf (filoverentacar, Sayı 142, Eylül-Ekim 2025) — sayfa 8: 2025 Ç2 operasyonel kiralama sektör tahmini + katılımcı büyüklük dağılımı.
- https://tokkder.org/wp-content/uploads/2026/06/filoverac146.pdf (filoverentacar, Sayı 146, Mayıs-Haziran 2026) — sayfa 7 ve 10: 2026 Ç1 operasyonel + günlük kiralama özet rakamları.
- https://tokkder.org/wp-content/uploads/2024/10/TOKKDER-Operasyonel-Kiralama-Sektor-Raporu-Sunumu_2025-1.Yariyil-sonu_v1.0.pdf — TOKKDER-NielsenIQ ortak sunumu, 2025 Ç2 operasyonel kiralama için katılımcı + sektör tahmini kırılımını ayrı ayrı veren orijinal slayt (dergideki tabloyu doğrulamak için kullanıldı).
- Doğrulayıcı ikincil kaynak: https://www.log.com.tr/arac-kiralama-sektorunde-bu-yil-simdiye-kadar-986-milyar-tl-tutarinda-arac-alimi-yapildi (10 Kasım 2025 haberi) — 2025 Ç3 günlük kiralama "ortalama araç yaşı 19 ay" rakamını TOKKDER raporundan bağımsız olarak teyit ediyor.

## Bu turda bulunamayan / denenip sonuçsuz kalan

- `tokkder.org/tokkder-dergi/tag/filo-arac-satisi` etiket sayfası — sadece 2010 tarihli alakasız bir haber döndürdü.
- `tokkder.org/tokkder-dergi/5956` (2026 Ç1 operasyonel kiralama haber sayfası, HTML) ve `.../3139` (2024 1. yarıyıl haber sayfası) — filo yaşı/elden çıkarma detayı içermiyor, yalnızca toplam filo büyüklüğü ve yatırım tutarı veriyor.
- `filoverac140.pdf` (Mayıs-Haziran 2025, Sayı 140) — ARAŞTIRMA bölümü bu turda taranan sayfalarda (1-16) bulunamadı; muhtemelen derginin başka bir sayfasında veya bu sayıda hiç çeyreklik sektör tahmini yayımlanmamış olabilir.
- `filoverac145.pdf` (Mart-Nisan 2026, Sayı 145; 2025 Ç4/yıl sonu verisini içermesi beklenir) — dosya boyutu WebFetch limitini aştığı için bu turda içeriği okunamadı; sonraki bir turda tekrar denenebilir.
- OYDER'in TOKKDER rapor arşivi (`oyder-tr.org/raporlar/3`) — 2022-2023 dönemi operasyonel kiralama raporlarının başlıklarını listeliyor ama sayfa içeriğinde indirme linkleri WebFetch özetinde görünmedi; ham HTML üzerinden linkler ayrıca çekilmeli.
