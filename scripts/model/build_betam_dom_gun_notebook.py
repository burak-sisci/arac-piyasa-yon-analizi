# -*- coding: utf-8 -*-
"""target_betam_dom_gun backtest calismasini aciklamali, yeniden calistirilabilir notebooka aktarir."""

from __future__ import annotations

import ast
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts" / "hiz_target_backtest_pipeline.py"
OUTPUT = ROOT / "notebooks" / "07_autogluon_target_betam_dom_gun.ipynb"


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
        r"""# Ortalama İlanda Kalış Süresi — `target_betam_dom_gun` (AutoGluon TimeSeries)

Bu defter, BETAM "Days on Market" (DOM) serisinin bir ay ilerisini tahmin eden rolling-origin
backtest çalışmasını uçtan uca üretir ve doğrular.

\[
\text{target\_betam\_dom\_gun}_t = \text{betam\_dom\_gun}_t
\]

Target, BETAM raporundaki ham `betam_dom_gun` kolonunun **aynı-ay birebir kopyasıdır** (referans
ayında bir aracın ortalama kaç günde satışa/ilandan çıkışa dönüştüğü, gün cinsinden). Bu yüzden
`betam_dom_gun` ham kolonunu feature olarak vermek doğrudan kopya sızıntısı olurdu — aşağıdaki
feature seçimi bunu ve komşu `indicata_*`/`arabam_*`/`betam_*` ailesinin aynı-ay versiyonlarını
açıkça dışlar (bkz. `data/target_bazli_birlesik_setler/modelleme_sizinti_kisitlari.csv`).

- Veri: 28 gözlem, 2024-01 → 2026-06 (seride 2024-05 ve 2025-02 iç boşluk)
- AutoGluon ayarı: `medium_quality`, fold başına `time_limit=45sn`
- Tahmin ufku: 1 ay (`prediction_length=1`)
- Backtest: son 6 ay, **rolling-origin / genişleyen pencere** — her test ayı yalnız kendinden
  önceki gerçek verilerle sıfırdan eğitilen ayrı bir modelle tahmin edilir
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
MASTER_PATH = ROOT / "data" / "birlesik_veri_seti" / "arac_piyasasi_master_veri_seti.csv"
OUT_DIR = ROOT / "outputs" / "hiz_target_backtest" / "target_betam_dom_gun"

TARGET = "target_betam_dom_gun"
DATE_COL = "referans_ayi"

print("Proje kökü:", ROOT)
print("Hedef:", TARGET)"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 2. Sızıntısız feature tablosu kurma

`feature_master_aylik.csv`'deki tüm aylık feature'lar hedefe eklenir. Üç tür kolon dışlanır:

1. **Hedefin kendi ham kaynağı** (`betam_dom_gun`) — birebir kopya, r=1.0 sızıntı.
2. **Genel sızıntı yasakları** (`modelleme_sizinti_kisitlari.csv`'nin `tum_targetlar` satırları):
   karışık aylık/yıllık reel değişim kolonu, ÖTV-en-yakın-olay farkı, audit kolonu.
3. **`indicata_*`/`arabam_*`/`betam_*` ailesinin aynı-ay versiyonları** — bu raporlar referans
   ayından sonra yayımlanıyor; bunun yerine 1 ay gecikmeli (`lag1`) türevleri kullanılır."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["build_feature_table"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 3. Korelasyon filtresi — |Pearson| < 0.1 ele

`min_periods=12` (en az 12 örtüşen gözlem) şartıyla hedefle mutlak korelasyonu 0.1 altında olan
veya hesaplanamayan (NaN) feature'lar elenir."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["korelasyon_filtresi"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 4. Çoklu-doğrusallık filtresi — |Pearson| > 0.9 ele

Kalan feature'lar arasında mutlak korelasyonu 0.9'u aşan çiftlerden target ile daha düşük
korelasyona sahip olan, union-find ile bulunan bağlı bileşen grupları üzerinden elenir."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["coklu_dogrusallik_azalt"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 5. Rolling-origin backtest ayları ve tek-adım eğitim/tahmin

Bir ay `m` geçerli bir backtest ayı sayılır ancak (a) `m-12` de hedefte mevcutsa (baseline için
gerekli) ve (b) `m`'den önce en az `MIN_TRAIN_AY=8` ay eğitim verisi varsa. Son 6 geçerli ay
seçilir. Her fold'da eğitim verisi hedefin **ilk gerçek gözleminden** başlar — aksi halde
`ffill().bfill()`, hedefin başlamadığı erken yılları ilk gerçek değerle geriye doldurup uydurma
bir geçmiş yaratırdı (bu proje bir kullanıcı sorusuyla yakalanıp düzeltilmiş bir hatadır)."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["find_backtest_months", "prev_actual_value", "fit_predict_one_step"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 6. Metrikler — yön doğruluğu, MAE, RMSE, MASE, sMAPE, bias

- **Yön doğruluğu**: tahmin edilen değişimin yönü (bir önceki bilinen gerçek değere göre), gerçekleşen
  yönle eşleşme oranı.
- **MASE**: MAE'nin, tüm geçmişteki ortalama mutlak 12-aylık (mevsimsel) farka bölünmüş hali; `<1`
  serinin kendi mevsimsel oynaklığından daha iyi demektir.
- **sMAPE**: ölçekten bağımsız, yüzdesel hata (`%`); farklı birimdeki hedefleri karşılaştırmaya
  yarar. `|gerçek|+|tahmin|=0` olan noktalar hesaplamadan dışarıda bırakılır.
- **Bias**: `ortalama(tahmin - gerçek)`; pozitifse model sistematik olarak yüksek, negatifse düşük tahmin eder."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["compute_metrics"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 7. Uçtan uca çalıştırma fonksiyonu

`run()` yukarıdaki tüm adımları sırayla uygular, her fold için AutoGluon'u eğitir/tahmin eder,
model ile "geçen yılın aynı ayı" baseline'ını aynı 6 metrikle karşılaştırır ve çıktıları
`outputs/hiz_target_backtest/target_betam_dom_gun/` altına yazar."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["run"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 8. Çalıştır veya mevcut checkpoint'i yükle

`RUN_TRAINING=False` mevcut tamamlanmış sonuçları yükler (6 fold × AutoGluon eğitimi ~birkaç
dakika sürer). Baştan çalıştırmak için `True` yapın — bu, `.venv-ag` ortamında `autogluon.timeseries`
gerektirir."""
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
print("Backtest ayları:", sonuc["backtest_aylari"])"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 9. Güvenlik ve bütünlük kontrolleri

