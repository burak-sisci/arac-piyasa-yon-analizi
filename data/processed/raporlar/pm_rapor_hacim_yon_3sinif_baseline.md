# PM Raporu — Hacim Yönü, Doğrudan Üç Sınıf Baseline (K9)

**Tarih:** 2026-08-06
**Branch:** `denetim/hacim-yon-baseline` (commit/push yapılmadı — Codex incelemesi bekliyor)
**Uygulayıcı:** Claude Code ("Kodcu")
**Kaynak görev:** `prompts/veri/28_hacim_yon_3sinif_uygulama_prompt.md`
**İlgili karar:** `docs/00_karar_kaydi.md` K9 (K8/ilan-fiyatı hedefinin YERİNE GEÇMEZ, paralel/ayrı bir hacim görevi)

## 1) Ne Yapıldı

1. Önceki (yanlış) fiyat-target denemesi temizlendi:
   `scripts/model/model_06_ilan_fiyati_yon_hedef_deneyimi.py`,
   `data/processed/raporlar/pm_rapor_ilan_fiyati_yon_hedef_protokolu.md` ve
   bunların ürettiği CSV/JSON çıktıları kaldırıldı; `prompts/veri/27_*.md`
   silindi.
2. `scripts/model/yon_degerlendirme.py`, hiçbir target'a özel varsayım
   taşımayan, target-bağımsız bir değerlendirme altyapısına dönüştürüldü:
   - `yon_etiketi(yuzde_degisim, esik_yuzde=5.0)` — sabit yüzde eşikli
     etiketleme (K2'deki oynaklık-uyarlamalı/sigma yaklaşımı, sadece K8/fiyat
     hedefine özgü kalacak şekilde bu modülden çıkarıldı).
   - `sonraki_ay_etiketleri(aylik_hacim, esik_yuzde)` — ay M'nin hacmini bir
     sonraki TAKVİM ayıyla (pozisyonel değil, takvim bazlı) karşılaştırıp
     etiketleyen saf fonksiyon.
   - `ay_agirligi(ay)` — `1/o aydaki gün sayısı`.
   - `uc_parcali_split_olustur(...)` — train→purge(1 ay)→val→purge(1 ay)→test
     kronolojik split'ini kurar ve çakışma/purge bütünlüğünü doğrular.
   - `olasiliklari_dogrula(...)`, `tahmin_sinifi_ve_guven(...)` — ürün
     olasılık sözleşmesi (toplam≈1, [0,1] aralığı, max-olasılık kararı).
   - `degerlendir(...)` (MCC-Gorodkin/macro-F1/accuracy/per-class/confusion)
     korunup opsiyonel `agirliklar` (sample-weight) desteği eklendi.
3. `tests/test_yon_degerlendirme.py` tamamen yeniden yazıldı: 21 pytest
   testi, eski sigma/K2 testleri kaldırıldı.
4. `docs/00_karar_kaydi.md`: orijinal K8 tarihsel karar olarak korundu; K8'in
   yarım "operasyonel ek notu" artık K9'a yönlendiriyor; yeni **K9** eklendi
   (aktif Aşama B kararı: hacim hedefi, sabit ±%5, günlük frekans,
   olasılık/güven çıktısı). Revizyon v10.
5. `README.md` Aşama B durumu ve `CLAUDE.md` (aktif target notu + rol
   hiyerarşisi: Codex denetmen/karar mercii, Claude Code Kodcu, Perplexity
   Araştırmacı) güncellendi. Aşama A checkbox'larına dokunulmadı.
6. `scripts/model/model_06_hacim_yon_siniflandirma.py` yazıldı ve
   `.venv312` ile hem DF-A hem DF-B için çalıştırıldı: özellik/lag mühendisliği
   (bkz. §5), purge'li kronolojik split, ay-ağırlıklı AutoGluon
   `TabularPredictor(problem_type="multiclass", eval_metric="mcc")` eğitimi
   (≤300 sn/set, tek deneme), test seti günlük+ay-bazlı metrikleri, majority/
   persistence/mevsimsel(t-12ay) baseline karşılaştırması, `predict_proba`
   çıktısı ve ayrı bir ileri-sinyal artefaktı.
