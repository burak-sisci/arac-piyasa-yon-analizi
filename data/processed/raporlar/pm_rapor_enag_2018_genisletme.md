---
başlık: PM Raporu — ENAG E-TÜFE Kontrol Serisi Geriye Genişletme (2018 Denemesi)
tarih: 2026-08-03
kapsam: 2018-01→2023-12 hedefiyle başlatıldı; Görev 1 bulgusu ve kademeli
  yıl-bazlı sonuçlar doğrultusunda proje sahibinin onayıyla 2021-01→2023-12
  aralığında durduruldu. Reel fiyat hesaplaması DEĞİŞTİRİLMEDİ, TÜİK ve ENAG
  TEK seri haline getirilmedi, mevcut 2024-2026 ana ENAG dosyasıyla
  BİRLEŞTİRİLMEDİ.
prompt_arşivi: prompts/veri/20_enag_2018_genisletme_prompt.md
durum: tamamlandı (kısmi kapsama — 2018-2020 aranmadı, bkz. Bölüm 2)
---

## 0) Ek Not (2026-08-03, sonradan eklendi)

Bu raporun 7. bölümünde ayrı dosya olarak bırakılması önerilen 2021-2023
genişletme verisi, proje sahibinin doğrudan talimatıyla mevcut 2024-2026
ana ENAG dosyasıyla **birleştirildi**. Tek/kapsamlı dosya:
`data/raw/enag/enag_aylik_2021_2026.csv` (65 ay, 2021-01→2026-06;
2021-02 ve 2018-2020 hâlâ yok — bu raporda açıklanan nedenlerle).
Birleşik dosya, kaynak dönemini (`veri_donemi`: genisletme_2021_2023 /
ana_2024_2026) ve doğrulama durumunu (`cift_dogrulama`) ayrı sütunlarda
korur — kalite farkı gizlenmedi. Üretim kodu:
`scripts/veri/genisletme_20_enag_birlestirme.py`. Aşağıdaki Bölüm 1-8,
birleştirme öncesi orijinal haliyle değiştirilmeden bırakılmıştır.

## 1) Ne yapıldı

ENAG E-TÜFE serisinin mevcut kapsamını (2024-01→2026-06) geriye doğru
genişletmek denendi. Önce metodoloji süreklilik kontrolü yapıldı (Görev 1);
bulgu, hedef aralığın (2018-01→2023-12) büyük bölümünün **aranacak veri
olmadığı için** imkansız olduğunu gösterdi. Bu bulgu proje sahibine
sunuldu; onunla birlikte yıl-bazında kademeli ilerleme planı kararlaştırıldı
(2023→2022→2021, her yıl sonunda özet + devam onayı). Üç yıl (2021, 2022,
2023) tarandı; 2021 sonuçlarındaki belirgin kalite düşüşü üzerine proje
sahibi 2020'ye gidilmeden durulmasına karar verdi.

## 2) Metodoloji süreklilik bulgusu (Görev 1)

- ENAG, 2016'da Prof. Dr. Veysel Ulusoy danışmanlığında bir **doktora tezi
  projesi** olarak başladı, **2020'de resmi olarak kuruldu**, ve
  **Haziran 2021'de kurumsallaştı** (enagrup.org bu tarihte açıldı).
- **İlk kamuya açık aylık bülten Kasım 2020'ye ait** (doğrulanan URL:
  `enagrup.org/bulten/kasim2020.pdf`); Aralık 2020 yıllık rakamı (%36,72)
  Ocak 2021'de basına yansımıştı.
- **Sonuç: 2018 ve 2019'un tamamı, ENAG için "veri yok" durumu** — bu bir
  arama başarısızlığı değil, kurumun o tarihlerde henüz kamuya veri
  yayınlamıyor olmasından kaynaklanıyor. Bu iki yıl hiç aranmadı (zaman
  kutusu boşa harcanmadı).
- **Ek yapısal bulgu (2021 taraması sırasında ortaya çıktı):** ENAG'ın
  günlük fiyat verisine dayalı endeksi Eylül 2020'de başladı. Bunun
  sonucu olarak **2021 Ocak-Ağustos aylarında henüz 12 aylık (yıllık)
  karşılaştırma rakamı yok** — yalnızca aylık % değişim ve bazı aylarda
  "yılbaşından bu yana kümülatif" rakamlar bulunabildi. Gerçek yıllık
  rakam ilk kez Eylül 2021'de (12 ay dolunca) görünüyor.
- Metodolojide (COICOP standardı, TÜİK'in 418 kaleminin 339'unun kullanımı)
  kurulduğundan bugüne büyük bir kırılma bulgusuna rastlanmadı — ama bu,
  sınırlı kaynak erişimi nedeniyle kesin bir sonuç değil, yalnızca "bilinen
  büyük bir değişiklik bulunamadı" düzeyinde bir gözlem.

