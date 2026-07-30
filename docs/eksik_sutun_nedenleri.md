# Eksik Sütun Nedenleri — Tam Envanter

**Tarih:** 2026-07-30
**Kapsam:** `data/processed/` altındaki 11 işlenmiş veri dosyası, sütun
bazında tarandı. Bu bir analiz/karar dökümanı değildir — yalnızca "hangi
sütun eksik, neden eksik" sorusuna cevap verir. Doluluk yüzdeleri için
`docs/veri_envanteri_ekip_lideri.md`'ye bakınız (bu rapor onu tekrarlamaz).

## 1) Kısa giriş

11 dosyada toplam **67 (dosya, sütun) çifti** eksik değer taşıyor (191
sütun tarandı, 124'ü tam dolu). En sık görülen neden **(d) TASARIM GEREĞİ**
(19 sütun) — yani sütun yapısı gereği zaten yalnızca belirli durumlarda
dolu olması beklenen sütunlar. İkinci en sık neden **(b) HESAPLAMA GEREĞİ**
(17 sütun) — çoğunlukla "ilk ay için önceki değer yok" deseni.

## 2) Dosya bazında liste

### `data/processed/genisletme/veri_2018_bugun_etiketli.csv` (ana/omurga, 41 sütun, 18'i eksik)

- **`tufe_aylik_degisim`** — 1/102 eksik (2018-01). **(b) HESAPLAMA GEREĞİ**:
  aylık değişim önceki aya ihtiyaç duyar, serinin ilk ayında önceki ay yok.
- **`tufe_yillik_degisim`** — 12/102 eksik (2018-01…12). **(b) HESAPLAMA
  GEREĞİ**: yıllık değişim 12 ay öncesine ihtiyaç duyar, ilk 12 ay için
  bu veri seti dışında.
- **`proxy_dom_gun`** — 74/102 eksik. **(a) KAYNAK BOŞLUĞU**: BETAM verisi
  yalnızca 2024-01'den itibaren var (72 ay pre-2024 boşluğu) + 2024-05 ve
  2025-02'de BETAM hiç rapor yayımlamadı (+2 ay). **Zincirleme etki:**
  yok içinde (bu sütun başka bir omurga sütununu doğrudan etkilemiyor,
  ama ayrı `piyasa_aktivite_endeksi.csv` dosyasını satır sayısı üzerinden
  etkiliyor — bkz. aşağıda).
- **`proxy_satis_orani_pct`** — 74/102 eksik, aynı desen. **(a) KAYNAK
  BOŞLUĞU** (DOM ile birebir aynı kaynak/aylar).
- **`proxy_fiyat_cari_tl`** — 74/102 eksik, aynı desen. **(a) KAYNAK
  BOŞLUĞU**. **Zincirleme etki: EN GENİŞ KAPSAMLI ZİNCİR bu sütundan
  başlıyor** — bkz. Bölüm "En kritik zincir" altında.
- **`proxy_kaynak`** — 72/102 eksik (30 dolu — pre-2024 boşluğu boş
  bırakılmış, ama 2024-05/2025-02 için "eksik (BETAM rapor yayımlamadı)"
  notuyla dolu tutulmuş). **(a) KAYNAK BOŞLUĞU** (metadata alanı, kaynağın
  kendisi yok).
- **`proxy_yayim_ayi`** — 72/102 eksik, aynı desen. **(a) KAYNAK BOŞLUĞU**.
- **`proxy_fiyat_arabamcom_referans_tl`** — 100/102 eksik (yalnız 2024-05
  ve 2025-02 dolu). **(d) TASARIM GEREĞİ**: bu sütun BİLİNÇLİ OLARAK
  yalnızca BETAM'ın boş bıraktığı 2 ayda referans amaçlı doldurulur, diğer
  aylarda kasıtlı boş — omurgaya karıştırılmaması için ayrı tutulmuş.
- **`odmd_otomobil_adet`**, **`odmd_hta_adet`** — 1/102 eksik (2026-06).
  **(e) HENÜZ YAYIMLANMADI**: ODMD bülteninde bu ay için otomobil/HTA
  kırılımı henüz ayrıştırılmamış.
- **`otv_aciklama`** — 92/102 eksik. **(d) TASARIM GEREĞİ**: yalnızca ÖTV
  olayı olan ayda (10 ay) dolu olması beklenir, bu normaldir.
- **`brut_ucret_maas_endeksi_2021_100`**, **`alim_gucu_ceyrek`** — 3/102
  eksik (2026-04, 05, 06). **(e) HENÜZ YAYIMLANMADI**: TÜİK'in ilgili
  çeyreği (2026-Q2) henüz yayımlamaması.
- **`erisim_endeksi`** — 3/102 eksik, aynı 3 ay. **(c) ZİNCİRLEME**:
  formül (`noter_devir_toplam_adet / brut_ucret_maas_endeksi_2021_100`)
  brüt ücret endeksine bağımlı, o eksik olunca bu da eksik kalıyor.
- **`proxy_nominal_aylik_pct`, `proxy_reel_aylik_pct`, `proxy_aylik_log_degisim`,
  `proxy_reel_aylik_log_degisim`** — 77/102 eksik her biri. **(c)
  ZİNCİRLEME + (b) HESAPLAMA GEREĞİ karışımı**: `proxy_fiyat_cari_tl`'nin
  74 eksik ayı bu 4 sütuna doğrudan yansıyor, +3 ekstra ay ise "değişim
  hesaplamak için hem o ay hem BİR ÖNCEKİ ayın da dolu olması" gereğinden
  (2024-05 ve 2025-02 boşlukları, hem kendi geçişlerini hem komşu ay
  geçişlerini NaN yapıyor).

### `data/processed/analiz/tufe_enag_karsilastirma.csv` (8 sütun)

**Eksik sütun yok — tamamı %100 dolu (30/30 ay).**

### `data/processed/analiz/piyasa_aktivite_endeksi.csv` (13 sütun)

**Sütun bazında eksik yok** (13 sütunun hepsi 25/25 satırda dolu) — AMA bu
dosya kasıtlı olarak yalnızca **25 satır** içeriyor (30 olası aydan). Neden:
script, `proxy_fiyat_cari_tl` ve `proxy_dom_gun` gibi girdilerden herhangi
biri eksik olan AYLARI baştan satır olarak dahil etmiyor (`dropna()` ile
düşürülüyor), NaN bırakmıyor. Bu, "sütun eksikliği" değil "satır dışlama"
biçiminde bir eksiklik — kök neden yine `proxy_fiyat_cari_tl`/`proxy_dom_gun`
kaynak boşluğu (**(c) ZİNCİRLEME**, ama sütun değil satır düzeyinde).

### `data/processed/mvp/mvp_2025_etiketli.csv` ve `mvp_2025_birlesik.csv` (MVP, 2025, 12 ay)

- **`proxy_ilan_sayisi`** (her iki dosyada) — 12/12 eksik (TÜM ay boş).
  **(a) KAYNAK BOŞLUĞU**: ne BETAM ne arabam.com bu veriyi mutlak sayı
  olarak hiç yayımlamıyor (yalnızca % değişim bazen verilir) — kalıcı,
  yapısal bir boşluk, ileride de dolmayacak.
- **`proxy_dom`** (birlesik) / **`proxy_dom_gun`** (etiketli) — 11/12 eksik
  (yalnız 2025-02). **(a) KAYNAK BOŞLUĞU**: BETAM o ay rapor yayımlamadı.
- **`proxy_fiyat_cari_tl`** — 11/12 eksik (2025-02). **(a) KAYNAK BOŞLUĞU**,
  aynı sebep.
- **`proxy_satis_orani_pct`** — 11/12 eksik (2025-02). **(a) KAYNAK
  BOŞLUĞU**.
- **`proxy_fiyat_arabamcom_referans_tl`** — 1/12 dolu (11 eksik). **(d)
  TASARIM GEREĞİ**: yalnızca 2025-02 referans amaçlı.
- **`proxy_nominal_aylik_pct`, `proxy_reel_aylik_pct`, `proxy_aylik_log_degisim`,
  `proxy_reel_aylik_log_degisim`** — 9/12 dolu (3 eksik her biri). **(c)
  ZİNCİRLEME + (b) HESAPLAMA GEREĞİ**: seri 2024-12 tabanı içermediği için
  2025-01'in kendi değişimi zaten tanımsız (+1), 2025-02 boşluğu hem
  01→02 hem 02→03 geçişini NaN yapıyor (+2).

### `data/processed/analiz/hedef_aday_karsilastirma.csv` (11 sütun)

- **`ters_yorum_notu`** — 5/6 eksik. **(d) TASARIM GEREĞİ**: yalnızca DOM
  hedef adayı için "ters yorum" notu gerekiyor (DOM düşerse piyasa
  hızlanıyor demektir), diğer 5 hedef adayı için gerekmiyor, kasıtlı boş.

### `data/processed/analiz/korelasyon_matrisi.csv` (11 sütun, 92 satır)

- **`beklenenle_tutarli_mi`** — 28/92 eksik. **(d) TASARIM GEREĞİ**:
  yalnızca `BEKLENEN_YON` sözlüğünde net yön (pozitif/negatif) belirtilen
  feature'lar için doldurulur; "belirsiz" (rejime bağlı çift yönlü,
  ör. ODMD/OSD) olarak işaretli feature'lar için kasıtlı boş bırakılır.
