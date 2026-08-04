# PM Raporu — Forward-Fill'li Günlük Tablo (Görev 26)

**Tarih:** 2026-08-04
**Prompt arşivi:** `prompts/veri/26_forward_fill_gunluk_tablo_prompt.md`
**Kaynak script:** `scripts/veri/genisletme_26_forward_fill_gunluk.py`
**Girdi:** `data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv`
(25 numaralı görevin çıktısı — **değiştirilmedi, olduğu gibi kaldı**)
**Çıktı:** `data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv`
(YENİ ve AYRI dosya; git-dışı, yalnızca kod + bu rapor commit'lenir)

---

## 1. Ne Yapıldı

25 numaralı görevin "as-of/sızıntısız" günlük-karışık-frekans tablosu
(`df_gunluk_karisik_frekans_2015_bugun.csv`) **okundu, hiçbir şekilde
değiştirilmedi**. Onun yanına, aylık/çeyreklik kaynak sütunlarının
forward-fill edildiği **yeni ve ayrı** bir tablo üretildi
(`df_gunluk_forward_fill_2015_bugun.csv`).

Mantık: her aylık/çeyreklik sütun, kaynak tabloda zaten yalnızca kendi
as-of gününde dolu, diğer tüm günlerde NaN. Bu deseni `.ffill()` ile
ileri doğru genişletmek tam istenen davranışı üretiyor — bir sonraki
gerçek as-of değer gelene kadar en son gerçek değer taşınıyor, ay
değişince otomatik güncelleniyor (önceki ayın değeri asla bir sonraki
ayın gerçek değerini geçersiz kılmıyor ya da sızmıyor). İlk as-of
değerinden önceki dönem NaN kalmaya devam ediyor (geriye doldurma yok).

Forward-fill edilen **her bir değer sütunu için** `<sütun>_gercek_mi`
adında bir bayrak sütunu eklendi (1 = o gün gerçek as-of günü, 0 =
taşınmış/forward-fill değer ya da henüz hiç veri gelmemiş dönem).

**Dokunulmayanlar (aynen kopyalandı):** `usdtry_*`, `eurtry_*` (zaten
günlük), `otv_referans_ay`/`otv_aciklama`/`otv_event_gunu_mu` (olay-bazlı,
forward-fill anlamsız), takvim sütunları (`yil, ay, gun, ceyrek,
haftanin_gunu, yilin_gunu`), `tarih`.

**Yorumlayıcı bir ek karar:** her grubun `..._referans_ay` yardımcı
sütunu da forward-fill edildi (hangi ayın değerinin o gün gösterildiğini
okunur kılmak için) — bu, görev talimatında açıkça istenmemişti ama
tablonun kendi başına anlaşılır olması için gerekli görüldü (bkz.
Bölüm 7, açık soru 1).

---

## 2. Yeni Tablo Boyutu

**4234 satır × 70 sütun** (orijinal 48 sütun + 22 `_gercek_mi` bayrağı).

Forward-fill edilen 22 değer sütunu (10 kaynak grubu): `altin_gram_try`;
`tufe_endeks, tufe_aylik_degisim, tufe_yillik_degisim`;
`enag_aylik_degisim, enag_yillik_degisim`; `noter_devir_toplam_adet,
noter_devir_otomobil_adet`; `odmd_toplam_adet, odmd_otomobil_adet,
odmd_hta_adet`; `osd_binek_adet, osd_kamyonet_adet,
osd_binek_kamyonet_toplam_adet`; `tuketici_guven_endeksi,
otomobil_satinalma_ihtimali_endeksi`; `proxy_fiyat_cari_tl,
proxy_dom_gun, proxy_satis_orani_pct`; `brut_ucret_maas_endeksi_2021_100`;
`tasit_kredisi_faiz, politika_faizi`.

---

## 3. Doğrulama Sonucu

**Satır sayısı teyidi:** Orijinal tablo 4234 satır, forward-fill tablosu
da 4234 satır — birebir eşleşiyor (forward-fill satır eklemedi/çıkarmadı,
yalnızca var olan NaN'ları doldurdu).

**3 örnek ay** (`noter_devir_toplam_adet` üzerinden, erken/orta/güncel):

| Ay | Ayın tüm günlerindeki değer | Benzersiz değer sayısı |
|---|---|---|
| 2016-06 | 593781.0 (01'den 30'a kadar sabit) | 1 |
| 2020-06 | 561375.0 (01'den 30'a kadar sabit) | 1 |
| 2026-06 | 752150.0 (01'den 30'a kadar sabit) | 1 |

Her üç ayda da ay içindeki TÜM günler aynı değeri taşıyor (kod ile
doğrulandı, `nunique()==1`).

**Ay sınırında sızıntı kontrolü** (2020-05-28 → 2020-06-03,
`noter_devir_toplam_adet`):

| tarih | değer | gerçek_mi | referans_ay |
|---|---|---|---|
| 2020-05-28 | 348678.0 | 0 | 2020-04 |
| 2020-05-31 | 348678.0 | 0 | 2020-04 |
| **2020-06-01** | **561375.0** | **1** | **2020-05** |
| 2020-06-02 | 561375.0 | 0 | 2020-05 |
| 2020-06-03 | 561375.0 | 0 | 2020-05 |

Mayıs ayının değeri (348678.0) Haziran'a SIZMADI — 2020-06-01'de yeni
as-of değer (561375.0) devreye girdi ve `gercek_mi=1` işaretlendi, sonraki
günler bu yeni değeri taşıyor. Beklenen davranış doğrulandı.

---

## 4. Doluluk Karşılaştırma Tablosu (Eski vs Yeni)

| Sütun | Eski (as-of-tek-gün) | Yeni (forward-fill) |
|---|---|---|
| altin_gram_try | 137/4234 | 4203/4234 |
| tufe_endeks | 138/4234 | 4201/4234 |
| tufe_aylik_degisim | 137/4234 | 4173/4234 |
| tufe_yillik_degisim | 126/4234 | 3836/4234 |
| enag_aylik_degisim | 65/4234 | 2011/4234 |
| enag_yillik_degisim | 58/4234 | 1769/4234 |
| noter_devir_toplam_adet | 138/4234 | 4203/4234 |
| noter_devir_otomobil_adet | 102/4234 | 3107/4234 |
| odmd_toplam_adet | 138/4234 | 4203/4234 |
| odmd_otomobil_adet | 137/4234 | 4203/4234 |
| odmd_hta_adet | 137/4234 | 4203/4234 |
| osd_binek_adet | 138/4234 | 4203/4234 |
| osd_kamyonet_adet | 138/4234 | 4203/4234 |
| osd_binek_kamyonet_toplam_adet | 138/4234 | 4203/4234 |
| tuketici_guven_endeksi | 139/4234 | 4203/4234 |
| otomobil_satinalma_ihtimali_endeksi | 139/4234 | 4203/4234 |
| proxy_fiyat_cari_tl | 26/4234 | 887/4234 |
| proxy_dom_gun | 26/4234 | 887/4234 |
| proxy_satis_orani_pct | 26/4234 | 887/4234 |
| brut_ucret_maas_endeksi_2021_100 | 99/4234 | 3107/4234 |
| tasit_kredisi_faiz | 139/4234 | 4203/4234 |
| politika_faizi | 139/4234 | 4203/4234 |

**Gözlem:** `proxy_fiyat_cari_tl` grubu en düşük doluluk artışını
gösteriyor (26 → 887, ~%21) — çünkü bu kaynak yalnızca 2024-01'den
itibaren mevcut (2015-2023 arası hiç yok, forward-fill'in dolduracağı
bir "önceki ay" yok). `noter_devir_otomobil_adet` ve
`brut_ucret_maas_endeksi_2021_100` de benzer şekilde daha kısa kapsamlı
kaynaklar oldukları için (sırasıyla 2018-01, 2018-01'den itibaren) diğer
138/139'dan başlayan sütunlara göre daha az doluyor (3107/4234).

---

## 5. Karşılaşılan Sorunlar

Teknik bir sorun çıkmadı. Tek not edilmesi gereken nokta: `.ffill()`
işleminin doğru çalışması için tablo `tarih` sütununa göre sıralı olması
gerekiyordu — kaynak tablo zaten sıralıydı, ancak script kendi içinde de
`sort_values("tarih")` ile bunu garanti altına aldı (savunmacı bir
kontrol, hata bulunmadı).

---

## 6. Veri Örneği

`noter_devir_toplam_adet` ve `tufe_endeks` için, 2020-06 ayının başındaki
gerçek as-of günü ile aynı ayın ortasındaki forward-fill edilmiş bir gün
yan yana:

| tarih | noter_devir_toplam_adet | noter_..._gercek_mi | tufe_endeks | tufe_endeks_gercek_mi | noter_referans_ay | tufe_referans_ay |
|---|---|---|---|---|---|---|
| **2020-06-01** (as-of) | 561375.0 | **1** | 454.43 | **0** | 2020-05 | 2020-04 |
| **2020-06-15** (ara gün) | 561375.0 | **0** | 460.62 | **0** | 2020-05 | 2020-05 |

**Dikkat çekici gözlem:** 2020-06-01'de noter devri KENDİ as-of günündeyken
(`gercek_mi=1`), TÜFE o gün henüz kendi as-of gününe ulaşmamış
(`tufe_endeks_gercek_mi=0`, hâlâ 2020-04'ün taşınan değerini gösteriyor) —
bu, farklı kaynakların as-of günlerinin birbirinden bağımsız/rastgele
dağıldığının somut bir kanıtı; aynı takvim gününde bazı sütunlar "taze",
bazıları "taşınmış" olabilir. Bu tam olarak `_gercek_mi` bayraklarının
var olma nedenidir.

---

## 7. Açık Sorular / PM Onayı Gerekenler

1. **`..._referans_ay` yardımcı sütunlarının forward-fill edilmesi**
   (Bölüm 1) — görev talimatında açıkça istenmemiş bir yorumlayıcı
   ekti. Onay bekleniyor: bu tercih uygun mu, yoksa referans_ay
   sütunları da orijinal (yalnızca as-of günü dolu) haliyle mi
   kalmalıydı?
2. **`_gercek_mi` bayrağının anlamı iki farklı durumu tek bir "0" değerinde
   birleştiriyor:** (a) önceki ayın taşınan değeri VE (b) henüz hiç veri
   gelmemiş dönem (örn. `proxy_fiyat_cari_tl` için 2024-01 öncesi tüm
   günler). İkisini ayırt etmek gerekirse (örn. 3 durumlu bir kategori:
   gerçek / taşınmış / hiç-veri-yok) ayrı bir görev olarak ele alınabilir.
3. **Sonraki adım önerisi (başlatılmadı, yalnızca öneri):** bu iki
   tablo (as-of vs forward-fill) üzerinde karşılaştırmalı korelasyon
   analizi YAPILMADI (görev talimatının YAPMA listesine uygun) —
   istenirse hangi yaklaşımın modele daha uygun olduğunu görmek için
   ayrı bir görev olarak ele alınabilir.
