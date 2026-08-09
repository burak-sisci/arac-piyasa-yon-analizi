"""Model 15: tek-aday Frank-Hall ordinal doğrulaması.

Ön-kayıt: prompts/veri/44_model15_frank_hall_ordinal_onkayit.md.
Model 14'ün 14 as-of feature'ı aynen kullanılır. Model 14'ün dört adayı ve
tek ordinal aday aynı süreçte, aynı 50 origin ve aynı blok bootstrap evreninde
beşli Holm ailesine girer. Kilitli test hiçbir veri yoluna alınmaz.
"""
from __future__ import annotations

import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import nowcast_baseline as nb  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

ADAY = "frank_hall_l2_c01"
MODEL14_ADAYLARI = list(m14.MODEL_ADLARI)
BESLI_AILE = [*MODEL14_ADAYLARI, ADAY]
REF = m14.REF_BASELINE
TEKRAR = m14.TEKRAR
KILITLI_TEST_BASLANGIC = m14.KILITLI_TEST_BASLANGIC
SON_DEGERLENDIRME_AYI = m14.SON_DEGERLENDIRME_AYI

ORTAM_KILIDI = {
    "python": "3.12.7",
    "scikit_learn": "1.7.2",
    "numpy": "2.3.5",
    "pandas": "2.3.3",
}
MODEL14_REFERANS = {
    "mcc": 0.0885950392362906,
    "macro_f1": 0.3658910750843209,
    "persistence_mcc": 0.0165080995517002,
    "persistence_macro_f1": 0.36415215989684074,
}


def ortam_dogrula() -> dict:
    """Ön-kayıt Bölüm 4 ortamını doğrular; farklı sklearn yolu yasaktır."""
    beklenen_python = (REPO_KOKU / ".venv312" / "Scripts" / "python.exe").resolve()
    gozlenen_python = Path(sys.executable).resolve()
    meta = {
        "python_executable": str(gozlenen_python),
        "python": platform.python_version(),
        "scikit_learn": sklearn.__version__,
        "numpy": np.__version__,
        "pandas": pd.__version__,
    }
    uyusmazlik = {
        anahtar: {"beklenen": beklenen, "gozlenen": meta[anahtar]}
        for anahtar, beklenen in ORTAM_KILIDI.items()
        if meta[anahtar] != beklenen
    }
    if gozlenen_python != beklenen_python:
        uyusmazlik["python_executable"] = {
            "beklenen": str(beklenen_python), "gozlenen": str(gozlenen_python)
        }
    if uyusmazlik:
        raise RuntimeError(f"STOP_ONLY_IF_ORTAM_UYUSMAZLIGI: {uyusmazlik}")
    return meta


