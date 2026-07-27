# PM Raporu — Genişletme 2018 ve Korelasyon Analizi

**Tarih:** 2026-07-24

---

## 1. Ne Yapıldı

Proje sahibinin talebiyle, TÜM mevcut feature'lar 2018-01'e geriye
genişletildi (proxy fiyat hariç — bilinen kısıt, bkz. Bölüm 2). 10 paralel
alt-görev (workflow) + ardından birleştirme/etiketleme/korelasyon adımları
tek oturumda yürütüldü.

| Seri | Hedef başlangıç | Gerçek başlangıç | Kaynak seviyesi |
|---|---|---|---|
| USD/TRY | 2018-01 | **2018-01** | A |
| TÜFE | 2018-01 | **2018-01** | A |
| Taşıt kredisi + politika faizi | 2018-01 | **2018-01** | A |
| ODMD satış adetleri | 2018-01 | **2018-01** | C |
| OSD üretim | 2018-01 | **2018-01** | A |
| Noter devir adedi | 2018-01 | **2018-01** | B |
| Tüketici güveni + oto satın alma ihtimali | 2018-01 | **2018-01** (hatta 2012-01'e kadar) | A |
| ÖTV olayları | 2018-01 | **2018-01** (ilk somut olay 2018-09) | D |
| Alım gücü (brüt ücret-maaş endeksi) | 2018-01 | **2018-01** | B |
| Proxy fiyat (BETAM) | 2018-01 | **2024-01** (genişletilemedi) | C |

**Metodolojik keşif (önemli, tekrar kullanılabilir):** TCMB EVDS3 API'si tek
istekte döndürebileceği satır sayısını **sessizce (hatasız) 1000 ile
sınırlıyor** — aralık bu sınırı aşarsa API en güncel 1000 kaydı döndürüp daha
eski kayıtları sessizce düşürüyor. Bu, USD/TRY (günlük) ve politika faizi
(günlük) serilerinde BAĞIMSIZ olarak iki kez keşfedildi ve doğrudan API
testleriyle kanıtlandı; tarih-parçalama (chunking) ile düzeltildi. **Bu bulgu,
projenin gelecekte EVDS'ten uzun/günlük seri çekeceği her durumda dikkate
alınmalı.**

genisletme_5_birlestir.py ve genisletme_6_hedef_etiket.py 2018-01→2026-06
kapsayacak şekilde güncellendi; genisletme_7_korelasyon_analizi.py (yeni)
korelasyon analizini üretti.

---

## 2. Proxy Fiyat Sonucu

**2018-2023 için BULUNAMADI — kabul edildi, saatlerce uğraşılmadı (talimata
uygun).** BETAM sahibindex Aralık 2023'ten öncesine gitmiyor (bilinen kısıt).
arabam.com için 4 aramalık kısıtlı bir kontrol yapıldı; 2018-2023 dönemine ait
bağımsız bir ortalama ilan fiyatı verisi bulunamadı.

**ŞÜPHELİ BULGU (proaktif bildirim — yeni otonomi kuralına göre):** Kontrol
sırasında arabam.com/AA kaynaklı bir rakam bulundu — Ocak 2025 için "695.831
TL" (kaynak: aa.com.tr, 18.02.2025 yayım). Bu, script'teki BETAM'in **aynı ay**
için verdiği rakamdan (935.136 TL) **belirgin şekilde farklı** — iki kaynak da
"arabam.com ilan verisi" ölçtüğünü iddia ediyor ama örtüşmüyor. Bu turda
çapraz doğrulama YAPILMADI (kapsam dışıydı), yalnızca bildiriliyor. Farkın
nedeni (farklı metodoloji/filtre/segment mi, yoksa biri hatalı mı) netleşmeden
bu rakam hiçbir dosyaya yazılmadı.

Sonuç: proxy fiyat ve ona bağlı hedef etiket sütunları 2018-01→2023-12
aralığında NaN ("eksik"); 2024-01'den itibaren (önceki gibi) dolu.

---

## 3. Yeni Veri Seti Boyutu

- `veri_2018_bugun_birlesik.csv`: **102 satır × 31 sütun** (2018-01→2026-06)
- `veri_2018_bugun_etiketli.csv`: **102 satır × 41 sütun**
- Hedef etiket hâlâ yalnızca **25/101 olası geçişte** üretilebiliyor (proxy
  fiyatın dolu olduğu dönemde) — σ ve sınıf dağılımı **değişmedi** (aynı 25
  geçerli gözlem kümesi): nominal 17 up/7 stable/1 down; reel 1 up/8
  stable/16 down; tercile 8/8/8.
- Ama artık bu 25 gözlemin **her biri, 12+ ay geriye giden bir feature
  geçmişiyle** birlikte duruyor — ileride lag-feature'lar (ör. 12 ay önceki
  kur/faiz/güven) kullanılabilir hale geldi.

