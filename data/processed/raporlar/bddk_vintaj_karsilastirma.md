# BDDK Haftalık Taşıt Kredisi — Erişim ve Vintaj Karşılaştırması

**İnceleme tarihi:** 2026-08-08

**Ön-kayıt:** `prompts/veri/39_bddk_erisim_vintaj_onkayit.md`

**Sonuç:** **KALDI**

## 1. Kararın kısa gerekçesi

BDDK'nın gelişmiş gösterim uç noktası, tüketici taşıt kredilerinin toplam
bakiye serisini 3 Ocak 2014–31 Temmuz 2026 arasında **657 haftalık gözlem**
olarak ücretsiz ve kimliksiz sunmaktadır. Ön-kayıtlı beş referans haftanın
güncel değerleri de alınabilmiştir.

Ancak canlı tarihsel seri ilk-yayım vintajı değildir. BDDK'nın Haftalık Bülten
yayın sayfası canlı bülten, metaveri, yayın takvimi, revizyon politikası ve
revizyon takvimine bağlantı verir; eski haftaların ilk yayımlandığı PDF/Excel
dosyalarını veya sürümlenmiş tablolarını sunan bir arşiv bağlantısı bulunamamıştır.
BDDK ayrıca geçmiş dönem değerlerinin takip eden yayınlarda revize
edilebileceğini açıklar.

Bu nedenle ilk dört tarihin ilk-yayım değeri yeniden kurulamadı. En güncel
31 Temmuz 2026 haftası, 6 Ağustos 2026 yayınından iki gün sonra canlı tabloda
gözlendiği için yalnız bu tarih ilk-yayıma yakın vintaj olarak kaydedildi.
Vintaj erişimi **1/5** ve zorunlu ilk tarih erişimi yoktur. Ön-kayıtlı `KALDI`
kapısı iki ayrı nedenle ateşlenmiştir.

## 2. Ön-kayıtlı beş tarih

Tüm tutarlar BDDK tablosunun birimiyle **milyon TL**, kapsam “Sektör / Tüketici
Kredileri / b) Taşıt / Toplam”dır.

| No | Referans hafta | Seçim nedeni | Güncel seri değeri | İlk-yayım vintajı | Yayın tarihi | Gecikme (gün) | Mutlak delta | Yüzde delta | Durum |
|---:|---|---|---:|---|---|---:|---:|---:|---|
| 1 | 2014-01-03 | Metaverideki başlangıç sınırının ilk haftası | 8.613,848 | `vintaj_erisilemedi` | Doğrulanmadı | — | — | — | Başlangıç vintajı yok |
| 2 | 2019-01-04 | K10 etiket penceresinin ilk yılı | 6.506,118 | `vintaj_erisilemedi` | Doğrulanmadı | — | — | — | Vintaj yok |
| 3 | 2022-01-07 | Etiket penceresinin ortanca yılı | 12.983,300 | `vintaj_erisilemedi` | Doğrulanmadı | — | — | — | Vintaj yok |
| 4 | 2025-04-25 | Model 10/11 analiz sınırının son haftası | 64.040,300 | `vintaj_erisilemedi` | Doğrulanmadı | — | — | — | Vintaj yok |
| 5 | 2026-07-31 | 2026-08-08 itibarıyla en güncel yayımlanmış hafta | 42.112,122 | 42.112,122 | 2026-08-06 | 6 | 0,000 | %0,000 | İlk-yayıma yakın canlı yakalama |

`delta_mutlak` ve `delta_yuzde`, yalnız iki değer birlikte mevcut olduğunda
hesaplandı. Eksik vintajlar güncel değerle doldurulmadı.

## 3. Kaynak ve erişim izi

### 3.1 Canlı tarihsel seri

