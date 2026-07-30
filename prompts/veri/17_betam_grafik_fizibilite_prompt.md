ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. BETAM'ın Aralık 2023 raporu (sahibindex Otomobil Piyasası
Görünümü), 2020 Ocak'tan itibaren aylık ortalama cari fiyat ve reel fiyat
endeksini gösteren bir TARİHSEL GRAFİK içeriyor — ama bu grafik bir görüntü,
sayısal tablo değil. 2021-2023 dönemi (tek-rejim sorunumuzu çözebilecek
farklı bir ekonomik rejimi kapsayan dönem) için proxy fiyat kaynağı arayışı
bu grafiğe kadar geldi.

BU GÖREV: Grafiği sayısal veriye çevirmenin (dijitalizasyon) İŞE YARAR
OLUP OLMADIĞINI ucuza test etmek. Dijitalizasyonun KENDİSİNİ YAPMA — sadece
mümkün olup olmadığını, ne kadar güvenilir olabileceğini değerlendir.

KAYNAK: BETAM Aralık 2023 raporu PDF'i —
https://image5.sahibinden.com/staticContent/1b9c4d5b/7758/44a8/b2a6/3f9dc2997532/1702637758.pdf
(daha önceki bir araştırmada bulunmuştu; erişilemezse
https://betam.bahcesehir.edu.tr/2023/12/sahibindex-otomobil-piyasasi-gorunumu/
sayfasından tekrar bul.)

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/veri/17_betam_grafik_fizibilite_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — GRAFİĞİ BUL VE GÖRSEL OLARAK İNCELE
======================================================================
- PDF'i indir, sayfa sayfa aç (görüntü olarak).
- Tarihsel grafiği (2020-01'den itibaren ortalama cari fiyat + reel fiyat
  endeksi) içeren sayfayı/sayfaları bul.
- Grafiği YÜKSEK ÇÖZÜNÜRLÜKLÜ olarak ayrı bir görüntü dosyasına çıkar
  (mümkünse PDF'in kendi çözünürlüğünü koru, aşırı sıkıştırma yapma).

======================================================================
GÖREV 2 — GÖRSEL KALİTE DEĞERLENDİRMESİ (fizibilitenin kalbi)
======================================================================
Grafiği DOĞRUDAN İNCELEYEREK (görüntüyü gerçekten "gör") şu soruları
dürüstçe cevapla:

1. EKSEN NETLİĞİ: X ekseni (zaman) ve Y ekseni (fiyat/endeks değeri) net
   işaretli mi? Kaç aralıkla etiketlenmiş (her ay mı, her 3 ay mı, her yıl
   mı)? Y ekseninin sayısal değerleri (100, 200, 300 gibi) okunabiliyor mu?

2. ÇİZGİ NETLİĞİ: Grafik çizgisi (veya çizgileri — cari fiyat ve reel
   endeks muhtemelen iki ayrı çizgi) net ve takip edilebilir mi, yoksa
   kalın/bulanık/kesişen mi? Birden fazla çizgi varsa birbirinden ayırt
   edilebiliyor mu (renk/stil farkı var mı)?

3. VERİ NOKTASI YOĞUNLUĞU: Grafik kaç aylık bir dönemi kapsıyor (2020-01'den
   2023-11'e kadar olması bekleniyor, yaklaşık 47 ay)? Bu kadar ayı, çizgi
   üzerinde AY AY ayırt etmek görsel olarak mümkün mü, yoksa çizgi çok sık
   dalgalanıp ay-ay okumayı imkânsız mı kılıyor?

4. ÇÖZÜNÜRLÜK YETERLİLİĞİ: PDF/görüntü çözünürlüğü, grafiği büyütüp
   (zoom) tek tek ayları ayırt edecek kadar yüksek mi, yoksa büyütünce
   pikselleşip bulanıklaşıyor mu?

5. SAYISAL METİN ÇAPASI: Grafiğin yakınında veya raporun metninde, grafikte
   görünen bazı NOKTALARA karşılık gelen KESİN sayısal değerler var mı
   (örn. "Kasım 2023 = 879.146 TL" gibi)? Bu tür "çapa noktaları" ne kadar
   çok bulunursa, dijitalizasyonun doğruluğu o kadar çapraz kontrol
   edilebilir.

======================================================================
GÖREV 3 — DENEME OKUMA (küçük ölçekli, TAM dijitalizasyon DEĞİL)
======================================================================
Tüm grafiği okumaya çalışma. Sadece ŞUNU yap: grafikte görsel olarak en
NET görünen 3-4 noktayı (örneğin bariz bir tepe, bariz bir dip, ve
metinde zaten bilinen bir çapa noktasına en yakın nokta) seç ve görsel
olarak "bu nokta yaklaşık şu değere karşılık geliyor" diye TAHMİN ET.
Bu tahminleri metinde geçen KESİN rakamlarla (varsa) karşılaştır.

Amaç: "elle/görsel okuma, bilinen gerçek değere ne kadar yakın çıkıyor"
sorusuna ilk bir fikir edinmek — tam doğrulama değil, bir ön-sinyal.

======================================================================
GÖREV 4 — FİZİBİLİTE KARARI (kanıt sun, karar verme)
======================================================================
Yukarıdaki bulgulara dayanarak NET bir değerlendirme yap (ama nihai "yapalım
mı yapmayalım mı" kararını PM/proje sahibine bırak):
- Grafik dijitalizasyona UYGUN mu (net eksen, net çizgi, yeterli çözünürlük)?
- Hangi TÜR belirsizlik bekleniyor (ör. "aylık ayrım zor, ama 3 aylık
  dönemler ayırt edilebilir" gibi kademeli bir değerlendirme de olabilir)?
- Tahmini hata payı ne olabilir (kaba bir aralık ver, örn. "%2-3 civarı"
  veya "bu grafikte ay-ay kesinlik mümkün değil, sadece yön/trend
  çıkarılabilir" gibi).
- SONUÇ: (a) tam dijitalizasyona değer / (b) sadece kaba trend (yön) çıkarımı
  için değer, kesin sayı için değil / (c) grafik kalitesi yetersiz, bu yoldan
  vazgeçilmeli.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_betam_grafik_fizibilite.md üret VE
oturumda KOPYALANABİLİR DÜZ METİN olarak göster. AYRICA incelenen grafiğin
kendisini (görüntü dosyasını) data/processed/analiz/gorseller/ altına koy
ki proje sahibi de kendi gözüyle görebilsin.

Başlıklar: (1) Ne yapıldı. (2) Görsel kalite değerlendirmesi (Görev 2'nin
5 sorusuna cevaplar). (3) Deneme okuma sonucu (Görev 3 — tahmin vs bilinen
gerçek değer karşılaştırması). (4) FİZİBİLİTE KARARI (Görev 4 — net (a)/(b)/(c)
sonucu ve gerekçesi). (5) Karşılaşılan sorunlar. (6) Açık sorular / PM onayı
gerekenler — özellikle "Aşama 2'ye (çoklu-yöntem dijitalizasyon) geçilsin mi"
sorusu net şekilde sorulsun.

YAPMA:
- Tüm grafiği tam dijitalize etme (bu Aşama 2'nin işi, bu görev sadece
  fizibilite).
- "Yapalım mı yapmayalım mı" kararını kendin verme — kanıt sun, karar
  PM/proje sahibine kalsın.
- Model/hedef değiştirme.
