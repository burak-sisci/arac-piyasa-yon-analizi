# Prompt 43 — Model 14: Mevcut As-of Feature Genişletme Ön-Kaydı

**Tarih:** 2026-08-09

**Karar yöneticisi / Uygulayıcı:** Pusula (`c8ed4e77-80c1-442f-bc12-f62523be3eba`, Sonnet 5/xhigh) —
bu ön-kayıtta ayrı bir Rota uygulayıcı yoktur; aynı oturum hem tasarımı kurar
hem yazar.

**Tetikleyici:** Proje sahibinin doğrudan talimatı (2026-08-09): "model
performansını artırma odaklı çalışalım. bize lazım olan performans
metriklerinin çok altındayız." Model performans iterasyonu açıkça
yetkilendirilmiştir. Bağlam: Model 10'un test-dışı rolling-origin sonucunda
dört adayın da M-2 persistence'ı geçemediği (`pm_rapor_nowcast_rolling_origin.md`)
ve Model 11'in "mevcut bilgi temsilleri altında saptanabilir öngörü becerisi
yoktur" hükmüyle sunduğu üç seçenekten biri olan "bilgi kümesini değiştir"
(`pm_rapor_model11_hedef_bilgi_tavani.md`, `docs/10_asama_b_nowcast_kapanis_sentezi.md`).

## 0. Kapsam ve sınır — bu bir ÖN-KAYITTIR, sonuç YOK

Bu görevde model **eğitilmez**, validation veya rolling-origin **koşulmaz**,
hiçbir performans sayısı üretilmez. Amaç, Model 14'ün deneysel tasarımını —
bilgi-zamanı tablosu, feature formülleri, model adayları, sabit seed'ler ve
başarı/durdurma kuralları — herhangi bir sonuç görülmeden önce kilitlemektir
(N7/N12 falsifikasyon ve çoklu-test disiplini). Koşum, bu ön-kayıt proje
sahibi/Codex tarafından görüldükten sonra **ayrı bir görevde** yapılır.

## 1. Değişmeyen sözleşme (K9/K10, Model 07-10 ile birebir)

- Target: `noter_devir_otomobil_adet`; sınıflar `down/stable/up`, kapalı
  sabit **±%5** bant (K9/K10).
- Bilgi kesimi: her pazartesi tahmini, bir önceki pazar cut-off'una kadar
  bilinen veriyle (K10 madde 2).
- Aylık feature/target gecikmesi: en az **M-2** (K10 madde 4); lag-1 ve cari
  ay değeri feature olarak yasaktır.
- Ay-gruplu bağımsız örnek birimi, ay-eşit ağırlık (K10 madde 3); DF-A 101
  bağımsız ay ile N≥50 geçidini aşar (K10 madde 8).
- Rolling-origin protokolü **Model 10 ile birebir aynı**:
  `genisleyen_originler("2019-01", "2025-04", ilk_train_ay_sayisi=24,
  embargo_ay_sayisi=2)` → 50 test-dışı origin, değerlendirme aralığı
  2021-03..2025-04; her origin'de `max(train) ≤ değerlendirme-3` ve
  `embargo == [değerlendirme-2, değerlendirme-1]` assertion'ları korunur.
- Kilitli test **`2025-07..2026-06` KAPALI kalır**; bu çalışma açmaz.
- Yalnız **DF-A** kullanılır (N≥50 geçer). DF-B (N=29, N<50) bu protokolde
  yalnız keşifsel referans olarak anılabilir, doğrulayıcı karara giremez.
- Dönüşümler ve preprocessing (imputer + scaler) **her origin'in TREN kümesi
  içinde ayrı ayrı fit edilir**; global/tek seferlik fit yasaktır — Model 10
  ile birebir aynı disiplin.

## 2. Bilgi-zamanı (as-of) tablosu — yeni feature ailesi

