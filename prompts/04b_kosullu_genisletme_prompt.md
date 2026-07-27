ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Mevcut durum: 2024-01 → 2026-06 arası 30 aylık etiketli veri seti
hazır. SORUN: reel hedef etiketin sınıf dağılımı 1 up / 8 stable / 16 down —
eğitim dönemi tek rejimden (reel düşüş) ibaret; tek "up" gözlemiyle o sınıf
öğrenilemez.

ÇÖZÜM HİPOTEZİ: Veriyi 2021-2023'e geriye genişletmek farklı bir rejim
kazandırabilir. Ön koşul: o dönem için bir proxy fiyat serisi bulunabilmeli.
BETAM sahibindex Aralık 2023'te başladığından, alternatif kaynak gerekiyordu.

BU TALİMATLA BİRLİKTE SANA BİR FİZİBİLİTE ARAŞTIRMASI ÇIKTISI VERİLECEK
(ayrı bir araçta yapıldı). O çıktı, hangi kaynakların mevcut olduğunu söylüyor.
Senin işin: o bulguları DOĞRULAMAK ve uygulamak. Araştırma çıktısındaki
iddiaları körü körüne kabul etme — her kaynağı kendin test et.

BAĞLAYICI İLKELER:
- Yalnızca kamuya açık kaynaklar (K5).
- Kaynaksız iddia yazılmaz; rejim veriden KEŞFEDİLİR, önceden VARSAYILMAZ.
  "Çip krizi = reel yükseliş" bir hipotezdir; veri gelmeden kabul edilmez.
- WebSearch/dış araç çıktısından gelen rakamlar RESMİ KAYNAKLA ÇAPRAZ
  DOĞRULANMADAN kullanılmaz (bu projede daha önce yıl-karışması hatası
  kanıtlanmıştır).
- As-of date disiplini, leakage önleme; veri Git-dışı, kod+rapor commit'lenir.

======================================================================
GÖREV 1 — KIRMIZI BAYRAK TARAMASI (önce bu, kısa tut)
======================================================================
Genişletmeye girmeden ÖNCE mevcut 30 aylık etiketli veri setine hızlı tarama
(dakikalar, tam analiz DEĞİL):
- Tarih sürekliliği: eksik/çift ay var mı?
- İmkânsız değerler: negatif fiyat, sıfır kur, aşırı aylık değişim.
- Hedef zinciri: proxy_fiyat_cari_tl → log değişim → etiket zinciri 2-3 ay için
  elle doğrulanabiliyor mu?
- Reel hesap: nominal − TÜFE ≈ reel mantığı tutuyor mu (spot kontrol)?
Bulduğun her şeyi raporla. HATA VARSA genişletmeye geçme, önce bildir.

======================================================================
GÖREV 2 — FİZİBİLİTE BULGULARINI DOĞRULA
======================================================================
Sana verilen araştırma çıktısındaki her aday kaynak için:
- URL'yi gerçekten fetch et / API'yi gerçekten çağır. Erişilebiliyor mu?
- Kapsadığı dönem iddia edilen dönem mi? (2021-2023 gerçekten var mı?)
- Frekans aylık mı?
- Ne ölçüyor: ortalama ilan fiyatı mı, endeks mi, değişim oranı mı?
- Makine-okunur mu, yoksa PDF/HTML kazıma mı gerekiyor?
- Araştırma çıktısındaki örnek rakamı kaynakta DOĞRULA. Tutmuyorsa bunu
  açıkça raporla (araştırma hatalı olabilir).

ÖZEL DİKKAT — TÜİK TÜFE ALT KALEMİ: Eğer araştırma "TÜFE sepetinde ikinci el
otomobil maddesi var" diyorsa, bunu EVDS'de bizzat doğrula: seri kodunu bul,
API'den çek, dönem kapsamını gör. Bu en yüksek getirili adaydır (resmi, aylık,
uzun geçmişli). Doğrularsan sorun büyük ölçüde çözülür.

KARAR: Doğrulanmış, kullanılabilir bir kaynak VAR mı? Net cevap ver.

======================================================================
GÖREV 3 — KOŞULLU GENİŞLETME (yalnızca Görev 2 olumluysa)
======================================================================
EĞER kullanılabilir kaynak DOĞRULANDIYSA:
- 2021-01 → 2023-12 için proxy fiyat serisini çek.
- Aynı dönem için diğer serileri de geriye uzat: USD/TRY, TÜFE, taşıt kredisi
  faizi, ODMD satışları, noter devir adedi, tüketici güveni, OSD üretim,
  ÖTV olayları (EVDS/TÜİK/ODMD bu döneme sorunsuz gitmeli).
- Birleşik tabloyu 2021-01 → 2026-06 olarak yeniden kur.
- Hedef etiketi TÜM seri üzerinde yeniden üret (σ daha uzun seriden hesaplanacak
  → daha güvenilir bant).
