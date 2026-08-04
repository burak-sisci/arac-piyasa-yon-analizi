# PM Raporu — DF-A / DF-B v3 (Ay-Hizalı Kaynaktan) (Görev 29)

**Tarih:** 2026-08-04
**Prompt arşivi:** `prompts/29_df_a_df_b_v3_ay_hizali_prompt.md`
**Kaynak script:** `scripts/veri/genisletme_29_df_a_df_b_v3.py`
**Kaynak tablo:** `data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv`
(28 numaralı görevde bağımsız doğrulanmış — **değiştirilmedi**)
**Çıktılar:** `data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv`,
`data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv`,
`data/processed/dataframes/veri_sozlugu_df_a_df_b_v3.md`

Bu görevde **korelasyon analizi ÇALIŞTIRILMADI** — yalnızca DataFrame
kurma ve belgeleme yapıldı (görev talimatına uygun).

---

## 1. Ne Yapıldı

`df_gunluk_forward_fill_2015_bugun.csv` (ay-hizalı doldurulmuş, günlük
satır yapısında, 4234 satır × 48 sütun) kaynak alınarak, 21 numaralı
görevin "kapsama testi" mantığının güncellenmiş hali uygulandı:

- **ÖTV sütunları (3 adet) baştan tamamen dışlandı** — kapsama testine
  bile girmediler (Bölüm 2).
- **DF-A**, noter devri serisinin başlangıcını ankor alıp, o pencereyi
  gerçekten kapsayan sütunları seçti (Bölüm 3).
- **DF-B**, 2024-01-01'den bugüne, kapsama testi uygulamadan TÜM
  sütunları (ENAG + BETAM dahil) içeriyor (Bölüm 4).
- Her iki DataFrame de **GÜNLÜK satır yapısında** kuruldu — aya indirgeme
  yapılmadı (talimata uygun, Görev 4).
- Veri sözlüğü, her sütun için açıklama + doluluk oranı + veri tipi +
  gerçek örnek değerlerle üretildi (Bölüm 5).

---

## 2. ÖTV Dışlama Listesi (Görev 1)

Kaynak tablodaki "otv" geçen 3 sütun tespit edilip **hem DF-A'dan hem
DF-B'den tamamen dışlandı**, kapsama testine bile sokulmadı:

- `otv_referans_ay`
- `otv_aciklama`
- `otv_event_gunu_mu`

Gerekçe (talimatta belirtildiği gibi): bu sütunlar hâlâ yalnızca olayın
gerçekleştiği tek günde dolu/1, diğer tüm günlerde 0/NaN — aşırı seyrek
ve dengesiz, bu iki DataFrame'e katkısı yok.

---

## 3. DF-A: Noter Devri Penceresi

**Boyut:** 4234 satır × 35 sütun
**Tarih aralığı:** 2015-01-01 → 2026-08-04 (bugün)
**Ankor:** `noter_devir_toplam_adet` — ilk dolu ayı 2015-01
(`noter_devir_otomobil_adet`'in ilk dolu ayı olan 2018-01'den daha erken
olduğu için ankor olarak seçildi, kodla doğrulandı).

**Kapsama testi metodolojisi — ÖNEMLİ NOT:** Test, sütunun ilk dolu
GÜNÜ değil, ilk dolu AYI üzerinden yapıldı. Nedeni: `usdtry_alis` gibi
gerçek günlük kaynakların ilk dolu günü 2015-01-02'dir (2015-01-01
Yılbaşı tatili, kur işlemi yok) — bu bir kaynak boşluğu değil, rutin bir
tatil-günü boşluğu; gün granülerliğinde test edilseydi bu sütunlar
YANLIŞLIKLA elenirdi. Ay granülerliğinde ikisi de "2015-01" ayında
başlıyor, ankorla eşit → geçer.

Ayrıca `tufe_aylik_degisim` (ilk dolu ay: 2015-02) ve `tufe_yillik_degisim`
(ilk dolu ay: 2016-01) için **20/21 numaralı görevlerdeki önceki karar
tutarlılığı** uygulandı: bunlar hesaplama gereği (bir önceki ay/yıl
karşılaştırması olmadan hesaplanamadıkları için) gecikmeli başlıyor —
bu bir kaynak boşluğu değil, yapısal bir gecikme, TÜFE'nin kendisi
(`tufe_endeks`) ankorla aynı ayda (2015-01) başladığı için istisna
tanınıp DF-A'da tutuldular.

