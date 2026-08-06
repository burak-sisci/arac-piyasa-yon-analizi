# PM Raporu — Model 11 Hedef ve Bilgi Tavanı

## 1. Ne Yapıldı

Pusula'nın sonuçlardan önce kilitlediği Model 11 protokolü uygulandı:

- `2019-01..2025-04` etiket rejimi ve üç kaynaklı dış kırılma ölçüldü.
- Geçiş matrisi, lag 1/2/3/12 yapısı ve aynı 50 origindeki persistence
  kuralları analiz edildi.
- ±2,5 / ±3,5 / ±5 / ±7,5 / ±10 stable-band duyarlılığında yalnız üç
  parametresiz baseline çalıştırıldı; dört model yeniden fit edilmedi.
- M-1/M bilgisini dışlayan Oracle-A durum tavanları ve aynı dört sabit
  konfigürasyonun Oracle-B in-sample tavanları kendi permütasyon null95
  düzeyleriyle karşılaştırıldı.
- Test açılmadı, target/sınıflar/K maddeleri değiştirilmedi.

### Ön-kayıt ve görev ayrımı

- Pusula: süreç yönetimi, yöntem seçimi, eşikler, kabul/ret koşulları ve nihai
  performans hükmü.
- Rota: kodlama, veri hazırlığı, test, uzun koşular, dokümantasyon ve Git.
- Ön-kayıt commit'i: `c1b3c6f`. Eşik listesi, üç dış kırılma tarihi, oracle
  durum uzayları, permütasyon sayıları ve A/B/C/D hüküm kuralları sonuçlar
  görülmeden bu commit'te sabitlendi.
- Model 11 uygulama dosyaları: `scripts/model/hedef_teshis.py` ve
  `scripts/model/model_11_hedef_bilgi_tavani.py`.

### Veri ve zaman kapsamı

- Aylık target kaynağı: `df_a_v3_noter_penceresi_2015_bugun.csv` içindeki
  `noter_devir_otomobil_adet`.
- Etiket analizi: `2019-01..2025-04`, 76 ay.
- Rolling-origin teşhisi: `2021-03..2025-04`, 50 bağımsız hedef ayı.
- İlk/son train büyüklüğü: 24/73 ay; her origin M için train sonu ≤M-3.
- `2025-05/06` embargo, `2025-07..2026-06` kilitli test.

### Hesaplama protokolü

- Blok güven aralıkları: hareketli blok uzunluğu 4 ay, 2.000 çekiliş,
  sabit seed ve karşılaştırılan yöntemlerde ortak indeksler.
- Kırılma/geçiş/lag bağımsızlık testleri: 10.000 permütasyon.
- Kırılma ailesi: üç dış tarih üzerinde Holm–Bonferroni, α=0,05.
- Lag ailesi: lag 1/2/3/12 üzerinde Holm–Bonferroni, α=0,05.
- Oracle-A null: 2.000 permütasyon; Oracle-B null: ön-kayıtlı maliyet
  indirimiyle 1.000 permütasyon × dört sabit model = 4.000 yeniden fit.
- Oracle-B etiketi bilerek in-sample kullanır; bu bir üretim skoru değil,
  temsilin ezber-düzeltilmiş üst tavan teşhisidir.

## 2. Sayısal Özet

- Lag-1 persistence: MCC `-0,020`, %95 GA `[-0,262; 0,154]`;
  operasyonel değildir ve yalnız teşhistir.
- Lag-2: MCC `0,0165`, GA `[-0,151; 0,239]`.
- Geçiş bağımsızlığı: V=`0,098`, permütasyon p=`0,845`.
- Hiçbir lag Holm sonrası anlamlı değildir.
- Hiçbir stable-band `maddi_farkli` koşulunu sağlamadı.
- Oracle gözlenen/null95: S1 `0,170/0,287`; S2 `0,238/0,343`;
  lojistikler `0,215/0,445` ve `0,169/0,468`; RF `0,917/0,916`; HGB `1/1`.
- Hiçbir oracle null95'i ön-kayıtlı `0,15` marjla aşmadı.

Pusula'nın resmî hükmü: **A — mevcut bilgi temsilleri altında, iki ay
gecikmeli aylık üç-sınıf hedefte saptanabilir öngörü becerisi yoktur.**

### Yıl bazında ana ±%5 sınıf payları

| Yıl | N | Down | Stable | Up |
|---:|---:|---:|---:|---:|
| 2019 | 12 | %25,0 | %25,0 | %50,0 |
| 2020 | 12 | %66,7 | %8,3 | %25,0 |
| 2021 | 12 | %41,7 | %0,0 | %58,3 |
| 2022 | 12 | %16,7 | %8,3 | %75,0 |
| 2023 | 12 | %41,7 | %41,7 | %16,7 |
| 2024 | 12 | %25,0 | %33,3 | %41,7 |
| 2025 | 4 | %50,0 | %0,0 | %50,0 |

