İki bağlantılı konuda net, uygulamalı bir araştırma istiyorum. Amacım akademik
değil: bir veri işleme adımını doğru kurmak.

BAĞLAM: Türkiye ikinci el otomobil piyasasında aylık bir nominal (cari) fiyat
serim var (TL cinsinden ortalama ilan fiyatı). Bunu "reel" (enflasyondan
arındırılmış) fiyat serisine çevirmek istiyorum. Amaç, piyasanın gerçekte
değer kazanıp kazanmadığını (sadece TL'nin değer kaybından dolayı değil)
görmek.

======================================================================
KONU 1 — REEL FİYAT ENDEKSİ HESAPLAMA YÖNTEMİ (somut adımlar)
======================================================================

Şunları net biçimde açıkla:

1. TEMEL FORMÜL: Nominal fiyattan reel fiyata geçişin standart formülü nedir?
   (Örn. reel_fiyat_t = nominal_fiyat_t / (deflatör_t / deflatör_baz) gibi bir
   şey mi? Baz dönem nasıl seçilir?)

2. HANGİ ENDEKS TÜRÜ KULLANILMALI: Merkez bankaları ve istatistik kurumları
   (TCMB, TÜİK, BIS, OECD, Eurostat) dayanıklı tüketim malı (özellikle araç)
   fiyatlarını reelleştirirken TÜFE'nin TAMAMINI mı kullanıyor, yoksa
   alt-kalem (araç/ulaştırma) endeksini mi, yoksa çekirdek enflasyonu mu
   tercih ediyor? Hangisi metodolojik olarak "doğru" kabul ediliyor ve neden?

3. KALİTE/HEDONİK DÜZELTME: CBRT'nin konut fiyat endeksinde yaptığı gibi
   (bkz. Hülagü ve diğerleri 2015), "nominal değişimin ne kadarı gerçek
   fiyat artışı, ne kadarı kalite/kompozisyon değişikliği" ayrımı araç
   fiyat endeksleri için nasıl yapılıyor? Somut bir hesaplama yöntemi
   (hedonik regresyon, matched-model, tekrarlı satış yöntemi) var mı?

4. AYLIK vs YILLIK BAZLAMA: Reel endeksi aylık zincirlemek (her ay bir
   önceki aya göre) ile sabit bir baz yıla göre hesaplamak arasında ne
   fark var, hangisi yön tahmini (üç ay sonra artacak mı azalacak mı) için
   daha uygun?

5. ÖRNEK HESAPLAMA: Somut bir sayısal örnek ver — örneğin "Ocak nominal
   fiyat X TL, TÜFE Y, Şubat nominal fiyat X2 TL, TÜFE Y2 ise reel değişim
   şöyle hesaplanır" gibi adım adım bir örnek.

======================================================================
KONU 2 — DEFLATÖR GÜVENİLİRLİĞİ VE ALTERNATİF ÖLÇÜMLER
======================================================================

Türkiye'de resmi TÜİK enflasyon rakamlarının bağımsız gruplar (ör. ENAG)
tarafından hesaplanan rakamlardan farklı olduğu biliniyor ve bu bir
tartışma konusu. Bu nedenle:

6. ALTERNATİF ENFLASYON ÖLÇÜMLERİ: ENAG dışında, Türkiye için TÜFE'ye
   alternatif veya onu doğrulayan/çelişen başka bağımsız enflasyon ölçüm
   girişimleri var mı (akademik, sivil toplum, uluslararası kurum)? Bunların
   metodolojisi nedir, aylık/kamuya açık veri sunuyorlar mı, hangi tarihten
   beri yayımlıyorlar?

7. ALTIN BAZLI DEFLATÖR: Fiyatı TL yerine ALTIN cinsinden ifade etmenin
   (yani "bu araç kaç gram altın eder" serisi kurmanın) enflasyondan
   arındırma için bir alternatif olup olmadığını araştır. Bunun akademik
   veya pratik literatürde (yüksek enflasyonlu ülkeler için) bir emsali
   var mı? Artıları (manipülasyona kapalı, uluslararası karşılaştırılabilir)
   ve eksileri (altının kendi fiyat dalgalanması, arz-talep dinamiği farklı)
   neler?

8. DÖVİZ BAZLI DEFLATÖR: Aynı soruyu USD veya "büyük mac" tarzı satın alma
   gücü paritesi endeksleri için sor. Türkiye'de yüksek enflasyon dönemlerinde
   akademisyenlerin/analistlerin fiyatları dolar bazında ifade etmesi
   (dolarizasyon) yaygın mı, bunun metodolojik tuzakları neler (kur kendisi
   de manipülasyona/politika müdahalesine açık olabilir)?

9. KIYASLAMA: TÜFE-deflatör, altın-deflatör ve döviz-deflatörün HANGİ
   KOŞULLARDA birbirinden farklı sonuç verdiğini gösteren bir çalışma
   var mı? (Örneğin resmi enflasyon düşük gösterilirken altın/döviz bazlı
   reel fiyatın daha farklı bir tablo çizdiği bir örnek/vaka çalışması.)

10. PRATİK ÖNERİ: Yüksek enflasyonlu/düşük-güven ortamlarında (Türkiye,
    Arjantin, Venezuela gibi) akademik veya kurumsal kaynakların BİRDEN
    FAZLA deflatörü PARALEL kullanmayı (ör. hem TÜFE hem altın hem döviz
    bazlı reel seri üretip karşılaştırmayı) önerip önermediğini araştır.

ÇIKTI FORMATI:
Türkçe, net, adım-adım. Her iddiayı kaynağa bağla (akademik makale, merkez
bankası dökümanı, resmi kurum metodolojisi). Emin olmadığın yerde
"literatürde net değil" yaz. Konu 1 için mutlaka somut bir sayısal örnek
hesaplama ver. Konu 2 için bulduğun her alternatif kaynağın güvenilirlik
düzeyini (akademik/kurumsal/sivil toplum/bağımsız araştırmacı) belirt.

Yanıtını KOPYALANABİLİR DÜZ METİN (kod bloğu içinde) olarak ver.