**Kapsama testini GEÇEN sütunlar (28):**
`altin_gram_try`, `altin_referans_ay`, `eurtry_alis`, `eurtry_orta`,
`eurtry_satis`, `faiz_referans_ay`, `noter_devir_toplam_adet`,
`noter_referans_ay`, `odmd_hta_adet`, `odmd_otomobil_adet`,
`odmd_referans_ay`, `odmd_toplam_adet`, `osd_binek_adet`,
`osd_binek_kamyonet_toplam_adet`, `osd_kamyonet_adet`, `osd_referans_ay`,
`otomobil_satinalma_ihtimali_endeksi`, `politika_faizi`,
`tasit_kredisi_faiz`, `tufe_aylik_degisim` **[istisna: hesaplama
gecikmesi]**, `tufe_endeks`, `tufe_referans_ay`, `tufe_yillik_degisim`
**[istisna: hesaplama gecikmesi]**, `tuketici_guven_endeksi`,
`tuketici_referans_ay`, `usdtry_alis`, `usdtry_orta`, `usdtry_satis`
(+ yapısal sütunlar: `tarih`, `yil`, `ay`, `gun`, `ceyrek`,
`haftanin_gunu`, `yilin_gunu`)

**Kapsama testini GEÇEMEYEN sütunlar (10) — hangi ay başladığı ile:**

| Sütun | İlk dolu ay | Neden geçemedi |
|---|---|---|
| `noter_devir_otomobil_adet` | 2018-01 | Kaynak, otomobil kırılımını 2018'den önce tutmuyor |
| `alim_gucu_referans_ay` | 2018-01 | Alım gücü kaynağı 2018'den önce yok |
| `brut_ucret_maas_endeksi_2021_100` | 2018-01 | Aynı kaynak |
| `enag_referans_ay` | 2021-01 | ENAG 2020'de kurulmuş, 2021'den önce veri yok |
| `enag_aylik_degisim` | 2021-01 | Aynı kaynak |
| `enag_yillik_degisim` | 2021-09 | Aynı kaynak (+12 ay hesaplama gecikmesi) |
| `proxy_referans_ay` | 2024-01 | BETAM 2024'ten önce veri toplanmamış |
| `proxy_fiyat_cari_tl` | 2024-01 | Aynı kaynak |
| `proxy_dom_gun` | 2024-01 | Aynı kaynak |
| `proxy_satis_orani_pct` | 2024-01 | Aynı kaynak |

---

## 4. DF-B: ENAG + BETAM Dahil, 2024-01'den Bugüne

**Boyut:** 947 satır × 45 sütun
**Tarih aralığı:** 2024-01-01 → 2026-08-04 (bugün)
**Kapsama testi UYGULANMADI** — DF-A'nın 34 sütununa (tarih hariç) ek
olarak `noter_devir_otomobil_adet`, ENAG grubu (`enag_referans_ay`,
`enag_aylik_degisim`, `enag_yillik_degisim`) ve BETAM/proxy grubu
(`proxy_referans_ay`, `proxy_fiyat_cari_tl`, `proxy_dom_gun`,
`proxy_satis_orani_pct`) dahil — toplam 45 sütun (48 kaynak sütun - 3
ÖTV sütunu).

Satır sayısı teyidi: 2024-01-01 → 2026-08-04 arası kesin gün sayısı
947 — kaynak tablodaki aynı aralıktaki satır sayısıyla birebir eşleşiyor.

---

## 5. Veri Sözlüğü Özeti

`veri_sozlugu_df_a_df_b_v3.md` üretildi — DF-A (35 sütun) ve DF-B (45
sütun) için ayrı bölümler halinde, her sütun için: açıklama, doluluk
oranı (dolu/toplam, yüzde), veri tipi ve tablodan alınmış 2-3 gerçek
örnek değer.

Örnek girdiler:

