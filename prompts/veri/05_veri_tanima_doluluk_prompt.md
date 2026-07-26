GÖREV: Bu bir VERİ TANIMA adımıdır. Veri değiştirme, model kurma, tahmin YOK.
Yalnızca mevcut veri setinin doluluk ve güvenilirlik dökümünü çıkar.

1) SÜTUN DOLULUK DÖKÜMÜ
data/processed/genisletme/veri_2024_bugun_etiketli.csv dosyasında her sütun için:
- kaç ay dolu, kaç ay boş (NaN), doluluk yüzdesi
- boş olan ayların tam listesi (hangi YYYY-MM'ler)
- veri türü: GERÇEK ölçüm mü, yoksa TÜRETME/İNTERPOLASYON mu?
  (ör. alım gücü çeyreklikten aylığa interpole edildiyse "interpole" yaz;
  erişilebilirlik endeksi ona bağlıysa onu da işaretle; TÜFE baz-zincirleme
  içeriyorsa belirt)

2) %9,1 EKSİK HÜCRE ANALİZİ
Toplam eksik hücrenin hangi sütunlarda yoğunlaştığını göster. Eksikler
"yapısal" mı (ör. BETAM'ın 2 ay rapor atlaması, ilk ayın değişim
üretememesi) yoksa "gerçek veri kaybı" mı — ayır.

3) HEDEF ZİNCİRİ SAĞLIĞI
proxy fiyat → log değişim → etiket zincirinde kaç geçerli gözlem var,
hangi aylar hedef üretemiyor ve neden.

ÇIKTI: Bulguları hem tablo halinde hem de KOPYALANABİLİR DÜZ METİN (kod bloğu)
olarak ver — proje sahibi PM'e iletecek, dosya aktarımı sorunlu.

PROMPT ARŞİVİ: Bu talimatı, çalıştırmadan önce prompts/veri/ klasörüne
05_veri_tanima_doluluk_prompt.md adıyla kaydet ve commit'le. Bundan sonra
sana verilen her prompt için aynısını yap: ilgili prompts/ alt klasörüne
açıklayıcı, sıralı bir adla arşivle, sonra işe başla.

YAPMA: veri değiştirme, model kurma, hedef tanımını değiştirme.
