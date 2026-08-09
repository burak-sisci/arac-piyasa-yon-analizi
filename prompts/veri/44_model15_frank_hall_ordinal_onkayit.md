# Prompt 44 — Model 15 Frank–Hall Ordinal Tek-Aday Ön-Kaydı

**Tarih:** 2026-08-09

**Karar yöneticileri:** Rota-2 + Pusula (Sonnet/xhigh kırmızı-takım incelemesi)

**Tetikleyici:** Proje sahibinin model performansını artırmaya odaklanma ve
otonom devam talimatı. Model 14'ün en iyi adayı M−2 persistence'a karşı
ΔMCC `+0,07208694`, Δmacro-F1 `+0,00173892` ve 5/5 yıl-dışı pozitif işaret
üretti; yalnız Holm alt sınırı pozitif olmadığı için terfi etmedi. Bu ön-kayıt,
karar kaydı N11'de zaten ileri deneme olarak tanımlanan Frank & Hall ordinal
ayrıştırmasını tek adayla sınar.

## 0. Sonuç Yok / Kapsam

Bu dosya yazılırken Model 15 eğitilmez ve hiçbir Model 15 sonucu görülmez.
Model 14 feature/model/sonuçları yalnız sabit kontrol ve birleşik çoklu-test
ailesi olarak kullanılır. K9/K10 hedefi, `down/stable/up`, kapalı ±%5 bant,
M−2 bilgi disiplini, haftalık cari-ay nowcast ve kilitli test değişmez.

## 1. Veri, Origin ve Kilitli Test

- Girdi yalnız Model 07 DF-A snapshot'ıdır.
- Feature üretimi yeniden yazılmaz; doğrudan
  `model_14_mevcut_asof_feature_genisletme.feature_hazirla` ve
  `TEST_FEATURELAR` (14 sütun) import edilir.
- 50 test-dışı rolling origin: `2021-03..2025-04`; ilk train 24 ay; her
  origin'de iki ay embargo; ay-eşit ağırlık.
- Imputer ve scaler her origin'in yalnız train satırlarında fit edilir.
- `2025-07..2026-06` kilitli test çalışma başında çıkarılır; train, embargo ve
  değerlendirme aylarının tümü `2025-07` öncesi assertion'la doğrulanır.
- Bootstrap: aynı 50 ay üzerinde ortak hareketli blok, blok=4, tekrar=2.000,
  seed=420. Hafta tanısı seed=421 ve terfi ailesi dışındadır.

## 2. Tek Model Adayı

Sınıf sırası sabittir: `down < stable < up`. İki kümülatif ikili alt-model:

1. `z1 = 1[y > down]` — stable/up ile down ayrımı.
2. `z2 = 1[y > stable]` — up ile down/stable ayrımı.

Her iki alt-model de:

- `LogisticRegression(C=0.1, penalty="l2", solver="lbfgs", max_iter=2000,
  class_weight="balanced", random_state=42)`;
- aynı origin-train matrisi ve aynı aylık `sample_weight`;
- ayrı `.fit()` çağrısı, aynı origin-içi imputer/scaler çıktısı;
- hiçbir threshold, C, feature veya model taraması yok.

Toplam Model 15 bütçesi: 50 origin × 2 ikili fit = 100 fit. Tek adayın adı
`frank_hall_l2_c01`.

## 3. Kümülatif Olasılık ve Monoton Projeksiyon

Ham çıktılar:

```text
q1 = P(y > down)
q2 = P(y > stable)
```

Geçerli ordinal dağılım için `q1 >= q2` gerekir. Her satırda L2-isotonic
iki-nokta projeksiyonu sonuçtan önce şu şekilde kilitlenmiştir:

```text
q1' = q1; q2' = q2                         eğer q1 >= q2
q1' = q2' = (q1 + q2) / 2                  eğer q1 < q2

p_down   = 1 - q1'
p_stable = q1' - q2'
p_up     = q2'
```

Tüm olasılıklar `[0,1]` aralığında ve toplamları `1±1e-12` olmalıdır; aksi
halde durulur. Tahmin, `[down, stable, up]` sabit sırasındaki `argmax`'tır;
eşitlikte soldaki sınıf kazanır. Alternatif projeksiyon/threshold post-hoc
denenmez.

## 4. Canlı Kontrol ve Ortam Kilidi

Model 14'ün git-ignored JSON/CSV'si referans değildir. Aynı süreçte ve aynı
snapshot üzerinde `model_14...kol_calistir(TEST_FEATURELAR)` canlı çalıştırılır.
Canlı Model 14 L2 C=0,1 nokta değerleri aşağıdaki yayımlanmış referanslarla
`abs_tol=1e-12` eşleşmelidir:

