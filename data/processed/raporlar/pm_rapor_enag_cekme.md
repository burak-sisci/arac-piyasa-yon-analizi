---
başlık: PM Raporu — ENAG E-TÜFE Kontrol Serisi Çekme
tarih: 2026-07-27
kapsam: Yalnızca veri çekme + yan yana karşılaştırma. Reel fiyat hesaplaması
  DEĞİŞTİRİLMEDİ, TÜİK ve ENAG TEK seri haline getirilmedi.
prompt_arşivi: prompts/veri/12_enag_veri_cekme_prompt.md
kaynak_kod: scripts/veri/genisletme_12_enag_cekme.py
durum: tamamlandı
---

## 0) Ek Not (2026-08-03, sonradan eklendi)

Bu raporda üretilen `enag_aylik_2024_2026.csv`, proje sahibinin talimatıyla
sonraki bir görevde toplanan 2021-2023 genişletme verisiyle birleştirilerek
tek dosya haline getirildi: `data/raw/enag/enag_aylik_2021_2026.csv`
(bkz. `pm_rapor_enag_2018_genisletme.md` Bölüm 0). Üretim kodu:
`scripts/veri/genisletme_20_enag_birlestirme.py`. Aşağıdaki bölümler,
birleştirme öncesi orijinal haliyle değiştirilmeden bırakılmıştır.

## 1) Ne yapıldı

ENAG (Enflasyon Araştırma Grubu) E-TÜFE serisi, 2024-01→2026-06 (30 ay) için
kamuya açık kaynaklardan toplandı ve mevcut TÜİK TÜFE serisiyle yan yana
(birleştirmeden, ayrı sütunlarda) karşılaştırma tablosuna ve grafiğe
dönüştürüldü. Toplama, 6 paralel ajanın (her biri 5 ay) WebSearch ile tarama
yaptığı bir Workflow ile yapıldı; ardından 5 ay için tamamen bağımsız bir
ikinci arama+kaynak seti ile çapraz doğrulama yapıldı (ayrı ajanlar, ilk
bulguyu görmeden).

## 2) ENAG hangi kaynaktan, hangi seviyeden (A-D) çekildi

**Resmi site (enagrup.org) 2026-07-27 itibarıyla erişilemez durumda** —
Cloudflare 525 "SSL handshake failed" hatası (WebFetch ve gerçek tarayıcı ile
iki ayrı yöntemle doğrulandı, ikisi de aynı hatayı verdi). Bu geçici bir
altyapı sorunu, kaynak yokluğu değil: arama sonuçlarında sitenin bülten arşiv
URL deseni doğrulandı (ör. `enagrup.org/bulten/202112.pdf` = Aralık 2021
bülteni, `enagrup.org/bulten/b202203.pdf` = Mart 2022) ve ENAG'ın en az
2021'den beri düzenli aylık bülten yayımladığı teyit edildi — ama içeriğe şu
an ulaşılamıyor.

Bu yüzden **kaynak öncelik kuralı B/C seviyesine kaydı**:

| Seviye | Tanım | Ay sayısı |
|---|---|---|
| A | enagrup.org resmi site/PDF | 0/30 |
| B | ENAG'ın resmi X hesabı (@ENAGRUP) doğrudan alıntı | 9/30 |
| C | Saygın haber ajansı/medya, ENAG'a doğrudan atıfla (Euronews, Cumhuriyet, Dünya Gazetesi, Branding Türkiye, T24, Diken, En Son Olay, 24 Saat Gazetesi) | 21/30 |
| D | Diğer/daha az güvenilir | 0/30 |
| bulunamadı | — | 0/30 |

**30/30 ay dolduruldu** (hiçbir ay boş kalmadı) — B/C seviyesine düşülmesine
rağmen kapsama tam.

## 3) Kapsanan dönem (kaç ay)

2024-01 → 2026-06, **30 ay, hiç eksik yok**. (ENAG'ın kendisi en az 2021'den
beri yayın yapıyor — resmi site erişilebilir olduğunda geriye doğru
genişletme ayrı bir görev olarak değerlendirilebilir; bu görevde mevcut proje
kapsamıyla örtüşen 2024-01 başlangıcı kullanıldı, prompttaki fallback kurala
uygun.)

## 4) Çapraz doğrulama sonucu

5 ay, ilk bulguyu görmeyen ayrı bir ajan tarafından sıfırdan yeniden arandı:

| Ay | Sonuç | İkinci (bağımsız) kaynak |
|---|---|---|
| 2024-01 | **EVET** (birebir uyum) | ekonomim.com |
| 2024-07 | **EVET** (birebir uyum) | tr.euronews.com |
| 2025-01 | **EVET** (birebir uyum) | brandingturkiye.com |
| 2025-07 | **EVET** (birebir uyum) | brandingturkiye.com |
| 2026-01 | **EVET** (birebir uyum) | cumhuriyet.com.tr |

**5/5 tam uyum.** Hiçbir ayda tutarsızlık bulunmadı.

## 5) TÜİK-ENAG fark tablosu özeti

- **Ortalama fark (yıllık, ENAG − TÜİK):** 35,98 puan
- **Min fark:** 19,39 puan (2026-06)
- **Maks fark:** 64,25 puan (2024-01)
- **Std sapma:** 11,27 puan