- **`yapisal_bagimlilik_notu`** — 90/92 eksik. **(d) TASARIM GEREĞİ**:
  yalnızca `YAPISAL_BAGIMLILIK_UYARISI` sözlüğünde tanımlı 2 çift
  (erişim_endeksi×noter_devir_hacim, tüfe_endeks×proxy_reel) için
  doldurulur, geri kalan 90 satır için uyarı gerekmediğinden boş.

### `data/processed/analiz/zaman_serileri.csv` (23 sütun, 102 satır, 22'si eksik)

Bu dosyanın TÜM eksiklikleri, omurga tablosunun (yukarıda anlatılan)
eksikliklerinin **doğrudan yansımasıdır** — ayrı bir kök neden yok, bu
yüzden tek tek tekrar edilmiyor, özetleniyor:

- **15 sütun** (çoğu `feature__*__log_degisim`, ör. `usdtry_aysonu`,
  `tufe_endeks`, `politika_faizi`, `odmd_toplam_adet`, `osd_binek_adet`,
  `noter_devir_toplam_adet` vb. + `hedef__noter_devir_hacim`,
  `hedef__odmd_toplam_satis`) — 1/102 eksik (ilk ay). **(b) HESAPLAMA
  GEREĞİ** (log-değişim için önceki ay gerekiyor).
