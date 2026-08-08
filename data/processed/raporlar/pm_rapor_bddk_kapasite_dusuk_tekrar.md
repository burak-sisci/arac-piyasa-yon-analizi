# PM Raporu — Model 13 BDDK C=0,01 Kapasite-Düşürülmüş Tekrar

**Tarih:** 2026-08-08

**Aşama:** Model 12 `ON_ELEME_ZAYIF` terminal tekrarı

**Durum:** Tamamlandı — **KAPASITE_DUSUK_ISARET_YOK / HEURISTIK**

**Karar yöneticisi:** Pusula (`claude-opus-5`, Opus/max)

**Uygulayıcı:** Rota-2

## 1. Ne Yapıldı

Prompt 41'in `f2a9132` commit'inde sonuçlardan önce kilitlenen sözleşmesi
uygulandı. Model 12'nin özgün dört konfigürasyonu harness/bağlam için yeniden
koşuldu; beşinci ve tek yeni konfigürasyon olarak lojistik L2 C=0,01 eklendi.
Kontrol kolu 10 Model 09 feature'ı, test kolu aynı 10 feature ile aynı dört BDDK
dönüşümünü kullandı. İki kol aynı 50 origin, seed=410 ve 1.000 permütasyon
matrisini paylaştı.

Bağlayıcı karar yalnız C=0,01 çiftinden üretildi. Özgün C=1'in Model 12'deki
zayıf deltası yeniden karar kapısına sokulmadı; böylece tekrar dalı terminal
olarak kapatıldı. Hash-kilitli BDDK cache yeniden doğrulandı, ağ çağrısı
yapılmadı ve kilitli test açılmadı.

## 2. Sayısal Özet

- Origin/snapshot: 50 ay × 4 = 200 satır; `2021-03..2025-04`.
- Kontrol/test feature sayısı: **10 / 14**; nominal artış **%40**.
- Konfigürasyon: 4 özgün + 1 yeni C=0,01 = **5**.
- Permütasyon: 1.000 × 5 × 2 = **10.000 fit**.
- Seed/thread: 410 / 1.
- Süre: **555,8 saniye**.
- Yeni HTTP çağrısı: **0**; cache SHA-256 doğrulandı.
- Özgün dört kontrol harness farkı: tüm alanlarda **0**.
- Özgün dört test-kolu Model 12 yeniden üretim farkı: tüm alanlarda **0**.
- Manipülasyon: C=0,01 kontrol null95 `0,421986 < 0,445034`; **geçti**.
- C=0,01 kol2 marjı: **-0,181477**; geçiş eşiği `+0,15` sağlanmadı.
- C=0,01 delta marjı: **+0,026848**; zayıf-teyit eşiği `+0,15` sağlanmadı.

| Config | Kol1 gözlenen | Kol2 gözlenen | Δ gözlenen | Kol1 null95 | Kol2 null95 | Δ null95 | Kol1 marj | Kol2 marj | Δ marj |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Lojistik C=0,01 (yeni baseline) | 0,2137 | 0,2713 | +0,0577 | 0,4220 | 0,4528 | +0,0308 | -0,2083 | -0,1815 | +0,0268 |
| Lojistik C=0,1 | 0,2148 | 0,3794 | +0,1646 | 0,4450 | 0,5006 | +0,0555 | -0,2303 | -0,1211 | +0,1091 |
| Lojistik C=1 | 0,1690 | 0,4936 | +0,3246 | 0,4684 | 0,5528 | +0,0844 | -0,2994 | -0,0592 | +0,2402 |
| Sığ RF | 0,9169 | 0,9690 | +0,0522 | 0,9155 | 0,9537 | +0,0382 | +0,0013 | +0,0153 | +0,0140 |
| Sığ HGB | 1,0000 | 1,0000 | 0,0000 | 1,0000 | 1,0000 | 0,0000 | 0,0000 | 0,0000 | 0,0000 |

C=0,01'de gözlenen artış `+0,0577`, null95 artışı `+0,0308`'den büyüktür;
delta marj `+0,0268` iyileşmiştir, **ancak mutlak kol2 marjı hâlâ -0,1815'tir**.
Yani gerçek etiket uyumu karıştırılmış etiket ezberinin 95. yüzdeliğinin altında
ve `+0,15` mutlak/delta kapılarından uzaktır. Bu nedenle terminal hüküm
`KAPASITE_DUSUK_ISARET_YOK / HEURISTIK`tir.

## 3. Karşılaşılan Sorunlar (Saklanmaz)

