---
faz_no: 10
faz_adi: "Aşama B Nowcast Kapanış Sentezi ve Karar Paketi"
tarih: 2026-08-06
kapsam_ozeti: "K10 aylık yön nowcast'inin Model 09-11 kanıt zinciri, negatif bulgu ve kullanıcı karar seçenekleri"
bagimli_oldugu_fazlar: [09]
bagimli_model_asamalari: [09, 10, 11]
durum: inceleniyor
hedef_kaynak_sayisi: 3
gerceklesen_kaynak_sayisi: 3
kaynak_arac: "Claude Code (Pusula karar ve performans yönetimi; Rota uygulama)"
son_guncelleme: 2026-08-06
---

# Aşama B — Aylık Nowcast Kapanış Sentezi

## Yönetici sonucu

Pusula'nın resmî hükmü:

> Mevcut etiket-lag durumları ve Model 09 feature temsilleri altında, iki ay
> bilgi gecikmeli aylık `up/stable/down` noter otomobil devir yönünde
> saptanabilir öngörü becerisi yoktur.

Bu, “araç piyasası hiçbir veriyle tahmin edilemez” hükmü değildir. Yalnız
`2019-01..2025-04` geliştirme penceresi, `noter_devir_otomobil_adet`, ana ±%5
stable bandı, mevcut kamuya açık DF-A feature'ları ve K10 bilgi gecikmesi için
geçerlidir. Kilitli `2025-07..2026-06` test dönemi hiç açılmamıştır.

### Projeye uygulanabilirlik

Mevcut feature/model hattı üretime terfi ettirilmemelidir. Yeni algoritma
denemek aynı bilgi kümesindeki sorunu çözmez; bir sonraki hamle bağlayıcı ürün
kararıdır.

## Kanıt zinciri

### 1. Validation geçidi — Model 09

12 aylık validation bloğunda en iyi naif kural `M-2 persistence` oldu
(MCC=0,110; macro-F1=0,415). Dört düşük kapasiteli modelin en iyisi sığ Random
Forest'tı (MCC=0,037; macro-F1=0,189) ve terfi kapısını geçemedi. Hafta 1→4
skorları monoton değildi.

Bu aşama tek başına nihai hüküm için yetersizdi; yalnız 12 bağımsız ay vardı.

### 2. Rolling-origin ölçüm — Model 10

50 test-dışı origin, her origin'de iki ay embargo ve yeniden fit ile ölçüldü.
Birincil belirsizlik hesabı 2.000 ortak indeksli dört aylık hareketli-blok
bootstrap'tı.

| Yaklaşım | MCC | Blok %95 GA |
|---|---:|---:|
| M-2 persistence | 0,0165 | -0,1464 .. 0,2344 |
| Seasonal t-12 | 0,0141 | -0,1375 .. 0,2416 |
| En iyi model noktası, lojistik C=1 | -0,0306 | -0,1954 .. 0,1385 |
| Sığ Random Forest | -0,1193 | -0,2428 .. 0,0864 |

Dört modelin persistence karşısındaki ΔMCC ve macro-F1 farkları negatiftir;
Holm reddi yoktur, yıllık jackknife koşulu sağlanmamıştır. ΔMCC güven aralığı
yarı genişlikleri 0,21–0,28 olduğundan küçük farkları ayırma gücü yoktur.

### 3. Hedef ve bilgi tavanı — Model 11

#### Etiket rejimi

Genişleyen çoğunluk MCC=-0,070 iken son-12-ay ve son-6-ay çoğunlukları
sırasıyla 0,063 ve 0,065'tir. Bayat önsel mekanizması yönsel olarak tutarlıdır;
ancak genişleyen modal sınıf yalnız üç kez değişmiş ve tüm aralıklar sıfırı
içermiştir. Bulgu kurulmuş değil, gürültü olabilir.

