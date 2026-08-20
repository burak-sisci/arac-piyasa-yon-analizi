# -*- coding: utf-8 -*-
"""target_capraz_ikinciel_yeniarac_satis_orani backtest calismasini aciklamali, yeniden
calistirilabilir notebooka aktarir.

Diger iki sablondan (target_betam_dom_gun: ham kolonun birebir kopyasi; target_quickfinans_dom_gun:
tamamen harici dosya) farkli olarak bu hedef DERIVED_TARGET_FORMULAS ailesinden -- feature_master_aylik.csv
icinde zaten var olan iki ham kolonun (noter_devir_otomobil_adet, odmd_otomobil_adet) oranidir.
"""

from __future__ import annotations

import ast
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts" / "hiz_target_backtest_pipeline.py"
OUTPUT = ROOT / "notebooks" / "09_autogluon_target_capraz_ikinciel_yeniarac_satis_orani.ipynb"


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
        r"""# Çapraz Hedef: İkinci El / Yeni Araç Satış Oranı — `target_capraz_ikinciel_yeniarac_satis_orani` (AutoGluon TimeSeries)

Bu defter, piyasadaki ikinci-el devir hacminin yeni araç (ODMD) satış hacmine oranını bir ay
ilerisi için tahmin eden rolling-origin backtest çalışmasını uçtan uca üretir ve doğrular.

Diğer üç hedeften (`target_betam_dom_gun`, `target_indicata_satis_hizi_gun`,
`target_indicata_satis_ilan_orani_pct`: ham kolonun birebir kopyası) ve
`target_quickfinans_dom_gun`'dan (tamamen harici bir dosyadan okunur) farklı olarak, bu hedef
üçüncü bir mekanizmadan geliyor: `hiz_target_backtest_pipeline.py` içindeki
`DERIVED_TARGET_FORMULAS` sözlüğü — harici hiçbir kaynağa ihtiyaç duymadan,
**`feature_master_aylik.csv` içinde zaten var olan iki ham kolonun matematiksel oranı** olarak
anında ("çapraz") hesaplanır:

\[
\text{target\_capraz\_ikinciel\_yeniarac\_satis\_orani}_t =
\frac{\text{noter\_devir\_otomobil\_adet}_t}{\text{odmd\_otomobil\_adet}_t}
\]

- `noter_devir_otomobil_adet`: o ay noterde el değiştiren otomobil (ikinci el devir) adedi
- `odmd_otomobil_adet`: o ay ODMD (Otomotiv Distribütörleri Derneği) raporuna göre yurt içi
  perakende satılan sıfır km otomobil adedi

Oran, piyasadaki ikinci-el / yeni-araç satış dengesinin bir göstergesidir — değer arttıkça ikinci
el devir hacmi yeni araç satışlarına göre büyüyor demektir (ör. yeni araç arzının daraldığı veya
fiyatların talebi ikinci-el'e kaydırdığı dönemlerde). Formülün her iki kaynak kolonu da
(`noter_devir_otomobil_adet`, `odmd_otomobil_adet`) kendi-kaynak sızıntı riski taşıdığından
feature listesinden dışlanır (bkz. Bölüm 2).

- Veri: 101 gözlem, 2018-01 → 2026-05
- AutoGluon ayarı: `medium_quality`, fold başına `time_limit=45sn`
- Tahmin ufku: 1 ay (`prediction_length=1`)
- Backtest: son 6 ay (2025-12, 2026-01, 2026-02, 2026-03, 2026-04, 2026-05) — rolling-origin /
  genişleyen pencere — her test ayı yalnız kendinden önceki gerçek verilerle sıfırdan eğitilen
  ayrı bir modelle tahmin edilir
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
OUT_DIR = ROOT / "outputs" / "hiz_target_backtest" / "target_capraz_ikinciel_yeniarac_satis_orani"

TARGET = "target_capraz_ikinciel_yeniarac_satis_orani"
DATE_COL = "referans_ayi"
KAYNAK_KOLONLAR = ["noter_devir_otomobil_adet", "odmd_otomobil_adet"]

print("Proje kökü:", ROOT)
print("Hedef:", TARGET)"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 2. Sızıntısız feature tablosu kurma — iki kaynak kolonun birlikte dışlanması

`feature_master_aylik.csv`'deki tüm aylık feature'lar hedefe eklenir. `target_capraz_ikinciel_yeniarac_satis_orani`,
`DERIVED_TARGET_FORMULAS` mekanizmasıyla üretilen bir "çapraz" (türetilmiş) hedeftir: ne
`target_quickfinans_dom_gun` gibi harici bir dosyadan okunur, ne de `target_betam_dom_gun` gibi
`feature_master_aylik.csv`'de zaten hazır duran tek bir ham kolonun birebir kopyasıdır — bunun
yerine, dosyada zaten var olan **iki** ham kolonun oranı olarak anında hesaplanır. Bu yüzden tek
kaynaklı hedeflerdeki `TARGET_TO_SOURCE_COL` (kolon → tek isim) yerine `DERIVED_TARGET_FORMULAS`
sözlüğü kullanılır; her girdinin `kaynak_kolonlar` alanı bir **küme** (burada iki eleman) tutar.
Üç tür kolon dışlanır:

1. **Hedefin türetildiği HER İKİ ham kaynak kolon** (`noter_devir_otomobil_adet` VE
   `odmd_otomobil_adet`) — hedef bu iki kolonun matematiksel bir fonksiyonu olduğundan, ikisinden
   biri feature olarak kalsaydı dolaylı/doğrudan kopya sızıntısı olurdu.
2. **Genel sızıntı yasakları** (`modelleme_sizinti_kisitlari.csv`'nin `tum_targetlar` satırları):
   karışık aylık/yıllık reel değişim kolonu, ÖTV-en-yakın-olay farkı, audit kolonu.
3. **`indicata_*`/`arabam_*`/`betam_*` ailesinin aynı-ay versiyonları** — bu raporlar referans
   ayından sonra yayımlanıyor; bunun yerine 1 ay gecikmeli (`lag1`) türevleri kullanılır.

`build_feature_table`, `target_col` bir `DERIVED_TARGET_FORMULAS` anahtarıysa ilgili `func`'ı
(`_formul_ikinciel_yeniarac_satis_orani`) uygulayarak hedefi `feature_master_aylik.csv`'den türetir
ve `kaynak_kolonlar` kümesinin tamamını `excluded_self`'e ekler — aşağıdaki iki fonksiyon kodunda
görülebilir."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["_formul_ikinciel_yeniarac_satis_orani", "build_feature_table"])))

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
- **sMAPE**: ölçekten bağımsız yüzdesel hata; farklı birimdeki hedefleri karşılaştırmaya yarar.
- **Bias**: `ortalama(tahmin - gerçek)`; pozitifse model sistematik olarak yüksek, negatifse düşük tahmin eder."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["compute_metrics"])))

cells.append(
    nbf.v4.new_markdown_cell(
        """## 7. Uçtan uca çalıştırma fonksiyonu

