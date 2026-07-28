ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Mevcut durum: TÜİK TÜFE serisi zaten çekili (data/raw/tufe/).
Şimdi görev: ENAG (Enflasyon Araştırma Grubu) E-TÜFE serisini KONTROL/PARALEL
seri olarak eklemek.

NEDEN: Reel fiyat hesaplamasında tek deflatöre (TÜİK TÜFE) güvenmek risklidir.
Araştırma (bkz. docs/00_karar_kaydi.md ilgili not) TÜİK ile ENAG arasında
sistematik ve büyük bir fark olduğunu gösterdi: 2026 Ocak-Mayıs arasında
yıllık enflasyon farkı tutarlı biçimde 20-24 puan bandında (TÜİK ~%30-32,
ENAG ~%53-55). Bu proje TÜFE ana deflatör olarak kullanacak ama ENAG'ı
KONTROL SERİSİ olarak paralel tutacak (K1'in alt kararı).

BAĞLAYICI İLKELER:
- Yalnızca kamuya açık kaynak (K5). ENAG verisi kamuya açık, ücretsiz.
- As-of date disiplini korunur: ENAG'ın yayım tarihi TÜİK'ten farklı olabilir,
  bunu ayrı sütunda tut.
- Veri Git-dışı, kod+rapor commit'lenir.
- Bu görev SADECE veri çekme; reel hesaplamayı değiştirme (ayrı görev).

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/veri/12_enag_veri_cekme_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — ENAG KAYNAK TESPİTİ VE ÇEKME YÖNTEMİ
======================================================================
- ENAG'ın resmi web sitesini (enagrup.org) incele. Aylık E-TÜFE verilerini
  (aylık % değişim, yıllık % değişim, ve varsa endeks seviyesi) yayımladığı
  sayfa/format ne? PDF mi, web sayfası mı, API var mı?
- Resmi API/CSV/indirilebilir veri YOKSA: aylık basın açıklamalarından
  (ENAG'ın kendi Twitter/X hesabı @ENAGRUP, resmi web sitesi duyuruları,
  veya güvenilir haber ajansı aktarımları — AA, Reuters, T24, Euronews gibi
  saygın kaynaklar) veriyi topla. HER RAKAM İÇİN kaynağı kaydet.
- KAYNAK ÖNCELİK KURALI uygula: (A) ENAG resmi site/API → (B) ENAG resmi
  sosyal medya açıklaması → (C) güvenilir haber ajansı aktarımı (ENAG'a
  doğrudan atıfla) → (D) diğer.
- Mevcut olduğu kadar geriye git (mümkünse ENAG'ın başladığı tarihe kadar;
  değilse en azından 2024-01'den itibaren, mevcut proje kapsamıyla örtüşecek
  şekilde).

======================================================================
GÖREV 2 — ÇEKME VE DOĞRULAMA
======================================================================
- Her ay için: aylık % değişim, yıllık % değişim, mümkünse endeks seviyesi
  (varsa baz yılı not et).
- ÇAPRAZ DOĞRULAMA: En az 3-5 ayı BAĞIMSIZ olarak iki farklı kaynaktan
  (örn. ENAG'ın kendi açıklaması + bir haber ajansı aktarımı) doğrula.
  Tutmuyorsa raporla, tahmin etme.
- WebSearch/dış kaynaktan gelen hiçbir rakamı ikinci bir kaynakla
  doğrulamadan kullanma (bu projede daha önce WebSearch yıl-karışması hatası
  kanıtlanmıştı — aynı disiplin burada da geçerli).

======================================================================
GÖREV 3 — ÇIKTI
======================================================================
- data/raw/enag/enag_aylik_YYYY_YYYY.csv: referans_ayi, enag_aylik_degisim,
  enag_yillik_degisim, enag_endeks (varsa), kaynak_url, kaynak_seviyesi.
- Mevcut TÜİK TÜFE tablosuyla YAN YANA (birleştirmeden, ayrı sütunlarda)
  karşılaştırma tablosu üret: data/processed/analiz/tufe_enag_karsilastirma.csv
  (referans_ayi, tufe_aylik, tufe_yillik, enag_aylik, enag_yillik, fark_yillik).
- Bu tabloyu GÖRSELLEŞTİR: aynı grafikte iki serinin yıllık enflasyon
  çizgisini üst üste koy (data/processed/analiz/gorseller/tufe_vs_enag.png).

BİRLEŞTİRME YAPMA: TÜİK ve ENAG serilerini TEK bir "enflasyon" sütununda
karıştırma. İkisi ayrı sütun/seri olarak kalacak; hangisinin ana deflatör
olacağı ayrı bir karardır (zaten K1'de TÜFE ana olarak kararlaştırıldı).

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_enag_cekme.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN olarak göster.

Başlıklar: (1) Ne yapıldı. (2) ENAG hangi kaynaktan, hangi seviyeden (A-D)
çekildi. (3) Kapsanan dönem (kaç ay). (4) Çapraz doğrulama sonucu — hangi
aylar iki kaynaktan teyit edildi. (5) TÜİK-ENAG fark tablosu özeti (ortalama
fark, min-max fark, trend var mı). (6) Karşılaşılan sorunlar. (7) Veri örneği
(ilk/son 3 satır). (8) Açık sorular / PM onayı gerekenler.

YAPMA:
- TÜİK ve ENAG'ı tek seri haline getirme.
- Hangi serinin "doğru" olduğuna dair yorum/karar verme — bu iş bilimsel
  değil, sadece iki ölçümü yan yana koyma işi.
- Model/hedef değiştirme.
