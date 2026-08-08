# Prompt 40 — Model 12 BDDK Heuristik Ön-Eleme Ön-Kaydı

**Tarih:** 2026-08-08

**Karar yöneticisi:** Pusula (`6f4c6fd0-6ddb-4b70-8e45-86d5b6d124c1`, Opus/max)

**Uygulayıcı:** Rota-2

**Kullanıcı yetkisi:** Pusula ve Rota-2 tam otonom çalışır; önemli kararlar
Pusula Opus/max ile alınır. Dış kişi/kuruma mesaj, ücretli/kimlikli servis ve
bağlayıcı sözleşme değişikliği bu yetkiyle genişlemez.

## 1. Amaç ve yorum sınırı

Model 12, BDDK haftalık taşıt kredisi cari/revize serisinin dört sabit
dönüşümünde hedef hakkında bir **ön-eleme işareti** bulunup bulunmadığını sınar.
Bu çalışma kesin bilgi üst sınırı değildir. Cari/revize seri ile ilk-yayım
vintajı farklı özellik vektörleridir; revizyon sinyali güçlendirmek zorunda
değildir.

Negatif sonuç yalnız şu hükme izin verir:

> Cari/revize BDDK serisinin, bu dört ön-kayıtlı dönüşümle, bu dört
> konfigürasyonla ve M−2 kesimiyle kurulan in-sample tavanı kendi permütasyon
> null'ını ön-kayıtlı marjla aşmamıştır. İlk-yayım vintajı temini maliyetini şu
> an gerekçelendiren kanıt yoktur.

Negatif sonuç şu hükümlere izin vermez:

- BDDK taşıt kredisi sinyal taşımıyor.
- Temiz vintaj serisi de geçemezdi.
- BDDK adayı kapanmıştır.
- Başka dönüşüm, kesim veya model konfigürasyonu da başarısız olur.
- Herhangi bir OOF performans veya üretim becerisi iddiası.

Pozitif sonuç yalnız vintaj temini maliyetinin artık gerekçelendiğini gösterir;
terfi veya beceri değildir.

## 2. Tarama kesinliği

JSON, PM raporu ve notebook hükmü daima `tarama_kesinligi` ile birlikte yazılır:

- `KESIN`: BDDK belgesi taşıt kredisi bakiyesinin revize edilmediğini açıkça
  söylüyorsa.
- `YAKLASIK`: Revizyon var fakat büyüklüğü belgeyle sınırlandırılmışsa.
- `HEURISTIK`: Revizyon durumu/büyüklüğü kalem düzeyinde belgelenmemişse.

Varsayılan `HEURISTIK`tir. En fazla dört resmî BDDK sayfası okunur.

## 3. Kaynak ve ağ bütçesi

Yalnız `bddk.org.tr`:

- Gelişmiş JSON uç noktası:
  `BultenHaftalik/tr/Gelismis/KiyaslamaJsonGetir`
- Kalem `1.0.5`, para `TRY`, sütun `3`, taraf `10001`.
- Revizyon politikası ve revizyon takvimi sayfaları.

Bütçe:

- Revizyon belgesi: en fazla 4 sayfa.
- Seri: en fazla 3 HTTP çağrısı.
- Toplam: en fazla 8 ağ erişimi.

Üçüncü taraf ayna, Wayback, ücretli/kimlikli erişim ve döngüsel scraping
yasaktır.

## 4. Haftalık seriden aylık origin özelliği

Haftalık seri `B(w)`, yayımlanan referans hafta bitiş tarihleriyle indekslenir.
Referans tarihleri tekil ve kesin artan olmalı; ardışık tarihler arasındaki fark
4–10 gün aralığında kalmalı ve toplam gözlem sayısı kaydedilmelidir. Cuma dışındaki
referans tarihleri hata sayılmaz: resmî tatil nedeniyle önceki iş gününe çekilen
haftalar ayrıca tatil adıyla eşleştirilir; eşleşmeyen kayma koşuyu durdurmaz, veri
kalitesi bayrağı olarak raporlanır.

Origin ayı `M` için çapa `w0(M)`, `M−2` ayının son takvim gününe eşit veya ondan
önce biten son yayımlanmış haftadır. `w0−k`, takvim aritmetiği değil yayımlanmış
hafta dizisinde `k` gözlem önceki haftadır.

Tam olarak dört feature:

1. `bddk_tasit_bakiye_4h_degisim_pct = (B(w0) / B(w0−4) − 1) × 100`
2. `bddk_tasit_bakiye_13h_degisim_pct = (B(w0) / B(w0−13) − 1) × 100`
3. `bddk_tasit_bakiye_52h_degisim_pct = (B(w0) / B(w0−52) − 1) × 100`
4. `bddk_tasit_bakiye_reel_4h_degisim_pct = ((1+n/100)/(1+p/100)−1)×100`
   - `n`: feature 1.
   - `p`: origin `M`'de `M−2` aylık değişimini taşıyan mevcut
     `tufe_aylik_degisim_lag2ay`.