## 3) YIL BAZINDA KAPSAMA TABLOSU

| Yıl | Bulunan ay | Çift doğrulanmış | Tek kaynaklı | Bulunamayan | Not |
|---|---|---|---|---|---|
| **2023** | 12/12 | 12 | 0 | 0 | Tam kapsama, tam doğrulama |
| **2022** | 12/12 | 12 | 0 | 0 | Tam kapsama, tam doğrulama |
| **2021** | 11/12 | 3 (Eki, Kas, Ara) | 8 (Oca, Mar-Ağu, Eyl) | 1 (Şubat) | Ocak-Ağustos'ta yıllık rakam yok (bkz. Bölüm 2), yalnızca aylık % var |
| 2020 | — | — | — | — | **Aranmadı** — proje sahibi onayıyla durduruldu |
| 2019 | — | — | — | — | **Aranmadı** — ENAG henüz veri yayınlamıyordu |
| 2018 | — | — | — | — | **Aranmadı** — ENAG henüz kurulmamıştı |

**En kritik gözlem:** Kapsama kalitesi yıl geriye gittikçe monoton biçimde
düşüyor — 2023 ve 2022 mükemmel (12/12, tam çift doğrulama), 2021 belirgin
biçimde zayıf (doğrulama oranı %25'e düşüyor, yılın 2/3'ünde yıllık rakam
kavramsal olarak yok). Bu düşüş eğilimi, 2020'ye gidilmesi durumunda
sonucun büyük ihtimalle tek-kaynaklı/kısmi veya tamamen boş çıkacağını
işaret ediyor — bu yüzden proje sahibi 2020'yi denemeden durmayı seçti.

## 4) Kaynak kalitesi dağılımı

35 satır (36 ay hedeflenmiş, 2021-02 bulunamadı):

| Seviye | Tanım | Ay sayısı |
|---|---|---|
| A | enagrup.org resmi site/PDF | 0/35 |
| B | ENAG resmi X hesabı doğrudan | 1/35 (2023-10) |
| C | Güvenilir haber ajansı, ENAG'a doğrudan atıfla | 34/35 |
| D | Diğer/az güvenilir | 0/35 |

**A seviyesi hiç elde edilemedi** — enagrup.org, tüm oturum boyunca
Cloudflare 525 (SSL handshake failed) hatası verdi; hem ana sayfa hem tüm
`enagrup.org/bulten/*.pdf` bülten URL'leri denendi, hepsi başarısız (önceki
Temmuz 2026 ENAG görevinde de aynı sorun tespit edilmişti — süregelen bir
altyapı sorunu). X/Twitter içeriğine doğrudan erişim de HTTP 402 (Payment
Required) ile sistematik olarak engellendi; bulunan tek B-seviyesi kayıt
(2023-10) yalnızca arama motoru snippet'i üzerinden dolaylı okunabildi.

## 5) Karşılaşılan sorunlar

1. **Yıl karışması riski beklenenden de yoğun gerçekleşti.** Her üç yılda
   da (2021, 2022, 2023) neredeyse her ay için en az bir yanlış-yıla ait
   sonuç ilk sırada çıktı. TÜİK'in bilinen aylık/yıllık rakamlarıyla
   çapraz kontrol edilerek tutarlı biçimde tespit edilip elendi — kural
   işe yaradı, ama arama maliyetini belirgin biçimde artırdı (2021 için ay
   başına ortalama 3-6 arama + 1-3 WebFetch gerekti).
2. **2021 Şubat tamamen bulunamadı** (~20 sorgu denendi, zaman kutusunun
   üzerine çıkıldı). ENAG'ın 3 Mart 2021 tarihli bir bülten tweet'i olduğu
   doğrulandı ama X erişim engeli nedeniyle içeriği okunamadı; arama
   motorunda bulunan tüm "ENAG şubat ayı enflasyon" başlıklı makaleler
   sistematik olarak 2022-2026 yıllarına aitti.
3. **WebSearch özetleme katmanı yüzde rakamlarının baştaki hanesini
   düşürüyor** (örn. "156,86" → "6,86"). Önceki ENAG görevinde de
   gözlemlenmişti; bu görevde de tekrarlandı. Her rakam WebFetch ile
   kaynak sayfadan doğrudan teyit edilerek düzeltildi — arama özetine asla
   doğrudan güvenilmedi.
4. **2021 Temmuz'da kaynak içi çelişki:** Bir haberin başlığı "yıllık
   %50'ye dayandı" derken gövde metni "Ocak-Temmuz kümülatif %25,14"
   diyordu. Kümülatif rakam, komşu ayların (Haziran %19,16, Ağustos
   %30,39) kümülatif trendiyle tutarlı olduğu için o kullanıldı, "%50"
   iddiası reddedildi (veri setine girmedi).
