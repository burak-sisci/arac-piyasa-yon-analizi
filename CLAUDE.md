# CLAUDE.md — Proje Bağlamı

## Proje Kimliği

**Proje:** Araç Piyasası Fiyat Yönü Tahmini
**Sahip:** Arabam.com Data Science Intern (proje yürütücüsü)
**Nihai amaç:** Geliştirici ekibin, araç piyasasında fiyat yönünü (up / down / stable)
tahmin eden bir ML sistemine "gelmiş geçmiş en iyi baseline" ile başlamasını sağlamak.

Proje İKİ AŞAMALIDIR:

- **Aşama A — Literatür Tarama ve Bilgi Tabanı (TAMAMLANDI, referans olarak
  kalıcı):** Çıktılar Markdown dökümanları, sentez raporu ve karar-odaklı
  sunum. Kod yalnızca döküman dönüşümü (pandoc, python-docx, python-pptx)
  gibi yardımcı işler için yazıldı. Bkz. `docs/`.
- **Aşama B — Veri Mühendisliği ve Keşif (AKTİF):** Aşama A'nın bulgularını
  gerçek Türkiye araç piyasası verisiyle test eden, **bu artık bir yazılım
  projesidir** (Python: veri çekme, temizleme, istatistiksel analiz,
  görselleştirme). Bkz. `data/`, `scripts/veri/`, `prompts/veri/`.

Bu iki aşamanın ortak noktası: nihai hedef aynı (fiyat yönü tahmini için
literatüre VE veriye dayalı bir baseline). README.md'deki "Aşama A / Aşama B"
bölümleri güncel durumu tutar; buradaki ayrım kalıcıdır, değişmez.

**Not (2026-08-06, K9):** Aşama A'nın "fiyat yönü" literatürü ve K8 kararı
(ilan fiyatının nominal yönü) tarihsel referans olarak korunur — proxy fiyat
serisi N<50 keşifsel geçitte dondurulmuş durumdadır. Aşama B'nin ŞU ANKİ
aktif operasyonel target'ı günlük `noter_devir_otomobil_adet` (hacim)
serisinin doğrudan üç-sınıflı (up/stable/down) yönüdür — gerekçe: veri
yeterliliği (N<50 kapısını fiyattan farklı olarak aşıyor) ve daha dengeli
sınıf dağılımı. Bu hacim sinyali fiyatlama kararlarına bir GİRDİdir, K8'in
yerine geçen doğrudan bir fiyat tahmini değildir. Ayrıntı: `docs/00_karar_kaydi.md`
K9.

## Çalışma Rolü Hiyerarşisi (Aşama B, 2026-08-06 itibarıyla)

- **Codex** — denetmen ve karar/onay mercii. Bağlayıcı kararları (K/N
  maddeleri) onaylar/reddeder; repoyu salt-okunur denetler.
- **Claude Code** — "Kodcu": Codex tarafından onaylanan işi uygular, kod
  yazar, test eder, PM raporu üretir.
- **Perplexity** — "Araştırmacı": dış araştırma (literatür/veri kaynağı
  taraması) yürütür.
- Codex onayından geçmeyen hiçbir yeni bağlayıcı karar uygulanmaz; belirsizlik
  durumunda mevcut K/N kararlarına sadık kalınır ve açık soru olarak PM
  raporuna yazılır (bkz. Zorunlu Kural 10).

## Hedef Kitle: Geliştirici Ekip Profili

- İleri seviye. Model eğitimi, zaman serisi analizi ve sınıflandırma deneyimliler.
- KURAL: Temel/giriş seviyesi ML açıklaması İÇEREN HİÇBİR içerik üretme.
  ("Random Forest nedir", "cross-validation nedir" gibi içerik yasak.)
- Her bulgu şu soruya bağlanmalı: "Bu, bizim fiyat yönü tahmin problemimize
  nasıl uygulanır?"

## Problem Çerçevesi (mevcut karar durumu)

- Görev tipi: Yön sınıflandırması (up / down / stable). Sınıf sayısı, tahmin ufku
  ve threshold kararları Faz 0 planı ve ilgili faz taramaları sonrası netleşecek.
