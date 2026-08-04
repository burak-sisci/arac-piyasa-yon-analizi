# Veri Sözlüğü v3 — DF-A (noter penceresi) ve DF-B (ENAG+BETAM, 2024+)

**Tarih:** 2026-08-04
**Kaynak kod:** `scripts/veri/genisletme_29_df_a_df_b_v3.py`
**Kaynak tablo:** `data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv`
(ay-hizalı doldurulmuş, 28 numaralı görevde bağımsız doğrulanmış)

**v2'den farkı:** v2, ay-bazlı bir tablodan (102/30 satır) türetilmişti.
v3, GÜNLÜK satır yapısındaki ay-hizalı doldurulmuş tablodan türetildi —
her ay içindeki tüm günler o ayın değerini taşıyor (forward-fill değil,
takvim-ayı hizalaması, bkz. Görev 26/28 raporları). Satır granülerliği
GÜNLÜK olarak korundu, aya indirgenmedi. Ayrıca v3'te ÖTV sütunları
(otv_referans_ay, otv_aciklama, otv_event_gunu_mu) HİÇBİR ŞEKİLDE dahil
edilmedi (v2'de vardı) — aşırı seyrek/dengesiz oldukları için proje
sahibi tarafından bu sürümde tamamen dışlandı.

---

## DF-A — Noter Devri Penceresi (`df_a_v3_noter_penceresi_2015_bugun.csv`)

**4234 satır × 36 sütun (2026-08-04 güncellemesiyle 35'ten 36'ya çıktı —
`noter_devir_otomobil_adet` manuel eklendi, bkz. aşağıda), 2015-01-01 →
2026-08-04 (bugün).**
Ankor: `noter_devir_toplam_adet` (ilk dolu ayı 2015-01 — `noter_devir_otomobil_adet`'ten
[2018-01] daha erken başladığı için ankor seçildi).

| Sütun | Açıklama | Doluluk | Tip + örnek değerler |
|---|---|---|---|
| `tarih` | Takvim günü (gerçek tarih, 2015-01-01→bugün) | 4234/4234 (%100,0) | tarih — 2015-01-01, 2015-01-02, 2015-01-03 |
| `yil`, `ay`, `gun`, `ceyrek`, `haftanin_gunu`, `yilin_gunu` | Türetilmiş takvim sütunları (`haftanin_gunu`: 0=Pazartesi…6=Pazar) | 4234/4234 (%100,0) | sayısal — yil: 2015, 2016, 2017 |
| `usdtry_alis`, `usdtry_satis`, `usdtry_orta` | USD/TRY döviz kuru (TCMB EVDS, alış/satış/ortalama), gerçek günlük | 2910/4234 (%68,7) | sayısal — 2.3269, 2.3449, 2.3411 |
| `eurtry_alis`, `eurtry_satis`, `eurtry_orta` | EUR/TRY döviz kuru, gerçek günlük | 2912/4234 (%68,8) | sayısal — 2.8272, 2.8258, 2.7931 |
| `altin_referans_ay` | Altın verisinin ait olduğu referans ay (aylık kaynak) | 4169/4234 (%98,5) | metin — "2015-01", "2015-02", "2015-03" |
| `altin_gram_try` | Külçe altın satış fiyatı (TL/gram, TCMB EVDS, aylık) | 4169/4234 (%98,5) | sayısal — 93.79, 97.32, 98.77 |
| `tufe_referans_ay` | TÜFE verisinin ait olduğu referans ay | 4199/4234 (%99,2) | metin — "2015-01", "2015-02", "2015-03" |
| `tufe_endeks` | TÜİK TÜFE endeksi (seviye) | 4199/4234 (%99,2) | sayısal — 250.45, 252.24, 255.23 |
| `tufe_aylik_degisim` | Aylık TÜFE değişimi (%) | 4168/4234 (%98,4) | sayısal — 0.71, 1.19, 1.63 |
| `tufe_yillik_degisim` | Yıllık TÜFE değişimi (%) | 3834/4234 (%90,6) | sayısal — 9.58, 8.78, 7.46 |
| `noter_referans_ay` | Noter devri verisinin ait olduğu referans ay | 4199/4234 (%99,2) | metin — "2015-01", "2015-02", "2015-03" |
| `noter_devir_toplam_adet` | Aylık toplam noter araç devir/satış adedi (ANKOR sütun) | 4199/4234 (%99,2) | sayısal — 462576, 486715, 576623 |
| `odmd_referans_ay` | ODMD verisinin ait olduğu referans ay | 4199/4234 (%99,2) | metin — "2015-01", "2015-02", "2015-03" |
| `odmd_toplam_adet` | ODMD (Otomotiv Distribütörleri Derneği) toplam araç satış adedi | 4199/4234 (%99,2) | sayısal — 34615, 55331, 83302 |
| `odmd_otomobil_adet` | ODMD otomobil satış adedi | 4169/4234 (%98,5) | sayısal — 24498, 40817, 61676 |
| `odmd_hta_adet` | ODMD hafif ticari araç (HTA) satış adedi | 4169/4234 (%98,5) | sayısal — 10117, 14514, 21626 |
| `osd_referans_ay` | OSD verisinin ait olduğu referans ay | 4199/4234 (%99,2) | metin — "2015-01", "2015-02", "2015-03" |
| `osd_binek_adet` | OSD (Otomotiv Sanayii Derneği) binek araç üretim adedi | 4199/4234 (%99,2) | sayısal — 60414, 65238, 72781 |
| `osd_kamyonet_adet` | OSD kamyonet üretim adedi | 4199/4234 (%99,2) | sayısal — 34292, 35062, 38605 |
| `osd_binek_kamyonet_toplam_adet` | OSD binek+kamyonet toplam üretim adedi | 4199/4234 (%99,2) | sayısal — 94706, 100300, 111386 |
| `tuketici_referans_ay` | Tüketici güveni verisinin ait olduğu referans ay | 4230/4234 (%99,9) | metin — "2015-01", "2015-02", "2015-03" |
| `tuketici_guven_endeksi` | TÜİK tüketici güven endeksi | 4230/4234 (%99,9) | sayısal — 89.35, 88.80, 86.49 |
| `otomobil_satinalma_ihtimali_endeksi` | Tüketici anketi: "önümüzdeki 12 ayda otomobil satın alma ihtimali" alt endeksi | 4230/4234 (%99,9) | sayısal — 11.68, 12.16, 10.92 |
| `faiz_referans_ay` | Faiz verisinin ait olduğu referans ay | 4230/4234 (%99,9) | metin — "2015-01", "2015-02", "2015-03" |
| `tasit_kredisi_faiz` | Taşıt kredisi faiz oranı (aylık ortalama) | 4230/4234 (%99,9) | sayısal — 11.01, 10.80, 10.82 |
| `politika_faizi` | TCMB politika faizi (aylık ortalama) | 4230/4234 (%99,9) | sayısal — 8.25, 7.92, 7.80 |
| `noter_devir_otomobil_adet` **[MANUEL EKLENDİ, kapsama testini GEÇEMEDİ]** | Noter devrinin otomobil-özel kırılımı (2018-01'den itibaren tutulmaya başlanmış) | 3103/4234 (%73,3) — **2015-01→2017-12 arası (1096 satır, %25,9) tamamen NaN** | sayısal — (2018-01'den itibaren) 530744, 573508, 580492 |

**[2026-08-04 EK] `noter_devir_otomobil_adet`, proje sahibinin AÇIK
talebiyle DF-A'ya manuel eklendi** — kapsama testini geçemiyor
(2018-01'de başlıyor, ankor 2015-01'den 3 yıl geç) ama bilinçli bir
istisna olarak dahil edildi. Sonuç: pencerenin başında (2015-2017)
büyük ve KESİNTİSİZ bir NaN bloğu var — diğer DF-A sütunlarındaki
dağınık/küçük boşluklardan farklı bir doluluk deseni, korelasyon
analizinde dikkat edilmeli.

**Kapsama testini GEÇEMEYEN, DF-A'da YOK olan sütunlar** (bkz. Bölüm 3,
Görev 6 doğrulaması): `alim_gucu_referans_ay`,
`brut_ucret_maas_endeksi_2021_100`, `enag_referans_ay`,
`enag_aylik_degisim`, `enag_yillik_degisim`, `proxy_referans_ay`,
`proxy_fiyat_cari_tl`, `proxy_dom_gun`, `proxy_satis_orani_pct`,
`proxy_reel_aylik_pct`, `proxy_nominal_yillik_pct`, `proxy_talep_aylik_pct`,
`proxy_nominal_aylik_pct`, `proxy_aylik_log_degisim`,
`proxy_reel_aylik_log_degisim`.

