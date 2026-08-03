# PM Raporu — DataFrame v2 Kurulumu (Kapsama Testi Mantığı)

**Tarih:** 2026-08-03
**Kaynak kod:** `scripts/veri/genisletme_21_dataframe_v2.py`
**Prompt arşivi:** `prompts/21_dataframe_yeniden_kurulum_prompt.md`

---

## 1. Ne Yapıldı

Önceki turda (19 numaralı görev) kurulan DF-A/DF-B, proje sahibinin yeni bir
mantık talebiyle **tamamen değiştirildi**:

- `data/processed/dataframes/df_a_genis_2015_bugun.csv` (+ .xlsx) **silindi**.
- `data/processed/dataframes/df_b_dar_betam_bugun.csv` (+ .xlsx) **silindi**.
- `data/processed/dataframes/veri_sozlugu_df_a_df_b.md` **silindi**.

Yerine, ESKİ mantık ("sütun kısmen doluysa NaN'larla dahil et") yerine YENİ
mantıkla ("sütun hedef pencereyi tarihsel olarak kapsıyor mu — kapsıyorsa
dahil, kapsamıyorsa hiç alma") iki yeni DataFrame kuruldu: **DF-A (kapsama
testli)** ve **DF-B (zengin, 2024+)**. Ayrıca `veri_sozlugu_df_a_df_b_v2.md`
üretildi.

---

## 2. Noter Devri Başlangıç Tarihi (Görev 1)

Omurgada (`veri_2015_bugun_etiketli.csv`) noter devrine ait İKİ sütun var:

- `noter_devir_toplam_adet`: ilk dolu ay **2015-01** (138/138, tamamen dolu).
- `noter_devir_otomobil_adet`: ilk dolu ay **2018-01** (102/138 dolu —
  2015-2017 arası, bülten metninde yalnızca yuvarlanmış yüzde olarak
  verildiği için bilinçli NaN bırakılmıştı, bkz. `genisletme_2a_noter_devir.py`).

