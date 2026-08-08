# PM Raporu — Öncü Bilgi Adayı Masa Başı Taraması

**Tarih:** 2026-08-08

**Aşama:** Model 11 sonrası Seçenek 2 / masa başı kapsam araştırması

**Durum:** Tamamlandı; veri erişimi ve modelleme başlamadı

**Karar yöneticisi:** Pusula

**Uygulayıcı:** Rota-2

## 1. Ne Yapıldı

Pusula, kullanıcının “projeye devam edeceğiz” talimatı üzerine hedefi kapatma
seçeneğini dışladı ve bağlayıcı hedef/sınıf sözleşmesini değiştirecek kanıt
bulunmadığı için **Seçenek 2'yi** seçti. Bunun ardından karar notebookundaki
`mevcut_temsilde_var=False` boşluklardan üçü masa başında tarandı:

1. BDDK haftalık taşıt kredisi bakiyesi ve değişimi — finansmana fiili erişim/
   kullanım vekili.
2. BETAM–sahibindex ilan arzı, kapatılan ilan ve ilan yaşı — ilan arzı/stok/yaş
   ve dönüşüm vekili.
3. Google Trends araç-alım arama ilgisi — gerçek zamanlı işlem niyeti vekili.

Yalnız kamuya açık dokümantasyon ve yayın sayfaları okundu. Veri indirilmedi,
scraping/API yapılmadı, model fit edilmedi, mevcut Model 09/10/11 çıktıları
değiştirilmedi ve kilitli test açılmadı. Ayrıntılı kartlar
`data/processed/raporlar/oncu_bilgi_aday_kartlari.md` dosyasındadır.

## 2. Sayısal Özet

- İncelenen aday: **3**
- Gerçek `False` boşlukla eşleşen aday: **3/3**
- Koşullu olarak erişim fizibilitesine taşınan: **1/3** — BDDK
- Mevcut rolling-origin protokolü için elenen: **2/3**
- Veri indirme/API/scraping: **0**
- Yeni feature/model fit/permutasyon/bootstrap: **0**
- Kilitli test erişimi: **0**
- Hedef/sınıf/ufuk/band/K değişikliği: **0**
- Kullanıcıya ait dirty/untracked dosyada değişiklik: **0**

| Aday | Tarihsel kapsam | M−2 erişimi | Vintaj riski | Ön hüküm |
|---|---|---|---|---|
| BDDK taşıt kredisi | Ocak 2014–bugün, haftalık | Takvim düzeyinde evet | Orta–yüksek | Koşullu devam |
| BETAM–sahibindex | İlk aylık yayın Aralık 2023; ilk raporda üç yıl backfill | Cari kullanımda muhtemelen evet | Yüksek | Elendi |
| Google Trends | UI 2004'e uzanabilir; tutarlı API 1.800 gün | Cari kullanımda evet | Çok yüksek | Elendi |

## 3. Karşılaşılan Sorunlar (Saklanmaz)

1. **BDDK bakiye, onay değildir.** Seri yeni bilgi ailesindedir fakat kredi
   başvuru/onay oranını değil, kullandırım ve geri ödemelerin net etkisini taşıyan
   stok değişimini ölçer. “Finansmana fiili erişim” için kusursuz değil, vekildir.
2. **BDDK revizyonu.** Kurum dönemsel bilgilerin takip eden yayınlarda
   değişebileceğini açıklar. Güncel tarihsel dosya tek başına as-of uyumlu kabul
   edilemez; ilk-yayım vintajı veya revizyon büyüklüğü sınanmalıdır.
3. **Yayın gecikmesi alanı.** BDDK kesin yayın takvimi sunuyor; ancak referans
   haftasıyla yayın satırının birebir eşlemesi veri indirilmeden doğrulanmadı.
   Kart bu alanı dürüstçe “doğrulanmadı” bırakır.
4. **BETAM geriye doldurma.** Aralık 2023 ilk raporu geçmiş üç yılı ele alır;
   bunlar 2020–2023 döneminde gerçekten yayımlanmış vintajlar değildir.
5. **Google Trends yeniden üretilebilirliği.** UI örnekleme, gürültü ve her sorgu
   penceresinde yeniden ölçekleme uygular. Alpha API tutarlı ölçek sunsa da erişim
   sınırlı ve pencere yaklaşık beş yıldır.
