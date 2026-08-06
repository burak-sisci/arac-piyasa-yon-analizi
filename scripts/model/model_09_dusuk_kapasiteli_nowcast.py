"""Model 09: validation-only, dusuk kapasiteli aylik-nowcast aday gecidi.

Toplam dort on-kayitli aday dener. Test bolumunu acmaz. Ayni aya ait haftalik
snapshot agirliklari toplam 1 olacak sekilde egitim ve genel validation
metriklerinde kullanilir; hafta-sirasi tanisi 1-4 ortak 12 ayda ay-esittir.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import haftalik_aylik_nowcast as hn  # noqa: E402
import nowcast_baseline as nb  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

FEATURELAR = [
    "ay_sin",
    "ay_cos",
    "is_gunu_ilerleme_orani",
    "usdtry_orta_ilk_son_degisim_pct",
    "eurtry_orta_ilk_son_degisim_pct",
    "otv_event_gunu_mu_cari_ay_sayisi",
    "tufe_aylik_degisim_lag2ay",
    "tasit_kredisi_faiz_lag2ay",
    "hedef_m2_m3_degisim_pct",
    "hedef_m12_m13_degisim_pct",
]


def _oran(son: pd.Series, ilk: pd.Series) -> pd.Series:
    return ((son / ilk) - 1.0) * 100.0


def _feature_hazirla(df: pd.DataFrame) -> pd.DataFrame:
    sonuc = df.copy()
    sonuc["hedef_m2_m3_degisim_pct"] = _oran(
        sonuc["noter_devir_otomobil_adet_lag2ay"],
        sonuc["noter_devir_otomobil_adet_lag3ay"],
    )
    sonuc["hedef_m12_m13_degisim_pct"] = _oran(
        sonuc["noter_devir_otomobil_adet_lag12ay"],
        sonuc["noter_devir_otomobil_adet_lag13ay"],
    )
    return sonuc.replace([np.inf, -np.inf], np.nan)


def _adaylar() -> dict:
    return {
        "lojistik_l2_c01": LogisticRegression(
            C=0.1, penalty="l2", solver="lbfgs", max_iter=2000,
            class_weight="balanced", random_state=42,
        ),
        "lojistik_l2_c1": LogisticRegression(
            C=1.0, penalty="l2", solver="lbfgs", max_iter=2000,
            class_weight="balanced", random_state=42,
        ),
        "random_forest_sigin": RandomForestClassifier(
            n_estimators=300, max_depth=3, min_samples_leaf=6,
            max_features="sqrt", class_weight="balanced", random_state=42,
            n_jobs=-1,
        ),
        "hist_gradient_sigin": HistGradientBoostingClassifier(
            max_iter=100, learning_rate=0.05, max_leaf_nodes=5,
            min_samples_leaf=12, l2_regularization=2.0, random_state=42,
        ),
    }


def _metrik_ozeti(m: dict) -> dict:
    return {
        "mcc_gorodkin": m["mcc_gorodkin"],
        "macro_f1": m["macro_f1"],
        "accuracy": m["accuracy"],
        "stable_recall": m["per_class"]["stable"]["recall"],
        "n": m["n"],
    }


def main() -> None:
    snapshot = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    snapshot["hedef_ay"] = pd.PeriodIndex(snapshot["hedef_ay"], freq="M")
    snapshot = _feature_hazirla(snapshot)
    split = hn.nowcast_uc_parcali_split_olustur(
        "2019-01", "2024-02", "2024-05", "2025-04",
        "2025-07", "2026-06", embargo_ay_sayisi=2,
    )
    train = snapshot[
        snapshot["hedef_ay"].isin(split["train"])
        & snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)
    ].copy()
    val = snapshot[
        snapshot["hedef_ay"].isin(split["validation"])
        & snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)
    ].copy()
    if len(FEATURELAR) > 10:
        raise RuntimeError("On-kayitli feature tavani (10) asildi")
    if len(_adaylar()) > 4:
        raise RuntimeError("On-kayitli aday tavani (4) asildi")

    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    x_train_imp = imputer.fit_transform(train[FEATURELAR])
    x_val_imp = imputer.transform(val[FEATURELAR])
    x_train_scaled = scaler.fit_transform(x_train_imp)
    x_val_scaled = scaler.transform(x_val_imp)

    denemeler = {}
    tahminler = {}
    for ad, model in _adaylar().items():
        lojistik = ad.startswith("lojistik")
        xtr = x_train_scaled if lojistik else x_train_imp
        xva = x_val_scaled if lojistik else x_val_imp
        model.fit(xtr, train["etiket"], sample_weight=train["agirlik"])
        yhat = model.predict(xva).tolist()
        tahminler[ad] = yhat
        genel = yd.degerlendir(
            val["etiket"], yhat, agirliklar=val["agirlik"]
        )
        hafta = {}
        for sira in (1, 2, 3, 4):
            maske = val["hafta_sirasi"].eq(sira).to_numpy()
            hafta[str(sira)] = _metrik_ozeti(
                yd.degerlendir(val.loc[maske, "etiket"], np.asarray(yhat)[maske])
            )
        denemeler[ad] = {
            "genel_validation": _metrik_ozeti(genel),
            "hafta_sirasi_1_4": hafta,
            "parametreler": model.get_params(),
        }

    siralama = sorted(
        denemeler,
        key=lambda ad: (
            denemeler[ad]["genel_validation"]["mcc_gorodkin"],
            denemeler[ad]["genel_validation"]["macro_f1"],
            denemeler[ad]["genel_validation"]["stable_recall"],
        ),
        reverse=True,
    )
    kazanan = siralama[0]

    aylik = snapshot.drop_duplicates("hedef_ay").set_index("hedef_ay")["etiket"]
    baseline = nb.baseline_degerlendir(aylik, split["train"], split["validation"])
    baseline_siralama = sorted(
        baseline["metrikler"],
        key=lambda ad: (
            baseline["metrikler"][ad]["mcc_gorodkin"],
            baseline["metrikler"][ad]["macro_f1"],
        ),
        reverse=True,
    )
    en_iyi_baseline = baseline_siralama[0]
    km = denemeler[kazanan]["genel_validation"]
    bm = baseline["metrikler"][en_iyi_baseline]
    terfi = (
        km["mcc_gorodkin"] > bm["mcc_gorodkin"]
        and km["macro_f1"] > bm["macro_f1"]
    )
    hafta_mcc = [denemeler[kazanan]["hafta_sirasi_1_4"][str(i)]["mcc_gorodkin"] for i in (1,2,3,4)]
    monoton = all(b >= a for a, b in zip(hafta_mcc, hafta_mcc[1:]))

    sonuc = {
        "durum": "validation_only_test_acilmadi",
        "etkin_train_ay": int(train["hedef_ay"].nunique()),
        "validation_ay": int(val["hedef_ay"].nunique()),
        "feature_sayisi": len(FEATURELAR),
        "featurelar": FEATURELAR,
        "aday_sayisi": len(denemeler),
        "denemeler": denemeler,
        "validation_kazanan": kazanan,
        "en_iyi_baseline": en_iyi_baseline,
        "en_iyi_baseline_metrikleri": _metrik_ozeti(bm),
        "terfi_kapisi": {
            "kural": "MCC ve macro-F1 en iyi baseline'dan birlikte yuksek olmali",
            "gecti_mi": terfi,
        },
        "haftalik_bilgi_kazanimi": {
            "kazanan_hafta_mcc_1_4": hafta_mcc,
            "monoton_iyilesme": monoton,
            "yorum": (
                "Monoton iyilesme var." if monoton else
                "Monoton iyilesme yok; haftalik kadansin duzenli ek bilgi tasidigi dogrulanmadi."
            ),
        },
        "test": "ACILMADI_KILITLI_DEGIL",
    }
    (MODEL_DIR / "model_09_dusuk_kapasiteli_nowcast_validation.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
