# -*- coding: utf-8 -*-
"""target_capraz_kuyruk_stok_seviyesi backtest calismasini aciklamali, yeniden
calistirilabilir notebooka aktarir.

target_capraz_ikinciel_yeniarac_satis_orani ile ayni ailede (DERIVED_TARGET_FORMULAS):
feature_master_aylik.csv icinde zaten var olan iki ham kolonun ("noter_devir_otomobil_adet",
"betam_dom_gun") matematiksel olarak birlestirilmesiyle -- bu kez oran degil, Little's Law
(L = lambda * W) uygulamasiyla -- turetilen bir "capraz" hedeftir. Fark: oran hedefinden farkli
olarak burada tek bir bolme degil, gunluk akisa cevirme (bolme) + carpma birlikte var, bu yuzden
9. bolumdeki bagimsiz yeniden hesaplama da iki adimli formulu birebir uygular.
"""

from __future__ import annotations

import ast
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts" / "hiz_target_backtest_pipeline.py"
OUTPUT = ROOT / "notebooks" / "10_autogluon_target_capraz_kuyruk_stok_seviyesi.ipynb"


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
        r"""# Çapraz Hedef: Kuyruk Teorisi Stok Seviyesi — `target_capraz_kuyruk_stok_seviyesi` (AutoGluon TimeSeries)

Bu defter, piyasada o an aktif olarak satılık olduğu tahmin edilen araç **stok seviyesini**
(adet) bir ay ilerisi için tahmin eden rolling-origin backtest çalışmasını uçtan uca üretir ve
doğrular.

Diğer iki hedeften (`target_betam_dom_gun`: ham kolonun birebir kopyası; `target_quickfinans_dom_gun`:
tamamen harici bir dosyadan okunur) farklı, ama `target_capraz_ikinciel_yeniarac_satis_orani` ile
aynı ailede: `hiz_target_backtest_pipeline.py` içindeki `DERIVED_TARGET_FORMULAS` sözlüğü — harici
hiçbir kaynağa ihtiyaç duymadan, **`feature_master_aylik.csv` içinde zaten var olan iki ham
kolonun matematiksel birleşimi** olarak anında ("çapraz") hesaplanır. Oran hedefinden farkı: bu
kez tek bir bölme değil, **Little's Law** (kuyruk teorisi, `L = λ·W`) uygulanan iki adımlı bir
dönüşüm var:

\[
\text{target\_capraz\_kuyruk\_stok\_seviyesi}_t =
\underbrace{\frac{\text{noter\_devir\_otomobil\_adet}_t}{\text{o ayın gün sayısı}}}_{\lambda_t \;(\text{günlük devir akışı})}
\times
\underbrace{\text{betam\_dom\_gun}_t}_{W_t \;(\text{ortalama ilanda kalış süresi, gün})}
\]

- `noter_devir_otomobil_adet`: o ay noterde el değiştiren otomobil (ikinci el devir) adedi —
  ay uzunluğu farkını (28-31 gün) gidermek için önce **günlük akışa** (`λ`) çevrilir.
- `betam_dom_gun`: BETAM raporundaki ortalama ilanda kalış süresi (gün) — kuyruk teorisindeki
  ortalama **bekleme/hizmet süresi** (`W`) rolünde.
- Little's Law (`L = λ·W`), bir kuyruktaki (burada: "satışa çıkmış ama henüz satılmamış araç
  havuzu") ortalama **eleman sayısını**, akış hızı ile o akıştaki ortalama kalış süresinin
  çarpımı olarak verir. Burada `L_t`, referans ayında piyasada aktif olduğu tahmin edilen
  satılık araç **SEVİYESİ** (stok adedi) — bir **büyüme hızı değil**.

> **Tasarım notu — neden büyüme hızı değil seviye?** Bu hedef bilinçli olarak seviye (level)
> olarak tanımlandı. Büyüme-hızı versiyonu (`log(L_t) - log(L_{t-1})`), `log(λ·W) = log(λ) + log(W)`
> özdeşliği gereği, projede zaten var olan iki hedefin — `target_1ay_hiz` (noter devrinin aylık
> büyüme hızı) ile `betam_dom_gun`'un log-farkının — cebirsel toplamına eşit çıktığı adversarial
> doğrulamada tespit edildi (fark < 1e-13): yani gerçek bir yeni etkileşim sinyali taşımıyor,
> matematiksel olarak zaten var olan iki hedefin toplamından ibaret. Seviye versiyonu ise gerçekten
> yeni bir büyüklüğü (stok adedi) ifade ettiği için modelleme açısından anlamlı.

Formülün her iki kaynak kolonu da (`noter_devir_otomobil_adet`, `betam_dom_gun`) kendi-kaynak
sızıntı riski taşıdığından feature listesinden birlikte dışlanır (bkz. Bölüm 2).

- Veri: 28 gözlem, 2024-01 → 2026-06
- AutoGluon ayarı: `medium_quality`, fold başına `time_limit=45sn`
- Tahmin ufku: 1 ay (`prediction_length=1`)
- Backtest: son 6 ay (2025-12, 2026-01, 2026-03, 2026-04, 2026-05, 2026-06; 2026-02 sıçraması
  hakkında bkz. Bölüm 5) — rolling-origin / genişleyen pencere — her test ayı yalnız kendinden
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
OUT_DIR = ROOT / "outputs" / "hiz_target_backtest" / "target_capraz_kuyruk_stok_seviyesi"

TARGET = "target_capraz_kuyruk_stok_seviyesi"
DATE_COL = "referans_ayi"
KAYNAK_KOLONLAR = ["betam_dom_gun", "noter_devir_otomobil_adet"]

print("Proje kökü:", ROOT)
print("Hedef:", TARGET)"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 2. Sızıntısız feature tablosu kurma — iki kaynak kolonun birlikte dışlanması

`feature_master_aylik.csv`'deki tüm aylık feature'lar hedefe eklenir. `target_capraz_kuyruk_stok_seviyesi`,
`DERIVED_TARGET_FORMULAS` mekanizmasıyla üretilen bir "çapraz" (türetilmiş) hedeftir: ne
`target_quickfinans_dom_gun` gibi harici bir dosyadan okunur, ne de `target_betam_dom_gun` gibi
`feature_master_aylik.csv`'de zaten hazır duran tek bir ham kolonun birebir kopyasıdır — bunun
yerine, dosyada zaten var olan **iki** ham kolonun (`noter_devir_otomobil_adet`, `betam_dom_gun`)
Little's Law ile birleşimi olarak anında hesaplanır. `TARGET_TO_SOURCE_COL` (kolon → tek isim)
yerine `DERIVED_TARGET_FORMULAS` sözlüğü kullanılır; bu hedefin girdisinin `kaynak_kolonlar`
alanı yine bir **küme** (iki eleman) tutar — formül tek bir oran değil, "böl + çarp" işlemi olsa
da sızıntı kaynağı sayılan ham kolon sayısı aynı şekilde ikidir. Üç tür kolon dışlanır:

1. **Hedefin türetildiği HER İKİ ham kaynak kolon** (`noter_devir_otomobil_adet` VE
   `betam_dom_gun`) — hedef bu iki kolonun matematiksel bir fonksiyonu olduğundan, ikisinden
   biri feature olarak kalsaydı dolaylı/doğrudan kopya sızıntısı olurdu.
2. **Genel sızıntı yasakları** (`modelleme_sizinti_kisitlari.csv`'nin `tum_targetlar` satırları):
   karışık aylık/yıllık reel değişim kolonu, ÖTV-en-yakın-olay farkı, audit kolonu.
3. **`indicata_*`/`arabam_*`/`betam_*` ailesinin aynı-ay versiyonları** — bu raporlar referans
   ayından sonra yayımlanıyor; bunun yerine 1 ay gecikmeli (`lag1`) türevleri kullanılır (bu
   ailenin bir üyesi olan `betam_dom_gun`'un kendisi zaten madde 1 kapsamında tamamen dışlandığı
   için, burada yalnızca `betam_dom_gun_lag1` gibi diğer `betam_*`/`indicata_*`/`arabam_*` aile
   üyeleri gecikmeli haliyle feature listesinde kalır).

`build_feature_table`, `target_col` bir `DERIVED_TARGET_FORMULAS` anahtarıysa ilgili `func`'ı
(`_formul_kuyruk_stok_seviyesi`) uygulayarak hedefi `feature_master_aylik.csv`'den türetir ve
`kaynak_kolonlar` kümesinin tamamını `excluded_self`'e ekler — aşağıdaki iki fonksiyon kodunda
görülebilir."""
    )
)
cells.append(nbf.v4.new_code_cell(get_functions(["_formul_kuyruk_stok_seviyesi", "build_feature_table"])))

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
bir geçmiş yaratırdı (bu proje bir kullanıcı sorusuyla yakalanıp düzeltilmiş bir hatadır).

