# PM Raporu — Korelasyon Analizi Fazı: 4 Final Veri Seti

**Tarih:** 2026-08-04
**Kaynak scriptler:** `scripts/veri/genisletme_36` … `genisletme_41`
**Kapsam:** DF-A/DF-B v3'ten (Görev 29) başlayan, proje sahibinin adım adım
yönlendirdiği korelasyon analizi fazının tamamı — trend temizliği,
log-değişim veri setlerinin kurulması, faiz gecikme (lag) analizi, düşük
korelasyonlu ve çoklu-doğrusal (multicollinear) feature temizliği.

---

## 1. Ne Yapıldı

Bu faz, DF-A v3 (36 sütun) ve DF-B v3'ten (51 sütun) başlayarak sırasıyla:

1. **Sadeleştirme:** Döviz kuru alış/satış sütunları silindi (yalnızca
   ortalama kaldı), tüm takvim sütunları (`tarih` hariç) ve tüm
   `*_referans_ay` metin sütunları kaldırıldı.
2. **Log-değişim tartışması ve 2 yeni veri seti:** Ham seviye sütunların
   (kur, TÜFE, faiz, ODMD, OSD, tüketici güveni vb.) ortak trend taşıması
   nedeniyle sahte-korelasyon riski değerlendirildi (klasik zaman serisi
   istatistiğindeki "sahte regresyon" kavramına dayanarak). Bunun
   sonucunda **DF-A-log** ve **DF-B-log** adında iki YENİ veri seti
   kuruldu — target dahil trend taşıyan tüm sütunlar log-değişime
   çevrildi, zaten trend taşımayan sütunlar (TÜİK/ENAG/BETAM'ın kendi %
   değişim göstergeleri) olduğu gibi kopyalandı. Satır yapısı GÜNLÜK
   kaldı (aya indirgenmedi); aylık kaynaklı sütunların log-değişimi
   kendi takvim ayına göre hesaplanıp o ayın tüm günlerine yayıldı
   (adım/step fonksiyonu), günlük kaynaklar (USD/EUR) gerçek gün-gün
   log-değişim aldı.
3. **Faiz gecikme (lag) analizi — 4 sette:** `tasit_kredisi_faiz` ve
   `politika_faizi` (ham ve log-değişim halleriyle), DF-A/DF-A-log'da
   1-12 ay, DF-B/DF-B-log'da 1-6 ay gecikmeyle target'a karşı test
   edildi; her sütun için en yüksek |r| veren gecikme YENİ bir sütun
   olarak eklendi (orijinaller silinmedi).
4. **Düşük korelasyon temizliği:** Her 4 sette, target ile
   |Pearson r|<0,2 olan tüm sütunlar silindi.
5. **Çoklu-doğrusallık temizliği:** Her 4 sette, kendi aralarında
   |r|>0,9 olan sütun kümeleri bulunup, her kümede target ile en yüksek
   korelasyona sahip sütun tutuldu — bir istisnayla: matematiksel olarak
   birebir özdeş bir çift (`proxy_nominal_aylik_pct` ↔
   `proxy_aylik_log_degisim`, r=1,0000) için target korelasyonuna
   bakılmadı, veri setine sonradan eklenen silindi.
6. **Final korelasyon görselleri** üretildi (4 ısı haritası).

---

## 2. Sayısal Özet — Boyut Değişimi

| Set | Başlangıç (bu faz başında) | Final | Satır |
|---|---|---|---|
| DF-A | 36 sütun | **9 sütun** | 4234 |
| DF-B | 51 sütun | **16 sütun** | 947 |
| DF-A-log | (yeni kuruldu, 18) | **6 sütun** | 4234 |
| DF-B-log | (yeni kuruldu, 29) | **10 sütun** | 947 |

**Final sütun listeleri ve target korelasyonları (Pearson r):**

**DF-A** (target: `noter_devir_toplam_adet`):
| Sütun | r_target |
|---|---|
| `usdtry_orta` | 0,6205 |
| `tufe_aylik_degisim` | 0,2780 |
| `tufe_yillik_degisim` | 0,4192 |
| `noter_devir_otomobil_adet` | 0,9829 |
| `odmd_otomobil_adet` | 0,4633 |
| `tuketici_guven_endeksi` | -0,3779 |
| `tasit_kredisi_faiz_lag12ay` | 0,5746 |