1. Prompt 41 yazılmadan önce özgün C=1'in deterministik zayıf deltayı yeniden
   ateşleyip sonsuz döngü yaratacağı fark edildi. Pusula spesifikasyon hatasını
   kabul etti; hüküm yalnız yeni C=0,01 çiftine bağlandı.
2. C=0,01'in Model 11 harness referansı yoktur. Sonuç açıkça `yeni baseline`
   olarak etiketlendi; özgün dört config harness'iyle karıştırılmadı.
3. Nominal feature sayısı 10'dan 14'e (%40) çıktı. Bu nedenle yalnız gözlenen
   artış okunmadı; null95 artışı ayrı raporlandı.
4. Kapasite manipülasyonu gerçekten null95'i düşürdü, fakat BDDK eklenince
   null95 yeniden `0,4528`'e yükseldi. Gözlenen daha fazla yükselse de net delta
   `+0,0268` ile eşik altında kaldı.
5. Cari/revize BDDK serisi ilk-yayım vintajı değildir; `HEURISTIK` etiketi
   kaldırılamadı.
6. Hesap 10.000 fit nedeniyle 555,8 saniye sürdü; 40 dakika stop sınırı
   aşılmadı ve tekrar sayısı azaltılmadı.
7. Kullanıcı çalışma ağacındaki dört notebook ve diğer untracked dosyalar
   korunarak yalnız bu aşama artefaktları üretildi.

## 4. Veri Örneği (Ham, İlk/Son Birkaç Satır)

Model 13 yeni veri çekmedi. Model 12'de hash-kilitlenen resmî cache yeniden
kullanıldı:

```text
referans_hafta,bakiye_milyon_tl
2014-01-03,8613.848
2014-01-10,8574.275
2014-01-17,8526.536
...
2026-07-17,41429.427
2026-07-24,42080.832
2026-07-31,42112.122
```

C=0,01 sonuç satırı:

```text
kol1: gozlenen=0.2136618826 null95=0.4219864222 marj=-0.2083245396
kol2: gozlenen=0.2713450196 null95=0.4528216193 marj=-0.1814765997
delta_marj=+0.0268479399
```

Sonuç JSON'u `data/processed/model/model_13_bddk_c001_ozet.json` altında
yeniden üretilebilir, Git'e girmeyen çalışma çıktısıdır.

## 5. Varsayımlar ve Kararlar (K/N Kararlarına Uygunluk)

- Target, üç sınıf, ±%5 bandı ve cari-ay nowcast sözleşmesi değişmedi.
- M−2 bilgi disiplini, 50 origin ve iki aylık embargo korundu.
- BDDK cache hash'i yüklemede doğrulandı; yeni ağ çağrısı yapılmadı.
- Yeni feature veya model ailesi eklenmedi; yalnız önkayıtlı C=0,01 eklendi.
- Özgün dört config karar dışı harness/bağlam rolünde kaldı.
- RF/HGB doygun sonuçları karar kapısına girmedi.
- Daha fazla C taraması (`C=0,001` dahil) yasaktır ve yapılmadı.
- `ISARET_YOK`, BDDK'nın ekonomik olarak sinyalsiz olduğu anlamına gelmez.
- Kilitli test açılmadı; performans/terfi iddiası kurulmadı.

## 6. Açık Sorular / PM Onayı Gerekenler

Bu aşamanın terminal dalı yeni kullanıcı kararı gerektirmeden BDDK'nın
önceliğini düşürür ve Prompt 38 kalıbında yeni, sınırlı masa başı taramasına
geçer. BDDK kapanmaz; kamuya açık izinli ilk-yayım vintajı veya revizyona-kapalı
kardeş gösterge ortaya çıkarsa **normal** yeniden-açma önceliğine sahiptir.

Ücretli/kimlikli vintaj temini, dış kuruma mesaj, hedef/sınıf/ufuk değişikliği
ve kilitli test erişimi hâlâ kullanıcı gerektirir; hiçbiri yapılmadı.

## 7. Önerilen Sonraki Adım (Başlatılmaz, Yalnızca Önerilir)

Prompt 38 kalıbıyla en fazla üç adaylı yeni masa başı taraması ön-kaydedilsin.
İlk-yayımı nihai değer olan, yapısı gereği revizyona kapalı ve 50 origin için
M−2 anında erişilebilir seriler önceliklendirilsin. Önceki BDDK/BETAM/Google
Trends kartları yeniden taranmasın; yeni veri veya model ancak masa başı kapıyı
geçen aday için ayrı küçük aşamada başlatılsın.
