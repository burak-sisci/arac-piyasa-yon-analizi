# Indicata aylık ikinci el online pazar serisi

`indicata_aylik.csv`, Türkiye'deki kurumsal ikinci el online binek ve hafif ticari araç pazarının aylık ilan ve satışa dönen ilan sayılarını içerir. Ana sayısal kaynak Indicata'nın resmi Türkiye raporlarıdır. Canlı PDF arşivi Temmuz 2024–Temmuz 2026 döneminde kesintisizdir; 2024'ün ilk altı raporu bugün 404 dönmesine rağmen resmi PDF metni arama indeksinde denetlenebilmiştir.

## Kolonlar

- `referans_ayi`: Verinin ait olduğu ay, `YYYY-MM`.
- `ilk_acik_yayin_tarihi`: Kullanılan resmi belgenin bilinen ilk açık yayın tarihi. Boşsa kesin gün doğrulanamamıştır.
- `ilan_yayinlanan_adet`: Ay içinde yayınlanan tekil/kurumsal ilan adedi; rapordaki terminoloji zamanla küçük biçim değişiklikleri gösterir.
- `satisa_donen_adet`: İlandan tamamen kaldırıldığı için satılmış kabul edilen kurumsal araç adedi. Noter devri değildir.
- `satis_ilan_orani_pct`: `100 * satisa_donen_adet / ilan_yayinlanan_adet`. Raporda tam yüzde verildiğinde rapor yüzdesi, aksi halde iki ondalıklı yeniden hesaplama kullanılır.
- `ortalama_satis_hizi_gun`: Pazar ortalama satış hızı. Yalnız 2024 tam raporlarında aylık yayımlanmıştır.
- `perakende_fiyat_aylik_pct`: Rapordaki aylık ortalama perakende fiyat değişimi, yüzde puan.
- `toptan_fiyat_aylik_pct`: Rapordaki aylık toptan fiyat değişimi, yüzde puan. 2025+ özetlerde yoktur.
- `method_version`: Rapor biçimi/metodoloji sürümü.
- `availability_status`: `retrospective_only` olan 2023 gözlemleri, 2024 karşılaştırma grafiklerinden çıkarılmıştır; gerçek zamanlı 2023 backtest feature'ı olarak kullanılamaz.
- `extraction_status` / `extraction_quality`: Değerin doğrudan canlı PDF, önbellekteki resmi PDF veya resmi toplamlardan türetilme durumunu belirtir.

## Metodoloji kırılmaları

- `v2024_full`: İlan, satış, oran, pazar satış hızı, perakende ve toptan fiyat bulunabilir.
- `v2025_summary`: İlan ve satış ayrı sayfalarda bulunur; oran yeniden hesaplanır. Satış hızı ve aylık toptan fiyat yayımlanmaz. Fiyat örneklemi 37 marka, 183 model, 2.098 varyant ve 0–10 yaş araçlarla tarif edilir.
- `v2026_summary_v2`: Dosya adı Şubat 2026'dan itibaren açıkça “Özet”tir. Ücretsiz sürüm ilan/satış adetlerini korur, fiyat ve satış hızı vermez.
- `v2024_comparative`: 2023 adetleri bir sonraki yılın aynı ay karşılaştırma grafiğinden gelir. Değerler tam sayıdır fakat yayın tarihi retrospektiftir.

Aralık 2023 ve Aralık 2024 aylık ilan/satışları, resmi yıl toplamından resmi ilk 11 ay toplamı çıkarılarak elde edilmiştir. Bu aritmetik kesin olsa da satır `derived_official_totals` olarak işaretlenmiştir.

## Kapsam ve target kullanımı

En güvenilir, tanımı en uzun süre korunan target adayları:

1. `log(satisa_donen_adet)` için mevsimsel yıllık değişim veya ileri 3 aylık toplam büyümesi.
2. `satis_ilan_orani_pct` için ileri 1–3 aylık değişim; online likidite/satışa dönüşüm göstergesidir.
3. İlan ve satışın birlikte kullanıldığı “absorpsiyon ivmesi”: satış büyümesi eksi ilan büyümesi.

Satış sayısı resmi noter devri değildir. Indicata'nın kaldırılan ilanı satış kabul eden proxy metodolojisidir. Model değerlendirmesinde 2023 satırları yalnız target geçmişini uzatmak için kullanılabilir; 2023'e ait gerçek zamanlı tahminde, kaynak raporlar 2024'te yayımlandığı için feature olarak kullanılmamalıdır.

Yeniden üretim ve HTTP denetimi:

```powershell
python scripts/collect_indicata.py --verify-online
```

PDF'leri yerel arşive almak istenirse ayrıca `--download-raw` verilebilir; varsayılan çalıştırma büyük ham dosya saklamaz.

