# PM Raporu — İki DataFrame Kurulumu (DF-A geniş / DF-B dar-temiz)

**Tarih:** 2026-07-31
**Kapsam:** Yalnızca filtreleme/birleştirme. Enterpolasyon, yeni feature
türetme, korelasyon analizi, hedef değişikliği YAPILMADI. Omurga tablo
(`veri_2015_bugun_etiketli.csv`) değiştirilmedi — ondan türetilen iki YENİ
dosya oluşturuldu.
**Prompt arşivi:** `prompts/19_iki_dataframe_kurulumu_prompt.md`
**Kaynak kod:** `scripts/veri/genisletme_19_iki_dataframe.py`

---

## 1. Ne Yapıldı

Ekip liderinin talimatıyla, projedeki mevcut tek omurga tablosundan iki ayrı,
net tanımlı DataFrame türetildi:

1. **DF-A (geniş):** Omurga tablonun (artık `veri_2015_bugun_etiketli.csv`,
   138 satır) birebir kopyası + ENAG'a özgü 5 sütunun (`enag_aylik`,
   `enag_yillik`, `enag_tufe_fark_yillik`, `enag_kaynak_seviyesi`,
   `enag_kaynak_url`) `referans_ayi` üzerinden sol-birleştirme (left join)
   ile eklenmesi. BETAM kaynaklı sütunlar 2024 öncesinde NaN bırakıldı —
   bu beklenen ve korunması istenen davranıştır, dokunulmadı.
2. **DF-B (dar/temiz):** DF-A'dan, yalnızca `proxy_fiyat_cari_tl` sütununun
   dolu olduğu satırlar filtrelendi (`.notna()`). Hiçbir ay elle
   seçilmedi/çıkarılmadı — filtre tamamen bu tek sütuna dayanıyor, tanım
   gereği "BETAM'ın olmadığı ay yok" ilkesini otomatik sağlıyor.

Ayrıca `data/processed/dataframes/veri_sozlugu_df_a_df_b.md` güncellendi —
46 sütunun her biri için DF-A ve DF-B doluluk oranları ayrı ayrı listelendi.

**ÜÇ ÖNEMLİ SAPMA (görev talimatı ile güncel repo durumu arasında) — bkz.
Bölüm 5 için ayrıntı:**
- Talimattaki girdi dosyası (`veri_2018_bugun_etiketli.csv`, 102 satır)
  artık mevcut değil — repo içinde ayrı bir görevle ("genişletme 2015")
  omurga 2015-01'e genişletilip yeniden adlandırılmıştı. Bu script GÜNCEL
  omurgayı (`veri_2015_bugun_etiketli.csv`, 138 satır) kullandı.
- ENAG, talimatın varsaydığının aksine omurgaya HİÇ eklenmemişti (bilinçli
  önceki bir karar gereği ayrı tutuluyordu) — bu görevde DF-A'ya eklendi.
- BETAM'ın gerçek başlangıç ayı veride 2024-01'dir, talimatın bağlam
  notundaki "2023-12" ile birebir örtüşmüyor.

---

## 2. DF-A Boyutu ve Kapsamı

- **Dosya:** `data/processed/dataframes/df_a_genis_2015_bugun.csv` (+ .xlsx)
- **Boyut:** **138 satır × 46 sütun**
- **Tarih aralığı:** 2015-01 → 2026-06
- **İçerik:** Omurganın tüm 41 sütunu (kur, TÜFE, proxy fiyat/BETAM, faiz,
  ODMD, ÖTV olayları, OSD, tüketici güveni, noter devir, alım gücü, erişim
  endeksi, hedef etiketler) + yeni eklenen 5 ENAG sütunu.
- BETAM kaynaklı sütunlar 2024-01 öncesinde (110/138 ay) NaN — beklenen.
  ENAG sütunları 2024-01 öncesinde (108/138 ay) NaN — ENAG'ın kendisi de
  yalnızca 2024-01'den itibaren toplanmıştı, aynı yapısal sınır.

---

## 3. DF-B Boyutu, Kapsamı, Dışarıda Kalan Aylar

- **Dosya:** `data/processed/dataframes/df_b_dar_betam_bugun.csv` (+ .xlsx)
- **Boyut:** **28 satır × 46 sütun**
- **Tarih aralığı:** 2024-01 → 2026-06
- **Dışarıda kalan ay sayısı:** **110** (138 − 28)
- **Dışarıda kalan aylar (isim isim):**
  - **2015-01 → 2023-12 (108 ay, ardışık):** BETAM verisi bu pencerede
    hiç yok — DF-B tanımı gereği tamamen dışarıda.
  - **2024-05:** BETAM bu ay için rapor yayımlamadı (bilinen, önceden
    belgelenmiş boşluk).
  - **2025-02:** Aynı şekilde, BETAM bu ay için de rapor yayımlamadı.