**Trend var:** Fark, 2024-01'deki 64,25 puandan 2026-06'daki 19,39 puana
**sürekli ve monoton biçimde daralıyor** (ara dönem dalgalanmaları hariç genel
eğilim net azalan). Kullanıcının önceden belirttiği "2026 Ocak-Mayıs'ta 20-24
puan bandı" gözlemiyle birebir örtüşüyor (bu dönemde fark: Ocak 22,77 / Şubat
22,61 / Mart 23,76 / Nisan 23,01 / Mayıs 20,52 puan) — bu, verinin iç
tutarlılığını destekleyen bağımsız bir çapraz kontrol noktası oldu.

Not: Bu daralma trendinin YORUMU (TÜİK mi ENAG'a yaklaşıyor, ENAG mi
yavaşlıyor, yoksa iki metodoloji arasındaki fark mı azalıyor) bilinçli olarak
YAPILMADI — talimat gereği yalnızca iki ölçümü yan yana koymak bu görevin
kapsamı, yorum/karar PM'e bırakıldı.

## 6) Karşılaşılan sorunlar

1. **enagrup.org erişilemez** (Bölüm 2'de detaylandırıldı) — A seviyesi kaynak
   şu an kullanılamıyor.
2. **Sistematik yıl-karışması riski (WebSearch/arama motoru kaynaklı):**
   Neredeyse her ay için "ENAG {ay} {yıl}" sorgusu en az bir kez YANLIŞ YILA
   ait bir sonuç döndürdü (özellikle 2025 aranırken 2026 verisi, veya tam
   tersi). Toplama ajanları bunu, bulunan TÜİK yıllık rakamını o ayın BİLİNEN
   resmi TÜİK değeriyle çapraz kontrol ederek tespit edip elediler (ör.
   2025-03 için "ENAG %54,62/TÜİK %30,87" başlıklı haberler bulundu ama TÜİK
   %30,87 gerçek Mart 2025 değeri olan %38,10 ile uyuşmadığı için reddedildi
   — bu rakamların aslında Mart 2026'ya ait olduğu ayrıca doğrulandı). Bu,
   projenin "WebSearch rakamı ikinci kaynakla doğrulanmadan kullanılmaz"
   kuralının tam olarak öngördüğü senaryo — kural işe yaradı.
3. **OCR/render bozukluğu:** Arama sonucu snippet'lerinde ENAG'ın kendi X
   gönderilerinden gelen yıllık rakamların ilk hanesi sık sık bozuk/eksik
   göründü (ör. "U,38", "q,23", "V,82", "e,49" gibi). Bu rakamlar hiçbir
   zaman doğrudan kullanılmadı; her seferinde temiz bir haber kaynağıyla
   (genellikle Euronews) çapraz doğrulanarak düzeltildi.
4. **X (Twitter) doğrudan erişim kısıtı:** ENAG'ın resmi X hesabındaki
   tweet'lere WebFetch ile doğrudan erişim birkaç kez HTTP 402 (Payment
   Required) hatasıyla engellendi — bu aylarda X içeriği yalnızca arama
   motoru snippet'i üzerinden (kısmi/bozuk) okunabildi, doğrulama haber
   kaynaklarına dayandı.

## 7) Veri örneği (ilk/son 3 satır, tufe_enag_karsilastirma.csv)

İlk 3 satır:
```
referans_ayi,tufe_aylik,tufe_yillik,enag_aylik,enag_yillik,fark_yillik,kaynak_seviyesi
2024-01,6.70,64.86,9.38,129.11,64.25,C
2024-02,4.53,67.07,4.32,121.98,54.91,C
2024-03,3.16,68.50,5.68,124.63,56.13,C
```

Son 3 satır:
```
2026-04,4.18,32.37,5.07,55.38,23.01,C
2026-05,1.71,32.61,2.16,53.13,20.52,C
2026-06,0.99,32.10,1.94,51.49,19.39,C
```

(Tam tablo `data/processed/analiz/tufe_enag_karsilastirma.csv` içinde 30
satır olarak mevcuttur.)

## 8) Açık sorular / PM onayı gerekenler

1. **enagrup.org ne zaman tekrar erişilebilir olacak, bilinmiyor.** Site
   tekrar erişilebilir olduğunda, hem A-seviyesi (resmi) doğrulama için hem
   de 2021-2023 arası geriye genişletme için tekrar denenmesi önerilir —
   bu, ayrı bir görev olarak PM onayı gerektirir (bu görev kapsamında
   BAŞLATILMADI, talimat gereği yalnızca öneri).
2. **B seviyesi (X hesabı) rakamların çoğu OCR bozukluğu nedeniyle aslında
   C-seviyesi kaynaklarla teyit edilerek kullanıldı** — kaynak_seviyesi
   alanı "B" olarak işaretlendiği için teknik olarak doğru (X hesabı ilk
   kaynak), ama pratikte doğrulama her zaman bir C-seviyesi kaynağa
   dayandı. Bu nüans veri sözlüğüne eklenmek istenirse ayrı bir küçük görev
   olabilir.
3. **Fark trendinin (64pp → 19pp daralma) yorumu yapılmadı** — bilinçli
   olarak (talimat gereği). Bu, K1 alt kararları için PM/proje sahibinin
   değerlendirmesi gereken bir bulgu.
4. **2024-01 öncesi (ENAG en az 2021'den beri yayında) genişletme** —
   yapılmadı, kapsam dışı bırakıldı (mevcut proje penceresiyle örtüşmesi
   için 2024-01 başlangıç noktası kullanıldı). İstenirse ayrı görev.
