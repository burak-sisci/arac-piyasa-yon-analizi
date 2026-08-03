# PM Raporu — Sütun Temizliği, Metin Düzeltmesi, Proxy Raporu ve Korelasyon Uygunluk Taraması

**Tarih:** 2026-08-03
**Kaynak kod:** `scripts/veri/genisletme_22_sutun_temizlik.py`
**Prompt arşivi:** `prompts/22_sutun_temizlik_ve_korelasyon_kontrol_prompt.md`
**Kapsam:** Yalnızca silme + raporlama. Hedef/model değiştirilmedi, boşluk
doldurulmadı, korelasyon analizinin kendisi çalıştırılmadı.

---

## 1. Ne Yapıldı — Silinen Sütunlar

11 sütun, hangi DataFrame'de bulunduysa oradan silindi:

| Sütun | DF-A | DF-B |
|---|---|---|
| otv_aciklama | ✅ silindi | ✅ silindi |
| proxy_yayim_ayi | bulunamadı (zaten yoktu) | ✅ silindi |
| proxy_kaynak | bulunamadı (zaten yoktu) | ✅ silindi |
| proxy_fiyat_arabamcom_referans_tl | bulunamadı (zaten yoktu) | ✅ silindi |
| proxy_yon_nominal | bulunamadı (zaten yoktu) | ✅ silindi |
| proxy_yon_reel | bulunamadı (zaten yoktu) | ✅ silindi |
| proxy_yon_tercile | bulunamadı (zaten yoktu) | ✅ silindi |
| kullanilan_esik_k | bulunamadı (zaten yoktu) | ✅ silindi |
| enag_tufe_fark_yillik | bulunamadı (zaten yoktu) | ✅ silindi |
| enag_kaynak_seviyesi | bulunamadı (zaten yoktu) | ✅ silindi |
| enag_kaynak_url | bulunamadı (zaten yoktu) | ✅ silindi |