- Sayfa: [BDDK Haftalık Bülten — Gelişmiş Gösterim](https://www.bddk.org.tr/BultenHaftalik/tr/Gelismis)
- Resmî sayfanın kullandığı ücretsiz POST uç noktası:
  `https://www.bddk.org.tr/BultenHaftalik/tr/Gelismis/KiyaslamaJsonGetir`
- Parametrelerin anlamı:
  - kalem: `1.0.5` — Tüketici Kredileri / b) Taşıt
  - para: `TRY`
  - sütun: `3` — Toplam
  - taraf: `10001` — Sektör
  - başlangıç/bitiş: `03.01.2014` / `31.07.2026`
- Dönen gözlem: 657 hafta.
- Erişim: ücretsiz, kimliksiz, resmî BDDK alan adı.

Bu uç nokta **bugünkü tarihsel görünümü** verir. Sorgu tarihi parametresi eski
bir origin seçse de sunucu eski ilk-yayım sürümünü değil canlı veritabanındaki
geçmiş değeri döndürdüğü için vintaj kaynağı sayılmadı.

### 3.2 Tarih ve kapsam kanıtı

- [Haftalık Bülten ana sayfası](https://www.bddk.org.tr/Veri/Detay/158)
- [Haftalık Bülten metaverisi](https://www.bddk.org.tr/BultenDosyalari/Home/Index/Haftalik-MetaVeri)
- [Veri yayımlama takvimi](https://www.bddk.org.tr/Veri/Detay/71)
- [Haftalık Bülten revizyon politikası](https://www.bddk.org.tr/BultenDosyalari/Home/Index/Haftalik-RevizyonPolitikas%C4%B1)
- [Haftalık Bülten revizyon takvimi](https://www.bddk.org.tr/BultenDosyalari/Home/Index/Haftalik-RevizyonTakvimi)
- [BDDK veri yayınları SSS](https://www.bddk.org.tr/Sss/Liste/110)

Ana sayfadaki resmî bağlantı envanterinde tarihli ilk-yayım PDF/Excel arşivi
bulunmadı. Bu yokluk, internette hiçbir kopya bulunmadığı iddiası değildir;
ön-kayıt gereği yalnız BDDK'nın kendi bağlantı hiyerarşisi taranmıştır.

## 4. Erişim bütçesi

Ön-kayıtlı üst sınır tamamen kullanıldı:

- Resmî sayfa/HTTP erişimi: **15/15**
- BDDK dışı kaynak: **0**
- Ücretli/kimlikli uç nokta: **0**
- Toplu crawling/scraping döngüsü: **0**
- Ek, sonuç-seçilmiş tarih: **0**

İki erişim yerel HTML/regex ayrıştırma hatası nedeniyle sonuç üretmedi; bunlar
bütçeden düşülmedi değil, **erişim olarak sayıldı**. Bütçe 15'e ulaştığında
araştırma durduruldu.

## 5. Ön-kayıt karar kapısı denetimi

| Kapı | Gözlenen | Sonuç |
|---|---:|---|
| Vintaj erişimi | 1/5 | `KALDI` — çoğunlukta `<3/5` |
| İlk tarih vintajı | Erişilemedi | `KALDI` — zorunlu ilk tarih yok |
| En güncel tarih vintajı | Erişildi | Tek başına yeterli değil |
| Güncel seri erişimi | 5/5; tam seri 657 hafta | Erişim kapısı geçti |
| Ölçülebilir revizyon deltası | Yalnız 1 tarih; %0 | Genellenemez |
| Tarihsel yayın gecikmesi | 1/5 doğrulandı | Gecikme kapısı geçmedi |
| Ücretsiz/kimliksiz erişim | Evet | Erişim maliyeti kapısı geçti |

Nihai hüküm: **KALDI — mevcut resmî BDDK web yayınıyla geçmiş ilk-yayım
vintajları as-of uyumlu rolling-origin değerlendirme için yeniden kurulamaz.**

Bu hüküm taşıt kredisi bakiyesinin ekonomik mekanizmasını reddetmez; yalnız
mevcut erişim biçimini model girdisi olarak reddeder.