**Yorum kararı (PM'e açıkça işaretleniyor):** Prompt "noter_devir_toplam_adet
(veya otomobile özgü varsa noter_devir_otomobil_adet)" diyordu. Projenin
kapsamı (K1: yolcu OTOMOBİLİ piyasası) otomobile özgü olduğundan ve
prompt'un "otomobile özgü varsa onu kullan" ifadesi bunu işaret ettiğinden,
**anchor olarak `noter_devir_otomobil_adet` (2018-01) seçildi**. Bu,
DF-A'nın başlangıcını 2015-01 değil **2018-01** yapıyor. Bu bir yorum
kararıdır — toplam seri (2015-01) seçilseydi DF-A'nın kapsama testi neredeyse
hiçbir şeyi elemeyecekti (zaten tüm 2015-başlangıçlı sütunlar geçerdi), bu
yüzden otomobile-özgü anlamlı/ayırt edici bir pencere sağlıyor. **Eğer proje
sahibi toplam seriyi (2015-01) tercih ederse, script'te tek satırlık bir
değişiklikle (`df_a_baslangic = noter_toplam_baslangic`) kolayca
yeniden üretilebilir.**

---

## 3. DF-A: Boyut, Kapsama Testi Sonucu, Kalan Boşluklar

**`df_a_kapsama_testli_v2.csv` — 102 satır × 25 sütun, 2018-01 → 2026-06.**

**Kapsama testini GEÇEN 24 sütun:**
`usdtry_aysonu`, `usdtry_ortalama`, `tufe_endeks`, `tufe_aylik_degisim`,
`tufe_yillik_degisim`, `tufe_yayim_tarihi`, `tasit_kredisi_faiz`,
`politika_faizi`, `odmd_toplam_adet`, `odmd_otomobil_adet`, `odmd_hta_adet`,
`otv_event_ay_mi`, `otv_aciklama`, `otv_ay_farki_en_yakin_olay`,
`osd_binek_adet`, `osd_kamyonet_adet`, `osd_binek_kamyonet_toplam_adet`,
`tuketici_guven_endeksi`, `otomobil_satinalma_ihtimali_endeksi`,
`noter_devir_toplam_adet`, `noter_devir_otomobil_adet`,
`brut_ucret_maas_endeksi_2021_100`, `alim_gucu_ceyrek`, `erisim_endeksi`.

**Kapsama testini GEÇEMEYEN 21 sütun (gerçek başlangıç tarihiyle):**

| Sütun | Gerçek başlangıç |
|---|---|
| proxy_dom_gun | 2024-01 |
| proxy_satis_orani_pct | 2024-01 |
| proxy_yayim_ayi | 2024-01 |
| proxy_fiyat_cari_tl | 2024-01 |
| proxy_kaynak | 2024-01 |
| proxy_fiyat_arabamcom_referans_tl | 2024-05 |
| proxy_nominal_aylik_pct | 2024-02 |
| proxy_reel_aylik_pct | 2024-02 |
| proxy_aylik_log_degisim | 2024-02 |
| proxy_reel_aylik_log_degisim | 2024-02 |
| proxy_yon_nominal | 2024-01 (proxy_fiyat'a bağımlı, bkz. §5) |
| proxy_yon_reel | 2024-01 (aynı) |
| proxy_yon_tercile | 2024-01 (aynı) |
| kullanilan_esik_k | 2024-01 (aynı) |
| kullanilan_sigma_nominal | 2024-01 (aynı) |
| kullanilan_sigma_reel | 2024-01 (aynı) |
| enag_aylik | 2024-01 |
| enag_yillik | 2024-01 |
| enag_tufe_fark_yillik | 2024-01 |
| enag_kaynak_seviyesi | 2024-01 |
| enag_kaynak_url | 2024-01 |

**DF-A içinde kalan tekil/ara boşluklar (doldurulmadı, yalnızca kayıt):**

| Sütun | Eksik ay sayısı | Neden |
|---|---|---|
| odmd_otomobil_adet, odmd_hta_adet | 1 | 2026-06 kaynak yalnızca toplam vermiş |
| otv_aciklama | 92 | Tasarım gereği — yalnızca olay ayında dolu (10/102 dolu) |
| brut_ucret_maas_endeksi_2021_100, alim_gucu_ceyrek, erisim_endeksi | 3 | 2026-Q2 henüz yayımlanmadı |

---

## 4. DF-B: Boyut, Tüm Sütunlar, Kalan Boşluklar

**`df_b_zengin_2024_bugun_v2.csv` — 30 satır × 46 sütun, 2024-01 → 2026-06.**
Kapsama testi burada uygulanmadı — DF-A'da dışlanan proxy fiyat + ENAG grubu
dahil TÜM 46 sütun mevcut (tam liste `veri_sozlugu_df_a_df_b_v2.md`'de).

**Kalan boşluklar:**

| Sütun | Eksik ay sayısı | Neden |
|---|---|---|
| proxy_dom_gun, proxy_satis_orani_pct, proxy_fiyat_cari_tl | 2 | BETAM 2024-05 ve 2025-02'de rapor yayımlamadı |
| proxy_fiyat_arabamcom_referans_tl | 28 | Yalnızca o 2 ayda referans (tasarım gereği) |
| proxy_nominal_aylik_pct, proxy_reel_aylik_pct, proxy_aylik_log_degisim, proxy_reel_aylik_log_degisim | 5 | Seri başı + 2 boşluğun komşu-ay geçişleri |
| odmd_otomobil_adet, odmd_hta_adet | 1 | 2026-06 tekil gap |
| otv_aciklama | 29 | Tasarım gereği (bu pencerede 1 olay: 2025-07) |
| brut_ucret_maas_endeksi_2021_100, alim_gucu_ceyrek, erisim_endeksi | 3 | 2026-Q2 henüz yayımlanmadı |

Diğer tüm sütunlar (kur, TÜFE, faiz, ODMD toplam, ÖTV bayrağı, OSD,
tüketici güveni, noter devir toplam+otomobil, ENAG grubu) **30/30 tam
dolu**.

---

## 5. Hedef Etiket Sütunlarının Durumu (Görev 4)

**DF-A'da hedef etiket sütunları (`proxy_yon_nominal`, `proxy_yon_reel`,
`proxy_yon_tercile`) YOKTUR** — çünkü proxy fiyat, DF-A'nın kapsama testini
(anchor 2018-01) geçemedi. Bu sütunlar teknik olarak omurgada 2015-01'den
itibaren dolu görünür (NaN yerine "eksik" metni/sabit sayı ile doldukları
için), ama script bunları BİLİNÇLİ OLARAK proxy_fiyat_cari_tl'nin gerçek
başlangıcına (2024-01) göre değerlendirdi — placeholder doluluğa değil.

**Önemli sonuç:** DF-A üzerinde "hedef = fiyat yönü" ile ÇALIŞILAMAZ, yalnızca
DF-B ile çalışılabilir. DF-A muhtemelen noter-devri-hacmi gibi alternatif bir
hedefle yapılacak deneyler için kullanılacaktır (bkz. daha önceki
`pm_rapor_hedef_kesif.md`).

---

## 6. Karşılaşılan Sorunlar

1. **Noter devri anchor kararı bir yorum gerektirdi** (bkz. §2) — prompt
   metni iki olası okumaya açıktı, otomobile-özgü seçildi, gerekçesi ve geri
   alma yolu açıkça belgelendi.
2. **ENAG kaynağı hakkında proaktif bildirim:** Bu script, ENAG verisi için
   hâlâ `data/processed/analiz/tufe_enag_karsilastirma.csv`'yi (2024-01→
   2026-06, 30 ay) kullanıyor. Repo içinde AYRI bir görevle (bu turdan hemen
   önce, commit `03d43b5` ve `d15ab28`) ENAG'ın 2021-01'e kadar KISMİ
   genişletildiği ve `data/raw/enag/enag_aylik_2021_2026.csv` (65 ay) olarak
   birleştirildiği görüldü — AMA bu yeni dosya BİLİNÇLİ OLARAK bu script'e
   entegre EDİLMEDİ, çünkü (a) sütun isimleri farklı (`enag_aylik_degisim`
   vs `enag_aylik`, TÜİK karşılaştırma sütunları yok), (b) 2021 verisi
   `cift_dogrulama=hayır` ile daha düşük kalite olarak işaretlenmiş, (c) bu
   prompt (21) o birleştirme işini hiç referans almıyor. **Bu, PM'in bilmesi
   gereken bir nokta:** DF-A/DF-B'nin ENAG kapsamı isteniyorsa 2021'e kadar
   genişletilebilir, ama bu ayrı bir onay/görev gerektirir (bkz. §8).
3. Bunların dışında teknik bir sorun çıkmadı.

---

## 7. Veri Örneği

**DF-A'dan ilk 2 / son 2 satır (seçili sütunlar):**

```
referans_ayi  usdtry_aysonu  tufe_endeks  noter_devir_toplam_adet  noter_devir_otomobil_adet  tuketici_guven_endeksi
     2018-01         3.7829       330.75                 631823.0                   445255.0               92.383158
     2018-02         3.7867       333.17                 597953.0                   419533.0               92.974206
     2026-05        45.67230     4097.317874             752150.0                   503057.0               85.755424
     2026-06        46.59705     4137.743556             941964.0                   608484.0               87.932449
```

**DF-B'den ilk 2 / son 2 satır (seçili sütunlar):**

```
referans_ayi  proxy_fiyat_cari_tl  enag_aylik  noter_devir_toplam_adet
     2024-01             860443.0        9.38                 782589.0
     2024-02             855781.0        4.32                 847861.0
     2026-05            1175000.0        2.16                 752150.0
     2026-06            1169000.0        1.94                 941964.0
```

---

## 8. Açık Sorular / PM Onayı Gerekenler

1. **Noter devri anchor'ı — toplam mı (2015-01) yoksa otomobil-özgü mü
   (2018-01)?** Mevcut karar otomobil-özgü yönünde (bkz. §2 gerekçe);
   toplam seçilirse DF-A 2015-01'e kadar genişler ama kapsama testi çok
   daha az sütunu eleyecektir (neredeyse tüm 2015-başlangıçlı sütunlar
   zaten geçiyor).
2. **ENAG'ın yeni 2021-2026 birleşik dosyası (65 ay) bu DataFrame'lere
   entegre edilsin mi?** (bkz. §6.2) Entegre edilirse DF-B'nin ENAG kapsamı
   2024-01'den 2021-01'e genişleyebilir — ama sütun isimleri/şema farkı ve
   kalite-etiketleme (cift_dogrulama) nedeniyle ayrı bir uyumlaştırma
   görevi gerektirir, bu turda YAPILMADI.
3. **Hedef etiket sütunlarının DF-A'da hiç bulunmaması kabul edilebilir
   mi?** (bkz. §5) DF-A üzerinde çalışacak biri fiyat yönü hedefine
   erişemeyecek — bu, "DF-A = noter devri/hacim odaklı deneyler,
   DF-B = fiyat yönü odaklı deneyler" ayrımının doğal sonucu, ama açıkça
   onaylanmalı.