Önceden kaynaklandırılan üç dış kırılma serbest tarih taraması yapılmadan
ölçüldü: WHO'nun Mart 2020 pandemi nitelemesi, Aralık 2021 kur korumalı
mevduat başlangıcı ve Şubat 2023 Kahramanmaraş depremleri. Hiçbiri Holm sonrası
anlamlı değildir. En büyük etki Şubat 2023'tedir (V=0,290; ham p=0,046;
Holm-düzeltilmiş p=0,138). Kaynaklar: [WHO pandemi basın konferansı](https://www.who.int/docs/default-source/coronaviruse/transcripts/who-audio-emergencies-coronavirus-press-conference-full-and-final-11mar2020.pdf),
[TCMB 2021 Faaliyet Raporu](https://www3.tcmb.gov.tr/yillikrapor/2021/tr/m-2-4.html),
[AFAD Kahramanmaraş basın bülteni](https://www.afad.gov.tr/kahramanmarasta-meydana-gelen-depremler-hkbasin-bulteni22).

#### Lag ve stable bandı

Geçiş bağımsızlığı permütasyon p=0,845; Cramér's V=0,098'dir. Lag 1/2/3/12
ilişkilerinin hiçbiri Holm sonrası anlamlı değildir. Operasyonel olmayan lag-1
persistence bile MCC=-0,020 ve %95 GA `[-0,262; 0,154]` üretmiştir. Dolayısıyla
yalnız iki aylık bilgi gecikmesini kaldırmanın yapıyı ortaya çıkaracağına dair
kanıt yoktur.

Ön-kayıtlı ±2,5 / ±3,5 / ±5 / ±7,5 / ±10 bantlarının hiçbirinde ana banda
göre ≥0,10 ve CI altı >0 persistence artışı yoktur. Stable payları %6,6–%38,2;
hiçbiri %60 yorumlanamazlık sınırını aşmaz. Ana ±%5 bandı değiştirilmemiştir.

±%10 bandında seasonal M-12 MCC=0,158 gözlenmiştir; maddi-fark kapısı
ön-kayıtta yalnız persistence için tanımlandığından bu post-hoc sayı aday veya
karar gerekçesi değildir.

#### Oracle tavanı

Oracle'lar değerlendirme aylarının gerçeğiyle bilerek in-sample fit edildi;
bu nedenle yalnız kendi permütasyon ezber null'larıyla karşılaştırıldı.

| Oracle | Gözlenen MCC | Permütasyon null95 |
|---|---:|---:|
| S1: y(M-2) durumu | 0,170 | 0,287 |
| S2: y(M-2) × M-3 stable durumu | 0,238 | 0,343 |
| Lojistik L2 C=0,1 | 0,215 | 0,445 |
| Lojistik L2 C=1 | 0,169 | 0,468 |
| Sığ Random Forest | 0,917 | 0,916 |
| Sığ HistGradientBoosting | 1,000 | 1,000 |

RF'nin 0,0013'lük null aşımı, ön-kayıtlı “modelleme alanı” marjı 0,15'in çok
altındadır. HGB gerçek ve karıştırılmış etiketi aynı mükemmellikle ezberler.
Yüksek in-sample skorlar bilgi değil, kapasite/ezber artefaktıdır.

### Projeye uygulanabilirlik

Sorun yalnız model seçimi değildir. Mevcut temsilin permütasyon null'ını aşan
bilgi tavanı gösterilememiştir. Aynı feature'larla beşinci algoritmayı denemek
kanıt zinciriyle uyumsuzdur.

## Ön-kayıt düzeltmesi

İlk hüküm şemasında A “hiçbir oracle null95'i aşmaz”, C ise “en az 0,15 marjla
aşar” olarak yazılmış ve `(0; 0,15)` aralığında mantıksal boşluk bırakılmıştı.
Pusula bu kusuru sonuç lehine değil, C'nin tümleyeni olacak biçimde kapattı:
hiçbir oracle ≥0,15 marj sağlamıyorsa diğer A koşullarıyla A ateşlenir. Bu
düzeltme prompt arşivinde görünürdür ve negatif hükme yol açmıştır.

## Kullanıcı karar paketi

Bu seçeneklerin hiçbiri uygulanmamıştır.

1. **Projeyi bu hedef için kapat:** Negatif bulguyu Aşama B'nin nihai çıktısı
   olarak kabul et. Ek veri/model maliyeti yoktur.
2. **Bilgi kümesini değiştir:** Gerçek haftalık taşıt kredisi faizi,
   ilan/stok/arama-talep gibi daha yakın araç-piyasası sinyalleri için yeni
   veri araştırması başlat. Target ve üç sınıf korunabilir; kapsam/K kararıdır.
3. **Hedef spesifikasyonunu değiştir:** Band değil, ufuk/toplulaştırma veya
   sınıf sayısını yeniden değerlendir; örneğin üç aylık yön ya da iki sınıf.
   Kullanıcının sabit tuttuğu amaçla çeliştiği için açık bağlayıcı karar olmadan
   uygulanamaz.

## Açık Sorular / Literatürde Net Olmayanlar

- Daha zengin, araç-piyasasına yakın bir bilgi temsili oracle tavanını aşar mı?
  Mevcut veride yanıtlanamaz.
- Aylık target'ın etkin yayın gecikmesi kaynak bazında gerçekten iki ay mıdır?
  Tarihsel yayın günü kaydı yoktur; K10 muhafazakâr lag2 kullanır.
- Üç aylık ufuk veya iki sınıf daha öngörülebilir midir? Ölçülmedi; mevcut
  sonuçlardan türetilemez.

## Kalite kontrolü

- [x] Target ve ana üç sınıf değiştirilmedi.
- [x] Test dönemi açılmadı.
- [x] Negatif bulgu ve ölçüm gücü sınırı birlikte yazıldı.
- [x] Post-hoc seasonal sayı terfi ettirilmedi.
- [x] Dış kırılma iddiaları kaynaklandırıldı.
- [x] Yeni K maddesi yazılmadı.
- [x] Promptlar 34–36 arşivlendi.
- [ ] Proje sahibi gözden geçirmesi bekleniyor.

## Kaynakça ve denetim izi

- `data/processed/raporlar/pm_rapor_nowcast_baseline_ve_dusuk_kapasite.md`
- `data/processed/raporlar/pm_rapor_nowcast_rolling_origin.md`
- `data/processed/raporlar/pm_rapor_model11_hedef_bilgi_tavani.md`
- `prompts/veri/34_nowcast_baseline_ve_asof_prompt.md`
- `prompts/veri/35_nowcast_rolling_origin_prompt.md`
- `prompts/veri/36_model11_hedef_bilgi_tavani_onkayit.md`
