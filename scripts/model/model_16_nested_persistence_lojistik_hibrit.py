"""Model 16: train-içi nested seçilen persistence–lojistik hibrit."""
from __future__ import annotations

import json
import time
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import model_15_frank_hall_ordinal as m15  # noqa: E402
import nowcast_baseline as nb  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

ADAY = "nested_persistence_lojistik_c01"
AGIRLIKLAR = (0.0, 0.25, 0.5, 0.75, 1.0)
ALTI_AILE = [*m14.MODEL_ADLARI, m15.ADAY, ADAY]
REF = m14.REF_BASELINE
TEKRAR = m14.TEKRAR

MODEL14_REFERANS = m15.MODEL14_REFERANS
MODEL15_REFERANS = {"mcc": 0.0857049536684403, "macro_f1": 0.33160241279832153}


def _lojistik() -> LogisticRegression:
    return LogisticRegression(
        C=0.1, penalty="l2", solver="lbfgs", max_iter=2000,
        class_weight="balanced", random_state=42,
    )


def hizali_olasilik(model: LogisticRegression, x: np.ndarray) -> np.ndarray:
    """Model sınıflarını sabit down/stable/up sırasına taşır; eksik sınıf sıfırdır."""
    ham = model.predict_proba(x)
    sonuc = np.zeros((len(x), len(yd.FIXED_LABEL_ORDER)), dtype=float)
    for kaynak_i, sinif in enumerate(model.classes_):
        if sinif not in yd.FIXED_LABEL_ORDER:
            raise AssertionError(f"Beklenmeyen model sınıfı: {sinif}")
        sonuc[:, yd.FIXED_LABEL_ORDER.index(str(sinif))] = ham[:, kaynak_i]
    toplam = sonuc.sum(axis=1)
    if not np.allclose(toplam, 1.0, atol=1e-12, rtol=0):
        raise AssertionError("Hizalı lojistik olasılık toplamı bir değil")
    return sonuc


def persistence_one_hot(sinif: str, n: int) -> np.ndarray:
    if sinif not in yd.FIXED_LABEL_ORDER:
        raise ValueError(f"Geçersiz persistence sınıfı: {sinif}")
    sonuc = np.zeros((n, len(yd.FIXED_LABEL_ORDER)), dtype=float)
    sonuc[:, yd.FIXED_LABEL_ORDER.index(sinif)] = 1.0
    return sonuc


def hibrit_olasilik(model_prob: np.ndarray, persistence_sinifi: str, w: float) -> np.ndarray:
    if w not in AGIRLIKLAR:
        raise ValueError(f"Ön-kayıt dışı ağırlık: {w}")
    model_prob = np.asarray(model_prob, dtype=float)
    p0 = persistence_one_hot(persistence_sinifi, len(model_prob))
    sonuc = w * model_prob + (1.0 - w) * p0
    if not np.allclose(sonuc.sum(axis=1), 1.0, atol=1e-12, rtol=0):
        raise AssertionError("Hibrit olasılık toplamı bir değil")
    return sonuc


def _tahmin(prob: np.ndarray) -> np.ndarray:
    labels = np.asarray(yd.FIXED_LABEL_ORDER, dtype=object)
    return labels[np.argmax(prob, axis=1)]


def agirlik_sec(metrikler: dict[float, dict]) -> tuple[float, str]:
    """Pareto filtresi + (MCC, macro-F1, -w) lexicographic seçim."""
    if 0.0 not in metrikler:
        raise KeyError("İç persistence (w=0) metriği yok")
    ref = metrikler[0.0]
    uygun = []
    for w in AGIRLIKLAR[1:]:
        m = metrikler[w]
        gerilemiyor = m["mcc"] >= ref["mcc"] and m["macro_f1"] >= ref["macro_f1"]
        iyilesiyor = m["mcc"] > ref["mcc"] or m["macro_f1"] > ref["macro_f1"]
        if gerilemiyor and iyilesiyor:
            uygun.append(w)
    if not uygun:
        return 0.0, "pareto_uygun_agirlik_yok"
    secilen = max(
        uygun,
        key=lambda w: (metrikler[w]["mcc"], metrikler[w]["macro_f1"], -w),
    )
    return float(secilen), "pareto_uygun_en_iyi"