Model 07'nin `haftalik_snapshot_uret` çıktısı (DF-A, 34 model feature'ı)
zaten bilgi-zamanı kurallarına uygun üretilmiştir: aylık feature'lar
`en_kucuk_aylik_lag=2` ile, günlük özet `_gunluk_ozet` yalnız cut-off'a kadarki
cari-ay gözlemleriyle hesaplanır. Model 09'un 10 feature'ı bu 34'ün küçük bir
alt-kümesidir. Bu ön-kayıt **yeni bir ham veri kaynağı, yeni bir sütun veya
yeni bir gecikme kuralı eklemez** — yalnızca zaten mevcut, zaten sızıntısız,
Model 09'da KULLANILMAYAN sütunlardan küçük ve domain-gerekçeli bir aile seçer.

Seçim kriterleri (neden bu 4/5 sütun, neden diğer ~29 unused sütun değil):
mevcut 10 feature ile bilgi çakışması düşük (ay_sin/ay_cos/is_gunu_ilerleme_orani
zaten takvim bilgisini tüketiyor → `ayin_gunu`, `ay`, `gecen_is_gunu`,
`aydaki_is_gunu` dışlandı); kur seviyesi/min/max birbirleriyle ve zaten
kullanılan `..._ilk_son_degisim_pct` ile yüksek kolineer → yalnız `_std`
(oynaklık, farklı bilgi türü) seçildi; `hafta_sirasi` tasarım gereği yalnızca
hafta-tanısı içindir, hiçbir model ailesinde feature olarak kullanılmaz (Model
09/10 ile aynı kural, Bölüm 6).

| # | Feature adı | Kaynak sütun(lar) (Model 07 snapshot, Model 09'da KULLANILMAYAN) | Doğal frekans | Bilgi gecikmesi / as-of kuralı | Sızıntı kontrolü (zaten Model 07'de uygulanmış) | Domain gerekçe |
|---|---|---|---|---|---|---|
| 1 | `usdtry_orta_std` | `usdtry_orta_std` (DF-A günlük USD/TRY orta kur, EVDS) | günlük iş günü | Gecikme yok; yalnız cari ayın başlangıcından cut-off'a kadarki gözlemlerin std'si (`_gunluk_ozet`, `cari_ay_parcasi`) | Kesit sonrası hiçbir gün dahil edilmez | Kur içi-ay oynaklığı; ithal parça/araç maliyet belirsizliği ve fiyatlama tereddüdü proxy'si. Model 09 yalnız ilk-son % değişimini (drift) kullanıyor; dağılım/belirsizlik bilgisi ayrı ve şu an kullanılmıyor. |
| 2 | `tuketici_guven_endeksi_lag2ay` | `tuketici_guven_endeksi_lag2ay` (TÜİK tüketici güven endeksi, aylık) | aylık | M-2 (K10 madde 4; Model 07 `aylik_a` listesi) | Zaten M-2 gecikmeli üretiliyor | Talep tarafı doğrudan duyarlılık göstergesi; N2 (karar kaydı) arz-talep rejim ayrımına tamamlayıcı, şu an modelde hiç yok. |
| 3 | `odmd_otomobil_adet_lag2ay` | `odmd_otomobil_adet_lag2ay` (ODMD yeni otomobil satış adedi, aylık) | aylık | M-2 | Zaten M-2 gecikmeli üretiliyor | Yeni araç arzı/ikamesi; ikinci el talebini dolaylı etkileyen dışsal arz sinyali (N2 — "arz değişkeni rejime bağlı çift yönlüdür"), şu an modelde hiç yok. |
| 4 | `reel_politika_faizi_lag2ay` (**TÜRETİLMİŞ**) | `politika_faizi_lag2ay` − `tufe_yillik_degisim_lag2ay` (ikisi de Model 09'da kullanılmıyor, ikisi de zaten M-2 snapshot'ta) | aylık | M-2 (iki bileşen de M-2; fark alma gecikmeyi bozmaz) | İki bileşen de zaten sızıntısız M-2; deterministik fark yeni bilgi kaynağı eklemez, yalnız yeniden ifade eder | Nominal politika faizinden enflasyon arındırılmış yaklaşık reel faiz (Fisher yaklaşıklığı, tam bileşik formül DEĞİL) — parasal sıkılık/gevşeklik rejimini nominal faizden daha iyi ayırt eder. Model 09 yalnız `tasit_kredisi_faiz_lag2ay`'ı (nominal, banka tarafı) kullanıyor; TCMB politika duruşu ve enflasyon rejimiyle ilişkisi modelde hiç yok. |

