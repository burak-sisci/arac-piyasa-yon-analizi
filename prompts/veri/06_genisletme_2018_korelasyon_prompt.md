ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Mevcut durum: 2024-01 → 2026-06 arası 30 aylık etiketli veri
seti hazır ancak tek rejim (reel düşüş) içeriyor; reel hedef etiket dağılımı
1 up / 8 stable / 16 down. 2021-2023 geriye genişletme denemesi FİZİBİLİTE
AŞAMASINDA BAŞARISIZ OLDU (proxy fiyat kaynağı bulunamadı — bkz.
pm_rapor_kosullu_genisletme.md).

YENİ KARAR: Proje sahibi, YENİ FEATURE eklemek yerine (etkisinin sınırlı
olacağını değerlendiriyor), MEVCUT feature'ların GEÇMİŞİNİ derinleştirmeyi
tercih etti. Hedef: 2018-01'den bugüne kadar TÜM mevcut değişkenleri geriye
genişletmek. Bu, 2021-2023 denemesinden FARKLI — o zaman tek bir eksik seriyi
(proxy fiyat) arıyorduk; şimdi TÜM pipeline'ı geriye çekiyoruz ve proxy fiyat
sorunu muhtemelen YİNE çıkacak (BETAM Aralık 2023 öncesine gitmiyor). Bu
kez bunu ÖNCEDEN kabul ediyoruz: proxy fiyat serisi 2018-2023 aralığında
EKSİK KALABİLİR, bu genişletmeyi durdurmaz — diğer TÜM feature'lar (kur,
TÜFE, faiz, ODMD, OSD, noter, güven, ÖTV olayları) genişletilir; hedef
etiketi yalnızca proxy fiyatın olduğu dönemde üretilir.

ÇALIŞMA İLKESİ: Otomasyona uygun her şeyi UÇTAN UCA, onay beklemeden yap
(CLAUDE.md'deki "Otonomi Sınırı" kuralına göre). Yalnızca HİBRİT/karar
gerektiren noktalarda dur ve proje sahibiyle birlikte ilerle (aşağıda
işaretli). Amaç: tüm veriyi TEK SEFERDE, mümkün olduğunca otonom halletmek.

BAĞLAYICI İLKELER (değişmedi):
- Yalnızca kamuya açık kaynaklar (K5).
- As-of date disiplini, yayım tarihi sütunları korunur.
- WebSearch/dış araç çıktısı resmi kaynakla çapraz doğrulanmadan kullanılmaz.
- Farklı kaynakların serilerini kontrolsüz uç uca ekleme (sahte kırılma riski);
  zincirleme veya ayrı sütun + raporlama.
- Hedef tanımını (K1) kendi başına değiştirme — bağlayıcı karar, PM/proje
  sahibi verir.

======================================================================
GÖREV 0 — BU PROMPTU ARŞİVLE (otomatik, ilk iş)
======================================================================
Bu talimatı prompts/veri/06_genisletme_2018_korelasyon_prompt.md olarak
kaydet ve commit'le. Bundan sonra sana verilen her promptta aynısını yap.

======================================================================
GÖREV 1 — OTONOM: TÜM SERİLERİ 2018-01'E GENİŞLET
======================================================================
Aşağıdaki her seri için 2018-01 → mevcut kapsamın başlangıcına kadar olan
boşluğu doldur (SIRAYLA, ama onay beklemeden — otomasyona uygun):

1a. USD/TRY (TCMB EVDS) — 2018-01'den itibaren, ay sonu + ay ortalaması.
1b. TÜFE (TÜİK/EVDS) — 2018-01'den itibaren. Baz değişiklikleri varsa (2023
    öncesi başka baz olabilir) ZİNCİRLE, mevcut kod zaten 2025 baz geçişini
    başarıyla zincirlemişti — aynı yaklaşımı uygula, dönüşümü raporla.
1c. Taşıt kredisi faizi + politika faizi (TCMB EVDS) — 2018-01'den itibaren.
1d. ODMD satış adetleri (toplam/otomobil) — 2018-01'den itibaren.
1e. OSD üretim (binek + kamyonet) — 2018-01'den itibaren.
1f. Noter devir adedi (TÜİK) — 2018-01'den itibaren.
1g. Tüketici güven endeksi + oto satın alma ihtimali (TÜİK) — 2018-01'den
    itibaren.