7. Tüm pytest testleri ve model script'i çalıştırıldı; sonuçlar denetmenin
   ön-hesapladığı referans değerlerle bit-bit karşılaştırıldı (bkz. §2).

## 2) Sayısal Özet

**Tam-seri (±%5) etiket dağılımı — denetmen referansıyla BİREBİR uyuştu:**

| Set  | n (geçerli ay) | up | down | stable |
|------|----------------|----|------|--------|
| DF-A | 101            | 40 | 35   | 26     |
| DF-B | 29             | 11 | 9    | 9      |

**Split özeti (kaynak ayına göre, purge dahil):**

| Set  | train (bağımsız ay) | val (ay) | test (ay) | train günlük satır | test günlük satır |
|------|----------------------|----------|-----------|---------------------|--------------------|
| DF-A | 75 (2018-01→2024-03) | 12       | 12 (2025-06→2026-05) | 2282 | 365 |
| DF-B | 15 (2024-01→2025-03) | 6        | 6 (2025-12→2026-05)  | 456  | 182 |

**Eğitim süresi:** DF-A 14.1 sn, DF-B 5.6 sn (limit 300 sn/set, tek deneme;
her ikisi de limitin çok altında bitti — `medium_quality` preset küçük veri
boyutunda hızlı yakınsadı). Kazanan modeller: DF-A → LightGBMLarge, DF-B →
LightGBMXT (AutoGluon leaderboard).

**Test metrikleri (ay-ağırlıklı günlük ≡ ay-bazlı, n=bağımsız ay sayısı):**

| Set  | Model MCC | Model macro-F1 | Model acc | Majority MCC | Persistence MCC | Mevsimsel(t-12ay) MCC | Mevsimsel F1 | Mevsimsel acc |
|------|-----------|-----------------|-----------|---------------|-------------------|--------------------------|----------------|-----------------|
| DF-A | 0.242     | 0.276           | %33       | 0.000         | -0.266            | **0.394**                | **0.579**      | **%58**         |
| DF-B | 0.387     | 0.413           | %50       | 0.000         | -0.500            | 0.000                    | 0.300          | %33             |

- **DF-A modeli mevsimsel-yön baseline'ını GEÇEMEDİ** (MCC 0.242 < 0.394,
  F1 0.276 < 0.579) — dürüst "sinyal yok / naif baseline'ın altında" bulgusu
  (N6/N13). Majority baseline'ı hafifçe geçti ama en güçlü naif baseline'ı
  (mevsimsellik) geçemedi.
- **DF-B modeli tüm baseline'ları geçti** (MCC 0.387, en yakın rakip
  mevsimsel MCC=0.000) ama n=6 ay ile **istatistiksel olarak anlamsız
  derecede küçük örneklem** — genellenebilir bir sonuç DEĞİLDİR, yalnızca
  keşifsel bir gözlem.
- **Mevsimsel-yön baseline denetmen referansıyla BİREBİR uyuştu:** DF-A
  MCC=0.393617 (referans 0.3936, fark 1.7e-05), F1=0.579365 (referans
  0.5794), acc=0.583333 (referans 0.5833); DF-B MCC=0.0/F1=0.3/acc=0.333333
  (referans birebir). Bu, etiket tanımı/split sınırlarının denetmenin
  varsayımıyla tam örtüştüğünün bağımsız kanıtıdır.

**DF-A ay-bazlı confusion matrix (satır=gerçek, sütun=tahmin, sıra down/stable/up):**
`[[3,0,0],[5,0,0],[3,0,1]]` — model **hiçbir "stable" ayı doğru tahmin
etmedi** (recall=0), "down"u aşırı tahmin etti (5 gerçek "stable" ay da
"down" olarak sınıflandı).