## 3. Feature formülleri

Raw geçişler (1-3) formül taşımaz — Model 07 sütunu birebir kopyalanır. Tek
türetilmiş formül:

```
reel_politika_faizi_lag2ay_t = politika_faizi_lag2ay_t - tufe_yillik_degisim_lag2ay_t
```

`t` = haftalık snapshot satırının `kesit_tarihi`'i; her iki bileşen de aynı
satırda zaten M-2 gecikmeli olarak mevcuttur (basit fark yaklaşıklığı; tam
bileşik Fisher formülü `(1+i)/(1+π)-1` KULLANILMAZ — yaklaşıklık olduğu
raporlamada açıkça yazılır).

Test kolu feature listesi := Model 09 `FEATURELAR` (10) + yukarıdaki 4 = **14
feature**. Kontrol kolu feature listesi := Model 09 `FEATURELAR` (10),
değişmeden.

## 4. Adaylar

### 4a. Model adayları — Model 09/10 ile birebir, yeni arama YOK

En fazla 2 model ailesi, toplam en fazla 4 sabit aday. Model 09'un
`_adaylar()` fonksiyonu **aynen** yeniden kullanılır; hiçbir hiperparametre
değişmez, hiperparametre taraması yapılmaz:

| Aile | Aday | Sabit hiperparametreler |
|---|---|---|
| Doğrusal (lojistik regresyon) | `lojistik_l2_c01` | C=0.1, L2, solver=lbfgs, max_iter=2000, class_weight=balanced, random_state=42 |
| Doğrusal (lojistik regresyon) | `lojistik_l2_c1` | C=1.0, diğerleri aynı |
| Ağaç-ensemble | `random_forest_sigin` | n_estimators=300, max_depth=3, min_samples_leaf=6, max_features=sqrt, class_weight=balanced, random_state=42 |
| Ağaç-ensemble | `hist_gradient_sigin` | max_iter=100, learning_rate=0.05, max_leaf_nodes=5, min_samples_leaf=12, l2_regularization=2.0, random_state=42 |

### 4b. Kol adayları

- **Kontrol kolu:** 10 feature, Model 10 ile birebir aynı çağrı. Model 10
  zaten commit'li ve deterministiktir (sabit seed); sonuçları doğrudan
  yeniden kullanılabilir. Tutarlılık için tek bir bit-eşitlik kontrolü
  (aynı `model_10_rolling_origin_ozet.json` yeniden üretilip üretilmediği)
  yapılır, yeniden yorumlanmaz.