**DF-B** (target: `noter_devir_toplam_adet`):
| Sütun | r_target |
|---|---|
| `tufe_aylik_degisim` | -0,2910 |
| `tufe_yillik_degisim` | -0,3072 |
| `enag_aylik_degisim` | -0,2774 |
| `noter_devir_otomobil_adet` | 0,9815 |
| `odmd_hta_adet` | 0,6322 |
| `osd_binek_adet` | 0,2545 |
| `otomobil_satinalma_ihtimali_endeksi` | 0,2094 |
| `proxy_dom_gun` | -0,4052 |
| `proxy_satis_orani_pct` | 0,7693 |
| `proxy_nominal_yillik_pct` | -0,2330 |
| `proxy_talep_aylik_pct` | 0,3852 |
| `proxy_reel_aylik_log_degisim` | 0,3562 |
| `tasit_kredisi_faiz_lag4ay` | 0,2585 |
| `politika_faizi_lag5ay` | 0,2253 |

**DF-A-log** (target: `noter_devir_toplam_adet_log_degisim`):
| Sütun | r_target |
|---|---|
| `noter_devir_otomobil_adet_log_degisim` | 0,9959 |
| `odmd_hta_adet_log_degisim` | 0,5065 |
| `osd_binek_adet_log_degisim` | 0,5416 |
| `otomobil_satinalma_ihtimali_endeksi_log_degisim` | 0,2164 |

**DF-B-log** (target: `noter_devir_toplam_adet_log_degisim`):
| Sütun | r_target |
|---|---|
| `noter_devir_otomobil_adet_log_degisim` | 0,9944 |
| `odmd_hta_adet_log_degisim` | 0,5832 |
| `osd_kamyonet_adet_log_degisim` | 0,4574 |
| `proxy_satis_orani_pct` | 0,3270 |
| `proxy_talep_aylik_pct` | 0,7445 |
| `proxy_nominal_aylik_pct` | -0,5514 |
| `proxy_reel_aylik_log_degisim` | -0,2465 |
| `politika_faizi_log_degisim_lag3ay` | 0,3569 |

---

## 3. Karşılaşılan Sorunlar

1. **[EN ÖNEMLİ BULGU] Faiz-target ilişkisi, ham seviyede güçlü ama
   trend-arındırılmışta neredeyse yok oluyor.** DF-A'da
   `tasit_kredisi_faiz`'in ham hali target ile 0,57 (12 ay gecikmeli)
   korelasyon gösterirken, log-değişim hali yalnızca -0,18 (ve işaret
   TERSİNE dönüyor). Bu, ham-seviye ilişkinin büyük ölçüde ortak trend
   (yıllar içinde hem faiz hem nominal noter devri arttı) kaynaklı
   olduğunu, gerçek bir nedensellik olmayabileceğini gösteriyor. Aynı
   örüntü USD/EUR kurları için de gözlendi (DF-A/DF-B'de ~0,6/~0,2
   iken, DF-A-log/DF-B-log'da ~0,005-0,009'a düşüp elendi).
2. **Bir turda yanlış anlama yaşandı ve düzeltildi:** DF-A-log/DF-B-log
   kurulurken "günlük frekans" talebi ilk yorumda TÜM sütunların gün-gün
   log-değişimine çevrilmesi olarak anlaşıldı; doğrusu satır yapısının
   zaten hep günlük kaldığı, yalnızca aylık kaynaklı sütunların
   log-değişiminin AYA göre hesaplanıp güne yayılması gerektiğiydi. Script
   düzeltilip diskteki (doğru) çıktıyla tutarlı hale getirildi, veri
   kaybı olmadı.
3. Teknik bir hata/veri bütünlüğü sorunu çıkmadı — her adımda tarih
   tekilliği ve satır sayısı korunumu doğrulandı.

---

## 4. Veri Örneği

