ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Mevcut durum: 2018-01→2026-06 arası genişletilmiş veri seti
hazır (veri_2018_bugun_etiketli.csv, 102 satır). Altı hedef adayı zaten
tanımlı: proxy_nominal, proxy_reel, noter_devir_hacim, proxy_dom_gun,
proxy_satis_orani, odmd_toplam_satis.

BU GÖREV BİR KARAR VERME DEĞİL, BİR KEŞİF GÖREVİDİR. Amaç: noter devir hacmi
(101 gözlem, dengeli) ve days-on-market/DOM (25 gözlem) verilerinden anlamlı
bir HEDEF veya BAĞLAM üretilip üretilemeyeceğini matematiksel ve görsel olarak
araştırmak. Nihai hedef seçimi (K1) PROJE SAHİBİNİN kararıdır — sen yalnızca
zengin, anlaşılır bir analiz + görselleştirme seti üretiyorsun.

BAĞLAYICI İLKELER:
- Yalnızca kamuya açık kaynaklar (K5).
- Hedef tanımını (K1) DEĞİŞTİRME — analiz et, karar verme.
- Bu bir "hangi hedef daha iyi" yarışması değil, "bu iki veri türü ne
  söylüyor, neye dönüşebilir" sorusu.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/veri/08_hedef_kesif_noter_dom_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — KAYNAK GÜVENİLİRLİK VE SÜRDÜRÜLEBİLİRLİK NOTU (kısa)
======================================================================
Her iki veri kaynağı için tek paragraflık bir güncel durum notu yaz:
- Noter devir hacmi: TÜİK'in resmi API'sinden (biruni.tuik.gov.tr veya
  ilgili portal) mi çekiliyor, yoksa bülten sayfası kazımasıyla mı? Şu anki
  çekim yöntemi bülten ID tahminine mi dayanıyor (önceki raporda belirtilen
  kırılganlık)? Varsa, resmi API'ye geçişin mümkün olup olmadığını kısaca
  değerlendir (geçiş YAPMA, sadece değerlendir).
- DOM: BETAM kaynağının bilinen boşluklarının (2024-05, 2025-02) bu analizi
  nasıl etkileyeceğini not et.

======================================================================
GÖREV 2 — TEK BAŞINA SERİ ANALİZİ (matematiksel + görsel)
======================================================================
Her iki seri (noter_devir_hacim, proxy_dom_gun) için AYRI AYRI:

2a. Tanımlayıcı istatistikler: ortalama, medyan, std sapma, min/max, çeyrekler.
2b. Zaman serisi görselleştirmesi: 2018-2026 (noter) / 2024-2026 (DOM) ham
    seviye + 3 aylık hareketli ortalama.
2c. Mevsimsellik testi: ay-bazlı boxplot (her ay için değer dağılımı) —
    belirgin bir mevsimsel örüntü var mı? (STL decomposition veya basit
    ay-dummy regresyonu ile mevsimsel bileşenin varyansa katkısını ölç.)
2d. Durağanlık testi: ADF (Augmented Dickey-Fuller) testi uygula — seri
    durağan mı, trend mi taşıyor?
2e. Otokorelasyon: ACF/PACF grafiği (ilk 12 lag) — serinin kendi geçmişiyle
    ne kadar ilişkili olduğunu göster.

======================================================================
GÖREV 3 — İKİ SERİ ARASI İLİŞKİ (noter devri × DOM)
======================================================================
- Örtüşen dönemde (2024-01→2026-06, ~25 ay) iki serinin birlikte hareketini
  incele: korelasyon (Pearson+Spearman), scatter plot, ve ÖNCÜ-GECİKMELİ
  ilişki (cross-correlation function, -6 ile +6 ay arası lag) — biri diğerini
  öncüllüyor mu? (Ör. DOM uzaması, birkaç ay sonra devir hacminde düşüşü
  öncülüyor mu?)
- Bu ilişkinin EKONOMİK YORUMUNU yaz: DOM ve noter devri aynı "piyasa
  hareketliliği" olgusunun iki farklı yüzü mü, yoksa bağımsız mı?

