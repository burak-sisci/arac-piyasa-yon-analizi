# PM Raporu — Hacim Yönü, Sınıf Ağırlığı İterasyonu ve Çakışma Kurtarma

**Tarih:** 2026-08-06
**Branch:** `denetim/hacim-yon-baseline` (commit/push yapılmadı — Codex incelemesi bekliyor)
**Uygulayıcı:** Claude Code ("Kodcu")
**Kaynak görevler:** `prompts/veri/31_hacim_yon_sinif_agirligi_iterasyonu_prompt.md`
(sınıf ağırlığı iterasyonu — önceki çakışan süreçlerce yarım/tutarsız bırakılmış),
`prompts/veri/32_hacim_yon_cakisma_kurtarma_prompt.md` (bu raporun doğrudan kaynağı)
**İlgili karar:** `docs/00_karar_kaydi.md` K9

## 1) Ne Yapıldı

1. Denetmen tespiti doğrulandı: `scripts/model/yon_degerlendirme.py` içinde
   `sinif_agirliklari_hesapla` **iki kez** tanımlıydı. İkinci tanım (satır
   ~315, yalnız `label_sirasi` parametresi alan, `agirliklar` desteklemeyen
   sürüm) Python'da birinciyi sessizce eziyordu. `agirliklar=None`
   parametresini destekleyen, sınıf frekansını eğitimdeki ay-eşit ağırlık
   toplamından hesaplayabilen **tek sürüm** (satır 198) korundu; ikinci
   tanım tamamen kaldırıldı.
2. Aday seçiminde iki paralel yaklaşım vardı: `yon_degerlendirme.py` içinde
   test-edilmiş `en_iyi_aday_sec(aday_metrikleri)` (val MCC → macro-F1 →
   'stable' recall, eşitlikte dict sırasına göre ilk aday kazanır) VE
   `model_06_hacim_yon_siniflandirma.py` içinde aynı mantığı tekrar eden
   yerel `_aday_secim_anahtari(val_metrik)` yardımcı fonksiyonu (`max(...,
   key=...)` ile kullanılıyordu). Yerel yardımcı kaldırıldı; script artık
   doğrudan `yd.en_iyi_aday_sec(val_metrikleri)` çağırıyor — tek yaklaşım.
   `ADAYLAR`/`val_metrikleri` dict sırası (`esit_agirlik` önce eklenir) ile
   `en_iyi_aday_sec`'in eşitlik-tercihi ("dict'te önce gelen aday kazanır")
   birleşince, tam eşitlikte baseline (`esit_agirlik`) deterministik olarak
   tercih ediliyor — denetmen talimatıyla birebir uyumlu.
3. `tests/test_yon_degerlendirme.py` içindeki yinelenen/örtüşen testler
   temizlendi (kapsam azaltılmadan):
   - `test_sinif_agirliklari_bilinmeyen_etiket_reddedilir` **iki kez**
     tanımlıydı (aynı isim, birebir aynı gövde) — ikinci tanım Python
     tarafından sessizce birinciyi gölgeliyordu (gerçek kapsam kaybı
     yoktu, sadece dosyada ölü/gölgeli kod vardı). İkinci tanım silindi.
   - `test_sinif_agirliklari_dengeli_sette_hepsi_bir`,
     `test_sinif_agirliklari_esit_sinif_sayisinda_hepsi_bir` ile tamamen
     örtüşüyordu (aynı senaryo — dengeli sınıf sayısı → tüm ağırlıklar 1.0
     — aynı iddialar, ek assertion yok). Silindi.
   - Görünüşte benzer diğer çiftler **korundu** çünkü ek/farklı iddialar
     taşıyorlar (kapsam azaltmama kısıtı): `..._azinlik_sinif_daha_yuksek_
     carpan_alir` (frekans-ağırlıklı ortalama == 1.0 invariant'ını da
     doğruluyor, `..._dengesiz_agirliksiz_ters_frekansla_orantili`'de yok)
     ve `..._gorulmeyen_sinif_reddedilir` (hata mesajında eksik sınıf adının
     geçtiğini `match="stable"` ile doğruluyor, `..._egitimde_hic_
     gorulmeyen_sinif_reddedilir`'in `match="hic gorulmedi"` iddiasından
     farklı).
4. Tüm testler koşuldu: düzeltme öncesi 36 testin 2'si (`agirliklar`
   TypeError) başarısızdı, doğrulandı; düzeltme sonrası **35/35 test
   geçti** (36→35 sayı değişimi yalnız gölgelenen yinelenen testin
   silinmesinden kaynaklanıyor, gerçek kapsam kaybı yok).