TÜFE sütununun yüzde puanı mı oran mı tuttuğu mevcut feature hattından assert ile
doğrulanır; oran ise 100 ile çarpılır. Lag semantiği M−2 aylık değişim değilse
koşu durur. Doğrusal `n−p` kullanılmaz.

Her origin'de gerçekleşen 4/13/52 gözlemlik takvim aralığı raporlanır; nominal
28/91/364 günden 7 günden fazla sapma bayraklanır. Her feature için NaN sayısı
raporlanır; 2021-03 başlangıç origininde 52 haftalık geri bakışın varlığı assert
edilir. Beşinci feature eklenmez.

## 5. İki kollu tasarım

- Kol 1 kontrol: yalnız Model 11 `m09.FEATURELAR`.
- Kol 2 test: aynı feature'lar + yukarıdaki dört BDDK feature'ı.
- Aynı etiket penceresi/origin satırları, aynı seed, aynı permütasyon indeksleri,
  aynı fit prosedürü ve aynı permütasyon sayısı.
- Dört sabit konfigürasyon:
  - lojistik L2 C=0,1
  - lojistik L2 C=1
  - sığ Random Forest
  - sığ HistGradientBoosting

RF ve HGB `doygun=true` olarak raporlanır, karar kapısına girmez. Birincil okuma
iki lojistik konfigürasyondur.

Permütasyon bütçesi: 1.000 × 4 konfigürasyon × 2 kol = 8.000 fit. Koşu 40
dakikayı aşarsa iki kol birlikte 500'e indirilir ve JSON'a yazılır. Tek kol
indirilemez. 500 permütasyonla 60 dakika aşılırsa stop.

Tek-thread belirlenimciliği: `OMP_NUM_THREADS=1` ve eşdeğer BLAS thread
değişkenleri sabitlenir.

## 6. Kontrol kolu harness toleransı

Model 11 referansları:

| Konfigürasyon | Gözlenen | Null95 |
|---|---:|---:|
| lojistik_l2_c01 | 0,2147571548065723 | 0,4450343895977828 |
| lojistik_l2_c1 | 0,16897848477598726 | 0,4683733695252251 |
| random_forest_sigin | 0,9168817090818534 | 0,9155435038620596 |
| hist_gradient_sigin | 1,0 | 1,0 |

- Lojistikler: `|Δ|≤1e−9` geçer; `1e−9<|Δ|≤1e−6` geçer ve not edilir;
  `|Δ|>1e−6` stop/veto.
- RF: `|Δ|≤1e−6` geçer; üstü stop/veto.
- HGB: `|Δ|≤1e−6` geçer; `1e−6<|Δ|≤0,01` notla geçer; `>0,01` stop/veto.

Kontrol kolu geçmeden test kolu hükmü geçerli değildir.

## 7. Karar kapıları

Her konfigürasyon için:

- `marj = gozlenen − null95`
- `delta_marj = marj_kol2 − marj_kol1`

Doygun olmayan lojistik konfigürasyonlarda:

- `ON_ELEME_GECTI`: en az bir `marj ≥ +0,15`.
- `ON_ELEME_ZAYIF`: üstteki yok, en az bir `delta_marj ≥ +0,15`.
- `ON_ELEME_ISARET_YOK`: ikisi de yok.

Hüküm daima `tarama_kesinligi` ile birlikte yazılır.

## 8. Otonom devam

- `ON_ELEME_GECTI`: vintaj temini maliyeti gerekçelidir. `KESIN` ise as-of
  feature inşası + Model 10 protokolüne geçilir; aksi halde önce vintaj riski
  sınırlandırılır.
- `ON_ELEME_ZAYIF`: lojistik C=0,01 eklenmiş kapasite-düşürülmüş iki kollu tekrar
  taramasına, aynı seed ve permütasyonla otomatik geçilir.
- `ON_ELEME_ISARET_YOK`: BDDK **kapanmaz**, `ONCELIK_DUSURULDU` olur. Gerekçe:
  bu temsille işaret bulunmadı ve vintaj maliyetini şu an gerekçelendiren kanıt
  yok. Ardından yapısı gereği revizyona kapalı yeni bir öncü aileye geçilir.

BDDK yeniden açma koşulları:

1. Mesaj/ücret gerektirmeyen kamuya açık ilk-yayım vintajı bulunması.
2. BDDK'nın aynı mekanizma için revizyona kapalı kardeş gösterge yayımlaması.
3. Bu seriden değil dışarıdan gelen kanıtın maddi farklı dönüşümü gerekçelendirmesi.

## 9. Veto ve stop koşulları

