# Target bazlı birleşik veri setleri

Bu klasör targetları feature'lardan ayırır. Ham tablolarda eksik değerler bilinçli
olarak korunmuştur; imputasyon, korelasyon filtresi ve feature seçimi modelin
eğitim fold'u içinde yapılmalıdır.

## Ortak feature tabloları

- `feature_master_aylik.csv`: 2015-01–2026-07, target içermeyen aylık feature'lar.
- `feature_master_gunluk_piyasa.csv`: 2015-01-01–2026-08-04, günlük USD/EUR,
  günlük TCMB ağırlıklı ortalama fonlama maliyeti, haftalık konut kredisi faizi
  ve takvim feature'ları. Ham gözlem tarihleri korunur; ara günler doldurulmaz.
- `feature_kapsama_ozeti.csv` ve `gunluk_feature_kapsama_ozeti.csv`: sütun bazında
  geçerli/eksik gözlem sayıları.

Aylık veriler günlük master'a henüz eklenmedi. Bunun için her değerin gerçek
yayın tarihine göre `available_at <= forecast_cutoff` as-of birleştirmesi gerekir.
Referans ayını bütün günlere yaymak zaman sızıntısı yaratabilir.

Önemli veri düzeltmesi: proje kaynaklarında `TP.KTF12` yanlışlıkla taşıt kredisi
faizi, `TP.APIFON4` ise yanlışlıkla politika faizi diye adlandırılmıştı. Yeni
çıktılarda bunlar kaynak kodlarına uygun olarak `konut_kredisi_faiz_ktf12` ve
`tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4` adlarını taşır. Doğru taşıt
kredisi serisi `TP.KTF11` mevcut ham dosyalarda bulunmadığından uydurulmamıştır.

## Ayrı targetlar ve birleşik ham tablolar

- `target_1ay_hiz.csv` ve `target_1ay_hiz_tum_featurelar.csv`
- `target_3ay_hiz.csv` ve `target_3ay_hiz_tum_featurelar.csv`
- `target_devir_orani.csv` ve `target_devir_orani_tum_featurelar.csv`

Her `target_*.csv` yalnız tarih ve tek target içerir. Her
`target_*_tum_featurelar.csv` ise yalnız ilgili target ile bütün aylık feature'ları
birleştirir. Bu geniş dosyalar inceleme içindir ve aynı-ay sütunları nedeniyle
doğrudan model-ready değildir; yasaklı alanlar `modelleme_sizinti_kisitlari.csv`
dosyasında yazılıdır.

## Yeni günlük targetlar

- `target_7g_absorpsiyon_sablon.csv`
- `target_7g_kalite_duzeltilmis_fiyat_getirisi_sablon.csv`

Bu iki dosya yalnız şemadır. Günlük doğrulanmış satış/aktif ilan kohortu ve
sabit-bileşimli günlük fiyat endeksi henüz klasörde bulunmadığı için target
değeri uydurulmamıştır.

## Yeniden üretim ve kontrol

```powershell
.\.venv-ag\Scripts\python.exe scripts\build_separated_target_datasets.py
```

`kalite_kontrol_raporu.json` tarih, satır, target ve duplicate denetimlerinin
özetidir. Kaynak betik mevcut ham veri dosyalarını değiştirmez.