1h. ÖTV/vergi düzenleme olayları (Resmî Gazete) — 2018-2023 arası TÜM
    düzenlemeleri tarihli event olarak ekle (bu dönemde birden fazla ÖTV
    değişikliği olduğunu unutma — hepsini bul, tek bir tanesini değil).
1i. Brüt ücret-maaş endeksi (TÜİK, çeyreklik→aylık) — 2018-01'den itibaren;
    önceki genişletmede olduğu gibi çeyreklik→aylık kopyalama olduğunu
    açıkça işaretle (gerçek ay-ay varyasyon değil).

Her seri için kaynak seviyesini (A-E, önceki promptlardaki tanım) ve
kapsanan gerçek aralığı raporla. Bir seri 2018'e gidemiyorsa (ör. kaynak o
tarihte başlamıyor), NEREDEN başladığını raporla, uydurma.

======================================================================
GÖREV 2 — OTONOM: PROXY FİYAT SERİSİNİ MÜMKÜN OLDUĞUNCA GENİŞLET
======================================================================
BETAM Aralık 2023'ten öncesine gitmiyor (bilinen kısıt). Yine de:
- arabam.com'un 2018-2023 arası herhangi bir aylık/yıllık fiyat verisi
  (bülten, blog, AA aktarımı) olup olmadığını KISA bir taramayla kontrol et
  (önceki fizibilite kadar derin değil — 30 dakikalık bir kontrol).
- Bulursan ve BETAM ile aynı büyüklüğü ölçüyorsa (ortalama ilan fiyatı),
  zincirleme dene; farklı büyüklükse ayrı sütunda tut, birleştirme.
- Bulamazsan: proxy fiyat serisi yalnızca Aralık 2023'ten itibaren dolu
  kalır. Bunu KABUL ET, dur, raporla — 2021-2023 fizibilitesindeki gibi
  saatlerce uğraşma. Diğer feature'lar 2018'den itibaren dolu olacak; hedef
  etiketi yalnızca proxy'nin olduğu dönemde üretilecek. Bu meşru bir sonuçtur.

======================================================================
GÖREV 3 — OTONOM: BİRLEŞTİRME VE HEDEF ETİKET
======================================================================
- Tüm serileri referans_ayi ile birleştir, tek tablo: 2018-01 → 2026-06.
- Hedef etiketi (nominal/reel/tercile) proxy fiyatın dolu olduğu aralıkta
  (muhtemelen 2023-12'den itibaren) üret; öncesi için proxy/hedef sütunları
  NaN kalır (feature sütunları dolu kalır — bu normal, feature'lar tahmin
  ANINDA kullanılacak, hedefin kendisi değil).
- Yeni sınıf dağılımını raporla (değişmeyecek, çünkü proxy dönemi aynı) —
  ama bu artık ÇOK DAHA FAZLA GEÇMİŞ FEATURE bağlamıyla birlikte duruyor;
  bu, ileride modelin daha uzun bir feature-geçmişinden (ör. 12 ay geriye
  lag) yararlanmasını sağlar.
- Veri sözlüğünü ve doluluk dökümünü (önceki formatta) güncelle.

======================================================================
GÖREV 4 — OTONOM: KORELASYON VE HEDEF-ADAY ANALİZİ
======================================================================
Bu, yarınki ekip lideri toplantısı için EN KRİTİK çıktı. Analiz Python'da
yapılsın, sonuçlar hem tablo hem görselleştirilebilir veri olarak
üretilsin (PM bunları bir sunuma dönüştürecek).

4a. HEDEF ADAYLARI — şu serilerin HER BİRİ için ayrı ayrı aylık log-değişim
    üret ve potansiyel hedef olarak değerlendir:
    - proxy fiyat (nominal + reel) — mevcut hedef
    - noter devir adedi (hacim)
    - proxy_dom_gun (hız, ters yönlü yorumlanır — düşerse piyasa hızlanıyor)
    - proxy_satis_orani_pct (dönüşüm hızı)
    - ODMD toplam satış (arz hacmi)
    Her aday için: kaç geçerli aylık gözlem var, aylık değişimin std sapması
    (oynaklık), ve ±0.5σ bandıyla up/stable/down dağılımı NASIL ÇIKARDI
    (deneme amaçlı, hedefi DEĞİŞTİRMEDEN sadece göster).

4b. KORELASYON MATRİSİ — tüm feature'ların (kur, TÜFE, faiz, ODMD, OSD,
    noter, güven, alım gücü, erişim endeksi) aylık değişimleri ile YUKARIDAKİ
    her hedef adayının aylık değişimi arasında Pearson VE Spearman korelasyonu
    hesapla (az-gözlemde Spearman daha dayanıklı olabilir, ikisini de ver).
    - Her feature-hedef çifti için: korelasyon katsayısı, p-değeri, kaç
      gözlemle hesaplandığı.
    - AZ-GÖZLEM UYARISI ZORUNLU: p-değerlerinin 25-90 gözlemle güvenilirliği
      sınırlıdır; bunu raporda ve çıktıda AÇIKÇA belirt. "Yüksek korelasyon"
      "kanıtlanmış nedensellik" DEĞİLDİR — bunu hem kod çıktısında hem
      PM'e iletilecek raporda vurgula.
    - Beklenen işaretlerle (ör. kur↑→fiyat↑, faiz↑→talep↓) TUTARLI mı
      DEĞİL mi işaretle — yön beklentiye aykırıysa özellikle vurgula.