`run()` yukarıdaki tüm adımları sırayla uygular, her fold için AutoGluon'u eğitir/tahmin eder,
model ile "geçen yılın aynı ayı" baseline'ını aynı 6 metrikle karşılaştırır ve çıktıları
`outputs/hiz_target_backtest/target_capraz_ikinciel_yeniarac_satis_orani/` altına yazar."""
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
print("Backtest ayları:", sonuc["backtest_aylari"], "( n =", sonuc["backtest_ay_sayisi"], ")")"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 9. Güvenlik ve bütünlük kontrolleri

Diğer iki şablon hedeften (`target_betam_dom_gun`: ham kolonla karşılaştırma; `target_quickfinans_dom_gun`:
harici dosyayla karşılaştırma) farklı olarak, burada target'ın eşleşeceği hazır bir tek "ham kolon"
veya "harici dosya" yok — bu yüzden formül `feature_master_aylik.csv`'den **bağımsız olarak**
(pipeline kodu tekrar çağrılmadan) elle yeniden hesaplanır ve gerçek backtest çıktısındaki
`gercek` değerleriyle karşılaştırılır. Ayrıca her iki kaynak kolonun da final feature setinde
bulunmadığı doğrulanır."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """fm_kaynak = pd.read_csv(FEATURE_PATH)[[DATE_COL, *KAYNAK_KOLONLAR]]
fm_kaynak["target_yeniden_hesap"] = fm_kaynak[KAYNAK_KOLONLAR[0]] / fm_kaynak[KAYNAK_KOLONLAR[1]]