---

## 4. Korelasyon Analizi — Özet Bulgular

**AZ-GÖZLEM UYARISI (zorunlu, tekrarlanıyor):** p-değerleri 22-101 gözlemle
hesaplandı. Bu küçük bir örneklem — düşük p-değeri **kanıtlanmış nedensellik
değildir**, yalnızca bu örneklemdeki bir ilişki sinyalidir. Çok sayıda çift
test edildiğinden (çoklu-test problemi) bazı "anlamlı" sonuçlar şans eseri
çıkmış olabilir. Bunlar ekip lideri toplantısı için **başlangıç noktası**,
kesin bulgu değil.

**Metodolojik not:** İki çift (feature'ın hedefin kendisinden türediği
durumlar — ör. `noter_devir_toplam_adet` × `noter_devir_hacim` hedefi)
**tautolojik olduğu için korelasyondan hariç tutuldu** (4 çift). Ayrıca 2 çift
**yapısal/tanımsal bağımlılık** taşıyor, bağımsız bulgu olarak OKUNMAMALI:
`erisim_endeksi`×`noter_devir_hacim` (erisim_endeksi'nin payı noter_devir'in
kendisi) ve `tufe_endeks`×`proxy_reel` (proxy_reel zaten TÜFE'ye bölünerek
tanımlanıyor).

**En yüksek |Pearson r| gösteren çiftler (yapısal bağımlılık taşımayanlar,
gerçek bulgu adayları):**

| Feature | Hedef adayı | Pearson r | p | n | Beklenenle tutarlı mı |
|---|---|---|---|---|---|
| noter_devir_otomobil_adet | proxy_satis_orani | 0,867 | <0,001 | 25 | TUTARLI |
| noter_devir_toplam_adet | proxy_satis_orani | 0,830 | <0,001 | 25 | TUTARLI |
| osd_binek_kamyonet_toplam_adet | noter_devir_hacim | 0,602 | <0,001 | 101 | belirsiz (N2) |
| osd_binek_adet | noter_devir_hacim | 0,600 | <0,001 | 101 | belirsiz (N2) |
| politika_faizi | proxy_nominal | **-0,596** | 0,002 | 25 | TUTARLI |
| osd_kamyonet_adet | noter_devir_hacim | 0,562 | <0,001 | 101 | belirsiz (N2) |
| otomobil_satinalma_ihtimali_endeksi | proxy_nominal | **-0,512** | 0,009 | 25 | **TUTARSIZ** |
| noter_devir_toplam_adet | proxy_nominal | **-0,553** | 0,004 | 25 | **TUTARSIZ** |
| tuketici_guven_endeksi | proxy_satis_orani | **-0,536** | 0,006 | 25 | **TUTARSIZ** |

**Dikkat çekici tutarsızlıklar (beklenene aykırı, özellikle vurgulanıyor):**
"Otomobil satın alma ihtimali" ve "tüketici güveni" arttığında nominal proxy
fiyatının/satış oranının **düşmesi** bekleniyordu ki tersi — talep göstergesi
arttıkça fiyat/satış oranı düşüyor gibi görünüyor (25 gözlemle). Aynı şekilde
noter devir hacmi arttıkça nominal fiyatın düşmesi de beklenmiyordu. Bu üçü
de **ekonomik olarak şaşırtıcı** ve ekip lideri toplantısında özellikle
tartışılmalı — gerçek bir ters-ilişki mi, yoksa az-gözlem/dönem-özel bir
tesadüf mü belirsiz.

Tam matris (92 satır, tüm feature×hedef çiftleri): `data/processed/analiz/korelasyon_matrisi.csv`

---

## 5. Hedef Aday Karşılaştırması

| Hedef adayı | Geçerli gözlem | σ (log-değişim) | up | stable | down | Az-gözlem uyarısı |
|---|---|---|---|---|---|---|
| proxy_nominal | 25 | 0,0126 | 17 | 7 | 1 | EVET |
| proxy_reel | 25 | 0,0152 | 1 | 8 | 16 | EVET |
| **noter_devir_hacim** | **101** | 0,2160 | 26 | 49 | 26 | hayır |
| proxy_dom_gun (ters yorumlu) | 25 | 0,0678 | 11 | 5 | 9 | EVET |
| proxy_satis_orani | 25 | 0,0898 | 5 | 14 | 6 | EVET |
| **odmd_toplam_satis** | **101** | 0,4155 | 35 | 45 | 21 | hayır |

