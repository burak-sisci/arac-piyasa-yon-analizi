# PM Raporu — Model 16 Nested Persistence–Lojistik Hibrit

## 1. Ne Yapıldı

Model 14 L2 C=0,1 olasılıkları ile M−2 persistence one-hot olasılığı,
`[0; 0,25; 0,50; 0,75; 1]` sabit ızgarasında karıştırıldı. Her dış origin için
karışım ağırlığı yalnız o origin'in train aylarında 12-ay başlangıç ve iki-ay
embargolu iç rolling ile seçildi. Model 14/15 aynı süreçte canlı yeniden
üretildi; altı aday ortak Holm ailesinde ölçüldü. Kilitli test açılmadı.

## 2. Sayısal Özet

| Yaklaşım | MCC | Macro-F1 | Accuracy | ΔMCC vs M−2 | Δmacro-F1 | Holm-6 alt sınır |
|---|---:|---:|---:|---:|---:|---:|
| M−2 persistence | 0,0165 | 0,3642 | 0,380 | — | — | — |
| Model 14 L2 C=0,1 | **0,0886** | **0,3659** | 0,385 | +0,0721 | +0,0017 | -0,2089 |
| Model 16 nested hibrit | 0,0031 | 0,3136 | 0,340 | -0,0134 | -0,0506 | -0,2016 |

Seçilen ağırlık dağılımı: `w=0`: 6 origin, `w=0,75`: 35 origin, `w=1`: 9
origin; `w=0,25/0,50`: 0. Toplam 1.725 iç lojistik fit + 50 dış fit yapıldı.
Yedi terminal kapının yalnız train-çoğunluğu karşılaştırması ve 50/50 train-içi
seçim denetimi geçti. Karar: **NESTED_HIBRIT_TERFI_YOK**.

## 3. Karşılaşılan Sorunlar

- İç rolling, çoğu dış origin için lojistik ağırlığı `0,75` seçti; bu seçim dış
  aylarda genellenmedi. Train-içi model seçimi sızıntısız olsa da örneklem ve
  rejim kararsızlığı nedeniyle yararlı olmadı.
- Yıl-dışı ΔMCC yalnız 2021 ve 2024'te pozitif; 2022/2023/2025 negatiftir.
- Holm-6 ailesinin genişlemesi Model 14'ün alt sınırını daha da muhafazakâr
  yaptı; yine de başarısızlık yalnız çoklu-test cezasından kaynaklanmıyor,
  Model 16 nokta farkları da negatiftir.
- Joblib fiziksel çekirdek sayısı uyarısı verdi; mantıksal çekirdeğe dönüş
  deterministik referansları etkilemedi.

## 4. Veri Örneği

Yeni ham veri çekilmedi. Dış-origin seçim denetimi şeması:

```text
fold,hedef_ay,dis_train_ilk,dis_train_son,secilen_w,ic_origin_kullanilan
1,2021-03,2019-01,2020-12,...,...
50,2025-04,2019-01,2025-01,...,...
```

Yerel artefaktlar: `model_16_nested_hibrit_ozet.json`,
`model_16_nested_hibrit_tahminleri.csv`,
`model_16_nested_hibrit_secim_denetimi.csv`; Git dışıdır.

## 5. Varsayımlar ve Kararlar

- K9/K10, M−2, ±%5 üç sınıf, iki ay embargo ve 14 as-of feature korundu.
- Dış gerçek etiket ağırlık seçimine girmedi.
- İç seçim persistence'a MCC/macro-F1 Pareto filtresi ve sabit tie-break ile
  yapıldı; post-hoc ağırlık eklenmedi.
- Model 14 ve Model 15 referansları aynı `.venv312` süreçte sıfır farkla
  yeniden üretildi.
- Altı aday aynı bootstrap indekslerini paylaştı; yerel FWER olarak raporlandı.
- Kilitli testten 57 snapshot satırı başta çıkarıldı.

## 6. Açık Sorular / PM Onayı Gerekenler

Bu ağırlık ızgarası ve nested hibrit aile kapatılmıştır. Dış performans kaybı
nedeniyle ek ağırlık/inner-objective taraması yapılmamalıdır.

## 7. Önerilen Sonraki Adım

Karar kaydı N11'de önceden tanımlı asimetrik/ordinal maliyet yaklaşımı, Model
14'ün aynı olasılıklarını kullanan tek ve sabit bir karar kuralı olarak
ön-kaydedilebilir. Reversal hatasına 4, komşu sınıf hatasına 1 maliyetli sabit
matris kullanılmalı; hiçbir maliyet katsayısı taranmamalıdır.
