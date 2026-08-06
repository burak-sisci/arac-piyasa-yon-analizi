# PM Raporu — Haftalık Güncellenen Aylık Hacim Yönü Nowcast Veri Sözleşmesi

**Tarih:** 2026-08-06

**Dal:** `gelistirme/haftalik-aylik-nowcast` (yalnız yerel; push yapılmadı)

**Kapsam:** Model eğitimi öncesi veri/etiket/cut-off/split sözleşmesi ve gerçek
DF-A/DF-B üzerinde doğrulama. AutoGluon eğitimi ve performans iddiası YOKTUR.

## 1. Ne Yapıldı

1. Proje sahibinin kararı K10 olarak kaydedildi: target
   `noter_devir_otomobil_adet`, sınıflar `down/stable/up`; her pazartesi,
   önceki pazar cut-off'uyla cari ay kapanış yönü nowcast edilir.
2. `haftalik_aylik_nowcast.py` eklendi: cari ay M / önceki ay M-1 etiketi,
   pazar cut-off'ları, cut-off'a kadar günlük özetler, lag2/3/12 target,
   lag2 aylık feature, ay-eşit snapshot ağırlığı ve iki aylık embargo split'i.
3. `turkiye_tatil_takvimi.py` eklendi: 2018-2026 tam/yarım gün tatilleri,
   2429 sayılı Kanun ve Diyanet yıllık takvimlerine göre iş-günü eşdeğerine
   dahil edildi.
4. `model_07_haftalik_nowcast_veri_hazirligi.py` gerçek DF-A/DF-B üzerinde
   snapshot tablolarını ve denetim JSON'unu üretti. Veri çıktıları Git-dışıdır.
5. 29 yeni nowcast/tatil testi ile mevcut 21 değerlendirme testi birlikte
   çalıştırıldı: **50/50 geçti**.
6. Pusula kalıcı Claude Code oturumunda karar ortağı olarak kullanıldı. Stage
   1'i koşullu kabul etti; test döneminin şimdiden kilitlenmesini açıkça
   reddetti. Bu nedenle split yalnız taslak olarak tutuldu.

## 2. Sayısal Özet

| Ölçüm | DF-A | DF-B |
|---|---:|---:|
| Haftalık snapshot | 448 | 135 |
| Etiketli snapshot | 439 | 126 |
| **Bağımsız etiketli ay (etkin N)** | **101** | **29** |
| Down / Stable / Up | 35 / 26 / 40 | 9 / 9 / 11 |
| Feature sayısı | 22 | 29 |
| Ay başına toplam ağırlık min–maks | 1,0–1,0 | 1,0–1,0 |
| N≥50 durumu | Geçer | **Geçmez — keşifsel** |

DF-A taslak muhasebesi: 2019-01→2026-06 arası 90 model-uygun ay;
62 train + 2 embargo + 12 validation + 2 embargo + 12 test taslağıdır.
2018-02→2018-12 arasındaki **11 etiketli ay**, lag12 ısınma dönemi nedeniyle
model matrisine girmez. Test dönemi kilitli değildir.

## 3. Karşılaşılan Sorunlar

1. Noter target aylıktır ve kamuya açık kaynakta ay-içi kümülatif seri yoktur.
   Bu nedenle sistem kısmi-target ekstrapolasyonu değil, öncü-gösterge tabanlı
   cari-ay nowcast olarak tanımlandı.
2. Tarihsel kesin feature yayın tarihleri tabloda bulunmuyor. İlk sürümde tüm
   aylık feature'lara konservatif lag2 uygulandı; lag1 reddedildi.
3. Önceden ekonomik lag taşıyan faiz sütunlarına ayrıca yayın lag2 eklenince
   semantik çift-lag oluşuyordu. Pusula uyarısıyla bu sütunlar Stage 1 feature
   setinden çıkarıldı; ham/gerçek yayınlı faiz kaynağı daha sonra ayrı kurulmalı.