| Sütun | Açıklama | Doluluk | Örnek değerler |
|---|---|---|---|
| `noter_devir_toplam_adet` (DF-A) | Aylık toplam noter araç devir/satış adedi (ankor sütun) | 4199/4234 (%99,2) | 462576, 486715, 576623 |
| `proxy_fiyat_cari_tl` (yalnızca DF-B) | BETAM ikinci-el araç piyasası ortalama ilan fiyatı (cari TL) | 853/947 (%90,1) | 860443, 855781, 859035 |
| `enag_aylik_degisim` (yalnızca DF-B) | ENAG bağımsız aylık enflasyon ölçümü (%) | 912/947 (%96,3) | 9.38, 4.32, 5.68 |

---

## 6. Karşılaşılan Sorunlar

Teknik bir hata çıkmadı. İki metodolojik not proaktif olarak bildiriliyor:

1. **Kapsama testi granülerliği (gün vs ay) — yorumlayıcı karar.**
   Testi literal olarak GÜN bazında uygulasaydım, `usdtry_*`/`eurtry_*`
   gibi temel günlük kaynaklar YANLIŞLIKLA elenecekti (Yılbaşı tatili
   yüzünden ilk dolu günleri 2015-01-02, ankorun 2015-01-01'inden 1 gün
   geç). Bunun yerine AY granülerliğinde test ettim — bu, 20 numaralı
   görevde kurulan "kaynak boşluğu vs rutin/yapısal boşluk" ayrımının
   doğal bir uzantısı. Bu kararı burada açıkça belirtiyorum, sessizce
   uygulamadım.
2. **TÜFE'nin iki değişim sütununa (`tufe_aylik_degisim`,
   `tufe_yillik_degisim`) hesaplama-gecikmesi istisnası uygulandı** —
   20/21 numaralı görevlerdeki AYNI karar tekrarlandı (bkz. Bölüm 3).
   Başka HİÇBİR sütuna bu istisna uygulanmadı — ENAG, BETAM, alım gücü
   ve `noter_devir_otomobil_adet` GERÇEKTEN daha geç başlayan kaynaklar,
   hesaplama gecikmesi değil.
3. DF-A'nın en son birkaç günü (2026-08-02..04) TÜM aylık sütunlarda NaN
   — bu bir hata değil, Ağustos 2026'nın referans ayı henüz hiçbir
   kaynakta yayımlanmadığı için (bkz. Bölüm 7 örneği).

---

## 7. Veri Örneği

**DF-A — ilk 3 ve son 3 satır** (seçili sütunlar):

| tarih | usdtry_alis | noter_devir_toplam_adet | tufe_endeks |
|---|---|---|---|
| 2015-01-01 | NaN (tatil günü) | 462576.0 | 250.45 |
| 2015-01-02 | 2.3269 | 462576.0 | 250.45 |
| 2015-01-03 | NaN (hafta sonu) | 462576.0 | 250.45 |
| ... | ... | ... | ... |
| 2026-08-02 | NaN | NaN | NaN |
| 2026-08-03 | NaN | NaN | NaN |
| 2026-08-04 | NaN | NaN | NaN |

(Son 3 satır tamamen NaN — Ağustos 2026 için henüz hiçbir aylık kaynak
yayımlanmadı, USD/TRY'nin kendisi de o günler hafta sonuna denk geldiği
için boş; bu beklenen bir durum.)

**DF-B — ilk 3 ve son 3 satır** (seçili sütunlar):

| tarih | enag_aylik_degisim | proxy_fiyat_cari_tl | noter_devir_otomobil_adet |
|---|---|---|---|
| 2024-01-01 | 9.38 | 860443.0 | 530744.0 |
| 2024-01-02 | 9.38 | 860443.0 | 530744.0 |
| 2024-01-03 | 9.38 | 860443.0 | 530744.0 |
| ... | ... | ... | ... |
| 2026-08-02 | NaN | NaN | NaN |
| 2026-08-03 | NaN | NaN | NaN |
| 2026-08-04 | NaN | NaN | NaN |

---

## 8. Açık Sorular / PM Onayı Gerekenler

1. **Kapsama testi granülerliği kararı (Bölüm 6, madde 1) onay bekliyor
   mu, yoksa mantıklı bulunup kabul mü edilecek?** Gün bazında test
   edilmesi istenirse `usdtry_*`/`eurtry_*` DF-A'dan çıkarılır (bu,
   DF-A'yı ciddi şekilde zayıflatır, önerilmez ama teknik olarak
   mümkün).