- MCC `0.0885950392362906`
- macro-F1 `0.3658910750843209`
- M−2 persistence MCC `0.0165080995517002`
- M−2 persistence macro-F1 `0.36415215989684074`

Çalışma ortamı, Model 14'ün doğrulanmış ve proje boyunca kullanılan izole
ortamıyla sabittir:

- yorumlayıcı: `.venv312/Scripts/python.exe`
- Python `3.12.7` (Anaconda build)
- scikit-learn `1.7.2`
- NumPy `2.3.5`
- pandas `2.3.3`

Sürüm veya canlı Model 14 referansı uyuşmazsa Model 15 tahmini yorumlanmadan
durulur. Bu ortam kilidi taşınabilirlik tercihi değil, karşılaştırma
determinizmi koşuludur.

Not: sistem Anaconda yorumlayıcısında scikit-learn `1.5.1`, NumPy `1.26.4` ve
pandas `2.2.2` vardır; Model 14 kontrol kolunda farklı lojistik tahminler
ürettiği doğrulanmıştır. Model 15 için bu yorumlayıcı yasaktır.

## 5. Birleşik Beşli Hipotez Ailesi

Tek süreçte canlı üretilen tahminler:

- Model 14'ün dört adayı;
- Model 15 `frank_hall_l2_c01`.

Beş adayın M−2 persistence'a karşı eşli ΔMCC dağılımları **aynı** seed=420
blok indeksleriyle hesaplanır. Tek-yönlü p-değerleri birlikte Holm–Bonferroni
`m=5` düzeltmesine girer. Model 14 PM raporundaki Holm-4 değerleri yeniden
kullanılmaz; Holm-5 altında değişmeleri beklenir ve ayrıca raporlanır.

Bu aile, Prompt 43 + Prompt 44'ün yerel FWER kontrolüdür; proje ömründeki tüm
önceki Model 09/10/12/13 denemeleri için kümülatif FWER iddiası kurulmaz.

## 6. Başarı / Terfi Kapısı

Model 15 için altı koşulun **tümü** gerekir:

1. Holm-5 altında `h0_reddedildi=True` ve eşzamanlı ΔMCC alt sınırı `>0`.
2. M−2 persistence'a ΔMCC `>=0,05`.
3. M−2 persistence'a Δmacro-F1 `>0`.
4. Her leave-one-year-out kesiminde ΔMCC `>0`.
5. Nokta MCC `>0,0885950392362906` ve nokta macro-F1
   `>0,3658910750843209` — Model 14 en iyi adayını iki metrkte de kesin
   aşan mühendislik ilerleme kapısı. Bu koşul inferential CI iddiası değildir;
   1. koşulun yerine geçmez.
6. Train-çoğunluğu baseline'ı hem MCC hem macro-F1'da geçilir.

Başarı: **TERFI_ADAYI_BULUNDU_MODEL15**. Bu hüküm kilitli testi otomatik
açmaz. Herhangi bir koşul başarısızsa:
**ORDINAL_TEK_ADAY_TERFI_YOK**; ordinal ailede ek threshold/C/projeksiyon
taraması yapılmaz.

## 7. STOP_ONLY_IF

Aşağıdakilerden biri oluşursa sonuç yorumlanmadan durulur:

1. Model 14 feature üretimi/listesi birebir import edilemezse.
2. Ortam sürümleri Bölüm 4 ile uyuşmazsa.
3. Canlı Model 14 referans metrikleri Bölüm 4'le eşleşmezse.
4. Origin=50, embargo=2, bootstrap=2.000 veya seed'ler değişirse.
5. Her iki binary fit aynı train matrisi/ağırlıkları kullanmazsa ya da origin
   dışında preprocessing fit edilirse.
6. `q1'/q2'` monotonluğu, olasılık aralığı veya toplam=1 kontrolü bozulursa.
7. Beş aday aynı bootstrap indeks ailesine girmezse.
8. Post-hoc feature, C, threshold, projeksiyon veya ikinci ordinal aday
   eklenmek istenirse.
9. Kilitli test satırı herhangi bir veri yoluna girerse.

## 8. Zorunlu Çıktı

- Model 15 script'i ve odaklı testler;
- canlı Model 14 kontrol doğrulaması;
- Holm-5 tablosu ve Model 15 altı-kapı matrisi;
- environment metadata;
- 7 başlıklı PM raporu, ders notebooku ve README durum güncellemesi;
- tüm tracked `tests/` paketinin sonucu;
- Türkçe mantıksal commitler ve `origin/main` push;
- kilitli test durumu açıkça `ACILMADI_KILITLI`.
