ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Ekip toplantısında zaman çözünürlüğünü aylıktan günlüğe
çekme kararı alındı. BU KARARIN NASIL UYGULANACAĞI ÖNEMLİ — kararı
kelimesi kelimesine ama YANLIŞ yorumlarsan projeye zarar verirsin, o
yüzden aşağıdaki kesin kuralı dikkatle oku.

KESİN KURAL (proje sahibi onayladı, sorgulamadan uygula):
- Yalnızca DOĞASI GEREĞİ günlük olan kaynaklar (döviz kurları, altın
  fiyatı) GERÇEK GÜNLÜK değerlerle günlük satırlara sahip olacak.
- Doğası gereği AYLIK olan kaynaklar (TÜFE, ENAG, noter devir adedi,
  ODMD satışları, OSD üretim, tüketici güven endeksi, alım gücü proxy'si,
  ÖTV olayları — hangileri kaldıysa) FORWARD-FILL İLE GÜNLÜK
  GÖRÜNÜME GETİRİLMEYECEK. Bunlar kendi doğal aylık satırlarında
  kalacak; günlük tabloyla İLİŞKİLENDİRİLECEK (aynı tabloda referans_ay
  sütunuyla eşlenebilir) ama her güne yapay olarak kopyalanmayacak.
- SONUÇ: tek bir tabloda İKİ FARKLI GRANÜLERLİKTE veri bir arada duracak
  (karışık frekans). Bu YAPISAL bir tasarımdır, hata değildir — bunu
  netçe belgele.
- NEDEN BÖYLE: aylık bir değeri her güne kopyalamak (forward-fill), model
  için "bu değer her gün değişiyor" yanılsaması yaratır; oysa gerçekte
  ayda bir değişiyor. Bu, projenin "sahte sinyal üretme" konusundaki
  disiplinine (N7, falsifikasyon ilkesi) aykırı düşer.

BAĞLAYICI İLKELER (değişmedi):
- Yalnızca kamuya açık kaynaklar (K5).
- As-of date disiplini korunur.
- WebSearch/dış kaynaktan gelen rakamlar ikinci kaynakla doğrulanmadan
  kullanılmaz.
- Veri Git-dışı, kod+rapor commit'lenir.

ÇALIŞMA MODU — İKİ AŞAMALI, OTONOMİ SINIRINA UYGUN (CLAUDE.md):
- OTONOM AŞAMA: aşağıdaki Görev 0-4 arası, kullanıcı onayı BEKLEMEDEN
  sırayla yürütülür.
- MANUEL AŞAMA: yeni bir API anahtarı/hesap kaydı gerekiyorsa, bunu
  DURDURMADAN devam et ama proje sahibine NET bir bildirim/talimat
  hazırla (Görev 5) — hangi siteden, nasıl alınacağını adım adım anlat.
  Anahtar gelene kadar o kaynağı "bekliyor" olarak işaretleyip diğer
  kaynaklarla devam et, tüm işi durdurma.
- Token-yoğun olabilecek adımlarda (örn. çok uzun bir günlük seri
  taraması) proje sahibinden yardım istemekten çekinme — bunu Görev 5'te
  açıkça belirt.
- Şüpheli/beklenmedik bulguları PROAKTİF bildir, sessiz geçme.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/veri/25_gunluk_eur_altin_karisik_frekans_prompt.md
olarak kaydet.

======================================================================
GÖREV 1 — EUR/TRY VE ALTIN/TRY: API ANAHTARI DURUMU KONTROLÜ
======================================================================
- EUR/TRY: TCMB EVDS seri kodu TP.DK.EUR.A.YTL — MEVCUT EVDS anahtarınla
  (USD/TRY'yi çektiğin aynı anahtar) çekilebilir. YENİ ANAHTAR GEREKMEZ.
  Bunu doğrula (bir deneme çağrısı yap) ve teyit et.
- Altın/TRY (gram altın): TCMB EVDS "Kıymetli Madenler" kategorisi,
  bie_mkaltytl serisi altında olması bekleniyor — tam seri kodunu EVDS
  kategori/seri arama üzerinden bul (muhtemelen TP.MK. öneki taşıyor).
  MEVCUT EVDS anahtarınla denenmeli — YENİ ANAHTAR GEREKMEMESİ bekleniyor.
  Doğrula ve teyit et.
- İKİSİ DE mevcut anahtarla çalışıyorsa: Görev 5'te "yeni anahtar
  gerekmedi" diye NET bir şekilde raporla — proje sahibinin kayıt
  açmasına gerek YOK.
- Çalışmıyorsa: alternatif ücretsiz kaynak ara (ör. TCMB'nin kendi kur/
  altın arşiv sayfası, ya da başka resmi kurum), bulursan Görev 5'te API
  anahtarı gerekip gerekmediğini ve nereden alınacağını NET adımlarla yaz.

======================================================================
GÖREV 2 — GÜNLÜK EUR/TRY VE ALTIN/TRY ÇEKME (OTONOM)
======================================================================
- Mevcut USD/TRY günlük çekme yöntemiyle AYNI mantıkla (data/raw/usdtry/
  altındaki günlük dosya formatına benzer), EUR/TRY ve Altın/TRY günlük
  serilerini 2015-01-01'den bugüne kadar çek.
- EVDS'in 1000-satır sessiz kesme davranışına DİKKAT (önceki
  genişletmelerde keşfedilmişti) — uzun aralığı gerekirse tarih-parçalama
  (chunking) ile çek, satır sayısını doğrula.