- Kontrol kolu tolerans dışında.
- M−2 zaman kesimi veya TÜFE lag/birim assert'i ihlali.
- Post-hoc feature ekleme/çıkarma.
- Kollar arası seed, permütasyon veya fit asimetrisi.
- Sonucun performans/beceri diye sunulması.
- Ağ bütçesinde seri alınamaması.
- Ücret/kimlik veya dış iletişim gereksinimi.
- 500 permütasyonla 60 dakikayı aşma.
- Bağlayıcı sözleşme değişikliği gereksinimi.

## 10. Zorunlu artefaktlar

- `scripts/model/model_12_bddk_tavan_taramasi.py` ve gerekli testler.
- `data/processed/model/model_12_bddk_tavan_ozet.json`.
- `data/processed/raporlar/pm_rapor_bddk_tavan_taramasi.md` — yedi başlık.
- `notebooks/bddk_tavan_taramasi_ders_kitabi.ipynb`.

Ara BDDK serisi ve feature CSV'si commit edilmez. Hedef, sınıf, ±%5 band,
haftalık cari-ay nowcast, iki aylık bilgi disiplini ve kilitli test yasağı
değişmez. Kullanıcı dirty/untracked dosyalarına dokunulmaz.

## 11. Koşu öncesi takvim doğrulama düzeltmesi — 2026-08-08

Tam permütasyon koşusu ve herhangi bir model sonucu üretilmeden önceki ilk veri
doğrulamasında, 657 resmî BDDK gözleminin 26'sının Cuma yerine önceki iş gününde
kapandığı görüldü. Örnekler `2015-04-30` (1 Mayıs), `2024-04-09` (Ramazan
Bayramı) ve `2026-05-26` (Kurban Bayramı) haftalarıdır. Bu nedenle “bütün
tarihler Cuma” kabulü, Pusula'nın Opus/max denetimi ve `DEVAM_KABUL` kararıyla
yukarıdaki takvim doğrulama predikatına çevrildi.

Bu düzeltme yalnız yanlış olgusal Cuma kabulünü giderir. `w0` ve `w0−k`
konumsal indeksleme kuralları, karar eşikleri, dört feature, model
konfigürasyonları, 1.000 permütasyon, seed=410 ve harness toleransları
**değişmemiştir**. Konumsal aralıkların nominal süreden yedi günden fazla
sapma bayrakları da aynen korunmuştur. Düzeltme sonuç görülmeden yapıldı; yeniden
koşu ancak bu not, yeni doğrulama ve regresyon testi commit edildikten sonra
başlatılır.

## 12. Koşu öncesi uzun bayram haftası düzeltmesi — 2026-08-08

İlk takvim düzeltmesi commit edildikten, fakat yine herhangi bir model fit'i
veya sonuç üretilmeden önce, iki Kurban Bayramı çevresinde dört ardışık tarih
çifti `[4,10]` gün kapısının dışında kaldı:

- `2018-08-17 → 2018-08-20`: 3 gün
- `2018-08-20 → 2018-08-31`: 11 gün
- `2021-07-16 → 2021-07-19`: 3 gün
- `2021-07-19 → 2021-07-30`: 11 gün

Repo'nun daha önce 2429 sayılı Kanun ve Diyanet yıllık listeleriyle doğrulanmış
tatil takvimi Kurban Bayramı ilk günlerini sırasıyla `2018-08-21` ve
`2021-07-20` olarak sabitler. Pazartesi arife kapanışını izleyen uzun tatil,
her iki olayda mekanik `3+11=14` gün örüntüsü üretir. Pusula Opus/max
`DEVAM_KABUL` kararıyla yalnız yukarıdaki dört exact `(önceki, sonraki, gün)`
tuple'ı beyaz listeye alınmıştır. Diğer bütün ardışık tarihler `[4,10]`
aralığında kalmak zorundadır. Beyaz liste dört öğeden uzun olamaz; dördü de tam
resmî seride tüketilmeli, doğrulanmış tatil takvimine programatik bağlanmalı ve
her 3 günlük geçişi hemen 11 günlük geçiş izleyerek toplam 14 gün etmelidir.

Üçüncü ve son izinli seri çağrısının yanıtı model sonucu görülmeden yerel cache'e
kaydedildi: 657 satır, `2014-01-03..2026-07-31`, SHA-256
`4ED663DC373C6BB6C63A7A2D910D22408C574CF71210FFB9453E7EB087F030DE`.
Yeniden ağ çağrısı yasaktır; koşu bu cache'i yüklerken hash'i doğrular ve
uyuşmazlıkta durur. Ağ sayacı `seri=3`, `toplam=5` olarak raporlanır. Her
4/13/52-gözlem aralığı için 3/11 çiftini asimetrik kesen origin sayısı ve bu
originlerde gerçekleşen gün aralıkları ayrıca raporlanır; bu bir karar kapısı
değil dürüstlük kaydıdır. Karar eşikleri, dört feature, model konfigürasyonları,
seed=410, 1.000 permütasyon ve harness toleransları değişmemiştir.