---

## 4. DF-B'de Doğrulama Sonrası Hâlâ Eksik Kalan Sütunlar

DF-B "tamamen eksiksiz" DEĞİL — 28 satırın 11 sütununda hâlâ NaN var:

| Sütun | DF-B doluluk | Neden |
|---|---|---|
| `proxy_fiyat_arabamcom_referans_tl` | **0/28 (tamamen boş)** | **Yapısal bir çelişki:** bu sütun YALNIZCA BETAM'ın boş bıraktığı 2 ayda (2024-05, 2025-02) doludur — ama DF-B'nin kendi tanımı gereği tam o 2 ay dışarıda bırakılıyor. Sonuç: bu sütun DF-B içinde **her zaman, yapı gereği** tamamen boş kalacak. Kullanışsız bir sütun değil ama DF-B bağlamında anlamsız — DF-A'da anlamlıdır. |
| `otv_aciklama` | 1/28 | Tasarım gereği (yalnızca olay ayında dolu) — DF-B penceresinde (2024-01→2026-06) yalnızca 1 ÖTV olayı (2025-07) var. |
| `odmd_otomobil_adet`, `odmd_hta_adet` | 27/28 | 2026-06 için kaynak yalnızca toplamı vermiş (önceden bilinen tekil gap, BETAM ile ilgisiz). |
| `brut_ucret_maas_endeksi_2021_100`, `alim_gucu_ceyrek`, `erisim_endeksi` | 25/28 | 2026-Q2 (Nisan-Haziran) TÜİK bülteni henüz yayımlanmadı — BETAM'dan bağımsız, ayrı bir yapısal gecikme. |
| `proxy_nominal_aylik_pct`, `proxy_reel_aylik_pct`, `proxy_aylik_log_degisim`, `proxy_reel_aylik_log_degisim` | 25/28 | 3 satır NaN: (i) 2024-01 — serinin ilk ayı, önceki ay yok; (ii) 2024-06 — 2024-05 boşluğunun bir sonraki aya sıçraması; (iii) 2025-03 — 2025-02 boşluğunun aynı şekilde sıçraması. Bu 3 satır DF-B'de KALIYOR (kendi `proxy_fiyat_cari_tl` dolu) ama komşu ayı NaN olduğu için değişim hesaplanamıyor. |

**ENAG sütunları için özel not:** Görev talimatı "BETAM'ın 2023-12 ayı için
ENAG NaN kalabilir" diye özel bir kontrol istiyordu — ama bu senaryo
GERÇEKLEŞMEDİ, çünkü (Bölüm 5'te açıklanan sapma nedeniyle) BETAM'ın DF-B'ye
giren ilk ayı zaten 2024-01'dir, ENAG de tam o aydan itibaren doludur.
Sonuç: **ENAG'ın 5 sütunu da DF-B içinde 28/28 (tamamen dolu).**

---

## 5. Karşılaşılan Sorunlar

1. **Girdi dosyası artık yok (kritik, proaktif bildirim):** Talimat
   `veri_2018_bugun_etiketli.csv`'yi (102 satır, 2018-01 başlangıçlı)
   girdi olarak gösteriyordu. Bu dosya, bu görevden ÖNCE başka bir görevle
   ("genişletme 2015") 2015-01'e genişletilip `veri_2015_bugun_etiketli.csv`
   olarak yeniden adlandırılmış, eski dosya silinmişti. Talimat muhtemelen
   bu değişiklikten önce yazılmış/planlanmıştı. Script GÜNCEL dosyayı
   kullandı — bu, DF-A'nın kapsamını talimattaki "2018-01→bugün" yerine
   fiilen "2015-01→bugün" yapıyor (138 satır, 102 değil). Çıktı dosya adı
   da buna göre `df_a_genis_2015_bugun.csv` olarak adlandırıldı (talimattaki
   `df_a_genis_2018_bugun.csv` yerine) — kapsamla tutarlı isimlendirme için.
2. **ENAG omurgada hiç yoktu:** Talimat DF-A'nın kapsamına ENAG'ı da
   sayıyor ve DF-B doğrulamasında ENAG'ın zaten sütun olarak var olduğunu
   varsayıyordu — ama ENAG önceki bir kararla (`pm_rapor_enag_cekme.md`)
   BİLİNÇLİ OLARAK omurgaya hiç eklenmemişti, ayrı bir karşılaştırma
   dosyasında duruyordu. Bu görev kapsamında ENAG'a özgü 5 sütun DF-A'ya
   eklendi (TÜFE'nin kendisi ENAG dosyasından TEKRAR alınmadı, omurganın
   kendi TÜFE sütunları korundu — iki farklı TÜFE hesaplamasını
   karıştırmamak için).
3. **BETAM başlangıç ayı talimatla örtüşmüyor:** Talimatın bağlam notu
   "BETAM verisi 2023-12'den itibaren düzenli yayımlanıyor" diyordu, ama
   omurga tablosunda `proxy_fiyat_cari_tl` GERÇEKTE ilk kez 2024-01'de
   doludur. Script yazılı varsayıma değil, verinin kendisine
   (`.notna()` filtresi) göre çalıştığı için bu sapma sonucu etkilemedi,
   ama rakamsal tutarsızlık açıkça not edilmelidir.
4. Bunların dışında teknik bir sorun çıkmadı — birleştirme/filtreleme
   sorunsuz tamamlandı, iki dosya da doğrulandı.

---

## 6. Veri Örneği

**DF-A'dan 3 satır (biri 2018, biri 2023 öncesi, biri 2024 sonrası —
seçilen sütunlar):**