5. `scripts/model/model_06_hacim_yon_siniflandirma.py`, `.venv312` ile
   DF-A ve DF-B için **bir kez** çalıştırıldı (AutoGluon 1.5.0,
   `medium_quality`, ≤300 sn/aday/set, `fit_weighted_ensemble=False`
   workaround önceki koddan değişmeden korundu). Test metrikleri bu
   çalıştırmada **KEŞİFSEL** işaretlendi (script'in kendi
   `test_degerlendirme_notu` alanı) ve aday seçim mantığına sokulmadı.
   Yeni feature, threshold, kalibrasyon veya frekans/hizalama değişikliği
   yapılmadı.

## 2) Sayısal Özet

**Tam-seri (±%5) etiket dağılımı — denetmen referansıyla BİREBİR uyuştu (her iki set):**

| Set  | n (geçerli ay) | up | down | stable |
|------|----------------|----|------|--------|
| DF-A | 101            | 40 | 35   | 26     |
| DF-B | 29             | 11 | 9    | 9      |

**Train sınıf ağırlıkları (yalnız train frekansından, balanced):**

| Set  | down  | stable | up    |
|------|-------|--------|-------|
| DF-A | 0.926 | 1.389  | 0.833 |
| DF-B | 1.000 | 1.667  | 0.714 |

**Validasyon karşılaştırması (mcc_gorodkin, macro_f1, stable_recall) ve seçilen aday:**