- Kapsam: Akademik (peer-reviewed) + finansal piyasa yön tahmini literatürü
  (hisse/kripto/emtia) + endüstri/Kaggle/blog kaynakları + araç piyasasına özgü
  dinamikler (kur, ÖTV/vergi, arz şokları, EV geçişi, Türkiye'ye özgü faktörler).

## Çalışma Modeli

- İş zamana yayılmış, çok fazlı yürütülür. Her faz ayrı oturum, her fazın çıktısı
  ayrı bir Markdown dosyasıdır.
- Ağır literatür taramaları claude.ai Deep Research'te yapılır; çıktılar bu repoya
  taşınır. Claude Code'un görevi: organizasyon, tutarlılık kontrolü, sentez,
  format dönüşümleri ve sunum üretimi.
- Master plan: `docs/00_master_plan_literatur_taramasi.md` (Faz 0 çıktısı).
  Her oturumda önce master planı ve ilgili önceki faz dosyalarını OKU, sonra çalış.
- Aşama B (veri mühendisliği) için karşılığı: proje sahibinden gelen prompt →
  öz-arşivleme (`prompts/veri/`) → çalışma → PM raporu (`data/processed/raporlar/`).
  Ayrıntı: README.md → "Nasıl çalışır (veri mühendisliği döngüsü)".

## Depo Yapısı

```
.
├── CLAUDE.md                  # bu dosya — her oturumda bağlam
├── README.md                  # repo tanıtımı (Aşama A + Aşama B durumu)
├── docs/
│   ├── standards.md           # döküman ve kalite standartları
│   ├── 00_master_plan_literatur_taramasi.md   # Faz 0 çıktısı (master plan)
│   ├── 00_karar_kaydi.md      # K/N kapsam kararları (bağlayıcı)
│   ├── 01_*.md ... 09_*.md    # faz çıktıları + sentez (numaralı)
│   └── sentez/                # (şu an boş — sentez dökümanı docs/09'da duruyor)
├── prompts/                   # Aşama A: faz promptlarının arşivi
│   └── veri/                  # Aşama B: veri mühendisliği promptlarının arşivi
├── scripts/veri/               # Aşama B: veri çekme/temizleme/analiz kodu
├── data/                       # Aşama B: raw/processed veri (bkz. data/README.md, K5)
└── exports/                   # docx/pptx/pdf dönüşüm çıktıları (git'e girmez)
```

## Zorunlu Kurallar

1. Tüm içerik Türkçe yazılır; kaynak başlıkları orijinal dilinde bırakılır.
2. Her faz dökümanı `docs/standards.md` içindeki metadata bloğu ile başlar ve
   kalite kontrol listesinden geçmeden "tamamlandı" işaretlenmez.
3. Kaynaksız iddia yazılmaz. Emin olunmayan nokta "literatürde net değil" diye
   açıkça işaretlenir; tahmin yürütülmez.
4. Var olan faz dosyaları sahibinin onayı olmadan yeniden yazılmaz; düzeltmeler
   küçük ve gerekçeli commit'lerle yapılır.
5. Git commit'leri: author olarak proje sahibinin adı/e-postası kullanılır
   (repo `git config user.name` / `user.email` ayarı ile). Commit mesajları
   Türkçe ve açıklayıcı olur: `faz-03: feature engineering taraması eklendi` gibi.
6. Belirsizlik varsa varsayım yapıp ilerleme; proje sahibine soru sor.
7. `README.md` içindeki "Durum" listesi (8 faz + sentez + sunum,
   `docs/00_master_plan_literatur_taramasi.md` Bölüm 1'deki faz adlarıyla birebir)
   her commit'te son duruma göre güncellenir: tamamlanan/eklenen faz `[x]`
   işaretlenir; bir dökümanın `durum` alanı `taslak`'a dönerse (ör. revizyon)
   README'deki işaret de geri alınır. Bu, her faz commit'inin bir parçasıdır,
   ayrı bir görev değildir.
8. Proje sahibi commit + push işlemini önceden onaylamıştır: değişiklikler
   tamamlandıkça (ayrı bir onay beklemeden) mantıksal commit'lere bölünüp
   `origin/main`'e push edilir. Bu onay geri alınana kadar geçerlidir.
9. Token maliyeti gözetilir: fazla token harcayabilecek işlere (çok-aşamalı veri
   çekme, geniş kapsamlı kod yazımı, çoklu API/scraping denemesi, büyük
   yeniden-üretimler vb.) başlamadan önce proje sahibinden onay alınır. Büyük
   görevler küçük aşamalara bölünür; her aşama bitince özet sunulup bir sonraki
   aşama için ayrıca onay istenir — tek seferde uçtan uca koşulmaz.
10. Veri mühendisliği (scripts/veri/) işi bittiğinde, ayrı bir oturumdaki proje
    yöneticisinin (PM) denetleyebilmesi için `data/processed/raporlar/pm_rapor_<asama_adi>.md`
    dosyası üretilir ve commit'lenir (veri dosyalarından farklı olarak bu rapor
    Git'e girer — denetim izi için). Rapor kısa, dürüst ve denetlenebilir olur;
    şu 7 başlığı içerir: (1) Ne Yapıldı, (2) Sayısal Özet, (3) Karşılaşılan
    Sorunlar (saklanmaz), (4) Veri Örneği (ham, ilk/son birkaç satır),
    (5) Varsayımlar ve Kararlar (K/N kararlarına uygunluk), (6) Açık Sorular /
    PM Onayı Gerekenler, (7) Önerilen Sonraki Adım (başlatılmaz, yalnızca önerilir).
    Rapor oturumda özet olarak da gösterilir.
11. Proje sahibinin kalıcı notebook talimatı (aynen):

    > bundan sonra senden tamamlanan her aşama için ders kitabı tadında bir .jpynb dosyası yazmanı istiyorum. sıradan birinin anlayabileceği kadar basit ve teknik kararlar verebilecek kadar eğitici olsun. bunu claude.md dosyasına aynen yaz. bundan sonra ki tüm çalışmalarda durum bu şekilde olacak.

    Uygulama standardı: Her tamamlanan aşama için geçerli Jupyter Notebook
    uzantısıyla (`.ipynb`) bir ders kitabı notebook'u üretilir. Notebook;
    sıradan bir okuyucunun izleyebileceği açık anlatımı, teknik karar verecek
    kişinin ihtiyaç duyacağı yöntem/gerekçe/varsayım/ölçüm ayrıntılarını,
    çalıştırılabilir kod hücrelerini, sonuçların yorumunu, sınırlılıkları ve
    sonraki karar noktalarını birlikte içerir. İlgili notebook üretilmeden
    aşama tamamlanmış sayılmaz; notebook aşamanın kod, test, PM raporu ve
    README güncellemesiyle aynı mantıksal commit/push paketine girer.

## Otonomi Sınırı — Kullanıcı Gerekli / Gerekli Değil

Bu projede iş süreçleri ikiye ayrılır. 'Kullanıcı gerekli' olmayan tüm işler
Claude Code tarafından onay beklenmeden uçtan uca yürütülür; proje sahibi
gerektiğinde müdahale eder.

KULLANICI GEREKLİ (onay/karar beklenir):
- Bağlayıcı karar değişiklikleri (hedef tanımı, kapsam, K/N maddeleri).
- Yeni bir AŞAMA TÜRÜ başlatma (ör. veri toplamadan modellemeye geçiş).
  Aynı aşama içindeki adım geçişleri onay gerektirmez.
- Para/hesap gerektiren işlemler (API anahtarı, ücretli servis).
- Kapsam dışına çıkacak veya geri alınması zor işlemler.

KULLANICI GEREKLİ DEĞİL (otonom yürütülür):
- Veri çekme, temizleme, birleştirme, doğrulama adımları.
- Kod yazma, refactor, test, hata düzeltme.
- Klasör/dosya organizasyonu, commit ve push.
- Rapor ve dokümantasyon üretimi.

PROAKTİF BİLDİRİM (onay değil, bilgilendirme — sessiz kalınmaz):
- Şüpheli/doğrulanmamış bulgular (kaynaklar arası çelişen rakamlar, dış araç
  çıktısındaki hatalar vb.).
- Beklenmedik sonuçlar, bloke edici riskler, varsayımla çözülen noktalar.
- PM raporları (bilgilendirme amaçlı iletilir, onay beklenmez).

Kural: Şüphe varsa bildir; bildirmemek, yanlış ilerlemekten daha maliyetlidir.