- YENİ SINIF DAĞILIMINI raporla: "up" sınıfı ortaya çıktı mı? ÇIKMADIYSA açıkça
  yaz — hipotez doğrulanmadı demektir; bu da geçerli bir bulgudur.

SERİ BİRLEŞTİRME UYARISI (kritik): Farklı kaynaklar farklı büyüklükleri ölçer
(ortalama ilan fiyatı vs endeks vs medyan). İki seriyi körü körüne uç uca eklemek
SAHTE BİR SIÇRAMA yaratır ve etiketleri bozar. Örtüşen dönem varsa zincirleme
(chaining) katsayısıyla birleştir; örtüşme yoksa AYRI SÜTUN olarak tut ve
durumu raporla. Birleştirme yöntemini açıkça belgele.

EĞER kaynak DOĞRULANAMADIYSA:
- GENİŞLETME YAPMA. Hangi adaylar denendi, neden olmadı — net raporla.
- Hedef tanımını KENDİ BAŞINA DEĞİŞTİRME (üç sınıf → ikili gibi). Bu bağlayıcı
  bir karardır; proje sahibi ve PM verir. Sadece raporla ve öneri sun.

======================================================================
GÖREV 4 — CLAUDE.md GÜNCELLEMESİ (otonomi kuralları)
======================================================================
CLAUDE.md'ye aşağıdaki bölümü ekle (mevcut kuralları bozmadan):

"## Otonomi Sınırı — Kullanıcı Gerekli / Gerekli Değil

Bu projede iş süreçleri ikiye ayrılır. 'Kullanıcı gerekli' olmayan tüm işler
Claude Code tarafından onay beklenmeden uçtan uca yürütülür; proje sahibi
gerektiğinde müdahale eder.

KULLANICI GEREKLİ (onay/karar beklenir):
- Bağlayıcı karar değişiklikleri (hedef tanımı, kapsam, K/N maddeleri).
- Yeni bir AŞAMA TÜRÜ başlatma (ör. veri toplamadan modellemeye geçiş).
  Aynı aşama içindeki adım geçişleri onay gerektirmez.
- Para/hesap gerektiren işlemler (API anahtarı, ücretli servis).
- Kapsam dışına çıkacak veya geri alınması zor işlemler.

KULLANICI GEREKLİ DEĞİL (otonom yürütülür):
- Veri çekme, temizleme, birleştirme, doğrulama adımları.
- Kod yazma, refactor, test, hata düzeltme.
- Klasör/dosya organizasyonu, commit ve push.
- Rapor ve dokümantasyon üretimi.

PROAKTİF BİLDİRİM (onay değil, bilgilendirme — sessiz kalınmaz):
- Şüpheli/doğrulanmamış bulgular (kaynaklar arası çelişen rakamlar, dış araç
  çıktısındaki hatalar vb.).
- Beklenmedik sonuçlar, bloke edici riskler, varsayımla çözülen noktalar.
- PM raporları (bilgilendirme amaçlı iletilir, onay beklenmez).

Kural: Şüphe varsa bildir; bildirmemek, yanlış ilerlemekten daha maliyetlidir."

======================================================================
PM RAPORU — ZORUNLU
======================================================================
İş bitince data/processed/raporlar/pm_rapor_kosullu_genisletme.md üret.
AYRICA raporun tamamını oturumda KOPYALANABİLİR DÜZ METİN (kod bloğu) olarak
göster — proje sahibi bunu PM'e iletecek, dosya aktarımı sorunlu.

Başlıklar:
1. NE YAPILDI — adımlar, üretilen/değişen dosyalar (yollarıyla).
2. KIRMIZI BAYRAK SONUCU — bulunanlar (yoksa "temiz").
3. FİZİBİLİTE DOĞRULAMA — her aday: iddia neydi, doğrulandı mı, kaynak URL,
   örnek rakam tuttu mu. NET KARAR: genişletme yapıldı mı?
4. (Yapıldıysa) SAYISAL ÖZET — yeni tablo boyutu, kapsanan dönem, YENİ SINIF
   DAĞILIMI (up/stable/down), eksik hücre dökümü.
5. SERİ BİRLEŞTİRME NOTU — nasıl birleştirildi, sahte kırılma riski nasıl
   ele alındı.
6. VERİ ÖRNEĞİ — ilk 3 ve son 3 satır (kritik sütunlarla), ham.
7. KARŞILAŞILAN SORUNLAR — gizleme; varsayımla çözülenler dahil.
8. AÇIK SORULAR / PM ONAYI GEREKENLER.
9. ÖNERİLEN SONRAKİ ADIM — başlatma, öneriyle bırak.

YAPMA:
- Hedef tanımını kendi başına değiştirme.
- Farklı kaynakların serilerini kontrolsüz uç uca ekleme.
- Dış araç çıktısındaki rakamı doğrulamadan kullanma.
- Veriye dayanmayan varsayımı (çip krizi yükselişti gibi) sonuç gibi yazma.
- Modelleme/tahmin (ayrı aşama).