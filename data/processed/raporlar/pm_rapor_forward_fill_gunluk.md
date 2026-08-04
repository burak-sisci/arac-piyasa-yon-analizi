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

1. **`..._referans_ay` yardımcı sütunlarının forward-fill edilmesi —
   talimatta yoktu, benim yorumlayıcı eklemem.**
   Görev metni yalnızca "değer sütunlarını forward-fill et, bayrak
   ekle" diyordu; 10 grubun referans_ay sütunları (`noter_referans_ay`,
   `tufe_referans_ay` vb.) için açık bir talimat yoktu. Ben bunları da
   ileri doğru doldurdum, çünkü doldurulmasalar tabloda şöyle bir
   tutarsızlık oluşuyordu: `noter_devir_toplam_adet` sütunu 2020-06-15
   gibi bir ara günde dolu (561375.0) görünürken, `noter_referans_ay`
   aynı satırda NaN kalıyordu — yani "bu değer hangi aya ait?" sorusunun
   cevabı tablo içinde bulunamıyordu, kullanıcı bunu ayrıca hesaplamak
   zorunda kalıyordu.
   **İki seçenek ve sonuçları:**
   - **(A) Şu anki hal — referans_ay de forward-fill edilir.** Artı:
     tablo kendi başına okunabilir, her satırda "bu değer hangi ay
     verisi" açık. Eksi: `referans_ay` sütunu artık "bu satırda gerçek
     bir yayım oldu" anlamına gelmiyor — o bilgiyi taşıyan tek şey
     `_gercek_mi` bayrağı oldu; birisi referans_ay'ı tek başına (bayrağı
     kontrol etmeden) okursa yanlışlıkla "bu ayın verisi bugün açıklandı"
     sanabilir.
   - **(B) Alternatif — referans_ay orijinal haliyle (yalnızca as-of
     gününde dolu) bırakılır.** Artı: referans_ay'ın doluluğu tek
     başına "gerçek as-of günü" anlamına gelmeye devam eder, `_gercek_mi`
     bayrağıyla aynı bilgiyi iki kez taşımamış olur. Eksi: ara günlerde
     hangi ayın verisinin gösterildiğini bulmak için ayrı bir sorgu/join
     gerekir.
   Proje sahibinin onayı gereken nokta: (A) mı kalsın, yoksa script
   (B)'ye göre mi güncellensin? (Değişikliği yapmak tek satırlık bir
   düzenleme — script'in `AYLIK_CEYREKLIK_GRUPLAR` döngüsündeki
   `df[referans_ay_col] = df[referans_ay_col].ffill()` satırı
   kaldırılır.)

2. **`_gercek_mi` bayrağı iki farklı "0" durumunu birbirinden
   AYIRT ETMİYOR — bu, modelleme aşamasında yanıltıcı olabilir.**
   Bayrak yalnızca 1 (gerçek as-of günü) / 0 (gerçek değil) ikili
   değeri taşıyor, ama "0" aslında iki temelde farklı senaryoyu
   kapsıyor:
   - **(a) Taşınmış değer:** o ay için gerçek veri VAR ama bu spesifik
     gün onun as-of günü değil, önceki as-of'tan taşınmış (ör. yukarıdaki
     örnekte 2020-06-15, noter için).
   - **(b) Hiç veri yok:** kaynağın kendisi o tarihte henüz mevcut
     değildi, forward-fill'in dolduracağı bir "önceki değer" bile yoktu
     (NaN kaldı). Somut büyüklük — kaynak bazında hâlâ NaN kalan satır
     sayısı (4234 üzerinden): `proxy_fiyat_cari_tl` **3347/4234**
     (BETAM verisi ancak 2024-03-01'den itibaren var), `enag_aylik_degisim`
     **2223/4234** (ENAG serisi 2021-02-01'den başlıyor),
     `noter_devir_otomobil_adet` ve `brut_ucret_maas_endeksi_2021_100`
     her ikisi de **1127/4234** (ikisi de 2018-02-01'den başlıyor).
   Bu iki durumu ayırmadan `_gercek_mi=0` olan satırları toplu olarak
   "eski/güvenilmez" diye işaretlemek yanlış olur — (a) durumunda değer
   GERÇEK ve güncel (yalnızca o gün açıklanmamış), (b) durumunda ise
   değer YOK. Bir modelin bu ikisini karıştırması, örneğin
   `proxy_fiyat_cari_tl` için 2015-2023 arası NaN'ları yanlışlıkla
   "taşınmış eski değer" sanıp bir doldurma/imputation stratejisi
   uygulamasına yol açabilir.
   **Öneri (başlatılmadı, PM onayı gerekir):** `_gercek_mi` yerine
   3 durumlu bir kategori sütunu (`gercek` / `tasinmis` / `veri_yok`)
   üretmek; bu, ayrı bir görev olarak ele alınabilir, mevcut ikili
   bayrağı BOZMADAN (geriye dönük uyumluluk için) ek bir sütun olarak
   eklenebilir.

3. **Görev 25'in BETAM (proxy_fiyat) çakışma-çözümü, forward-fill
   tablosuna SESSİZCE miras kalıyor — bunun farkında olunmalı.**
   Hatırlatma (bkz. `pm_rapor_gunluk_karisik_frekans.md` Bölüm 6/madde 2):
   BETAM bazen iki referans ayını (ör. 2024-01 ve 2024-02) aynı yayım
   ayında birlikte açıklıyor; Görev 25'te bu çakışmalarda yalnızca EN
   GÜNCEL referans ayın değeri tutulup diğeri elendi. Bu script o
   kararı DEĞİŞTİRMEDEN kaynak tablodan okuyor — yani örneğin 2024-01'in
   kendi değeri (855781 TL değil, 860443 TL) bu forward-fill tablosunda
   HİÇBİR günde görünmüyor, doğrudan 2024-02'nin değerine atlanıyor.
   Bu, Görev 25'te onaylanan bir tasarım kararının ikinci bir tabloya
   sessizce yayılması anlamına geliyor — yanlış değil, ama PM'in
   bunun farkında olması ve gerekirse Görev 25'teki kararı yeniden
   değerlendirmesi (örn. "atlanan ay da ayrı bir sütunda saklansın mı")
   gerekebilir.

4. **Sonraki adım önerisi (başlatılmadı, yalnızca öneri):** bu iki
   tablo (as-of vs forward-fill) üzerinde karşılaştırmalı korelasyon
   analizi YAPILMADI (görev talimatının YAPMA listesine uygun) —
   istenirse hangi yaklaşımın modele daha uygun olduğunu (forward-fill'in
   yapay günlük varyans yaratıp yaratmadığı, as-of'un ise çok seyrek
   veri nedeniyle korelasyon gücünü düşürüp düşürmediği) görmek için
   ayrı bir görev olarak ele alınabilir.