Not: bu hedefte 6 backtest ayı **ardışık değil** — liste `2025-12, 2026-01, 2026-03, 2026-04,
2026-05, 2026-06` şeklinde, 2026-02 aralıkta yok. Bunun nedeni `find_backtest_months`'ın (a)
şartı: 2026-02'nin geçerli olması için 2025-02'nin de hedefte mevcut olması gerekir, ama seride
2025-02 iç boşluk (eksik gözlem) olduğundan 2026-02 aday listesine hiç girmiyor ve en yakın 6
geçerli ay (2026-02 hariç) seçiliyor."""
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
`outputs/hiz_target_backtest/target_capraz_kuyruk_stok_seviyesi/` altına yazar."""
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
harici dosyayla karşılaştırma) ve tek-bölme çapraz hedeften (`target_capraz_ikinciel_yeniarac_satis_orani`)
farklı olarak, burada formül **iki adımlıdır** (günlük akışa çevirme + çarpma): bu yüzden formül
`feature_master_aylik.csv`'den **bağımsız olarak** (pipeline kodu tekrar çağrılmadan), `pd.Timestamp`
üzerinden `days_in_month` hesaplanarak elle yeniden üretilir ve gerçek backtest çıktısındaki
`gercek` değerleriyle karşılaştırılır. Ayrıca her iki kaynak kolonun da final feature setinde
bulunmadığı doğrulanır."""
    )
)
cells.append(
    nbf.v4.new_code_cell(
        """fm_kaynak = pd.read_csv(FEATURE_PATH)[[DATE_COL, *KAYNAK_KOLONLAR]]
