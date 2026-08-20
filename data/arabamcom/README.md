# arabam.com aylık fiyat serisi

Bu klasör, arabam.com Aylık Fiyat Endeksi'nin açık resmi yazılarda sayısal olarak belirtilen aylık ortalama ilan fiyatlarını ayrı bir kaynak serisi olarak tutar. BETAM fiyatlarıyla aynı kolonda birleştirilmemelidir.

- `ortalama_ilan_fiyati_tl`: İlan fiyatı ortalaması; gerçekleşen satış fiyatı değildir.
- `reel_aylik_degisim_pct`: Resmi yazıda açıkça belirtilmişse aylık reel değişim. Boş değer tahmin edilmemiştir.
- 2024-06 ve 2024-07 için kesin nominal ortalama açık metinde bulunmadığı için boş bırakılmıştır.
- 2025-01’den 2025-02’ye yaklaşık `%12,5` nominal sıçrama vardır. Şubat yazısındaki “ciddi değişim yok” ifadesiyle çeliştiği için muhtemel kapsam/metodoloji kırılması olarak ele alınmalıdır.

## Mevcut proxy dosyasındaki iki tarih hatası

- `913.190 TL`, Mayıs 2024 değil **Mayıs 2026** değeridir. Mayıs 2024 doğru değer `684.042 TL`dir.
- `888.689 TL`, Şubat 2025 değil **Şubat 2026** değeridir. Şubat 2025 doğru değer `783.068 TL`dir.

Mevcut `data/proxy_fiyat` dosyaları değiştirilmemiştir. Yeni seri bu hataları ayrı ve denetlenebilir biçimde düzeltir.