- **Test kolu:** 14 feature (10 + Bölüm 2'deki 4), aynı 4 model adayı, aynı
  origin/embargo/seed.

Toplam hesap bütçesi: 2 kol × 4 aday × 50 origin = 400 model fit (kontrol
kolu Model 10'dan yeniden kullanılırsa yalnız test kolu için 200 yeni fit) +
kol başına 2.000 hareketli-blok bootstrap yeniden örneklemesi (model fit
değil, Holm/CI için). Bu ölçek Model 09/10 ile aynı büyüklük mertebesindedir;
Model 12/13'teki 40 dakikalık permütasyon bütçesi gibi ayrı bir zaman sınırı
gerekmez.

## 5. Sabit seed'ler (Model 10 ile birebir)

- Model `random_state`: **42** (tüm 4 adayda, `_adaylar()` içinde sabit)
- Hareketli-blok bootstrap (Holm/CI): `seed=420`, `blok_uzunlugu=4`,
  `tekrar=2000`
- IID duyarlılık bootstrap: `seed=420` (Model 10 ile aynı çağrı)
- Hafta-tanısı bootstrap (yalnız teşhis, terfi gerekçesi DEĞİL): `seed=421`
- Hiçbir seed origin'ler arası veya kollar arası değişmez; iki kol arasında
  seed/permütasyon asimetrisi STOP_ONLY_IF koşuludur (Bölüm 7).

## 6. Terfi kapısı (= başarı kuralı) — Model 10'dan gevşek DEĞİL

Referans: `persistence_m_eksi_2` (M-2 persistence baseline; Model 10'daki
`ref` değişkeniyle birebir). Test kolundaki her aday için, aşağıdaki dört
koşulun **TÜMÜ** terminal ve zorunludur:

a. **Eşli hareketli-blok + Holm alt sınır pozitif:** `h0_reddedildi=True` VE
   `delta_mcc_holm_alt_sinir > 0` (Model 10 ile birebir).
b. **Delta MCC ≥ 0.05:** `delta_mcc_nokta = mcc(aday) − mcc(persistence_m_eksi_2) ≥ 0.05`.
c. **Delta macro-F1 > 0:** `delta_macro_f1_nokta = macro_f1(aday) − macro_f1(persistence_m_eksi_2) > 0`.
d. **Yıl-dışı (leave-one-year-out) jackknife işaret koruması:**
   `isaret_her_yil_pozitif = True` — her çıkarılan yıl için delta MCC > 0
   korunur.

**Terfi = a AND b AND c AND d.** Hafta 1→4 tanısı hiçbir koşulda terfi
gerekçesi olarak kullanılamaz — Model 10'daki `terfi_gerekcesi_olamaz: True`
bayrağı burada da geçerlidir.

**İkincil/bilgilendirici (terfi kapısının PARÇASI DEĞİL):** kontrol kolu (10
feature) ile test kolu (14 feature) arasındaki nokta MCC/macro-F1 farkı
(Model 12/13'teki `delta_marj` üslubunda) ayrıca raporlanır — yeni feature
ailesinin katkısını persistence karşılaştırmasından bağımsız göstermek için.
Bu ikincil okuma yukarıdaki a-d kapısını **gevşetmez veya ikame etmez**.

## 7. Başarı / durdurma kuralları

**BAŞARI:** ≥1 test kolu adayı Bölüm 6'daki a-d koşullarının tümünü
karşılarsa → sonuç `TERFI_ADAYI_BULUNDU` olarak kaydedilir. Bu, kilitli
testin (2025-07..2026-06) otomatik açılması **anlamına gelmez**; K10 madde 6
gereği ayrı bir onay/karar adımı gerekir.

**BAŞARISIZLIK (dürüst negatif sonuç, N6/N13 ile tutarlı):** Hiçbir aday a-d
koşullarının tümünü karşılamazsa → `SINYAL_YOK_14_FEATURE` olarak kaydedilir;
K9/K10 hedefi/sınıfları değişmez, bu ailede ek ad-hoc feature araması
durdurulur.

**STOP_ONLY_IF** (aşağıdakilerden biri gerçekleşirse Pusula onay beklemeden
durur ve raporlar):

1. Herhangi bir feature'ın cut-off sonrası bilgi kullandığı veya M-2/lag2
   kuralının ihlal edildiği tespit edilirse.
2. Preprocessing'in (imputer/scaler) origin train'i dışında, global fit
   edildiği bir kod yolu bulunursa.
3. Origin sayısının 50'den, embargonun 2 aydan, bootstrap tekrarının
   2.000'den sapması gerekirse.
4. İki kol (kontrol/test) arasında seed, permütasyon indeksi, ay ağırlığı
   veya fit sırası asimetrisi bulunursa.
5. Post-hoc feature, model ailesi, hiperparametre arama veya beşinci aday
   ekleme isteği doğarsa.
6. Kilitli test erişimi, ücretli/kimlikli kaynak veya dış kuruma mesaj
   gereksinimi doğarsa.
7. Bağlayıcı K/N kararı, hedef, sınıf sayısı veya ufuk değişikliği gerektiren
   bir bulgu ortaya çıkarsa.
8. Kontrol kolu yeniden koşulduğunda Model 10'un commit'li
   `model_10_rolling_origin_ozet.json` çıktısıyla bit-eşit sonuç
   ÜRETMEZSE (determinizm/ortam sapması sinyali).

Bu koşullar dışında, ön-kayıt onaylandıktan sonra Model 14 koşumu ayrı bir
görevde onay beklemeden yürütülür (Otonomi Sınırı: "kod yazma... test, hata
düzeltme" kullanıcı gerekli değildir).

## 8. Zorunlu raporlama (Model 14 koşumu tamamlandığında)

1. Kontrol (10) ve test (14) kolu için her adayın nokta MCC/macro-F1/accuracy,
   Holm alt sınırı, delta MCC/macro-F1, yıl-jackknife işareti ayrı tablo
   halinde.
2. Terfi kapısı a-d'nin her biri açık EVET/HAYIR; herhangi bir terfi varsa
   hangi koşulun sınırında olduğu.
3. Kontrol-test delta'sı (Bölüm 6 ikincil okuma) ayrı başlıkta, terfi
   kapısından açıkça ayrıştırılmış.
4. Kilitli test durumu: `ACILMADI_KILITLI` ifadesi Model 10 ile birebir.
5. PM raporu 7 zorunlu başlık (AGENTS.md kural 10) + ders kitabı notebook
   (AGENTS.md kural 11) aynı commit/push paketinde.
6. Seed, origin sayısı, embargo, bootstrap tekrarı ve çalışma süresi açıkça
   yazılır.

Bu ön-kayıt commit'lendikten sonra hiçbir madde proje sahibi/Codex onayı
olmadan gevşetilemez; değişiklik gerekirse yeni bir revizyon notuyla ayrı bir
prompt açılır (AGENTS.md kural 4 ruhuna uygun).

## 9. Sonuç Öncesi Protokol Düzeltmesi — Kontrol Artefaktı Referansı

**Tarih:** 2026-08-09  
**Durum:** Model 14 test kolu çalıştırılmadan ve hiçbir 14-feature performans
sonucu görülmeden kilitlendi.

İlk odaklı testte kontrol kolunun güncel Model 10 koduyla aynı süreçte ürettiği
1.400 tahminin tamamı birebir eşleşmiş; buna karşılık
`data/processed/model/model_10_rolling_origin_{ozet.json,tahminleri.csv}` yerel
dosyalarıyla eşleşme sağlanmamıştır. Denetimde bu iki artefaktın
`.gitignore:17` nedeniyle Git tarafından **izlenmediği**, dolayısıyla ön-kayıtta
yanlış biçimde "committed Model 10 çıktısı" diye tanımlandığı ve yerelde eski
kalabildiği doğrulanmıştır. Bu bir Model 14 sonucu değildir; test kolu henüz
çalıştırılmamıştır.

Bu nedenle Bölüm 4b ve STOP_ONLY_IF madde 8 aşağıdaki daha güçlü ve taşınabilir
kuralla düzeltilmiştir:

- Kontrol referansı, eski/izlenmeyen yerel JSON veya CSV değildir.
- Referans, **aynı Python sürecinde, aynı HEAD kodundan** çağrılan
  `model_10_rolling_origin_nowcast._rolling_tahminleri(snapshot)` çıktısıdır.
- Model 14'ün parametrik 10-feature kontrol yolu ile bu güncel Model 10 kod
  yolunun 1.400 tahmini; `fold`, `hedef_ay`, `train_ay_sayisi`, `hafta_sirasi`,
  `yaklasim`, `gercek`, `tahmin` alanlarında satır satır birebir eşleşmelidir.
- Origin/embargo/model listesi/bootstrap seed ve tekrar sabitleri ayrıca Model
  10 modülünden doğrudan alınır ve assertion ile doğrulanır.
- Bu çalışma-anı eşitliği sağlanmazsa deney, test kolunun metrikleri
  yorumlanmadan `STOP_ONLY_IF_KONTROL_KOD_YOLU_UYUSMAZLIGI` ile durur.
- Git-ignored eski Model 10 artefaktları denetim izi olarak hash'lenebilir,
  ancak başarı/durdurma kapısına girmez ve güncel referans sayılmaz.

Bu düzeltme feature/model/hiperparametre/başarı kapısını değiştirmez; yalnız
yeniden-üretim referansını yanlış ve sürümlenmemiş bir dosyadan, aynı HEAD'deki
çalıştırılabilir Model 10 kod yoluna taşır.
