# PM Raporu — Nowcast Baseline ve Düşük Kapasite Geçidi

## 1. Ne Yapıldı

- Yalnız kilitlenmemiş `2024-05..2025-04` validation penceresinde train
  çoğunluğu, bilgi-anına uygun `M-2 persistence` ve seasonal `t-12`
  baseline'ları ölçüldü. Taslak test penceresi açılmadı.
- Gerçek günlük EVDS EUR/TRY ve yürürlük-tarihli ÖTV olayları snapshot'a
  eklendi. Aylık ortalama taşıt kredisi/politika faizleri yalnız `lag2`
  kullanıldı; cari ay ve `lag1` reddedildi.
- Önceden sınırlanmış 10 feature ile dört düşük-kapasiteli aday denendi:
  iki L2 lojistik regresyon, sığ Random Forest ve sığ Histogram Gradient
  Boosting. Geniş arama yapılmadı.
- Genel validation ay-eşit snapshot ağırlıklarıyla, hafta sırası 1–4 ise
  her sırada aynı 12 ayla ölçüldü.

## 2. Sayısal Özet

Etkin train N=62 ay, validation N=12 ay; validation'da 52 haftalık tahmin
anı vardır fakat bunlar 52 bağımsız target değildir.

| Yaklaşım | MCC | Macro-F1 | Accuracy |
|---|---:|---:|---:|
| Train çoğunluğu | 0,000 | 0,222 | 0,500 |
| Persistence M-2 | **0,110** | **0,415** | 0,417 |
| Seasonal t-12 | -0,045 | 0,250 | 0,250 |
| Lojistik L2, C=0,1 | 0,000 | 0,095 | 0,167 |
| Lojistik L2, C=1 | 0,000 | 0,095 | 0,167 |
| Sığ Random Forest | **0,037** | **0,189** | 0,225 |
| Sığ HistGradientBoosting | -0,035 | 0,284 | 0,375 |

En iyi model adayı sığ Random Forest'tır; hem MCC hem macro-F1'da en iyi
baseline'ı geçemediği için **terfi etmedi**. Bu bir validation bulgusudur,
test sonucu veya genellenebilir performans iddiası değildir.

Kazanan adayın hafta 1→4 MCC değerleri sırasıyla `-0,099 / 0,182 / 0,000 /
0,182` oldu. Monoton iyileşme yoktur; mevcut sinyallerle haftalık kadansın
düzenli ek bilgi taşıdığı doğrulanmadı.

## 3. Karşılaşılan Sorunlar (saklanmaz)

1. Validation yalnız 12 bağımsız aydır; tek ay skorları belirgin oynatabilir.
2. EUR/TRY, USD/TRY ile yüksek ortak hareket edebilir; eklenmesi bağımsız
   bilgi kazanımı garantilemez.
3. ÖTV serisi 2015–2026 arasında yalnız 11 olaydır; seyrektir.
4. Faiz verisi doğal haftalık/günlük frekanstan yerelde aylık ortalamaya
   indirgenmiştir. Bu aşamada yüksek frekanslı faiz sinyali gibi sunulmadı.
5. İlk hafta bazı aylarda kur gözlemi olmadan gelebilir; eksikler yalnız
   train medyanıyla dolduruldu.
6. Model aramasını genişletmek mevcut validation'a uyum riskini artırır;
   negatif sonuç nedeniyle arama durduruldu.

## 4. Veri Örneği (ham, ilk/son birkaç satır)

Validation snapshot'ından seçili sütunlar:

| kesit | hedef ay | hafta | etiket | ağırlık | USD ay-içi % | EUR ay-içi % | ÖTV olay sayısı | taşıt faizi lag2 |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 2024-05-05 | 2024-05 | 1 | up | 0,25 | 0,033 | -0,045 | 0 | 42,302 |
| 2024-05-12 | 2024-05 | 2 | up | 0,25 | -0,409 | -0,259 | 0 | 42,302 |
| 2024-05-19 | 2024-05 | 3 | up | 0,25 | -0,470 | 0,980 | 0 | 42,302 |
| 2025-04-13 | 2025-04 | 2 | up | 0,25 | 0,262 | 2,730 | 0 | 39,975 |
| 2025-04-20 | 2025-04 | 3 | up | 0,25 | 0,782 | 6,296 | 0 | 39,975 |
| 2025-04-27 | 2025-04 | 4 | up | 0,25 | 1,227 | 6,838 | 0 | 39,975 |

## 5. Varsayımlar ve Kararlar (K/N kararlarına uygunluk)

- Target, `up/stable/down`, ±%5 stable bandı ve cari ay-sonu nowcast tanımı
  K10'a uygun ve değişmedi.
- Tahmin pazartesi; bilgi kesimi önceki pazardır. Günlük/olay feature'ları
  kesim sonrası veri kullanmaz.
- Aylık target `lag2/3/12/13`, aylık kovaryatlar en az `lag2` kullanır.
- Aynı ayın snapshot ağırlıkları toplamı 1'dir; split ay bazındadır.
- EUR/TRY kaynak kodları `TP.DK.EUR.A/S` ve veri tarihleri yerel EVDS
  arşivinden gelir. ÖTV feature'ı `genisletme_4_otv_olaylari.py` içindeki
  kaynaklandırılmış yürürlük tarihlerini kullanır.
- Pusula'nın test açmama ve aday sayısını sınırlama kararlarına uyuldu.

## 6. Açık Sorular / PM Onayı Gerekenler

- Test penceresi hâlâ kilitli değildir ve hiç açılmamıştır.
- Mevcut feature ailesi terfi edemedi. Aynı validation üzerinde yeni
  algoritmalar denemek profesyonel bir sonraki adım değildir.
- Gerçek haftalık taşıt kredisi faizi, ilan akışı/stok ve arama-talep gibi
  daha yakın piyasa sinyalleri mevcut repoda yoktur.

## 7. Önerilen Sonraki Adım (başlatılmaz, yalnızca önerilir)

Model ailesini genişletmek yerine veri katmanına gerçek haftalık taşıt
kredisi faizi ve en az bir araç-piyasasına özgü akış/talep sinyali eklenmesi;
ardından aynı dört-adaylı protokolün yeni bir validation tasarımında veya
rolling-origin duyarlılık analizinde tekrarlanması önerilir. Yeni bilgi
gelmeden test açılmamalıdır.
