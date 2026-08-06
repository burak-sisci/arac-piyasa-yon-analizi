# Nowcast baseline ve as-of özellik geçidi

## Talep

Kullanıcı, target `noter_devir_otomobil_adet` ve `up/stable/down` amacı
dışında projeyi profesyonelleştirmek ve model performansını artırmak üzere
Rota'nın otonom ilerlemesini istedi. Tahmin ürünü haftalık güncellenen cari
ay-sonu yön nowcast'idir. Uzak repoya push yapılmayacaktır.

## Bu aşamanın sınırı

1. Kilitlenmemiş validation döneminde train çoğunluğu, bilgi-anı persistence
   (`M-2`) ve seasonal `t-12` baseline'larını ölç.
2. Mevcut repodaki kaynakları as-of açısından denetle; kanıtı olmayan sütunu
   feature setine alma.
3. Haftalık bilgi kazanımı için hafta sırası kapsamını çıkar; baseline ay
   içinde değişmediği için sahte monotonluk iddiası üretme.
4. Test dönemini açma veya kilitleme; model araması yapma.
5. DF-B'yi N<50 nedeniyle yalnız keşifsel tut.

## Pusula'nın sert koşulları

- Baseline ilk sırada çalışır.
- As-of kanıtı olmayan feature reddedilir.
- Validation'da toplam aday sayısı 10'u aşamaz.
- Negatif sonuç gizlenmez ve geniş aramayla kurtarılmaya çalışılmaz.
- Test setinin açılması ile yeni bağlayıcı K maddesi bu aşamada reddedilmiştir.