Target formülünün ham kolonla birebir eşleştiğini, backtest ayı sayısının beklenenle uyuştuğunu
ve tahminlerde eksik/sonsuz değer olmadığını doğrular."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """master = pd.read_csv(MASTER_PATH)[[DATE_COL, TARGET, "betam_dom_gun"]]
karsilastirma = master.dropna(subset=[TARGET])
fark = (karsilastirma[TARGET] - karsilastirma["betam_dom_gun"]).abs().max()
assert fark < 1e-9, "target_betam_dom_gun, betam_dom_gun ham kolonuyla birebir eşleşmiyor"

assert sonuc["durum"] == "TAMAMLANDI"
assert sonuc["backtest_ay_sayisi"] == 6
assert sonuc["backtest_aylari"] == ["2025-12", "2026-01", "2026-03", "2026-04", "2026-05", "2026-06"]
assert not backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].isna().any().any()
assert np.isfinite(backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].values).all()
assert "betam_dom_gun" not in final_features["feature"].tolist(), "ham kaynak kolonu sizmis"

print("Target formülü doğrulandı. En büyük fark:", fark)
print("Bütünlük kontrolleri geçti. Final feature sayısı:", len(final_features))"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 10. Sonuçlar — model vs "geçen yılın aynı ayı" baseline'ı"""
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
        """## Bilinen sınırlamalar

- Örneklem küçük (28 ay, 6 test fold'u); tek bir yanlış/doğru tahmin yön doğruluğunu ~%17 oynatır.
- Serideki 2 iç boşluk ay (2024-05, 2025-02), eğitim verisi hazırlanırken ileri/geri doldurma ile
  kapatılır — bu, uzun bir uydurma geçmiş yaratan (ve bu notebook'un temel aldığı düzeltmeyle
  giderilen) hatadan farklı, standart ve sınırlı kapsamlı bir uygulamadır.
- Model, tüm 6 metrikte (yön doğruluğu, MAE, RMSE, MASE, sMAPE, bias) baseline'ı geçiyor ama yön
  doğruluğu (%50) sınırlı; tek başına "gelecek ay çıkar mı, düşer mi" kararı için mutlak hata
  metrikleriyle birlikte okunmalı."""
    )
)

nb["cells"] = cells
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUTPUT)
print(OUTPUT)