======================================================================
GÖREV 4 — KOMPOZİT "PİYASA AKTİVİTE ENDEKSİ" DENEMESİ
======================================================================
Bu, ana teslimat. Noter devri ve DOM'u (ve varsa proxy_satis_orani'yi) TEK BİR
kompozit göstergede birleştirmeyi dene:

4a. Basit yaklaşım: her seriyi standardize et (z-score), ardından ortalamasını
    al (DOM ters işaretli olmalı — DOM düşerse piyasa hızlanıyor demektir,
    işaret çevrilmeli). Sonucu "piyasa_aktivite_endeksi" olarak adlandır.
4b. PCA (Temel Bileşen Analizi): noter devri, DOM (ters işaretli), satış oranı
    ve varsa ODMD satışını tek bir ana bileşende birleştirmeyi dene. Açıklanan
    varyans oranını raporla — tek bileşen bu üç/dört seriyi ne kadar iyi özetliyor?
4c. Bu kompozit endeksin KENDİ yönünü (aylık değişim, up/stable/down) üret ve
    sınıf dağılımını raporla — kaç gözlemle, nasıl bir denge?
4d. GÖRSELLEŞTİRME: kompozit endeksi ham bileşenleriyle birlikte tek bir
    grafikte göster (çok-eksenli veya normalize edilmiş ortak eksen).

======================================================================
GÖREV 5 — FİYAT HEDEFİYLE ÇAPRAZ İLİŞKİ (asıl soru)
======================================================================
Örtüşen dönemde (proxy fiyatın dolu olduğu ~25 ay):
5a. Kompozit piyasa aktivite endeksi ile proxy_reel/proxy_nominal fiyat yönü
    arasındaki ilişkiyi test et (korelasyon + lag analizi — aktivite endeksi
    fiyattan ÖNCE mi hareket ediyor?).
5b. AÇIKÇA DEĞERLENDİR: bu kompozit endeks (i) bağımsız bir HEDEF olarak mı
    daha anlamlı, yoksa (ii) fiyat-yönü modeline ÖNCÜ FEATURE olarak mı daha
    değerli görünüyor? İkisini de destekleyen/zayıflatan kanıtı göster,
    kendi başına karar verme.
5c. Eğer aktivite endeksi fiyat yönünü anlamlı biçimde öncülüyorsa (lag>0'da
    güçlü korelasyon), bunu vurgula — bu, K11 kararının (hacim = güven
    düzeyi/destekleyici sinyal) güçlü bir ampirik dayanağı olur.

======================================================================
GÖREV 6 — ÇIKTI VE RAPOR
======================================================================
- data/processed/analiz/piyasa_aktivite_endeksi.csv (kompozit seri + bileşenleri)
- data/processed/analiz/hedef_kesif_gorseller/ altında tüm grafikler (PNG)
- PM RAPORU: data/processed/raporlar/pm_rapor_hedef_kesif.md VE oturumda
  KOPYALANABİLİR DÜZ METİN olarak.

Rapor başlıkları: (1) Kaynak güvenilirlik/sürdürülebilirlik notu (Görev 1).
(2) Her serinin tek başına davranışı — mevsimsellik, durağanlık, otokorelasyon
var mı (Görev 2, sade dille özetlenmiş). (3) İki seri birbirini nasıl
etkiliyor, öncü-gecikmeli ilişki var mı (Görev 3). (4) Kompozit endeks —
nasıl kuruldu, PCA açıklanan varyans, kendi sınıf dağılımı (Görev 4).
(5) EN KRİTİK BÖLÜM: kompozit endeks ile fiyat yönü ilişkisi — hedef mi,
öncü feature mi olmalı, kanıtlarla (Görev 5). (6) Görsel envanteri —
üretilen her grafiğin bir cümlelik açıklaması. (7) Açık sorular / PM
onayı gerekenler. (8) Veri örneği.

YAPMA:
- Hedef tanımını (K1) değiştirme veya "şu olmalı" diye karar verme — kanıt
  sun, karar PM/proje sahibine bırak.
- Model eğitme/tahmin üretme (bu, keşif aşaması).
- Yeni dış veri kaynağı arama (mevcut veriyle çalış).
