# Doğuş Otomotiv (DOAS) — konsolide grup stok devir hızı/süresi

DOAS (Volkswagen/Audi/Škoda/SEAT/Porsche/Bentley/Scania ithalatçısı-distribütörü + Doğuş Oto
perakende bayi ağı + DOD ikinci el birimini içeren konsolide grup), her çeyrek sonunda
Yatırımcı İlişkileri Sunumu'nun **"Konsolide Bilanço"** bölümünde bilanço/COGS bazlı bir
**stok devir süresi (gün)** rasyosu yayımlıyor: klasik "Days Inventory Outstanding" hesabı
(dönem sonu Stoklar / Satışların Maliyeti × gün sayısı).

**Önemli sınırlama:** Bu, tek bir aracın ortalama kaç günde satıldığını ölçen ilan/unit-level
bir gösterge **değildir**. Grup genelindeki TÜM stokların (yeni araç ithalat stoku + yedek
parça + ikinci el DOD stoku dahil) konsolide bilanço oranından türetilen kurumsal bir KPI'dır.
Yine de şirketin kendisi bunu doğrudan "stok devir hızı/süresi" olarak adlandırıp yatırımcılara
sunuyor ve büyük bir bayi/distribütör zincirinin operasyonel stok-devir göstergesi olarak
projeye değer katıyor.

## Dosya

### `doas_stok_devir_ceyreklik.csv`

2021-12-31 → 2026-03-31 arası **10 çeyreklik gözlem** (aradaki çeyrekler bu turda taranmadı,
aşağıya bakın). Her satır, indirilen gerçek yatırımcı sunumu PDF'inin ilgili sayfası **Read
aracıyla görsel olarak açılıp tablo satırından okunarak** doğrulandı (metin çıkarma/tahmin
değil).

## Metodoloji kırılması

`satir_adi` sütunu 2025 sonu ile 2026 1. çeyrek arasında **"Stok Devir Hızı (gün)"**'nden
**"Stok Devir Süresi (gün)"**'ne değişti. Hesaplama/konumun aynı göründüğü (aynı satır, aynı
tablo konumu) değerlendirildi — muhtemelen yalnızca isimlendirme değişikliği — ama bu resmi
olarak doğrulanmadı; kullanılırken not edilmeli.

## Bilinmeyenler / eksik çeyrekler

- 2022 1.Ç/3.Ç, 2023 1.Ç/2.Ç, 2024 1.Ç/2.Ç, 2025 1.Ç/2.Ç dönemlerine ait aynı formatta ek
  sunumlar da DOAS arşivinde mevcut (aylık yayımlanıyorlar) ancak zaman kısıtı nedeniyle bu
  turda yalnızca 5 sunum dosyası (Ekim 2022, Aralık 2023, Aralık 2024, Aralık 2025, Ağustos
  2026) açılıp doğrulandı. Seri istenirse aynı yöntemle tam çeyreklik hale genişletilebilir.
- TL enflasyon muhasebesi (TMS 29) etkisi rasyoyu etkiliyor olabilir; bu düzeltilmedi, ham
  rapor değeri kullanıldı.
- `www.dogusotomotiv.com.tr` WebFetch'i 403 ile engelliyor; PDF'lere yalnızca tarayıcı
  User-Agent'lı indirme ile erişilebildi. Seriyi genişletecek bir sonraki turun da aynı
  yöntemi (indirme + görsel sayfa okuma) kullanması gerekiyor.

## Aranıp bulunamayan kaynaklar (negatif sonuç)

Borusan Oto, Otokoç Ekspres, Bayraktar Oto, Alarko Oto için yapılan aramalarda hiçbir somut
"stok devir/ortalama satış süresi" KPI'sı bulunamadı (yalnızca genel eğitim içerikleri çıktı).
Bir haber sitesinde (technopat.net, 17 Aralık 2025) "2. el otomobillerin ortalama ilanda kalma
süresi 22,2 gün" ifadesi bulundu ama kaynağı "sektör verilerine göre" şeklinde belirsiz
bırakılmış, hangi kurumdan geldiği tespit edilemedi — bu yüzden **kullanılmadı**.

## Kapsam ve target kullanımı

`stok_devir_suresi_gun` çeyreklik bir seridir; aylık target'larla birleştirilmek istenirse
ay bazına indirgeme (forward-fill/interpolasyon) gerekir, ham veri çeyreklik kalmalıdır. Küçük
örneklem (10 nokta, düzensiz aralıklarla) ve grup-geneli (araç-dışı stok içeren) tanım nedeniyle,
bu kaynağın doğrudan bir target'tan çok, aylık targetlara (örn. `target_betam_dom_gun`) ek bir
**çeyreklik doğrulama/çapraz-kontrol serisi** olarak kullanılması önerilir.
