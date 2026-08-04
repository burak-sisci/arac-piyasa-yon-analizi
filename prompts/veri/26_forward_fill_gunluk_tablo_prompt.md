ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. 25 numaralı görevde, aylık kaynakların YALNIZCA as-of gününde
dolu olduğu (forward-fill YAPILMAMIŞ) bir günlük/karışık-frekans tablo
üretilmişti (data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv,
4234 satır × 48 sütun). Proje sahibi şimdi BUNA EK OLARAK, aylık kaynakların
forward-fill edildiği bir versiyonu da istiyor.

KESİN KURAL — DİKKATLE UYGULA:
- 25 numaralı görevin ürettiği ORİJİNAL tabloya (df_gunluk_karisik_frekans_
  2015_bugun.csv) DOKUNMA, DEĞİŞTİRME, ÜZERİNE YAZMA. O tablo olduğu gibi
  kalacak — "sızıntısız/as-of" referans sürümü olarak korunuyor.
- YENİ VE AYRI bir dosya üret. İki tablo ayrı ayrı var olacak, biri
  diğerinin yerini almayacak.
- FORWARD-FILL MANTIĞI: Her aylık (veya çeyreklik) kaynak sütunu için,
  bir ayın değeri o ayın İÇİNDEKİ TÜM GÜNLERE kopyalanacak. Örnek: Ocak
  ayının noter devir adedi, Ocak'ın 1'inden 31'ine kadar HER GÜNE aynı
  sayı olarak yazılacak; Şubat ayının değeri geldiğinde Şubat'ın tüm
  günlerine o yeni değer yazılacak (Ocak'ın değeri Şubat'a taşmayacak —
  her ay kendi değerini alır, önceki ayın değeri sızmaz).
- GÜNLÜK kaynaklar (USD/TRY, EUR/TRY) zaten günlük olduğu için bu
  sütunlarda DEĞİŞİKLİK YOK, aynen kalır.
- OLAY-BAZLI kaynak (ÖTV) forward-fill EDİLMEZ — bir olay hangi güne aitse
  sadece o gün 1, diğer günler 0 kalmaya devam eder (bunu "doldurmak"
  anlamsız olur, olay tek seferliktir).
- Her forward-fill edilmiş sütun için YANINA bir işaret/bayrak sütunu
  ekle: "..._gercek_mi" (o günün GERÇEK as-of günü mü, yoksa forward-fill
  ile mi dolduruldu — 1/0). Bu, ileride modelin/analizin "bu değer o gün
  gerçekten mi açıklandı, yoksa önceki ayın taşınmış hali mi" ayrımını
  yapabilmesi için ŞART. Şeffaflık olmadan forward-fill yapılmaz.

BAĞLAYICI İLKELER (değişmedi):
- Veri Git-dışı, kod+rapor commit'lenir.
- Şüpheli/beklenmedik bulguları proaktif bildir.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/veri/26_forward_fill_gunluk_tablo_prompt.md olarak
kaydet.

======================================================================
GÖREV 1 — FORWARD-FILL TABLOSUNU ÜRET
======================================================================
- Kaynak: df_gunluk_karisik_frekans_2015_bugun.csv (25 numaralı görevin
  çıktısı) — bunu OKU, üzerine yazma.
- Her aylık/çeyreklik sütun grubu için (TÜFE, ENAG, noter devri, ODMD,
  OSD, tüketici güveni, alım gücü, proxy fiyat/dom/satış oranı, altın —
  25 numaralı raporun Bölüm 3 tablosundaki TÜM "aylık" işaretli kaynaklar)
  forward-fill uygula: ay içindeki ilk (as-of) günden itibaren, bir
  SONRAKİ as-of güne kadar olan TÜM günlere o değeri kopyala.
- İlk ay öncesi (tablonun en başında, henüz hiçbir as-of değeri
  gelmemişken) boş kalan günler NaN kalmaya devam eder (geriye doğru
  doldurma YAPMA, yalnızca ileri doğru forward-fill).
- Her forward-fill edilen sütun için "{sütun_adı}_gercek_mi" bayrak
  sütununu ekle (1 = o gün gerçek as-of günü, 0 = önceki ayın taşınan
  değeri).
- ÖTV olay sütunları (event_gunu_mu vb.) DOKUNULMADAN aynen kopyalanır.
- USD/TRY, EUR/TRY sütunları DOKUNULMADAN aynen kopyalanır (zaten günlük).
- Takvim sütunları (yil, ay, gun, ceyrek, haftanin_gunu, yilin_gunu) aynen
  korunur.
- Çıktı: data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv

======================================================================
GÖREV 2 — DOĞRULAMA
======================================================================
- Rastgele 3 farklı ay seç (biri erken/2016, biri orta/2020, biri güncel/
  2026) ve o ayın TÜM günlerinde forward-fill edilen değerin GERÇEKTEN
  aynı olduğunu, ay değişince değerin GERÇEKTEN değiştiğini kodla
  doğrula (örnek satırlarla göster).
- Toplam satır sayısının 25 numaralı görevdeki orijinal tabloyla AYNI
  (4234) olduğunu doğrula — forward-fill satır eklemez/çıkarmaz, sadece
  var olan NaN'ları doldurur.
- Her sütunun YENİ doluluk oranını (forward-fill sonrası) hesapla ve
  ESKİ (as-of-tek-gün) doluluk oranıyla yan yana karşılaştır.

======================================================================
YAPMA
======================================================================
- Orijinal (25 numaralı) tabloyu değiştirme veya silme.
- Geriye doğru doldurma (backward-fill) — yalnızca ileri yönlü.
- ÖTV olay sütunlarını veya günlük kur sütunlarını forward-fill etme
  (zaten gerekmiyor/anlamsız).
- Korelasyon analizi çalıştırma (ayrı, sonraki görev).
- Hedef/model değiştirme.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_forward_fill_gunluk.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN olarak göster.

Başlıklar: (1) Ne yapıldı. (2) Yeni tablo boyutu (satır × sütun — sütun
sayısı, eklenen "_gercek_mi" bayraklarıyla birlikte, orijinalden fazla
olacak). (3) Doğrulama sonucu (Görev 2 — 3 örnek ay + satır sayısı teyidi).
(4) Doluluk karşılaştırma tablosu (eski vs yeni, sütun bazında). (5)
Karşılaşılan sorunlar. (6) Veri örneği: bir ayın başındaki gerçek as-of
günü + o ayın ortasındaki forward-fill edilmiş bir gün, yan yana (bayrak
sütunuyla birlikte). (7) Açık sorular / PM onayı gerekenler.
