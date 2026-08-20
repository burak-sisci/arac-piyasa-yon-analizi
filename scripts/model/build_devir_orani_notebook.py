# -*- coding: utf-8 -*-
"""IP-7 calismasini aciklamali ve yeniden calistirilabilir notebooka aktarir."""

from __future__ import annotations

import ast
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts" / "ag_06_devir_orani_h1.py"
OUTPUT = ROOT / "notebooks" / "05_autogluon_target_devir_orani_best_quality.ipynb"


def get_functions(names: list[str]) -> str:
    text = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    blocks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            blocks.append("\n".join(lines[node.lineno - 1 : node.end_lineno]))
    missing = set(names).difference(
        node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    if missing:
        raise RuntimeError(f"Kaynak scriptte bulunamayan fonksiyonlar: {sorted(missing)}")
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
        r"""# Noter devir oranı — AutoGluon TimeSeries (`best_quality`)

Bu defter yeni hedefi uçtan uca üretir ve test eder:

\\[
\text{target}_t =
\frac{\text{noter\_devir\_otomobil\_adet}_t}
{\text{trafiğe\_kayıtlı\_toplam\_otomobil\_adet}_t}
\\]

Hedef, o ay el değiştiren otomobillerin mevcut otomobil parkına **ham oranıdır**. Örneğin değer `0.042` ise kayıtlı otomobillerin yaklaşık `0,042`'si o ay noter devrine konu olmuştur. Yüzde gösterimi yalnız yorum amacıyla `0.042 × 100 = %4,2` şeklinde ayrıca türetilebilir; model targetı yüzde değildir.

Zaman sızıntısını önlemek için modele bütün feature'ların **bir ay gecikmeli (`lag1`)** değerleri verilir. Feature seçimi yalnız eğitim döneminde yapılır; validasyon ve test ayları seçime katılmaz."""
    )
)
cells.append(
    nbf.v4.new_markdown_cell(
        """## 1. Kütüphaneler ve sabitler

`best_quality` eğitimi yalnız AutoGluon ortamında çalışır. Notebook proje kökünden veya `notebooks` klasöründen açılabilir."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """from pathlib import Path
import json
import shutil

import numpy as np
import pandas as pd
from IPython.display import display

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent

DATA_DIR = ROOT / "data"
TRAFFIC_DIR = DATA_DIR / "trafige_kayitli_otomobiller"
MERGED_DIR = DATA_DIR / "birlesik_target_setleri"
OUT = ROOT / "outputs" / "autogluon" / "ip7_devir_orani"
MODEL_DIR = OUT / "ag_model"

TARGET = "target_devir_orani"
DATE = "referans_ayi"
ITEM_ID = "TR_otomobil"
PREDICTION_LENGTH = 1
FREQ = "MS"
TEST_MONTHS = 6
VALIDATION_MONTHS = 6
MIN_PERIODS = 12
TARGET_CORR_THRESHOLD = 0.10
FEATURE_CORR_THRESHOLD = 0.90

print("Proje kökü:", ROOT)
print("Hedef:", TARGET)"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 2. TÜİK otomobil parkı verisini temizleme

Kaynak dosya uzun formattadır: benzin, dizel, LPG, hibrit, elektrik ve bilinmeyen gibi yakıt kırılımları hem sayı hem yüzde olarak bulunur. Biz yalnız `YAKIT_TUR == '_T'` (Toplam) ve `UNIT_MEASURE == 'PN'` (Sayı) satırını tutarız. Dosya iki sütunlu hale getirilerek aynı konuma yazılır; hücre ikinci kez çalıştırıldığında da güvenle aynı sonucu verir."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["traffic_file", "parse_tr_number", "clean_traffic_source"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 3. Tüm verileri aylık olarak birleştirme ve hedefi üretme

Ana tümleşik tablo mevcut proje kaynaklarının tamamını ay başı zaman damgasıyla birleştirir. Hedef cari ayda hesaplanır; model girdileri ise bir ay geciktirilir. Böylece `t` ayını tahmin ederken yalnız `t-1` ve daha eski bilgiler kullanılır."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["build_integrated_data", "split_dates"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 4. Feature seçimi — yalnız eğitim döneminde

İki aşamalı Pearson filtresi uygulanır:

1. Hedefle mutlak Pearson korelasyonu `0.1` altında olan veya en az 12 ortak gözlemle hesaplanamayan feature ayrılır.
2. Kalan feature'lar arasında mutlak Pearson korelasyonu `0.9` üzerinde bağlantılı gruplar kurulur. Her grupta hedefle mutlak korelasyonu en yüksek feature tutulur.

Spearman korelasyonu ayrıca raporlanır; otomatik eleme kararını değiştirmez."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        get_functions(["union_find_components", "select_features", "causal_impute", "prepare_outputs"])
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """traffic, integrated, model_ready, selected, dropped, selection_summary, dates = prepare_outputs()

print(f"Temiz otomobil parkı serisi: {len(traffic)} ay")
print(f"Tümleşik hedef seti: {len(integrated)} ay, {integrated.shape[1]} sütun")
print(f"Seçilen feature: {len(selected)} | Ayrılan feature: {len(dropped)}")
print({k: v.strftime('%Y-%m') for k, v in dates.items()})
display(selection_summary)
display(integrated[[DATE, 'noter_devir_otomobil_adet',
                    'trafige_kayitli_toplam_otomobil_adet', TARGET]].tail())"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 5. AutoGluon TimeSeries yardımcıları

Model bir ay sonrasını tahmin eder (`prediction_length=1`). Feature sütunları `lag1` olduğu için hedef ay için değerleri karar tarihinde bilinmektedir. Model seçimi 6 aylık validasyon MAE'sine göre yapılır. Test 6 ay boyunca rolling-origin biçiminde simüle edilir: her ayın gerçek değeri ancak sonraki ayın tahmininde geçmişe eklenir."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        get_functions(
            [
                "tsdf",
                "q50",
                "rolling_predictions",
                "add_baselines",
                "score",
                "train_and_evaluate",
            ]
        )
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 6. `best_quality` eğitimi

İlk çalıştırmada `YENIDEN_EGIT = True` olmalıdır. Model dosyaları zaten mevcutsa aşağıdaki varsayılan `False` değeri pahalı eğitimi tekrarlamaz; üretilmiş sonuçları yükler. Model klasörü yoksa değer `False` olsa bile eğitim otomatik başlar.

Zaman sınırı 900 saniyedir. AutoGluon bu süre içinde `best_quality` presetindeki uygun modelleri ve ensemble'ı dener."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """YENIDEN_EGIT = False
TIME_LIMIT_SECONDS = 900

sonuc_dosyalari_var = (
    (OUT / 'validasyon_siralama.csv').exists()
    and (OUT / 'test_siralama_tum_modeller.csv').exists()
    and (OUT / 'test_sonuc_secili_model.csv').exists()
)

if YENIDEN_EGIT or not MODEL_DIR.exists() or not sonuc_dosyalari_var:
    predictor, chosen, validation_rank, test_rank, final_test = train_and_evaluate(
        model_ready, selected, dates, TIME_LIMIT_SECONDS
    )
    egitim_durumu = 'Model bu notebook koşusunda eğitildi.'
else:
    from autogluon.timeseries import TimeSeriesPredictor
    predictor = TimeSeriesPredictor.load(MODEL_DIR)
    chosen = (OUT / 'secili_model.txt').read_text(encoding='utf-8').strip()
    validation_rank = pd.read_csv(OUT / 'validasyon_siralama.csv')
    test_rank = pd.read_csv(OUT / 'test_siralama_tum_modeller.csv')
    final_test = pd.read_csv(OUT / 'test_sonuc_secili_model.csv')
    egitim_durumu = 'Mevcut best_quality modeli ve doğrulanmış sonuçlar yüklendi.'

print(egitim_durumu)
print('Validasyonda seçilen model:', chosen)"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 7. Sonuçlar

- `MAE`: ham oran biriminde ortalama mutlak hata.
- `RMSE`: büyük hataları daha fazla cezalandırır.
- `MASE`: eğitim dönemindeki bir-adım son-değer hatasına göre ölçekli hata; `1` altı bu ölçeğe göre iyidir.
- `yon_dogrulugu_yuzde`: tahmin edilen oranın bir önceki aya göre artış/azalış yönünün doğruluğu.
- `bias`: pozitifse model ortalamada yüksek, negatifse düşük tahmin etmiştir.

Model adı yalnız validasyon tablosuna göre sabitlenmiştir. Test tablosu model seçiminde kullanılmamıştır."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """print('VALIDASYON — ilk 10')
display(validation_rank.head(10))

print('NİHAİ TEST — validasyonda seçilen model ve baselinelar')
display(final_test)

print('TEST — tüm modeller (yalnız teşhis)')
display(test_rank)"""
    )
)

nb["cells"] = cells
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUTPUT)
print(OUTPUT)