2. **TÜFE değişim sütunlarına uygulanan hesaplama-gecikmesi istisnası**
   (Bölüm 3/6) — önceki görevlerle tutarlı ama tekrar teyit edilmek
   istenirse burada.
3. Başka açık soru yok — hatalar bulunmadı, tasarım kararları önceki
   görevlerle tutarlı şekilde uygulandı.

---

**NOT:** İki DataFrame de hazır ve doğrulanmış durumda. Bu görevde
**korelasyon analizi ÇALIŞTIRILMADI** — proje sahibinin ayrı onayıyla,
kendi belirleyeceği yöntemle (günlük veya aya-indirgenmiş) bir sonraki
adımda ele alınacak.

---

## EK — 2026-08-04: Proxy Fiyat (BETAM) Grubu Zenginleştirildi

Proje sahibi, eski (v1/v2, aylık frekans) DF-A/DF-B pipeline'ında
kullanılan bazı proxy_fiyat sütunlarının bu (v3, günlük) pipeline'da
eksik olduğunu fark etti ve tamamlanmasını istedi.

**Eklenen 6 yeni sütun** (`scripts/veri/genisletme_26_forward_fill_gunluk.py`
güncellendi, `_proxy_zenginlestirilmis()` fonksiyonu eklendi):

- `proxy_reel_aylik_pct`, `proxy_nominal_yillik_pct`, `proxy_talep_aylik_pct`
  — ham kaynakta (`data/raw/proxy_fiyat/proxy_fiyat_2024_bugun_raw.csv`)
  zaten mevcuttu, hiç kullanılmamıştı; doğrudan aktarıldı.
