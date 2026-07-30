---
başlık: PM Raporu — BETAM Aralık 2023 Grafiği Dijitalizasyon Fizibilitesi
tarih: 2026-07-30
kapsam: Yalnızca fizibilite testi. Tam dijitalizasyon YAPILMADI, hedef/model
  değiştirilmedi.
prompt_arşivi: prompts/veri/17_betam_grafik_fizibilite_prompt.md
kaynak: BETAM sahibindex Otomobil Piyasası Görünümü, Aralık 2023
  (https://image5.sahibinden.com/staticContent/1b9c4d5b/7758/44a8/b2a6/3f9dc2997532/1702637758.pdf)
durum: tamamlandı
---

## 1) Ne yapıldı

BETAM'ın Aralık 2023 raporu PDF'i (14 sayfa) indirildi, PyMuPDF ile 400 DPI
çözünürlükte sayfa görüntülerine dönüştürüldü. Rapordaki iki hedef grafik
bulundu ve yüksek çözünürlüklü ayrı görüntü dosyalarına kırpıldı:

- **Şekil 1** (rapor sayfa 4): "Ortalama otomobil fiyatı (TL) (Sol panel),
  ortalama fiyatının yıllık değişimi (%) (Sağ panel)" — 2020-01 → 2023-11.
- **Şekil 2** (rapor sayfa 5): "Ortalama otomobil reel fiyatı (2020 Ocak=100)
  (Sol panel), ortalama reel fiyatının yıllık değişimi (%) (Sağ panel)" —
  aynı dönem.

Görüntüler `data/processed/analiz/gorseller/betam_aralik2023_sekil1_nominal_400dpi.png`
ve `..._sekil2_reel_400dpi.png` olarak repoya eklendi.

## 2) Görsel kalite değerlendirmesi

1. **Eksen netliği:** Çok iyi. X ekseni **her ayı tek tek etiketliyor**
   (2020-1'den 2023-11'e, 47 ay — Şekil 1 sol panelde; Şekil 1/2 sağ
   panellerde 2021-1'den başlıyor çünkü yıllık değişim bir önceki yıla
   ihtiyaç duyuyor). Y ekseni sayısal değerleri net: Şekil 1 sol panelde
   0-1.000.000 TL arası 100.000'lik dilimler; sağ panelde %10-170 arası
   ~20 puanlık dilimler; Şekil 2 sol panelde 50-350 endeks arası 50'lik
   dilimler; sağ panelde -%10/+%70 arası 10 puanlık dilimler.
2. **Çizgi netliği:** Çok iyi. Her panelde **TEK** siyah çizgi (kesişen/
   karışan ikinci bir seri yok — nominal ve reel ayrı şekillerde, birbirine
   karışmıyor). Her ay net bir nokta işaretleyicisiyle gösterilmiş.
3. **Veri noktası yoğunluğu:** Orta-iyi. 47 ay, panel genişliğine sıkışık
   ama 400 DPI'da noktalar birbirinden ayrılabiliyor. **Keskin
   dönüm noktaları (tepe/dip) net görülüyor**; düz/yatay seyreden
   bölgelerde (ör. 2021 ortası, fiyatların yavaş yükseldiği dönem) komşu
   ay noktalarını birbirinden kesin ayırmak daha zor.
4. **Çözünürlük yeterliliği:** İyi. 400 DPI render + kırpma sonrası
   pikselleşme yok, noktalar ve eksen etiketleri net; ekstra zum
   mümkün.
5. **Sayısal metin çapası:** ÇOK ZENGİN — beklenenin ötesinde. Rapor
   metninde en az **9 kesin çapa noktası** var (aşağıda Görev 3'te
   kullanıldı), hem nominal hem reel, hem seviye hem yıllık değişim için.
   Bu, dijitalizasyon için olağandışı derecede elverişli bir durum.

## 3) Deneme okuma sonucu (5 nokta test edildi)

| Nokta | Görsel tahmin | Metindeki kesin değer | Fark |
|---|---|---|---|
| Ekim 2021, yıllık nominal artış (Şekil 1 sağ, dip) | ~%16-17 | **%16,4** | <1 puan |
| Aralık 2022, yıllık nominal artış (Şekil 1 sağ, dip) | ~%55 | **%53,6** | ~1,4 puan |
| Kasım 2023, yıllık nominal artış (Şekil 1 sağ, son nokta) | ~%76 | **%76,2** | <1 puan |
| Kasım 2023, reel fiyat endeksi (Şekil 2 sol, son nokta) | ~220-225 | **223** | <3 puan |
| Haziran 2023, reel fiyat endeksi (Şekil 2 sol, tepe) | ~295 | **293** | ~2 puan |

**5/5 nokta, metindeki kesin değere ~%1-3 bağıl hatayla çok yakın çıktı.**
Bu, güçlü bir olumlu ön-sinyal.

**ÖNEMLİ NÜANS:** Bu 5 nokta %-değişim ve endeks (50-350 aralığı) panellerinden
seçildi — bunlar Y ekseninde nispeten SIKI aralıklı (gridline'lar arası az
"boşluk"). **Şekil 1 sol panel (mutlak TL fiyat, 0-1.000.000 aralığı,
100.000'lik dilimler)** için aynı testi yapmadım ama gridline aralığı çok
daha kaba — Kasım 2023 = 879.146 TL çapa noktasını görsel olarak okusaydım
muhtemelen "~880.000-900.000" gibi bir aralık verirdim, yani **mutlak TL
seviyesi okumasında hata payı muhtemelen %-panellerden daha büyük** (kaba
tahmin: ±%2-5).

## 4) FİZİBİLİTE KARARI

**SONUÇ: (a) tam dijitalizasyona değer — ama panel bazında farklılaşan bir
güvenle.**

- **%-değişim panelleri (nominal yıllık değişim, reel yıllık değişim) ve
  reel endeks paneli:** Yüksek güven. Deneme okuması ~%1-3 bağıl hata
  gösterdi, eksen/çizgi/çözünürlük kalitesi çok iyi, zengin çapa noktası
  seti kalibrasyon/doğrulama için kullanılabilir. **Tahmini hata payı:
  ~%2-4 civarı** (bant genişliği tahmini, tam dijitalizasyon sonrası
  kesinleşir).
- **Mutlak TL fiyat paneli (Şekil 1 sol):** Orta güven — kaba gridline
  aralığı (100.000 TL) nedeniyle ay-ay kesin TL değeri okumak daha
  belirsiz. **Tahmini hata payı: ~%2-5 civarı**, muhtemelen bazı aylarda
  daha fazla.
- **Ay-ay ayrım:** Keskin dönüm noktalarında (tepe/dip) güvenilir; düz
  seyreden dönemlerde komşu ayları kesin ayırt etmek daha zor olabilir —
  ama bu dönemlerde zaten mutlak seviye de az değiştiği için, hata payının
  pratik etkisi (yön sınıflandırması açısından) sınırlı olabilir.

**Genel değerlendirme:** Bu proje için asıl ilgi alanı **yön (up/down/
stable) sınıflandırması** olduğundan, %-değişim panellerinin yüksek
güvenilirlikte okunabilir olması özellikle değerli — bu tam da projenin
ihtiyaç duyduğu türde bir sinyal. Mutlak TL seviyesi daha az kesin olsa
da, trend/yön çıkarımı için yeterli görünüyor.

## 5) Karşılaşılan sorunlar

- Yok — PDF sorunsuz indirildi (200 HTTP, 484 KB, 14 sayfa), sayfa
  numaralandırması beklenenden bir kayma gösterdi (kapak+içindekiler
  sayfaları basılı sayfa numarasına dahil değil) ama bu yalnızca kırpma
  aşamasında küçük bir düzeltme gerektirdi, veri kalitesini etkilemedi.

## 6) Açık sorular / PM onayı gerekenler

**ASIL SORU: Aşama 2'ye (çoklu-yöntem dijitalizasyon) geçilsin mi?**

Kanıt bu yönde olumlu (bkz. Bölüm 4), ama karar PM/proje sahibine bırakılır.
Değerlendirirken göz önünde bulundurulması gerekenler:

1. Bu TEK BİR raporun (Aralık 2023) grafiğidir — 2020-01→2023-11 arası
   TAM kapsıyor, yani 2021-2023 hedef dönemi için ayrı ayrı her ayın
   raporunu bulmaya gerek YOK, tek bir grafikten tüm dönem çıkarılabilir
   (bu, fizibiliteyi ekstra cazip kılan bir avantaj).
2. Bu, sahibinden.com'un TÜM veri havuzundan BETAM'ın türettiği bir
   ORTALAMA seridir — ham ilan verisi değil, BETAM'ın kendi metodolojik
   varsayımlarına (mix/kompozisyon düzeltmesi yapılıp yapılmadığı
   belirsiz) tabidir; bu proje için zaten bilinen N1 sınırlamasına benzer
   bir sınırlama taşıyabilir — dijitalizasyon bu metodolojik belirsizliği
   ÇÖZMEZ, yalnızca var olan grafiği sayıya çevirir.
3. Aşama 2 "çoklu-yöntem" ne anlama geliyor (ör. birden fazla kişi/araç ile
   çapraz okuma, otomatik görüntü-işleme + elle doğrulama karışımı) —
   kapsam/yöntem netleştirilmeli.
4. Mutlak TL paneli mi, %-değişim panelleri mi, yoksa reel endeks paneli
   mi öncelikli dijitalize edilecek — üçünün de farklı güven seviyesi var
   (Bölüm 4), hangisinin projenin ihtiyacına (hedef mi, kontrol serisi mi)
   en uygun olduğu bir tasarım kararı.