DF-A-log'da `noter_devir_toplam_adet_log_degisim`, 2020-06 ayı için tüm
gün boyunca sabit (0,670047), `usdtry_orta_log_degisim` ise gün-gün
değişiyordu (bu sütun artık final sette YOK, düşük korelasyon nedeniyle
elendi, ama yöntemi doğrulamak için kullanılan orijinal örnekti).

Final DF-A-log'dan gerçek bir satır (`tarih=2020-06-15`):
`noter_devir_otomobil_adet_log_degisim`, `odmd_hta_adet_log_degisim`,
`osd_binek_adet_log_degisim`, `otomobil_satinalma_ihtimali_endeksi_log_degisim`
— hepsi o ayın (2020-06) sabit değerini taşıyor (kod ile doğrulandı).

---

## 5. Varsayımlar ve Kararlar

1. **Kapsama testi granülerliği (Görev 29'dan miras):** Aylık kaynaklı
   sütunlar için korelasyon hesaplaması, `referans_ay` sütunları
   kaldırıldığı için artık `tarih`'in kendi takvim ayı (`%Y-%m`) üzerinden
   yapılıyor — tasarım gereği (Görev 26/28) bu her zaman doğru referans
   ayı verir.
2. **Log-değişim formülü:** `ln(x_t/x_{t-1})`, aylık kaynaklarda kendi
   takvim ayına göre (ardışık AY, ardışık gün değil), günlük kaynaklarda
   (USD/EUR) ardışık GÜN'e göre.
3. **Multicollinearity tie-break:** Varsayılan kural "kümede target ile
   en yüksek |r|'ye sahip olanı tut" — proje sahibiyle görüşülüp kabul
   edildi. Tek istisna: matematiksel özdeş çiftlerde (r=1,0000) target
   korelasyonuna bakılmadı, sonradan eklenen sütun silindi.
4. **Faiz-lag özellikleri EKLENDİ, orijinaller SİLİNMEDİ** — önceki
   turda (geri alınan) "kazananı tut, diğerini sil" yaklaşımından farklı
   olarak, bu kez hem ham hem gecikmeli faiz sütunları bir arada
   tutuldu; ancak Görev 40'ın çoklu-doğrusallık temizliği bu ikisini de
   aynı kümede bulup birini elemiş olabilir (DF-A'da `tasit_kredisi_faiz`
   ve `politika_faizi`'nin ham halleri bu adımda zaten silindi, yalnızca
   `tasit_kredisi_faiz_lag12ay` kaldı).

---

## 6. Açık Sorular / PM Onayı Gerekenler

1. **DF-A ve DF-A-log artık çok küçük** (9 ve 6 sütun) — kalan
   feature'ların çoğu ya `noter_devir_otomobil_adet` (target'ın
   neredeyse birebir bir alt-kırılımı, r=0,98-0,99 — kendi başına ayrı
   bir "sızıntı" riski taşıyabilir, target'ın parçası gibi davranıyor)
   ya da tek tük başka göstergeler. Bu, modelleme için yeterli bir
   feature seti mi, yoksa bazı elenen sütunlar (özellikle |r| eşiği
   0,2'ye çok yakın olanlar, ör. DF-A'da elenen `osd_*` grubu) geri mi
   alınmalı?
2. **`noter_devir_otomobil_adet`'in çok yüksek target korelasyonu**
   (0,98-0,99 dört sette de) — bu beklenen bir durum (aynı ailenin
   alt-kırılımı) ama modelleme aşamasında "sızıntıya çok yakın" bir
   feature olarak ele alınmalı, ayrı bir karar gerektirebilir.
3. Başka açık soru yok — talimatlar adım adım uygulandı, her adımda
   sonuç raporlandı.

---

## 7. Önerilen Sonraki Adım (başlatılmadı, yalnızca öneri)

4 final veri seti artık modellemeye hazır durumda. Önerilen sıradaki
adımlar: (a) DF-A/DF-A-log'un küçük feature sayısı nedeniyle eşik
değerlerinin (0,2 / 0,9) gözden geçirilmesi, (b)
`noter_devir_otomobil_adet`'in target ile ilişkisinin modelleme
tasarımında nasıl ele alınacağının netleştirilmesi, (c) zaman serisi
modelleme fazına geçiş.
