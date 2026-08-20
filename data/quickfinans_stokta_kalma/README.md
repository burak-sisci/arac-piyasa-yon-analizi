# Quick Finans – SmartIQ "2. El Oto Raporu": ikinci el stokta kalma süresi

Quick Finans (tüketici finansmanı şirketi), veri analitiği ortağı **SmartIQ** ile birlikte
**aylık** bir "2. El Oto Raporu" yayımlıyor. Bu raporun temel kalemi, ikinci el bir aracın
(0-15 yaş, ~350.000 km altı; galeri/ekspertiz ağı kaynaklı) satılana kadar ortalama kaç gün
**stokta/piyasada kaldığıdır** — projenin aradığı "araçlar ne kadar hızlı satışa dönüyor"
sorusuna doğrudan cevap veren bir gösterge.

Bu, Indicata'nın **online ilan kaldırma** bazlı `ortalama_satis_hizi_gun` metriğinden
(bkz. `data/indicata/`) **farklı, bağımsız bir metodolojidir** — muhtemelen galeri/ekspertiz ağı
verisine dayanıyor. Indicata'nın bu metriği yalnızca 2024'te yayımlanıp sonra kesildiği için,
Quick Finans serisi tam olarak Indicata'nın bıraktığı 2025+ boşluğunu dolduran/tamamlayan bir
kaynak niteliğinde.

## Dosyalar

### `quickfinans_aylik_stokta_kalma.csv`

**2024-09 → 2026-06 arası 20 aylık gözlem** (2024-11 ve 2024-12'de iç boşluk var — bkz. aşağıda).
İlk sürümde yalnızca 2025-05 → 2026-06 (14 ay) vardı; 2. turda geriye dönük genişletme
araştırıldı ve **pazar/binek/ticari formatıyla uyumlu** 6 yeni ay (2024-09, 2024-10, 2025-01,
2025-02, 2025-03, 2025-04) eklendi, ayrıca 2025-05 ve 2025-12 satırlarının binek/ticari
kırılımları tamamlandı. Sütunlar:

- `stokta_kalma_suresi_gun_pazar/_binek/_ticari`: pazar ortalaması ve araç tipi kırılımı (gün).
- `veri_turu`: `dogrudan` (o ayın kendi raporu WebFetch ile tam metinden doğrulandı) veya
  `turetilmis` (bir sonraki ayın raporundaki "X günden Y güne çıktı/indi" karşılaştırma
  cümlesinden türetildi — kendi ayının raporu bu turda bulunamadı). Türetilmiş satırlarda
  binek/ticari kırılımı bazen bilerek boş bırakıldı; yalnızca pazar ortalaması güvenilir şekilde
  türetilebiliyordu.
- Ana kanal Anadolu Ajansı (aa.com.tr); AA'nın haberi resmi rapordan birebir alıntıladığı,
  bazı aylarda ikinci bir haber sitesiyle (sigortacigazetesi.com.tr, cnbce.com, haberler.com,
  hergungazetesi.com, yeniakit.com.tr, milligazete.com.tr) çapraz doğrulandığı için güvenilirlik
  sorunu yok. Resmi arşiv sayfası (`quickfinans.com.tr/kurumsal/ikinci-el-oto-raporu/`) JS ile
  render olduğu için WebFetch doğrudan içerik çekemedi; bu yüzden doğrulama syndike eden haber
  siteleri üzerinden yapıldı.

**İç boşluklar (2024-11, 2024-12):** Bu iki ay için pazar/binek/ticari formatında uyumlu veri
bulunamadı — 2024-11'in bulunan tek "pazar" rakamı (53) segment-bazlı (B/C/D/E) bir raporda
geçiyor ve 2024-10'un pazar değeriyle (53) tesadüfen aynı olduğundan güvenilir sayılmayıp
`quickfinans_erken_donem_2023_2024_farkli_format.csv`'ye kondu; 2024-12 için hiçbir uyumlu
rakam bulunamadı (yalnızca elektrikli araç alt-segmentine özel, ilgisiz bir "59 gün" bulundu).

### `quickfinans_erken_donem_2023_2024_farkli_format.csv`

2023-09 → 2024-11 arası, ana dosyayla **doğrudan birleştirilmemiş** 8 satır. Bu dönemin
raporları farklı bir çerçeve kullanıyor gibi görünüyor — 2024'ün ilk yarısında segment bazlı
(B/C/D/E fiyat/lüks segmentleri) raporlama, 2023 sonunda ise yalnızca tek bir "pazar" rakamı
(binek/ticari kırılımı yok) görülüyor; pazar/binek/ticari formatı ilk net olarak 2024-09'da
ortaya çıkıyor. Bu yüzden bu satırlar metodolojik süreklilik garantisi olmadan ana seriye
eklenmedi. İçerik:

- 2023-09, 2023-10: pazar-only (kırılım yok).
- 2023-11: kesin rakam yok, yalnızca ">65 gün" ifadesi — sayısal kolon bilerek boş bırakıldı.
- **2024-01: İKİ FARKLI KAYNAKTAN BİRBİRİYLE ÇELİŞEN İKİ DEĞER** (52 gün vs 70 gün) — hangisinin
  doğru olduğu çözülemedi, ikisi de "CELISKILI" etiketiyle ayrı satırlar halinde kayıtlı.
  **Bu ayı kullanmayın**, yalnızca şeffaflık için saklandı.
- 2024-04: segment bazlı (B/C/D/E), tek "pazar" rakamına indirgenemez.
- 2024-07: "sıfır km muadili araçlar" için niş bir alt-metrik, pazar geneli değil.
- 2024-11: segment bazlı format ama bir "pazar" rakamı da veriyor (53) — güvenilirliği şüpheli
  (2024-10 ile aynı rakam, tesadüf mü seri tekrarı mı belirsiz).

### `smartiq_ceyreklik_farkli_metodoloji.csv`

SmartIQ'nun kendi sitesinde ayrıca yayımladığı **çeyreklik** "İkinci El Otomotiv Pazar Raporu"
— 2026 Ç1: 35,8 gün, 2026 Ç2: 38,4 gün. Bu rakamlar Quick Finans'ın aylık serisinden (42-52 gün)
belirgin şekilde farklı bir aralıkta; muhtemelen farklı araç segmenti/tanım kullanıyor.
**Bu iki seri kesinlikle karıştırılmamalı** — ayrı dosyalarda tutuldu.

## Metodoloji notları / bilinmeyenler

- Rapor hâlâ aktif yayımlanıyor (en son görülen: 2026-06 verisi, 16.07.2026 tarihli haber);
  gelecek aylarda seri genişletilebilir — bkz. "Devam eden yayın" aşağıda.
- **2. tur genişletme sonuçları (kapsam boşlukları):** 2023-12, 2024-02, 2024-03, 2024-05,
  2024-06, 2024-08, 2024-12 için hiçbir doğrulanabilir kaynak bulunamadı — WebSearch bazen
  bu aylar için rakam "üretti" ama WebFetch ile açıldığında rakamların aslında başka bir yıla
  ait olduğu ortaya çıktı (arama motoru özet karışıklığı); bu yüzden hiçbiri eklenmedi.
  **2024-09'dan önceki seri, dolayısıyla parça parça (2023 sonu + 2024 başı-ortası büyük ölçüde
  boş) kalıyor** — sürekli/kesintisiz bir 2023-2024 serisi mümkün olmadı.
