# PM Raporu — Model 12 BDDK Heuristik Ön-Eleme

**Tarih:** 2026-08-08

**Aşama:** Model 11 sonrası Seçenek 2 / BDDK cari-seri heuristik taraması

**Durum:** Tamamlandı — **ON_ELEME_ZAYIF / HEURISTIK**

**Karar yöneticisi:** Pusula (`claude-opus-5`, Opus/max)

**Uygulayıcı:** Rota-2

## 1. Ne Yapıldı

Pusula'nın sonuçlardan önce kilitlediği iki kollu Model 12 protokolü uygulandı.
Kontrol kolu yalnız Model 11 `m09.FEATURELAR` setini; test kolu aynı set ile
dört ön-kayıtlı BDDK taşıt kredisi dönüşümünü kullandı. İki kol aynı 50 aylık
etiket dizisi, seed=410, 1.000 permütasyon matrisi ve dört sabit model
konfigürasyonuyla çalıştırıldı.

Dört BDDK özelliği M−2 kesimindeki son yayımlanmış referans haftasından
konumsal 4/13/52 gözlem değişimleri ve bileşik reel 4-hafta değişimidir. Cari
veya M−1 bilgi kullanılmadı. Kontrol harness'i Model 11 değerlerini dört
konfigürasyonda da sıfır farkla yeniden üretti. RF/HGB doygun sayıldı ve karar
kapısına sokulmadı. Kilitli `2025-07..2026-06` testi açılmadı.

Önkayıt ve takvim denetim izi:

- İlk protokol commit'i: `061996c`.
- Cuma-dışı tatil haftası düzeltmesi: `8fa2ead`.
- Ağ sayacı düzeltmesi: `a99938b`.
- Tarih çifti tanı izi: `3349961`.
- Exact 3/11 uzun-bayram sözleşmesi: `cffe97b`.
- Tam koşu: 1.000 tekrar, tek thread, 538,7 saniye.

## 2. Sayısal Özet

- Resmî cari/revize BDDK serisi: **657 hafta**, `2014-01-03..2026-07-31`.
- Cache SHA-256: `4ED663DC373C6BB6C63A7A2D910D22408C574CF71210FFB9453E7EB087F030DE`;
  yüklemede doğrulandı.
- Ağ erişimi: 3 seri + 2 revizyon belgesi = **5/8**.
- Origin: **50**, `2021-03..2025-04`; her ay 4 snapshot, toplam 200 satır.
- Dört BDDK feature'ında eksik: **0**.
- M−1/M haftası kullanılan origin: **0**.
- Nominal aralıktan 7 günden fazla sapan 4/13/52 pencere: **0/0/0**.
- 3/11 uzun-tatil çiftini asimetrik kesen 4/13/52 pencere: **0/0/0**.
- Cuma-dışı referans haftası: **26**; tatil haritasıyla eşleşmeyen: **0**.
- Exact izinli ardışık aralık istisnası: **4/4 tüketildi**.
- Permütasyon: 1.000 × 4 konfigürasyon × 2 kol = **8.000 fit**.
- Kontrol harness farkı: dört modelde gözlenen ve null95 için **0**.

| Konfigürasyon | Kol 1 gözlenen | Kol 1 null95 | Kol 1 marj | Kol 2 gözlenen | Kol 2 null95 | Kol 2 marj | Δ marj | Kararda? |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Lojistik L2 C=0,1 | 0,2148 | 0,4450 | -0,2303 | 0,3794 | 0,5006 | -0,1211 | +0,1091 | Evet |
| Lojistik L2 C=1 | 0,1690 | 0,4684 | -0,2994 | 0,4936 | 0,5528 | -0,0592 | **+0,2402** | Evet |
| Sığ Random Forest | 0,9169 | 0,9155 | +0,0013 | 0,9690 | 0,9537 | +0,0153 | +0,0140 | Hayır; doygun |
| Sığ HistGradientBoosting | 1,0000 | 1,0000 | 0,0000 | 1,0000 | 1,0000 | 0,0000 | 0,0000 | Hayır; doygun |

Ön-kayıt hükmü **ON_ELEME_ZAYIF / HEURISTIK**tir. Hiçbir lojistik test-kolu
marjı `+0,15` geçiş kapısını sağlamadı. C=1 kolunun `delta_marj=+0,2402`
değeri `+0,15` zayıf-işaret kapısını sağladı. Bu nedenle BDDK terfi etmedi;
önkayıtlı otomatik dal C=0,01 kapasite-düşürülmüş tekrardır.

## 3. Karşılaşılan Sorunlar (Saklanmaz)

1. İlk koşu, 26 tatil haftasının Cuma yerine önceki iş gününde kapanması
   nedeniyle sonuç üretmeden durdu. Pusula bunun yöntem değil yanlış olgusal
   kabul olduğunu onayladı; tekillik/sıralılık/aralık/tatil denetimi eklendi.
2. İkinci koşu, iki uzun Kurban Bayramı haftasındaki `3+11` günlük çiftler
   nedeniyle yine model fitlerinden önce durdu. Yalnız dört exact tuple beyaz
   listeye alındı; genel kapı genişletilmedi.