4c. ÇIKTI DOSYALARI:
    - data/processed/analiz/korelasyon_matrisi.csv (feature x hedef-adayı,
      hem Pearson hem Spearman, hem p-değeri)
    - data/processed/analiz/hedef_aday_karsilastirma.csv (her hedef adayının
      gözlem sayısı, oynaklığı, sınıf dağılımı)
    - Grafik-hazır veri: her feature-hedef çifti için zaman serisi verisi
      (PM bunu görselleştirecek) — data/processed/analiz/zaman_serileri.csv

======================================================================
DUR VE HİBRİT — PROJE SAHİBİYLE BİRLİKTE (buraya kadar otonom, burada dur)
======================================================================
Analiz tamamlanınca DUR. Aşağıdakileri OTONOM OLARAK YAPMA, PM'e/proje
sahibine bırak:
- Hangi hedef adayının seçileceği kararı (K1 değişikliği — bağlayıcı karar).
- Korelasyon sonuçlarının yorumlanması ve iş anlamına çevrilmesi (bu, ekip
  lideri toplantısının konusu).
- Sunum/görselleştirme üretimi (PM tarafında yapılacak).

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_genisletme2018_korelasyon.md üret VE
tamamını oturumda KOPYALANABİLİR DÜZ METİN (kod bloğu) olarak göster.

Başlıklar: (1) Ne yapıldı — genişletme özeti, her serinin kapsadığı gerçek
aralık. (2) Proxy fiyat sonucu — 2018-2023 için bulunabildi mi, hangi
dönemden itibaren dolu. (3) Yeni veri seti boyutu (satır×sütun, dönem).
(4) Korelasyon analizi ÖZET BULGULARI — en yüksek |korelasyon| gösteren
5-10 feature-hedef çifti, işaretleriyle birlikte; az-gözlem uyarısı. (5) Hedef
aday karşılaştırması — hangi aday hangi sınıf dağılımını veriyor (tablo).
(6) Karşılaşılan sorunlar (gizleme). (7) Açık sorular/PM onayı gerekenler —
özellikle "hangi hedefi seçelim" sorusu burada net şekilde sorulsun.
(8) Veri örneği (ilk/son 3 satır, kritik sütunlar).

YAPMA:
- Hedef tanımını kendi başına değiştirme veya "en iyi" hedefi otomatik seçme.
- Proxy fiyat için 2018-2023 arayışını saatlerce sürdürme (30 dk kontrol yeter).
- Farklı kaynakların serilerini kontrolsüz birleştirme.
- Model kurma/tahmin (ayrı aşama).
