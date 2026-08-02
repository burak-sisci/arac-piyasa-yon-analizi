# PM Raporu — DF-A'nın Tam Kapsamlı (2015'ten Beri Kesintisiz) Alt Kümesi

**Tarih:** 2026-07-31
**Kapsam:** Yalnızca sütun filtreleme. DF-A/DF-B değiştirilmedi — ayrı, yeni
bir dosya üretildi.
**Kaynak kod:** `scripts/veri/genisletme_20_df_a_tam_kapsamli.py`

---

## 1. Ne Yapıldı

Kullanıcı talebiyle, DF-A'dan (`df_a_genis_2015_bugun.csv`, 138 satır × 46
sütun) kaynağı **gerçekten** 2015-01'den sonra başlayan tüm sütunlar
çıkarılarak `df_a_tam_kapsamli_2015_bugun.csv` (+ .xlsx) üretildi. Amaç: iki
veri seti arasında net bir ikilik kurmak — biri BETAM/ENAG/alım gücü içeren
(DF-A, DF-B), diğeri bunları hiç içermeyen, 2015'ten beri kesintisiz olan
(bu yeni dosya).

Kapsam kararı oturum içinde netleştirildi: "kaynağı geç başlayan" (kaynak
boşluğu) ile "kaynağı 2015'ten beri var ama hesaplama/tasarım gereği ilk
birkaç satırı boş olan" ayrıştırıldı — yalnızca ilki çıkarıldı.
`tufe_aylik_degisim`, `tufe_yillik_degisim` (hesaplama gereği) ve
`otv_aciklama` (tasarım gereği) DF-A'da kalmaya devam ediyor.

## 2. Çıkarılan Sütunlar (25 adet, 4 grup)

| Grup | Sütunlar | İlk dolu ay |
|---|---|---|
| Proxy fiyat / BETAM (10) | proxy_dom_gun, proxy_satis_orani_pct, proxy_yayim_ayi, proxy_fiyat_cari_tl, proxy_kaynak, proxy_fiyat_arabamcom_referans_tl, proxy_nominal_aylik_pct, proxy_reel_aylik_pct, proxy_aylik_log_degisim, proxy_reel_aylik_log_degisim | 2024-01 / 2024-02 |
| BETAM'a bağımlı hedef etiket + parametre (6) | proxy_yon_nominal, proxy_yon_reel, proxy_yon_tercile, kullanilan_esik_k, kullanilan_sigma_nominal, kullanilan_sigma_reel | (2015-01'de teknik olarak dolu ama BETAM'sız anlamsız — kullanıcı onayıyla çıkarıldı) |
| ENAG (5) | enag_aylik, enag_yillik, enag_tufe_fark_yillik, enag_kaynak_seviyesi, enag_kaynak_url | 2024-01 |
| 2015-2017 erişim engeli (4) | noter_devir_otomobil_adet, brut_ucret_maas_endeksi_2021_100, alim_gucu_ceyrek, erisim_endeksi | 2018-01 |

## 3. Sonuç Boyutu

- **`df_a_tam_kapsamli_2015_bugun.csv`: 138 satır × 21 sütun** (2015-01 → 2026-06).
- 21 sütunun 16'sı **tam dolu (138/138)**; kalan 5'i (`tufe_aylik_degisim` 1,
  `tufe_yillik_degisim` 12, `odmd_otomobil_adet`/`odmd_hta_adet` 1'er,
  `otv_aciklama` 127) hesaplama/tasarım/tekil-kaynak-gecikmesi gereği eksik —
  kaynak boşluğu DEĞİL, kullanıcıyla mutabık kalınan kural gereği bilinçli
  olarak bırakıldı.

## 4. Karşılaşılan Sorunlar

Yok — filtreleme sorunsuz tamamlandı. Kapsam kararı (hangi sütunların
"kaynak boşluğu" sayılıp çıkarılacağı) baştan belirsizdi, oturum içinde
kullanıcıyla netleştirildi (bkz. Bölüm 1).

## 5. Açık Sorular / Onay Gerekenler

Yok — üç seçim de (kural kapsamı, hedef etiketlerinin çıkarılması, ayrı
dosya stratejisi) kullanıcı tarafından açıkça onaylandı.
