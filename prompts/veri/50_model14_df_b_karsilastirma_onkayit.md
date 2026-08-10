# Model 14 — DF-B Karşılaştırma Ön Kaydı

**Tarih:** 2026-08-10
**Kullanıcı talebi:** “DF-B’yi base modelimiz olan Model 14’e sok ve sonuçları
benimle paylaş: yön doğruluğu matrisi, macro-F1, MCC.”

## Sabitlenen deney sözleşmesi

1. Dondurulmuş Model 14 değiştirilmez; ayrı bir DF-B karşılaştırma kolu
   çalıştırılır.
2. Aday yalnız dondurulmuş `lojistik_l2_c01` modelidir: L2 cezası, `C=0,1`,
   `class_weight=balanced`, `random_state=42`.
3. Model 14’ün 14 feature’ı aynen korunur. DF-B snapshot’ında bulunmayan
   `tuketici_guven_endeksi_lag2ay` ve `odmd_otomobil_adet_lag2ay`, aynı tarih ve
   hafta anahtarındaki DF-A snapshot’ından alınır. Bu iki seri DF-B’ye özgü
   değildir; birleştirme `one_to_one` doğrulanır.
4. Temmuz 2025–Haziran 2026 kilitli testi açılmaz. Son değerlendirme ayı
   2025-06’dır.
5. DF-B’nin ilk etiketli ayı 2024-02’dir. En az 12 eğitim ayı ve 2 ay embargo
   korunur. Bu nedenle değerlendirilebilen originler 2025-04, 2025-05 ve
   2025-06 ile sınırlıdır.
6. Her origin’de median imputer ve standard scaler yalnız eğitim kümesinde fit
   edilir. Ay içindeki haftaların toplam eğitim ağırlığı 1’dir.
7. Birincil raporlama, Model 14 ile aynı şekilde dört haftanın havuzlandığı 12
   tahmin üzerinden yapılır: çok-sınıflı MCC, macro-F1, accuracy ve 3×3
   confusion matrix. Bağımsız gözlem sayısı 3 aydır; 12 haftalık satır etkin
   örneklem sayısını artırmaz.
8. Sonuç hiçbir koşulda model terfisi, DF-A/DF-B seçimi veya kilitli test kararı
   olarak kullanılmaz; yalnız kullanıcı tarafından istenen keşifsel
   karşılaştırmadır.
