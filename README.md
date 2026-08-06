# Araç Piyasası Fiyat Yönü Tahmini

Bu repo, araç piyasasında fiyat yönünü (up / down / stable) tahmin edecek bir
ML sisteminin geliştirici ekibine "gelmiş geçmiş en iyi baseline" ile
başlamasını sağlayacak, **literatür temelli, veri odaklı bir piyasa yönü
tahmin projesidir**. İki iç içe aşamadan oluşur: (A) tamamlanmış bir literatür
taraması ve karar-odaklı sentez, (B) bu taramanın bulgularını gerçek Türkiye
araç piyasası verisiyle test eden, hâlâ aktif süren bir veri mühendisliği ve
keşif çalışması.

## Aşama A — Literatür Tarama ve Sentez

Faz 0-7 tamamlandı (`durum: tamamlandi`); Faz 8 (başarısızlık modları) ve
sentez raporu (Faz 09) **taslak** durumunda, proje sahibi onayı bekliyor —
bkz. `docs/00_karar_kaydi.md` (K1-K13 kapsam kararları) ve
`docs/00_master_plan_literatur_taramasi.md`.

- Master plan `docs/00_master_plan_literatur_taramasi.md` içindedir; tarama
  fazlara bölünmüştür.
- Her fazın taraması claude.ai Deep Research ile yapılır; kullanılan prompt
  `prompts/` (kök) altına, çıktı `docs/` altına eklenir.
- Organizasyon, tutarlılık kontrolü, sentez ve format dönüşümleri Claude Code
  ile bu repo içinde yürütülür.
