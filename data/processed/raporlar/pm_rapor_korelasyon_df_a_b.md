# PM Raporu — DF-A / DF-B Korelasyon Analizi (Genel + Noter Devri Odaklı)

**Tarih:** 2026-08-03
**Kaynak kod:** `scripts/veri/genisletme_23_korelasyon_df_a_b.py`,
`scripts/veri/genisletme_24_noter_devir_korelasyon.py`
**Kapsam:** Yalnızca korelasyon hesaplama + görselleştirme. Hedef/model
değiştirilmedi, herhangi bir veri temizliği/doldurma bu turda YAPILMADI.

---

## 1. Ne Yapıldı

İki ayrı korelasyon analizi çalıştırıldı, ikisi de **güncel** (en son sütun
temizliği turlarından — `brut_ucret_maas_endeksi_2021_100`, `otv_event_ay_mi`,
`otv_ay_farki_en_yakin_olay` silindikten — SONRAKİ) DF-A ve DF-B üzerinde:

1. **Genel korelasyon matrisi** (`genisletme_23`): Her iki DataFrame'in TÜM
   sayısal sütunları birbirine karşı (Pearson) korele edildi, ısı haritası
   (heatmap) görseli üretildi.
2. **Noter devri odaklı korelasyon** (`genisletme_24`): `noter_devir_toplam_adet`
   ve `noter_devir_otomobil_adet`'in, diğer TÜM özelliklerle tek tek
   korelasyonu hesaplandı, yatay çubuk grafiği (bar chart) görseli üretildi.

**ÖNEMLİ NOT (zamanlama):** Bu iki analiz İLK KEZ, henüz `brut_ucret_maas_endeksi_2021_100`
ve iki ÖTV sütunu (`otv_event_ay_mi`, `otv_ay_farki_en_yakin_olay`)
silinmeden ÖNCE çalıştırılmıştı (kullanıcı "PM raporunu şimdi yazma"
demişti). Bu rapor talep edilince, aradan geçen sütun silme turları fark
edildi ve rapor yazılmadan ÖNCE her iki script GÜNCEL (post-silme) DF-A/DF-B
üzerinde YENİDEN çalıştırıldı — aşağıdaki tüm sayılar güncel veriye aittir,
eski/stale değildir.

---

## 2. Sayısal Özet

**DF-A:** 102 satır × 16 sütun (3'ü hariç tutuldu: `referans_ayi` [tarih],
`tufe_yayim_tarihi` [metin], `alim_gucu_ceyrek` [kategorik, artık yetim]) →
**13 sayısal sütun** korelasyona katıldı:
`usdtry_aysonu`, `usdtry_ortalama`, `tufe_endeks`, `tufe_aylik_degisim`,
`tufe_yillik_degisim`, `tasit_kredisi_faiz`, `politika_faizi`,
`odmd_otomobil_adet`, `osd_binek_adet`, `tuketici_guven_endeksi`,
`otomobil_satinalma_ihtimali_endeksi`, `noter_devir_toplam_adet`,
`noter_devir_otomobil_adet`.

