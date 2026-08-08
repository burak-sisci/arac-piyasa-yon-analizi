"""Model 13: BDDK C=0,01 kapasite-düşürülmüş iki kollu tekrar.

Model 12'nin ON_ELEME_ZAYIF dalını tek bir yeni lojistik kapasite noktasında
terminal olarak kapatır. OOF performans üretmez; cari/revize BDDK serisi için
HEURISTIK in-sample/permutasyon ön-elemesidir.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

for _degisken in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_degisken] = "1"

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_12_bddk_tavan_taramasi as m12  # noqa: E402

YENI_AD = "lojistik_l2_c001"
MANIPULASYON_ESIGI = 0.4450343895977828
SEED = 410

MODEL12_TEST_REFERANSI = {
    "lojistik_l2_c01": (0.3794043068249444, 0.5005527170007357),
    "lojistik_l2_c1": (0.4935593865570038, 0.5527829345828528),
    "random_forest_sigin": (0.9690397174704891, 0.9537093723276986),
    "hist_gradient_sigin": (1.0, 1.0),
}


def adaylar() -> dict:
    modeller = m12._adaylar()
    modeller[YENI_AD] = LogisticRegression(
        C=0.01,
        penalty="l2",
        solver="lbfgs",
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
    )
    if list(modeller)[-1] != YENI_AD or len(modeller) != 5:
        raise AssertionError("Model 13 tam dört özgün + bir yeni config kullanmalı")
    return modeller


def oracle_kolu(
    veri: pd.DataFrame,
    featurelar: list[str],
    perm_matris: np.ndarray,
) -> dict:
    m12.ht.bilgi_maskesini_dogrula(featurelar)
    if any(c.endswith("lag1ay") for c in featurelar):
        raise AssertionError("M-1 feature yasak")
    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    xi = imputer.fit_transform(veri[featurelar])
    xs = scaler.fit_transform(xi)
    y_ay = veri.drop_duplicates("hedef_ay")["etiket"].to_numpy(dtype=object)
    y = np.repeat(y_ay, 4)
    agirlik = np.full(len(y), 0.25)
    cikti = {}
    for ad, model in adaylar().items():
        x = xs if ad.startswith("lojistik") else xi
        model.fit(x, y, sample_weight=agirlik)
        gozlenen = m12.yd.degerlendir(
            y, model.predict(x), agirliklar=agirlik
        )["mcc_gorodkin"]
        null = np.empty(len(perm_matris))
        for i, yp_ay in enumerate(perm_matris):
            yp = np.repeat(yp_ay, 4)
            mp = adaylar()[ad]
            mp.fit(x, yp, sample_weight=agirlik)
            null[i] = m12.yd.degerlendir(
                yp, mp.predict(x), agirliklar=agirlik
            )["mcc_gorodkin"]
        null95 = float(np.quantile(null, 0.95))
        cikti[ad] = {
            "tavan_gozlenen": float(gozlenen),
            "tavan_null95": null95,
            "marj": float(gozlenen - null95),
            "null_tekrar": int(len(perm_matris)),
            "doygun": ad in m12.DOYGUN_MODELLER,
            "yeni_baseline": ad == YENI_AD,
        }
    return cikti


def model12_test_tekrarini_dogrula(test: dict) -> dict:
    denetim = {}
    for ad, (gozlenen, null95) in MODEL12_TEST_REFERANSI.items():
        farklar = {
            "tavan_gozlenen": abs(test[ad]["tavan_gozlenen"] - gozlenen),
            "tavan_null95": abs(test[ad]["tavan_null95"] - null95),
        }
        denetim[ad] = {"farklar": farklar, "gecti": max(farklar.values()) <= 1e-6}
    if not all(x["gecti"] for x in denetim.values()):
        raise RuntimeError(f"Model 12 test kolu yeniden üretilemedi: {denetim}")
    return denetim


def karar_ver(kontrol_c001: dict, test_c001: dict) -> dict:
    marj_kol1 = float(kontrol_c001["marj"])
    marj_kol2 = float(test_c001["marj"])
    delta = marj_kol2 - marj_kol1
    manipulasyon_gecti = float(kontrol_c001["tavan_null95"]) < MANIPULASYON_ESIGI
    if not manipulasyon_gecti:
        hukum = "KAPASITE_MANIPULASYONU_ETKISIZ"
        sonraki = "YENI_MASA_BASI_TARAMASI_NORMAL_YENIDEN_ACMA"
        yeniden_acma = "NORMAL"
    elif marj_kol2 >= 0.15:
        hukum = "KAPASITE_DUSUK_GECTI"
        sonraki = "REVIZYON_KIRILMA_NOKTASI_ANALIZI"
        yeniden_acma = None
    elif delta >= 0.15:
        hukum = "KAPASITE_DUSUK_ZAYIF_TEYIT"
        sonraki = "YENI_MASA_BASI_TARAMASI_YUKSEK_YENIDEN_ACMA"
        yeniden_acma = "YUKSEK"
    else:
        hukum = "KAPASITE_DUSUK_ISARET_YOK"
        sonraki = "YENI_MASA_BASI_TARAMASI_NORMAL_YENIDEN_ACMA"
        yeniden_acma = "NORMAL"
    return {
        "hukum": hukum,
        "tarama_kesinligi": "HEURISTIK",
        "manipulasyon_kapisi": {
            "olculen_null95": float(kontrol_c001["tavan_null95"]),
            "strict_esik": MANIPULASYON_ESIGI,
            "gecti": manipulasyon_gecti,
        },
        "kol1_marj": marj_kol1,
        "kol2_marj": marj_kol2,
        "delta_marj": float(delta),
        "otomatik_sonraki_dal": sonraki,
        "yeniden_acma_onceligi": yeniden_acma,
        "daha_fazla_c_taramasi": False,
        "performans_iddiasi": False,
        "bddk_kapandi": False,
    }


def karsilastirma_tablosu(kontrol: dict, test: dict) -> dict:
    sonuc = {}
    for ad in kontrol:
        gozlenen_artis = test[ad]["tavan_gozlenen"] - kontrol[ad]["tavan_gozlenen"]
        null95_artis = test[ad]["tavan_null95"] - kontrol[ad]["tavan_null95"]
        sonuc[ad] = {
            "kol1_gozlenen": kontrol[ad]["tavan_gozlenen"],
            "kol2_gozlenen": test[ad]["tavan_gozlenen"],
            "gozlenen_degisim": float(gozlenen_artis),
            "kol1_null95": kontrol[ad]["tavan_null95"],
            "kol2_null95": test[ad]["tavan_null95"],
            "null95_degisim": float(null95_artis),
            "kol1_marj": kontrol[ad]["marj"],
            "kol2_marj": test[ad]["marj"],
            "delta_marj": float(test[ad]["marj"] - kontrol[ad]["marj"]),
            "gozlenen_artisi_null95_artisindan_buyuk": bool(gozlenen_artis > null95_artis),
            "doygun": ad in m12.DOYGUN_MODELLER,
            "yeni_baseline": ad == YENI_AD,
        }
    return sonuc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tekrar", type=int, default=1000, choices=(1000,))
    args = parser.parse_args()
    basla = time.perf_counter()

    seri, takvim_meta = m12.bddk_serisini_cacheden_oku()
    veri, _, feature_meta, tufe_meta = m12._snapshot_ve_feature_hazirla(seri)
    kontrol_feature = list(m12.m09.FEATURELAR)
    test_feature = [*kontrol_feature, *m12.BDDk_FEATURELARI]
    if len(kontrol_feature) != 10 or len(test_feature) != 14:
        raise AssertionError("Model 13 feature kapasitesi 10→14 olmalı")

    y_ay = veri.drop_duplicates("hedef_ay")["etiket"].to_numpy(dtype=object)
    perm = m12.permutasyon_matrisi(y_ay, args.tekrar)
    kontrol = oracle_kolu(veri, kontrol_feature, perm)
    harness = m12.harness_dogrula(kontrol)
    test = oracle_kolu(veri, test_feature, perm)
    test_tekrar = model12_test_tekrarini_dogrula(test)
    karar = karar_ver(kontrol[YENI_AD], test[YENI_AD])
    karsilastirma = karsilastirma_tablosu(kontrol, test)

    sure = float(time.perf_counter() - basla)
    if sure > 2400:
        raise RuntimeError(f"Model 13 40 dakika sınırını aştı: {sure:.1f} saniye")

    sonuc = {
        "model": "Model 13 BDDK C=0,01 kapasite-dusuk tekrar",
        "durum": "test_disi_in_sample_permutasyon_taramasi",
        "on_kayit_commit": "f2a9132",
        "model12_sonuc_commit": "23b42a2",
        "analiz_penceresi": ["2021-03", "2025-04"],
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
        "ag_erisim": {"yeni_http_cagrisi": 0, "cache_kullanildi": True},
        "cache_sha256": m12.BDDk_CACHE_SHA256,
        "cache_hash_yuklemede_dogrulandi": True,
        "takvim_denetimi": takvim_meta,
        "tufe_birim_lag_denetimi": tufe_meta,
        "feature_denetimi": feature_meta,
        "kapasite": {
            "kontrol_feature_sayisi": len(kontrol_feature),
            "test_feature_sayisi": len(test_feature),
            "nominal_artis_pct": 40.0,
            "config_sayisi": 5,
            "yeni_config": YENI_AD,
        },
        "seed": SEED,
        "permutasyon_tekrar": args.tekrar,
        "thread_sayisi": 1,
        "kol1_kontrol": kontrol,
        "harness_ozgun_dort": harness,
        "kol2_bddk_ekli": test,
        "model12_test_tekrar_denetimi": test_tekrar,
        "karsilastirma": karsilastirma,
        "karar": karar,
        "yorum_siniri": {
            "izinli": (
                "C=0,01 kapasite düşürme aynı iki kollu heuristikte sınandı; "
                "sonuç yalnız BDDK veri edinme önceliğini etkiler."
            ),
            "yasak": [
                "Bu bir OOF performans veya üretim becerisidir.",
                "Temiz vintaj aynı sonucu verirdi.",
                "BDDK sinyal taşımıyor.",
                "Başka bir C denenmelidir.",
            ],
        },
        "sure_saniye": sure,
    }
    yol = MODEL_DIR / "model_13_bddk_c001_ozet.json"
    yol.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