- **`feature__odmd_otomobil_adet__log_degisim`** — 2/102 eksik. **(c)
  ZİNCİRLEME** (ilk ay + kaynaktaki 2026-06 gecikmesi).
- **`feature__brut_ucret_maas_endeksi_2021_100__log_degisim`,
  `feature__erisim_endeksi__log_degisim`** — 4/102 eksik her biri. **(c)
  ZİNCİRLEME** (ilk ay + TÜİK'in henüz yayımlamadığı 3 ay).
- **`hedef__proxy_nominal__log_degisim`, `hedef__proxy_reel__log_degisim`,
  `hedef__proxy_dom_gun__log_degisim`, `hedef__proxy_satis_orani__log_degisim`**
  — 77/102 eksik her biri. **(c) ZİNCİRLEME** (omurgadaki
  `proxy_fiyat_cari_tl`/`proxy_dom_gun` kaynak boşluğunun doğrudan
  yansıması).

### `data/processed/analiz/hedef_kesif_iliski_ccf.csv` (6 sütun, 39 satır)

**Eksik sütun yok** — tasarımda `n<5` durumunda boş bırakma kuralı vardı
ama bu veri setinde hiçbir lag için gerçekleşen `n` 5'in altına düşmedi
(minimum n=19), bu yüzden fiilen hiç boşluk oluşmadı.

### `data/processed/analiz/hedef_kesif_tekli_seri_istatistik.csv` (16 sütun, 10 satır, 13'ü eksik)

Bu dosya "uzun format" bir tablo — her satır farklı bir **ölçüm türü**
(ham seviye tanımlayıcı istatistik / log-değişim tanımlayıcı istatistik /
ADF ham seviye / ADF log-değişim / mevsimsellik ay-dummy R²) temsil ediyor
ve her tür yalnızca KENDİ ilgili sütun setini dolduruyor. Örnek: ADF
satırları `adf_ist`/`p_degeri`/`kritik_5pct` doldurur ama `ortalama`/
`medyan`/`std` gibi tanımlayıcı istatistik sütunlarını boş bırakır (ve
tersi). **13 sütunun tamamı (d) TASARIM GEREĞİ** — bu, tablo yapısının
doğal bir sonucudur, veri kaybı değildir.

### `data/processed/analiz/odmd_oyder_kapsam_ozeti.csv` (7 sütun)

**Eksik sütun yok** — tamamı dolu. (Bu dosyanın kendisi zaten "kaç ay
bulunamadı" sorusunu cevaplayan bir özet tablo — asıl eksiklik orada ayrı
bir konu olarak ele alınıyor, bkz. `pm_rapor_odmd_oyder.md`.)

### `data/raw/` — göze çarpan sistematik boşluklar (kısa not)

- **BETAM (proxy_fiyat kaynağı):** 2024-05 ve 2025-02'de hiç rapor
  yayımlamamış — yukarıda zaten kök neden olarak işlendi.
- **ODMD/OYDER/Indicata "İkinci El Online Sektör Raporu":** 2021-2023
  için 36 aydan yalnızca 10'u bu tur taramasında bulunabildi (ayrıntı:
  `pm_rapor_odmd_oyder.md`) — bu bir "eksik sütun" değil, ayrı bir kaynağın
  henüz veri setine hiç eklenmemiş olması, bu yüzden ana tabloda bir sütun
  karşılığı yok.
