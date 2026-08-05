# PM Raporu — Modelleme Fazı (2. Bölüm): Metrik Düzeltmesi, DF-B Karşılaştırması, high_quality Baseline

**Tarih:** 2026-08-05
**Önceki rapor:** `pm_rapor_modelleme_fazi_1.md` (target seçimi, ortam kurulumu, ilk model + doğrulama penceresi hatası)
**Bu raporun kapsamı:** MASE'in mevsimsel periyot hatasının düzeltilmesi, DF-B ile karşılaştırma, `medium_quality` → `high_quality` geçişi ve nihai baseline.

---

## 1. Ne Yapıldı (kronolojik)

1. **DF-B ile aynı kurulum tekrarlandı** (`scripts/model/model_02_autogluon_df_b.py`) — model_01 ile birebir aynı yöntem (hedef, covariate dışlama mantığı, doğrulama düzeltmesi), farklı veri seti/pencere (2024-01→2026-06, 912 gün).
2. **[PROAKTİF BULGU] `leaderboard()` çağrısının `score_test` sütunu, eğitimde düzelttiğimiz AYNI hatayı taşıyordu** — bu fonksiyon kendi iç değerlendirmesinde yine verinin son 30 gününü (tek, tesadüfen ay-sınırına denk gelen pencere) kullanıyordu. `score_val` (4 pencereli, düzeltilmiş) sütunu esas alındı, `score_test` güvenilmez olarak işaretlendi.
3. **MASE'in referans aldığı mevsimsel periyot netleştirildi:** AutoGluon, `freq='D'` için varsayılan olarak **m=7 (haftalık)** kullanıyordu — kaynağın gerçek güncelleme sıklığıyla (aylık) uyumsuz. `eval_metric_seasonal_period=30` ile düzeltildi.
4. **`medium_quality` → `high_quality` preset karşılaştırması** yapıldı (aynı m=30 ayarıyla).
5. **Sonuç `baseline` olarak kaydedildi**: `high_quality` + `eval_metric_seasonal_period=30` + `WeightedEnsemble` — hem DF-A hem DF-B için.

---

## 2. Metrik Düzeltmesinin Etkisi (m=7 → m=30)

| Set | m=7 (yanlış referans) | m=30 (doğru referans) |
|---|---|---|
| DF-A — WeightedEnsemble | MASE 1,575 | **MASE 0,531** |
| DF-B — WeightedEnsemble | MASE 2,505 | **MASE 0,570** |

m=7 ile HİÇBİR model basit referans yöntemi (MASE<1) geçemiyordu. m=30 ile (kaynağın gerçek aylık ritmiyle örtüşen referans) en iyi modeller referans yöntemden **%45-47 daha az hata** yapıyor — ilk kez anlamlı, güvenilir bir başarı sinyali.

---

## 3. `medium_quality` → `high_quality` Karşılaştırması (m=30 sabit)

| Set | medium_quality (baseline v1) | high_quality (nihai baseline) | İyileşme |
|---|---|---|---|
| **DF-A** | MASE 0,531 | **MASE 0,454** | ~%15 |
| **DF-B** | MASE 0,570 | **MASE 0,449** | ~%21 |

**Kazanan model bileşimi değişti:**
- DF-A: %87 TemporalFusionTransformer + %13 Theta → **%95 TemporalFusionTransformer + %5 Chronos2**
- DF-B: ağırlıklı TemporalFusionTransformer → **%69 ChronosWithRegressor[bolt_small] + %31 TemporalFusionTransformer** (dikkat çekici bir değişim — Chronos tabanlı model DF-B'de baskın hale geldi)

**Eğitim süresi:** DF-A ~15,6 dk, DF-B ~14,6 dk (20 dakikalık sınırın altında; `Chronos2SmallFineTuned` DF-A'da kendi ayrılan süre içinde bitmediği için atlandı, nihai sonucu etkilemedi).

---

## 4. Nihai Baseline — Tam Leaderboard (high_quality, m=30)

**DF-A** (`data/processed/model/model_01_leaderboard_baseline_m30.csv`):

| Model | MASE (score_val) |
|---|---|
| **WeightedEnsemble** | **0,454** |
| TemporalFusionTransformer | 0,456 |
| DynamicOptimizedTheta | 0,695 |
| AutoETS | 0,658 |
| ChronosWithRegressor[bolt_small] | 0,655 |
| Chronos2 | 0,708 |
| DirectTabular | 0,637 |
| DeepAR | 0,739 |
| SeasonalNaive | 0,926 |
| RecursiveTabular | 0,930 |

**DF-B** (`data/processed/model/model_02_leaderboard_baseline_m30.csv`):

| Model | MASE (score_val) |
|---|---|
| **WeightedEnsemble** | **0,449** |
| ChronosWithRegressor[bolt_small] | 0,589 |
| TemporalFusionTransformer | 0,709 |
| AutoETS | 0,811 |
| DynamicOptimizedTheta | 0,846 |
| Chronos2SmallFineTuned | 0,953 |
| Chronos2 | 1,022 |
| DeepAR | 0,937 |
| SeasonalNaive | 1,154 |
| DirectTabular | 1,281 |
| RecursiveTabular | 1,075 |

Görsel: `data/processed/model/leaderboard_gorsel.png` (gönderildi).

---

## 5. Karşılaşılan Sorunlar

1. `leaderboard()` fonksiyonunun `score_test` sütunundaki aynı doğrulama hatası (Bölüm 1, madde 2) — bu, ilk raporda bulunan sorunun farklı bir yerde tekrar ortaya çıkmasıydı, proaktif olarak bildirildi ve `score_val` kullanılarak aşıldı.
2. Başka teknik sorun çıkmadı.

---

## 6. Açık Sorular / PM Onayı Gerekenler

1. DF-B'de Chronos tabanlı modelin (ChronosWithRegressor) baskın hale gelmesi — bu, zengin ama kısa pencerede (proxy/ENAG gibi) modern ön-eğitimli modellerin daha iyi genelleyebildiğine işaret edebilir; ayrı bir inceleme konusu olabilir.
2. Sonraki adım proje sahibi tarafından belirlendi: tahminlerin dönemsel olarak (hangi zamanlarda iyi/kötü) detaylı incelenmesi — bu raporun kapsamı dışında, ayrı ele alınacak.

---

## 7. Kalıcı Baseline Dosyaları

- `data/processed/model/model_01_leaderboard_baseline_m30.csv`, `model_01_tahmin_baseline_m30.csv`
- `data/processed/model/model_02_leaderboard_baseline_m30.csv`, `model_02_tahmin_baseline_m30.csv`
- `data/processed/model/autogluon_model_01_baseline_m30/`, `autogluon_model_02_baseline_m30/` (eğitilmiş model dosyaları — yeniden eğitmeden tahmin/analiz yapmak için kullanılabilir)
- `data/processed/model/leaderboard_gorsel.png`