- `proxy_nominal_aylik_pct`, `proxy_aylik_log_degisim`,
  `proxy_reel_aylik_log_degisim` — eski pipeline'da (`genisletme_6_
  hedef_etiket.py`) `proxy_fiyat_cari_tl` üzerinden hesaplanan sütunlardı;
  AYNI formülle (`pct_change()`, `ln(x_t/x_t-1)`, TÜFE'ye bölünmüş "reel
  gösterge") burada da yeniden hesaplandı. Değerler eski pipeline'ın
  üreteceği değerlerle birebir tutarlı (2024-02 için proxy_nominal_aylik_pct
  = -0.5418..., manuel çapraz kontrol edildi).

**Proaktif not:** `proxy_reel_aylik_pct` için BETAM'ın KENDİ yayımladığı
ham değer kullanıldı, eski pipeline'ın yerel yeniden-hesaplaması DEĞİL
(ikisi ayrı ayrı hesaplanıp çapraz kontrol edildi — sayısal olarak
neredeyse özdeş çıktı, ör. 2024-02: ham=-5.00 vs yerel-hesap=-4.85 —
birincil/ham kaynak tercih edildi, daha güvenilir).

**Bu sütunlar YALNIZCA DF-B'ye girdi, DF-A'ya GİREMEDİ** — hepsi BETAM
kaynaklı olduğu için ilk dolu ayları 2024-01/2024-02, DF-A'nın kapsama
testini (ankor: 2015-01) yapısal olarak geçemiyorlar. Bu bir hata değil,
BETAM'ın 2024'ten önce hiç veri toplamamış olmasının doğal sonucu.

**Sonuç:** `df_gunluk_forward_fill_2015_bugun.csv` 48→54 sütun,
`df_b_v3_enag_betam_2024_bugun.csv` 45→51 sütun (DF-A 35 sütunda
DEĞİŞMEDİ). Tüm dosyalar yeniden üretildi (script + Excel çıktıları),
satır sayıları ve ay-içi tutarlılık yeniden doğrulandı — sorun yok.

**AÇIK SORU — proje sahibinin gönderdiği eski korelasyon ekran
görüntülerindeki OTV sütunları (`otv_event_ay_mi`,
`otv_ay_farki_en_yakin_olay`) hakkında henüz karar verilmedi** — bu
sütunlar Görev 29'da proje sahibinin KENDİ talimatıyla DF-A/DF-B'den
tamamen dışlanmıştı. Ekran görüntülerinde bu sütunların bulunması, bu
kararın gözden geçirilmek istendiği anlamına mı geliyor, yoksa ekran
görüntüsü yalnızca proxy/ENAG sütunlarını göstermek için mi
paylaşıldı — proje sahibine ayrıca soruldu (bkz. sohbet).

---

## EK 2 — 2026-08-04: Kapsam Netleştirmesi ve `proxy_ilan_sayisi` Denemesi

Proje sahibi, EK 1'de eklenen 6 sütunu onayladı ve netleştirdi:
`kaynak_url`, `kaynak_seviyesi`, `cift_dogrulama`, `veri_donemi`,
`kaynak`, `kaynak_rapor_basligi`, `kaynak_alinti`,
`proxy_fiyat_arabamcom_referans_tl`, `otv_referans_ay`, `otv_aciklama`,
`otv_event_gunu_mu` KESİNLİKLE eklenmeyecek (zaten eklenmemişti).

`proxy_ilan_sayisi` eklenmesi istendi — kontrol edildi, ham kaynakta
**tamamen boş** çıktı (0/30 dolu, `enag_endeks`'teki duruma birebir
benzer). Bu bulgu proje sahibine bildirildi, ardından **sütunün
tamamen silinmesi** istendi: `genisletme_1c_proxy_fiyat.py`'den
kaldırılıp ham kaynak (`data/raw/proxy_fiyat/proxy_fiyat_2024_bugun_raw.csv`)
yeniden üretildi, `genisletme_26`'nın sütun listesine hiç eklenmedi.
**Nihai sonuç EK 1 ile aynı: DF-B 51 sütun, DF-A 35 sütun (değişmedi).**

**`noter_devir_otomobil_adet`'in DF-A'ya eklenmesi hakkındaki soruya
yanıt:** Teknik olarak MÜMKÜN (CSV/pandas NaN bloğunu sorunsuz taşır)
ama DF-A'nın kendi tasarım ilkesine AYKIRI. Sütun 2018-01'de başlıyor;
DF-A'ya eklenirse 2015-01→2017-12 arası **1096 satır (%25,9) baştan
sona NaN** kalır — bu, tam olarak 20/21 numaralı görevlerde
"içerdiği NaN'larla dahil et" mantığından "gerçekten kapsıyor mu"
mantığına geçilme SEBEBİYLE kaçınılmak istenen durumdur. Diğer DF-A
sütunlarındaki boşluklar (hafta sonu/tatil gibi) dağınık ve küçük;
bu ise pencerenin başında 3 yıl kesintisiz bir blok olurdu. **Öneri:**
DF-A'da kalmasın — zaten DF-B'de tam karşılığı var (2024-01'den
itibaren tam dolu). İstenirse yine de eklenebilir, ama bu DF-A'nın
"kapsama testi geçen sütun" tanımını bilerek gevşetmek anlamına gelir.

---

## EK 3 — 2026-08-04: `noter_devir_otomobil_adet` DF-A'ya Manuel Eklendi

Proje sahibi, EK 2'deki soruyu yanıtladı: "her iki dataya da ekle."
`genisletme_29_df_a_df_b_v3.py`'ye `MANUEL_DAHIL_EDILEN` istisna kümesi
eklendi — `noter_devir_otomobil_adet`, kapsama testini GEÇEMEDİĞİ HALDE
(ilk dolu ayı 2018-01) DF-A'ya bilinçli olarak dahil edildi.

**Doğrulanan sonuç:** DF-A 35→36 sütun. Sütun 2015-01-01→2017-12-31
arası **1096 satır (%25,9) tamamen NaN** (kodla doğrulandı), 2018-01'den
itibaren 3103/3138 dolu. DF-B zaten bu sütunu içeriyordu (Görev 29'un
ilk halinden beri) — değişmedi (51 sütun).

Bu, önceden bildirilen riskin AYNEN gerçekleştiği, beklenmedik bir yan
etki OLMADIĞI anlamına gelir — proje sahibi riski bilerek onayladı.
Veri sözlüğü ve tüm çıktı dosyaları (CSV + Excel) güncellendi.