- **ENAG:** 30/30 ay dolu (Bölüm 2'de belirtildi), eksik değil ama kaynak
  seviyesi (B/C, resmi site değil) bir güvenilirlik notu — bu ayrı bir konu,
  eksiklik değil.

## En kritik zincir

**`proxy_fiyat_cari_tl` (omurga tablosu)**, projedeki EN GENİŞ KAPSAMLI
zincirin kök nedenidir. Eksikliği şunları tetikliyor:
1. Omurgada doğrudan 4 sütun: `proxy_nominal_aylik_pct`,
   `proxy_reel_aylik_pct`, `proxy_aylik_log_degisim`,
   `proxy_reel_aylik_log_degisim`.
2. `zaman_serileri.csv`'de aynı kökten 2 sütun daha (`hedef__proxy_nominal__
   log_degisim`, `hedef__proxy_reel__log_degisim` — ve DOM/satış oranı
   üzerinden 2 sütun daha).
3. `piyasa_aktivite_endeksi.csv`'nin 30 değil yalnızca 25 satır olması
   (satır düzeyinde dışlama).
4. `korelasyon_matrisi.csv` ve `hedef_aday_karsilastirma.csv`'deki
   proxy-tabanlı hedef adaylarının örneklem büyüklüğünün (n) küçük kalması.

## 3) Özet tablo

| Sütun | Dosya | Eksik/Toplam | Neden | Zincirleme etki |
|---|---|---|---|---|
| tufe_aylik_degisim | veri_2018_bugun_etiketli | 1/102 | b | Hayır |
| tufe_yillik_degisim | veri_2018_bugun_etiketli | 12/102 | b | Hayır |
| proxy_dom_gun | veri_2018_bugun_etiketli | 74/102 | a | Evet → piyasa_aktivite_endeksi.csv satır sayısı |
| proxy_satis_orani_pct | veri_2018_bugun_etiketli | 74/102 | a | Evet → piyasa_aktivite_endeksi.csv satır sayısı |
| proxy_fiyat_cari_tl | veri_2018_bugun_etiketli | 74/102 | a | **Evet — en geniş zincir (yukarı bakınız)** |
| proxy_kaynak | veri_2018_bugun_etiketli | 72/102 | a | Hayır |
| proxy_yayim_ayi | veri_2018_bugun_etiketli | 72/102 | a | Hayır |
| proxy_fiyat_arabamcom_referans_tl | veri_2018_bugun_etiketli | 100/102 | d | Hayır |
| odmd_otomobil_adet | veri_2018_bugun_etiketli | 1/102 | e | Hayır |
| odmd_hta_adet | veri_2018_bugun_etiketli | 1/102 | e | Hayır |
| otv_aciklama | veri_2018_bugun_etiketli | 92/102 | d | Hayır |
| brut_ucret_maas_endeksi_2021_100 | veri_2018_bugun_etiketli | 3/102 | e | Evet → erisim_endeksi |
| alim_gucu_ceyrek | veri_2018_bugun_etiketli | 3/102 | e | Hayır |
| erisim_endeksi | veri_2018_bugun_etiketli | 3/102 | c | Evet → feature__erisim_endeksi__log_degisim |
| proxy_nominal_aylik_pct | veri_2018_bugun_etiketli | 77/102 | c | Evet → hedef__proxy_nominal (zaman_serileri) |
| proxy_reel_aylik_pct | veri_2018_bugun_etiketli | 77/102 | c | Evet → hedef__proxy_reel (zaman_serileri) |
| proxy_aylik_log_degisim | veri_2018_bugun_etiketli | 77/102 | c | Evet |
| proxy_reel_aylik_log_degisim | veri_2018_bugun_etiketli | 77/102 | c | Evet |
| (13 sütun, satır bazında) | piyasa_aktivite_endeksi | 0/25 (satır dışlama: 5/30 ay) | c | Kök neden proxy kaynak boşluğu |
| proxy_ilan_sayisi | mvp_2025_birlesik | 12/12 | a | Hayır |
| proxy_dom | mvp_2025_birlesik | 1/12 | a | Hayır |
| proxy_ilan_sayisi | mvp_2025_etiketli | 12/12 | a | Hayır |
| proxy_dom_gun | mvp_2025_etiketli | 1/12 | a | Hayır |
| proxy_fiyat_cari_tl | mvp_2025_etiketli | 1/12 | a | Evet → 4 türetilmiş sütun |
| proxy_satis_orani_pct | mvp_2025_etiketli | 1/12 | a | Hayır |
| proxy_fiyat_arabamcom_referans_tl | mvp_2025_etiketli | 11/12 | d | Hayır |
| proxy_nominal_aylik_pct | mvp_2025_etiketli | 3/12 | c | Hayır |
| proxy_reel_aylik_pct | mvp_2025_etiketli | 3/12 | c | Hayır |
| proxy_aylik_log_degisim | mvp_2025_etiketli | 3/12 | c | Hayır |
| proxy_reel_aylik_log_degisim | mvp_2025_etiketli | 3/12 | c | Hayır |
| ters_yorum_notu | hedef_aday_karsilastirma | 5/6 | d | Hayır |
| beklenenle_tutarli_mi | korelasyon_matrisi | 28/92 | d | Hayır |
| yapisal_bagimlilik_notu | korelasyon_matrisi | 90/92 | d | Hayır |
| (15 sütun, `feature__*`/`hedef__*` ilk-ay) | zaman_serileri | 1/102 her biri | b | Hayır |
| feature__odmd_otomobil_adet__log_degisim | zaman_serileri | 2/102 | c | Kaynak: odmd_otomobil_adet |
| feature__brut_ucret_maas_endeksi_2021_100__log_degisim | zaman_serileri | 4/102 | c | Kaynak: brut_ucret_maas_endeksi |
| feature__erisim_endeksi__log_degisim | zaman_serileri | 4/102 | c | Kaynak: erisim_endeksi |
| hedef__proxy_nominal__log_degisim | zaman_serileri | 77/102 | c | Kaynak: proxy_fiyat_cari_tl |
| hedef__proxy_reel__log_degisim | zaman_serileri | 77/102 | c | Kaynak: proxy_fiyat_cari_tl |
| hedef__proxy_dom_gun__log_degisim | zaman_serileri | 77/102 | c | Kaynak: proxy_dom_gun |
| hedef__proxy_satis_orani__log_degisim | zaman_serileri | 77/102 | c | Kaynak: proxy_satis_orani_pct |
| (13 sütun, ölçüm-türü bazlı) | hedef_kesif_tekli_seri_istatistik | değişken | d | Hayır |

*(Tabloda okunabilirlik için bazı benzer-desenli sütunlar tek satırda
gruplanmıştır; tam liste Bölüm 2'dedir.)*

## 4) Kategori dağılımı

67 (dosya, sütun) çiftinden:
- **(a) Kaynak boşluğu:** 11
- **(b) Hesaplama gereği:** 17
- **(c) Zincirleme etkisi:** 16
- **(d) Tasarım gereği:** 19
- **(e) Henüz yayımlanmadı:** 4
- **(f) Nedeni net değil:** 0
