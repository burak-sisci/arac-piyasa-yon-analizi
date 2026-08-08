# PM Raporu — Revizyona Kapalı Yeni Öncü Aday Taraması

**Tarih:** 2026-08-08

**Aşama:** Model 13 sonrası Seçenek 2 / Prompt 42 masa başı taraması

**Durum:** Tamamlandı — **BU_TURDA_UYGUN_ADAY_YOK**

**Karar yöneticisi:** Pusula (`claude-opus-5`, Opus/max)

**Uygulayıcı:** Rota-2

## 1. Ne Yapıldı

Prompt 42'nin `26a692b` commit'inde sonuçlardan önce kilitlenen kapsamıyla en
fazla üç yeni aday aile masa başında tarandı:

1. TCMB haftalık kart işlem adedi, araç kiralama-satış/servis/yedek parça.
2. SBM trafik sigortası yazılan poliçe adedi.
3. TÜİK NACE 45 Ticaret Satış Hacim Endeksi.

Karar labındaki gerçek `False` boşluklara bağ, başlangıç, frekans, M−2
zamanlılığı, revizyon, kapsam ve mekanizma birincil/resmî sayfalardan incelendi.
Veri/API/scraping/model yapılmadı. BDDK, BETAM ve Google Trends yeniden
taranmadı. Pusula Opus/max üç kartın çoklu kapılarda düştüğünü doğruladı ve
`BU_TURDA_UYGUN_ADAY_YOK` hükmünü kabul etti.

## 2. Sayısal Özet

- Yeni aday kartı: **3/3**.
- İlerletilen: **0/3**.
- Revizyona kapalı olduğu doğrulanan: **0/3**.
- Revizyona açık: **2/3** — TCMB, TÜİK.
- Revizyon durumu doğrulanamayan/aktif mutable: **1/3** — SBM.
- M−2 zamanlılığı belgelenen: **2/3** — TCMB, TÜİK.
- N<50 kapsam nedeniyle elenen: **1/3** — SBM.
- Kullanılan farklı resmî/birincil sayfa: **7/10**.
- Veri indirme/API/scraping/model/test: **0**.
- Hedef/sınıf/ufuk/band/K değişikliği: **0**.

| Aday | Operasyonel kapsam | Revizyon | Mekanizma/boşluk | Hüküm |
|---|---|---|---|---|
| TCMB kart işlem adedi | 2014+, haftalık, +4 iş günü | Geçici ve revizyona tabi | Kategori 02 satıştan çok daha geniş; kart dışı ödemeler yok | Elendi |
| SBM poliçe adedi | Kamu sayfası 2024–2026 | İptal/zeyil ile mutable | Yenileme ve satış karışık | Elendi |
| TÜİK NACE 45 satış hacmi | 2010+, aylık, ~39–41 gün | Resmî revizyon geçmişi | Eşzamanlı; hedef geçmişine yakın ve kapsam çok geniş | Elendi |

## 3. Karşılaşılan Sorunlar (Saklanmaz)

1. TCMB kart serisi operasyonel olarak en zamanlı adaydı; ekonomik olarak en
   güçlü değildir. Türkiye araç satışlarının kart dışı ödeme kısmını kaçırır ve
   kategori servis/parça/kiralama ağırlığı taşıyabilir.
2. TCMB metaverisi veriyi açıkça geçici ve revizyona tabi ilan eder. BDDK'da
   yaşanan yükseltilemez `HEURISTIK` yolunu tekrar etmek gerekçelendirilmedi.
3. SBM kamu sayfasında exact yayın gecikmesi ve resmî revizyon politikası yoktu.
   Yazılan adet iptalleri düşer, zeyil/poliçe başlangıcına dayanır ve merkezî
   kayıt güncellenir; ilk-yayım=nihai eşitliği kurulamadı.
4. SBM kamu kapsamı 2024–2026 ile N<50'dir; 50 origin ve uzun geri bakış için
   yetersizdir.
5. TÜİK serisi uzun ve M−2 uyumludur; ancak resmî revizyon geçmişi vardır.
   Ayrıca yeni/ikinci el, toptan/perakende, onarım ve motosiklet karışımıdır.
6. TÜİK göstergesi öncü yeni boşluk yerine M−2 hedef hafızasının daha kaba ve
   eşzamanlı bir kopyasına yaklaşır; karar labındaki `False` aileyi temiz kapatmaz.
7. Kalan 3 sayfa bir aday geçene kadar aramayı sürdürmek için kullanılmadı;
   önkayıtlı stop kuralı korundu.
