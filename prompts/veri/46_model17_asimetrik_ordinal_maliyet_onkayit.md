# Prompt 46 — Model 17 Sabit Asimetrik Ordinal Maliyet Ön-Kaydı

**Tarih:** 2026-08-09

**Gerekçe:** Karar kaydı N11, reversal hatasını komşu sınıf hatasından daha
pahalı gören ordinal/asimetrik maliyet yaklaşımını ileri deneme olarak
tanımlar. Model 15 ordinal eğitim ve Model 16 nested hibrit terfi etmemiştir.

## 1. Değişmeyen Protokol

- K9/K10, `down/stable/up`, ±%5, M−2, Model 14'ün 14 as-of feature'ı.
- `.venv312`: Python 3.12.7, sklearn 1.7.2, NumPy 2.3.5, pandas 2.3.3.
- 50 dış origin, iki ay embargo, origin-içi imputer/scaler/model fit.
- L2 lojistik Model 14 ile birebir: C=0,1, lbfgs, balanced, seed=42.
- Kilitli test `2025-07..2026-06` kapalı.

## 2. Tek Sabit Karar Kuralı

Model olasılıkları sabit `[down, stable, up]` sırasına hizalanır. Maliyet
matrisi satır=gerçek, sütun=tahmin:

```text
             tahmin down  stable  up
gerçek down       0         1      4
gerçek stable     1         0      1
gerçek up         4         1      0
```

Her tahmin sınıfı `j` için beklenen maliyet `sum_i p_i*C[i,j]`; karar minimum
beklenen maliyetli sınıftır. Tam eşitlikte sabit `[down,stable,up]` sırasındaki
soldaki sınıf kazanır. Tek aday adı `lojistik_c01_maliyet_014`.

Maliyet katsayısı, probability kalibrasyonu, threshold, feature veya C
taraması yoktur. Argmax lojistik tahminleri aynı süreçte Model 14 L2 C=0,1
tahminleriyle 1.400 satırda birebir eşleşmelidir.

## 3. Canlı Referans ve Yedili Aile

Aynı süreçte Model 14 dört aday, Model 15 Frank–Hall ve Model 16 nested hibrit
yeniden üretilir. Referans metrikler `abs_tol=1e-12`:

- Model 14 L2: MCC 0,0885950392362906; macro-F1 0,3658910750843209.
- Model 15: MCC 0,0857049536684403; macro-F1 0,33160241279832153.
- Model 16: MCC 0,0031241897683421307; macro-F1 0,31359289027165616.
- M−2 persistence: MCC 0,0165080995517002; macro-F1 0,36415215989684074.

Model 14 dört + Model 15 + Model 16 + Model 17 = yedi aday, aynı seed=420,
blok=4, tekrar=2.000 bootstrap evreninde Holm `m=7` ailesine girer. Bu Prompt
43-46 yerel FWER kontrolüdür; proje-ömrü kümülatif FWER değildir.

## 4. Başarı Kapısı

Tümü zorunlu:

1. Holm-7 reddi ve ΔMCC alt sınırı >0.
2. Persistence'a ΔMCC≥0,05.
3. Persistence'a Δmacro-F1>0.
4. Her leave-one-year-out ΔMCC>0.
5. Model 14 en iyisini MCC ve macro-F1'da kesin aşma.
6. Train-çoğunluğunu MCC ve macro-F1'da aşma.
7. Argmax kontrol tahminlerinin Model 14 L2 ile 1.400/1.400 eşleşmesi.

Başarı `TERFI_ADAYI_BULUNDU_MODEL17`; aksi halde
`ASIMETRIK_MALIYET_TERFI_YOK`. Kilitli test otomatik açılmaz.

## 5. STOP_ONLY_IF ve Çıktı

Ortam/canlı referans/argmax kontrol uyuşmazlığı; train-dışı fit; ortak
bootstrap sapması; maliyet/threshold post-hoc değişikliği veya kilitli test
erişimi durumunda sonuç yorumlanmadan durulur.

Script, odaklı test, maliyetli tahmin CSV/JSON, Holm-7, yedi-kapı matrisi,
7 başlıklı PM raporu, ders notebooku, README, tam tracked test ve push zorunlu.