---

## DF-B — ENAG + BETAM Dahil (`df_b_v3_enag_betam_2024_bugun.csv`)

**947 satır × 51 sütun (2026-08-04 güncellemesiyle 45'ten 51'e çıktı —
proxy grubuna 6 yeni sütun eklendi, bkz. aşağıda), 2024-01-01 → 2026-08-04
(bugün).** Kapsama testi
UYGULANMADI — DF-A'da bulunan her şeye ek olarak ENAG ve BETAM (proxy
fiyat) grupları da dahil.

DF-A ile ORTAK olan 28 sütun (tarih, takvim sütunları, kur, altın, TÜFE,
noter devri — hem toplam hem [2026-08-04'ten itibaren] otomobil kırılımı,
ODMD, OSD, tüketici güveni, faiz) — açıklamaları yukarıdaki DF-A
tablosuyla AYNI, yalnızca doluluk oranları farklı (daha kısa/daha güncel
pencere, 2024-2026):

| Sütun | Doluluk (947 satır) | Örnek değerler |
|---|---|---|
| `usdtry_alis/satis/orta` | 644/947 (%68,0) | 29.44, 29.67, 29.74 |
| `eurtry_alis/satis/orta` | 646/947 (%68,2) | 32.57, 32.67, 32.54 |
| `altin_gram_try` | 882/947 (%93,1) | 2069.67, 2085.58, 2394.82 |
| `tufe_endeks` | 912/947 (%96,3) | 1984.02, 2073.88, 2139.47 |
| `noter_devir_toplam_adet` | 912/947 (%96,3) | 782589, 847861, 865144 |
| `noter_devir_otomobil_adet` | 912/947 (%96,3) | 530744, 573508, 580492 |
| `odmd_toplam_adet` | 912/947 (%96,3) | 79701, 105990, 109828 |
| `osd_binek_adet` | 912/947 (%96,3) | 67059, 83955, 87260 |
| `tuketici_guven_endeksi` | 943/947 (%99,6) | 80.42, 79.34, 79.35 |
| `tasit_kredisi_faiz` | 943/947 (%99,6) | 41.68, 40.97, 42.30 |

**[2026-08-04 EK] Proxy fiyat (BETAM) grubu zenginleştirildi — 6 yeni
sütun.** Eskiden yalnızca `proxy_fiyat_cari_tl`, `proxy_dom_gun`,
`proxy_satis_orani_pct` kullanılıyordu. Proje sahibinin talebiyle,
eski (v1/v2) DF-A/DF-B pipeline'ında (`genisletme_6_hedef_etiket.py`)
kullanılan ek göstergeler bu tabloya da taşındı:

| Sütun | Kaynak | Açıklama | Doluluk | Örnek değerler |
|---|---|---|---|---|
| `proxy_reel_aylik_pct` | Ham (BETAM'ın kendi yayımladığı) | BETAM'ın kendi hesapladığı, enflasyondan arındırılmış (reel) aylık fiyat değişimi (%) | 636/947 (%67,2) | -6.0, -5.0, -2.7 |
| `proxy_nominal_yillik_pct` | Ham (BETAM'ın kendi yayımladığı) | BETAM'ın kendi hesapladığı yıllık nominal fiyat değişimi (%) | 853/947 (%90,1) | 50.9, 39.3, 31.8 |
| `proxy_talep_aylik_pct` | Ham (BETAM'ın kendi yayımladığı) | BETAM'ın kendi hesapladığı aylık talep değişimi (%) | 853/947 (%90,1) | 5.6, 4.0, 3.9 |
| `proxy_nominal_aylik_pct` | Hesaplanan (yerel, `proxy_fiyat_cari_tl.pct_change()*100`) | Aylık nominal fiyat değişimi (%), eski pipeline'la AYNI formül | 761/947 (%80,4) | -0.54, 0.38, 1.02 |
| `proxy_aylik_log_degisim` | Hesaplanan (yerel, ln(x_t/x_t-1)) | Aylık log-fiyat değişimi | 761/947 (%80,4) | -0.0054, 0.0038, 0.0102 |
| `proxy_reel_aylik_log_degisim` | Hesaplanan (yerel, TÜFE'ye bölünmüş fiyat üzerinden ln(x_t/x_t-1)) | Aylık reel log-fiyat değişimi | 761/947 (%80,4) | -0.0497, -0.0273, -0.0211 |

Not: `proxy_reel_aylik_pct` için BETAM'ın KENDİ yayımladığı ham değer
kullanıldı (eski pipeline'ın yerel olarak yeniden hesapladığı versiyon
DEĞİL) — ikisi çapraz kontrol edildi, sayısal olarak neredeyse aynı
çıktı, birincil/ham kaynak tercih edildi.

**DF-B'ye ÖZGÜ (DF-A'da olmayan) 23 sütun** (`noter_devir_otomobil_adet`
2026-08-04'ten itibaren DF-A'da da MANUEL olarak var, bkz. DF-A bölümü —
artık ortak sütun, buradan çıkarıldı):
| `enag_referans_ay` | ENAG verisinin ait olduğu referans ay | 912/947 (%96,3) | metin — "2024-01", "2024-02", "2024-03" |
| `enag_aylik_degisim` | ENAG (bağımsız enflasyon araştırma grubu) aylık enflasyon ölçümü (%) | 912/947 (%96,3) | sayısal — 9.38, 4.32, 5.68 |
| `enag_yillik_degisim` | ENAG yıllık enflasyon ölçümü (%) | 912/947 (%96,3) | sayısal — 129.11, 121.98, 124.63 |
| `proxy_referans_ay` | BETAM proxy fiyat verisinin ait olduğu referans ay | 912/947 (%96,3) | metin — "2024-01", "2024-02", "2024-03" |
| `proxy_fiyat_cari_tl` | BETAM ikinci-el araç piyasası ortalama ilan fiyatı (cari TL) | 853/947 (%90,1) | sayısal — 860443, 855781, 859035 |
| `proxy_dom_gun` | BETAM: ilanın piyasada kalma süresi (gün, "days on market") | 853/947 (%90,1) | sayısal — 25.1, 23.3, 22.5 |
| `proxy_satis_orani_pct` | BETAM: ilan başına satış gerçekleşme oranı (%) | 853/947 (%90,1) | sayısal — 17.7, 19.0, 17.1 |
| `alim_gucu_referans_ay` | Alım gücü (brüt ücret) verisinin ait olduğu referans ay | 821/947 (%86,7) | metin — "2024-01", "2024-02", "2024-03" |
| `brut_ucret_maas_endeksi_2021_100` | Brüt ücret/maaş endeksi (2021=100), alım gücü proxy'si | 821/947 (%86,7) | sayısal — 693.11, 741.92, 796.61 |

(Yukarıdaki tabloda 10 sütun listelendi; kalan 8 sütun DF-A ile ortak olan
`_referans_ay` yardımcı sütunlarının DF-B'deki karşılıklarıdır — açıklamaları
DF-A bölümüyle aynıdır, ayrıca listelenmedi.)

**Kapsama testi UYGULANMADI, tüm sütunlar dahil** — bu DataFrame'de
"geçemeyen" sütun kavramı yok.