8. Model 13'te delta marj kapasiteyle C=1 `+0,2402` → C=0,1 `+0,1091` →
   C=0,01 `+0,0268` azaldı; null95 de `0,4684 → 0,4450 → 0,4220` geriledi.
   Tek kapasite noktasındaki delta işareti artefakt olabilir.

### Genel metodolojik ders

Gelecekteki herhangi bir in-sample/permutasyon ön-elemesinde tek kapasite
noktasındaki delta marj tek başına yorumlanmayacaktır. Aday en az iki kapasite
noktasında sınanmalı; pozitif delta her zaman mutlak marj ve null95 kapasite
eğrisiyle birlikte raporlanmalıdır.

### Yapısal as-of bulgusu

Seçenek 2'de toplam altı aile tüketildi: BDDK, BETAM–sahibindex, Google Trends,
TCMB, SBM ve TÜİK. İncelenen altı ailede temiz hedef mekanizması ile kamuya açık
ilk-yayım/as-of korunumu birlikte kurulamadı; bazıları ek kapsam/mekanizma
kapılarında da düştü. Bu sınırlı taramaların proje hükmü:

> Mevcut kamuya açık Türkiye veri ortamı, bu hedef ve bu as-of disipliniyle,
> geriye dönük değerlendirmeye uygun öncü bilgi eklenmesini desteklememektedir.

Bu, tüm olası Türkiye verileri hakkında evrensel yokluk iddiası değildir.

## 4. Veri Örneği (Ham, İlk/Son Birkaç Satır)

Bu aşamada veri çekilmedi; ham satır yoktur. Kaynak sayfalarındaki doğrulanmış
metadata/yayın kanıtı örnekleri:

```text
TCMB işlem adedi: haftalık akım; Mart 2014 başlangıcı; +4 iş günü;
                   her hafta geçici ve revizyona tabi.
TCMB kategori 02: yeni+ikinci el satış + servis + tamir + parça + kiralama.
SBM yazılan adet: üretilen poliçe - başlangıçtan iptal;
                  poliçe/zeyil başlama tarihi; kamu kapsamı 2024-2026.
TÜİK NACE 45:     Ocak 2010 başlangıcı; aylık; KDV beyannamesi;
                  ayrı Revizyon Geçmişi; ticaret + onarım + motosiklet.
```

Bu satırlar model girdisi değildir; aday kartlarının denetim özetidir.

## 5. Varsayımlar ve Kararlar (K/N Kararlarına Uygunluk)

- Target, üç sınıf, ±%5 bandı ve haftalık cari-ay nowcast değişmedi.
- M−2 bilgi disiplini ve kilitli test korundu.
- Mevcut feature'ın başka dönüşümü yeni aday sayılmadı.
- `revizyona_kapali_mi` tahmin edilmedi; kaynak kanıtı yoksa doğrulanmadı yazıldı.
- Uzun kapsam tek başına ilerleme gerekçesi yapılmadı.
- Veri/API/model başlatılmadı; test açılmadı.
- BDDK/BETAM/Google Trends yeniden açılmadı.
- Kullanıcının dirty/untracked dosyalarına dokunulmadı.

## 6. Açık Sorular / PM Onayı Gerekenler

Seçenek 2'de yeni aday aramasına devam etmek, kapıları gevşetmek veya yön
değiştirmek artık kullanıcı kararıdır. Üç seçenek:

1. **Seçenek 2'yi kapat:** Kamuya açık as-of bulgusunu meşru negatif sonuç
   olarak kabul et; yeni aday/veri arama.
2. **İleriye dönük gölge vintaj arşivi kur:** Bugünden itibaren seçili kamu
   serilerinin ilk yayımlarını değişmez olarak yakala. Kısa vadede geriye dönük
   kanıt üretmez. İlk en ucuz keşfedilmemiş kontrol TCMB revizyon-yakınsama
   ufkudur; mekanizma uyuşmazlığını tek başına çözmez.
3. **Seçenek 3'e geç:** Ufuk/toplulaştırma/sınıf sözleşmesini yeniden ele al.
   Bağlayıcı hedef tasarımı değişebileceği için kullanıcı kararı olmadan
   başlatılamaz.

Karar notebooklarındaki puanlama tablosu kullanıcı adına doldurulmamıştır.

## 7. Önerilen Sonraki Adım (Başlatılmaz, Yalnızca Önerilir)

Bu tur `BU_TURDA_UYGUN_ADAY_YOK` hükmüyle kapatılsın ve yeni aday araması
durdurulsun. Kullanıcı yukarıdaki üç yönden birini seçene kadar veri erişimi,
gölge arşiv, hedef yeniden-tasarımı veya modelleme başlatılmasın.
