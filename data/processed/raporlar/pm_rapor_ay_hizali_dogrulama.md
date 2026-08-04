# PM Raporu — Ay-Hizalı Doldurma Yönteminin Bağımsız Doğrulaması (Görev 28)

**Tarih:** 2026-08-04
**Prompt arşivi:** `prompts/28_ay_hizali_doldurma_dogrulama_prompt.md`
**Doğrulanan çıktı:** `data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv`
**Doğrulanan üretim kodu:** `scripts/veri/genisletme_26_forward_fill_gunluk.py`
(yalnızca OKUNDU/test edildi — bu görevde YENİDEN YAZILMADI)

Bu görev bir **üretim** görevi değil, **bağımsız doğrulama** görevidir:
mevcut çıktı dosyası, kaynağı olduğu ham verilerle karşılaştırılarak
kod dışından (ayrı, tek seferlik Python sorgularıyla) test edildi. Hata
bulunursa yalnızca raporlanacaktı, otomatik düzeltme yapılmayacaktı —
**hiçbir hata bulunmadı**, bu yüzden düzeltme gerekmedi.

---

## 1. Hangi Dosya/Yöntem Doğrulandı, 26 Numaralı Görevden Farkı

Doğrulanan dosya: `df_gunluk_forward_fill_2015_bugun.csv` — bu, **26
numaralı görevin dosyasının YERİNE GEÇEN** (üçüncü bir ek tablo DEĞİL)
güncel/düzeltilmiş halidir. Aynı dosya adı, aynı konum; içindeki üretim
mantığı proje sahibinin netleştirmesiyle değiştirildi.