gun_sayisi = pd.to_datetime(fm_kaynak[DATE_COL]).dt.days_in_month
fm_kaynak["target_yeniden_hesap"] = (fm_kaynak["noter_devir_otomobil_adet"] / gun_sayisi) * fm_kaynak["betam_dom_gun"]

gecerli = fm_kaynak.dropna(subset=["target_yeniden_hesap"])
assert len(gecerli) == sonuc["n_obs_toplam"] == 28, "Yeniden hesaplanan gozlem sayisi metrikler.json ile uyusmuyor"
tarih_araligi = f"{gecerli[DATE_COL].min()} -> {gecerli[DATE_COL].max()}"
assert tarih_araligi == sonuc["tarih_araligi"] == "2024-01 -> 2026-06"

karsilastirma = backtest_df[["ay", "gercek"]].merge(
    fm_kaynak.rename(columns={DATE_COL: "ay"})[["ay", "target_yeniden_hesap"]], on="ay", how="left"
)
fark = (karsilastirma["gercek"] - karsilastirma["target_yeniden_hesap"]).abs().max()
assert fark < 1e-9, "target_capraz_kuyruk_stok_seviyesi formulu backtest 'gercek' degerleriyle eslesmiyor"

for kolon in KAYNAK_KOLONLAR:
    assert kolon not in final_features["feature"].tolist(), f"ham kaynak kolonu sizmis: {kolon}"
assert sonuc["disislanan_kolonlar"]["hedefin_ham_kaynak_kolonu_disi"] == sorted(KAYNAK_KOLONLAR)

assert sonuc["durum"] == "TAMAMLANDI"
assert sonuc["backtest_ay_sayisi"] == 6
assert sonuc["backtest_aylari"] == ["2025-12", "2026-01", "2026-03", "2026-04", "2026-05", "2026-06"]
assert not backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].isna().any().any()
assert np.isfinite(backtest_df[["gercek", "model_tahmin", "baseline_gecen_yil_ayni_ay"]].values).all()

