# Hacim yönü — sınıf ağırlığı iterasyonu

## Rol ve sınırlar

Claude Code uygulayıcı ve rapor yazarıdır. Codex denetmen ve nihai karar
yetkilisidir. `main` dalına geçme, push yapma veya kullanıcıya ait ilgisiz
değişikliklere dokunma.

## Sabit problem tanımı

- Hedef: `noter_devir_otomobil_adet` için bir sonraki takvim ayının yönü.
- Sınıflar: `down`, `stable`, `up`; ana eşik ±%5 ve tam sınırlar `stable`.
- Veri günlük frekansta kalacak; kaynak hizalaması ve doldurma yöntemi
  değiştirilmeyecek.
- DF-A ve DF-B birlikte korunacak.
- Ana metrikler global/Gorodkin MCC ve macro-F1; accuracy ikincil.
- Test ayları model/hiperparametre seçimi için kullanılmayacak.

## Görev

Mevcut `scripts/model/model_06_hacim_yon_siniflandirma.py` baseline'ını dar
kapsamda geliştir. İlk ve tek müdahale, mevcut ay-eşit örnek ağırlıklarıyla
sınıf ağırlıklarını çarpan maliyet-duyarlı eğitim varyantı olsun. Ağırlıkları
yalnızca eğitim bölümündeki sınıf frekanslarından hesapla. Veri sızıntısı,
frekans değişimi, threshold moving, kalibrasyon ve yeni feature ekleme yok.

1. Önce mevcut kodu, raporu ve testleri incele.
2. Baseline ile sınıf-ağırlıklı aday arasında seçim yalnız validasyon MCC,
   ardından macro-F1 ve stable recall sırasıyla yapılsın. Test metriklerini
   seçim mantığına sokma.
3. Seçilen aday için test değerlendirmesini bir kez üret; test daha önce
   görülmüş olduğundan sonucu doğrulayıcı değil keşifsel diye açıkça işaretle.
4. Her iki veri setinde sınıf bazlı precision/recall/support, sabit sıralı
   confusion matrix ve ham olasılıkları koru.
5. Küçük, birim-test edilebilir yardımcı fonksiyonlar ekle; ilgili testleri
   çalıştır. Mevcut kullanıcı dosyalarına dokunma.
6. Yeni bir PM raporu oluştur: zorunlu 7 başlığın tümünü içersin, başarısız
   sonuçları saklamasın ve sonraki adımı yalnız önersin.
7. Değişiklikleri commit etme veya push etme. Sonunda değişen dosyaları,
   komutları, metrikleri ve açık riskleri kısa biçimde bildir.

Token tasarrufu için yalnız ilgili dosyaları oku; Sonnet high-effort kullan.