3. Üçüncü seri çağrısı son izinli çağrıydı. Yanıt sonuç görülmeden cache'e
   kaydedildi; sonraki koşu hash doğrulamalı cache kullandı. Dördüncü çağrı
   yapılmadı.
4. Pusula oturum kotası 23.00'e kadar doluydu. Önemli takvim kararı Pusula
   olmadan alınmadı; kota yenilenince aynı oturum Opus/max ile devam etti.
5. Pusula, 2021 uzun-tatil çiftinin bazı pencerelerde asimetrik kesilebileceğini
   öngördü. Saf aritmetik denetim gerçek 50 originde 4/13/52 için sıfır buldu;
   beklentiye uydurulmadı ve sonuç aynen raporlandı.
6. Proje `.venv312` ortamında Jupyter yoktu; paket kurulmadı. Notebook sistemde
   zaten bulunan Jupyter/Python 3.14 kernel'iyle başarıyla çalıştırıldı.
7. İlk `python -m pytest` denemesinde sistem Python'unda pytest yoktu. Paket
   kurulmadan mevcut `.venv312` kullanıldı; tam paket sonunda 83/83 geçti.
8. Revizyon takvimi sayfası inceleme sırasında HTTP 502 döndürdü. Kalem düzeyi
   revizyon istisnası veya büyüklük sınırı belgelenemediği için kesinlik
   `HEURISTIK` kaldı.
9. Cari/revize seri ilk-yayım vintajı değildir. Sonuç temiz vintajın aynı
   davranacağını kanıtlamaz.

## 4. Veri Örneği (Ham, İlk/Son Birkaç Satır)

Hash-kilitli resmî BDDK cache'inin ilk ve son satırları:

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

İlk ve son origin feature örneği:

| Hedef ay | M−2 çapa | 4h % | 13h % | 52h % | Reel 4h % | Aralık gün 4/13/52 |
|---|---|---:|---:|---:|---:|---|
| 2021-03 | 2021-01-29 | 1,2919 | 6,8140 | 71,0657 | -0,3834 | 29 / 91 / 364 |
| 2025-04 | 2025-02-28 | -3,9140 | -9,0189 | -26,7791 | -6,0498 | 28 / 91 / 364 |

Ham seri, feature CSV ve sonuç JSON'u yeniden üretilebilir fakat Git'e girmeyen
`data/processed/model/` çıktılarıdır. Bu PM raporu ve çalıştırılmış notebook
denetim izi olarak Git'e girer.

## 5. Varsayımlar ve Kararlar (K/N Kararlarına Uygunluk)

- Target `noter_devir_otomobil_adet`, sınıflar `down/stable/up` ve ±%5 kapalı
  stable bandı değişmedi.
- Haftalık güncellenen cari-ay nowcast ve M−2 bilgi disiplini korundu.
- BDDK serisi yalnız taşıt kredisi bakiye/kullanım vekilidir; kredi onay oranı
  diye sunulmadı.
- Cari/revize seri ilk-yayım vintajı yerine geçirilmedi; kesinlik etiketi
  `HEURISTIK`tir.
- İki kol aynı etiketler, seed, permütasyon ve fit prosedürünü kullandı.
- RF/HGB doygun sonuçları karar kapısından dışlandı.
- `ON_ELEME_ZAYIF` OOF performans, üretim becerisi veya terfi değildir.
- Kilitli test açılmadı; yeni K/N kararı ve hedef sözleşmesi yazılmadı.
- Kullanıcının mevcut dirty/untracked dosyaları değiştirilmedi veya stage
  edilmedi.

## 6. Açık Sorular / PM Onayı Gerekenler

Bu aşamanın ön-kayıtlı kararı yeni kullanıcı seçimi gerektirmeden C=0,01
kapasite-düşürülmüş iki kollu tekrara yönlendirir. Açık metodolojik soru,
iyileşmenin daha düşük kapasiteli lojistik modelde de en az `+0,15` delta marj
üretip üretmediğidir. Bu tekrar da temiz vintaj veya OOF becerisi kanıtlamaz.

Kullanıcı kararı gerektirecek durumlar değişmemiştir: hedef/sınıf/ufuk
sözleşmesini değiştirmek, ücretli/kimlikli vintaj temini, dış kuruma mesaj veya
kilitli testi açmak. Bunların hiçbiri bu aşamada yapılmadı.

## 7. Önerilen Sonraki Adım (Başlatılmaz, Yalnızca Önerilir)

Önkayıttaki `ON_ELEME_ZAYIF` dalı uygulanarak yalnız lojistik L2 C=0,01 eklenen
kapasite-düşürülmüş iki kollu tekrar ayrı bir promptta sonuçlardan önce
kilitlensin. Aynı 50 origin, dört BDDK feature'ı, seed=410, ortak 1.000
permütasyon, hash-kilitli cache ve yorum sınırı korunsun. Tekrar sonucu ayrı PM
raporuyla kapatılmadan vintaj temini veya rolling-origin aşamasına geçilmesin.