print("Target formulu ((noter_devir_otomobil_adet / gun_sayisi) * betam_dom_gun) feature_master_aylik.csv'den")
print("bagimsiz olarak yeniden hesaplandi ve backtest 'gercek' degerleriyle eslesti. En buyuk fark:", fark)
print("Iki kaynak kolon da final feature setinde yok. Butunluk kontrolleri gecti. Final feature sayisi:", len(final_features))"""
    )
)

cells.append(
    nbf.v4.new_markdown_cell(
        """## 10. Sonuçlar — model vs "geçen yılın aynı ayı" baseline'ı

Bu çalıştırmada model, 4 mutlak-hata metriğinde (MAE, RMSE, MASE, sMAPE) baseline'ı geçiyor;
yön doğruluğunda ikisi eşit çıktı (ayrıntı ve ihtiyat notu için bkz. Bölüm 11)."""
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

- **Model mutlak hatada baseline'ı belirgin biçimde geçiyor, yön doğruluğunda eşitler.** MAE
  46,177 vs 66,766, RMSE 64,733 vs 72,539, MASE 0.921 vs 1.332 (ikisi de `<1`'e ne kadar yakınsa
  o kadar mevsimsel naif'ten iyi; model burada gerçek mevsimsel oynaklığa daha yakın), sMAPE
  %9.92 vs %14.83 — dördünde de model daha düşük hatalı. Ama yön doğruluğunda ikisi de aynı
  oranda (5/6 = %83.3) tuttu; mutlak hatadaki üstünlük "gelecek ay çıkar mı düşer mi" sorusuna
  otomatik olarak yansımıyor. İkisi de negatif bias taşıyor (model −26,949, baseline −35,740) —
  yani her ikisi de stok seviyesini sistematik olarak hafif düşük tahmin ediyor, baseline daha
  belirgin biçimde.
- **AutoGluon'un `medium_quality` preset'i sabit random seed kullanmadığından ve backtest
  örneklemi küçük (n=6) olduğundan**, bu hedefte de yeniden çalıştırmalar arasında sonuçların
  (özellikle yön doğruluğunda) belirgin şekilde değişebildiği bu projede daha önce gözlemlenmiş
  bir bulgudur; tek bir çalıştırmadaki "kazanan" yorumu ihtiyatla okunmalı.
- Fold başına en iyi model üç farklı aileden geldi: `DirectTabular` (2/6), `WeightedEnsemble`
  (3/6), `Toto2` (1/6) — model seçiminin fold'lar arasında istikrarsız olması küçük örneklemin
  bir başka belirtisi.
- Örneklem yalnızca 28 ay (2024-01 → 2026-06) ve backtest ayları **ardışık değil** (2026-02
  seride 2025-02 iç boşluğu yüzünden aday listesinden düşüyor, bkz. Bölüm 5); tek bir
  yanlış/doğru yön tahmini, yön doğruluğunu ~%17 oynatıyor.
- Hedef, iki farklı ölçekteki serinin (aylık devir hacmi ve ilanda kalış süresi) çarpımı
  olduğundan, iki kaynaktan birindeki tek aylık bir anomali (ör. kısa bir ayda devir hacminin
  aniden sıçraması veya DOM'un aniden uzaması) stok seviyesini orantısız büyütebilir — 2025-12
  gözlemindeki sıçrama (gerçek 556,455 vs model tahmini 432,094, bkz. Bölüm 10 tablosu) buna bir
  örnek.
- Hedef, tasarım gereği bir **seviye** (stok adedi) ölçüsüdür, büyüme hızı değil — bkz. Bölüm 0
  başlık altındaki tasarım notu: büyüme-hızı versiyonu, zaten var olan iki targetin (`target_1ay_hiz`
  + `betam_dom_gun` log-farkı) cebirsel toplamına eşit çıktığından (log özdeşliği gereği, fark <
  1e-13) ayrı bir hedef olarak eklenmedi."""
    )
)

nb["cells"] = cells
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUTPUT)
print(OUTPUT)
