# Veri Envanteri — Ekip Lideri Özeti

**Tarih:** 2026-07-28
**Kapsam:** `data/processed/genisletme/veri_2018_bugun_etiketli.csv` (ana/omurga
tablo) + `data/processed/analiz/tufe_enag_karsilastirma.csv` (ENAG kontrol
serisi, henüz ana tabloya eklenmemiş). `piyasa_aktivite_endeksi.csv` bu
envantere dahil edilmemiştir (proje sahibi ayrıca ele alacak).

## 1) Kısa Giriş

Proje şu an **2 işlenmiş veri seti** barındırıyor: ana omurga tablo (**41
sütun**, 2018-01 → 2026-06, 102 aylık satır) ve ondan ayrı tutulan ENAG
E-TÜFE kontrol karşılaştırması (**8 sütun**, 2024-01 → 2026-06, 30 aylık
satır — 5'i omurgayla ortak/bağlam sütunu, 5'i yeni). Genel tarih aralığı
**2018-01 → 2026-06**; genel doluluk düzensiz: kur, faiz, TÜFE endeksi, ODMD,
OSD, tüketici güveni, noter devir gibi ana ekonomik göstergeler **%100
dolu**, ama ilan-fiyatı kaynaklı (proxy fiyat, DOM, satış oranı) ve ondan
türeyen tüm hedef sütunlar yalnızca **2024-01'den itibaren** dolu (%24-28
doluluk) — bu, tek bir kaynağın (BETAM) geç başlamasından kaynaklanan
**yapısal** bir sınırdır, veri kaybı değildir.

---

## 2) Döviz Kuru (USD/TRY)

