ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Mevcut ENAG (E-TÜFE) serisi 2024-01→2026-06 arasını kapsıyor
(bkz. pm_rapor_enag_cekme.md). Görev: bu seriyi 2018-01'e kadar geriye
genişletmeyi DENEMEK.

DÜRÜST BEKLENTİ YÖNETİMİ: Bu genişletmenin 2024-2026 kadar kolay olmayacağı
biliniyor. Üç bilinen risk var:
1. Haber arşivlerinde ENAG'a atıf, eski yıllarda (2018-2021) çok daha
   seyrek olabilir — ENAG 2024'te daha yüksek medya görünürlüğüne sahipti.
2. ENAG'ın metodolojisi zaman içinde değişmiş olabilir; bu ihtimali
   araştır ve varsa raporla (aynı "ENAG" etiketi altında farklı
   metodolojiyle üretilmiş rakamları aynı seri gibi sunmak yanıltıcı olur).
3. Çift-kaynak doğrulama (aşağıda Görev 2) eski aylar için mümkün olmayabilir.

BU GÖREV BAŞARISIZ OLURSA SORUN DEĞİL — kısmi kapsama (örn. sadece
2021-2026) veya "2018'e gidilemedi" sonucu da değerli ve kabul edilebilir
bir çıktıdır. ZORLA DOLDURMA, TEK-KAYNAKLI TAHMİNLE BOŞLUK KAPATMA YOK.

BAĞLAYICI İLKELER (12 numaralı ENAG promptundakiyle aynı):
- Yalnızca kamuya açık kaynaklar (K5).
- Kaynak öncelik kuralı: (A) ENAG resmi site/API → (B) ENAG resmi sosyal
  medya açıklaması → (C) güvenilir haber ajansı aktarımı (ENAG'a doğrudan
  atıfla) → (D) diğer.
- HER AY, MÜMKÜNSE EN AZ 2 BAĞIMSIZ KAYNAKTAN ÇAPRAZ DOĞRULANIR. Tek
  kaynaklı aylar "D-seviyesi/doğrulanmamış" olarak ayrıca işaretlenir,
  ana seriye aynı güvenle karıştırılmaz.
- WebSearch/dış kaynaktan gelen rakamlar ikinci kaynakla doğrulanmadan
  kullanılmaz (bu projede daha önce yıl-karışması hatası kanıtlanmıştı).
- Bu proje TÜİK TÜFE'yi ana deflatör olarak kullanıyor; ENAG KONTROL
  SERİSİDİR, birleştirilmeyecek, ayrı sütun olarak kalacak.
- Veri Git-dışı, kod+rapor commit'lenir.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/veri/20_enag_2018_genisletme_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — ENAG METODOLOJİ SÜREKLİLİĞİ KONTROLÜ (önce bu, kısa)
======================================================================
2018'den bugüne ENAG'ın (a) hep aynı isimle/kurumla yayın yapıp yapmadığını,
(b) hesaplama yönteminde bilinen büyük bir değişiklik olup olmadığını kısaca
araştır. Bulgunu raporla — bu, geriye giden serinin ne kadar "aynı şeyi
ölçtüğü" sorusuna cevap verecek.

======================================================================
GÖREV 2 — GERİYE DOĞRU AYLIK VERİ ARAYIŞI (2018-01 → 2023-12)
======================================================================
Zaman kutusu: makul tut, her ay için sonsuz arama yapma. Yıl yıl ilerle
(önce 2023, sonra 2022, ... 2018'e doğru) — böylece nereye kadar makul
kapsama elde edildiği kademeli olarak görülür.

Her ay için:
- Kaynak öncelik kuralına göre ara (haber ajansı aktarımları: AA, Bloomberg
  HT, Reuters Türkiye, T24, Sputnik, İzGazete, Euronews Türkçe gibi
  kaynaklarda "ENAG enflasyon [ay] [yıl]" taraması).
- Bulunan her rakam için: aylık % değişim, yıllık % değişim (varsa),
  kaynak URL, kaynak türü (A-D).
- MÜMKÜNSE ikinci bağımsız kaynakla çapraz doğrula. Doğrulanamıyorsa
  "D-seviyesi/tek-kaynaklı" olarak işaretle, silme ama ayrı tut.

======================================================================
GÖREV 3 — KAPSAMA RAPORU (yıl bazında, net)
======================================================================
Her yıl için: kaç ay bulunabildi / 12, kaç tanesi çift-doğrulanmış (A/B/C
karışımı) kaç tanesi tek-kaynaklı (D). Bu, ekip liderine sunulacak en
önemli sayı — net ve dürüst olsun.

======================================================================
GÖREV 4 — ÇIKTI
======================================================================
- data/raw/enag/enag_2018_2023_genisletme.csv: referans_ayi,
  enag_aylik_degisim, enag_yillik_degisim, kaynak_url, kaynak_seviyesi
  (A-D), cift_dogrulama (evet/hayır).
- Mevcut ana ENAG dosyasıyla (2024-2026) BİRLEŞTİRME YAPMA — ayrı dosya
  olarak bırak; birleştirme kararı ayrı bir onay gerektirir (kalite
  seviyeleri farklı olabileceğinden karıştırılmamalı).

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_enag_2018_genisletme.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN (markdown kod bloğu) olarak göster.

Başlıklar: (1) Ne yapıldı. (2) Metodoloji süreklilik bulgusu (Görev 1).
(3) YIL BAZINDA KAPSAMA TABLOSU (Görev 3 — en kritik bölüm, net sayılarla).
(4) Kaynak kalitesi dağılımı (kaç A/B/C/D). (5) Karşılaşılan sorunlar —
özellikle hangi yıllarda arama tamamen boşa çıktı. (6) Veri örneği.
(7) NET ÖNERİ: bu genişletme kullanılabilir mi (tamamı/kısmi/hiç), ana
seriyle birleştirilmeli mi yoksa ayrı mı kalmalı — kanıt sun, kararı
PM/proje sahibine bırak.

YAPMA:
- Zorla/tek-kaynaklı tahminle boşluk kapatma.
- Ana ENAG dosyasıyla otomatik birleştirme.
- TÜİK TÜFE ile ENAG'ı tek seri haline getirme.
- Model/hedef değiştirme.