def _fit_ve_prob(train: pd.DataFrame, val: pd.DataFrame) -> np.ndarray:
    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    xtr = scaler.fit_transform(imputer.fit_transform(train[m14.TEST_FEATURELAR]))
    xva = scaler.transform(imputer.transform(val[m14.TEST_FEATURELAR]))
    if train["etiket"].nunique() < 2:
        raise ValueError("Lojistik train tek sınıflı")
    model = _lojistik()
    model.fit(xtr, train["etiket"], sample_weight=train["agirlik"])
    return hizali_olasilik(model, xva)


def ic_agirlik_sec(snapshot: pd.DataFrame, dis_train_aylari: list[pd.Period]) -> tuple[float, dict]:
    """Yalnız dış train içinde nested rolling ile ağırlık seçer."""
    ilk, son = dis_train_aylari[0], dis_train_aylari[-1]
    ic_originler = rn.genisleyen_originler(
        ilk, son, ilk_train_ay_sayisi=12, embargo_ay_sayisi=2,
    )
    aylik_etiket = snapshot.drop_duplicates("hedef_ay").set_index("hedef_ay")["etiket"]
    gercekler: list[str] = []
    tahminler = {w: [] for w in AGIRLIKLAR}
    agirliklar: list[float] = []
    atlanan_tek_sinif = 0
    kullanilan_origin = 0
    for origin in ic_originler:
        if not set(origin["train"] + origin["embargo"] + [origin["degerlendirme"]]).issubset(
            set(dis_train_aylari)
        ):
            raise AssertionError("İç origin dış train sınırını aştı")
        train = snapshot[snapshot["hedef_ay"].isin(origin["train"])].copy()
        val = snapshot[
            snapshot["hedef_ay"].eq(origin["degerlendirme"])
            & snapshot["hafta_sirasi"].isin([1, 2, 3, 4])
        ].sort_values("hafta_sirasi").copy()
        if len(val) != 4 or val["etiket"].nunique() != 1:
            raise AssertionError("İç değerlendirme ayı dört haftalık değil")
        if train["etiket"].nunique() < 2:
            atlanan_tek_sinif += 1
            continue
        model_prob = _fit_ve_prob(train, val)
        bt, _ = nb.baseline_tahminleri(
            aylik_etiket, origin["train"], [origin["degerlendirme"]]
        )
        p_sinif = bt[REF][0]
        gercekler.extend(val["etiket"].astype(str).tolist())
        agirliklar.extend(val["agirlik"].astype(float).tolist())
        for w in AGIRLIKLAR:
            tahminler[w].extend(_tahmin(hibrit_olasilik(model_prob, p_sinif, w)).tolist())
        kullanilan_origin += 1

    denetim = {
        "ic_origin_toplam": len(ic_originler),
        "ic_origin_kullanilan": kullanilan_origin,
        "ic_origin_atlanan_tek_sinif": atlanan_tek_sinif,
    }
    if kullanilan_origin < 5:
        denetim.update({"secim_nedeni": "gecerli_ic_origin_5ten_az", "ic_metrikler": {}})
        return 0.0, denetim
    metrikler = {}
    for w in AGIRLIKLAR:
        m = yd.degerlendir(gercekler, tahminler[w], agirliklar=agirliklar)
        metrikler[w] = {"mcc": m["mcc_gorodkin"], "macro_f1": m["macro_f1"]}
    secilen, neden = agirlik_sec(metrikler)
    denetim.update({
        "secim_nedeni": neden,
        "secilen_w": secilen,
        "ic_metrikler": {str(w): metrikler[w] for w in AGIRLIKLAR},
    })
    return secilen, denetim