6. **Kaynak kapsamı kasıtlı dar tutuldu.** Token ve kapsam maliyeti nedeniyle üç
   adayın dışına çıkılmadı; zorla dördüncü aday üretilmedi.
7. **Çalışma ağacı kirli.** Dört değiştirilmiş notebook ve birkaç untracked dosya
   kullanıcı çalışması olarak korundu; okunması gereken karar notebooku dışında
   hiçbirine yazılmadı ve commit kapsamına alınmayacaktır.

## 4. Veri Örneği (Ham, İlk/Son Birkaç Satır)

Bu aşamada veri çekilmediği için ham veri satırı yoktur. Denetim için kaynak
sayfalarında gözlenen ilk/son **yayın kayıtları** aşağıdadır; bunlar model girdisi
değildir:

```text
BETAM ilk yayın kaydı:  Aralık 2023 raporu → Kasım 2023 piyasa görünümü
BETAM güncel örnek:     Temmuz 2026 raporu → ilan sayısı, kapatılan ilan,
                        satılan/satılık oranı ve ilanda kalma süresi
BDDK kapsam başlangıcı: Ocak 2014 → haftalık seri (metaveri beyanı)
BDDK güncel tablo alanı: Haftalık Bülten → Tüketici Kredileri → Taşıt
Google API kapsamı:     Kayan 1.800 gün; günlük/haftalık/aylık/yıllık
```

Bu bölümde sayısal gözlem kopyalanmaması bilinçlidir: Pusula bu aşamada veri
indirmeyi ve seri çıkarmayı açıkça yasakladı.

## 5. Varsayımlar ve Kararlar (K/N Kararlarına Uygunluk)

- Target `noter_devir_otomobil_adet` olarak kaldı.
- Sınıflar `down / stable / up`, stable bandı ±%5 olarak kaldı.
- Haftalık güncellenen cari-ay nowcast sözleşmesi değişmedi.
- Target lagları, iki aylık embargo ve kilitli test sınırı değişmedi.
- BDDK taşıt kredisi, mevcut faiz feature'ının başka dönüşümü sayılmadı: biri
  kredi fiyatını, diğeri gerçekleşmiş bakiye kullanımını ölçer.
- BDDK “geçti” ilan edilmedi; yalnız erişim/vintaj fizibilitesine taşınabilecek
  tek aday olarak işaretlendi.
- BETAM ve Google Trends ekonomik açıdan anlamsız ilan edilmedi; yalnız mevcut
  geriye dönük as-of değerlendirme sözleşmesine uygun bulunmadı.
- Oracle tavan kapısı değişmedi: gözlenen tavan kendi permütasyon `null95`
  düzeyini en az **0,15** aşmadan rolling-origin model kıyasına geçilemez.
- Test `2025-07..2026-06` açılmadı.

## 6. Açık Sorular / PM Onayı Gerekenler

Bir sonraki aşama gerçek veri erişimi içerdiği için kullanıcı onayı gerektirir.
Önerilen kapsam yalnız BDDK adayıdır. Onay verilirse şu sorular cevaplanacaktır:

1. Gelişmiş gösterim veya tarihli bültenler ilk-yayım vintajlarını koruyor mu?
2. Kesin referans haftası–yayın zamanı eşleşmesi nedir?
3. Taşıt kredisi bakiye serisinde kapsam/kırılma/revizyon olayları var mı?
4. Ücretsiz ve hukuken uygun, makinece tekrarlanabilir erişim yolu nedir?
5. Bakiye değişiminin nominal büyümeden ayrılması için hangi ön-kayıtlı dönüşüm
   seti en küçük ve ekonomik olarak savunulabilir olur?

Bu sorular yanıtlanmadan veri seti, feature veya model üretimi başlamamalıdır.

## 7. Önerilen Sonraki Adım

Kullanıcı onayından sonra yalnız **BDDK erişim ve vintaj fizibilitesi** adlı küçük
bir aşama başlatılsın. Aşama veri setini modele bağlamasın; yalnız kaynak dosya/
endpoint envanteri, ilk-yayım korunumu, yayın gecikmesi, tarih kapsamı ve örnek
beş tarihte revizyon karşılaştırması üretsin. As-of kapısı geçmezse aday elensin;
geçerse ayrı bir ön-kayıtla feature üretimi ve oracle tavan testi önerilsin.