- Çıktı: data/raw/eurtry/eurtry_gunluk_2015_bugun.csv,
  data/raw/altintry/altintry_gunluk_2015_bugun.csv.

======================================================================
GÖREV 3 — data/raw ENVANTERİ: HANGİ KAYNAK GÜNLÜK, HANGİSİ AYLIK
======================================================================
data/raw/ altındaki TÜM kaynakları tara ve her biri için DOĞAL frekansını
(günlük/haftalık/aylık/çeyreklik/olay-bazlı) belirle. Bir tablo üret:
kaynak | doğal frekans | günlük tabloya nasıl dahil edilecek (gerçek
günlük mü, yoksa aylık-referans olarak mı bağlanacak mı).

Beklenen sonuç: USD/TRY, EUR/TRY, Altın/TRY = günlük. TÜFE, ENAG, noter
devri, ODMD, OSD, tüketici güveni, alım gücü = aylık (forward-fill
YAPILMAYACAK). ÖTV olayları = olay-bazlı (hangi güne denk geldiği
biliniyorsa o günde işaretlenir, aksi halde ay başına atanır — bunu
netleştir).

======================================================================
GÖREV 4 — KARIŞIK-FREKANS TABLOSUNU KUR
======================================================================
- Ana tabloyu GÜNLÜK tarih ekseninde kur (2015-01-01 → bugün, her gün bir
  satır — hafta sonu/tatil günleri dahil, kur/altın o günlerde
  yayımlanmıyorsa NaN kalabilir, bunu belirt).
- Günlük sütunlar (USD/TRY, EUR/TRY, Altın/TRY): her güne gerçek değer.
- Aylık sütunlar (TÜFE, ENAG, noter devri vb.): SADECE o ayın verisinin
  YAYIMLANDIĞI gün (as-of date) dolu, diğer günlerde NaN. Forward-fill
  YOK. Ayrıca her aylık sütun için referans_ay adlı bir yardımcı sütun
  tut (hangi aya ait olduğu, birleştirme/analiz kolaylığı için).
- TARİH FORMATI: tarih sütunu GERÇEK date/datetime tipinde kalacak
  (string veya sayısal doğal-sayı formatına ÇEVRİLMEYECEK). Buna EK
  olarak şu türetilmiş TAKVİM sütunlarını oluştur (tarihi silme, yanına
  ekle): yil, ay, gun, ceyrek, haftanin_gunu, yilin_gunu. Bu, ileride
  hangi model ailesi (klasik zaman serisi / ağaç-tabanlı / hibrit)
  seçilirse seçilsin, tablo yeniden hazırlanmadan kullanılabilsin diye.
- Çıktı: data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv

======================================================================
GÖREV 5 — MANUEL AŞAMA BİLDİRİMİ (yalnızca gerekiyorsa)
======================================================================
Eğer Görev 1'de herhangi bir kaynak için YENİ bir API anahtarı/hesap kaydı
gerektiği tespit edildiyse, proje sahibine NET bir talimat hazırla: hangi
sitede, hangi sayfada, nasıl kayıt olunacağı, anahtarın nereye
gireceği (ortam değişkeni — KODA GÖMME). Bu görev tamamlanmadan diğer
kaynaklarla İŞİ DURDURMA, bekleyen kaynağı işaretleyip devam et.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_gunluk_karisik_frekans.md üret VE
oturumda KOPYALANABİLİR DÜZ METİN olarak göster.

Başlıklar: (1) Ne yapıldı. (2) API anahtarı durumu — EUR/Altın için yeni
anahtar gerekti mi (Görev 1 sonucu, net). (3) data/raw envanteri (Görev 3
tablosu). (4) Karışık-frekans tablo boyutu, kapsamı, hangi sütun hangi
frekansta. (5) Manuel aşama bildirimi (varsa, Görev 5). (6) Karşılaşılan
sorunlar. (7) Veri örneği (bir günlük-dolu satır + bir aylık-dolu satır +
bir hiçbir aylık verinin düşmediği ara gün). (8) Açık sorular / PM onayı
gerekenler.

YAPMA:
- Aylık kaynakları forward-fill ile günlük görünüme getirme.
- Tarihi string veya sayısal indekse çevirme (date formatı korunur).
- Hedef/model değiştirme, korelasyon analizi çalıştırma (sonraki adım).
- Onay bekleyerek işi durdurma — otonom kısmı sonuna kadar götür.
