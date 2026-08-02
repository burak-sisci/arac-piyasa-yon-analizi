# Veri Sözlüğü — DF-A (geniş) ve DF-B (dar/temiz)

**Tarih:** 2026-07-31
**Kapsam:** `data/processed/dataframes/df_a_genis_2015_bugun.csv` (138 satır,
2015-01 → 2026-06) ve ondan filtrelenen `df_b_dar_betam_bugun.csv` (28 satır,
2024-01 → 2026-06, yalnızca BETAM proxy fiyatının dolu olduğu aylar).
Doluluk sütunları "dolu gözlem / toplam satır" biçimindedir.

| Sütun | Ne olduğu (kısa) | DF-A doluluk | DF-B doluluk | Not |
|---|---|---|---|---|
| `referans_ayi` | Ay anahtarı (YYYY-MM) | 138/138 | 28/28 | — |
| **Döviz kuru** | | | | |
| `usdtry_aysonu` | Ay-sonu USD/TRY | 138/138 | 28/28 | Tam |
| `usdtry_ortalama` | Aylık ortalama USD/TRY | 138/138 | 28/28 | Tam |
| **TÜFE (TÜİK, EVDS)** | | | | |
| `tufe_endeks` | TÜFE seviyesi (zincirlenmiş) | 138/138 | 28/28 | Tam |
| `tufe_aylik_degisim` | Aylık % değişim | 137/138 | 28/28 | DF-A'da yalnızca ilk ay (2015-01) NaN |
| `tufe_yillik_degisim` | Yıllık % değişim | 126/138 | 28/28 | DF-A'da ilk 12 ay (2015) NaN — 12 ay geriye taban gerekir |
| `tufe_yayim_tarihi` | TÜİK yayım tarihi (yaklaşık) | 138/138 | 28/28 | Tam |
| **ENAG (kontrol serisi — bu görevde DF-A'ya eklendi)** | | | | |
| `enag_aylik` | ENAG aylık % enflasyon | 30/138 | 28/28 | Yalnızca 2024-01→2026-06 mevcut kaynağın kendisi |
| `enag_yillik` | ENAG yıllık % enflasyon | 30/138 | 28/28 | Aynı |
| `enag_tufe_fark_yillik` | ENAG−TÜİK yıllık fark (puan) | 30/138 | 28/28 | Aynı |
| `enag_kaynak_seviyesi` | Kaynak güven düzeyi (B/C) | 30/138 | 28/28 | Aynı |
| `enag_kaynak_url` | Kaynak referansı | 30/138 | 28/28 | Aynı |
| **Proxy fiyat (BETAM sahibindex / arabam.com)** | | | | |
| `proxy_fiyat_cari_tl` | Ortalama ilan fiyatı (TL) | 28/138 | 28/28 | DF-B'nin tanımlayıcı sütunu (filtre bu sütuna göre yapıldı) |
| `proxy_dom_gun` | Ortalama ilanda kalma süresi (gün) | 28/138 | 28/28 | Aynı kapsam |
| `proxy_satis_orani_pct` | Satış oranı (%) | 28/138 | 28/28 | Aynı kapsam |
| `proxy_yayim_ayi` | BETAM raporunun kendi başlık ayı | 30/138 | 28/28 | Metadata; DF-B'de 2 ay için "eksik" notu barındırır (bkz. proxy_kaynak) |
| `proxy_kaynak` | Kaynak etiketi (BETAM / eksik notu) | 30/138 | 28/28 | Aynı |
| `proxy_fiyat_arabamcom_referans_tl` | arabam.com referans fiyatı | 2/138 | **0/28** | **DF-B'de YAPI GEREĞİ tamamen boş** — bu sütun yalnızca BETAM'ın boş bıraktığı 2 ayda (2024-05, 2025-02) dolar; ama DF-B tanımı gereği tam o 2 ay dışarıda bırakılıyor (bkz. PM raporu §4) |
| `proxy_nominal_aylik_pct` | Nominal aylık % değişim | 25/138 | 25/28 | DF-B'de 3 satır NaN (seri başı + 2 boşluk sonrası geçiş, bkz. PM raporu) |
| `proxy_reel_aylik_pct` | TÜFE-deflate reel aylık % değişim | 25/138 | 25/28 | Aynı desen |
| `proxy_aylik_log_degisim` | Nominal log-değişim | 25/138 | 25/28 | Aynı desen |
| `proxy_reel_aylik_log_degisim` | Reel log-değişim | 25/138 | 25/28 | Aynı desen |
| **Hedef etiketler** | | | | |
| `proxy_yon_nominal` | up/stable/down (nominal) | 138/138 | 28/28 | "eksik" değeri de dahil tam (kategorik sütun, NaN yok) |
| `proxy_yon_reel` | up/stable/down (reel) | 138/138 | 28/28 | Aynı |
| `proxy_yon_tercile` | up/stable/down (tercile) | 138/138 | 28/28 | Aynı |
| `kullanilan_esik_k` | Sabit k=0,5 | 138/138 | 28/28 | Sabit değer, her satırda tekrar |
| `kullanilan_sigma_nominal` | Kalibre σ (nominal) | 138/138 | 28/28 | Sabit değer |
| `kullanilan_sigma_reel` | Kalibre σ (reel) | 138/138 | 28/28 | Sabit değer |
| **Faiz (TCMB EVDS)** | | | | |
| `tasit_kredisi_faiz` | Taşıt kredisi ağırlıklı ort. faiz | 138/138 | 28/28 | Tam |
| `politika_faizi` | TCMB politika/fonlama faizi | 138/138 | 28/28 | Tam |
| **ODMD (sıfır araç satışı)** | | | | |
| `odmd_toplam_adet` | Toplam satış adedi | 138/138 | 28/28 | Tam |
| `odmd_otomobil_adet` | Yalnızca otomobil | 137/138 | 27/28 | 2026-06 kaynakta yalnızca toplam verilmiş |
| `odmd_hta_adet` | Hafif ticari araç | 137/138 | 27/28 | Aynı |
| **ÖTV olay-dummy** | | | | |
| `otv_event_ay_mi` | 0/1 bayrak | 138/138 | 28/28 | Tam |
| `otv_aciklama` | Olay açıklaması (varsa) | 11/138 | 1/28 | TASARIM GEREĞİ yalnızca olay ayında dolu |
| `otv_ay_farki_en_yakin_olay` | En yakın olaya ay farkı | 138/138 | 28/28 | Tam |
| **OSD (yerli üretim)** | | | | |
| `osd_binek_adet` | Binek otomobil üretimi | 138/138 | 28/28 | Tam |
| `osd_kamyonet_adet` | Kamyonet üretimi | 138/138 | 28/28 | Tam |
| `osd_binek_kamyonet_toplam_adet` | Toplam | 138/138 | 28/28 | Tam |
| **Tüketici güveni (TÜİK, EVDS)** | | | | |
| `tuketici_guven_endeksi` | Genel tüketici güveni | 138/138 | 28/28 | Tam |
| `otomobil_satinalma_ihtimali_endeksi` | Oto satın alma ihtimali | 138/138 | 28/28 | Tam |
| **Noter devir (TÜİK bültenleri)** | | | | |
| `noter_devir_toplam_adet` | Toplam devir | 138/138 | 28/28 | Tam |
| `noter_devir_otomobil_adet` | Yalnızca otomobil | 102/138 | 28/28 | 2015-2017 (36 ay) bilinçli NaN — bkz. genisletme_2a script docstring |
| **Alım gücü / erişim endeksi** | | | | |
| `brut_ucret_maas_endeksi_2021_100` | Brüt ücret-maaş endeksi | 99/138 | 25/28 | 2015-2017 erişim engeli (39 ay) + DF-B içinde 2026-Q2 henüz yayımlanmadı (3 ay) |
| `alim_gucu_ceyrek` | Hangi çeyreğin değeri | 99/138 | 25/28 | Aynı desen |
| `erisim_endeksi` | noter_devir/alım_gücü oranı | 99/138 | 25/28 | Aynı desen (türetilmiş) |

## DF-A'nın "tam kapsamlı" alt kümesi (2026-07-31 eklendi)

`df_a_tam_kapsamli_2015_bugun.csv` (+ .xlsx), DF-A'dan (46 sütun) kaynağı
GERÇEKTEN 2015'ten sonra başlayan 25 sütunun çıkarılmasıyla üretildi (bkz.
`scripts/veri/genisletme_20_df_a_tam_kapsamli.py`). **138 satır × 21 sütun.**
Çıkarılan gruplar: proxy fiyat/BETAM (10 sütun, ilk dolu 2024-01/02), BETAM'a
bağımlı hedef etiket/parametre sütunları (`proxy_yon_*`, `kullanilan_esik_k`,
`kullanilan_sigma_*` — 6 sütun), ENAG (5 sütun, ilk dolu 2024-01), 2015-2017
erişim engeli grubu (`noter_devir_otomobil_adet`, `brut_ucret_maas_endeksi_2021_100`,
`alim_gucu_ceyrek`, `erisim_endeksi` — 4 sütun, ilk dolu 2018-01).