Yıllar arasında görünür kompozisyon değişimi vardır; ancak tablo tanımlayıcıdır
ve tek başına kırılma testi değildir.

### Çoğunluk kuralları ve bayat önsel teşhisi

| Kural | MCC | Blok %95 GA |
|---|---:|---:|
| Sabit down | 0,000 | 0,000 .. 0,000 |
| Sabit stable | 0,000 | 0,000 .. 0,000 |
| Sabit up | 0,000 | 0,000 .. 0,000 |
| Genişleyen train çoğunluğu R1 | -0,070 | -0,306 .. 0,122 |
| M-3 itibarıyla son-12-ay çoğunluğu R2 | 0,063 | -0,164 .. 0,280 |
| M-3 itibarıyla son-6-ay çoğunluğu R3 | 0,065 | -0,127 .. 0,264 |

R1<R0 ve R2/R3>R1 olduğu için ön-kayıtlı yönsel `bayat_onsel_dogrulandi`
bayrağı açılmıştır. Bununla birlikte R1 yalnız üç kez sınıf değiştirmiş ve
tüm belirsizlik aralıkları sıfırı içerdiği için ayrıca
`bayat_onsel_gurultu_uyarisi=true` yazılmıştır. Mekanizma tutarlı görünür,
istatistiksel olarak kurulmuş değildir.

### Ön-kayıtlı dış kırılma testleri

| Aday tarih | Dış olay | Cramér's V | Ham perm. p | Holm p | Holm reddi |
|---|---|---:|---:|---:|---|
| 2020-03 | WHO pandemi nitelemesi | 0,130 | 0,552 | 0,656 | Hayır |
| 2021-12 | Kur korumalı mevduat başlangıcı | 0,177 | 0,328 | 0,656 | Hayır |
| 2023-02 | Kahramanmaraş depremleri | 0,290 | 0,046 | 0,138 | Hayır |

Şubat 2023 ham p<0,05 üretse de üç tarih ailesinde Holm sonrasında eşik
sağlanmaz. Serbest tarih taraması veya alternatif tarih denemesi yapılmadı.

### Geçiş matrisi

Yön açıkça `satır=önceki ay`, `sütun=cari ay` olarak kaydedildi.

| Önceki \ Cari | Down | Stable | Up | Satır N |
|---|---:|---:|---:|---:|
| Down | 10 (%35,7) | 4 (%14,3) | 14 (%50,0) | 28 |
| Stable | 5 (%35,7) | 2 (%14,3) | 7 (%50,0) | 14 |
| Up | 12 (%36,4) | 8 (%24,2) | 13 (%39,4) | 33 |

Geçiş bağımsızlığı: χ²=1,442; V=0,098; 10.000 permütasyon p=0,845.
Önceki sınıfın cari sınıfı açıkladığına dair kanıt yoktur.

### Lag bağımlılığı ve persistence performansı

| Lag | Cramér's V | V blok %95 GA | Ham p | Holm p | Persistence MCC | MCC blok %95 GA | Operasyonel? |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0,098 | 0,062 .. 0,330 | 0,845 | 1,000 | -0,020 | -0,262 .. 0,154 | Hayır |
| 2 | 0,216 | 0,119 .. 0,394 | 0,144 | 0,576 | 0,0165 | -0,151 .. 0,239 | Evet |
| 3 | 0,117 | 0,076 .. 0,368 | 0,740 | 1,000 | 0,0165 | -0,189 .. 0,217 | Evet |
| 12 | 0,116 | 0,078 .. 0,309 | 0,803 | 1,000 | 0,0141 | -0,147 .. 0,241 | Evet |

V negatif olamadığı için V güven aralıkları bağımsızlık testi değildir;
istatistiksel hüküm permütasyon p ve Holm'a dayanır. Lag-1 hedef ayı M için
M-1 etiketini gerektirdiğinden operasyonel değildir; yalnız “gecikme ortadan
kalksaydı” teşhisidir ve bu teşhis de beceri göstermemiştir.

### Stable-band duyarlılığı — model refit edilmeden

| Band | Down/Stable/Up payı | M-2 MCC | Blok %95 GA | Ana ±%5'e ΔMCC | Seasonal M-12 | Train çoğunluğu | Maddi farklı? |
|---:|---|---:|---:|---:|---:|---:|---|
| ±%2,5 | %43,4 / %6,6 / %50,0 | 0,0099 | -0,155 .. 0,252 | -0,0066 | 0,0787 | -0,0764 | Hayır |
| ±%3,5 | %38,2 / %14,5 / %47,4 | -0,0785 | -0,225 .. 0,133 | -0,0950 | 0,1127 | -0,0543 | Hayır |
| ±%5,0 | %36,8 / %18,4 / %44,7 | 0,0165 | -0,151 .. 0,239 | 0,0000 | 0,0141 | -0,0700 | Ana |
| ±%7,5 | %31,6 / %32,9 / %35,5 | -0,0297 | -0,209 .. 0,179 | -0,0462 | 0,0763 | -0,0897 | Hayır |
| ±%10,0 | %30,3 / %38,2 / %31,6 | -0,0996 | -0,274 .. 0,102 | -0,1161 | 0,1584 | -0,0211 | Hayır |