- Döküman standartları ve kalite kontrol listesi: `docs/standards.md`.
- PDF/pptx dönüşümleri: `exports/` (Git'e girmez).

## Aşama B — Veri Mühendisliği ve Keşif (AKTİF)

Aşama A'nın bulgularını gerçek veriyle test eden, adım adım ilerleyen aktif
çalışma. Şu ana kadarki sıra:

1. **MVP çekirdek veri seti** (2025, 12 ay) — `data/processed/mvp/`.
2. **Genişletme** (2024-01 → içinde bulunulan ay) — dışsal faktörler eklendi.
3. **2018'e geriye genişletme** — 9/10 seri 2018-01'e kadar uzatıldı (proxy
   fiyat kaynak kısıtı nedeniyle 2024-01 öncesi dolu değil).
4. **Korelasyon / hedef-aday analizi** — 6 hedef adayı × feature seti.
5. **Hedef keşfi (noter devir × DOM)** — kompozit "piyasa aktivite endeksi"
   denemesi — tamamlandı, sonuçlar `pm_rapor_hedef_kesif.md`'de.
6. **2015'e geriye genişletme** — proxy fiyat (BETAM) ve ENAG hariç tüm
   dışsal özellikler 2015-01'e kadar uzatıldı (alım gücü/erişim endeksi
   erişim engeli nedeniyle yalnızca 2018-01'den itibaren dolu); sonuçlar
   `pm_rapor_genisletme_2015.md`'de.
7. **ENAG kontrol serisi geriye genişletme (denendi)** — hedef 2018-01
   idi; ENAG'ın 2020'de kurulmuş olması nedeniyle 2018-2019 için veri
   yok, 2021-01→2023-12 (kısmi, kalite düşen) kapsandı, ana 2024-2026
   dosyasıyla birleştirilmedi; sonuçlar `pm_rapor_enag_2018_genisletme.md`'de.

**Durum:** Aktif Aşama B target'ı **K9 ile kararlaştırılmıştır** — günlük
granülerlikte `noter_devir_otomobil_adet` (hacim) serisinin doğrudan
üç-sınıflı (up/stable/down) yönü. K1'in aylık tahmin ufku, bu çalışma
kapsamında bir varsayım olarak kullanılıyor (nihai/bağlayıcı hedef
değişken/ufuk/eşik seçimi hâlâ proje sahibinin nihai onayına açıktır;
K9 bu arada geçerli aktif çalışma hedefidir). `data/` klasörüne bkz.

### Nasıl çalışır (veri mühendisliği döngüsü)

- Her görev, proje sahibinden gelen bir **prompt** ile başlar; Claude Code
  çalışmaya başlamadan önce promptu `prompts/veri/` (veya kapsam dışı
  navigasyon/meta işleri için `prompts/` kökü) altına **öz-arşivler**.
- Her veri mühendisliği görevi bitince `data/processed/raporlar/` altına bir
  **PM raporu** (`pm_rapor_<aşama_adı>.md`) üretilir — kısa, dürüst,
  denetlenebilir; Git'e girer (veri dosyalarının aksine).
- Otonomi sınırı (hangi işler onay beklemeden yürütülür, hangileri proje
  sahibinin kararını gerektirir): `CLAUDE.md` → "Otonomi Sınırı" bölümü.

## Klasör Yapısı

| Yol | İçerik |
|---|---|
| `docs/` | Master plan, karar kaydı, 8 numaralı faz çıktısı, sentez dökümanı |
| `docs/sentez/` | Sentez/sunum kaynak dosyaları için ayrılmış (şu an boş — sentez dökümanı `docs/09_sentez_ve_karar_dokumani.md`'de duruyor) |
| `prompts/` (kök) | Tarama fazlarında kullanılan promptların arşivi + bu repo'nun navigasyon/meta promptları (ör. bu döküman) |
| `prompts/veri/` | Veri mühendisliği promptlarının arşivi (MVP, genişletme, fizibilite, korelasyon, hedef keşfi) |
| `scripts/veri/` | Veri çekme/temizleme/birleştirme/analiz kodu (kaynak adına göre, tekrar çalıştırılabilir) |
| `notebooks/` | Proje sahibinin serbest/keşifsel Jupyter notebook analizleri (`scripts/veri/`'nin aksine — pipeline değil, ad-hoc) |
| `data/raw/` | Kaynak bazlı ham veri (usdtry, tüfe, proxy_fiyat, faiz, odmd, otv, osd, tüketici_güveni, noter_devir, alım_gücü) |
| `data/processed/mvp/` | MVP (2025) birleşik + etiketli tablo |
| `data/processed/genisletme/` | Genişletme (2015/2018/2024-bugün) birleşik + etiketli tablo |
| `data/processed/analiz/` | Korelasyon matrisi, hedef-aday karşılaştırması, piyasa aktivite endeksi, keşifsel grafikler |
| `data/processed/raporlar/` | Veri sözlüğü, temizleme raporu, PM raporları (Git'e giren tek veri-ilişkili içerik) |
| `data/` (genel) | Kaynak/format ayrımı, K5 kısıtı, bilinen sınırlar — bkz. `data/README.md` |
| `exports/` | docx/pptx/pdf dönüşümleri (Git'e girmez) |

## Durum

**Aşama A — Literatür Tarama ve Sentez**

- [x] Faz 0 — Planlama promptu hazırlandı
- [x] Faz 0 — Master plan üretildi ve onaylandı
- [x] Faz 1 — Problem Çerçeveleme ve Label Tasarımı
- [x] Faz 2 — Araç Piyasasına Özgü Dinamikler
- [x] Faz 3 — Finansal Piyasa Yön Tahmini Literatürü
- [x] Faz 4 — Araç Fiyat Tahmini Akademik Literatürü
- [x] Faz 5 — Feature Engineering ve Alternatif Veri Kaynakları
- [x] Faz 6 — Model Mimarileri ve Ensemble Stratejileri
- [x] Faz 7 — Validasyon, Metrik Seçimi, Backtest Metodolojisi
- [ ] Faz 8 — Başarısızlık Modları, Tuzaklar, Data Leakage Riskleri (taslak, onay bekliyor)
- [ ] Sentez raporu (`09_sentez_ve_karar_dokumani.md`) (taslak, onay bekliyor)
- [x] Sunum (`exports/arac_piyasa_yon_tahmini_sentez.pptx`, `arac_dissal_faktorler_sunum.pptx`)

**Aşama B — Veri Mühendisliği ve Keşif**

- [x] MVP çekirdek veri seti (2025, 12 ay)
- [x] Genişletme (2024-01 → bugün) — dışsal faktörler
- [x] 2018-01'e geriye genişletme (proxy fiyat hariç 9/10 seri)
- [x] Korelasyon / hedef-aday analizi (6 aday × feature seti)
- [x] Hedef keşfi — noter devir × DOM, kompozit piyasa aktivite endeksi
- [x] 2015-01'e geriye genişletme (proxy fiyat/ENAG hariç; alım gücü/erişim
      endeksi yalnızca 2018-01'den itibaren)
- [x] ENAG kontrol serisi geriye genişletme denemesi (kısmi: 2021-01→2023-12,
      2018-2020 elde edilemedi, ana dosyayla birleştirilmedi)
- [x] Aktif hedef tanımı — K9 ile kararlaştırıldı: günlük granülerlikte
      `noter_devir_otomobil_adet` üç-sınıf yönü (aşağıya bkz.); K1'in aylık
      tahmin ufku bu çalışma için varsayımdır. Nihai/bağlayıcı hedef
      değişken seçimi (K1) proje sahibinin nihai onayına hâlâ açıktır.
- [ ] İlan fiyatı yön hedefi (K8) — dondurulmuş: proxy_fiyat_cari_tl
      serisinde 28 dolu fiyat ayı / yaklaşık 25 hesaplanabilir yön etiketi
      N<50 (N12)
      keşifsel geçidinde kaldığı için model eğitimi başlatılamıyor. Bu hedef
      terk edilmedi, yalnızca N≥50'ye ulaşana kadar aktif çalışma dışıdır.
- [x] **Aktif operasyonel hedef — hacim yönü, doğrudan üç sınıf (K9,
      2026-08-06):** `noter_devir_otomobil_adet` (hacim) serisinin bir
      sonraki takvim ayına göre up/stable/down yönü, sabit ±%5 eşik,
      günlük frekans. Target-bağımsız değerlendirme altyapısı
      (`scripts/model/yon_degerlendirme.py`, 21 pytest testi) + AutoGluon
      `TabularPredictor(problem_type="multiclass")` ile DF-A/DF-B ayrı
      eğitim (`scripts/model/model_06_hacim_yon_siniflandirma.py`).
      Test sonucu (purge'li kronolojik split, ay-ağırlıklı): **DF-A**
      MCC=0.242/macro-F1=0.276/acc=%33 (n=12 ay) — mevsimsel-yön(t-12ay)
      baseline'ı (MCC=0.394/F1=0.579/acc=%58) **GEÇEMEDİ**, "sinyal yok"
      dürüst bulgusu (N6/N13). **DF-B** (yalnızca 15 bağımsız eğitim ayı —
      KEŞİFSEL) MCC=0.387/macro-F1=0.413/acc=%50 (n=6 ay), tüm naif
      baseline'ları geçti ama örneklem çok küçük, genellenebilir değil.
      Olasılıklar RAW (kalibre edilmemiş). Ayrıntı:
      `pm_rapor_hacim_yon_3sinif_baseline.md`, karar gerekçesi
      `docs/00_karar_kaydi.md` K9.
- [ ] Model kurma / tahmin — K8 (fiyat) hedefi için N≥50 eşiğine ulaşılana
      kadar başlatılmadı; hacim hedefi (K9) için DF-A/DF-B baseline denemesi
      yukarıda tamamlandı, sonraki iterasyon (feature/model geliştirme) PM
      onayı bekliyor. (`scripts/model/model_01`/`model_02` — commit'li,
      AutoGluon TimeSeries SEVİYE baseline'ı + PM raporu
      `pm_rapor_modelleme_fazi_1.md`/`_fazi_2.md` — bu üç-sınıf yön
      protokolünün parçası değildir ama PM onaylı ayrı bir çalışmadır.
      `model_03`/`model_04`/`model_05` ise untracked, PM onayından geçmemiş
      denemelerdir — bu paketin dışındadır.)
