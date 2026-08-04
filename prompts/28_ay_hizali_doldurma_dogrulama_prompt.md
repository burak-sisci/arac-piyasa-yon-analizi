ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Proje sahibi, önceki forward-fill yaklaşımını (26 numaralı
görev — açıklanma/as-of gününden itibaren taşıma) DEĞİL, farklı bir yöntem
istedi ve şu anda onu uyguluyorsun:

DOĞRU YÖNTEM (netleştirilmiş): Her ayın kendi değeri, o REFERANS AYIN
KENDİ TAKVİM GÜNLERİNE yazılır — Ocak'ın değeri Ocak'ın 1-31'ine, Şubat'ın
değeri Şubat'ın 1-28/29'una, vb. AÇIKLANMA/YAYIM TARİHİNİN bu dağıtımla
HİÇBİR İLGİSİ YOKTUR. Yani bir kaynağın Ocak verisi gerçekte Şubat başında
açıklanmış olsa bile, o değer yine de OCAK ayının takvim günlerine
(01-01'den 01-31'e) yazılır — açıklanma gecikmesi bu dağıtımda dikkate
ALINMAZ.

BU GÖREVİN İŞİ: Bu yöntemin DOĞRU uygulandığını BAĞIMSIZ olarak
doğrulamak ve raporlamak. Kendi ürettiğin kodu/tabloyu kendin tekrar
yazma — MEVCUT ÇIKTIYI test et, hataları varsa raporla (düzeltme ayrı bir
onay gerektirebilir).

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/28_ay_hizali_doldurma_dogrulama_prompt.md olarak
kaydet.

======================================================================
GÖREV 1 — HANGİ DOSYA/YÖNTEM OLDUĞUNU NETLEŞTİR
======================================================================
Az önce ürettiğin (veya üretmekte olduğun) ay-hizalı tabloyu tanımla:
dosya adı, 25/26 numaralı görevlerin çıktılarından FARKI ne (26 numaralı
"as-of'tan itibaren taşıma" idi, bu YENİ yöntem "referans aya göre
hizalama" — ikisi FARKLI kurallar, farklı sonuçlar üretir). Bu dosyanın
26 numaralı dosyanın YERİNE mi geçtiğini, yoksa ONA EK üçüncü bir tablo
mu olduğunu netleştir ve raporla.

======================================================================
GÖREV 2 — BAĞIMSIZ DOĞRULAMA (kritik, dikkatle uygula)
======================================================================
En az 5 farklı ay-sütun çifti seç (farklı kaynaklardan — örn. noter
devri, TÜFE, ODMD, proxy fiyat, tüketici güveni — ve farklı dönemlerden:
erken/2016, orta/2020, güncel/2026) ve HER BİRİ İÇİN:

1. O ayın KENDİ REFERANS AYINA ait ham/kaynak değerini (data/raw/
   altındaki orijinal dosyadan) bul.
2. Yeni tabloda, O AYIN TAKVİM GÜNLERİNİN (örn. 2020-06-01'den
   2020-06-30'a kadar HEPSİNİN) gerçekten bu değeri taşıdığını TEK TEK
   (veya nunique()==1 ile toplu) doğrula.
3. AY SINIRI KONTROLÜ: bir önceki ayın SON günü ile bu ayın İLK günü
   arasında değer DOĞRU şekilde değişiyor mu (örn. 2020-05-31 Mayıs
   değerini taşırken, 2020-06-01 HEMEN Haziran değerine geçmeli — bu
   sefer AÇIKLANMA TARİHİNE BAKILMAKSIZIN, çünkü artık kural "referans
   ay = takvim ayı" eşleşmesi).
4. Bunun 26 numaralı görevdeki "as-of'tan itibaren taşıma" davranışından
   FARKLI bir sonuç ürettiğini EN AZ 1 ÖRNEKTE somut olarak göster (iki
   yöntemin aynı tarihte FARKLI değer verdiği bir an bulup karşılaştır)
   — bu, yeni yöntemin gerçekten eskisinden farklı çalıştığının kanıtı
   olacak.

======================================================================
GÖREV 3 — KENAR DURUMLARI KONTROL ET
======================================================================
- İlk ay (tablonun en başı, 2015-01 civarı) doğru işleniyor mu (henüz
  önceki ay verisi olmadığından NaN kalması normal, bunu doğrula).
- Şubat ayının 28/29 gün olduğu yıllarda (artık yıl kontrolü) doğru
  çalışıyor mu.
- BETAM gibi kaynağın 2 ay atladığı (2024-05, 2025-02) durumlarda ne
  oluyor — o aylar tamamen NaN mi kalıyor, yoksa bir önceki ayın değeri
  mi sızıyor? (SIZMAMASI gerekir — kural yalnızca "bu ayın KENDİ
  referans değeri varsa o aya yaz" olmalı, komşu aydan ödünç alma OLMAMALI.
  Bunu özellikle test et, bu en riskli kenar durumu.)
- Kaynağın hiç veri vermediği dönemler (proxy fiyat için 2024 öncesi
  gibi) doğru şekilde NaN kalıyor mu (yoksa yanlışlıkla 0 veya başka bir
  değerle mi dolduruluyor).

======================================================================
GÖREV 4 — TUTARLILIK/BÜTÜNLÜK KONTROLÜ
======================================================================
- Toplam satır sayısı, önceki tablolarla (4234) aynı mı.
- Her ay için, o ayın TÜM günlerinin GERÇEKTEN aynı değeri taşıdığını
  toplu olarak doğrula (her sütun × her ay için nunique() <= 1 olmalı,
  istisna: kaynağın o ay hiç verisi yoksa hepsi NaN olmalı, bu da
  nunique()==0 olarak sayılır, hata değildir).
- Bu toplu kontrolde İSTİSNA (nunique() > 1 olan bir ay-sütun çifti)
  bulursan bunu HATA olarak raporla, gizleme.

======================================================================
YAPMA
======================================================================
- Tabloyu yeniden üretme/kod yazma (bu doğrulama görevi, üretim değil).
- Hata bulursan otomatik düzeltme — sadece raporla, düzeltme kararı ayrı.
- Model/hedef değiştirme.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_ay_hizali_dogrulama.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN olarak göster.

Başlıklar: (1) Hangi dosya/yöntem doğrulandı, 26 numaralı görevden farkı
(Görev 1). (2) 5 örnek doğrulama sonucu (Görev 2, tablo halinde).
(3) 26-numaralı yöntemle FARK gösteren somut örnek (Görev 2, madde 4).
(4) Kenar durumu sonuçları (Görev 3 — özellikle BETAM'ın atladığı aylarda
komşu aydan sızıntı olup olmadığı, NET cevap). (5) Toplu bütünlük kontrolü
sonucu (Görev 4 — kaç ay-sütun çiftinde istisna bulundu, varsa hangileri).
(6) Karşılaşılan sorunlar. (7) Açık sorular / PM onayı gerekenler.
