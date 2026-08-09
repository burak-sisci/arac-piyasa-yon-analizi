# Prompt 48 — Model 18 Prospektif İzleme Ön-Kaydı

**Tarih:** 2026-08-09  
**Karar yöneticileri:** Rota-2 + Pusula (`019fd8ad-8e18-7b4e-a6d4-3c0214efc923`, Sonnet/xhigh)  
**Tetikleyici:** Proje sahibinin “Claude token yenilendi; tekrar başlayın; model
performansını en yüksekte istiyorum” talimatı ve daha önce verdiği tam otonom
çalışma yetkisi.

## 0. Amaç ve bilimsel sınır

Model 14 `lojistik_l2_c01`, mevcut test-dışı kanıtta en iyi dengeli adaydır ancak
terfi etmemiştir. Aynı 50 origin üzerinde yeni algoritma, feature, eşik veya karar
kuralı denenmeyecektir. Model 18 yeni bir aday değildir; Model 14’ün tamamen
dondurulmuş konfigürasyonunu, gerçekleşmeden önce kaydedilen yeni bağımsız aylarda
izlemek için kurulan prospektif kanıt hattıdır.

Bu aşama bugün performans artışı iddia etmez. Amaç, gelecekte performans hakkında
güvenilir ve validation-mining’den bağımsız kanıt üretmektir.

## 1. Değişmeyen hedef ve model sözleşmesi

- Target: `noter_devir_otomobil_adet` aylık yönü.
- Sınıflar ve sıra: `down`, `stable`, `up`.
- Stable bandı: kapalı ±%5.
- Tahmin kadansı: pazartesi; bilgi kesiti önceki tamamlanmış pazar.
- Aylık feature ve target geçmişi: en az M−2.
- Final model: `LogisticRegression(C=0.1, penalty="l2", solver="lbfgs",
  max_iter=2000, class_weight="balanced", random_state=42)`.
- Ön işleme: `SimpleImputer(strategy="median", add_indicator=True)` ve ardından
  `StandardScaler`; ikisi yalnız aşağıda tanımlı eğitim kümesinde fit edilir.
- Feature listesi ve sırası, Model 14 `TEST_FEATURELAR` ile birebir aynı 14
  feature’dır; hiçbir ekleme, çıkarma veya yeniden sıralama yapılmaz.
- Olasılık kararı salt `argmax`; kalibrasyon, maliyet matrisi ve threshold yoktur.

## 2. Eğitim kümesi — kapalı ve sabit sınır

- Eğitim hedef ayı aralığı kapalı olarak `2019-01..2025-04`.
- `2025-05` ve `2025-06` embargo ayları eğitime girmez.
- Kilitli `2025-07..2026-06` test aylarının yön etiketleri hiçbir amaçla
  hesaplanmaz, okunmaz, fit edilmez veya raporlanmaz.
- Eğitim snapshot’ı, ham DF-A yalnız `2025-04-30` tarihine kadar kesildikten
  sonra Model 07’nin mevcut bilgi-zamanı kurallarıyla yeniden kurulur. Böylece
  kilitli dönem etiketleri önce üretilip sonra filtrelenmez; yapısal olarak hiç
  üretilmez.
- Eğitimde tüm haftalık snapshot’lar kullanılır; mevcut ay-eşit `agirlik`
  korunur. Feature dönüşümleri Model 14 `feature_hazirla` kod yoludur.

## 3. Gelecek tahmin satırı — etiketsiz inşa

Prospektif satır için `haftalik_snapshot_uret` ve
`ay_sonu_nowcast_etiketleri` çağrılmaz. Tek hedef ay ve tek pazar kesiti için
etiketsiz feature satırı, Model 07 ile aynı formüller kullanılarak kurulur.

Kilitli test dönemindeki ham target adetleri, gelecek ayın dondurulmuş
`lag12/lag13` feature’larını hesaplamak için kullanılabilir. Bu kullanım bir
kilitli-test performans okuması değildir: yön etiketi üretilmez, tahmin-gerçek
karşılaştırması yapılmaz ve metrik hesaplanmaz. Bu ayrım kodda assertion ve
testlerle korunur.

İlk kayıt:

- hedef ay: `2026-08`
- kavramsal kesit: `2026-08-02`
- tahmin tarihi: `2026-08-03`
- arşivleme tarihi: `2026-08-09`
- `gercek_zamanli_mi=false`; veri 2 Ağustos’ta fiziksel olarak dondurulmadığı,
  9 Ağustos’ta yerel dosyalardan yeniden kurulduğu açıkça kaydedilir.

Bu ilk kayıt hedef ay kapanmadan üretildiği için prospektif kanıta adaydır; ancak
yedi günlük arşiv gecikmesi ayrıca işaretlenir. Sonraki kayıtlar gerçek pazartesi
operasyonuna mümkün olduğunca yakın çalıştırılacaktır.

## 4. Değiştirilemez kayıt ve hash sözleşmesi

Tahmin defteri:
`data/processed/model/model_18_ileri_izleme_defteri.csv`.

