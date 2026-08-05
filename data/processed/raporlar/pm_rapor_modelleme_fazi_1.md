# PM Raporu — Modelleme Fazı (1. Bölüm): Target Değişikliği, Ortam Kurulumu, İlk AutoGluon Modeli

**Tarih:** 2026-08-05
**Kapsam:** Korelasyon analizi fazından modelleme fazına geçiş — target kararı,
AutoGluon TimeSeries ortam kurulumu, ilk deneme modeli ve doğrulama hatası
düzeltmesi.
**Durum:** Devam ediyor — bu, modelleme fazının İLK bölümünün raporu.

---

## 1. Ne Yapıldı (kronolojik)

1. **Target değişikliği:** Proje sahibi, önceki fazda kullanılan
   `noter_devir_toplam_adet` yerine **`noter_devir_otomobil_adet`**'i nihai
   target olarak seçti.
2. **Target veri kalitesi denetimi** (proje sahibinin isteğiyle, modellemeye
   geçmeden önce): Ham kaynak, DF-A/DF-B tutarlılığı ve mantıksal kısıtlar
   kontrol edildi — **hiçbir tutarsızlık bulunamadı** (detay Bölüm 3).
3. **AutoGluon TimeSeries kurulum kararları** — 4 temel soru proje sahibiyle
   netleştirildi (detay Bölüm 4).
4. **Ortam engeli ve çözümü:** Ana Python ortamı (3.14.2) AutoGluon
   TimeSeries'i desteklemiyor. Sistemde mevcut Python 3.12 bulunup, proje
   klasöründe izole bir sanal ortam (`.venv312/`) kurularak AutoGluon
   TimeSeries 1.5.0 (PyTorch, gluonts, chronos-forecasting dahil) başarıyla
   kuruldu — ana 3.14 ortamına dokunulmadı.
5. **İlk model denemesi** (`scripts/model/model_01_autogluon_ilk_tahmin.py`)
   çalıştırıldı — kod hatası içermeyen ama **doğrulama (validation)
   metodolojisinde ciddi bir kusur** tespit edilip düzeltildi (detay
   Bölüm 5).
6. **Düzeltilmiş model yeniden çalıştırıldı**, sonuçlar çok daha güvenilir
   çıktı (detay Bölüm 6).

---

## 2. Kaynak Kod ve Çıktı Dosyaları

- **Script:** `scripts/model/model_01_autogluon_ilk_tahmin.py`
- **Sanal ortam:** `.venv312/` (git-dışı, `.gitignore`'a eklendi)
- **Model çıktıları** (git-dışı, `data/processed/*` genel kuralına tabi):
  - `data/processed/model/autogluon_model_01/` (eğitilmiş model dosyaları)
  - `data/processed/model/model_01_leaderboard.csv`
  - `data/processed/model/model_01_tahmin.csv`

---

## 3. Target Veri Kalitesi Denetimi Sonucu

`noter_devir_otomobil_adet` için yapılan kontroller:

| Kontrol | Sonuç |
|---|---|
| 2018-01→2026-06 arası iç boşluk | Yok |
| `otomobil_adet > toplam_adet` mantık ihlali | Yok (0 ay) |
| Otomobil/toplam oranı stabilitesi | %61-%74 arası, ortalama %68, ani sıçrama yok |
| DF-A ile DF-B'nin çakıştığı 30 ay (2024-2026) | **Birebir aynı** (0 fark) |
| En sert ay-ay sıçramalar | 2020-04/05/06 (COVID-19 kapanma/toparlanma dönemi) — gerçek bir ekonomik olay, veri hatası değil, ama küçük veri setinde (102 ay) modeli çarpıtabilecek bir aykırı değer olarak not edildi |

**Sonuç: target temiz, tutarsızlık yok.**

---

## 4. AutoGluon TimeSeries Kurulum Kararları (proje sahibiyle netleştirildi)

| Karar | Sonuç |
|---|---|
| Yön (yukarı/aşağı/sabit) stratejisi | Henüz kesinleşmedi — "hepsini tek tek deneyeceğiz" (seviye-tahmin-sonra-eşikle / quantile-tabanlı / önce saf seviye kalitesine bak) |
| Zaman penceresi | "İkisini de dene, karşılaştır" (DF-A 2018-2026 geniş, DF-B 2024-2026 dar/zengin) — bu ilk model DF-A ile yapıldı |
| Satır granülerliği | **Günlük (takvim-genişletilmiş) — proje sahibinin AÇIK tercihi**, önerim (gerçek aylık satırlara dönüştürme) reddedildi, riskleri açıkça anlatıldı ve kabul edildi |
| Target formu | **Ham seviye** (log-değişim değil) — proje sahibinin onayladığı öneri |

---

## 5. İlk Model Denemesi ve Bulunan Doğrulama Hatası

**Kurulum:** DF-A'dan (`df_a_v3_noter_penceresi_2015_bugun.csv`) 2018-01-01→
2026-06-30 aralığı (3103 gün, target'in geçerli olduğu tek pencere).
`prediction_length=30` gün, `freq='D'`, `presets='medium_quality'`,
`time_limit=600` saniye. Covariate'ler: `usdtry_orta`, `tufe_aylik_degisim`,
`tufe_yillik_degisim`, `odmd_otomobil_adet`, `tuketici_guven_endeksi`,
`tasit_kredisi_faiz_lag12ay`.

**[PROAKTİF BULGU — ÖNEMLİ] `noter_devir_toplam_adet` covariate'lerden
BİLİNÇLİ OLARAK ÇIKARILDI.** Bu sütun, yeni target'ın (`noter_devir_otomobil_adet`)
neredeyse birebir bir üst-kategorisi (r≈0,98) — dahil edilseydi model bunu
"kopyalayarak" sahte bir başarı gösterirdi (veri sızıntısı). Bu karar proje
sahibine önceki fazın PM raporunda zaten bildirilmişti, burada uygulandı.

**İlk çalıştırmada bulunan hata:** AutoGluon, varsayılan ayarla (tek
doğrulama penceresi) eğitim verisinin SON 30 gününü otomatik test penceresi
yaptı — bu pencere **tesadüfen tam bir takvim ayına (2026-06-01→06-30)**
denk geldi ve o ay boyunca target **TEK bir sabit değer** taşıyordu (kod ile
doğrulandı). Sonuç: TemporalFusionTransformer modeli MASE=0,058 gibi aşırı
iyi (ve güvenilmez) bir skor aldı — "dünkü değeri kopyala" stratejisi bu
yapay-sabit pencerede neredeyse mükemmel çalışıyordu, gerçek bir tahmin
başarısı değildi.

**Düzeltme:** `num_val_windows=4`, `val_step_size=15` ile birden fazla,
farklı başlangıç noktalarından doğrulama penceresi kuruldu. Kodla doğrulandı:
4 pencereden 2'si ay geçişi içeriyor (target'ın birden fazla değer taşıdığı),
2'si içermiyor — ortalama skor artık tek bir "kolay" pencereye bağlı değil.

---

## 6. Düzeltilmiş Model Sonuçları

| Model | Skor (düzeltme öncesi, tek pencere) | Skor (düzeltme sonrası, 4 pencere ortalaması) |
|---|---|---|
| TemporalFusionTransformer | -0,0579 (şüpheli) | -1,6334 |
| **WeightedEnsemble (kazanan)** | — | **-1,5754** |
| DirectTabular | -3,18 | -3,40 |
| Chronos2 | -5,35 | -3,08 |
| ETS | -5,57 | -2,83 |
| Theta | -5,79 | -2,98 |
| RecursiveTabular | -5,40 | -3,89 |
| SeasonalNaive | -5,57 | -3,98 |

Düzeltme öncesi en iyi model ile ikincisi arasında ~50 kat fark vardı
(güvenilmez); düzeltme sonrası fark 1,5-2,5 kata indi (çok daha inandırıcı).

**Kazanan: WeightedEnsemble** (%93 TemporalFusionTransformer + %7 Theta),
MASE≈1,58 — yani AutoGluon'un kendi basit referans yöntemine (MASE'nin
tanım gereği kıyasladığı temel tahminci) göre hâlâ biraz daha yüksek hata
payı taşıyor. Bu, "mükemmel bir model" değil, **çalışan ama henüz basit bir
referans yöntemi kadar iyi olmayan bir ilk deneme** olarak okunmalı.

