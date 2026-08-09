# Prompt 45 — Model 16 Nested Persistence–Lojistik Hibrit Ön-Kaydı

**Tarih:** 2026-08-09

**Karar yöneticileri:** Rota-2 + Pusula

## 0. Gerekçe ve Sonuçsuzluk Beyanı

Model 14 L2 C=0,1, M−2 persistence'a nokta MCC'de `+0,0721` ve 5/5 yıl-dışı
pozitif fark üretmiş, fakat güven aralığı kapısını geçememiştir. Model 15
ordinal aday macro-F1 kaybetmiş ve kapatılmıştır. Model 16, zayıf lojistik
sinyalini yalnız dış-origin train'i içinde doğrulandığı ölçüde kullanıp diğer
durumlarda güçlü M−2 persistence'a dönmeyi sınar.

Bu ön-kayıt yazılırken Model 16 eğitilmez veya dış-origin sonucu görülmez.
K9/K10 hedefi, üç sınıf, ±%5 bant, M−2 as-of ve kilitli test değişmez.

## 1. Dış Protokol

- Model 14 `feature_hazirla` + `TEST_FEATURELAR` birebir import edilir.
- Dış 50 origin: 2021-03..2025-04; ilk train=24 ay; embargo=2 ay.
- Her dış origin'de imputer/scaler ve nihai L2 lojistik yalnız dış train'de
  fit edilir.
- Ortam `.venv312`: Python 3.12.7, sklearn 1.7.2, NumPy 2.3.5, pandas 2.3.3.
- `2025-07..2026-06` kilitli test çalışma başında dışlanır.

## 2. İç Rolling ve Sabit Ağırlık Izgarası

Her dış origin'in train ayları içinde ayrı iç rolling kurulur:

- iç başlangıç dış train'in ilk ayı;
- iç ilk train=12 ay;
- iç embargo=2 ay;
- iç değerlendirme dış train'in son ayına kadar genişler;
- dış origin'in embargo/değerlendirme ayları iç seçime hiçbir yoldan girmez.

Tek model `LogisticRegression(C=0.1, penalty="l2", solver="lbfgs",
max_iter=2000, class_weight="balanced", random_state=42)`; Model 14'ün
14 feature'ı ve ay-eşit `sample_weight` kullanılır. Her iç origin'de imputer,
scaler ve lojistik sıfırdan yalnız iç train'de fit edilir. `predict_proba`
sabit `[down,stable,up]` sırasına hizalanır; train'de bulunmayan sınıfa sıfır
olasılık verilir. Tek sınıflı iç train origin'i atlanır ve sayısı raporlanır.

Karışım ağırlıkları sonuçtan önce sabittir:

```text
W = [0.00, 0.25, 0.50, 0.75, 1.00]
p_hibrit(w) = w * p_lojistik + (1-w) * one_hot(M-2 persistence)
```

Tahmin sabit `[down,stable,up]` argmax; eşitlikte soldaki sınıftır.

İç seçim:

1. Her `w`, tüm geçerli iç değerlendirme aylarında ay-eşit MCC ve macro-F1
   ile ölçülür.
2. `w=0` iç persistence referansıdır.
3. Uygun ağırlık, persistence'a göre MCC ve macro-F1'da gerilemeyen ve en az
   birinde kesin iyileşen ağırlıktır.
4. Uygunlar lexicographic `(MCC, macro-F1, -w)` ile seçilir; tam eşitlikte daha
   küçük `w` kazanır.
5. Uygun ağırlık yoksa veya geçerli iç değerlendirme ayı `<5` ise `w=0`.

Seçilen `w`, dış origin'in train'inde fit edilen nihai lojistik olasılıklarıyla
yalnız o dış değerlendirme ayına uygulanır. Dış gerçek etiket ağırlık seçimine
girmez.

## 3. Canlı Kontroller

Aynı süreçte Model 14 test kolu ve Model 15 ordinal aday canlı yeniden
üretilir. Aşağıdaki metrikler `abs_tol=1e-12` eşleşmelidir:

- Model 14 L2 C=0,1: MCC `0.0885950392362906`, macro-F1 `0.3658910750843209`.
- Model 15 Frank–Hall: MCC `0.0857049536684403`, macro-F1
  `0.33160241279832153`.
- M−2 persistence: MCC `0.0165080995517002`, macro-F1
  `0.36415215989684074`.

Uyuşmazlıkta Model 16 sonucu yorumlanmadan durulur.

## 4. Altılı Hipotez Ailesi

Aynı süreç/seed=420/blok=4/2.000 bootstrap evreninde:

- Model 14'ün dört adayı;
- Model 15 Frank–Hall;
- Model 16 nested hibrit.

Altı adayın M−2 persistence'a eşli ΔMCC p-değerleri birlikte Holm `m=6`
düzeltmesine girer. Prompt 43-45 yerel FWER ailesidir; proje-ömrü kümülatif
FWER iddiası değildir. İç ağırlık ızgarası dış hipotez ailesine ayrı adaylar
olarak girmez; tamamı tek nested öğrenme algoritmasının train-içi seçimidir.

## 5. Başarı Kapısı

Model 16 için tümü zorunlu:

1. Holm-6 `h0_reddedildi=True` ve ΔMCC alt sınırı `>0`.
2. M−2 persistence'a ΔMCC `>=0,05`.
3. M−2 persistence'a Δmacro-F1 `>0`.
4. Leave-one-year-out ΔMCC her yılda `>0`.
5. MCC `>0.0885950392362906` ve macro-F1 `>0.3658910750843209`.
6. Train-çoğunluğu MCC ve macro-F1'da geçilir.
7. Bütün 50 dış origin için ağırlık seçiminin yalnız dış train içinde yapıldığı
   denetim sayacı/assertion ile doğrulanır.

Başarı: `TERFI_ADAYI_BULUNDU_MODEL16`; kilitli test otomatik açılmaz.
Başarısızlık: `NESTED_HIBRIT_TERFI_YOK`; bu ağırlık ızgarasında post-hoc
genişletme yapılmaz.

## 6. STOP_ONLY_IF

- Ortam, canlı Model 14/15 veya as-of feature referansı uyuşmazsa.
- Dış/İç embargo, origin sınırı veya train-only preprocessing bozulursa.
- Dış etiket/metric seçilen ağırlığı etkilerse.
- Sabit W, C, seçim/tie-break veya olasılık formülü değiştirilmek istenirse.
- Altı aday ortak bootstrap indekslerini paylaşmazsa.
- Kilitli test veri yoluna girerse.

## 7. Zorunlu Çıktı

Script + odaklı testler; origin-bazlı seçilen ağırlık/iç metrik denetim CSV'si;
Holm-6 ve yedi-kapı matrisi; 7 başlıklı PM raporu; ders notebooku; README;
tracked `tests/` sonucu; Türkçe commitler ve `origin/main` push.
