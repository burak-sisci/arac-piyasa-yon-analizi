# Veri Sözlüğü v2 — DF-A (kapsama testli) ve DF-B (zengin, 2024+)

**Tarih:** 2026-08-03
**Kaynak kod:** `scripts/veri/genisletme_21_dataframe_v2.py`
**Mantık:** Eski (v1, `genisletme_19`) mantık "sütun kısmen doluysa NaN'larla
dahil et" idi. Bu v2 mantığı FARKLI: "sütun, hedef pencereyi tarihsel olarak
KAPSIYOR mu (kaynağı yeterince erken başlıyor mu)?" — kapsıyorsa dahil
(içindeki tekil boşluklar sorun değil), kapsamıyorsa (kaynağı o pencerede
YAPISAL olarak hiç yok) sütun DF-A'ya hiç alınmaz. DF-B ise ayrı bir
mantıkla, tarih penceresini daraltıp (2024-01→bugün) TÜM sütunları dahil eder.

---

## DF-A — kapsama testli (`df_a_kapsama_testli_v2.csv`)

**102 satır × 25 sütun, 2018-01 → 2026-06.**

Anchor tarih: `noter_devir_otomobil_adet`'in ilk dolu ayı (2018-01) — bkz.
PM raporu §2 için yorum kararının gerekçesi.

| Sütun | DF-A'da mı | Doluluk (102 satır içinde) | Not |
|---|---|---|---|
| `usdtry_aysonu`, `usdtry_ortalama` | ✅ | 102/102 | Tam |
| `tufe_endeks`, `tufe_yayim_tarihi` | ✅ | 102/102 | Tam |
| `tufe_aylik_degisim` | ✅ | 102/102 | Tam (2018-01'den itibaren pencere içinde önceki ay hep mevcut) |
| `tufe_yillik_degisim` | ✅ | 102/102 | Tam (aynı sebep) |
| `tasit_kredisi_faiz`, `politika_faizi` | ✅ | 102/102 | Tam |
| `odmd_toplam_adet` | ✅ | 102/102 | Tam |
| `odmd_otomobil_adet`, `odmd_hta_adet` | ✅ | 101/102 | 2026-06 kaynakta yalnızca toplam verilmiş (bilinen, tekil gap) |
| `otv_event_ay_mi`, `otv_ay_farki_en_yakin_olay` | ✅ | 102/102 | Tam |
| `otv_aciklama` | ✅ | 10/102 | Tasarım gereği — yalnızca olay ayında dolu |
| `osd_binek_adet`, `osd_kamyonet_adet`, `osd_binek_kamyonet_toplam_adet` | ✅ | 102/102 | Tam |
| `tuketici_guven_endeksi`, `otomobil_satinalma_ihtimali_endeksi` | ✅ | 102/102 | Tam |
| `noter_devir_toplam_adet` | ✅ | 102/102 | Tam |
| `noter_devir_otomobil_adet` | ✅ | 102/102 | Tam (anchor sütun) |
| `brut_ucret_maas_endeksi_2021_100`, `alim_gucu_ceyrek`, `erisim_endeksi` | ✅ | 99/102 | 2026-Q2 (3 ay) henüz yayımlanmadı |
| `proxy_dom_gun`, `proxy_satis_orani_pct`, `proxy_yayim_ayi`, `proxy_fiyat_cari_tl`, `proxy_kaynak` | ❌ | — | Kaynak (BETAM) 2024-01'de başlıyor, kapsama testini geçemedi |
| `proxy_fiyat_arabamcom_referans_tl` | ❌ | — | Kaynak 2024-05'te başlıyor |
| `proxy_nominal_aylik_pct`, `proxy_reel_aylik_pct`, `proxy_aylik_log_degisim`, `proxy_reel_aylik_log_degisim` | ❌ | — | Kaynak 2024-02'de başlıyor |
| `proxy_yon_nominal`, `proxy_yon_reel`, `proxy_yon_tercile`, `kullanilan_esik_k`, `kullanilan_sigma_nominal`, `kullanilan_sigma_reel` | ❌ | — | proxy_fiyat_cari_tl'ye tamamen bağımlı, gerçek başlangıcı 2024-01 sayıldı — bkz. Görev 4 |
| `enag_aylik`, `enag_yillik`, `enag_tufe_fark_yillik`, `enag_kaynak_seviyesi`, `enag_kaynak_url` | ❌ | — | Kaynak 2024-01'de başlıyor |

## DF-B — zengin, 2024-01 → bugün (`df_b_zengin_2024_bugun_v2.csv`)

**30 satır × 46 sütun, 2024-01 → 2026-06.** Kapsama testi UYGULANMAZ — DF-A'da
dışlanan proxy/ENAG grubu dahil TÜM 46 sütun burada var. Kalan tekil/ara
boşluklar (doldurulmadı, yalnızca kayıt tutuldu):

| Sütun | Eksik (30 satır içinde) | Neden |
|---|---|---|
| `proxy_dom_gun`, `proxy_satis_orani_pct`, `proxy_fiyat_cari_tl` | 2/30 | BETAM 2024-05 ve 2025-02'de rapor yayımlamadı |
| `proxy_fiyat_arabamcom_referans_tl` | 28/30 | Yalnızca o 2 boşluk ayında referans olarak dolu (tasarım gereği) |
| `proxy_nominal_aylik_pct`, `proxy_reel_aylik_pct`, `proxy_aylik_log_degisim`, `proxy_reel_aylik_log_degisim` | 5/30 | Seri başı (2024-01) + 2 boşluğun komşu-ay geçişleri |
| `odmd_otomobil_adet`, `odmd_hta_adet` | 1/30 | 2026-06 tekil gap |
| `otv_aciklama` | 29/30 | Tasarım gereği (yalnızca olay ayında dolu — bu pencerede 1 olay: 2025-07) |
| `brut_ucret_maas_endeksi_2021_100`, `alim_gucu_ceyrek`, `erisim_endeksi` | 3/30 | 2026-Q2 henüz yayımlanmadı |

Diğer tüm sütunlar (kur, TÜFE, faiz, ODMD toplam, ÖTV bayrağı, OSD, tüketici
güveni, noter devir — hem toplam hem otomobil, ENAG grubu) **30/30 tam dolu**.

---

## Görev 4 — Hedef etiket sütunlarının durumu

**DF-A'da hedef etiket sütunları (`proxy_yon_nominal`, `proxy_yon_reel`,
`proxy_yon_tercile`) YOKTUR** — çünkü bunların gerçek başlangıcı,
kendilerini üreten `proxy_fiyat_cari_tl` sütununun başlangıcı (2024-01) olarak
sayıldı; bu, DF-A'nın anchor tarihinden (2018-01) daha geç olduğu için
kapsama testini geçemediler. **Önemli sonuç: DF-A üzerinde "hedef = fiyat
yönü" ile çalışılamaz — yalnızca DF-B ile çalışılabilir.** DF-A, muhtemelen
noter-devri-hacmi gibi alternatif bir hedefle yapılacak deneyler için
kullanılacaktır (bkz. `pm_rapor_hedef_kesif.md`'deki daha önceki keşif).