**Kalan 21 sütun** (referans_ayi dahil) 2015-01'den itibaren kaynağı
kesintisiz olan sütunlardır — `tufe_aylik_degisim` (1 ay), `tufe_yillik_degisim`
(12 ay) ve `otv_aciklama` (127 ay) dışında hepsi 138/138 tam doludur; bu üçü
KAYNAK BOŞLUĞU değil, hesaplama gereği (ilk aylarda önceki veri yokluğu) ve
tasarım gereği (yalnızca olay ayında dolu) boşluklardır — bilinçli olarak
DF-A'da bırakıldı, çıkarılmadı.

**Üç dosyanın özeti:**

| Dosya | Satır | Sütun | BETAM/ENAG/alım gücü içerir mi |
|---|---|---|---|
| `df_a_genis_2015_bugun.csv` | 138 | 46 | Evet (kısmi dolu, NaN korunur) |
| `df_a_tam_kapsamli_2015_bugun.csv` | 138 | 21 | **Hayır** — yalnızca 2015'ten beri kesintisiz seriler |
| `df_b_dar_betam_bugun.csv` | 28 | 46 | Evet (tam dolu, BETAM'ın olduğu aylarla sınırlı) |

## Genel not

DF-A'daki hiçbir sütun bu görevde doldurulmadı/enterpolasyon yapılmadı —
yukarıdaki eksiklikler kaynak sınırlamalarının (BETAM, alım gücü erişim
engeli, TÜFE ilk-12-ay hesaplama sınırı, ÖTV'nin tasarım gereği seyrek
olması) doğrudan yansımasıdır. DF-B, yalnızca `proxy_fiyat_cari_tl` dolu
olan aylara filtrelenerek elde edildiği için BETAM kaynaklı sütunlar
(`proxy_fiyat_arabamcom_referans_tl` hariç) ve ENAG sütunları DF-B içinde
tamamen doludur; alım gücü/erişim endeksi grubu ise kendi bağımsız
yapısal gecikmesi (2026-Q2) nedeniyle DF-B içinde de kısmen eksik kalır.