gecerli = fm_kaynak.dropna(subset=["target_yeniden_hesap"])
assert len(gecerli) == sonuc["n_obs_toplam"] == 101, "Yeniden hesaplanan gozlem sayisi metrikler.json ile uyusmuyor"
tarih_araligi = f"{gecerli[DATE_COL].min()} -> {gecerli[DATE_COL].max()}"
assert tarih_araligi == sonuc["tarih_araligi"] == "2018-01 -> 2026-05"

karsilastirma = backtest_df[["ay", "gercek"]].merge(
    fm_kaynak.rename(columns={DATE_COL: "ay"})[["ay", "target_yeniden_hesap"]], on="ay", how="left"
)
fark = (karsilastirma["gercek"] - karsilastirma["target_yeniden_hesap"]).abs().max()
assert fark < 1e-9, "target_capraz_ikinciel_yeniarac_satis_orani formulu backtest 'gercek' degerleriyle eslesmiyor"

for kolon in KAYNAK_KOLONLAR:
    assert kolon not in final_features["feature"].tolist(), f"ham kaynak kolonu sizmis: {kolon}"
assert sonuc["disislanan_kolonlar"]["hedefin_ham_kaynak_kolonu_disi"] == sorted(KAYNAK_KOLONLAR)

assert sonuc["durum"] == "TAMAMLANDI"
assert sonuc["backtest_ay_sayisi"] == 6
assert sonuc["backtest_aylari"] == ["2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]
assert not backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].isna().any().any()
assert np.isfinite(backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].values).all()

print("Target formulu (noter_devir_otomobil_adet / odmd_otomobil_adet) feature_master_aylik.csv'den")
print("bagimsiz olarak yeniden hesaplandi ve backtest 'gercek' degerleriyle eslesti. En buyuk fark:", fark)
print("Iki kaynak kolon da final feature setinde yok. Butunluk kontrolleri gecti. Final feature sayisi:", len(final_features))"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 10. Sonuçlar — model vs "geçen yılın aynı ayı" baseline'ı

Bu çalıştırmada baseline, modelin 6 metriğin de önünde (ayrıntı ve ihtiyat notu için bkz. Bölüm 11)."""
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

- **Bu çalıştırmada baseline, modelin tüm 6 metrikte önünde.** "Geçen yılın aynı ayı" (t-12) naive
  baseline'ı yön doğruluğunda %100 (6/6) tutarken model %83.3 (5/6) kaldı; mutlak hata
  metriklerinde de baseline daha iyi: MAE 0.58 vs 0.91, RMSE 0.78 vs 1.15, MASE 0.124 vs 0.195,
  sMAPE %8.35 vs %15.09. İkisi de negatif bias taşıyor (model −0.89, baseline −0.47) — yani her
  ikisi de oranı sistematik olarak hafif düşük tahmin ediyor, model daha belirgin biçimde.
- **AutoGluon'un `medium_quality` preset'i sabit random seed kullanmadığından ve backtest
  örneklemi küçük (n=6) olduğundan**, bu hedefte de yeniden çalıştırmalar arasında sonuçların
  (özellikle yön doğruluğunda) belirgin şekilde değişebildiği bu projede daha önce gözlemlenmiş
  bir bulgudur; tek bir çalıştırmadaki "kazanan" yorumu ihtiyatla okunmalı — burada baseline'ın
  üstünlüğü de kalıcı bir sonuç olmak zorunda değil, bu çalıştırmaya özgü bir gözlem olabilir.
- Fold başına en iyi model çoğunlukla `WeightedEnsemble` (4/6 fold), ayrıca birer kez
  `RecursiveTabular` ve `Toto2` seçildi — model seçiminin fold'lar arasında istikrarsız olması da
  küçük örneklemin bir başka belirtisi.
- Örneklem 101 ay olsa da (2018-01 → 2026-05), backtest yalnızca son 6 ayı kapsıyor; tek bir
  yanlış/doğru yön tahmini, yön doğruluğunu ~%17 oynatıyor.
- Oran hem `noter_devir_otomobil_adet` hem `odmd_otomobil_adet`'in pay/payda dinamiklerine bağlı
  olduğundan, iki seriden birindeki tek aylık bir anomali (ör. ÖTV değişikliği öncesi stoklama,
  resmi tatil kaynaklı düşük tescil) oranı büyük sıçratabilir — model bu tür payda-kaynaklı
  gürültüyü, bu çalıştırmada en azından, baseline'dan daha iyi ayıklayamamış görünüyor."""
    )
)

nb["cells"] = cells
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUTPUT)
print(OUTPUT)
