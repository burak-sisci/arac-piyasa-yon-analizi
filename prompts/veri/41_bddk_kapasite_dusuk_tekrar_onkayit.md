# Prompt 41 — BDDK C=0,01 Kapasite-Düşürülmüş Tekrar Ön-Kaydı

**Tarih:** 2026-08-08

**Karar yöneticisi:** Pusula (`6f4c6fd0-6ddb-4b70-8e45-86d5b6d124c1`, Opus/max)

**Uygulayıcı:** Rota-2

**Tetikleyici:** Model 12 `ON_ELEME_ZAYIF / HEURISTIK`; commit `23b42a2`

## 1. Amaç ve yorum sınırı

Bu tekrar Model 12'de C=1 lojistik kolunda görülen `delta_marj=+0,2401713367`
iyileşmesinin daha güçlü düzenlileştirmede sürüp sürmediğini tek bir yeni
kapasite noktasında sınar. Yalnız lojistik L2 `C=0,01` eklenir. Başka C değeri,
feature, veri, eşik veya model eklenmez.

Çalışma yine cari/revize BDDK serisi üzerinde in-sample/permutasyon heuristiğidir.
OOF performans, üretim becerisi veya temiz ilk-yayım vintaj sonucu değildir.
Her hüküm `HEURISTIK` etiketiyle yazılır.

## 2. Sabit veri ve bilgi sözleşmesi

- Hedef: `noter_devir_otomobil_adet`.
- Sınıflar: `down / stable / up`; kapalı stable bandı ±%5.
- Analiz originleri: `2021-03..2025-04`, tam 50 ay × 4 snapshot.
- Bilgi kesimi: M−2; M−1/M target veya feature yasaktır.
- Kontrol kolu: Model 09'un 10 feature'ı (`m09.FEATURELAR`).
- Test kolu: aynı 10 feature + Model 12'nin aynı dört BDDK dönüşümü; toplam 14.
- BDDK girdisi: Model 12'nin hash-kilitli cache'i, SHA-256
  `4ED663DC373C6BB6C63A7A2D910D22408C574CF71210FFB9453E7EB087F030DE`.
- Yeni HTTP çağrısı: **0**. Hash yüklemede yeniden doğrulanır; uyuşmazlıkta durur.
- Kilitli test `2025-07..2026-06` açılmaz.

Dört BDDK feature'ı, tatil takvimi, exact 3/11 istisnaları, TÜFE yüzde-puan
birimi, bileşik reel formül ve konumsal 4/13/52-gözlem indeksleme Model 12 ile
birebirdir.

## 3. İki kollu ve beş konfigürasyonlu hesap

Özgün dört konfigürasyon aynen yeniden koşulur:

1. lojistik L2 C=0,1
2. lojistik L2 C=1
3. sığ Random Forest
4. sığ HistGradientBoosting

Beşinci ve tek yeni konfigürasyon:

5. lojistik L2 C=0,01; `solver=lbfgs`, `max_iter=2000`,
   `class_weight=balanced`, `random_state=42`.

Seed=410, iki kolda ortak 1.000 permütasyon matrisi, ay başına toplam 1 ağırlık,
aynı imputer/scaler ve tek-thread belirlenimciliği korunur. Toplam hesap bütçesi
1.000 × 5 × 2 = 10.000 permütasyon fit'idir. 40 dakika aşılırsa azaltma veya
post-hoc uyarlama yapılmaz; koşu durur ve raporlanır.

## 4. Harness ve yeni baseline

Model 12'nin özgün dört kontrol referansı değişmez:

| Konfigürasyon | Gözlenen | Null95 |
|---|---:|---:|
| lojistik_l2_c01 | 0,2147571548065723 | 0,4450343895977828 |
| lojistik_l2_c1 | 0,16897848477598726 | 0,4683733695252251 |
| random_forest_sigin | 0,9168817090818534 | 0,9155435038620596 |
| hist_gradient_sigin | 1,0 | 1,0 |

Model 12'deki asimetrik toleranslar aynen uygulanır. Bu dört referanstan biri
geçmezse sonuç geçersizdir ve koşu durur.

C=0,01 Model 11'de bulunmadığı için harness referansı yoktur; bu çalışmada
**yeni baseline** olarak üretilir. Aynı seed ve ortak permütasyon matrisini
kullanması zorunludur.

## 5. Bağlayıcı hüküm yalnız C=0,01 içindir

Özgün dört konfigürasyon yalnız harness ve bağlamdır. Model 12 C=1 deltası bu
tekrarın kararına giremez. Böylece `ON_ELEME_ZAYIF` dalının kendini yeniden
çağırması engellenir.