**DF-B:** 30 satır × 25 sütun (aynı 3'ü hariç) → **22 sayısal sütun**:
DF-A'nın 13 sütunu + `proxy_dom_gun`, `proxy_satis_orani_pct`,
`proxy_fiyat_cari_tl`, `proxy_nominal_aylik_pct`, `proxy_reel_aylik_pct`,
`proxy_aylik_log_degisim`, `proxy_reel_aylik_log_degisim`, `enag_aylik`,
`enag_yillik`.

### 2.1 Genel korelasyon matrisi — |r| > 0,8 olan çiftler

**DF-A (12 çift):**

| Çift | r |
|---|---|
| usdtry_aysonu ↔ usdtry_ortalama | 0,9996 |
| usdtry_ortalama ↔ tufe_endeks | 0,9839 |
| noter_devir_toplam_adet ↔ noter_devir_otomobil_adet | 0,9829 |
| usdtry_aysonu ↔ tufe_endeks | 0,9827 |
| tasit_kredisi_faiz ↔ politika_faizi | 0,9253 |
| tufe_endeks ↔ otomobil_satinalma_ihtimali_endeksi | 0,9196 |
| usdtry_aysonu ↔ otomobil_satinalma_ihtimali_endeksi | 0,8801 |
| usdtry_ortalama ↔ otomobil_satinalma_ihtimali_endeksi | 0,8795 |
| usdtry_ortalama ↔ tasit_kredisi_faiz | 0,8743 |
| usdtry_aysonu ↔ tasit_kredisi_faiz | 0,8718 |
| tufe_endeks ↔ tasit_kredisi_faiz | 0,8390 |
| tufe_endeks ↔ politika_faizi | 0,8019 |

**DF-B (34 çift, en dikkat çekici olanlar):**

| Çift | r |
|---|---|
| proxy_nominal_aylik_pct ↔ proxy_aylik_log_degisim | 1,0000 |
| proxy_reel_aylik_pct ↔ proxy_reel_aylik_log_degisim | 1,0000 |
| usdtry_aysonu ↔ usdtry_ortalama | 0,9994 |
| usdtry_ortalama ↔ tufe_endeks | 0,9930 |
| noter_devir_toplam_adet ↔ noter_devir_otomobil_adet | 0,9815 |
| usdtry_ortalama ↔ proxy_fiyat_cari_tl | 0,9718 |
| tufe_yillik_degisim ↔ enag_yillik | 0,9709 |
| tufe_endeks ↔ enag_yillik | -0,9410 |
| tasit_kredisi_faiz ↔ politika_faizi | 0,8756 |
| proxy_satis_orani_pct ↔ noter_devir_otomobil_adet | 0,8235 |

(Tam liste — 34 çift — `korelasyon_matrisi_df_b.csv` dosyasında.)

### 2.2 Noter devri odaklı korelasyon — en yüksek |r| değerleri

**DF-A (102 satır):**

| Diğer özellik | noter_devir_toplam_adet | noter_devir_otomobil_adet |
|---|---|---|
| odmd_otomobil_adet | **0,5822** | **0,4970** |
| usdtry_aysonu | 0,4862 | 0,3766 |
| usdtry_ortalama | 0,4825 | 0,3729 |
| tufe_endeks | 0,4537 | 0,3617 |
| otomobil_satinalma_ihtimali_endeksi | 0,4452 | 0,3750 |
| tasit_kredisi_faiz | 0,2845 | 0,1690 |
| politika_faizi | 0,2377 | 0,1604 |
| osd_binek_adet | 0,2171 | 0,2412 |
| tuketici_guven_endeksi | -0,0678 | -0,0229 |

**DF-B (30 satır, BETAM'lı pencere):**

| Diğer özellik | noter_devir_toplam_adet | noter_devir_otomobil_adet |
|---|---|---|
| proxy_satis_orani_pct | **0,7693** | **0,8235** |
| odmd_otomobil_adet | 0,5304 | 0,5653 |
| proxy_dom_gun | -0,4052 | -0,4817 |
| proxy_reel_aylik_pct | 0,3584 | 0,4050 |
| tufe_yillik_degisim | -0,3072 | -0,3934 |
| enag_yillik | -0,2944 | -0,3599 |
| osd_binek_adet | 0,2545 | 0,2509 |
| proxy_fiyat_cari_tl | 0,0910 | 0,1377 |
| politika_faizi | -0,0013 | -0,0917 |

**Hiçbir çift 0,9 eşiğini geçmedi** (bu, kullanıcının önceki sorusunda da
teyit edilmişti) — en güçlü ilişki DF-B'de `noter_devir_otomobil_adet` ↔
`proxy_satis_orani_pct` (r=0,8235).

---

## 3. Karşılaşılan Sorunlar

1. **Zamanlama/tazelik sorunu (bkz. Bölüm 1):** Analiz ilk çalıştırıldığında
   DF-A/DF-B'de artık silinmiş 3 sütun (`brut_ucret_maas_endeksi_2021_100`,
   `otv_event_ay_mi`, `otv_ay_farki_en_yakin_olay`) hâlâ mevcuttu. Rapor
   talep edildiğinde bu fark edildi, her iki script rapor yazılmadan önce
   güncel veriyle YENİDEN çalıştırıldı — bu raporda ve ilişkili CSV/PNG
   dosyalarında artık STALE veri yok.
2. Bunun dışında teknik bir sorun çıkmadı.

---

## 4. Veri Örneği

**`korelasyon_matrisi_df_a.csv`'den bir kesit** (ilk 3 sütun × ilk 3 satır):

```
                usdtry_aysonu  usdtry_ortalama  tufe_endeks
usdtry_aysonu          1.0000           0.9996       0.9827
usdtry_ortalama        0.9996           1.0000       0.9839
tufe_endeks            0.9827           0.9839       1.0000
```

**`noter_devir_korelasyon_df_b.csv`'den bir kesit:**

```
noter_sutunu               diger_ozellik           pearson_r   n
noter_devir_toplam_adet     proxy_satis_orani_pct       0.7693  28
noter_devir_otomobil_adet   proxy_satis_orani_pct       0.8235  28
```

---

## 5. Varsayımlar ve Kararlar

| Karar | Not |
|---|---|
| Korelasyon HAM SEVİYE (level) değerleri üzerinden hesaplandı, log-değişim/stationarize edilmiş seriler üzerinden DEĞİL | Kendi kararım — kullanıcı bir metodoloji belirtmedi, en basit/literal yorum uygulandı. **RİSK:** trend taşıyan seviye serileri (kur, TÜFE, alım gücü grubu gibi) arasındaki yüksek korelasyonlar (ör. DF-A'da usdtry↔tufe_endeks r=0,98) gerçek bir ilişkiden çok ORTAK ZAMAN TRENDİNDEN kaynaklanıyor olabilir — bu SAHTE (spurious) korelasyon riski taşır, ekonomik olarak doğrudan yorumlanmamalı. |
| `referans_ayi`, `tufe_yayim_tarihi`, `alim_gucu_ceyrek` korelasyondan hariç tutuldu | Önceki uygunluk taramasında (pm_rapor_sutun_temizlik_korelasyon.md §4b-c) zaten (b)/(c) kategorisi olarak işaretlenmişti |
| Noter devri analizi için hem `_toplam` hem `_otomobil` versiyonu ayrı ayrı raporlandı | K1 kapsamı otomobile özgü olduğu için otomobil versiyonu daha isabetli, ama toplam da referans için tutuldu |

---

## 6. Açık Sorular / PM Onayı Gerekenler

1. **Ham seviye korelasyonu mu, log-değişim (stationarize) korelasyonu mu
   esas alınmalı?** (bkz. Bölüm 5) Mevcut ham-seviye sonuçları, trend
   paylaşan seriler arasında yapay derecede yüksek korelasyon üretiyor
   olabilir. İstenirse aynı analiz log-aylık-değişim serileri üzerinden
   (genisletme_7'deki gibi) tekrarlanabilir — bu genellikle daha
   "temiz"/ekonomik olarak yorumlanabilir sonuçlar verir.
2. **`alim_gucu_ceyrek` hâlâ DF-A/DF-B'de duruyor** (önceki turda "yetim
   kaldı, silinsin mi?" diye sorulmuş, henüz cevap gelmedi) — bu rapor
   kapsamında da hariç tutuldu ama silinmedi.
3. **`odmd_otomobil_adet` — hem genel matriste hem noter devri analizinde
   en tutarlı orta-güçlü sinyal** (DF-A'da r=0,58/0,50; DF-B'de r=0,53/0,57)
   — bu, iki bağımsız kaynağın (ODMD sıfır-km satış, TÜİK noter devri)
   benzer bir piyasa hareketliliğini yakaladığına işaret ediyor, ekip
   lideri toplantısında ayrıca değerlendirilebilir.
4. **Az-gözlem uyarısı (projenin genel kültürüne uygun, tekrar
   hatırlatılıyor):** DF-B'nin bazı sütun çiftleri yalnızca n=25-28
   gözlemle hesaplandı (proxy log-değişim sütunları). Bu örneklem
   büyüklüğüyle p-değeri/anlamlılık testi bu raporda HİÇ hesaplanmadı —
   yalnızca r katsayıları raporlandı, çoklu-test düzeltmesi de
   uygulanmadı.

---

## 7. Önerilen Sonraki Adım (başlatılmadı — yalnızca öneri)

1. Log-değişim tabanlı bir korelasyon turu (Bölüm 6.1) — trend kaynaklı
   sahte korelasyonları ayıklamak için.
2. `alim_gucu_ceyrek`'in silinip silinmeyeceğine karar verilmesi (Bölüm 6.2).
3. p-değeri + çoklu-test düzeltmesi eklenmiş bir "resmi" korelasyon
   analizi (genisletme_7'nin DF-A/DF-B'ye uyarlanmış hali) — bu rapor
   yalnızca keşifsel/ön-tarama niteliğindeydi.
