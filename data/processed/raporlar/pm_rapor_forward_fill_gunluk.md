# PM Raporu — Takvim-Ayı Bazlı Genişletilmiş Günlük Tablo (Görev 26)

**Tarih:** 2026-08-04 (2026-08-04'te proje sahibinin düzeltmesiyle
güncellendi)
**Prompt arşivi:** `prompts/veri/26_forward_fill_gunluk_tablo_prompt.md`
**Kaynak script:** `scripts/veri/genisletme_26_forward_fill_gunluk.py`
**Girdi:** `data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv`
(25 numaralı görevin çıktısı — yalnızca günlük/ÖTV/takvim sütunları için
kullanıldı, **değiştirilmedi**) + `data/raw/{altintry,tufe,enag,
noter_devir,odmd,osd,tuketici_guveni,proxy_fiyat,alim_gucu,faiz}` (aylık/
çeyreklik kaynakların kendi ham dosyaları)
**Çıktı:** `data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv`
(git-dışı, yalnızca kod + bu rapor commit'lenir)

---

## ÖNEMLİ NOT — TASARIM DÜZELTMESİ

Bu görevin ilk versiyonunda "forward-fill"i, 25 numaralı görevin as-of
(yayım) tarihinden itibaren bir sonraki yayım tarihine kadar değeri ileri
taşıma olarak yorumlamıştım. Proje sahibi bunun yanlış olduğunu belirtti
ve doğru tanımı netleştirdi: **her referans ayın değeri, doğrudan O
REFERANS AYIN KENDİ TAKVİM GÜNLERİNE yazılır — yayım/as-of tarihinin hiç
önemi yok.** Örnek: Mayıs ayına ait bir değer, Mayıs'ın 1'inden 31'ine
kadar tüm günlere yazılır; bu değerin gerçekte hangi ayda açıklandığı
(Haziran başı gibi) bu tabloda dikkate alınmaz.

Script tamamen bu düzeltilmiş mantığa göre yeniden yazıldı. Ayrıca, proje
sahibinin talebiyle ilk versiyondaki `_gercek_mi` bayrak sütunları
TAMAMEN KALDIRILDI (korelasyon hazırlığı için gereksiz/uygunsuz
bulundu).

---

## 1. Ne Yapıldı

25 numaralı görevin tablosu (`df_gunluk_karisik_frekans_2015_bugun.csv`)
**değiştirilmedi**. Bu tablodan yalnızca zaten günlük olan sütunlar
(`usdtry_*`, `eurtry_*`), olay-bazlı ÖTV sütunları ve takvim sütunları
aynen alındı.

Aylık/çeyreklik 10 kaynak grubu (altın, TÜFE, ENAG, noter devri, ODMD,
OSD, tüketici güveni, proxy fiyat/dom/satış oranı, alım gücü, faiz) için
**kendi ham `data/raw/...` dosyalarından doğrudan okuma** yapıldı: her
kaynağın `referans_ayi` sütunu (ör. "2020-06") ile günlük tablonun
takvim ayı ("YYYY-MM" biçiminde) eşleştirilip, o referans ayın değeri
kendi ayının TÜM günlerine yazıldı. Yayım/as-of tarihi bu işlemde HİÇ
kullanılmadı.

**Dokunulmayanlar (aynen kopyalandı):** `usdtry_*`, `eurtry_*` (zaten
günlük), `otv_referans_ay`/`otv_aciklama`/`otv_event_gunu_mu` (olay-bazlı,
takvim-ayı mantığı uygulanmaz), takvim sütunları (`yil, ay, gun, ceyrek,
haftanin_gunu, yilin_gunu`), `tarih`.

**[PROAKTİF BULGU] BETAM (proxy_fiyat) verisinde daha önce kaybolan 2 ay
geri kazanıldı.** 25 numaralı görevde, BETAM'ın bazı ayları aynı yayım
gününde birlikte açıklaması nedeniyle (2024-01/2024-02 ikisi de
2024-03'te, 2024-03/2024-04 ikisi de 2024-05'te yayımlanmış) o tabloda
yalnızca en güncel referans ayın değeri tutulmuş, diğeri elenmişti.
Bu görevde yayım tarihine hiç bakılmadığı için (doğrudan referans_ayi
kullanıldığı için) bu çakışma yapısal olarak ORTADAN KALKTI —
**2024-01 ve 2024-03'ün kendi gerçek değerleri artık bu tabloda mevcut**
(kodla doğrulandı, bkz. Bölüm 3).

---

## 2. Yeni Tablo Boyutu

**4234 satır × 48 sütun** — 25 numaralı görevle SÜTUN SAYISI AYNI (bayrak
sütunu eklenmedi, proje sahibinin talebiyle). Sütun sırası da kaynak
tabloyla birebir aynı tutuldu (okunabilirlik/karşılaştırma için).

---

## 3. Doğrulama Sonucu

**Satır sayısı teyidi:** 4234 satır — 25 numaralı görevle birebir aynı,
`tarih` sütunu tekil (tekrar yok).

**3 örnek ay** (`noter_devir_toplam_adet`, ayın TÜM günlerinde tek ve
aynı değer, aylar arasında karışma yok):

| Ay | Ayın tüm günlerindeki değer | Benzersiz değer sayısı |
|---|---|---|
| 2016-06 | 578750.0 | 1 |
| 2020-06 | 1097112.0 | 1 |
| 2026-06 | 941964.0 | 1 |

**Ay değişiminde sızıntı kontrolü** — 2020-01 vs 2020-02 vs 2020-03
(`noter_devir_toplam_adet`): sırasıyla 856697.0 / 843550.0 / 720025.0 —
her ay kendi farklı değerini taşıyor, önceki ayın değeri bir sonraki aya
SIZMIYOR.

**BETAM geri kazanım teyidi** (`proxy_fiyat_cari_tl`, 2024-01..2024-04):

| Ay | Değer |
|---|---|
| 2024-01 | 860443.0 (25 numaralı tabloda YOKTU, şimdi geri kazanıldı) |
| 2024-02 | 855781.0 |
| 2024-03 | 859035.0 (25 numaralı tabloda YOKTU, şimdi geri kazanıldı) |
| 2024-04 | 867813.0 |

---

## 4. Doluluk Karşılaştırma Tablosu (Eski as-of-tek-gün vs Yeni takvim-ayı)

| Sütun | Eski (as-of-tek-gün) | Yeni (takvim-ayı) |
|---|---|---|
| altin_gram_try | 137/4234 | 4169/4234 |
| tufe_endeks | 138/4234 | 4199/4234 |
| tufe_aylik_degisim | 137/4234 | 4168/4234 |
| tufe_yillik_degisim | 126/4234 | 3834/4234 |
| enag_aylik_degisim | 65/4234 | 1979/4234 |
| enag_yillik_degisim | 58/4234 | 1764/4234 |
| noter_devir_toplam_adet | 138/4234 | 4199/4234 |
| noter_devir_otomobil_adet | 102/4234 | 3103/4234 |
| odmd_toplam_adet | 138/4234 | 4199/4234 |
| odmd_otomobil_adet | 137/4234 | 4169/4234 |
| odmd_hta_adet | 137/4234 | 4169/4234 |
| osd_binek_adet | 138/4234 | 4199/4234 |
| osd_kamyonet_adet | 138/4234 | 4199/4234 |
| osd_binek_kamyonet_toplam_adet | 138/4234 | 4199/4234 |
| tuketici_guven_endeksi | 139/4234 | 4230/4234 |
| otomobil_satinalma_ihtimali_endeksi | 139/4234 | 4230/4234 |
| proxy_fiyat_cari_tl | 26/4234 | 853/4234 |
| proxy_dom_gun | 26/4234 | 853/4234 |
| proxy_satis_orani_pct | 26/4234 | 853/4234 |
| brut_ucret_maas_endeksi_2021_100 | 99/4234 | 3012/4234 |
| tasit_kredisi_faiz | 139/4234 | 4230/4234 |
| politika_faizi | 139/4234 | 4230/4234 |

(Not: bu sayılar ilk — yanlış anlaşılan — versiyona göre birkaç gün
farklı çıkıyor, çünkü artık ayın kendi takvim günü sayısı kullanılıyor,
bir önceki ayın yayım tarihine bağlı kayma yok.)

---

## 5. Karşılaşılan Sorunlar

Teknik bir sorun çıkmadı. Tek not: her kaynağın kendi ham dosyasında
`referans_ayi` sütununun BENZERSİZ olduğu (tekrar yok) baştan kodla
doğrulandı — bu, takvim-ayı eşlemesinde hiçbir satırın çoğalmayacağını
(fan-out riski olmadığını) garanti ediyor.

---

## 6. Veri Örneği

`noter_devir_toplam_adet` ve `tufe_endeks` için, 2020-06 ayının başındaki
gün ile aynı ayın ortasındaki bir gün yan yana — artık İKİSİ DE aynı
(o ayın kendi) değeri taşıyor, çünkü bayrak/yayım-tarihi ayrımı kalktı:

| tarih | noter_devir_toplam_adet | noter_referans_ay | tufe_endeks | tufe_referans_ay |
|---|---|---|---|---|
| 2020-06-01 | 1097112.0 | 2020-06 | 465.84 | 2020-06 |
| 2020-06-15 | 1097112.0 | 2020-06 | 465.84 | 2020-06 |

Artık iki satır arasında hiçbir fark yok — ikisi de Haziran 2020'nin
kendi değerini gösteriyor, çünkü tasarım artık "hangi gün açıklandı"
sorusunu hiç sormuyor.

---

## 7. Açık Sorular / PM Onayı Gerekenler

1. **İlk versiyondaki `referans_ay` forward-fill ve `_gercek_mi` bayrağı
   soruları artık GEÇERSİZ/ÇÖZÜLMÜŞ durumda** — yeni tasarımda her günün
   `referans_ay` etiketi her zaman doğru (o ayın kendi etiketi), ayrıca
   bayrak talebe göre tamamen kaldırıldı. Ayrıca bir onay gerekmiyor.
2. **Sonraki adım önerisi (başlatılmadı, yalnızca öneri):** bu tablo
   artık korelasyon analizine hazır durumda (bayraksız, sade sayısal
   sütunlar) — istenirse ayrı bir görev olarak ele alınabilir.