- Append-only’dir; mevcut satır güncellenmez veya silinmez.
- Tekil anahtar `(hedef_ay, kesit_tarihi, konfig_hash)`.
- Aynı anahtar ve aynı içerik ikinci kez gelirse idempotent no-op.
- Aynı anahtar farklı içerikle gelirse çalışma hata vererek durur.
- `konfig_hash`: tüm sabit model/hedef/eğitim/feature sözleşmesinin kanonik
  JSON SHA-256 değeri.
- `train_veri_hash`: eğitim meta+feature+etiket+ağırlık tablosunun kanonik
  SHA-256 değeri.
- `tahmin_satiri_hash`: etiketsiz gelecek meta+feature satırının kanonik
  SHA-256 değeri.
- `prediction_hash`: hedef, kesit, olasılıklar, sınıf ve yukarıdaki hash’leri
  bağlayan kanonik SHA-256 anahtarı.

Gerçekleşme defteri:
`data/processed/model/model_18_gerceklesme_defteri.csv`.

- Tahmin defterinden ayrıdır ve append-only’dir.
- `prediction_hash` ile tek yönlü bağ kurar.
- Aynı hash ikinci kez aynı içerikle gelirse no-op, farklı içerikle gelirse hata.
- Tahmin olasılıkları ve sınıfı hiçbir zaman geriye dönük değişmez.

Her iki veri defteri K5/.gitignore gereği Git’e girmez. Kod, ön-kayıt, testler,
PM raporu ve nötr sayaç/durum bilgisi Git’e girer.

## 5. Kadans ve birincil değerlendirme birimi

- Her hedef ayda ilk dört tamamlanmış pazar kesiti birincil değerlendirmeye
  girer (`hafta_sirasi=1..4`). Beşinci pazar varsa kaydedilebilir fakat birincil
  metriğe girmez.
- Her hedef ay toplam ağırlık 1 taşır; dört haftanın her biri 1/4 ağırlıktadır.
- Bir ayın “eksiksiz” sayılması için 1–4 haftalarının dört tahmini ve tek
  gerçekleşme etiketi bulunmalıdır.
- Retrospektif 50 origin ile prospektif örneklem istatistiksel olarak
  birleştirilmez.

## 6. Peeking yasağı ve terminal eşik

- En az **12 eksiksiz yeni bağımsız hedef ay** birikmeden MCC, macro-F1,
  accuracy, sınıf metriği, delta, güven aralığı veya performans tablosu
  hesaplanmaz.
- Eşik tek ve sabittir: `N=12`; “tercihen 24” gibi sonradan esnetilebilir ikinci
  eşik yoktur.
- Terminal değerlendirme kodu N<12’de `RuntimeError` ile çalışmayı reddeder.
- README/PM yalnız nötr `N=x/12` operasyon sayacı taşıyabilir; ara performans
  sayısı veya yön yorumu taşıyamaz.
- N=12 terminal değerlendirmesinde Model 14’ün a–d kapısı yeni örneklemde
  yeniden uygulanır; referans M−2 persistence’dır. Eski 50 origin eklenmez.

## 7. Uygulama dosyaları

1. `scripts/model/model_18_ileri_izleme.py`: güvenli eğitim inşası, etiketsiz
   tek-kesit feature üretimi, fit/tahmin, hash ve tahmin defterine append.
2. `scripts/model/model_18_gerceklesme_kaydet.py`: gelecekte gerçekleşme
   değerinden etiketi hesaplayıp ayrı deftere append.
3. `scripts/model/model_18_terminal_degerlendirme.py`: N=12 sert kapılı terminal
   değerlendirme; bugün çalıştırılmaz.
4. `tests/test_model_18_ileri_izleme.py`: sözleşme ve append-only testleri.

## 8. STOP_ONLY_IF

Aşağıdakilerden biri oluşursa tahmin yazılmadan durulur:

1. Eğitim hedef ayı `2019-01..2025-04` dışına taşarsa.
2. Kilitli dönem yön etiketi üreten/okuyan bir kod yolu gerekirse.
3. Model 14 feature sırası, hiperparametre, preprocessing veya argmax kuralı
   değişirse.
4. Tahmin kesiti hedef ay kapanışından sonra ise.
5. Kesit tarihinden sonraki günlük bilgi feature satırına girerse.
6. Aynı defter anahtarı farklı içerikle yeniden yazılmak istenirse.
7. N<12 iken performans metriği üretilmek istenirse.
8. Ücretli/kimlikli kaynak, kilitli-test metriği veya bağlayıcı K/N değişikliği
   gerekirse.

## 9. Bugünkü başarı ölçütü

Bugünkü çalışma yalnız şu koşullarda başarılıdır:

- ön-kayıt uygulamadan önce commit edilmiştir;
- Model 18 kodu ve testleri geçmiştir;
- 2026-08-02 satırı etiketsiz, hash’li, append-only deftere yazılmıştır;
- hiçbir performans metriği üretilmemiştir;
- kilitli dönem yön etiketleri üretilmemiş/okunmamıştır;
- PM raporu yedi zorunlu başlıkla ve `N=0/12 tamamlanmış ay` nötr sayacıyla
  üretilmiştir.

Bu koşullar yeni model terfisi veya üretim performansı iddiası değildir.
