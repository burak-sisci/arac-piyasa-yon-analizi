# PM Raporu — DF-A Ders Kitabı Notebook'u

**Tarih:** 2026-08-03
**Kaynak dosya:** `notebooks/df_a_ders_kitabi.ipynb`
**Prompt arşivi:** `prompts/23_df_a_ders_kitabi_notebook_prompt.md`
**Kapsam:** Yalnızca eğitim amaçlı bir notebook üretimi. Hedef/model
değiştirilmedi, kalıcı veri dosyaları değiştirilmedi (notebook salt-okunur
bir keşif aracıdır).

---

## 1. Notebook Yapısı — Kaç Bölüm/Hücre

**Toplam 82 hücre: 47 markdown (anlatım/yorum) + 35 kod.**

9 ana bölüm + başlık:

| Bölüm | İçerik |
|---|---|
| Başlık | Notebook'un amacı, kullanım kılavuzu |
| 1 | DF-A ne, neden var, DF-B ile farkı, ilk bakış (`head()`, boyut) |
| 2 | Sütun sütun tanışma — her sütun için describe() + zaman grafiği + yorum |
| 3 | 📖 Temel Kavram: Zaman Serisi, Trend, Mevsimsellik |
| 4 | Hedef: Noter Devir Adedi — yıllık özet, grafik, "hep yukarı tuzağı" tartışması |
| 5 | 📖 Temel Kavram: Korelasyon, Sahte (spurious) korelasyon |
| 6 | Ham seviye korelasyon matrisi + ısı haritası |
| 7 | 📖 Temel Kavram: Aylık değişim / log-değişim, log-değişim hesaplama |
| 8 | Log-değişim korelasyonu + Bölüm 6 ile karşılaştırma + noter devri odaklı tablo |
| 9 | Stratejik çıkarımlar (karar değil, bulgu özeti) |

Tüm 35 kod hücresi, notebook'un kendisi dışında ayrıca sırayla çalıştırılıp
**hatasız çalıştığı doğrulandı** — markdown yorum hücrelerindeki sayılar,
gerçek kod çıktılarıyla birebir eşleşiyor.

---

## 2. Ele Alınan Sütunlar (Gerçek, Güncel Liste)

Notebook yazılmadan önce DF-A'nın (`df_a_kapsama_testli_v2.csv`) GÜNCEL
sütun listesi kodla okunup doğrulandı: **102 satır × 16 sütun**,
2018-01 → 2026-06.

Bölüm 2'de tam describe()+grafik+yorum ile ele alınan 13 sayısal sütun:
`usdtry_aysonu`, `usdtry_ortalama`, `tufe_endeks`, `tufe_aylik_degisim`,
`tufe_yillik_degisim`, `tasit_kredisi_faiz`, `politika_faizi`,
`odmd_otomobil_adet`, `osd_binek_adet`, `tuketici_guven_endeksi`,
`otomobil_satinalma_ihtimali_endeksi`, `noter_devir_toplam_adet`,
`noter_devir_otomobil_adet`.

2 "metadata" sütunu (daha hafif ele alındı, describe/grafik yerine kısa
açıklama): `tufe_yayim_tarihi` (tarih metni), `alim_gucu_ceyrek` (artık
"yetim" kategorik etiket — bkz. Bölüm 4 aşağıda).

**`referans_ayi`** doğal olarak zaman ekseni/indeks olarak kullanıldı,
ayrıca ele alınmadı.

**Silinmiş sütunlara HİÇBİR referans yok** — talimatın kesin kuralı
(`otv_aciklama`, `proxy_yon_*`, `kullanilan_sigma_*`, `odmd_toplam_adet`,
`odmd_hta_adet`, `osd_binek_kamyonet_toplam_adet`, `osd_kamyonet_adet`,
`erisim_endeksi`, `brut_ucret_maas_endeksi_2021_100`, `otv_event_ay_mi`,
`otv_ay_farki_en_yakin_olay`) doğrulandı — bunların hiçbiri kodla okunan
güncel sütun listesinde zaten yoktu.

---

## 3. En Çarpıcı Bulgular

1. **Ham seviye korelasyonun büyük kısmı "sahte" çıkıyor.**
   `usdtry_ortalama ↔ tufe_endeks` ham seviyede r=0,984 iken, log-değişime
   geçince r=0,44'e düşüyor; `usdtry_aysonu ↔ tufe_endeks` ise neredeyse
   tamamen kayboluyor. Bu, notebook'un Bölüm 5'te öğrettiği "sahte
   korelasyon" kavramının somut, kendi verimizden gelen bir kanıtı.
2. **Noter devriyle en tutarlı (log-değişimde de ayakta kalan) ilişkiler:
   `osd_binek_adet`** (yerli üretim, ham seviyede görünmüyordu ama
   log-değişimde r≈0,60 ile ortaya çıktı) **ve `odmd_otomobil_adet`**
   (sıfır km satış, r≈0,46). Kur/TÜFE/faiz gibi makro göstergelerin
   noter devriyle log-değişim ilişkisi ise çok zayıf (|r|<0,2).
3. **Noter devri "hep yukarı" tuzağına kur/TÜFE kadar açık değil.**
   Yıllık ortalamalar 2018'den 2025'e hafif bir yükseliş gösteriyor
   (644 bin → 934 bin) ama yıl-içi dalgalanma çok büyük (ör. 2020'de
   348 bin - 1.097 bin arası) — kur/TÜFE gibi neredeyse hiç düşmeyen
   seriler değil, bu yüzden "her zaman artacak" tahmini burada o kadar
   kolay doğru çıkmaz.

---

## 4. Karşılaşılan Sorunlar

1. **Notebook'un kendisi çalıştırılamadı (kernel yok)** — bunun yerine
   tüm 35 kod hücresi, notebook dışında ayrı bir Python oturumunda
   sırayla çalıştırılıp doğrulandı; markdown yorum metinleri bu
   doğrulanmış gerçek sayılara dayanıyor (varsayım/tahmin değil).
2. **`tufe_aylik_degisim`/`tufe_yillik_degisim` log-değişim setine bilinçli
   olarak dahil edilmedi** — bunlar zaten birer "değişim" ölçüsü olduğu
   için tekrar log-değişimi almak (bir değişimin değişimi) kafa
   karıştırıcı ve neredeyse totolojik bir sonuç (`tufe_endeks`'in kendi
   log-değişimiyle r≈1,0) üretiyordu. Bu, notebook içinde açıkça
   gerekçelendirildi.
3. Bunun dışında teknik bir sorun çıkmadı.

---

## 5. Açık Sorular / PM Onayı Gerekenler

1. **`alim_gucu_ceyrek` hâlâ "yetim" — silinmesi bekleniyor** (önceki
   PM raporunda da açık soru olarak duruyordu). Notebook bu durumu
   şeffafça açıklıyor ama kalıcı çözüm proje sahibine ait.
2. **Tüketici güveni endeksinin noter devriyle neredeyse hiç ilişkisi
   olmaması** (r≈-0,03, hem ham hem log-değişimde) sezgiye aykırı bir
   bulgu — ekip lideriyle ayrıca tartışılmaya değer.
3. **Notebook'un kapsamı yalnızca DF-A'yla sınırlı** — DF-B (BETAM/ENAG
   dahil) için benzer bir "ders kitabı" istenirse ayrı bir görev olarak
   ele alınmalı.