C=0,01 için:

- `marj = gozlenen_kol2 − null95_kol2`
- `delta_marj = marj_kol2 − marj_kol1`

Kapılar aşağıdaki sırayla ve terminal olarak uygulanır:

0. **Manipülasyon kapısı:** `null95(C=0,01, kol1) < 0,4450343895977828`?
   - Hayır: `KAPASITE_MANIPULASYONU_ETKISIZ` → BDDK `ONCELIK_DUSURULDU`
     (normal yeniden-açma önceliği) → yeni masa başı taraması. Son.
   - Evet: 1. kapıya geç.
1. `marj(C=0,01, kol2) ≥ +0,15`?
   - Evet: `KAPASITE_DUSUK_GECTI` → ön-kayıtlı revizyon kırılma-noktası
     analizine geç. Son.
   - Hayır: 2. kapıya geç.
2. `delta_marj(C=0,01) ≥ +0,15`?
   - Evet: `KAPASITE_DUSUK_ZAYIF_TEYIT` → BDDK `ONCELIK_DUSURULDU`, fakat
     izinli vintaj kanalı veya revizyona-kapalı kardeş gösterge ortaya çıkarsa
     **yüksek yeniden-açma önceliği** → yeni masa başı taraması. Son.
   - Hayır: `KAPASITE_DUSUK_ISARET_YOK` → BDDK `ONCELIK_DUSURULDU`
     (normal yeniden-açma önceliği) → yeni masa başı taraması. Son.

Dört dalın dördü terminaldir. C=0,001 veya başka bir C değeri hiçbir dalda
açılamaz.

## 6. Terminal eylemler

### KAPASITE_DUSUK_GECTI

İzinli ilk-yayım vintajı hâlâ yoktur; ücretli/kimlikli kaynak veya dış kuruma
mesaj yasaktır. Ayrı önkayıtla, sabit seed altında BDDK seviye serisine
önceden seçilecek ±%0,1 / ±%0,5 / ±%1 / ±%2 perturbasyon ölçekleri uygulanır.
Marjın +0,15 altına düştüğü revizyon kırılma noktası aranır. Bu çalışma vintaj
edinmez; gözlenmeyen revizyona duyarlılığı sınırlar.

### Diğer üç dal

Prompt 38 kalıbında en fazla üç yeni adaylı sınırlı masa başı taraması yapılır.
İlk-yayımı nihai değer olan, yapısı gereği revizyona kapalı seriler önceliklidir.
Önceki üç kart tüketilmiştir: BDDK bu dalla değerlendirilir; BETAM ve Google
Trends mevcut rolling-origin sözleşmesi için daha önce elenmiştir.

## 7. Zorunlu raporlama

1. Kol başına feature sayısı açıkça yazılır: kontrol 10, test 14; nominal
   feature sayısı artışı yaklaşık %40'tır.
2. Beş konfigürasyonun her biri için gözlenen ve null95 değişimleri kol1→kol2
   ayrı ayrı; ayrıca marj ve delta marj raporlanır. Gözlenen artışın null95
   artışından büyük olup olmadığı açıkça belirtilir.
3. Her delta iddiası aynı cümlede mutlak kol2 marjıyla birlikte yazılır. Pozitif
   delta, mutlak marj negatif veya +0,15 altında ise geçiş gibi sunulmaz.
4. C=0,01 kontrol sonucu `yeni baseline` olarak etiketlenir; Model 11 harness
   değeriymiş gibi sunulmaz.
5. Test kilidi, hash, ağ çağrısı=0, 1.000 tekrar, seed ve koşu süresi yazılır.
6. PM raporu yedi zorunlu başlığı taşır; ayrı ders-kitabı notebooku gerçek
   sonuç JSON'uyla çalıştırılır.

## 8. STOP_ONLY_IF

- Cache SHA-256 uyuşmazlığı veya yeni ağ çağrısı gereksinimi.
- Özgün dört config harness toleransının aşılması.
- İki kol arasında seed, permütasyon, satır, ağırlık veya fit asimetrisi.
- M−2/TÜFE/takvim bilgi sözleşmesi ihlali.
- Post-hoc feature, veri, eşik, C veya model ekleme isteği.
- 40 dakikayı aşan 10.000-fit koşusu.
- Kilitli teste erişim, ücret/kimlik veya dış iletişim gereksinimi.
- Bağlayıcı hedef/sınıf/ufuk/K değişikliği.

Bu koşullar dışında Rota-2 terminal dala onay beklemeden devam eder.