- **`usdtry_aysonu`**
  - Ne ölçtüğü: Ayın son iş günündeki USD/TRY döviz kuru (TL cinsinden 1 USD).
  - Kaynak: TCMB EVDS3 (`TP.DK.USD.A`/`.S` günlük seri, ay-sonu değeri seçilerek).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0), 0 boş.
  - İstatistik: ortalama 19,16 TL, min 3,78 TL, max 46,60 TL, std sapma 13,99.
  - Veri türü: **GERÇEK** günlük ölçüm; ay-sonu seçimi yerelde yapılan basit bir türetmedir (EVDS'in kendi aylık agregasyonu kullanılmamıştır).
- **`usdtry_ortalama`**
  - Ne ölçtüğü: Ayın tüm iş günü USD/TRY gözlemlerinin ortalaması.
  - Kaynak: TCMB EVDS3, yerelde (pandas) aylık ortalamaya indirgenmiş.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 18,96 TL, min 3,78 TL, max 46,18 TL, std sapma 13,88.
  - Veri türü: **GERÇEK** günlük ölçümden **TÜRETME** (yerel aylık ortalama).

## 3) TÜFE

- **`tufe_endeks`**
  - Ne ölçtüğü: TÜİK Tüketici Fiyat Endeksi seviyesi (zincirlenmiş baz: 2003=100 → 2025=100 geçişi dahil).
  - Kaynak: TCMB EVDS3 (`TP.FG.J0`, orijinali TÜİK TÜFE).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 1385,84, min 330,75, max 4137,74, std sapma 1158,62.
  - Veri türü: **GERÇEK** (resmi endeks), baz-yılı zincirleme metodolojik bir düzeltmedir (uydurma değil).
- **`tufe_aylik_degisim`**
  - Ne ölçtüğü: TÜFE'nin bir önceki aya göre yüzde değişimi.
  - Kaynak: Yerelde `tufe_endeks.pct_change()` ile hesaplanmış (EVDS'in hazır değişim serisi kullanılmamış).
  - Tarih aralığı: 2018-02 – 2026-06.
  - Gözlem: 101/102 dolu (%99,0), 1 boş (ilk ay, önceki değer yok — yapısal).
  - İstatistik: ortalama %2,56, min -%1,44, max %13,58, std sapma 2,33.
  - Veri türü: **TÜRETME** (yerel hesaplama).
- **`tufe_yillik_degisim`**
  - Ne ölçtüğü: TÜFE'nin bir önceki yılın aynı ayına göre yüzde değişimi.
  - Kaynak: Yerelde `tufe_endeks.pct_change(12)` ile hesaplanmış.
  - Tarih aralığı: 2019-01 – 2026-06.
  - Gözlem: 90/102 dolu (%88,2), 12 boş (2018'in ilk 12 ayı — 12 ay öncesi veri seti dışında olduğu için yapısal olarak hesaplanamaz).
  - İstatistik: ortalama %37,82, min %8,55, max %85,51, std sapma 22,66.
  - Veri türü: **TÜRETME** (yerel hesaplama).
- **`tufe_yayim_tarihi`**
  - Ne ölçtüğü: TÜFE'nin o ay için yayımlandığı (yaklaşık) resmi tarih.
  - Kaynak: Yerelde hesaplanmış (referans ayını takip eden ayın takvim-3'ü kuralı).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: metin (tarih), 102 benzersiz değer.
  - Veri türü: **TÜRETME/YAKLAŞIK** (gerçek EVDS vintage tarihi değil, kural-bazlı tahmin).

## 4) ENAG E-TÜFE Kontrol Serisi *(ayrı dosya — henüz ana tabloya eklenmemiş)*

Kaynak dosya: `data/processed/analiz/tufe_enag_karsilastirma.csv` (30 satır,
2024-01 – 2026-06). `referans_ayi`, `tufe_aylik`, `tufe_yillik` sütunları
yukarıdaki TÜFE sütunlarının aynı aralıktaki kopyasıdır (bağlam için); burada
yalnızca YENİ sütunlar detaylandırılıyor.

- **`enag_aylik`**
  - Ne ölçtüğü: ENAG'ın (Enflasyon Araştırma Grubu, bağımsız akademik grup) hesapladığı E-TÜFE'nin bir önceki aya göre yüzde değişimi.
  - Kaynak: ENAG (resmi X hesabı @ENAGRUP ve saygın haber ajansları üzerinden — enagrup.org resmi sitesi erişilemediği için).
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 30/30 dolu (%100,0).
  - İstatistik: ortalama %4,33, min %1,94, max %9,38, std sapma 1,71.
  - Veri türü: **GERÇEK** ölçüm (ENAG'ın kendi hesapladığı rakam), ancak B/C-seviye (dolaylı) kaynaktan toplanmış — bkz. Bilinen Sınırlamalar.
- **`enag_yillik`**
  - Ne ölçtüğü: ENAG E-TÜFE'nin bir önceki yılın aynı ayına göre (12 aylık) yüzde değişimi.
  - Kaynak: ENAG (aynı yukarıdaki gibi).
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 30/30 dolu (%100,0).
  - İstatistik: ortalama %80,40, min %51,49, max %129,11, std sapma 25,11.
  - Veri türü: **GERÇEK** ölçüm, B/C-seviye kaynaktan toplanmış.
- **`fark_yillik`**
  - Ne ölçtüğü: ENAG yıllık enflasyonu ile TÜİK yıllık enflasyonu arasındaki puan farkı (ENAG − TÜİK).
  - Kaynak: Yerelde hesaplanmış (`enag_yillik - tufe_yillik`).
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 30/30 dolu (%100,0).
  - İstatistik: ortalama 35,98 puan, min 19,39 puan, max 64,25 puan, std sapma 11,27.
  - Veri türü: **TÜRETME** (yerel hesaplama).
- **`kaynak_seviyesi`**
  - Ne ölçtüğü: O ayın ENAG rakamının hangi güvenilirlik seviyesinden geldiği (A=resmi site, B=ENAG resmi X hesabı, C=saygın haber ajansı).
  - Kaynak: Metadata, yerelde etiketlenmiş.
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 30/30 dolu (%100,0).
  - İstatistik (kategorik): C = 21 ay, B = 9 ay, A = 0 ay.
  - Veri türü: Metadata (kaynak izlenebilirliği).
- **`kaynak_url`**
  - Ne ölçtüğü: O ayın rakamının alındığı web adresi.
  - Kaynak: Metadata.
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 30/30 dolu (%100,0), 30 benzersiz URL.
  - Veri türü: Metadata (izlenebilirlik).

## 5) Taşıt Kredisi ve Politika Faizi

- **`tasit_kredisi_faiz`**
  - Ne ölçtüğü: Bankaların taşıt kredilerinde uyguladığı ortalama faiz oranı (yıllık %).
  - Kaynak: TCMB EVDS3.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama %25,57, min %9,11, max %44,72, std sapma 11,58.
  - Veri türü: **GERÇEK** ölçüm.
- **`politika_faizi`**
  - Ne ölçtüğü: TCMB'nin belirlediği bir hafta vadeli repo (politika) faiz oranı.
  - Kaynak: TCMB EVDS3.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama %24,74, min %7,55, max %51,36, std sapma 14,42.
  - Veri türü: **GERÇEK** ölçüm.

## 6) ODMD Sıfır Araç Satışları

- **`odmd_toplam_adet`**
  - Ne ölçtüğü: O ay Türkiye'de satılan toplam sıfır (otomobil + hafif ticari araç) adedi.
  - Kaynak: ODMD (Otomotiv Distribütörleri ve Mobilite Derneği) basın bültenleri.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 76.384 adet, min 14.373, max 191.620, std sapma 33.422.
  - Veri türü: **GERÇEK** ölçüm.
- **`odmd_otomobil_adet`**
  - Ne ölçtüğü: O ay satılan yalnızca otomobil (binek) adedi (hafif ticari araç hariç).
  - Kaynak: ODMD basın bültenleri.
  - Tarih aralığı: 2018-01 – 2026-05.
  - Gözlem: 101/102 dolu (%99,0), 1 boş (2026-06 — bültende henüz ayrıştırılmamış/yapısal gecikme).
  - İstatistik: ortalama 59.670, min 10.979, max 146.319, std sapma 26.449.
  - Veri türü: **GERÇEK** ölçüm.
- **`odmd_hta_adet`**
  - Ne ölçtüğü: O ay satılan hafif ticari araç (HTA) adedi.
  - Kaynak: ODMD basın bültenleri.
  - Tarih aralığı: 2018-01 – 2026-05.
  - Gözlem: 101/102 dolu (%99,0), 1 boş (2026-06, aynı yapısal gecikme).
  - İstatistik: ortalama 16.430, min 2.529, max 45.301, std sapma 7.358.
  - Veri türü: **GERÇEK** ölçüm.

## 7) OSD Üretim

- **`osd_binek_adet`**
  - Ne ölçtüğü: O ay Türkiye'de üretilen binek otomobil adedi.
  - Kaynak: TCMB EVDS3 (orijinali OSD — Otomotiv Sanayii Derneği).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 74.071, min 9.661, max 105.687, std sapma 17.401.
  - Veri türü: **GERÇEK** ölçüm.
- **`osd_kamyonet_adet`**
  - Ne ölçtüğü: O ay üretilen kamyonet (hafif ticari) adedi.
  - Kaynak: TCMB EVDS3 (OSD).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 32.975, min 951, max 47.881, std sapma 8.005.
  - Veri türü: **GERÇEK** ölçüm.
- **`osd_binek_kamyonet_toplam_adet`**
  - Ne ölçtüğü: Binek + kamyonet toplam üretim adedi.
  - Kaynak: TCMB EVDS3 (OSD), yerelde toplanmış (`binek + kamyonet`).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 107.047, min 10.612, max 150.877, std sapma 23.146.
  - Veri türü: **GERÇEK** ölçümden **TÜRETME** (basit toplama).

## 8) Tüketici Güven Endeksi

- **`tuketici_guven_endeksi`**
  - Ne ölçtüğü: Tüketicilerin genel ekonomik duruma ilişkin güven düzeyi (100 üstü iyimser, altı kötümser).
  - Kaynak: TCMB EVDS3.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 80,47, min 63,41, max 92,97, std sapma 5,84.
  - Veri türü: **GERÇEK** ölçüm.
- **`otomobil_satinalma_ihtimali_endeksi`**
  - Ne ölçtüğü: Tüketicilerin önümüzdeki 12 ayda otomobil satın alma ihtimaline dair beyan endeksi.
  - Kaynak: TCMB EVDS3.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 15,21, min 7,25, max 27,29, std sapma 5,23.
  - Veri türü: **GERÇEK** ölçüm.

## 9) Noter Devir Adedi

- **`noter_devir_toplam_adet`**
  - Ne ölçtüğü: O ay noterde el değiştiren (devri yapılan) toplam motorlu kara taşıtı sayısı.
  - Kaynak: TÜİK veri portalı ("Motorlu Kara Taşıtları" bültenleri, resmi indirilebilir tablo).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 799.762, min 348.678, max 1.158.490, std sapma 171.857.
  - Veri türü: **GERÇEK** ölçüm.
- **`noter_devir_otomobil_adet`**
  - Ne ölçtüğü: Yukarıdakinin yalnızca otomobil (binek) alt kırılımı.
  - Kaynak: TÜİK veri portalı.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 545.620, min 231.977, max 813.548, std sapma 121.157.
  - Veri türü: **GERÇEK** ölçüm.

## 10) Alım Gücü Proxy'si

- **`brut_ucret_maas_endeksi_2021_100`**
  - Ne ölçtüğü: Sanayi+inşaat+ticaret-hizmet sektörlerinde brüt ücret-maaş endeksi (2021=100, nominal — TÜFE'ye bölünmemiş).
  - Kaynak: TÜİK veri portalı ("İşgücü Girdi Endeksleri").
  - Tarih aralığı: 2018-01 – 2026-03.
  - Gözlem: 99/102 dolu (%97,1), 3 boş (2026-04, 2026-05, 2026-06 — TÜİK'in en güncel çeyreği henüz yayımlamaması, yapısal gecikme).
  - İstatistik: ortalama 373,39, min 55,08, max 1374,31, std sapma 401,79.
  - Veri türü: **GERÇEK** ölçüm ama **çeyreklik** — aylık sütuna, her çeyreğin değeri 3 ay boyunca AYNEN TEKRARLANARAK (forward-fill) yerleştirilmiştir; gerçek ay-ay değişim GÖSTERMEZ, yalnızca çeyrek-çeyrek değişim yansır.
- **`alim_gucu_ceyrek`**
  - Ne ölçtüğü: Yukarıdaki değerin ait olduğu çeyrek etiketi (ör. "2018-Q1").
  - Kaynak: Metadata.
  - Tarih aralığı: 2018-01 – 2026-03.
  - Gözlem: 99/102 dolu (%97,1), 3 boş (aynı gecikme).
  - İstatistik (kategorik): 33 benzersiz çeyrek, her biri 3 ay için tekrarlanmış.
  - Veri türü: Metadata (izlenebilirlik).

## 11) ÖTV Olayları

- **`otv_event_ay_mi`**
  - Ne ölçtüğü: O ayda ÖTV oranı/matrahında resmi bir değişiklik (Cumhurbaşkanı Kararı/Kanun) yürürlüğe girip girmediği (1=evet, 0=hayır).
  - Kaynak: Resmî Gazete kararları (haber taraması ile derlenmiş).
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 0,098 (yani ayların ~%9,8'i bir ÖTV olayı ayı) — 10 olay ayı, 92 olay-dışı ay.
  - Veri türü: **TÜRETME** (gerçek tarihsel olaylardan inşa edilmiş 0/1 gösterge).
- **`otv_aciklama`**
  - Ne ölçtüğü: O ayki ÖTV kararının kısa özeti (karar numarası, Resmî Gazete sayısı, değişikliğin içeriği).
  - Kaynak: Resmî Gazete, haber taraması.
  - Tarih aralığı: 2018-09 – 2025-07 (yalnızca olay ayları).
  - Gözlem: 10/102 dolu (%9,8) — yapısal olarak yalnızca olay aylarında dolu.
  - İstatistik (metin): 10 benzersiz karar özeti (ör. 132, 287, 535, 1013, 2912, 4373, 6417, 7456, 7803, 7555 sayılı kararlar/kanunlar).
  - Veri türü: **GERÇEK** (kaynak metninden özetlenmiş).
- **`otv_ay_farki_en_yakin_olay`**
  - Ne ölçtüğü: O aydan en yakın ÖTV olayına kaç ay uzaklıkta olunduğu (negatif=olay geçmişte, pozitif=olay gelecekte).
  - Kaynak: Yerelde hesaplanmış.
  - Tarih aralığı: 2018-01 – 2026-06.
  - Gözlem: 102/102 dolu (%100,0).
  - İstatistik: ortalama 0,52 ay, min -9 ay, max 11 ay, std sapma 4,58.
  - Veri türü: **TÜRETME** (yerel hesaplama).

## 12) Proxy Fiyat ve Hedef Etiketler

- **`proxy_fiyat_cari_tl`**
  - Ne ölçtüğü: İkinci el otomobil piyasasında ortalama ilan fiyatı (cari/nominal TL, mix/kompozisyon düzeltmesiz).
  - Kaynak: BETAM sahibindex Otomobil Piyasası Görünümü raporu.
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 28/102 dolu (%27,5), 74 boş — **yapısal** (BETAM verisi yalnızca 2024-01'den başlıyor; ayrıca 2024-05 ve 2025-02 BETAM'ın rapor yayımlamadığı 2 ay).
  - İstatistik: ortalama 990.375 TL, min 855.781 TL, max 1.175.000 TL, std sapma 118.505.
  - Veri türü: **GERÇEK** ölçüm (yer tutucu/proxy hedef — mix düzeltmesiz, nihai hedef değil, karar N1).
- **`proxy_dom_gun`**
  - Ne ölçtüğü: İlanların ortalama piyasada kalma süresi (gün, days-on-market).
  - Kaynak: BETAM sahibindex.
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 28/102 dolu (%27,5), aynı yapısal boşluk.
  - İstatistik: ortalama 22,15 gün, min 19,10, max 25,60, std sapma 1,76.
  - Veri türü: **GERÇEK** ölçüm.
- **`proxy_satis_orani_pct`**
  - Ne ölçtüğü: İlanların ne kadarının satışla sonuçlandığına dair BETAM oranı (%).
  - Kaynak: BETAM sahibindex.
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 28/102 dolu (%27,5), aynı yapısal boşluk.
  - İstatistik: ortalama %21,01, min %14,90, max %25,50, std sapma 2,37.
  - Veri türü: **GERÇEK** ölçüm.
- **`proxy_yayim_ayi`**
  - Ne ölçtüğü: Kaynak raporun/yazının yayımlandığı ay (referans ayı DEĞİL — sızıntı önleme için ayrı tutulur).
  - Kaynak: Metadata.
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 30/102 dolu (%29,4).
  - İstatistik (kategorik): 27 benzersiz değer.
  - Veri türü: Metadata.
- **`proxy_kaynak`**
  - Ne ölçtüğü: Hangi kaynaktan geldiği (BETAM veya eksik notu).
  - Kaynak: Metadata.
  - Tarih aralığı: 2024-01 – 2026-06.
  - Gözlem: 30/102 dolu (%29,4).
  - İstatistik (kategorik): "BETAM sahibindex" = 28, "eksik (BETAM rapor yayımlamadı)" = 2.
  - Veri türü: Metadata.
- **`proxy_fiyat_arabamcom_referans_tl`**
  - Ne ölçtüğü: BETAM'ın boş bıraktığı 2025-02 ayı için arabam.com'dan alınan REFERANS (omurgaya karışmayan) fiyat.
  - Kaynak: arabam.com Aylık Fiyat Endeksi.
  - Tarih aralığı: 2024-05, 2025-02 (yalnızca bu 2 ay).
  - Gözlem: 2/102 dolu (%2,0).
  - İstatistik: ortalama 900.940 TL, min 888.689, max 913.190, std sapma 17.325.
  - Veri türü: **GERÇEK** ölçüm (yalnızca karşılaştırma amaçlı).
- **`proxy_nominal_aylik_pct`**
  - Ne ölçtüğü: Nominal proxy fiyatın aylık yüzde değişimi.
  - Kaynak: Yerelde `pct_change()` ile hesaplanmış.
  - Tarih aralığı: 2024-02 – 2026-06.
  - Gözlem: 25/102 dolu (%24,5).
  - İstatistik: ortalama %1,16, min -%1,02, max %3,70, std sapma 1,28.
  - Veri türü: **TÜRETME**.
- **`proxy_reel_aylik_pct`**
  - Ne ölçtüğü: TÜFE'ye bölünerek enflasyondan arındırılmış (reel) proxy fiyatın aylık yüzde değişimi.
  - Kaynak: Yerelde hesaplanmış (`proxy_fiyat_cari_tl / tufe_endeks`, sonra `pct_change()`).
  - Tarih aralığı: 2024-02 – 2026-06.
  - Gözlem: 25/102 dolu (%24,5).
  - İstatistik: ortalama -%1,39, min -%4,85, max %1,10, std sapma 1,49.
  - Veri türü: **TÜRETME**.
- **`proxy_aylik_log_degisim`**
  - Ne ölçtüğü: Nominal proxy fiyatın aylık log-değişimi (hedefin temel büyüklüğü).
  - Kaynak: Yerelde `ln(x_t/x_{t-1})`.
  - Tarih aralığı: 2024-02 – 2026-06.
  - Gözlem: 25/102 dolu (%24,5).
  - İstatistik: ortalama 0,0115, min -0,0103, max 0,0363, std sapma 0,0126.
  - Veri türü: **TÜRETME**.
- **`proxy_reel_aylik_log_degisim`**
  - Ne ölçtüğü: Reel proxy fiyatın aylık log-değişimi.
  - Kaynak: Yerelde hesaplanmış.
  - Tarih aralığı: 2024-02 – 2026-06.
  - Gözlem: 25/102 dolu (%24,5).
  - İstatistik: ortalama -0,0141, min -0,0497, max 0,0109, std sapma 0,0152.
  - Veri türü: **TÜRETME**.
- **`proxy_yon_nominal`**
  - Ne ölçtüğü: Nominal fiyat yönü etiketi (up/stable/down), oynaklık-uyarlamalı bant (k=0,5·sigma) ile.
  - Kaynak: Yerelde hesaplanmış.
  - Tarih aralığı: 2018-01 – 2026-06 (sütun her satırda dolu ama çoğu "eksik" değeriyle).
  - Gözlem: 102/102 teknik olarak dolu; gerçek sınıf dağılımı: eksik=77, up=17, stable=7, down=1.
  - İstatistik (kategorik): yukarıda.
  - Veri türü: **TÜRETME** (etiketleme).
- **`proxy_yon_reel`**
  - Ne ölçtüğü: Reel fiyat yönü etiketi (up/stable/down).
  - Kaynak: Yerelde hesaplanmış.
  - Tarih aralığı: aynı.
  - Gözlem: sınıf dağılımı: eksik=77, down=16, stable=8, up=1.
  - Veri türü: **TÜRETME**.
- **`proxy_yon_tercile`**
  - Ne ölçtüğü: Nominal fiyat yönü, üçe eşit dilime (tercile) bölünerek etiketlenmiş (karşılaştırma amaçlı).
  - Kaynak: Yerelde hesaplanmış (`pd.qcut`).
  - Tarih aralığı: aynı.
  - Gözlem: sınıf dağılımı: eksik=77, down=9, stable=8, up=8 (yapı gereği dengeli).
  - Veri türü: **TÜRETME**.
- **`kullanilan_esik_k`, `kullanilan_sigma_nominal`, `kullanilan_sigma_reel`**
  - Ne ölçtüğü: Etiketleme metodolojisinin parametreleri (sabit eşik katsayısı k=0,5 ve bu koşuda hesaplanan sigma değerleri — tüm satırlarda aynı, seri-geneli tek değer).
  - Kaynak: Metadata/parametre.
  - Tarih aralığı: 2018-01 – 2026-06 (her satırda aynı sabit değer).
  - Gözlem: 102/102 dolu (%100,0).
  - Veri türü: **TÜRETME** (metodoloji parametresi, ölçüm değil).

## 13) Erişim Endeksi

- **`erisim_endeksi`**
  - Ne ölçtüğü: Noter devir hacminin alım gücüne oranı — piyasa erişilebilirliği/talep baskısı göstergesi (FEATURE, K8 — hedef değil).
  - Kaynak: Yerelde hesaplanmış (`noter_devir_toplam_adet / brut_ucret_maas_endeksi_2021_100`).
  - Tarih aralığı: 2018-01 – 2026-03.
  - Gözlem: 99/102 dolu (%97,1), 3 boş (alım gücü verisinin henüz gelmediği 2026-04/05/06 — yapısal, alım gücü sütunundan miras).
  - İstatistik: ortalama 5927,75, min 586,90, max 17916,13, std sapma 4521,25.
  - Veri türü: **TÜRETME** (formül, iki başka sütundan). **Not:** noter devir hacmi ile yapısal/tanımsal bağımlılığı var — bağımsız bir ölçüm değil.

---

## 3) Genel Özet Tablosu

| Kaynak | Sütun sayısı | Tarih aralığı | Ortalama doluluk % | Gerçek mi türetme mi |
|---|---|---|---|---|
| Döviz Kuru (USD/TRY) | 2 | 2018-01 – 2026-06 | %100,0 | Gerçek (+ türetilmiş agregasyon) |
| TÜFE | 4 | 2018-01/02 – 2026-06 | %96,8 | Gerçek (endeks) + Türetme (değişimler) |
| ENAG E-TÜFE (ayrı dosya) | 5 (yeni) | 2024-01 – 2026-06 | %100,0 | Gerçek (B/C-seviye) + Türetme (fark) |
| Taşıt Kredisi ve Politika Faizi | 2 | 2018-01 – 2026-06 | %100,0 | Gerçek |
| ODMD Sıfır Araç Satışları | 3 | 2018-01 – 2026-05/06 | %99,3 | Gerçek |
| OSD Üretim | 3 | 2018-01 – 2026-06 | %100,0 | Gerçek (+ türetilmiş toplam) |
| Tüketici Güven Endeksi | 2 | 2018-01 – 2026-06 | %100,0 | Gerçek |
| Noter Devir Adedi | 2 | 2018-01 – 2026-06 | %100,0 | Gerçek |
| Alım Gücü Proxy'si | 2 | 2018-01 – 2026-03 | %97,1 | Gerçek (çeyreklik, aya tekrarlanmış) |
| ÖTV Olayları | 3 | 2018-01/09 – 2025-07/2026-06 | %69,9 (sütun-ortalaması) | Gerçek (metin) + Türetme (dummy, mesafe) |
| Proxy Fiyat ve Hedef Etiketler | 16 | 2024-01/02 – 2026-06 (proxy kaynaklı kısım) | %52,6 (sütun-ortalaması) | Gerçek (BETAM ham) + Türetme (%, log, etiket) |
| Erişim Endeksi | 1 | 2018-01 – 2026-03 | %97,1 | Türetme (formül) |
| **TOPLAM** | **46 benzersiz sütun** (41 omurga + 5 yeni ENAG) | **2018-01 – 2026-06** (omurga); **2024-01 – 2026-06** (ENAG, proxy) | — | — |

**Not (Proxy Fiyat ve Hedef Etiketler grubu için önemli):** Bu grubun %52,6
ortalaması yanıltıcı olabilir — 10 sütun gerçekten seyrek (%2-30 arası, BETAM
kaynaklı ham veri ve ondan türeyenler), 6 sütun ise (3 yön etiketi + 3
metodoloji parametresi) pandas açısından "%100 dolu" görünür çünkü boş
aylarda NaN yerine `"eksik"` metin değeri veya sabit parametre yazılıdır —
bu 6 sütunun GERÇEK sinyal oranı, altındaki BETAM verisiyle aynıdır (~%25-28).
Ayrıntı için Bölüm 12'deki her sütunun kendi maddesine bakınız.

---

## 4) Bilinen Sınırlamalar

1. **BETAM kaynaklı her şey (proxy fiyat, DOM, satış oranı ve bunlardan türeyen tüm hedef/etiket sütunları) yalnızca 2024-01'den itibaren dolu** — 2018-2023 için bilinen, araştırılmış ve kapatılamamış bir kaynak kısıtıdır (bkz. `pm_rapor_genisletme2018_korelasyon.md`, `pm_rapor_kosullu_genisletme.md`).
2. **BETAM, 2024-05 ve 2025-02 için hiç rapor yayımlamamıştır** — bu 2 ay, proxy fiyat/DOM/satış oranı sütunlarında ek boşluk yaratır (28/30 ay dolu, 30/30 değil).
3. **ENAG resmi sitesi (enagrup.org) 2026-07 itibarıyla Cloudflare 525 hatasıyla erişilemez durumda** — ENAG verisi bu yüzden A-seviye (resmi site) değil, B-seviye (ENAG'ın resmi X hesabı, 9/30 ay) ve C-seviye (saygın haber ajansları, 21/30 ay) kaynaklardan toplanmıştır; 5 ay bağımsız ikinci kaynakla çapraz doğrulanmış (5/5 uyum) — bkz. `pm_rapor_enag_cekme.md`.
4. **Alım gücü verisi TÜİK'te çeyreklik yayımlanır** — aylık sütuna, her çeyreğin değeri 3 ay boyunca aynen tekrarlanarak yerleştirilmiştir; bu sütun (ve ondan türeyen erişim endeksi) gerçek ay-ay varyasyon göstermez.
5. **Alım gücü ve erişim endeksi, 2026-04/05/06 için henüz boş** — TÜİK'in en güncel çeyreği (2026-Q2) henüz yayımlamamış olmasından kaynaklanan yapısal/güncel bir gecikmedir, veri kaybı değildir.
6. **ODMD otomobil/HTA kırılımı 2026-06 için boş** — bültende henüz ayrıştırılmamış, yapısal gecikme.
7. **Noter devir verisi canlı bir API'den değil, elle güncellenen TÜİK bültenlerinden hardcode edilmiştir** — her yeni ay için script'in manuel güncellenmesi gerekir (otomatik değildir); işletim sürdürülebilirliği açısından bilinmesi gereken bir kısıttır.
8. **`proxy_fiyat_cari_tl` mix/kompozisyon düzeltmesizdir (karar N1)** — ham ortalama ilan fiyatıdır, nihai hedef değil, yer tutucu (proxy) hedeftir.
9. **`erisim_endeksi`, noter devir hacmiyle yapısal/tanımsal bir bağımlılık taşır** (payı noter devir hacmi) — bağımsız bir ölçüm olarak yorumlanmamalıdır (bkz. `korelasyon_matrisi.csv` içindeki yapısal bağımlılık uyarıları).
10. **TÜFE yıllık değişim (`tufe_yillik_degisim`), 2018'in ilk 12 ayında hesaplanamaz** — 12 ay öncesi referans veri setinin başlangıcından önce olduğu için yapısal bir boşluktur.