**DF-B ay-bazlı confusion matrix:** `[[1,0,1],[0,0,2],[0,0,2]]` — "stable"
yine hiç yakalanamadı (n=2, recall=0); "down"/"up" kısmen ayırt edildi.

## 3) Karşılaşılan Sorunlar (saklanmaz)

1. **AutoGluon 1.5.0 dahili çökme (gözlemlenen davranış, WORKAROUND ile
   bypass edildi — kök neden KANITLANMADI):** `eval_metric="mcc"` +
   küçük/ağırlıklı örneklemde bazı taban modeller (önce NeuralNetTorch, NN_
   TORCH dışlanınca sırada LightGBMLarge) `val_score=NaN` üretiyor (sklearn
   MCC formülünde `sqrt(negatif)` — dejenere/sabit tahmin dağılımı olası bir
   açıklama, upstream'de kesin doğrulanmadı). AutoGluon bu modeli
   kaydetmiyor ama `WeightedEnsemble` aux-stacking aşaması yine de ona
   referans vermeye çalışıp `ValueError: Model does not exist` ile çöküyor.
   Model-bazlı dışlama (`excluded_model_types`) sorunu bir sonraki NaN'li
   modele taşıdığı için çalışmadı; bunun yerine `fit_weighted_ensemble=False`
   uygulandı (aux/ensemble adımı tamamen atlanır, taban modeller yine
   eğitilir, leaderboard'dan en iyi TEK model seçilir). **Bu bir kök-neden
   düzeltmesi DEĞİLDİR** — gözlemlenen crash'i bypass eden geçici bir
   workaround'dur; AutoGluon'un bu versiyondaki iç davranışının kesin nedeni
   incelenmedi.

   **Dürüst deneme geçmişi (saklanmadı):** Geliştirme sırasında bu hatayı
   teşhis ederken script EN AZ İKİ KEZ başarısız tam-set çalıştırması yaptı:
   (i) ilk çalıştırmada DF-B, NeuralNetTorch'un NaN val_score'u yüzünden
   crash etti; (ii) NN_TORCH dışlandıktan sonraki ikinci çalıştırmada DF-B
   bu kez LightGBMLarge belirtisiyle AYNI şekilde crash etti (DF-A her iki
   denemede de crash etmedi). `fit_weighted_ensemble=False` uygulandıktan
   sonraki ÜÇÜNCÜ çalıştırmada hem DF-A hem DF-B başarıyla tamamlandı. Bu,
   "tek deneme" kuralının ihlali değildir — kural, "aynı sabit konfigürasyon
   ile bir set için birden fazla fit deneyerek en iyi sonucu seçme" anlamında
   hiperparametre/sonuç araması yapılmamasını hedefler; burada denemeler
   arasında değişen şey bir çöken framework hatasının konfigürasyon
   düzeltmesiydi, sonuç seçimi değil. **Bu raporda ve `_sonuc.json`
   dosyalarında yer alan TÜM metrikler yalnızca üçüncü (nihai, workaround'lu)
   çalıştırmadan gelir** — başarısız denemelerin hiçbir çıktısı
   raporlanmadı/kullanılmadı.
2. **DF-A model çıktısı neredeyse dejenere:** 12 test ayı boyunca yalnızca
   **3 farklı olasılık vektörü** üretildi (`p_down` için 3 benzersiz değer),
   ve 11/12 ayda "down" tahmin edildi. Model, `usdtry_orta` (ay içi
   gerçekten değişen tek feature) dahil çoğu feature'ı fiilen görmezden
   gelmiş görünüyor — hızlı/tek-deneme baseline (`medium_quality`,
   ≤300 sn) ile küçük ve gürültülü bir eğitim setinde beklenen bir sonuç,
   ama açıkça bir sınırlamadır, "iyi model" gibi sunulamaz. DF-A'nın
   mevsimsel baseline'ı geçememesiyle tutarlı.
3. **"Stable" sınıfı iki sette de hiç yakalanamadı** (recall=0 her iki
   confusion matrix'te) — sınıf dengesizliği + küçük test örneklemi + hızlı
   baseline kombinasyonunun beklenen bir sonucu; class-weighting/threshold-
   moving (N4 sırası) bu baseline'da denenmedi (kapsam dışı bırakıldı,
   §7'de önerildi).
4. Kalan diğer her şey (etiket dağılımı, split ay sayıları, mevsimsel
   baseline metrikleri) denetmenin ön-hesabıyla bit-bit uyuştu — hiçbir
   tanım/örneklem uyuşmazlığı bulunmadı.

## 4) Veri Örneği (ham, ilk/son birkaç satır)

**Kaynak CSV'lerin gerçek ilk/son 3 satırı** (dosyadan okundu, uydurulmadı —
her iki dosya da 2015-01/2024-01'de başlayıp `kullanilan_gun`'den (2026-08-04)
sonrasına ay-hizalı olarak uzatıldığı için ilk ve/veya son satırlar target
henüz/artık dolu olmadığından NaN'dır; bu da ham verinin gerçek durumudur):

`data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv`
(sütunlar: `tarih`, `noter_devir_otomobil_adet`, `usdtry_orta`, `tufe_aylik_degisim`):

```
tarih,noter_devir_otomobil_adet,usdtry_orta,tufe_aylik_degisim
2015-01-01,NaN,NaN,NaN
2015-01-02,NaN,2.329,NaN
2015-01-03,NaN,NaN,NaN
...
2026-08-02,NaN,NaN,NaN
2026-08-03,NaN,NaN,NaN
2026-08-04,NaN,NaN,NaN
```

`data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv`
(sütunlar: `tarih`, `noter_devir_otomobil_adet`, `proxy_dom_gun`, `tufe_aylik_degisim`):

```
tarih,noter_devir_otomobil_adet,proxy_dom_gun,tufe_aylik_degisim
2024-01-01,530744.0,25.1,6.70331
2024-01-02,530744.0,25.1,6.70331
2024-01-03,530744.0,25.1,6.70331
...
2026-08-02,NaN,NaN,NaN
2026-08-03,NaN,NaN,NaN
2026-08-04,NaN,NaN,NaN
```

Aşağıdaki model çıktı örnekleri bu ham kaynaklardan üretilen pipeline'ın
sonuçlarıdır:

`data/processed/model/model_06_hacim_yon_df_a_test_gunluk_tahmin.csv` (365 satır):

```
tarih,_ay,etiket,agirlik,p_down,p_stable,p_up,tahmin_sinifi,raw_confidence
2025-06-01,2025-06,up,0.033333,0.379432,0.266343,0.354225,down,0.379432
2025-06-02,2025-06,up,0.033333,0.379432,0.266343,0.354225,down,0.379432
2025-06-03,2025-06,up,0.033333,0.379432,0.266343,0.354225,down,0.379432
...
2026-05-29,2026-05,up,0.032258,0.379432,0.266343,0.354225,down,0.379432
2026-05-30,2026-05,up,0.032258,0.379432,0.266343,0.354225,down,0.379432
2026-05-31,2026-05,up,0.032258,0.379432,0.266343,0.354225,down,0.379432
```

`data/processed/model/model_06_hacim_yon_df_b_test_gunluk_tahmin.csv` (182 satır):

```
tarih,_ay,etiket,agirlik,p_down,p_stable,p_up,tahmin_sinifi,raw_confidence
2025-12-01,2025-12,down,0.032258,0.475066,0.152553,0.372381,down,0.475066
2025-12-02,2025-12,down,0.032258,0.475066,0.152553,0.372381,down,0.475066
2025-12-03,2025-12,down,0.032258,0.475066,0.152553,0.372381,down,0.475066
...
2026-05-29,2026-05,up,0.032258,0.345503,0.160670,0.493827,up,0.493827
2026-05-30,2026-05,up,0.032258,0.345503,0.160670,0.493827,up,0.493827
2026-05-31,2026-05,up,0.032258,0.345503,0.160670,0.493827,up,0.493827
```

`data/processed/model/model_06_hacim_yon_df_a_ileri_sinyal.json` (tam dosya, küçük/deterministik):

```json
{
  "veri_seti": "DF-A", "durum": "gerceklesme_bekleniyor",
  "kullanim_durumu": "yalniz_pipeline_demonstrasyonu",
  "model_egitim_son_ayi": "2024-03",
  "kullanilan_gun": "2026-06-30", "referans_ay": "2026-06", "hedef_ay": "2026-07",
  "p_down": 0.3592, "p_stable": 0.2750, "p_up": 0.3658,
  "tahmin_sinifi": "up", "raw_confidence": 0.3658
}
```

`data/processed/model/model_06_hacim_yon_df_b_ileri_sinyal.json`:

```json
{
  "veri_seti": "DF-B", "durum": "gerceklesme_bekleniyor",
  "kullanim_durumu": "yalniz_pipeline_demonstrasyonu",
  "model_egitim_son_ayi": "2025-03",
  "kullanilan_gun": "2026-06-30", "referans_ay": "2026-06", "hedef_ay": "2026-07",
  "p_down": 0.3511, "p_stable": 0.1921, "p_up": 0.4568,
  "tahmin_sinifi": "up", "raw_confidence": 0.4568
}
```

DF-A ve DF-B ileri-sinyalleri 2026-07 için AYNI yönde (up) ama farklı
olasılıklarla ayrışıyor; ikisi de saklandı, keyfi biri seçilmedi.

**Önemli sınırlama — bu sinyaller STALE'dir, üretim/fiyatlama kararında
KULLANILAMAZ:** Her iki ileri-sinyal de test değerlendirmesinde kullanılan
AYNI predictor'dan üretildi; bu predictor'lar `kullanilan_gun`'e (2026-06-30)
kadar YENİDEN eğitilmedi — DF-A modeli en son **2024-03** (train split
sonu), DF-B modeli en son **2025-03** (train split sonu) ayına kadarki
veriyle eğitilmiş durumda. Yani DF-A sinyali ~27 ay, DF-B sinyali ~15 ay
eski bir eğitim kesitinden geliyor. Olasılıklar RAW (kalibre edilmemiş) ve
güven düşük (bkz. §2 confusion matrix'leri — model "stable"ı hiç
yakalayamıyor). Bu artefaktın TEK amacı pipeline'ın uçtan uca (özellik
mühendisliği → eğitim → `predict_proba` → ürün sözleşmesi) çalıştığını
göstermektir; `kullanim_durumu: "yalniz_pipeline_demonstrasyonu"` alanı bunu
makine-okunur şekilde işaretler.

## 5) Varsayımlar ve Kararlar (K/N kararlarına uygunluk)

- **K9 (yeni):** target=`noter_devir_otomobil_adet`, günlük frekans,
  doğrudan üç sınıf, sabit ±%5 eşik. K8'in (ilan fiyatı yönü) yerine
  GEÇMEZ — K8 hâlâ N<50 kapısında dondurulmuş, ayrı ve paralel bir hedeftir.
- **Leakage önlemi:** `noter_devir_toplam_adet` (target'in ~üst-kategorisi,
  r≈0.98) tamamen dışlandı. Target'in GÜNCEL/gelecek değeri feature
  setinde YOK — yalnızca ay-takvimli lag1/2/3/12 (geçmiş) kullanıldı
  (lag0/güncel ay bilinçli olarak dışlandı). Aylık eşzamanlı kovaryatlar
  (TÜİK/ODMD/BETAM vb.) gerçek yayım gecikmesini modellemek için en az 1
  takvim ayı geciktirildi (`_lag1ay` sonekiyle); adında zaten
  `lag4ay/lag5ay/lag12ay` olan sütunlara ikinci kez gecikme uygulanmadı;
  DF-A'daki `usdtry_orta` gerçek günlük veri olduğu için kendi gününde
  kullanıldı. Ay-hizalı ham CSV dosyaları hiçbir şekilde değiştirilmedi —
  tüm mühendislik script'in bellek-içi kopyasında yapıldı. Global
  `bfill`/yeni `ffill` kullanılmadı (yalnızca `usdtry_orta`'nın hafta
  sonu NaN'ları kaynakta zaten olduğu gibi bırakıldı; AutoGluon eksik
  değeri kendi içinde ele alır).
- **Split/purge:** Denetmenin verdiği SABİT split'ler birebir kullanıldı;
  `uc_parcali_split_olustur` her iki sette de çakışma/purge bütünlüğünü
  doğruladı (aksi halde ValueError fırlatırdı — fırlatmadı).
- **Ağırlık:** Her günlük satıra `1/o aydaki gün sayısı` ağırlığı verildi;
  AutoGluon `sample_weight="agirlik"` + `weight_evaluation=True` ile hem
  eğitimde hem test değerlendirmesinde kullanıldı. Ay-ağırlıklı günlük
  metrikler ile ay-bazlı (her ayın son günü) metrikler DF-A/DF-B'de
  pratik olarak örtüştü (beklenen — bkz. §3 pseudo-replikasyon notu).
- **Pseudo-replikasyon:** DF-A'da yalnızca `usdtry_orta` ay içinde
  GERÇEKTEN değişiyor; DF-B'nin TÜM feature'ları ay-hizalı (ay içinde
  sabit). Bu, DF-B'de ay-ağırlıksız günlük metriklerin aynı ayın
  günlerini fiilen tekrar saydığı, DF-A'da ise ay-içi değişimin (küçük de
  olsa) gerçek bir sinyal taşıyabileceği anlamına gelir — ikisi de raporda
  ayrı ayrı işaretlendi, gizlenmedi.
- **DF-B küçük örneklem:** 15 bağımsız eğitim ayı, 6 test ayı — N12'nin
  N<50 keşifsel geçidinin altında; script ve bu rapor bunu KEŞİFSEL olarak
  açıkça işaretliyor, baseline/başarı iddiası kurulmuyor (N6/N12/N13'e uygun).
- **Olasılık kalibrasyonu:** Her iki sette de olasılıklar `predict_proba`
  ham çıktısıdır, Platt/temperature scaling UYGULANMADI (validation
  örneklemi — 12 ve özellikle 6 ay — güvenilir çok-sınıflı kalibrasyon
  için yetersiz). Çıktı JSON/CSV'lerde ve bu raporda açıkça "RAW" olarak
  etiketlendi.
- **Tek deneme kuralı:** ≤300 sn/set bütçe içinde AutoGluon'un kendi
  model-seçim/leaderboard mekanizması dışında hiçbir hiperparametre
  araması/sonuç-seçici manuel tekrar yapılmadı. Ancak dürüstçe belirtilmeli:
  geliştirme sırasında bir framework crash'ini teşhis ederken script en az
  iki kez başarısız tam-set çalıştırması yaptı (bkz. §3.1); nihai
  `fit_weighted_ensemble=False` konfigürasyonuyla yapılan ÜÇÜNCÜ (son)
  çalıştırma başarılı oldu ve bu raporda/`_sonuc.json`'da yer alan TÜM
  metrikler yalnızca o son çalıştırmadan gelir. §3.1'deki
  `fit_weighted_ensemble=False` bir hiperparametre denemesi değil, gözlenen
  bir framework crash'ini bypass eden GEÇİCİ workaround'dur (kök neden
  kanıtlanmadı — AutoGluon 1.5.0'a özgü davranış olarak not edildi).
- **İleri-sinyal ayrımı:** Test metriklerinden tamamen AYRI bir artefakt
  olarak üretildi, `durum: "gerceklesme_bekleniyor"` ve
  `kullanim_durumu: "yalniz_pipeline_demonstrasyonu"` ile işaretlendi;
  performans/test sonucu gibi sunulmadı. Değerlendirme (test) için eğitilen
  AYNI predictor'dan üretildi — DF-A için 2024-03, DF-B için 2025-03 train
  kesitiyle sınırlı, `kullanilan_gun`'e (2026-06-30) kadar yeniden
  eğitilmedi; bu yüzden STALE'dir ve operasyonel/fiyatlama kararında
  kullanılamaz (bkz. §4).
- **Dokunulmayanlar:** `notebooks/*.ipynb`, `AGENTS.md`, `urls_out.txt`,
  `scripts/model/model_03_geriye_donuk_test.py`,
  `model_04_yon_dogrulugu.py`, `model_05_feature_importance.py` — hiçbiri
  değiştirilmedi/silinmedi.

## 6) Açık Sorular / PM Onayı Gerekenler — Codex Kararlarıyla Kapatıldı

Bu bölüm önceki taslakta açık soru olarak bırakılmıştı; Codex denetimiyle
aşağıdaki şekilde karara bağlandı (2026-08-06):

1. **DF-A "sinyal yok" bulgusu — KABUL EDİLDİ, üretime alınmaz.** Model
   mevsimsel-yön baseline'ını geçemedi (N6/N13 anlamında dürüst negatif
   sonuç); bu, "mevcut feature seti + hızlı baseline yetersiz" olarak
   kayda geçti. DF-A modeli PRODUCTION/fiyatlama sinyali olarak
   KULLANILMAYACAK. Feature/model iyileştirmesi ancak §7'deki önerilerin
   ayrı bir görev olarak onaylanmasıyla başlar.
2. **DF-B sonucu (MCC=0.387) — YALNIZ KEŞİFSEL, genellenebilir kabul
   EDİLMEDİ.** n=6 ay ile istatistiksel olarak gürültü payı yüksektir;
   N12'nin N<50 keşifsel geçidine ulaşana kadar bu sonuç "umut verici ama kanıtlanmamış"
   statüsünde kalır, hiçbir operasyonel karara girdi olarak kullanılmaz.
3. **"Stable" sınıfının hiç yakalanamaması (recall=0, iki sette de) —
   OPERASYON İÇİN KABUL EDİLEMEZ.** Sonraki iterasyonda İLK müdahale
   **class-weighting** olacak (N4 sırası, adım 1) — threshold-moving ve
   kalibrasyon ancak class-weighting denendikten sonra sıradadır.
4. **`fit_weighted_ensemble=False` — YALNIZ AutoGluon 1.5.0 için geçici.**
   Kalıcı bir tasarım kararı DEĞİLDİR; bu spesifik sürümde gözlenen
   `WeightedEnsemble` aux-stacking crash'ini (§3.1, kök nedeni
   kanıtlanmamış) bypass eder. AutoGluon güncellendiğinde veya farklı bir
   preset/versiyon denendiğinde bu ayarın hâlâ gerekli olup olmadığı
   yeniden test edilmeden varsayılan (`True`) davranışa dönülmeyecek.

## 7) Önerilen Sonraki Adım (başlatılmadı, yalnızca öneri)

- DF-A için mevsimsellik-farkındalı feature'lar (ör. ay-of-year dummy'leri
  veya `hacim(t-12ay)` doğrudan feature olarak) denenip mevsimsel
  baseline'ı geçip geçemediği test edilebilir.
- Class-weighting (N4 sırası, adım 1) ile "stable" sınıfının recall=0
  sorunu hedeflenebilir.
- DF-B için veri biriktikçe (aylık yeniden-çalıştırma) split'ler
  genişletilip N12'nin N<50 keşifsel geçidine yaklaşıldığında sonuç
  güvenilirliği yeniden değerlendirilebilir.
- Olasılık kalibrasyonu (Platt/temperature scaling) yalnızca validation
  örneklemi yeterli büyüklüğe ulaştığında (özellikle DF-A'da) denenebilir.