**Dikkat çekici:** `noter_devir_hacim` ve `odmd_toplam_satis` tek adaylar ki
**101 gözlemle** (tüm 2018-2026 penceresi) üretilebiliyor ve ikisi de
**dengeli bir sınıf dağılımı** veriyor (proxy fiyat serilerindeki gibi 1
sınıfın neredeyse yok olması sorunu YOK). Bu, istatistiksel güç açısından
proxy fiyata göre çok daha sağlam ama **fiyat DEĞİL, hacim/hız** ölçüyorlar
— hedef tanımını (K1: "ilan fiyatının yönü") değiştirir. Bu bir öneri değil,
yalnızca bir gözlem — karar Bölüm 7'de PM'e soruluyor.

Tam tablo: `data/processed/analiz/hedef_aday_karsilastirma.csv`

---

## 6. Karşılaşılan Sorunlar (saklanmadı)

- **EVDS3'ün sessiz 1000-satır kesme davranışı** (Bölüm 1) — kritik, tekrar
  kullanılabilir bir bulgu, projenin gelecekteki tüm günlük/uzun-seri
  çekimlerinde hatırlanmalı.
- **arabam.com/BETAM Ocak-2025 rakam uyuşmazlığı** (Bölüm 2) — çözülmedi,
  proaktif bildirildi.
- **TÜİK noter devir portalının press ID'leri sıra dışı** (Ağustos ayı
  düzeltmeleri) — ID tahmini güvenilir değil, "önceki bülten" zincirinin adım
  adım takip edilmesi gerekti (daha yavaş ama güvenilir yöntem, script
  docstring'ine not düşüldü).
- **ÖTV araştırmasında bir WebSearch AI-özet hatası** yakalandı ve düzeltildi
  ("535 sayılı karar" ilk seferde "541" ile karışmıştı; doğrudan kaynak
  fetch'iyle düzeltildi) — WebSearch özetine güvenmeme ilkesinin bir kez daha
  doğrulanması.
- **Bazı çıktı dosya adları hâlâ "2024_bugun" ön-ekini taşıyor** (faiz, osd,
  tuketici_guveni, noter_devir, proxy_fiyat) — içerik 2018'den başlıyor ama
  isim yanıltıcı kalmış; tutarlılık için ileride toplu yeniden adlandırma
  düşünülebilir (işlevsel bir sorun değil, yalnızca isimlendirme).
- **10 paralel alt-görevden 2'si (ODMD, ÖTV) kendi başına commit attı** —
  sıralı olduğu için çakışma olmadı (doğrulandı), ama bu bir sonraki çoklu-
  ajan görevde göz önünde bulundurulmalı.

---

## 7. Açık Sorular / PM Onayı Gerekenler

1. **"Hangi hedefi seçelim?" — bağlayıcı karar, burada net soruluyor:**
   Proxy fiyat (K1'in orijinal tanımı) yalnızca 25 gözlem ve şiddetli sınıf
   dengesizliği veriyor. Noter devir hacmi/ODMD satışı 101 gözlem ve dengeli
   dağılım veriyor ama **fiyat değil hacim** ölçüyor. Bu, hedef tanımını
   değiştirmez (ben değiştirmedim), ama ekip lideri toplantısında
   tartışılması gereken merkezi soru budur.
2. arabam.com/BETAM Ocak-2025 uyuşmazlığı araştırılsın mı (ayrı bir görev)?
3. Beklenene aykırı 3 korelasyon (Bölüm 4) — ekonomik olarak mı yorumlanmalı,
   yoksa az-gözlem artefaktı olarak mı bir kenara bırakılmalı?
4. Dosya adı tutarsızlığı (Bölüm 6, son madde) — toplu yeniden adlandırma
   yapılsın mı, yoksa mevcut haliyle bırakılsın mı?

---

## 8. Veri Örneği

**İlk 3 satır (kritik sütunlar):**
```
referans_ayi  usdtry_aysonu  tufe_endeks  proxy_fiyat_cari_tl  proxy_yon_nominal
    2018-01         3.7829       330.75                   NaN              eksik
    2018-02         3.7867       333.17                   NaN              eksik
    2018-03         3.9985       336.48                   NaN              eksik
```

**Son 3 satır:**
```
referans_ayi  usdtry_aysonu  tufe_endeks  proxy_fiyat_cari_tl  proxy_yon_nominal
    2026-04       45.02555  4028.244072             1168000.0                 up
    2026-05       45.67230  4097.317874             1175000.0             stable
    2026-06       46.59705  4137.743556             1169000.0             stable
```
