# -*- coding: utf-8 -*-
"""target_quickfinans_dom_gun backtest calismasini aciklamali, yeniden calistirilabilir notebooka aktarir."""

from __future__ import annotations

import ast
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts" / "hiz_target_backtest_pipeline.py"
OUTPUT = ROOT / "notebooks" / "08_autogluon_target_quickfinans_dom_gun.ipynb"


def get_functions(names: list[str]) -> str:
    text = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    by_name = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    missing = set(names) - set(by_name)
    if missing:
        raise RuntimeError(f"Kaynak scriptte bulunamayan fonksiyonlar: {sorted(missing)}")
    blocks = ["\n".join(lines[by_name[name].lineno - 1 : by_name[name].end_lineno]) for name in names]
    return "\n\n".join(blocks)


nb = nbf.v4.new_notebook()
nb["metadata"]["kernelspec"] = {
    "display_name": "Python (Araç Piyasası - AutoGluon)",
    "language": "python",
    "name": "arac-piyasasi-autogluon",
}
nb["metadata"]["language_info"] = {"name": "python", "version": "3.12"}

cells = []

cells.append(
    nbf.v4.new_markdown_cell(
        r"""# İkinci El Ortalama Stokta Kalma Süresi — `target_quickfinans_dom_gun` (AutoGluon TimeSeries)

> **Güncelleme (2. tur):** Bu hedef ilk eklendiğinde yalnızca 14 aylık veri vardı ve backtest
> yalnızca 2 ay çalışabiliyordu (istatistiksel olarak anlamsız örneklem). Kaynağı 2024-09'a
> kadar geriye genişleten ikinci bir araştırma turundan sonra (bkz.
> `data/quickfinans_stokta_kalma/README.md`) backtest artık **6 ay**a ulaştı — diğer iki
> hedefle (`target_betam_dom_gun`, `target_indicata_satis_ilan_orani_pct`) aynı standart.

Bu defter, Quick Finans / SmartIQ "2. El Oto Raporu"nun ikinci el araçlar için ortalama
**stokta kalma süresini** (gün) tahmin eden rolling-origin backtest çalışmasını üretir ve
doğrular. Diğer üç hedeften (`target_betam_dom_gun`, `target_indicata_satis_hizi_gun`,
`target_indicata_satis_ilan_orani_pct`) farkı: bu hedefin ham kaynağı
`data/target_bazli_birlesik_setler/feature_master_aylik.csv` içinde **yer almaz** — tamamen
harici, yeni eklenmiş bir kaynaktan (`data/quickfinans_stokta_kalma/`) okunur.

\[
\text{target\_quickfinans\_dom\_gun}_t = \text{stokta\_kalma\_suresi\_gun\_pazar}_t
\]

(`data/quickfinans_stokta_kalma/quickfinans_aylik_stokta_kalma.csv`'deki pazar-ortalaması
sütunu, referans ayına göre birebir.)

- Veri: **20 gözlem, 2024-09 → 2026-06** (2024-11 ve 2024-12'de iç boşluk var; Indicata'nın
  2025+ döneminde kaybettiği `ortalama_satis_hizi_gun` metriğine tamamlayıcı olarak toplandı)
- AutoGluon ayarı: `medium_quality`, fold başına `time_limit=45sn`
- Tahmin ufku: 1 ay (`prediction_length=1`)
- Backtest: **6 ay** (2026-01 → 2026-06) — proje standardı `MAX_BACKTEST_AY` tavanına ulaşıldı
- Referans: "geçen yılın aynı ayı" (t-12) naive baseline"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 1. Kütüphaneler ve sabitler

Bu notebook proje kökünden veya `notebooks/` klasöründen açılabilir; `.venv-ag` ortamını gerektirir."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """from pathlib import Path
import json

import numpy as np
import pandas as pd
from IPython.display import display, Image

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent

FEATURE_PATH = ROOT / "data" / "target_bazli_birlesik_setler" / "feature_master_aylik.csv"
QUICKFINANS_PATH = ROOT / "data" / "quickfinans_stokta_kalma" / "quickfinans_aylik_stokta_kalma.csv"
OUT_DIR = ROOT / "outputs" / "hiz_target_backtest" / "target_quickfinans_dom_gun"

TARGET = "target_quickfinans_dom_gun"
DATE_COL = "referans_ayi"

print("Proje kökü:", ROOT)
print("Hedef:", TARGET)"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 2. Sızıntısız feature tablosu kurma — harici hedef kaynağı

`feature_master_aylik.csv`'deki tüm aylık feature'lar hedefe eklenir. Diğer üç hedeften farklı
olarak burada **"hedefin kendi ham kaynağı" hariç tutma kuralı devreye girmez** — çünkü Quick
Finans stokta kalma süresi `feature_master_aylik.csv` içinde bir feature olarak zaten mevcut
değil (`pipeline`'daki `EXTERNAL_TARGET_SOURCES` sözlüğü bu hedefi harici CSV'den okur ve
`referans_ayi` üzerinden birleştirir). Yine de iki genel koruma geçerli kalır:

1. **Genel sızıntı yasakları** (`modelleme_sizinti_kisitlari.csv`'nin `tum_targetlar` satırları).
2. **`indicata_*`/`arabam_*`/`betam_*` ailesinin aynı-ay versiyonları** — 1 ay gecikmeli
   (`lag1`) türevleriyle değiştirilir (bu aile Quick Finans'ın kendisiyle aynı sektörden farklı
   kaynaklar olduğu için, dolaylı da olsa erken-yayın riski taşıyabilir)."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["build_feature_table"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 3. Korelasyon filtresi — |Pearson| < 0.1 ele

`min_periods=12` şartıyla hedefle mutlak korelasyonu 0.1 altında olan veya hesaplanamayan
feature'lar elenir. Hedefte 20 gözlem var; bu diğer iki tam hedeften (28 ve 43 gözlem) hâlâ
daha az, bu yüzden korelasyon tahminleri biraz daha gürültülü olabilir ama artık ilk sürümdeki
(n=14, min_periods eşiğine çok yakın) kadar kırılgan değil."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["korelasyon_filtresi"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 4. Çoklu-doğrusallık filtresi — |Pearson| > 0.9 ele

Kalan feature'lar arasında mutlak korelasyonu 0.9'u aşan çiftlerden target ile daha düşük
korelasyona sahip olan elenir."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["coklu_dogrusallik_azalt"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 5. Rolling-origin backtest ayları ve tek-adım eğitim/tahmin

Bir ay `m` geçerli bir backtest ayı sayılır ancak (a) `m-12` de hedefte mevcutsa ve (b) `m`'den
önce en az `MIN_TRAIN_AY=8` ay eğitim verisi varsa. Seri artık 2024-09'da başladığından, bu iki
şartı sağlayan aylar 2025-09'dan itibaren mevcut; proje standardı `MAX_BACKTEST_AY=6` tavanı
nedeniyle en yakın **6 ay** (2026-01 → 2026-06) seçilir."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["find_backtest_months", "prev_actual_value", "fit_predict_one_step"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 6. Metrikler — yön doğruluğu, MAE, RMSE, MASE, bias

- **Yön doğruluğu**: tahmin edilen değişimin yönü (bir önceki bilinen gerçek değere göre),
  gerçekleşen yönle eşleşme oranı.
- **MASE**: MAE'nin, tüm geçmişteki ortalama mutlak 12-aylık farka bölünmüş hali.
- **Bias**: `ortalama(tahmin - gerçek)`."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["compute_metrics"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 7. Uçtan uca çalıştırma fonksiyonu"""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["run"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 8. Çalıştır veya mevcut checkpoint'i yükle

`RUN_TRAINING=False` mevcut tamamlanmış sonuçları yükler. Baştan çalıştırmak isterseniz `True`
yapın (6 fold, ~5 dakika sürer)."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """RUN_TRAINING = False

if RUN_TRAINING:
    sonuc = run(TARGET)
else:
    sonuc = json.loads((OUT_DIR / "metrikler.json").read_text(encoding="utf-8"))

backtest_df = pd.read_csv(OUT_DIR / "backtest_sonuclari.csv")
korelasyon_ozet = pd.read_csv(OUT_DIR / "korelasyon_filtre_ozeti.csv")
coklu_dogrusallik = pd.read_csv(OUT_DIR / "coklu_dogrusallik_ciftleri.csv")
final_features = pd.read_csv(OUT_DIR / "final_feature_seti.csv")

print("Durum:", sonuc["durum"])
print("Backtest ayları:", sonuc["backtest_aylari"], "( n =", sonuc["backtest_ay_sayisi"], ")")"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 9. Güvenlik ve bütünlük kontrolleri

Target formülünün harici Quick Finans dosyasıyla birebir eşleştiğini, harici-kaynak mekanizması
nedeniyle "ham kaynak kolonu" hariç tutma listesinin boş olması gerektiğini, backtest ayı
sayısının beklenen 6 ile uyuştuğunu ve tahminlerde eksik/sonsuz değer olmadığını doğrular."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """quickfinans_ham = pd.read_csv(QUICKFINANS_PATH)[[DATE_COL, "stokta_kalma_suresi_gun_pazar"]]
feature_tablosu = pd.read_csv(FEATURE_PATH)[[DATE_COL]].merge(
    quickfinans_ham.rename(columns={"stokta_kalma_suresi_gun_pazar": TARGET}), on=DATE_COL, how="left"
)
karsilastirma = feature_tablosu.dropna(subset=[TARGET])
assert len(karsilastirma) == 20, f"Beklenen 20 gozlem, bulunan {len(karsilastirma)}"

assert sonuc["durum"] == "TAMAMLANDI"
assert sonuc["n_obs_toplam"] == 20
assert sonuc["backtest_ay_sayisi"] == 6
assert sonuc["backtest_aylari"] == ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
assert sonuc["disislanan_kolonlar"]["hedefin_ham_kaynak_kolonu_disi"] == [], (
    "Harici hedef icin ham-kaynak-disi listesi bos olmali (feature_master_aylik.csv'de "
    "esdeger kolon yok)"
)
assert not backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].isna().any().any()
assert np.isfinite(backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].values).all()

# Baseline'in gercekten t-12 karsiligi oldugunu dogrula: 2026-01 baseline'i == 2025-01 gercek degeri
ocak_2025 = quickfinans_ham.loc[quickfinans_ham[DATE_COL] == "2025-01", "stokta_kalma_suresi_gun_pazar"].iloc[0]
ocak_2026_baseline = backtest_df.loc[backtest_df["ay"] == "2026-01", "baseline_gecen_yil_ayni_ay"].iloc[0]
assert ocak_2025 == ocak_2026_baseline == 51.0

print("Target formülü ve t-12 baseline mantığı doğrulandı.")
print("Bütünlük kontrolleri geçti. Final feature sayısı:", len(final_features))"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 10. Sonuçlar — model vs "geçen yılın aynı ayı" baseline'ı

`n_test_ay=6` — artık diğer iki tam hedefle aynı örneklem büyüklüğünde, sonuçlar anlamlı
şekilde okunabilir."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """metrik_tablosu = pd.DataFrame(
    {
        "Model": sonuc["model_metrikleri"],
        "Baseline (t-12)": sonuc["baseline_metrikleri_gecen_yil_ayni_ay"],
    }
).T[["yon_dogrulugu", "mae", "rmse", "mase", "smape_pct", "bias", "n_test_ay"]]

display(metrik_tablosu)
display(backtest_df)
display(final_features)

grafik_yolu = OUT_DIR / "tahmin_grafigi.png"
if grafik_yolu.exists():
    display(Image(filename=str(grafik_yolu)))"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 11. Bilinen sınırlamalar

- **Seri genişletmesi tek biçimli değil.** Ana dosyadaki 20 gözlemin tamamı aynı
  pazar/binek/ticari formatında ve WebFetch ile doğrulanmış, ama 2024-11 ve 2024-12'de iç
  boşluk var (bu aylar için uyumlu format bulunamadı — bkz.
  `quickfinans_erken_donem_2023_2024_farkli_format.csv`). `build_feature_table` bu iç
  boşlukları `ffill/bfill` ile dolduruyor; bu, 9 yıllık uydurma bir geçmiş yaratan (ve daha önce
  `target_betam_dom_gun` çalışmasında düzeltilen) hatadan farklı, yalnızca 2 aylık ve
  sınırlı-kapsamlı standart bir uygulamadır.
- **2023 ve 2024'ün ilk yarısı seriye dahil edilmedi.** O dönemin raporları farklı bir
  metodoloji (segment bazlı B/C/D/E) kullanıyor gibi görünüyor ve bir ay (2024-01) için iki
  bağımsız kaynak birbiriyle doğrudan çelişen rakamlar veriyor (52 gün vs 70 gün) — bu veriler
  metodoloji sürekliliği garanti edilemediği için ana seriye **bilerek eklenmedi**.
- En çarpıcı bulgu (bkz. 10. bölüm): baseline'ın **+4.17 gün sistematik pozitif bias'ı** —
  "geçen yılın aynı ayı" yöntemi, seride yaşanan genel kısalma trendini yakalayamayıp sürekli
  fazla tahmin ediyor. Model, MASE=0.449 (baseline: 0.667) ve MAE=2.80 gün (baseline: 4.17 gün)
  ile bu trendi hem baseline'dan hem de serinin kendi 12-aylık mevsimsel oynaklığından daha iyi
  takip edebiliyor; model kendisi de hafif negatif bias taşıyor (-1.75 gün — sistematik olarak
  biraz düşük tahmin ediyor), ama bu baseline'ın pozitif sapmasından çok daha küçük.
- Yön doğruluğunda tablo bu turda tersine döndü: model %60 (3/5), baseline **%80 (4/5)** tuttu —
  mutlak hata metriklerinde (MAE, RMSE, MASE, sMAPE) model net üstün olsa da, "gelecek ay çıkar
  mı düşer mi" sorusunda şu an baseline modelden daha güvenilir; bu karşılaştırma yalnızca 5
  geçerli (sıfır-olmayan) yön değişimine dayandığından tek bir fold'un sonucu oranı ~%20 oynatır,
  bu yüzden temkinli okunmalı."""
    )
)

nb["cells"] = cells
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUTPUT)
print(OUTPUT)