4. İlk hafta cari ayda henüz iş-günü gözlemi olmayabilir. Örneğin 2026-08-02
   pazar cut-off'unda cari-ağustos USD özeti boştur; önceki ay değeri forward
   fill edilmedi. Model bu eksikliği açık biçimde yönetmelidir.
5. DF-B yalnız 29 bağımsız ay içerir. Snapshot sayısının 135 olması etkin N'yi
   artırmaz; doğrulayıcı model iddiası yasaktır.

## 4. Veri Örneği

DF-A ilk üç snapshot (ham çıktıdan):

```csv
kesit_tarihi,tahmin_tarihi,hedef_ay,hafta_sirasi,etiket,agirlik,gecen_is_gunu,aydaki_is_gunu,usdtry_orta_son,noter_devir_otomobil_adet_lag2ay
2018-01-07,2018-01-08,2018-01,1,eksik,0.25,4.0,22.0,3.7634,
2018-01-14,2018-01-15,2018-01,2,eksik,0.25,9.0,22.0,3.79535,
2018-01-21,2018-01-22,2018-01,3,eksik,0.25,14.0,22.0,3.80015,
```

Son üç snapshot:

```csv
2026-07-19,2026-07-20,2026-07,3,eksik,0.25,12.0,22.0,47.00935,503057.0
2026-07-26,2026-07-27,2026-07,4,eksik,0.25,17.0,22.0,47.1892,503057.0
2026-08-02,2026-08-03,2026-08,1,eksik,1.0,0.0,21.0,,608484.0
```

## 5. Varsayımlar ve Kararlar

- **K10:** Etiket M/M-1 yüzde değişimi; kapalı ±%5 `stable` bandı.
- Haftalık ritim target frekansını değiştirmez; aynı ay snapshot'ları aynı
  fold'da ve toplam ağırlıkları 1'dir.
- Cari target ve lag1 kullanılmaz. Target yalnız lag2/3/12; aylık feature'lar
  ilk güvenli sürümde lag2'dir.
- Tahmin pazartesi üretilir, bilgi cut-off'u önceki pazardır.
- Birincil metrikler eğitimden önce global/Gorodkin MCC ve macro-F1 olarak
  sabitlenmiştir; majority, persistence ve t-12 mevsimsel baseline zorunludur.
- Tatil kaynağı: Diyanet'in yayımladığı [2429 sayılı Kanun](https://vakithesaplama.diyanet.gov.tr/2429_kanun.php)
  ve yıllık `resmitatiller.php?yil=YYYY` listeleri. Yarım günler 0,5 iş-günü
  azaltımıyla korunur.

## 6. Açık Sorular / PM Onayı Gerekenler

1. Taslak test dönemi **kilitli değildir**. Model eğitimi başlamadan önce
   rolling-origin fold sayısı ve nihai holdout stratejisi ayrıca kararlaştırılmalı.
2. Gerçek haftalık performansı artırmak için USD dışındaki yüksek frekanslı
   feature'lar (EUR, altın, haftalık taşıt kredisi faizi, platform içi trafik)
   yayın takvimiyle yeniden kurulmalıdır.
3. Noter/TÜİK'te ay-içi kümülatif devir verisi bulunursa ayrı kaynak olarak,
   gerçek as-of kanıtıyla değerlendirilmelidir; şu anda mevcut değildir.
4. Stable eşiği ±%5 K9'dan devralındı. Eşik optimizasyonu yapılacaksa yalnız
   train fold içinde ve duyarlılık analiziyle yapılmalıdır; test üzerinden
   ayarlanamaz.

## 7. Önerilen Sonraki Adım

Yüksek maliyetli model aramasına geçmeden önce ikinci küçük aşama önerilir:
(a) EUR/TRY ve haftalık taşıt kredisi faizini gerçek as-of tarihleriyle ekle,
(b) rolling-origin baseline'ları ve hafta-sırası bazlı metrikleri üret,
(c) ancak bundan sonra hafif modellerle ilk nowcast benchmark'ını çalıştır.
DF-B model seçimine sokulmaz; yalnız keşifsel karşılaştırma olarak korunur.
