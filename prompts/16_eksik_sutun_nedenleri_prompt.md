ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Görev: projedeki TÜM işlenmiş veri dosyalarında hangi
sütunların eksik/boş değer taşıdığını ve BUNUN NEDENİNİ tek bir raporda
toplamak.

Bu bir ANALİZ veya KARAR görevi DEĞİLDİR — sadece mevcut durumu doğru ve
kısa biçimde AÇIKLAMAK. Daha önce doluluk yüzdelerini (05 numaralı analiz)
ve genel envanteri (13 numaralı analiz) çıkarmıştık; bu görev onlardan
FARKLI — bu sefer odak yalnızca EKSİK OLAN sütunlarda ve "NEDEN eksik"
sorusunda, dolu sütunları tekrar anlatmaya gerek yok.

BAĞLAYICI İLKELER:
- Yeni veri çekme, model kurma, hedef değiştirme YOK.
- Uydurma yok: bir sütunun neden eksik olduğunu bilmiyorsan "neden net
  değil, araştırılmalı" yaz, tahmin etme.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/16_eksik_sutun_nedenleri_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — TARANACAK DOSYALAR
======================================================================
data/processed/ altındaki TÜM işlenmiş veri dosyalarını tara (en azından):
- data/processed/genisletme/veri_2018_bugun_etiketli.csv
- data/processed/analiz/tufe_enag_karsilastirma.csv
- data/processed/analiz/piyasa_aktivite_endeksi.csv (bu sefer DAHİL ET —
  önceki envanterde hariç tutulmuştu ama bu görev farklı, eksik-sütun
  taraması için her dosya dahil olmalı)
- Varsa başka işlenmiş dosya (data/processed/ klasörünü tam tara).
- Ayrıca data/raw/ altındaki ham dosyalarda da göze çarpan sistematik
  boşluklar varsa (örn. bir kaynağın belirli aylarda hiç veri vermemesi)
  bunları da kısaca ekle.

======================================================================
GÖREV 2 — HER EKSİK/BOŞ SÜTUN İÇİN
======================================================================
Doluluğu %100 OLMAYAN her sütun için:
1. Sütun adı ve hangi dosyada olduğu
2. Kaç gözlem eksik / toplam kaç gözlem (ör. "5/102 ay eksik")
3. NEDEN eksik — kısa, net bir açıklama. Kategorilere ayır:
   a. KAYNAK BOŞLUĞU: kaynağın kendisi o dönemde veri yayımlamamış
      (örn. "BETAM Mayıs 2024'te rapor yayımlamadı")
   b. HESAPLAMA GEREĞİ: bir türetilmiş değerin hesaplanabilmesi için
      önceki veriye ihtiyaç var, seri başında bu yok (örn. "yıllık değişim
      için 12 ay geriye taban gerekiyor, ilk 11 ay hesaplanamıyor")
   c. ZİNCİRLEME ETKİSİ: başka bir sütunun eksik olması bunu da eksik
      bırakıyor (örn. "önceki ay NaN olduğu için bu ayın değişimi de
      hesaplanamıyor")
   d. TASARIM GEREĞİ: sütun yapısı gereği yalnızca belirli durumlarda dolu
      olması bekleniyor (örn. "otv_aciklama yalnızca ÖTV olayı olan ayda
      doludur, bu normaldir")
   e. HENÜZ YAYIMLANMADI: veri kaynağı ilgili dönem için henüz veri
      açıklamamış (örn. "2026-Q2 TÜİK bülteni henüz çıkmadı")
   f. NEDEN NET DEĞİL: araştırılması gerekiyor, şu an bilinmiyor.
4. Bu eksikliğin ZİNCİRLEME ETKİSİ var mı — yani bu sütunun eksik olması
   başka hangi sütunları/hesaplamaları etkiliyor? (Örn. proxy fiyatın 2 ay
   eksik olması, ondan türeyen 5-6 farklı sütunu da etkiliyor — bunu
   belirt.)

======================================================================
GÖREV 3 — ÇIKTI FORMATI
======================================================================
1. KISA GİRİŞ (2-3 cümle): kaç dosyada toplam kaç eksik-içeren sütun
   bulundu, en sık görülen eksiklik nedeni hangisi.
2. DOSYA BAZINDA GRUPLANMIŞ LİSTE — her dosya bir başlık, altında o
   dosyadaki eksik sütunlar Görev 2'deki bilgilerle birer madde.
3. ÖZET TABLO: sütun | dosya | eksik sayısı/toplam | neden kategorisi (a-f)
   | zincirleme etki var mı (evet/hayır, varsa hangi sütunlara).
4. KATEGORİ DAĞILIMI (kısa): kaç sütun (a) kaynak boşluğu, kaç (b)
   hesaplama gereği, kaç (c) zincirleme, kaç (d) tasarım gereği, kaç (e)
   henüz yayımlanmadı, kaç (f) nedeni net değil.

======================================================================
GÖREV 4 — KAYDETME
======================================================================
- Dosya: docs/eksik_sutun_nedenleri.md
- Repoya commit'le.
- Oturumda tamamını KOPYALANABİLİR DÜZ METİN (markdown kod bloğu) olarak
  da göster.

YAPMA:
- Eksikleri doldurma önerisi/çözümü sunma (bu görev sadece NEDEN sorusuna
  cevap veriyor, "ne yapmalı" ayrı bir konu).
- Hedef/model hakkında yorum yapma.
- Neden bilinmeyen bir eksikliği tahminle açıklama — "neden net değil" yaz.

BİTİRİNCE: Kısa not — kaç sütun tarandı, kaçı eksiksiz kaçı eksik, en çok
zincirleme etkisi olan sütun hangisi, "neden net değil" kategorisine kaç
sütun düştü.