| Set  | esit_agirlik                  | sinif_agirlikli               | Seçilen aday      | Kural |
|------|--------------------------------|--------------------------------|-------------------|-------|
| DF-A | (0.3575, 0.4444, 0.000)        | (0.2935, 0.4749, 0.333)        | **esit_agirlik**  | MCC daha yüksek (sinif_agirlikli f1/stable_recall'da daha iyi olsa da MCC ilk kriter) |
| DF-B | (0.2132, 0.3000, 0.000)        | (0.3371, 0.3333, 0.000)        | **sinif_agirlikli** | MCC daha yüksek |

Eğitim süreleri: DF-A esit_agirlik 19.1s / sinif_agirlikli 10.4s; DF-B
esit_agirlik 5.1s / sinif_agirlikli 5.2s (ikisi de 300s zaman sınırının
çok altında).

**Test metrikleri (seçilen aday, KEŞİFSEL — bkz. §5) ve baseline karşılaştırması (ay-bazlı):**

| Set  | Model (gunluk_agirlikli) mcc/f1/acc | majority mcc/f1/acc | persistence mcc/f1/acc | mevsimsel(t-12ay) mcc/f1/acc |
|------|--------------------------------------|----------------------|--------------------------|-------------------------------|
| DF-A | 0.242 / 0.276 / 0.333                | 0.000 / 0.167 / 0.333 | -0.266 / 0.133 / 0.167   | 0.394 / 0.579 / 0.583 (denetmen referansıyla birebir) |
| DF-B | -0.387 / 0.095 / 0.167               | 0.000 / 0.167 / 0.333 | -0.500 / 0.000 / 0.000   | 0.000 / 0.300 / 0.333 (denetmen referansıyla birebir) |

Her iki settte de seçilen model, test döneminde mevsimsel (t-12 ay) baseline'ın
altında kaldı; DF-B'de model MCC'si negatif (mevsimsel baseline'dan da kötü).
Bu sonuçlar KEŞİFSEL bir gözlemdir, model/hiperparametre seçimini etkilemedi.

İleri sinyal (test dışı, henüz gerçekleşmemiş): DF-A 2026-07 → "up"
(raw_confidence=0.366); DF-B 2026-07 → "up" (raw_confidence=0.357).

## 3) Karşılaşılan Sorunlar

- Denetmenin bildirdiği 2/36 test hatası (`agirliklar` TypeError, yinelenen
  fonksiyon tanımından) doğrulandı ve giderildi (bkz. §1).
- **Proaktif bildirim (beklenmedik gözlem):** Her iki settte de test dönemi
  boyunca `predict_proba` çıktısı neredeyse sabit — DF-A'da 12 ay boyunca
  yalnızca **3 farklı** olasılık vektörü, DF-B'de 6 ay boyunca yalnızca
  **2 farklı** vektör üretildi (bkz. §4 örnek). Bu, seçilen modelin test
  döneminde ay-takvimli lag feature'larındaki değişime karşı çok düşük
  ayrım gücüne sahip olduğuna işaret ediyor (DF-A'da model fiilen
  "down"a yakın sabit bir tahmine yaslanıyor — test confusion matrix'inde
  down recall=1.0 ama down precision=0.27). Kök neden (feature seti,
  medium_quality preset kısıtı, 300sn zaman sınırı, ya da küçük
  train/val boyutu) bu görev kapsamında **araştırılmadı** — yeni
  feature/threshold/kalibrasyon eklemek görev talimatıyla yasaktı.
- DF-B: train yalnızca 15 bağımsız ay — script'in kendi çıktısı da bu
  deneyin KEŞİFSEL olduğunu, baseline/başarı iddiası kurulamayacağını
  bildiriyor (yeni değil, önceki fazlardan bilinen kısıt).
- Repoda bu görevle ilgisiz görünen, izlenmeyen (untracked) dosyalar var:
  `scripts/model/model_03_geriye_donuk_test.py`,
  `model_04_yon_dogrulugu.py`, `model_05_feature_importance.py`,
  `AGENTS.md`, `urls_out.txt`. Talimat gereği ("ilgisiz izlenmeyen
  dosyalara dokunma") bunlara **dokunulmadı**; önceki çakışan CLI
  süreçlerinin kalıntısı olabilirler — proje sahibinin/Codex'in ayrıca
  değerlendirmesi önerilir (bkz. §6).
- `notebooks/df_a_ders_kitabi.ipynb` ve `df_b_ders_kitabi.ipynb` değişmiş
  görünüyor (git status'ta `M`) — kullanıcı dosyaları olduğu ve talimat
  bunlara dokunulmamasını söylediği için **incelenmedi/değiştirilmedi**.

## 4) Veri Örneği

DF-A test çıktısı (`model_06_hacim_yon_df_a_test_gunluk_tahmin.csv`), ay
başına tek gözlem (olasılıklar ay içinde sabit kalıyor):

```
_ay      etiket  p_down    p_stable  p_up      tahmin_sinifi
2025-06  up      0.379432  0.266343  0.354225  down
2025-10  down    0.399787  0.226985  0.373228  down
2026-02  down    0.329867  0.274513  0.395620  up
2026-05  up      0.379432  0.266343  0.354225  down
```

DF-B test çıktısı (`model_06_hacim_yon_df_b_test_gunluk_tahmin.csv`):

```
_ay      etiket  p_down    p_stable  p_up      tahmin_sinifi
2025-12  down    0.321350  0.321350  0.357300  up
2026-02  stable  0.333333  0.333333  0.333333  down
2026-05  up      0.321350  0.321350  0.357300  up
```

## 5) Varsayımlar ve Kararlar

- Denetmenin `prompts/veri/32_*.md` talimatına harfiyen uyuldu: yalnız
  `agirliklar=None` destekleyen sürüm korundu; aday seçiminde tek yardımcı
  yaklaşım (`yd.en_iyi_aday_sec`) bırakıldı; sıra val MCC → macro-F1 →
  stable recall; tam eşitlikte `esit_agirlik` deterministik kazanır.
- Test temizliğinde "kapsam azaltma" kısıtına uyuldu: yalnız birebir
  aynı/gölgeli testler kaldırıldı; ek/farklı iddia taşıyan yakın-örtüşen
  testler korundu (bkz. §1.3).
- `prompts/veri/31_*.md`'nin sabit problem tanımı (K9, ±%5 sabit eşik,
  günlük frekans, DF-A/DF-B birlikte, MCC/macro-F1 ana metrik, test
  ayları model seçiminde kullanılmaz) değiştirilmeden korundu.
- Test sonuçları daha önce görülmüş olduğundan (`pm_rapor_hacim_yon_
  3sinif_baseline.md`'de raporlanmıştı) **doğrulayıcı değil keşifsel**
  diye açıkça işaretlendi; aday seçimine sokulmadı.
- Yeni feature, threshold moving, kalibrasyon, frekans/hizalama değişimi
  yapılmadı (talimat gereği).
- Commit/push yapılmadı (talimat gereği) — Codex/proje sahibi onayı
  bekleniyor.

## 6) Açık Sorular / PM Onayı Gerekenler

- Test döneminde her iki settte de olasılık çıktısının neredeyse sabit
  kalması (§3) — modelin gerçek ayrım gücünün çok sınırlı olduğuna işaret
  ediyor. Kök neden incelemesi (feature importance, hiperparametre/zaman
  sınırı artırımı) ayrı bir görev olarak mı planlansın, yoksa bu bilgi
  yalnız not düşülüp mevcut baseline ile mi ilerlensin?
- Repodaki ilgisiz untracked dosyalar (`model_03/04/05_*.py`, `AGENTS.md`,
  `urls_out.txt`) ne yapılsın — silinsin mi, ayrı bir görev kapsamında mı
  değerlendirilsin, yoksa proje sahibinin bilinen/kasıtlı çalışması mı?
- Test sayısının nominal 36'dan 35'e düşmesi onaylanıyor mu (gerçek kapsam
  kaybı yok — sadece gölgelenmiş/ölü yinelenen test tanımının temizliği,
  bkz. §1.3)?

## 7) Önerilen Sonraki Adım (yalnız öneri, başlatılmadı)

- Test döneminde gözlenen düşük ayrım gücü/near-constant olasılık
  bulgusunun kök nedenini (feature importance, `time_limit`/preset
  etkisi) ayrı ve dar kapsamlı bir keşifsel görevle incelemek — Codex
  onayına bağlı.
- Untracked kalıntı dosyaların (`model_03/04/05_*.py` vb.) durumunu proje
  sahibiyle netleştirmek.