**Temmuz 2026 tahmini (örnek satırlar):**

| Tarih | Medyan tahmin | %10 | %90 |
|---|---|---|---|
| 2026-07-01 | 627.004 | 591.370 | 682.339 |
| 2026-07-05 | 617.040 | 572.094 | 670.044 |
| 2026-07-10 | 615.084 | 571.555 | 663.350 |

Belirsizlik aralığı (%10-%90) oldukça geniş — model kendi belirsizliğini
düşük tutmuyor, bu olumlu bir işaret (yanlış kesinlik iddiası yok).

---

## 7. Karşılaşılan Sorunlar

1. **Python sürüm uyumsuzluğu** (Bölüm 1/4) — çözüldü, izole ortamla aşıldı.
2. **Doğrulama penceresi hatası** (Bölüm 5) — bulunup düzeltildi, bu proje
   sahibinin daha önce net bir şekilde işaret ettiği "günlük kalmanın
   riski"nin somut, gerçekleşmiş bir örneğiydi.
3. Başka teknik sorun çıkmadı.

---

## 8. Açık Sorular / PM Onayı Gerekenler

1. **En iyi model bile basit referans yöntemden daha kötü (MASE>1)** —
   devam edilecek yön: daha fazla iyileştirme mi (özellik mühendisliği,
   farklı ayarlar), yoksa DF-B (2024-2026, zengin ama dar pencere) ile
   karşılaştırma mı yapılsın, proje sahibinin tercihini bekliyor.
2. **Yön (yukarı/aşağı/sabit) dönüşüm stratejisi** henüz seçilmedi — üç
   seçenek de (eşikleme / quantile-tabanlı / önce seviye kalitesine bakma)
   masada, proje sahibi "hepsini deneyeceğiz" dedi ama sıralama/öncelik
   belirlenmedi.
3. **DF-B ile karşılaştırma** henüz yapılmadı (proje sahibinin "ikisini de
   dene" talimatının ikinci yarısı).
4. **COVID dönemi aykırı değerleri** (Bölüm 3) modelde özel olarak ele
   alınmadı (ne çıkarıldı ne işaretlendi) — küçük veri setinde etkisi
   önemli olabilir, ayrı bir karar gerektirebilir.

---

## 9. Önerilen Sonraki Adım (başlatılmadı, yalnızca öneri)

(a) Aynı kurulumu DF-B (2024-2026) ile tekrarlayıp DF-A sonuçlarıyla
karşılaştırmak, (b) hangi covariate'lerin gerçekten katkı sağladığını
görmek için feature importance/ablation denemesi, (c) yön dönüşüm
stratejisinden birine karar verip uçtan uca bir "yön tahmini" örneği
üretmek.