- **Resmi arşiv sayfası artık eski derin linkleri sunmuyor:** `quickfinans.com.tr`'nin eski ay
  slug'ları (`/kasim-2024/`, `/aralik-2024/`, `/ekim-2024/`, `/mart-2025/` vb.) tek tek denendi;
  hepsi aynı jenerik listeye düşüyor ve yalnızca son ~4 ayı gösteriyor. Bu bir JS-render sorunu
  değil, sitenin eski sayfaları artık barındırmaması. Wayback Machine (web.archive.org) de
  denendi ama bu oturumdaki WebFetch aracı o domaine erişemiyor — ileride farklı bir araçla
  denenebilir.
- "15 yaş üstü araçlar" için ayrı bir stokta kalma süresi serisi de raporlarda mevcut
  (Mayıs 2026: 51 gün, Haziran 2026: 52 gün gibi) — istenirse üçüncü bir segment sütunu
  olarak eklenebilir; bu turda dahil edilmedi.
- Arabam.com CEO'sunun "araç dönüş süresini 3,5-4 günden 2,5 güne indirdik" açıklaması
  bulundu ama bu şirketin kendi trink-sat operasyonuna özgü, pazar geneli bir istatistik
  değil — veri noktası olarak eklenmedi.

## Devam eden yayın

Aylık basın bültenleri düzenli yayımlanıyor (genelde bir sonraki ayın 14-19'u arası). Seri
güncellenmek istenirse `aa.com.tr` üzerinde "Quick Finans [ay] ayı 2. El Oto Raporu" aramasıyla
takip edilebilir.

## Kapsam ve target kullanımı

`quickfinans_aylik_stokta_kalma.csv`'deki `stokta_kalma_suresi_gun_pazar` sütunu,
`scripts/hiz_target_backtest_pipeline.py`'deki `target_quickfinans_dom_gun` hedefinin kaynağıdır
(`EXTERNAL_TARGET_SOURCES` mekanizmasıyla, master veri setine dokunmadan okunur). Seri
genişletildikten sonra (20 gözlem, 2024-09 → 2026-06) t-12 referansı artık çok daha fazla ay için
hesaplanabiliyor — ilk sürümde yalnızca 2 backtest ayı mümkündü, genişletme sonrası pipeline
yeniden çalıştırılıp `outputs/hiz_target_backtest/target_quickfinans_dom_gun/` altındaki
sonuçlar güncellenmelidir. `quickfinans_erken_donem_2023_2024_farkli_format.csv`'deki satırlar
metodoloji sürekliliği garanti edilemediği için **modellemede kullanılmamalı**, yalnızca
referans/ileri araştırma amaçlıdır. Indicata'nın 2025+ döneminde kaybolan
`ortalama_satis_hizi_gun` metriğine tamamlayıcı/alternatif bir seri olarak eklenmesi önerilir;
farklı metodoloji nedeniyle `target_indicata_satis_hizi_gun` ile doğrudan birleştirilmemeli,
ayrı bir target adayı olarak değerlendirilmelidir.