(DF-A bu 11 sütunun 10'unu zaten hiç içermiyordu — 21 numaralı görevdeki
"kapsama testi" onları zaten dışlamıştı, bkz. `pm_rapor_dataframe_v2.md`.
Yalnızca `otv_aciklama` DF-A'da vardı, o da silindi.)

**Sonuç boyutlar:** DF-A **102 satır × 24 sütun** (25→24), DF-B **30 satır
× 35 sütun** (46→35).

---

## 2. "Eksik" Metin Düzeltmesi (Görev 2)

Tüm sütunlar (her iki DataFrame, dtype ayrımı yapılmadan) "eksik" alt-dizesi
içeren hücreler için tarandı. Bulgular:

- **DF-A:** hiç yok (DF-A zaten bu sütunları içermiyordu).
- **DF-B:** 4 sütunda toplam **17 hücre** düzeltildi (silinmeden hemen önce,
  aynı DataFrame üzerinde):
  - `proxy_kaynak`: 2 hücre ("eksik (BETAM rapor yayımlamadı)" → NaN)
  - `proxy_yon_nominal`: 5 hücre ("eksik" → NaN)
  - `proxy_yon_reel`: 5 hücre ("eksik" → NaN)
  - `proxy_yon_tercile`: 5 hücre ("eksik" → NaN)

Bu 4 sütunun tamamı zaten Görev 1'de silindiği için düzeltme nihai
dosyalarda görünmüyor — ama düzeltme, silme işleminden ÖNCE uygulanıp
sayıldı (talimatın istediği sıra) ve **yedek dosyalarda** (silme öncesi
hal) bu ham "eksik" string'leri hâlâ görülebilir durumda duruyor.

---

## 3. Dört Proxy Sütunu Raporu (Görev 3)

**Not:** `proxy_kaynak` Görev 1'de silindiği için raporlanmadı (talimatın
kendisi de bunu istemiyordu). Aşağıdaki 3 sütun yalnızca **DF-B'de**
bulunuyor (DF-A'da hiç yok — kapsama testini geçemediler). Kapsam: DF-B,
30 satır, 2024-01 → 2026-06.

### 3.1 `proxy_dom_gun` (ortalama ilanda kalma süresi, gün)

- **Doluluk:** 28/30 dolu, 2/30 boş (**%93,3 dolu**).
- **Boş aylar:** 2024-05, 2025-02.
- **Neden:** BETAM bu iki ay için hiç rapor yayımlamadı (bilinen, önceden
  belgelenmiş bir kaynak boşluğu — kaynak/kendi arşivinden teyitli).
- **Genel karakter:** ortalama 22,15 gün, min 19,10, max 25,60,
  std sapma 1,76 gün. Ortalama mutlak aylık değişim ~%5,5 — nispeten
  istikrarlı, sıçramalı değil.
- **Boşluk öncesi/sonrası:**
  - 2024-05: önceki (2024-04) = 24,5 gün → sonraki (2024-06) = 23,7 gün
    (komşu değerler birbirine yakın, ~1 günlük fark).
  - 2025-02: önceki (2025-01) = 21,1 gün → sonraki (2025-03) = 21,3 gün
    (neredeyse aynı, çok küçük fark).
- **İlişkili sütunlar:** `proxy_satis_orani_pct` ve `proxy_fiyat_cari_tl`
  ile AYNI 2 ayda (2024-05, 2025-02) boş — üçü de aynı BETAM kaynağından
  geliyor, aynı ay boşluğu hepsine birden yansıyor (kaynak-düzeyinde
  paylaşılan boşluk, bağımsız değil).

### 3.2 `proxy_satis_orani_pct` (ilana çıkan araçların satılma oranı, %)

- **Doluluk:** 28/30 dolu, 2/30 boş (**%93,3 dolu**).
- **Boş aylar:** 2024-05, 2025-02 (aynı ikisi).
- **Neden:** Aynı — BETAM'ın rapor yayımlamadığı aylar.
- **Genel karakter:** ortalama %21,01, min %14,90, max %25,50,
  std sapma 2,37 puan. Ortalama mutlak aylık değişim ~%6,7 — üç proxy
  sütunu içinde en oynak olanı.
- **Boşluk öncesi/sonrası:**
  - 2024-05: önceki (2024-04) = %17,1 → sonraki (2024-06) = %14,9
    (yaklaşık 2,2 puanlık düşüş — ara değer enterpolasyonu bu iki uç
    arasında olurdu, ama trend net değil, tek bir doğrusal enterpolasyon
    gerçek Mayıs değerini yanıltıcı verebilir).
  - 2025-02: önceki (2025-01) = %20,3 → sonraki (2025-03) = %21,3
    (küçük, kademeli bir artış — enterpolasyon burada daha güvenilir
    görünebilir).
- **İlişkili sütunlar:** proxy_dom_gun ve proxy_fiyat_cari_tl ile aynı.

### 3.3 `proxy_fiyat_cari_tl` (ortalama otomobil ilan fiyatı, TL)

- **Doluluk:** 28/30 dolu, 2/30 boş (**%93,3 dolu**).
- **Boş aylar:** 2024-05, 2025-02 (aynı ikisi).
- **Neden:** Aynı — BETAM'ın rapor yayımlamadığı aylar.
- **Genel karakter:** ortalama 990.375 TL, min 855.781 TL,
  max 1.175.000 TL, std sapma 118.505 TL. Ortalama mutlak aylık değişim
  ~%1,3 — üç proxy sütunu içinde EN İSTİKRARLI olanı (TL enflasyonunun
  sürekli yukarı baskısına rağmen ay-ay sıçrama nispeten düşük).
- **Boşluk öncesi/sonrası:**
  - 2024-05: önceki (2024-04) = 867.813 TL → sonraki (2024-06) = 871.156 TL
    (yalnızca ~3.343 TL / %0,4 fark — bu iki nokta arasında doğrusal
    enterpolasyon muhtemelen makul bir yaklaşım olur, seri bu aralıkta
    zaten düz).
  - 2025-02: önceki (2025-01) = 935.136 TL → sonraki (2025-03) = 950.515 TL
    (~15.379 TL / %1,6 fark — yine nispeten düz bir geçiş).
- **İlişkili sütunlar:** `proxy_nominal_aylik_pct`, `proxy_aylik_log_degisim`
  (nominal log-değişim, DF-B'de mevcut) bu sütundan DOĞRUDAN türetiliyor —
  proxy_fiyat_cari_tl boş olduğunda bu iki türetilmiş sütun da otomatik
  NaN kalıyor (zincirleme etki); ayrıca boşluğa komşu ayların (2024-06,
  2025-03) DEĞİŞİM sütunları da NaN kalıyor çünkü önceki ay eksik (toplamda
  bu iki boşluk, değişim sütunlarında 5 satırı etkiliyor: 2024-01 seri
  başı + 2024-06 + 2025-03, artı ilk hesaplanamayan noktalar).

---

## 4. Korelasyon Analizine Uygunluk Taraması (Görev 4)

Tarama, Görev 1'in silme işleminden SONRAKİ (nihai) DF-A ve DF-B üzerinde
yapıldı.

### (a) Sabit / neredeyse değişmeyen sütunlar

| Sütun | DataFrame | Gerekçe |
|---|---|---|
| `kullanilan_sigma_nominal` | DF-B | std=0, tüm satırlarda 0,012608 — sabit parametre değeri |
| `kullanilan_sigma_reel` | DF-B | std=0, tüm satırlarda 0,015208 — sabit parametre değeri |

Not: Bu iki sütun, artık silinmiş olan `proxy_yon_*` etiketlerinin
hesaplanmasında kullanılan sabit katsayılardı — etiketler silindiği için
şu an "yetim" (orijinal bağlamı kalmamış) sabit değerler olarak duruyorlar.

### (b) Metin / kategorik sütunlar

| Sütun | DataFrame | Gerekçe |
|---|---|---|
| `tufe_yayim_tarihi` | DF-A, DF-B | Tarih metni (yaklaşık TÜİK yayım tarihi), sayısal değil |
| `alim_gucu_ceyrek` | DF-A, DF-B | Kategorik etiket ("2024-Q1" gibi), sayısal değil |

### (c) Tarih/zaman damgası sütunları

| Sütun | DataFrame | Not |
|---|---|---|
| `referans_ayi` | DF-A, DF-B | Korelasyona doğrudan sokulmamalı, ama zaman-serisi indeksi/sıralaması için gerekli — **hariç tutulmalı, silinmemeli** |

### (d) Aşırı yüksek oranda boş sütunlar (%70+)

**Bulunamadı.** Görev 1'in silme işlemi, bu kategoriye giren en belirgin
adayları (`otv_aciklama` %90-97 boş, `proxy_fiyat_arabamcom_referans_tl`
%93 boş) zaten kaldırmıştı — kalan hiçbir sütun %70 eşiğine yaklaşmıyor
(en yükseği DF-B'de `proxy_nominal_aylik_pct` grubu, %16,7 boş).

### (e) Birebir kopya veya doğrusal türev şüphesi taşıyan sütun çiftleri

| Çift | DataFrame | r / ilişki türü | Gerekçe |
|---|---|---|---|
| `odmd_toplam_adet` ↔ (`odmd_otomobil_adet` + `odmd_hta_adet`) | DF-A, DF-B | **TAM ARİTMETİK ÖZDEŞLİK** (fark=0,0 her satırda) | toplam, iki bileşenin toplamı olarak TANIMLANMIŞ — üçü birlikte kullanılırsa mükemmel çoklu-doğrusallık |
| `osd_binek_kamyonet_toplam_adet` ↔ (`osd_binek_adet` + `osd_kamyonet_adet`) | DF-A, DF-B | **TAM ARİTMETİK ÖZDEŞLİK** (fark=0,0) | Aynı durum |
| `usdtry_aysonu` ↔ `usdtry_ortalama` | DF-A, DF-B | r=0,9996 (DF-A), r=0,9994 (DF-B) | Aynı kur serisinin iki farklı agregasyonu (ay-sonu vs ay-ortalaması) |
| `tufe_endeks` ↔ `brut_ucret_maas_endeksi_2021_100` | DF-A, DF-B | r≈0,98-0,995 | Bağımsız kaynaklar ama ikisi de zamanla monoton artan endeksler (enflasyon etkisiyle) — yapısal olarak yüksek korelasyon beklenir, gerçek bir "kopya" değil ama çoklu-doğrusallık riski taşıyor |
| `odmd_toplam_adet` ↔ `odmd_otomobil_adet` | DF-A, DF-B | r≈0,997 (DF-A), 0,997 (DF-B) | Otomobil, toplamın büyük çoğunluğunu oluşturduğu için yüksek korelasyon |
| `noter_devir_toplam_adet` ↔ `noter_devir_otomobil_adet` | DF-A, DF-B | r≈0,98 | Aynı sebep |
| `proxy_nominal_aylik_pct` ↔ `proxy_aylik_log_degisim` | DF-B | r=1,0000 | İkisi de aynı proxy_fiyat_cari_tl'den türetilen, matematiksel olarak neredeyse birebir eşdeğer (küçük değişimlerde log-değişim ≈ yüzde değişim) |
| `proxy_reel_aylik_pct` ↔ `proxy_reel_aylik_log_degisim` | DF-B | r=1,0000 | Aynı durum, reel versiyon |
| `erisim_endeksi` ↔ (`noter_devir_toplam_adet`, `brut_ucret_maas_endeksi_2021_100`) | DF-A, DF-B | Doğrusal DEĞİL (oran/bölme) ama DOĞRUDAN türetilmiş | erisim_endeksi = noter_devir_toplam_adet / brut_ucret_maas_endeksi_2021_100 — üçü birlikte kullanılırsa fazlalık bilgi taşınır |

### (f) Aşırı değer (outlier) şüphesi

| Sütun | DataFrame | Bulgu |
|---|---|---|
| `tufe_aylik_degisim` | DF-A | 2021-12'de |z|=4,74 (değer %13,58 — bu ay gerçek bir yüksek enflasyon şoku, veri hatası değil, ama tek bir ay korelasyonu domine edebilir) |
| `odmd_hta_adet` | DF-A, DF-B | 2025-12'de |z|=3,6-3,9 (değer ~45.300 — mevsimsel yıl-sonu sıçraması olabilir, doğrulama gerektirir) |
| `osd_binek_adet`, `osd_kamyonet_adet`, `osd_binek_kamyonet_toplam_adet` | DF-A | 2020-04'te |z|=3,7-4,2 (COVID-19 üretim durması ayı — bilinen, açıklanabilir bir dış şok, veri hatası değil) |
| `otv_event_ay_mi` | DF-B | 2025-07'de |z|=5,29 (bu, 0/1 İKİLİ bir bayrak sütunu — z-score yöntemi ikili değişkenlerde yanıltıcıdır, "aykırı değer" değil sadece azınlık sınıfın doğal sonucu, dikkatli yorumlanmalı) |

---

## 5. Karşılaşılan Sorunlar

1. **Script'in ilk çalıştırmasında bir tip-kontrolü hatası** oluştu (Görev 4
   taramasında tarih/metin sütunları için `std()` çağrılmaya çalışılması) —
   Görev 1/2/3 zaten başarıyla tamamlanıp kaydedilmişti, yalnızca Görev 4'ün
   kod mantığı düzeltilip DataFrame'ler yedekten geri yüklenerek script
   baştan (temiz durumdan) yeniden çalıştırıldı. Nihai sonuç etkilenmedi.
2. Bunun dışında teknik bir sorun çıkmadı.

---

## 6. Yedek Dosyaların Konumu

Silme/düzeltme işleminden ÖNCEKİ tam hal, şurada saklanıyor:
- `data/processed/dataframes/yedek/df_a_kapsama_testli_v2_20260803_v22.csv`
- `data/processed/dataframes/yedek/df_b_zengin_2024_bugun_v2_20260803_v22.csv`

(Bu yedekler, DF-B'deki ham "eksik" string değerlerini ve silinen 11
sütunun tamamını — DF-A'da yalnızca `otv_aciklama` — hâlâ içeriyor; geri
dönüş gerekirse doğrudan kullanılabilir.)

---

## 7. Açık Sorular / PM Onayı Gerekenler

1. ~~`kullanilan_sigma_nominal`/`kullanilan_sigma_reel` (DF-B'de "yetim"
   sabit sütunlar, bkz. §4a) silinsin mi?~~ **ÇÖZÜLDÜ (2026-08-03,
   takip görevi):** Proje sahibi onayıyla ikisi de DF-B'den silindi.
   DF-A'da zaten yoktu. Silmeden önce DF-B'nin yedeği
   `data/processed/dataframes/yedek/df_b_zengin_2024_bugun_v2_20260803_v23_oncesi.csv`
   olarak alındı. DF-B: 35 → **33 sütun** (satır sayısı değişmedi, 30).
2. ~~Tam aritmetik özdeşlik taşıyan üçlüler (`odmd_toplam_adet` =
   `odmd_otomobil_adet` + `odmd_hta_adet`; `osd_binek_kamyonet_toplam_adet`
   = `osd_binek_adet` + `osd_kamyonet_adet`) korelasyon analizine
   HANGİSİYLE girsin?~~ **ÇÖZÜLDÜ (2026-08-03, takip görevi):** Proje
   sahibi onayıyla K1'in kapsamıyla (yolcu otomobili piyasası) tutarlı
   olan sütunlar (`odmd_otomobil_adet`, `osd_binek_adet`) tutuldu; diğer
   dört sütun (`odmd_toplam_adet`, `odmd_hta_adet`,
   `osd_binek_kamyonet_toplam_adet`, `osd_kamyonet_adet`) her iki
   DataFrame'den de silindi. Yedekler
   `df_a_kapsama_testli_v2_20260803_v24_oncesi.csv` ve
   `df_b_zengin_2024_bugun_v2_20260803_v24_oncesi.csv`.
3. ~~`erisim_endeksi` ile onu oluşturan iki bileşen birlikte mi
   kullanılacak?~~ **ÇÖZÜLDÜ (2026-08-03, takip görevi):** Proje sahibi
   `erisim_endeksi`'nin her iki DataFrame'den de silinmesine karar verdi
   — `noter_devir_toplam_adet` ve `brut_ucret_maas_endeksi_2021_100` ham
   bileşenler olarak kaldı. Yedekler
   `df_a_kapsama_testli_v2_20260803_v25_oncesi.csv` ve
   `df_b_zengin_2024_bugun_v2_20260803_v25_oncesi.csv`.

   **Nihai boyutlar (bu üç takip görevinden sonra):** DF-A **102 satır ×
   19 sütun**, DF-B **30 satır × 28 sütun**.
4. **proxy_dom_gun ve proxy_satis_orani_pct'nin 2 boşluk ayı için
   enterpolasyon yapılabilir mi?** (§3.1-3.2) Fiyat sütunu (proxy_fiyat_cari_tl)
   için komşu değerler çok yakın (%0,4-1,6 fark) ve enterpolasyon makul
   görünüyor; ama proxy_satis_orani_pct'nin 2024-05 boşluğunda komşu
   değerler arasında daha belirgin bir fark var (%17,1→%14,9) — bu, karar
   proje sahibine bırakılan bir nokta.
