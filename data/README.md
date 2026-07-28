# data/ — Araç Piyasası Fiyat Yönü Verisi

Bu klasör, araç piyasası fiyat yönü tahmini projesinin kamuya açık kaynaklardan
çekilen aylık zaman serisi veri setlerini barındırır. İki aşama iç içedir:

- **MVP (2025, 12 ay)** — ilk prototip, yalnızca 2025 (bkz.
  `prompts/veri/01_mvp_cekirdek_veri_prompt.md`).
- **Genişletme (2018-01 → içinde bulunulan ay)** — daha uzun, dışsal faktörleri
  de içeren seri (bkz. `prompts/veri/03_genis_veri_cekme_prompt.md` ve
  `prompts/veri/06_genisletme_2018_korelasyon_prompt.md`). Proxy fiyat (BETAM)
  yalnızca 2024-01'den itibaren dolu — 2018-2023 için bilinen bir kısıt
  (bkz. `pm_rapor_genisletme2018_korelasyon.md`).
- **Hedef keşfi — noter devir × DOM** — kompozit "piyasa aktivite endeksi"
  denemesi, hedef seçimi (K1) için karar değil kanıt üretir (bkz.
  `prompts/veri/08_hedef_kesif_noter_dom_prompt.md` ve
  `pm_rapor_hedef_kesif.md`).
- **ENAG E-TÜFE kontrol serisi (2024-01 → 2026-06)** — TÜİK TÜFE'ye paralel,
  ana deflatörü DEĞİŞTİRMEYEN kontrol serisi (bkz.
  `prompts/veri/12_enag_veri_cekme_prompt.md` ve `pm_rapor_enag_cekme.md`).
  enagrup.org resmi sitesi şu an erişilemez durumda — B/C seviyesi kaynak
  kullanıldı, ayrıntı raporda.

**UYARI:** Bu klasöre şirket içi, lisanslı veya özel veri **konulmaz** (karar
K5 — `docs/00_karar_kaydi.md`). Yalnızca kamuya açık kaynaklardan (TCMB EVDS,
TÜİK, BETAM sahibindex, arabam.com, ODMD vb.) çekilen veri kullanılır.

Veri dosyaları (`.csv`/`.xlsx`/`.json`) `.gitignore` ile Git dışıdır; yalnızca
klasör yapısı (`.gitkeep`) ve `processed/raporlar/` altındaki `.md` belgeleri
versiyonlanır. Prompt/kod versiyonlanır, çekilen veri versiyonlanmaz.

## Klasör yapısı

Her iki alt klasör (`raw/`, `processed/`) kendi içinde **kaynak/kategori
adına göre** alt klasörlere ayrılmıştır (karışıklığı önlemek için — birden
fazla format (csv/xlsx/json) ve birden fazla aşama (2025 MVP + 2024-bugün
genişletme) aynı düz klasörde biriktiğinde okunması zorlaşıyordu).

```
data/
├── raw/                    # her kaynaktan çekilen ham/ara dosyalar
│   ├── usdtry/              USD/TRY (TCMB EVDS3)
│   ├── tufe/                 TÜFE (TCMB EVDS3 — 2003=100 + 2025=100 zincirlenmiş)
│   ├── proxy_fiyat/          proxy ilan fiyatı (BETAM sahibindex + arabam.com)
│   ├── faiz/                 taşıt kredisi faizi + politika faizi (TCMB EVDS3)
│   ├── odmd/                 sıfır araç satış adetleri (ODMD basın bültenleri)
│   ├── otv/                  ÖTV event-dummy (Resmî Gazete/haber taraması)
│   ├── osd/                  OSD yerli üretim, binek+kamyonet (TCMB EVDS3)
│   ├── tuketici_guveni/      tüketici güven endeksi + otomobil satın alma ihtimali (TCMB EVDS3)
│   ├── noter_devir/          noter devir adedi, toplam+otomobil (TÜİK veri portalı)
│   ├── alim_gucu/            brüt ücret-maaş endeksi, alım gücü proxy'si (TÜİK veri portalı, çeyreklik)
│   └── enag/                 ENAG E-TÜFE kontrol serisi (ENAG resmi X hesabı + haber ajansları, 2024-01→bugün)
└── processed/               # birleştirilmiş / etiketlenmiş / belgelenmiş çıktılar
    ├── mvp/                  MVP (2025) birleşik + etiketli tablo
    ├── genisletme/            genişletme (2018-bugün) birleşik + etiketli tablo
    ├── analiz/                korelasyon matrisi, hedef-aday karşılaştırması, zaman serileri,
    │                          piyasa aktivite endeksi (noter×DOM keşfi), TÜİK-ENAG karşılaştırması (keşifsel)
    │   └── gorseller/          keşifsel karşılaştırma grafikleri (ör. tufe_vs_enag.png)
    └── raporlar/              veri sözlüğü, temizleme raporu, PM raporları (.md — Git'e girer)
```

**Not (script yazarken/güncellerken):** `scripts/veri/*.py` içindeki her script
kendi kategorisinin alt klasörüne okur/yazar (ör. `data/raw/usdtry/`). Yeni bir
kaynak eklerken aynı deseni izleyin — düz `data/raw/` köküne dosya yazmayın.

## Bilinen sınır

Kamuya açık ikinci el araç fiyat serileri (BETAM sahibindex, arabam.com aylık
fiyat endeksi) mix/kompozisyon düzeltmesizdir (karar N1). Bu serilerdeki
`proxy_fiyat` sütunu **yer tutucu (proxy) hedeftir**, nihai hedef değildir.

Diğer bilinen boşluklar ve kaynak-seviyesi ayrıntıları için:
`data/processed/raporlar/veri_sozlugu.md` ve ilgili `pm_rapor_*.md` dosyaları.