def binary_hedefler(etiket: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """down < stable < up sırasındaki iki kümülatif ikili hedefi üretir."""
    etiket = etiket.astype(str)
    gecersiz = sorted(set(etiket) - set(yd.FIXED_LABEL_ORDER))
    if gecersiz:
        raise ValueError(f"Geçersiz ordinal etiket: {gecersiz}")
    z1 = etiket.isin(["stable", "up"]).astype(int).to_numpy()
    z2 = etiket.eq("up").astype(int).to_numpy()
    return z1, z2


def monoton_olasiliklar(q1, q2) -> np.ndarray:
    """İki-nokta L2-isotonic projeksiyonu ve üç-sınıf olasılıklarını üretir."""
    q1 = np.asarray(q1, dtype=float)
    q2 = np.asarray(q2, dtype=float)
    if q1.shape != q2.shape:
        raise ValueError("q1 ve q2 şekilleri eşleşmiyor")
    if np.any(~np.isfinite(q1)) or np.any(~np.isfinite(q2)):
        raise ValueError("Kümülatif olasılık sonlu değil")
    if np.any((q1 < 0) | (q1 > 1) | (q2 < 0) | (q2 > 1)):
        raise ValueError("Kümülatif olasılık [0,1] dışında")
    capraz = q1 < q2
    orta = (q1 + q2) / 2.0
    q1p = np.where(capraz, orta, q1)
    q2p = np.where(capraz, orta, q2)
    olasilik = np.column_stack([1.0 - q1p, q1p - q2p, q2p])
    if np.any(olasilik < -1e-12) or np.any(olasilik > 1 + 1e-12):
        raise AssertionError("Projeksiyon sonrası olasılık aralık ihlali")
    if not np.allclose(olasilik.sum(axis=1), 1.0, atol=1e-12, rtol=0):
        raise AssertionError("Projeksiyon sonrası olasılık toplamı bir değil")
    olasilik = np.clip(olasilik, 0.0, 1.0)
    return olasilik


def ordinal_tahmin(olasilik: np.ndarray) -> np.ndarray:
    """Sabit down/stable/up sırasıyla argmax; eşitlikte soldaki sınıf."""
    olasilik = np.asarray(olasilik, dtype=float)
    if olasilik.ndim != 2 or olasilik.shape[1] != 3:
        raise ValueError("Ordinal olasılık matrisi (n,3) olmalı")
    labels = np.asarray(yd.FIXED_LABEL_ORDER, dtype=object)
    return labels[np.argmax(olasilik, axis=1)]


def _pozitif_olasilik(model: LogisticRegression, x: np.ndarray) -> np.ndarray:
    siniflar = list(model.classes_)
    if siniflar != [0, 1]:
        raise AssertionError(f"İkili alt-model sınıfları [0,1] değil: {siniflar}")
    return model.predict_proba(x)[:, siniflar.index(1)]


def _ikili_model() -> LogisticRegression:
    return LogisticRegression(
        C=0.1, penalty="l2", solver="lbfgs", max_iter=2000,
        class_weight="balanced", random_state=42,
    )


def rolling_ordinal_tahminleri(snapshot: pd.DataFrame) -> tuple[pd.DataFrame, list[dict], dict]:
    """Her origin'de preprocessing ve iki ikili modeli yalnız train'de fit eder."""
    originler = rn.genisleyen_originler(
        "2019-01", SON_DEGERLENDIRME_AYI,
        ilk_train_ay_sayisi=24, embargo_ay_sayisi=2,
    )
    kayitlar: list[dict] = []
    denetim = {
        "on_isleme_fit_sayisi": 0,
        "binary_model_fit_sayisi": 0,
        "monoton_projeksiyon_satir_sayisi": 0,
        "ham_capraz_satir_sayisi": 0,
    }
    for fold_no, origin in enumerate(originler, start=1):
        assert max(origin["train"]) <= origin["degerlendirme"] - 3
        assert origin["embargo"] == [
            origin["degerlendirme"] - 2, origin["degerlendirme"] - 1
        ]
        assert origin["degerlendirme"] < KILITLI_TEST_BASLANGIC
        assert all(x < KILITLI_TEST_BASLANGIC for x in origin["train"])
        assert all(x < KILITLI_TEST_BASLANGIC for x in origin["embargo"])

        train = snapshot[snapshot["hedef_ay"].isin(origin["train"])].copy()
        val = snapshot[
            snapshot["hedef_ay"].eq(origin["degerlendirme"])
            & snapshot["hafta_sirasi"].isin([1, 2, 3, 4])
        ].sort_values("hafta_sirasi").copy()
        assert val["hafta_sirasi"].tolist() == [1, 2, 3, 4]
        assert val["etiket"].nunique() == 1

        imputer = SimpleImputer(strategy="median", add_indicator=True)
        scaler = StandardScaler()
        xtr = scaler.fit_transform(imputer.fit_transform(train[m14.TEST_FEATURELAR]))
        xva = scaler.transform(imputer.transform(val[m14.TEST_FEATURELAR]))
        denetim["on_isleme_fit_sayisi"] += 1

        z1, z2 = binary_hedefler(train["etiket"])
        model1, model2 = _ikili_model(), _ikili_model()
        agirlik = train["agirlik"].to_numpy(dtype=float)
        model1.fit(xtr, z1, sample_weight=agirlik)
        model2.fit(xtr, z2, sample_weight=agirlik)
        denetim["binary_model_fit_sayisi"] += 2
        q1, q2 = _pozitif_olasilik(model1, xva), _pozitif_olasilik(model2, xva)
        denetim["ham_capraz_satir_sayisi"] += int(np.sum(q1 < q2))
        prob = monoton_olasiliklar(q1, q2)
        denetim["monoton_projeksiyon_satir_sayisi"] += len(prob)
        yhat = ordinal_tahmin(prob)

        gercek = str(val["etiket"].iloc[0])
        for hafta, tahmin, p in zip((1, 2, 3, 4), yhat, prob):
            yd.olasiliklari_dogrula(*p, atol=1e-12)
            kayitlar.append({
                "fold": fold_no, "hedef_ay": str(origin["degerlendirme"]),
                "train_ay_sayisi": len(origin["train"]), "hafta_sirasi": hafta,
                "yaklasim": ADAY, "gercek": gercek, "tahmin": str(tahmin),
                "p_down": float(p[0]), "p_stable": float(p[1]), "p_up": float(p[2]),
            })

    if len(originler) != 50 or denetim["on_isleme_fit_sayisi"] != 50:
        raise AssertionError("Origin/preprocessing fit sayısı sözleşmeden saptı")
    if denetim["binary_model_fit_sayisi"] != 100:
        raise AssertionError("İkili model fit sayısı 100 değil")
    return pd.DataFrame(kayitlar), originler, denetim


def _matrisler(birlesik: pd.DataFrame):
    return m14._matrisler(birlesik)


def besli_degerlendir(model14_tahmin: pd.DataFrame, ordinal_tahminler: pd.DataFrame) -> dict:
    """Beş adayın aynı bootstrap evrenindeki metrik/Holm/jackknife sonucunu üretir."""
    birlesik = pd.concat([model14_tahmin, ordinal_tahminler], ignore_index=True, sort=False)
    gercek, tahminler, aylar = _matrisler(birlesik)
    assert len(aylar) == 50 and max(aylar) == SON_DEGERLENDIRME_AYI
    assert set(BESLI_AILE).issubset(tahminler)

    blok_idx = rn.hareketli_blok_indeksleri(50, tekrar=TEKRAR, blok_uzunlugu=4, seed=420)
    blok = rn.ortak_indeksli_metrik_dagilimlari(gercek, tahminler, blok_idx)
    genel = {ad: m14._nokta(gercek, tahminler[ad]) for ad in tahminler}
    fark = {
        ad: blok["dagilimlar"][ad]["mcc"] - blok["dagilimlar"][REF]["mcc"]
        for ad in BESLI_AILE
    }
    p_ham = {
        ad: float((1 + np.sum(fark[ad] <= 0)) / (TEKRAR + 1))
        for ad in BESLI_AILE
    }
    holm = rn.holm_bonferroni(p_ham, alfa=0.05)
    for ad in BESLI_AILE:
        holm[ad]["delta_mcc_nokta"] = genel[ad]["mcc"] - genel[REF]["mcc"]
        holm[ad]["delta_macro_f1_nokta"] = (
            genel[ad]["macro_f1"] - genel[REF]["macro_f1"]
        )
        holm[ad]["delta_mcc_holm_alt_sinir"] = float(
            np.quantile(fark[ad], holm[ad]["holm_esik"])
        )

    yillar = np.array([int(x[:4]) for x in aylar])
    yil_farklari = {}
    for yil in sorted(set(yillar)):
        tut = yillar != yil
        yil_farklari[str(yil)] = (
            m14._nokta(gercek[tut], tahminler[ADAY][tut])["mcc"]
            - m14._nokta(gercek[tut], tahminler[REF][tut])["mcc"]
        )
    ordinal_jackknife = {
        "yil_disarida_delta_mcc": yil_farklari,
        "isaret_her_yil_pozitif": all(x > 0 for x in yil_farklari.values()),
    }
    return {
        "genel_metrikler": genel,
        "holm_besli_aile": holm,
        "ordinal_yil_jackknife": ordinal_jackknife,
        "aile_siniri_notu": (
            "Prompt43+44 yerel FWER ailesidir; proje-omru kumulatif FWER iddiasi degildir."
        ),
    }


def model14_canli_referans_dogrula(model14_ozet: dict) -> dict:
    lojistik = model14_ozet["genel_metrikler"]["lojistik_l2_c01"]["nokta"]
    persistence = model14_ozet["genel_metrikler"][REF]["nokta"]
    gozlenen = {
        "mcc": lojistik["mcc"], "macro_f1": lojistik["macro_f1"],
        "persistence_mcc": persistence["mcc"],
        "persistence_macro_f1": persistence["macro_f1"],
    }
    fark = {
        k: abs(float(gozlenen[k]) - float(MODEL14_REFERANS[k]))
        for k in MODEL14_REFERANS
    }
    if any(v > 1e-12 for v in fark.values()):
        raise RuntimeError(f"STOP_ONLY_IF_MODEL14_CANLI_REFERANS_UYUSMAZLIGI: {fark}")
    return {"gozlenen": gozlenen, "abs_fark": fark, "uyumlu": True}


def kapi_hesapla(degerlendirme: dict) -> dict:
    genel = degerlendirme["genel_metrikler"]
    h = degerlendirme["holm_besli_aile"][ADAY]
    o = genel[ADAY]
    cogunluk = genel["train_cogunlugu"]
    kosullar = {
        "a_holm5_alt_sinir_pozitif": bool(
            h["h0_reddedildi"] and h["delta_mcc_holm_alt_sinir"] > 0
        ),
        "b_delta_mcc_en_az_005": bool(h["delta_mcc_nokta"] >= 0.05),
        "c_delta_macro_f1_pozitif": bool(h["delta_macro_f1_nokta"] > 0),
        "d_yil_disinda_isaret_korunuyor": bool(
            degerlendirme["ordinal_yil_jackknife"]["isaret_her_yil_pozitif"]
        ),
        "e_model14_en_iyiyi_iki_metrikte_asiyor": bool(
            o["mcc"] > MODEL14_REFERANS["mcc"]
            and o["macro_f1"] > MODEL14_REFERANS["macro_f1"]
        ),
        "f_train_cogunlugunu_iki_metrikte_asiyor": bool(
            o["mcc"] > cogunluk["mcc"] and o["macro_f1"] > cogunluk["macro_f1"]
        ),
    }
    return {"kosullar": kosullar, "terfi": all(kosullar.values())}


def main() -> None:
    baslangic = time.time()
    ortam = ortam_dogrula()
    ham = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    ham["hedef_ay"] = pd.PeriodIndex(ham["hedef_ay"], freq="M")
    guvenli, kilitli_sayisi = m14.kilitli_test_disla(ham)
    snapshot = m14.feature_hazirla(guvenli)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    assert (snapshot["hedef_ay"] < KILITLI_TEST_BASLANGIC).all()

    model14_ozet, model14_tahmin, _ = m14.kol_calistir(
        snapshot, m14.TEST_FEATURELAR, "model14_canli_14_feature"
    )
    model14_dogrulama = model14_canli_referans_dogrula(model14_ozet)
    ordinal_df, originler, ordinal_denetim = rolling_ordinal_tahminleri(snapshot)
    degerlendirme = besli_degerlendir(model14_tahmin, ordinal_df)
    kapi = kapi_hesapla(degerlendirme)
    karar = "TERFI_ADAYI_BULUNDU_MODEL15" if kapi["terfi"] else "ORDINAL_TEK_ADAY_TERFI_YOK"

    sonuc = {
        "yonetici": "Rota-2 + Pusula",
        "onkayit": "prompts/veri/44_model15_frank_hall_ordinal_onkayit.md",
        "ortam": ortam,
        "origin_sayisi": len(originler), "embargo_ay_sayisi": 2,
        "degerlendirme_ay_araligi": ["2021-03", "2025-04"],
        "bootstrap_tekrar": TEKRAR,
        "featurelar": m14.TEST_FEATURELAR,
        "model14_canli_referans": model14_dogrulama,
        "ordinal_denetim": ordinal_denetim,
        **degerlendirme,
        "terfi_kapisi": kapi,
        "karar": karar,
        "kilitli_test_disarida_birakilan_satir_sayisi": kilitli_sayisi,
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
        "calisma_suresi_saniye": round(time.time() - baslangic, 1),
    }
    ordinal_df.to_csv(
        MODEL_DIR / "model_15_frank_hall_ordinal_tahminleri.csv",
        index=False, encoding="utf-8-sig",
    )
    (MODEL_DIR / "model_15_frank_hall_ordinal_ozet.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