**26 numaralı görevin İLK (yanlış anlaşılan) versiyonu:** her aylık
kaynağın değeri, o kaynağın **as-of/yayım tarihinden** itibaren bir
sonraki as-of tarihine kadar ileri taşınıyordu (`.ffill()`). Bu, bir
ayın değerinin çoğunlukla **bir SONRAKİ takvim ayının günlerine**
yazılması anlamına geliyordu (çünkü as-of tarihi genelde "referans ayın
bir sonraki ayının 1. günü" olarak tanımlanmıştı).

**Şu an doğrulanan (düzeltilmiş) versiyon:** her aylık kaynağın değeri,
**doğrudan kendi referans ayının takvim günlerine** yazılıyor —
açıklanma/yayım tarihinin bu dağıtımla hiçbir ilgisi yok. Ocak'ın değeri
Ocak'ın 1-31'ine, Şubat'ın değeri Şubat'ın 1-28/29'una yazılıyor.

Bu iki yöntem **farklı kurallar, farklı sonuçlar** üretir — Bölüm 3'te
somut bir örnekle gösteriliyor.

---

## 2. 5 Örnek Doğrulama Sonucu

Farklı kaynaklardan ve farklı dönemlerden (erken/orta/güncel) 5 ay-sütun
çifti seçildi; her biri için ham kaynaktaki değer, tablodaki o ayın TÜM
günlerinin taşıdığı değerle karşılaştırıldı:

| Kaynak | Sütun | Ay | Ham kaynak değeri | Tabloda (ay içi benzersiz değer) | Ay içi gün sayısı | Eşleşme |
|---|---|---|---|---|---|---|
| Noter devri | noter_devir_toplam_adet | 2016-03 | 659681 | 659681.0 | 31 | ✅ |
| TÜFE | tufe_endeks | 2020-09 | 477.21 | 477.21 | 30 | ✅ |
| ODMD | odmd_otomobil_adet | 2026-05 | 65386.0 | 65386.0 | 31 | ✅ |
| Proxy fiyat (BETAM) | proxy_fiyat_cari_tl | 2024-07 | 862232.0 | 862232.0 | 31 | ✅ |
| Tüketici güveni | tuketici_guven_endeksi | 2018-11 | 80.94738021 | 80.94738021 | 30 | ✅ |

**5/5 tam eşleşme.** Her ayın TÜM günlerinde tek ve aynı değer var, hiçbiri
ham kaynaktan sapmıyor.

**Ay sınırı kontrolü** (bir önceki ayın son günü → bu ayın ilk günü,
aynı 5 çift üzerinde):

| Sütun | Önceki ayın son günü | Değer | Yeni ayın ilk günü | Değer | Değişti mi |
|---|---|---|---|---|---|
| noter_devir_toplam_adet | 2016-02-28 | 519089.0 | 2016-03-01 | 659681.0 | ✅ Evet |
| tufe_endeks | 2020-08-31 | 472.61 | 2020-09-01 | 477.21 | ✅ Evet |
| odmd_otomobil_adet | 2026-04-30 | 80182.0 | 2026-05-01 | 65386.0 | ✅ Evet |
| proxy_fiyat_cari_tl | 2024-06-30 | 871156.0 | 2024-07-01 | 862232.0 | ✅ Evet |
| tuketici_guven_endeksi | 2018-10-31 | 78.41815398 | 2018-11-01 | 80.94738021 | ✅ Evet |

**5/5 doğru geçiş.** Değer, takvim ayı değiştiği ANDA değişiyor —
açıklanma tarihine bakılmaksızın.

---

## 3. 26-Numaralı (Eski) Yöntemle Fark Gösteren Somut Örnek

Eski yöntemin davranışını (as-of tarihinden itibaren taşıma) yeniden
üretmek için, 25 numaralı görevin as-of tablosundaki ilgili sütuna
doğrudan `.ffill()` uygulandı (bu, eski script'in TAM OLARAK yaptığı
işlemdi) ve yeni yöntemle yan yana karşılaştırıldı:

| Tarih | Yeni yöntem: noter_devir_toplam_adet | Eski yöntem (simülasyon) | Yeni yöntem: tufe_endeks | Eski yöntem (simülasyon) |
|---|---|---|---|---|
| 2020-06-01 | **1097112.0** (Haziran'ın kendi değeri) | 561375.0 (Mayıs'ın taşınan değeri) | **465.84** (Haziran'ın kendi değeri) | 454.43 (Nisan'ın taşınan değeri — TÜFE'nin yayım gecikmesi 2 ay) |
| 2020-06-15 | 1097112.0 (aynı, değişmedi) | 561375.0 (aynı, değişmedi) | 465.84 (aynı, değişmedi) | 460.62 (ay içinde bile DEĞİŞTİ — çünkü 2020-06-01 ile 2020-06-15 arasında Mayıs'ın kendi as-of'u devreye girmiş) |

**Somut kanıt:** aynı tarihte (2020-06-01) iki yöntem tamamen farklı
sayılar veriyor — yeni yöntem Haziran'ın kendi verisini gösterirken,
eski yöntem hâlâ önceki ayların taşınan (gecikmeli) değerlerini
gösteriyordu. Bu, iki yöntemin gerçekten farklı çalıştığının açık
kanıtıdır.

---

## 4. Kenar Durumu Sonuçları

| Kenar durumu | Test | Sonuç |
|---|---|---|
| İlk ay (tablo başı) | TÜFE'nin en erken referans ayı 2015-01 — tablonun kendisi de 2015-01'de başlıyor, bu yüzden "önceki ay verisi yok" durumu TÜFE için gözlenemiyor. Onun yerine `noter_devir_otomobil_adet` (2018-02'den başlıyor) test edildi. | ✅ 2018 öncesi TÜM günler NaN (0/1096 dolu) — geriye doğru sızıntı YOK, beklenen davranış. |
| Artık yıl Şubat (2016, 29 gün) | 2016-02 ayının gün sayısı ve 2016-02-29'un varlığı kontrol edildi. | ✅ 29 gün doğru sayıldı, 2016-02-29 mevcut ve noter değeri (519089.0) doğru taşınıyor. |
| Artık olmayan yıl Şubat (2018, 28 gün) | 2018-02 ayının gün sayısı kontrol edildi. | ✅ 28 gün — doğru. |
| **BETAM'ın atladığı aylar (2024-05, 2025-02) — EN RİSKLİ senaryo** | Bu iki ayda `proxy_fiyat_cari_tl` tamamen NaN mı, yoksa komşu aydan (2024-04/2024-06 veya 2025-01/2025-03) sızıntı mı var? | ✅ **NET CEVAP: SIZINTI YOK.** 2024-05 ve 2025-02 ayları TAMAMEN NaN (`nunique()` boş küme). Komşu aylar (2024-04=867813.0, 2024-06=871156.0, 2025-01=935136.0, 2025-03=950515.0) hepsi BİRBİRİNDEN FARKLI — hiçbiri atlanan aya sızmamış, hiçbiri komşusundan ödünç almamış. |
| Kaynağın hiç veri vermediği dönem | `proxy_fiyat_cari_tl` için 2024-01 öncesi tüm dönem (3287 gün) kontrol edildi. | ✅ Tamamı NaN (0/3287 dolu) — 0 veya başka bir yer tutucu değerle YANLIŞLIKLA doldurulmamış. |

Tüm kenar durumları beklenen (doğru) şekilde davranıyor.

---

## 5. Toplu Bütünlük Kontrolü Sonucu

- **Satır sayısı:** 4234 — önceki tüm tablolarla (25 ve 26 numaralı
  görevler) birebir aynı. ✅
- **Toplu ay-içi-sabitlik kontrolü:** 22 forward-fill edilen değer
  sütununun her biri, tablonun kapsadığı her takvim ayı için ayrı ayrı
  test edildi (`groupby(ay).nunique()`). Toplam **3080 ay-sütun çifti**
  kontrol edildi.
- **Bulunan istisna sayısı: 0.** Hiçbir ay-sütun çiftinde birden fazla
  farklı değer bulunmadı — her ay ya tek bir sabit değer taşıyor, ya da
  (kaynağın o ay verisi yoksa) tamamen NaN. **Hiçbir hata, sızıntı veya
  tutarsızlık tespit edilmedi.**

---

## 6. Karşılaşılan Sorunlar

Doğrulama sırasında hiçbir hata bulunmadı. Tek metodolojik not: "eski
yöntem"in davranışını yeniden üretmek için 26 numaralı görevin ilk
(değiştirilmiş/üzerine yazılmış) script'i artık diskte mevcut değildi —
bunun yerine, o script'in yaptığı işlemi (`.ffill()` üzerinden 25
numaralı as-of tablosunun ilgili sütununa uygulama) birebir simüle
edilerek Bölüm 3'teki karşılaştırma üretildi. Bu, orijinal script'in
DOKÜMANTE EDİLMİŞ mantığına dayanıyor (bkz. önceki PM raporları), bir
tahmin değil.

---

## 7. Açık Sorular / PM Onayı Gerekenler

Doğrulama sonucunda hiçbir hata/tutarsızlık bulunmadığı için, düzeltme
gerektiren bir açık soru yok. Tek bilgilendirme notu: bu doğrulama
raporu, `df_gunluk_forward_fill_2015_bugun.csv`'nin proje sahibinin
netleştirdiği "referans aya göre hizalama" kuralına **tam uyduğunu**
teyit ediyor — tablo, korelasyon analizi gibi sonraki adımlar için
güvenle kullanılabilir durumda.