5. **2021 Ağustos'ta küçük bir hane tutarsızlığı:** T24 başlığı "%4,6"
   derken gövde metni ve diğer kaynaklar "%4,06" diyordu; birden fazla
   bağımsız arama sonucunda tutarlı çıkan %4,06 kullanıldı.

## 6) Veri örneği

İlk 3 satır (data/raw/enag/enag_2018_2023_genisletme.csv):
```
referans_ayi,enag_aylik_degisim,enag_yillik_degisim,kaynak_url,kaynak_seviyesi,cift_dogrulama
2021-01,2.99,,https://tr.euronews.com/2021/02/03/enag-n-ac-klad-g-ocak-ay-enflasyon-rakam-tuik-verilerinden-1-8-kat-daha-fazla,C,hayır
2021-03,3.36,,https://turkish.aawsat.com/home/article/2900951,C,hayır
2021-04,2.62,,https://www.gazeteduvar.com.tr/enflasyon-yuzde-kac-nisan-2021-haber-1521113,C,hayır
```

Son 3 satır:
```
2023-10,5.09,126.18,https://twitter.com/ENAGRUP/status/1720323181532057907,B,evet
2023-11,5.58,129.27,https://medyascope.tv/2023/12/04/enflasyon-tuike-gore-yuzde-6198-enaga-gore-yuzde-12927/,C,evet
2023-12,4.12,127.21,https://www.brandingturkiye.com/enag-aralik-2023-enflasyonunu-acikladi/,C,evet
```

Not: `enag_yillik_degisim` sütunu 2021-01, 2021-03..2021-08 için boş
bırakıldı — bu aylarda ENAG henüz gerçek 12 aylık rakam yayınlamıyordu
(Bölüm 2), kümülatif rakamı yıllık gibi göstermek yanıltıcı olurdu.
2021-02 satırı hiç yok (bulunamadı, uydurulmadı).

## 7) NET ÖNERİ

**Kullanılabilirlik: KISMİ.**

- **2022 ve 2023 (24 ay): kullanıma hazır kalitede** — tam kapsama, tam
  çift doğrulama, mevcut 2024-2026 dosyasıyla aynı kalite seviyesinde
  (ikisi de ağırlıklı C-seviyesi kaynak, aynı doğrulama disiplini).
- **2021 (11 ay, 1 eksik): dikkatli kullanılmalı** — yalnızca 4 ayı
  (Eylül-Aralık) tam anlamıyla "yıllık enflasyon" rakamı; Ocak-Ağustos
  yalnızca aylık % değişim içeriyor ve çoğu tek-kaynaklı. Ana seriyle
  aynı güvenle karıştırılmamalı.
- **2018-2020: elde edilemedi** — 2018-2019 için veri yok (ENAG henüz
  yoktu), 2020 proje sahibi onayıyla hiç aranmadı (2021 trendine bakılınca
  düşük getiri/yüksek maliyet beklentisi nedeniyle).

**Birleştirme kararı:** Talimat gereği bu görevde YAPILMADI (ayrı dosya
olarak bırakıldı: `data/raw/enag/enag_2018_2023_genisletme.csv`). Öneri:
2022-2023 (24 ay) mevcut 2024-2026 dosyasıyla aynı kalite bandında olduğu
için birleştirilmesi teknik olarak savunulabilir; 2021 ayrı/işaretli
tutulmalı (kısmi yıllık kapsama nedeniyle); 2018-2020 zaten yok. Karar
PM/proje sahibine bırakılmıştır.

## 8) Açık sorular / PM onayı gerekenler

1. 2022-2023 verisi mevcut ana ENAG dosyasıyla (2024-2026) birleştirilsin
   mi? (Aynı kalite seviyesinde — teknik engel yok, ayrı bir onay
   gerektiren bir karar.)
2. 2021 verisi (özellikle Ocak-Ağustos, yalnızca aylık rakam) nasıl
   kullanılsın — hiç mi kullanılmasın, yoksa "kısmi/yalnızca aylık"
   etiketiyle mi tutulsun?
3. enagrup.org'a (A-seviyesi kaynak) erişim ne zaman düzelirse, hem bu
   dönem hem 2024-2026 dönemi için A-seviyesi doğrulama tekrar denenebilir
   — ayrı görev, bu görevde başlatılmadı.
4. 2020 (Kasım-Aralık, ~2 ay) denenmek istenirse ayrı bir küçük görev
   olarak başlatılabilir; bu görevde proje sahibi onayıyla atlandı.