def rolling_hibrit_tahminleri(snapshot: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[dict], dict]:
    """50 dış origin için nested ağırlık seçer ve dış tahmini üretir."""
    originler = rn.genisleyen_originler(
        "2019-01", m14.SON_DEGERLENDIRME_AYI,
        ilk_train_ay_sayisi=24, embargo_ay_sayisi=2,
    )
    aylik_etiket = snapshot.drop_duplicates("hedef_ay").set_index("hedef_ay")["etiket"]
    kayitlar, denetim_kayitlari = [], []
    sayac = {"dis_origin": 0, "dis_model_fit": 0, "ic_model_fit": 0}
    for fold, origin in enumerate(originler, start=1):
        assert origin["degerlendirme"] < m14.KILITLI_TEST_BASLANGIC
        assert max(origin["train"]) <= origin["degerlendirme"] - 3
        secilen_w, ic = ic_agirlik_sec(snapshot, origin["train"])
        sayac["ic_model_fit"] += ic["ic_origin_kullanilan"]
        train = snapshot[snapshot["hedef_ay"].isin(origin["train"])].copy()
        val = snapshot[
            snapshot["hedef_ay"].eq(origin["degerlendirme"])
            & snapshot["hafta_sirasi"].isin([1, 2, 3, 4])
        ].sort_values("hafta_sirasi").copy()
        model_prob = _fit_ve_prob(train, val)
        bt, _ = nb.baseline_tahminleri(
            aylik_etiket, origin["train"], [origin["degerlendirme"]]
        )
        p_sinif = bt[REF][0]
        prob = hibrit_olasilik(model_prob, p_sinif, secilen_w)
        yhat = _tahmin(prob)
        for hafta, gercek, tahmin, p in zip(
            (1, 2, 3, 4), val["etiket"], yhat, prob
        ):
            kayitlar.append({
                "fold": fold, "hedef_ay": str(origin["degerlendirme"]),
                "train_ay_sayisi": len(origin["train"]), "hafta_sirasi": hafta,
                "yaklasim": ADAY, "gercek": str(gercek), "tahmin": str(tahmin),
                "secilen_w": secilen_w,
                "p_down": float(p[0]), "p_stable": float(p[1]), "p_up": float(p[2]),
            })
        denetim_kayitlari.append({
            "fold": fold, "hedef_ay": str(origin["degerlendirme"]),
            "dis_train_ilk": str(origin["train"][0]), "dis_train_son": str(origin["train"][-1]),
            "secilen_w": secilen_w, **ic,
        })
        sayac["dis_origin"] += 1
        sayac["dis_model_fit"] += 1
    if sayac["dis_origin"] != 50 or sayac["dis_model_fit"] != 50:
        raise AssertionError("Dış origin/fit sayısı 50 değil")
    return pd.DataFrame(kayitlar), pd.DataFrame(denetim_kayitlari), originler, sayac


def altili_degerlendir(
    model14_tahmin: pd.DataFrame,
    model15_tahmin: pd.DataFrame,
    model16_tahmin: pd.DataFrame,
) -> dict:
    birlesik = pd.concat(
        [model14_tahmin, model15_tahmin, model16_tahmin],
        ignore_index=True, sort=False,
    )
    gercek, tahminler, aylar = m14._matrisler(birlesik)
    assert len(aylar) == 50 and set(ALTI_AILE).issubset(tahminler)
    blok_idx = rn.hareketli_blok_indeksleri(50, tekrar=TEKRAR, blok_uzunlugu=4, seed=420)
    blok = rn.ortak_indeksli_metrik_dagilimlari(gercek, tahminler, blok_idx)
    genel = {ad: m14._nokta(gercek, tahminler[ad]) for ad in tahminler}
    fark = {
        ad: blok["dagilimlar"][ad]["mcc"] - blok["dagilimlar"][REF]["mcc"]
        for ad in ALTI_AILE
    }
    p_ham = {
        ad: float((1 + np.sum(fark[ad] <= 0)) / (TEKRAR + 1))
        for ad in ALTI_AILE
    }
    holm = rn.holm_bonferroni(p_ham, alfa=0.05)
    for ad in ALTI_AILE:
        holm[ad]["delta_mcc_nokta"] = genel[ad]["mcc"] - genel[REF]["mcc"]
        holm[ad]["delta_macro_f1_nokta"] = genel[ad]["macro_f1"] - genel[REF]["macro_f1"]
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
    return {
        "genel_metrikler": genel,
        "holm_altili_aile": holm,
        "hibrit_yil_jackknife": {
            "yil_disarida_delta_mcc": yil_farklari,
            "isaret_her_yil_pozitif": all(x > 0 for x in yil_farklari.values()),
        },
        "aile_siniri_notu": "Prompt43-45 yerel FWER; proje-omru kumulatif FWER degildir.",
    }


def canli_referans_dogrula(model14_ozet: dict, model15_tahmin: pd.DataFrame) -> dict:
    d14 = m15.model14_canli_referans_dogrula(model14_ozet)
    gercek, tahminler, _ = m14._matrisler(model15_tahmin)
    m15_nokta = m14._nokta(gercek, tahminler[m15.ADAY])
    fark = {
        k: abs(m15_nokta[k] - MODEL15_REFERANS[k])
        for k in ("mcc", "macro_f1")
    }
    if any(x > 1e-12 for x in fark.values()):
        raise RuntimeError(f"STOP_ONLY_IF_MODEL15_CANLI_REFERANS_UYUSMAZLIGI: {fark}")
    return {"model14": d14, "model15_nokta": m15_nokta, "model15_abs_fark": fark}


