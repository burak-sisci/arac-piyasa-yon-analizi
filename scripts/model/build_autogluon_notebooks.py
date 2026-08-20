"""Build the two readable AutoGluon experiment notebooks."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_DIR = ROOT / "notebooks"


def markdown(text: str) -> dict:
    return {
        "id": uuid4().hex[:8],
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip() + "\n",
    }


def code(text: str) -> dict:
    return {
        "id": uuid4().hex[:8],
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip() + "\n",
    }


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "AutoGluon - Araç Piyasası",
                "language": "python",
                "name": "arac-piyasasi-autogluon",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


COMMON_SETUP = r'''
from pathlib import Path
import importlib.util
import sys

import numpy as np
import pandas as pd
from IPython.display import display

# Notebook notebooks/ klasöründen veya proje kökünden açılabilir.
PROJECT_ROOT = Path.cwd().resolve()
if PROJECT_ROOT.name == "notebooks":
    PROJECT_ROOT = PROJECT_ROOT.parent

assert (PROJECT_ROOT / "data").exists(), "Proje kökü bulunamadı."

try:
    import autogluon.timeseries as agts
except ImportError as exc:
    raise RuntimeError(
        "Bu notebook'u projenin .venv-ag Python ortamıyla çalıştırın."
    ) from exc

pd.set_option("display.max_columns", 100)
pd.set_option("display.float_format", lambda value: f"{value:,.4f}")

print("Proje:", PROJECT_ROOT)
print("Python:", sys.version.split()[0])
print("AutoGluon:", agts.__version__)
'''


LOAD_MODULE = r'''
def load_module(module_name: str, script_path: Path):
    """Bir Python betiğini fonksiyonlarına erişebileceğimiz modül olarak yükler."""
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
'''


THREE_MONTH_CELLS = [
    markdown(r'''
# AutoGluon Time Series — `target_3ay_hiz`

Bu notebook, üç aylık toplam otomobil devir hızını doğrudan tahmin eden nihai doğrulama çalışmasını yeniden üretir.

- AutoGluon ayarı: `medium_quality`
- Tahmin ufku: 3 ay
- Puanlanan çıktı: yalnız üçüncü adımın (`h=3`) medyanı
- Doğrulama originleri: 2020-04 – 2025-03, toplam 60 ay
- Test originleri: 2025-04 – 2026-03; **bu notebookta açılmaz**

Uzun eğitim checkpointlidir. Mevcut sonuçları incelemek için yeniden eğitim gerekmez.
'''),
    code(COMMON_SETUP),
    markdown(r'''
## Targetın anlamı

Karar ayı `t` olmak üzere:

\[
y_t = 100\ln\left(
\frac{V_{t+1}+V_{t+2}+V_{t+3}}
{V_{t-2}+V_{t-1}+V_t}
\right)
\]

- Pozitif değer: gelecek üç aylık toplam hacim, son üç aylık toplamdan yüksek.
- Negatif değer: gelecek üç aylık toplam hacim daha düşük.
- Mutlak değer: logaritmik değişimin şiddeti.

Veri setindeki target gerçekleşme ayına yazılmıştır. AutoGluon `prediction_length=3` ile bu serinin üç adım sonrasını tahmin eder; yalnız `h=3` sonucu iş targetına karşılık gelir.
'''),
    code(r'''
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "birlesik_target_setleri"
    / "target_3ay_hiz_tum_featurelar_final.csv"
)

data = pd.read_csv(DATA_PATH)
data["referans_ayi"] = pd.to_datetime(data["referans_ayi"], errors="raise")
data = data.sort_values("referans_ayi").reset_index(drop=True)

expected_months = pd.date_range(
    data["referans_ayi"].min(), data["referans_ayi"].max(), freq="MS"
)

assert data.shape == (97, 13)
assert data["referans_ayi"].equals(pd.Series(expected_months, name="referans_ayi"))
assert not data["referans_ayi"].duplicated().any()
assert data["target_3ay_hiz"].notna().all()
assert np.isfinite(data["target_3ay_hiz"]).all()

print("Tarih:", data["referans_ayi"].min().date(), "→", data["referans_ayi"].max().date())
print("Gözlem:", len(data))
display(data.head(3))
'''),
    markdown(r'''
## Target formülünü veriden doğrulama

Dosyanın ilk beş satırında önceki üç aylık blok dosya dışında kaldığı için karşılaştırma altıncı satırdan itibaren yapılabilir.
'''),
    code(r'''
volume = data["noter_devir_otomobil_adet"]
rolling_3m = volume.rolling(3).sum()
reconstructed = 100 * np.log(rolling_3m / rolling_3m.shift(3))

check_mask = reconstructed.notna()
max_target_difference = (
    reconstructed[check_mask] - data.loc[check_mask, "target_3ay_hiz"]
).abs().max()

assert max_target_difference < 1e-9
print("Formül doğrulandı. En büyük fark:", max_target_difference)
'''),
    markdown(r'''
## Deney kolları ve sızıntı koruması

- **T0:** yalnız target geçmişi.
- **T1:** noter otomobil devri, OSD binek, ÖTV olayı; tamamı `lag3`.

`lag3`, hedef ayındaki kovaryant değerinin üç ay önceki kaynaktan gelmesini sağlar. Böylece `t+1`, `t+2` ve `t+3` için verilen değerlerin kaynak tarihleri karar ayı `t` veya daha erkendir.
'''),
    code(r'''
T1_FEATURES = [
    "noter_devir_otomobil_adet",
    "osd_binek_adet",
    "otv_event_ay_mi",
]

source = data.set_index("referans_ayi")[T1_FEATURES]
lagged = source.shift(3)
lagged.columns = [f"{column}_lag3" for column in lagged.columns]

sample_origin = pd.Timestamp("2024-04-01")
future_months = pd.date_range(sample_origin + pd.DateOffset(months=1), periods=3, freq="MS")

for future_month in future_months:
    source_month = future_month - pd.DateOffset(months=3)
    assert source_month <= sample_origin
    print(f"Tahmin ayı {future_month:%Y-%m} ← kaynak {source_month:%Y-%m}")
'''),
    markdown(r'''
## Eğitimi çalıştırma veya mevcut checkpointi kullanma

`RUN_TRAINING=False` mevcut tamamlanmış sonuçları yükler. Baştan eğitim için `True` yapın. Eğitim yarıda kesilirse `RESUME=True` ile tamamlanan originler atlanır.
'''),
    code(LOAD_MODULE + r'''

RUN_TRAINING = False
RESUME = True

runner = load_module(
    "ag_target_3ay_runner",
    PROJECT_ROOT / "scripts" / "ag_04_uzun_pencere_h3.py",
)

if RUN_TRAINING:
    model_data = runner.load_data()
    predictions = runner.run(model_data, resume=RESUME)
    scored = runner.score(predictions)
    ranking = runner.make_ranking(scored)
    paired, mcnemar = runner.comparisons(scored)
    reproduction = runner.reproduction(predictions)
    verdict = runner.decision(ranking, paired)

    ranking.to_csv(runner.RANK_PATH, index=False, encoding="utf-8-sig")
    paired.to_csv(runner.PAIRED_PATH, index=False, encoding="utf-8-sig")
    mcnemar.to_csv(runner.MCNEMAR_PATH, index=False, encoding="utf-8-sig")
    runner.REPRO_PATH.write_text(reproduction, encoding="utf-8")
    runner.DECISION_PATH.write_text(verdict, encoding="utf-8")
else:
    predictions = pd.read_csv(runner.PRED_PATH, parse_dates=["origin", "hedef_ay"])
    ranking = pd.read_csv(runner.RANK_PATH)
    paired = pd.read_csv(runner.PAIRED_PATH)
    mcnemar = pd.read_csv(runner.MCNEMAR_PATH)
    verdict = runner.DECISION_PATH.read_text(encoding="utf-8")

print("Tahmin satırı:", len(predictions))
'''),
    markdown(r'''
## Güvenlik ve bütünlük kontrolleri
'''),
    code(r'''
assert predictions["origin"].min() == pd.Timestamp("2020-04-01")
assert predictions["origin"].max() == pd.Timestamp("2025-03-01")
assert predictions["origin"].nunique() == 60
assert len(predictions[predictions["origin"].between("2025-04-01", "2026-03-01")]) == 0
assert predictions["y_pred_q50"].notna().all()
assert np.isfinite(predictions["y_pred_q50"]).all()

print("Test origin satırı: 0")
print("Tahminler sonlu ve eksiksiz.")
'''),
    markdown(r'''
## Sonuç tabloları
'''),
    code(r'''
important_models = ["Chronos2", "Toto2", "DirectTabular", "sifir"]
summary = ranking[
    ranking["rejim"].eq("TUM") & ranking["model"].isin(important_models)
].sort_values("MAE")

display(summary)
display(paired)
print(verdict)
'''),
    markdown(r'''
## Deney kararı

Ön kayıtlı kriterlerin tamamı karşılanmadığı için `IP5_KABUL=False` sonucuna ulaşıldı. Test dönemi açılmadı. Bu notebook sonuçları yeniden üretmek ve incelemek içindir; test değerlendirmesi içermez.
'''),
]


ONE_MONTH_CELLS = [
    markdown(r'''
# AutoGluon Time Series — `target_1ay_hiz`

Bu notebook, bir sonraki ayın otomobil devir hızını tahmin eden nihai IP-6 çalışmasını yeniden üretir.

- AutoGluon ayarı: `medium_quality`
- Tahmin ufku: 1 ay
- Puanlanan çıktı: `h=1` medyan tahmini
- Doğrulama originleri: 2020-02 – 2025-05, toplam 64 ay
- Test originleri: 2025-06 – 2026-05; **bu notebookta açılmaz**
'''),
    code(COMMON_SETUP),
    markdown(r'''
## Targetın anlamı

Gerçekleşme ayı `τ` için:

\[
target\_1ay\_hiz_{\tau}
=100\ln\left(\frac{V_{\tau}}{V_{\tau-1}}\right)
\]

Origin `t` tarihinde AutoGluon `target_1ay_hiz[t+1]` değerini tahmin eder.

- Pozitif: gelecek ay hacim artışı.
- Negatif: gelecek ay hacim düşüşü.
- Mutlak değer: logaritmik hareketin şiddeti.
'''),
    code(r'''
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "birlesik_target_setleri"
    / "target_1ay_hiz_tum_featurelar_final.csv"
)

data = pd.read_csv(DATA_PATH)
data["referans_ayi"] = pd.to_datetime(data["referans_ayi"], errors="raise")
data = data.sort_values("referans_ayi").reset_index(drop=True)

expected_months = pd.date_range("2018-02-01", "2026-06-01", freq="MS")

assert data.shape == (101, 14)
assert data["referans_ayi"].equals(pd.Series(expected_months, name="referans_ayi"))
assert not data["referans_ayi"].duplicated().any()
assert data["target_1ay_hiz"].notna().all()
assert np.isfinite(data["target_1ay_hiz"]).all()

print("Tarih:", data["referans_ayi"].min().date(), "→", data["referans_ayi"].max().date())
print("Gözlem:", len(data))
display(data.head(3))
'''),
    markdown(r'''
## Target formülünü doğrulama

İlk target 2018-01 hacmini gerektirdiği için dosyanın ikinci satırından itibaren yeniden hesaplanır.
'''),
    code(r'''
volume = data["noter_devir_otomobil_adet"]
reconstructed = 100 * np.log(volume / volume.shift(1))
check_mask = reconstructed.notna()

max_target_difference = (
    reconstructed[check_mask] - data.loc[check_mask, "target_1ay_hiz"]
).abs().max()

assert max_target_difference < 1e-9
print("Formül doğrulandı. En büyük fark:", max_target_difference)
'''),
    markdown(r'''
## Deney kolları

- **T0:** yalnız target geçmişi.
- **T1:** beş geniş kapsamlı feature; tamamı `lag1`.

T1 feature’ları:

1. Noter otomobil devri
2. TÜFE aylık değişimi
3. OSD kamyonet adedi
4. OSD binek + kamyonet toplamı
5. ODMD hafif ticari araç adedi

`lag1`, hedef ayı `t+1` için yalnız karar ayında (`t`) bilinen değeri verir. Kaydırılmamış `lag0` sütun yasaktır.
'''),
    code(r'''
T1_FEATURES = [
    "noter_devir_otomobil_adet",
    "tufe_aylik_degisim",
    "osd_kamyonet_adet",
    "osd_binek_kamyonet_toplam_adet",
    "odmd_hta_adet",
]

source = data.set_index("referans_ayi")[T1_FEATURES].copy()
source["odmd_hta_adet"] = source["odmd_hta_adet"].ffill()

lagged = source.shift(1)
lagged.columns = [f"{column}_lag1" for column in lagged.columns]

assert all(column.endswith("_lag1") for column in lagged.columns)
assert not set(T1_FEATURES).intersection(lagged.columns)

sample_origin = pd.Timestamp("2024-04-01")
target_month = sample_origin + pd.DateOffset(months=1)

for original in T1_FEATURES:
    supplied = lagged.loc[target_month, f"{original}_lag1"]
    observed_at_origin = source.loc[sample_origin, original]
    assert np.isclose(supplied, observed_at_origin, rtol=0, atol=1e-12)

print("Örnek lag1 denetimi geçti:", sample_origin.date(), "→", target_month.date())
'''),
    markdown(r'''
## Eğitimi çalıştırma veya tamamlanmış checkpointi kullanma

`RUN_TRAINING=False` mevcut sonuçları yükler. Baştan veya yarım kalan eğitim için `True` yapın; `RESUME=True` tamamlanmış originleri atlar.
'''),
    code(LOAD_MODULE + r'''

RUN_TRAINING = False
RESUME = True

runner = load_module(
    "ag_target_1ay_runner",
    PROJECT_ROOT / "scripts" / "ag_05_1ay_h1.py",
)

if RUN_TRAINING:
    model_data = runner.load_data()
    predictions = runner.run(model_data, resume=RESUME)
    evaluated = runner.scored(predictions)
    ranking = runner.ranking(evaluated)
    _, chosen_model = runner.select_model(ranking)
    paired, mcnemar = runner.paired_tables(evaluated, chosen_model)
    selection = runner.selection_text(ranking, chosen_model)
    verdict = runner.decision_text(ranking, paired, mcnemar, chosen_model)

    ranking.to_csv(runner.RANK_PATH, index=False, encoding="utf-8-sig")
    paired.to_csv(runner.PAIRED_PATH, index=False, encoding="utf-8-sig")
    mcnemar.to_csv(runner.MCNEMAR_PATH, index=False, encoding="utf-8-sig")
    runner.SELECTION_PATH.write_text(selection, encoding="utf-8")
    runner.DECISION_PATH.write_text(verdict, encoding="utf-8")
else:
    predictions = pd.read_csv(runner.PRED_PATH, parse_dates=["origin", "hedef_ay"])
    ranking = pd.read_csv(runner.RANK_PATH)
    paired = pd.read_csv(runner.PAIRED_PATH)
    mcnemar = pd.read_csv(runner.MCNEMAR_PATH)
    selection = runner.SELECTION_PATH.read_text(encoding="utf-8")
    verdict = runner.DECISION_PATH.read_text(encoding="utf-8")

print("Tahmin satırı:", len(predictions))
'''),
    markdown(r'''
## Güvenlik kontrolleri
'''),
    code(r'''
assert predictions["origin"].min() == pd.Timestamp("2020-02-01")
assert predictions["origin"].max() == pd.Timestamp("2025-05-01")
assert predictions["origin"].nunique() == 64
assert len(predictions[predictions["origin"].ge("2025-06-01")]) == 0
assert predictions["hedef_ay"].eq(predictions["origin"] + pd.DateOffset(months=1)).all()
assert predictions["y_pred_q50"].notna().all()
assert np.isfinite(predictions["y_pred_q50"]).all()

leakage_audit = runner.LEAKAGE_PATH.read_text(encoding="utf-8")
assert "A7_A8_PASS=True" in leakage_audit

print("Test origin satırı: 0")
print("A7/A8 lag1 sızıntı denetimi geçti.")
'''),
    markdown(r'''
## Model seçimi ve sonuçlar

Model yalnız 2020-02–2022-12 arasındaki SELECT bloğunda seçilir. 2023 sonrası CONFIRM sonucuna bakılarak değiştirilmez.
'''),
    code(r'''
display(
    ranking[
        ranking["rejim"].eq("TUM")
        & ranking["model"].isin(["Chronos2", "DirectTabular", "sifir", "naive"])
    ].sort_values("MAE")
)

display(paired)
display(mcnemar)
print(selection)
print(verdict)
'''),
    markdown(r'''
## Naive yön tanısı

Naive yön doğruluğu yaklaşık %50 ise targetta mekanik ters-yön problemi yoktur. Üç aylık targettaki çok düşük naive doğruluğunun aksine, bir aylık target bu kontrolde daha sağlıklıdır.
'''),
    code(r'''
naive_direction = (
    ranking[ranking["model"].eq("naive")]
    [["rejim", "DA_adet", "n", "DA_yuzde"]]
    .drop_duplicates("rejim")
    .sort_values("rejim")
)
display(naive_direction)
'''),
    markdown(r'''
## Deney kararı

Seçilen T1–Chronos2 modeli sıfır değişim tahmininden daha iyi görünse de ön kayıtlı hata, yön ve istatistiksel güven eşiklerinin tamamını geçemedi. Sonuç `IP6_KABUL=False`; test dönemi açılmadı.
'''),
]


def write_notebook(filename: str, cells: list[dict]) -> Path:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    path = NOTEBOOK_DIR / filename
    path.write_text(
        json.dumps(notebook(cells), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return path


def main() -> None:
    paths = [
        write_notebook("03_autogluon_target_3ay_hiz.ipynb", THREE_MONTH_CELLS),
        write_notebook("04_autogluon_target_1ay_hiz.ipynb", ONE_MONTH_CELLS),
    ]
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
