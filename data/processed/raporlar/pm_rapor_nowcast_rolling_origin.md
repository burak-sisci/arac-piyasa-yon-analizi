# PM Raporu — Nowcast Rolling-Origin Performans Ölçümü

## 1. Ne Yapıldı

Pusula'nın `effort=max` düzeyinde önceden belirlediği protokol uygulandı.
`2019-01` başlangıçlı genişleyen train penceresi, her tahmin ayından önce iki
ay embargo ve tek aylık out-of-fold değerlendirme ile `2021-03..2025-04`
arasında 50 origin üretildi. Her origin'de ön işleme yeniden fit edildi.

Aynı üç baseline ve Model 09'da sabitlenmiş aynı dört düşük kapasiteli model
ölçüldü. Dört hafta havuzlandı; her hedef ayın toplam ağırlığı 1 tutuldu.
Birincil belirsizlik ölçümü 2.000 ortak indeksli, dört aylık hareketli-blok
bootstrap; i.i.d. ay-bootstrap yalnız duyarlılık analizidir. Dört modelin
`M-2 persistence` karşılaştırmasına Holm–Bonferroni uygulandı. Kilitli
`2025-07..2026-06` test dönemi açılmadı.

## 2. Sayısal Özet

| Yaklaşım | MCC | Blok %95 GA | Macro-F1 |
|---|---:|---:|---:|
| Train çoğunluğu | -0,0700 | -0,2965 .. 0,1237 | 0,2778 |
| Persistence M-2 | **0,0165** | **-0,1464 .. 0,2344** | **0,3642** |
| Seasonal t-12 | 0,0141 | -0,1375 .. 0,2416 | 0,3261 |
| Lojistik L2, C=0,1 | -0,0700 | -0,2053 .. 0,0961 | 0,2374 |
| Lojistik L2, C=1 | -0,0306 | -0,1954 .. 0,1385 | 0,2946 |
| Sığ Random Forest | -0,1193 | -0,2428 .. 0,0864 | 0,2407 |
| Sığ HistGradientBoosting | -0,1097 | -0,2729 .. 0,1009 | 0,2447 |

Dört modelin persistence karşısındaki ΔMCC değerleri `-0,0471` ile
`-0,1358` arasındadır. Dört macro-F1 farkı da negatiftir; Holm altında H0
reddi yoktur ve hiçbir model yıllık jackknife işaret koşulunu sağlamamıştır.
**Terfi yoktur.**

Pusula'nın resmî performans hükmü:

> 2021-03..2025-04 arasında, iki ay bilgi gecikmesi altında, test edilen yedi
> yaklaşımın hiçbiri — üç baseline dahil — aylık üç sınıflı yön hedefinde
> istatistiksel olarak gösterilebilir bir beceri sergilememiştir.

Bu hüküm yalnız mevcut DF-A snapshot feature'ları, dört sabit model, iki ay
bilgi gecikmesi ve belirtilen dönem için geçerlidir. ΔMCC güven aralığı yarı
genişlikleri 0,210–0,280 olduğundan yalnız büyük farklar ayırt edilebilir;
“modeller kanıtlı biçimde kötüdür” sonucu çıkarılamaz.

## 3. Karşılaşılan Sorunlar (saklanmaz)

1. İlk saf sklearn bootstrap uygulaması 300 saniyede zaman aşımına uğradı ve
   sonuç üretmedi. Aynı çekilişler/metrikler değiştirilmeden karışıklık matrisi
   vektörleştirildi; 68 test içinde sklearn referansına eşdeğerliği doğrulandı.
2. Hareketli bloklar dairesel değildir; son üç ay blok başlangıcı olamadığı
   için hafif eksik örneklenir. Ortak indeksli eşli farklarda etkisi sınırlıdır.
3. Gerçek sınıfı eksik blok çekilişi oranı `%0` oldu. Tahmin tarafında yalnız
   train-çoğunluğu için `%0,6` dejenere çekiliş oluştu; atılmadı, MCC=0
   davranışıyla hesapta ve denetim izinde tutuldu. Diğer yaklaşımlar `%0`.
4. ΔMCC aralıkları geniştir; saptanabilir fark büyüklüğü yaklaşık 0,21–0,28
   düzeyindedir. Küçük iyileşmeler hakkında hüküm üretilemez.
5. Hiçbir modelde hafta bilgisi Pusula kuralıyla doğrulanmadı. HGB'nin hafta
   MCC noktaları azalmayan olsa da hafta4−hafta1 CI alt sınırı tam `0,0`dır.

## 4. Veri Örneği (ham, ilk/son birkaç satır)

Rolling-origin tahmin çıktısından seçili satırlar:

| hedef ay | train ayı | hafta | yaklaşım | gerçek | tahmin |
|---|---:|---:|---|---|---|
| 2021-03 | 24 | 1 | persistence_m_eksi_2 | up | down |
| 2021-03 | 24 | 1 | seasonal_t_eksi_12 | up | down |
| 2021-03 | 24 | 1 | lojistik_l2_c01 | up | stable |
| 2025-04 | 73 | 4 | persistence_m_eksi_2 | up | down |
| 2025-04 | 73 | 4 | random_forest_sigin | up | stable |
| 2025-04 | 73 | 4 | hist_gradient_sigin | up | down |

Not: Tablo, Git'e girmeyen
`data/processed/model/model_10_rolling_origin_tahminleri.csv` çıktısının
denetim örneğidir.

## 5. Varsayımlar ve Kararlar (K/N kararlarına uygunluk)

- Target `noter_devir_otomobil_adet`, üç sınıf ve ana ±%5 stable bandı
  değiştirilmedi.
- Her origin M için train en geç M-3'te biter; M-2 ve M-1 embargo içindedir.
- 50 origin'de 50 ön işleme ve 200 model fit işlemi assertion ile doğrulandı.
- Bootstrap indeksleri tüm yaklaşım ve eşli farklarda ortaktır.
- MCC birincil; macro-F1 tanımlayıcıdır. Hafta sonuçları terfi gerekçesi değildir.
- Dört modelden oluşan tek ailede Holm–Bonferroni kullanıldı.
- Test `2025-07..2026-06` açılmadı ve kilitli kaldı.

## 6. Açık Sorular / PM Onayı Gerekenler

Model seçimine ilişkin açık karar yoktur: Pusula hiçbir adayın terfi
etmediğine hükmetmiştir. Asıl açık araştırma sorusu, mevcut target'ın iki ay
bilgi gecikmesi altında öğrenilebilir olup olmadığıdır. Stable bandı veya
bilgi gecikmesini değiştirmek bağlayıcı karar gerektirir; Model 11 yalnız
teşhis üretecek, bunları değiştirmeyecektir.

## 7. Önerilen Sonraki Adım (başlatılmaz, yalnızca önerilir)

Pusula'nın belirlediği tek yön Model 11 “hedef ve bilgi tavanı teşhisi”dir:
etiket paylarının zaman seyri/kırılmaları, yön geçiş matrisi ve lag yapısı,
stable-band duyarlılığı ve M-2'ye kadar geçmişi bilen fakat M-1/M'yi bilmeyen
oracle bilgi tavanı aynı test-dışı 50 origin üzerinde ölçülmelidir. Yeni model
adayı eklenmemeli ve test açılmamalıdır.