def kapi_hesapla(degerlendirme: dict, nested_sayac: dict) -> dict:
    genel = degerlendirme["genel_metrikler"]
    h = degerlendirme["holm_altili_aile"][ADAY]
    o, cog = genel[ADAY], genel["train_cogunlugu"]
    kosullar = {
        "a_holm6_alt_sinir_pozitif": bool(h["h0_reddedildi"] and h["delta_mcc_holm_alt_sinir"] > 0),
        "b_delta_mcc_en_az_005": bool(h["delta_mcc_nokta"] >= 0.05),
        "c_delta_macro_f1_pozitif": bool(h["delta_macro_f1_nokta"] > 0),
        "d_yil_disinda_isaret_korunuyor": bool(
            degerlendirme["hibrit_yil_jackknife"]["isaret_her_yil_pozitif"]
        ),
        "e_model14_en_iyiyi_iki_metrikte_asiyor": bool(
            o["mcc"] > MODEL14_REFERANS["mcc"] and o["macro_f1"] > MODEL14_REFERANS["macro_f1"]
        ),
        "f_train_cogunlugunu_iki_metrikte_asiyor": bool(
            o["mcc"] > cog["mcc"] and o["macro_f1"] > cog["macro_f1"]
        ),
        "g_50_dis_origin_train_ici_secim": bool(
            nested_sayac["dis_origin"] == 50 and nested_sayac["dis_model_fit"] == 50
        ),
    }
    return {"kosullar": kosullar, "terfi": all(kosullar.values())}


def main() -> None:
    t0 = time.time()
    ortam = m15.ortam_dogrula()
    ham = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    ham["hedef_ay"] = pd.PeriodIndex(ham["hedef_ay"], freq="M")
    guvenli, kilitli_sayisi = m14.kilitli_test_disla(ham)
    snapshot = m14.feature_hazirla(guvenli)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    assert (snapshot["hedef_ay"] < m14.KILITLI_TEST_BASLANGIC).all()

    model14_ozet, model14_tahmin, _ = m14.kol_calistir(
        snapshot, m14.TEST_FEATURELAR, "model14_canli_14_feature"
    )
    model15_tahmin, _, _ = m15.rolling_ordinal_tahminleri(snapshot)
    canli = canli_referans_dogrula(model14_ozet, model15_tahmin)
    hibrit, secim, originler, sayac = rolling_hibrit_tahminleri(snapshot)
    degerlendirme = altili_degerlendir(model14_tahmin, model15_tahmin, hibrit)
    kapi = kapi_hesapla(degerlendirme, sayac)
    karar = "TERFI_ADAYI_BULUNDU_MODEL16" if kapi["terfi"] else "NESTED_HIBRIT_TERFI_YOK"

    secim_dagilimi = {
        str(k): int(v) for k, v in secim["secilen_w"].value_counts().sort_index().items()
    }
    sonuc = {
        "yonetici": "Rota-2 + Pusula",
        "onkayit": "prompts/veri/45_model16_nested_persistence_lojistik_hibrit_onkayit.md",
        "ortam": ortam, "origin_sayisi": len(originler), "embargo_ay_sayisi": 2,
        "degerlendirme_ay_araligi": ["2021-03", "2025-04"],
        "bootstrap_tekrar": TEKRAR, "agirlik_izgarasi": list(AGIRLIKLAR),
        "canli_referans": canli, "nested_sayac": sayac,
        "secilen_agirlik_dagilimi": secim_dagilimi,
        **degerlendirme, "terfi_kapisi": kapi, "karar": karar,
        "kilitli_test_disarida_birakilan_satir_sayisi": kilitli_sayisi,
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
        "calisma_suresi_saniye": round(time.time() - t0, 1),
    }
    hibrit.to_csv(MODEL_DIR / "model_16_nested_hibrit_tahminleri.csv", index=False, encoding="utf-8-sig")
    secim.to_csv(MODEL_DIR / "model_16_nested_hibrit_secim_denetimi.csv", index=False, encoding="utf-8-sig")
    (MODEL_DIR / "model_16_nested_hibrit_ozet.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
