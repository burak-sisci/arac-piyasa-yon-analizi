# PM Raporu — DF-B Ders Kitabı Notebook'u

**Tarih:** 2026-08-03
**Kaynak dosya:** `notebooks/df_b_ders_kitabi.ipynb`
**Prompt arşivi:** `prompts/24_df_b_ders_kitabi_notebook_prompt.md`
**Kapsam:** Yalnızca eğitim amaçlı bir notebook üretimi (DF-A notebook'unun
— 23 numaralı görev — kardeşi). Hedef/model değiştirilmedi, kalıcı veri
dosyaları değiştirilmedi.

---

## 1. Notebook Yapısı — Kaç Bölüm/Hücre

**Toplam 41 hücre: 23 markdown (anlatım/yorum) + 18 kod.** (DF-A
notebook'unun 82 hücresinden belirgin şekilde daha kısa — talimatın
istediği gibi, DF-A'da zaten öğretilmiş temel kavramlar burada
TEKRARLANMADI, yalnızca DF-B'ye özgü konulara odaklanıldı.)

7 ana bölüm + başlık:

| Bölüm | İçerik |
|---|---|
| Başlık | DF-A notebook'unun kardeşi olduğu, temel kavramların tekrar edilmeyeceği belirtildi |
| 1 | DF-B ne, DF-A'dan farkı (karşılaştırma tablosu), ilk bakış |
| 2 | 📖 Temel Kavram: Neden iki ayrı tablo (arkadaş örneği) |
| 3 | Yeni sütunlarla tanışma — BETAM'ın 3 göstergesi (eksik ay işaretlemeli grafik), 4 türetilmiş değişim sütunu, ENAG'ın 2 göstergesi |
| 4 | 📖 Temel Kavram: Az gözlemle çalışmanın riski (yazı-tura örneği) |
| 5 | TÜİK vs ENAG karşılaştırması (üst üste grafik + fark istatistiği) |
| 6 | Log-değişim korelasyon matrisi (DF-A yöntemi kısaca hatırlatılıp uygulandı) + noter devri odaklı tablo |
| 7 | Stratejik çıkarımlar + DF-A/DF-B tutarlılık karşılaştırması |

Tüm 18 kod hücresi, notebook dışında ayrıca sırayla çalıştırılıp
**hatasız çalıştığı doğrulandı** — yorum metinlerindeki sayılar gerçek
kod çıktılarıyla birebir eşleşiyor.

---

## 2. Ele Alınan Yeni Sütunlar (Gerçek, Güncel Liste)

Notebook yazılmadan önce DF-B'nin (`df_b_zengin_2024_bugun_v2.csv`)
GÜNCEL sütun listesi kodla okunup doğrulandı: **30 satır × 25 sütun**,
2024-01 → 2026-06.

DF-A'da OLMAYAN, yalnızca DF-B'ye özgü 9 sütun tam işlendi:
`proxy_dom_gun`, `proxy_satis_orani_pct`, `proxy_fiyat_cari_tl` (BETAM'ın
3 ham göstergesi — describe + eksik-ay-işaretli grafik + yorum),
`proxy_nominal_aylik_pct`, `proxy_reel_aylik_pct`, `proxy_aylik_log_degisim`,
`proxy_reel_aylik_log_degisim` (fiyattan türetilen 4 değişim sütunu, birlikte
ele alındı), `enag_aylik`, `enag_yillik` (ENAG'ın 2 göstergesi).

DF-A ile ORTAK sütunlar (kur, TÜFE, faiz, ODMD, OSD, tüketici güveni,
noter devri, `alim_gucu_ceyrek`) yalnızca isim olarak anıldı, tekrar
detaylandırılmadı — talimata uygun.

**Silinmiş sütunlara HİÇBİR referans yok** — DF-A notebook'unda doğrulanan
aynı 11 sütun (`otv_aciklama`, `proxy_yon_*`, `kullanilan_sigma_*`,
`odmd_toplam_adet`, `odmd_hta_adet`, `osd_binek_kamyonet_toplam_adet`,
`osd_kamyonet_adet`, `erisim_endeksi`, `brut_ucret_maas_endeksi_2021_100`,
`otv_event_ay_mi`, `otv_ay_farki_en_yakin_olay`) DF-B'nin kodla okunan
güncel listesinde de yoktu.

---

## 3. DF-A ile Tutarlılık Karşılaştırması

DF-A ve DF-B'de ORTAK olan iki özelliğin (`odmd_otomobil_adet`,
`osd_binek_adet`) noter devriyle log-değişim korelasyonu karşılaştırıldı:

| Özellik | DF-A'da r (n=100) | DF-B'de r (n=24) | Sonuç |
|---|---|---|---|
| `odmd_otomobil_adet` | ≈0,46 | ≈0,44 | **Çok tutarlı** — neredeyse aynı büyüklük, aynı yön |
| `osd_binek_adet` | ≈0,60 | ≈0,43 | Aynı yön (pozitif) ama büyüklük farklı |

**Yorum:** `odmd_otomobil_adet`'in iki bağımsız tabloda/pencerede benzer
bir ilişki göstermesi, projenin bu bulguya olan güvenini artıran bir
işaret. `osd_binek_adet`'in yönü tutarlı ama büyüklüğü DF-B'nin küçük
örneklemi (n=24) nedeniyle farklı çıkmış olabilir.

---

## 4. En Çarpıcı Bulgular

1. **`proxy_satis_orani_pct` (BETAM'ın satış oranı), noter devriyle en
   güçlü ilişkiyi gösteren özellik** (r≈0,83-0,87) — iki BAĞIMSIZ
   kaynağın (TÜİK noter devri, BETAM ilan-satış oranı) aynı piyasa
   hareketliliğini yakaladığına işaret ediyor.
2. **Nominal fiyat değişimi ile noter devri arasında BEKLENMEDİK bir
   NEGATİF ilişki** (r≈-0,53/-0,55) — sezgiye aykırı (normalde "fiyat
   artıyorsa piyasa canlı" beklenir), ama n≈24-25 ile hesaplandığı için
   temkinli okunmalı; ekip lideriyle tartışılmaya değer.
3. **TÜİK-ENAG enflasyon farkı, 2024-01'deki 64,25 puandan 2026-06'daki
   19,39 puana kadar sürekli ve neredeyse monoton daralmış** — bu
   trendin yorumu (hangi ölçümün diğerine yaklaştığı) bilinçli olarak
   yapılmadı, yalnızca gözlem raporlandı.

---

## 5. Karşılaşılan Sorunlar

1. **`tufe_endeks` ve `proxy_fiyat_cari_tl`'nin log-değişim matrisine
   dahil edilme şekli iki aşamalı düzeltme gerektirdi:** İlk denemede bu
   iki seviye sütunun YENİ log-değişimini hesaplayıp, zaten var olan
   `tufe_aylik_degisim`/`proxy_aylik_log_degisim` sütunlarıyla BİRLİKTE
   matrise koymuştum — bu, aynı şeyi iki kez ölçen totolojik bir çift
   (r≈1,0) üretti. Fark edilip düzeltildi: bu iki sütun için YENİ
   log-değişim hesaplanmadı, yalnızca zaten var olan değişim sütunları
   (`tufe_aylik_degisim`, `proxy_aylik_log_degisim` vb.) kullanıldı.
2. **Notebook'un kendisi çalıştırılamadı (kernel yok)** — DF-A
   notebook'unda olduğu gibi, tüm kod hücreleri ayrı bir Python
   oturumunda çalıştırılıp doğrulandı.
3. Bunun dışında teknik bir sorun çıkmadı.

---

## 6. Açık Sorular / PM Onayı Gerekenler

1. **Nominal fiyat değişimi ile noter devri arasındaki negatif ilişkinin
   (bkz. Bölüm 4) ekonomik bir açıklaması var mı?** Notebook yalnızca
   bulguyu raporluyor, yorumlamıyor — ekip lideri toplantısında ele
   alınmaya değer.
2. **TÜİK-ENAG farkının daralma trendinin yorumu** (Bölüm 5) bilinçli
   olarak yapılmadı — proje sahibinin/ekip liderinin değerlendirmesi
   gereken bir nokta.
3. **`alim_gucu_ceyrek` hâlâ "yetim"** (önceki raporlarda da açık soru) —
   bu notebook'ta da yalnızca isim olarak anıldı, silinmedi.
4. **İki notebook (DF-A, DF-B) artık mevcut** — üçüncü bir "birleşik"
   ders kitabı (ikisini karşılaştıran, tek bir yerde toplayan) istenirse
   ayrı bir görev olarak ele alınabilir.
