# Hacim yönü — çakışma kurtarma ve iterasyonu tamamlama

Önce `prompts/veri/31_hacim_yon_sinif_agirligi_iterasyonu_prompt.md` dosyasını
oku; tüm bağlayıcı sınırlar geçerlidir. Önceki iki CLI sürecinin çakışması
nedeniyle çalışma ağacı kısmen tutarsızdır. Başka yazıcı süreç artık yoktur.

## Denetmen kararı

- `scripts/model/yon_degerlendirme.py` içinde
  `sinif_agirliklari_hesapla` iki kez tanımlanmış. Yalnız `agirliklar=None`
  parametresini destekleyen, sınıf frekansını eğitimdeki ay-eşit ağırlık
  toplamından hesaplayabilen tek sürümü koru. Yinelenen sürümü kaldır.
- Aday seçiminde yalnız bir yardımcı yaklaşım bırak. Sıra kesin olarak
  validasyon MCC, macro-F1, stable recall olsun; tam eşitlikte deterministik
  biçimde baseline (`esit_agirlik`) tercih edilsin.
- Yinelenen/örtüşen testleri temizle ama kapsamı azaltma.
- Şu an 36 testin 2'si `agirliklar` TypeError nedeniyle başarısız; önce tüm
  testleri geçir.
- Ardından iki veri seti için deneyi bir kez çalıştır, çıktıları ve zorunlu yedi
  başlıklı yeni PM raporunu üret. Test sonuçlarını aday seçiminde kullanma ve
  daha önce görüldüğü için keşifsel diye işaretle.
- Yeni feature, threshold moving, kalibrasyon, frekans/hizalama değişimi yok.
- Kullanıcı notebooklarına ve ilgisiz izlenmeyen dosyalara dokunma.
- Commit/push yapma. Sonunda değişen dosyalar, testler, aday bazlı validasyon
  metrikleri, seçilen adaylar, test metrikleri ve riskleri bildir.

Token tasarruflu çalış; yalnız ilgili diff ve dosyaları oku. Sonnet high-effort.