Hiçbir stable payı %60'ı aşmadı; `mcc_yorumlanamaz` bayrağı açılmadı.
`maddi_farkli` için gereken iki koşulu (ΔMCC≥0,10 ve CI altı>0) hiçbir bant
sağlamadı. Seasonal ±%10 değeri post-hoc gözlemdir; bu kapının parçası değildir.

### Oracle-A — etiket durum uzayı

| Durum | Durum sayısı | Ortalama hücre N | Minimum hücre N | Gözlenen | Null95 | Gözlenen-null95 |
|---|---:|---:|---:|---:|---:|---:|
| S0 sabit | 1 | 50,0 | 50 | 0,000 | 0,000 | 0,000 |
| S1 y(M-2) | 3 | 16,7 | 10 | 0,170 | 0,287 | -0,118 |
| S2 y(M-2) × M-3 stable/stable-değil | 6 | 8,3 | 2 | 0,238 | 0,343 | -0,105 |

S2'nin bazı hücreleri küçüktür; ön-kayıtlı kısıt minimum hücre değil, durum
başına ortalama N≥8 ve durum sayısı≤6 idi. İki koşul da sağlandı ve minimum
hücre N=2 dürüstçe raporlandı.

### Oracle-B — mevcut dört konfigürasyonun in-sample tavanı

| Konfigürasyon | Gözlenen MCC | Null95 | Fark | Null tekrar |
|---|---:|---:|---:|---:|
| Lojistik L2 C=0,1 | 0,215 | 0,445 | -0,230 | 1.000 |
| Lojistik L2 C=1 | 0,169 | 0,468 | -0,299 | 1.000 |
| Sığ Random Forest | 0,917 | 0,916 | +0,0013 | 1.000 |
| Sığ HistGradientBoosting | 1,000 | 1,000 | 0,000 | 1.000 |

RF ve HGB yüksek skorları bilgi tavanı kanıtı değildir: karıştırılmış etiket
null'ı aynı seviyede ezberlenir. Ön-kayıtlı C hükmü için farkın en az 0,15
olması gerekiyordu; hiçbir konfigürasyon sağlamadı.

## 3. Karşılaşılan Sorunlar (saklanmaz)

1. İlk A/C hüküm tanımı `(0; 0,15)` ölü bölgesi bırakmıştı. RF null95'i
   yalnız `0,0013` aştığında hiçbir bayrak ateşlenmedi. Pusula kendi ön-kayıt
   kusurunu C'nin tümleyeni olarak kapattı; düzeltme negatif hükme çıkar.
2. İlk geçiş-matrisi JSON'u `DataFrame.to_dict()` nedeniyle devrik sunuldu.
   Hesap değişmeden `orient=index` ve açık yön alanıyla düzeltildi; satırlar 1.
3. Cramér's V ≥0 olduğu için bootstrap CI sıfır testi değildir. Her V aralığı
   `bagimsizlik_testi_degil=true` taşır; hüküm permütasyon p/Holm'a dayanır.
4. Lag çiftleri 2019 penceresi içinde shift edildi; 2018 warmup kullanılmadı.
   Bu sızıntı değil, muhafazakâr kapsam kaybıdır.
5. Oracle-B ilk ve düzeltme sonrası yeniden üretimlerde 4.000'er fit gerektirdi;
   çalışma yaklaşık 9–12 dakika sürdü. Permütasyon sayısı azaltılmadı.
6. ±%10 seasonal MCC=0,158 post-hoc dikkat çekicidir; ön-kayıtlı karar kapısı
   persistence içindi. Bu sonuç terfi veya K önerisi yapılmadı.
7. Oracle-B permütasyon maliyeti nedeniyle ilk koşu 561,5 saniye, zorunlu
   sunum/mantık düzeltmeleri sonrası tam yeniden üretim 719 saniye sürdü.
8. Oracle-B'nin 1.000 permütasyon sayısı Pusula tarafından sonuçlardan önce
   hesap maliyeti istisnası olarak izin verilmiş ve JSON'da açıkça yazılmıştır.

## 4. Veri Örneği (ham, ilk/son birkaç satır)

50-origin teşhis CSV'sinden seçili satırlar:

| hedef ay | gerçek | genişleyen çoğunluk | son-12 çoğunluk | lag1 | lag2 | lag12 |
|---|---|---|---|---|---|---|
| 2021-03 | up | down | down | up | down | down |
| 2021-04 | down | down | down | up | up | down |
| 2021-05 | down | down | down | down | up | up |
| 2025-02 | down | up | up | down | up | up |
| 2025-03 | up | up | up | down | down | stable |
| 2025-04 | up | up | up | up | down | down |

Bu tablo Git'e girmeyen `model_11_origin_teshisleri.csv` çıktısından denetim
örneğidir; commit öncesi kaynak satırlarla yeniden kontrol edilmiştir.

### Üretilen çalışma çıktıları

Git'e girmeyen, yeniden üretilebilir model çıktıları:

- `model_11_hedef_teshis_ozet.json`: tüm metrik, CI, permütasyon, oracle ve
  A/B/C/D hüküm bayrakları.
- `model_11_yillik_sinif_paylari.csv`: yıl bazlı sınıf payları.
- `model_11_kayan12_sinif_paylari.csv`: her ay için geçmiş 12 aylık paylar.
- `model_11_origin_teshisleri.csv`: 50 origin gerçekleri ve R1/R2/R3 ile
  lag-1/2/3/12 tahminleri.

Git'e giren denetim çıktıları:

- Bu PM raporu.
- `docs/10_asama_b_nowcast_kapanis_sentezi.md`.
- Ön-kayıt `prompts/veri/36_model11_hedef_bilgi_tavani_onkayit.md`.
- Uygulama ve test kodu.

## 5. Varsayımlar ve Kararlar (K/N kararlarına uygunluk)

- Ana target, üç sınıf, cari ay nowcast'i ve ±%5 bandı değişmedi.
- M-1/M oracle feature'larından assertion ile dışlandı.
- Oracle-B'nin etiketi in-sample kullanması bilinçli üst-tavan avantajıdır;
  sonuçlar Model 10 OOF skorlarıyla değil yalnız permütasyon null'ıyla kıyaslandı.
- Durum uzayı ≤6 ve ortalama hücre N≥8 doygunluk kısıtı korundu.
- Test `2025-07..2026-06` açılmadı ve kilitli kaldı.
- Pusula süreç yönü ve performans hükmünü verdi; Rota yalnız uyguladı.

### Kabul kriteri denetimi

| Kriter | Sonuç |
|---|---|
| Analiz 2025-04'te biter | Geçti; assertion var |
| Test ve 2025-05/06 okunmaz | Geçti; çıktı `ACILMADI_KILITLI` |
| M-1/M oracle feature'larında yok | Geçti; bilgi maskesi testli |
| Oracle durum sayısı≤6, ortalama N≥8 | Geçti |
| Lag-1 operasyonel dışı işaretli | Geçti |
| Band analizinde model fit yok | Geçti; her bantta `model_fit_sayisi=0` |
| Permütasyon seed deterministik | Geçti; birim test var |
| Geçiş satırları 1'e toplamlanır | Geçti; test ve yeniden kontrol |
| Mevcut test paketi | 74/74 geçti |
| Yeni K veya hedef değişikliği | Yapılmadı |

## 6. Açık Sorular / PM Onayı Gerekenler

Kullanıcı kararı gereken üç seçenek vardır:

1. Negatif bulguyla bu hedef için projeyi kapatmak.
2. Target/üç sınıfı koruyup bilgi kümesini yeni öncü verilerle değiştirmek.
3. Ufuk/toplulaştırma veya sınıf sayısını değiştirmek.

Hiçbiri uygulanmamıştır. Üçüncü seçenek mevcut kullanıcı sabitini değiştirir;
açık bağlayıcı karar olmadan başlatılamaz.

### Kullanıcı kararında etkiler ve maliyetler

- **Kapat:** Mevcut negatif kanıt korunur; ek veri/model maliyeti yoktur.
- **Bilgi kümesini değiştir:** Target ve üç sınıf sabit kalabilir; yeni resmi
  veya kamuya açık yüksek frekanslı araç-piyasası sinyalleri için veri
  araştırması, as-of kayıt ve yeni ön-kayıt gerekir.
- **Hedef spesifikasyonunu değiştir:** Ufuk/toplulaştırma veya sınıf sayısı
  değişir; kullanıcının sabit hedef kararını etkilediğinden en yüksek karar
  maliyetli seçenektir. Mevcut analiz hangi yeni tanımın iyi olduğunu ölçmedi.

## 7. Önerilen Sonraki Adım (başlatılmaz, yalnızca önerilir)

Pusula'nın kararı doğrultusunda yeni ölçüm ve model araması durdurulur.
`docs/10_asama_b_nowcast_kapanis_sentezi.md` kullanıcıya karar paketi olarak
sunulur. Kullanıcı seçim yapana kadar test açılmaz ve yeni çalışma başlatılmaz.