```
referans_ayi  usdtry_aysonu  tufe_endeks  proxy_fiyat_cari_tl  noter_devir_toplam_adet  enag_aylik  enag_yillik enag_kaynak_seviyesi
     2018-06        4.61245       357.44                  NaN                 617217.0         NaN          NaN                  NaN
     2021-06        8.71300       547.48                  NaN                 842050.0         NaN          NaN                  NaN
     2025-06       39.77820      3132.17             968926.0                 840022.0        3.05        68.68                    C
```

**DF-B'den ilk 3 satır:**

```
referans_ayi  usdtry_aysonu  tufe_endeks  proxy_fiyat_cari_tl  noter_devir_toplam_adet  enag_aylik  enag_yillik enag_kaynak_seviyesi
     2024-01       30.33260      1984.02             860443.0                 782589.0        9.38       129.11                    C
     2024-02       31.14810      2073.88             855781.0                 847861.0        4.32       121.98                    C
     2024-03       32.28865      2139.47             859035.0                 865144.0        5.68       124.63                    C
```

**DF-B'den son 3 satır:**

```
referans_ayi  usdtry_aysonu  tufe_endeks  proxy_fiyat_cari_tl  noter_devir_toplam_adet  enag_aylik  enag_yillik enag_kaynak_seviyesi
     2026-04       45.02555  4028.244072            1168000.0                 919896.0        5.07        55.38                    C
     2026-05       45.67230  4097.317874            1175000.0                 752150.0        2.16        53.13                    C
     2026-06       46.59705  4137.743556            1169000.0                 941964.0        1.94        51.49                    C
```

---

## 7. Açık Sorular / PM Onayı Gerekenler

1. **Kapsam sapması (2018 → 2015) kabul edilebilir mi?** DF-A talimatta
   istenenden 3,5 yıl daha geniş (2015-01 başlangıçlı) çıktı, çünkü
   güncel omurga zaten bu şekilde. Eğer ekip lideri gerçekten yalnızca
   2018-01→bugün kapsamlı bir DF-A istiyorsa, mevcut DF-A'dan basit bir
   tarih filtresiyle (`referans_ayi >= "2018-01"`) ayrı bir sürüm
   üretilebilir — bu görevde YAPILMADI, onay bekleniyor.
2. **`proxy_fiyat_arabamcom_referans_tl` sütunu DF-B'de yapı gereği hep
   boş kalacak (Bölüm 4) — bu sütun DF-B'den tamamen çıkarılsın mı, yoksa
   "DF-A'da anlamlı, DF-B'de her zaman boş" notuyla olduğu gibi mi
   kalsın?** Bu görevde ÇIKARILMADI (talimat "sütun ekleme/çıkarma yok"
   demiyordu ama temkinli davranıldı) — küçük bir sonraki adım olabilir.
3. **ENAG'ın omurgaya (DF-A'ya) eklenmesi kalıcı bir karar mı, yoksa
   yalnızca bu iki DataFrame'e özgü mü?** Önceki bir karar ENAG'ın TÜİK
   TÜFE ile "tek seri" haline getirilmemesini istemişti (metodoloji
   karışıklığı riski) — burada birleştirme yapılmadı, yalnızca ayrı
   sütunlar olarak eklendi, bu farkı netleştirmek gerekebilir.
4. **DF-A dosya adı (`df_a_genis_2015_bugun.csv`) talimattaki isimden
   (`df_a_genis_2018_bugun.csv`) farklı** — bu, kapsam sapmasının doğal
   sonucu olarak seçildi (isim içeriğe uysun diye), ama eğer başka
   kod/analiz zaten talimattaki ismi bekliyorsa bu bir uyumsuzluk
   yaratabilir; onay/bilgilendirme gerekir.
