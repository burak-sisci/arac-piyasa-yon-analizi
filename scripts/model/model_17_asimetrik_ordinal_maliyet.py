"""Model 17: Model 14 olasılıklarında sabit asimetrik ordinal maliyet kararı."""
from __future__ import annotations

import json
import time
from pathlib import Path
import sys

import numpy as np
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import model_15_frank_hall_ordinal as m15  # noqa: E402
import model_16_nested_persistence_lojistik_hibrit as m16  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

ADAY = "lojistik_c01_maliyet_014"
YEDILI_AILE = [*m14.MODEL_ADLARI, m15.ADAY, m16.ADAY, ADAY]
REF = m14.REF_BASELINE
TEKRAR = m14.TEKRAR
MALIYET = np.array([[0.0, 1.0, 4.0], [1.0, 0.0, 1.0], [4.0, 1.0, 0.0]])
MODEL16_REFERANS = {"mcc": 0.0031241897683421307, "macro_f1": 0.31359289027165616}


def beklenen_maliyet(prob: np.ndarray) -> np.ndarray:
    prob = np.asarray(prob, dtype=float)
    if prob.ndim != 2 or prob.shape[1] != 3:
        raise ValueError("Olasılık matrisi (n,3) olmalı")
    if np.any(prob < -1e-12) or not np.allclose(prob.sum(axis=1), 1, atol=1e-12, rtol=0):
        raise ValueError("Geçersiz sınıf olasılıkları")
    return prob @ MALIYET


def maliyet_tahmin(prob: np.ndarray) -> np.ndarray:
    """Minimum beklenen maliyet; eşitlikte down/stable/up sırasında soldaki."""
    labels = np.asarray(yd.FIXED_LABEL_ORDER, dtype=object)
    return labels[np.argmin(beklenen_maliyet(prob), axis=1)]


def rolling_maliyet_tahminleri(snapshot: pd.DataFrame):
    originler = rn.genisleyen_originler(
        "2019-01", m14.SON_DEGERLENDIRME_AYI,
        ilk_train_ay_sayisi=24, embargo_ay_sayisi=2,
    )
    maliyet_kayit, argmax_kayit = [], []
    for fold, origin in enumerate(originler, start=1):
        assert origin["degerlendirme"] < m14.KILITLI_TEST_BASLANGIC
        assert max(origin["train"]) <= origin["degerlendirme"] - 3
        train = snapshot[snapshot["hedef_ay"].isin(origin["train"])].copy()
        val = snapshot[
            snapshot["hedef_ay"].eq(origin["degerlendirme"])
            & snapshot["hafta_sirasi"].isin([1, 2, 3, 4])
        ].sort_values("hafta_sirasi").copy()
        prob = m16._fit_ve_prob(train, val)
        y_maliyet = maliyet_tahmin(prob)
        y_argmax = m16._tahmin(prob)
        costs = beklenen_maliyet(prob)
        for i, hafta in enumerate((1, 2, 3, 4)):
            ortak = {
                "fold": fold, "hedef_ay": str(origin["degerlendirme"]),
                "train_ay_sayisi": len(origin["train"]), "hafta_sirasi": hafta,
                "gercek": str(val["etiket"].iloc[i]),
            }
            maliyet_kayit.append({
                **ortak, "yaklasim": ADAY, "tahmin": str(y_maliyet[i]),
                "p_down": float(prob[i, 0]), "p_stable": float(prob[i, 1]),
                "p_up": float(prob[i, 2]), "beklenen_maliyet_down": float(costs[i, 0]),
                "beklenen_maliyet_stable": float(costs[i, 1]),
                "beklenen_maliyet_up": float(costs[i, 2]),
            })
            argmax_kayit.append({
                **ortak, "yaklasim": "lojistik_l2_c01", "tahmin": str(y_argmax[i])
            })
    return pd.DataFrame(maliyet_kayit), pd.DataFrame(argmax_kayit), originler


def argmax_kontrol_dogrula(argmax_df: pd.DataFrame, model14_df: pd.DataFrame) -> dict:
    ref = model14_df[model14_df["yaklasim"].eq("lojistik_l2_c01")].copy()
    kolon = ["fold", "hedef_ay", "train_ay_sayisi", "hafta_sirasi", "yaklasim", "gercek", "tahmin"]
    a = argmax_df.sort_values(["fold", "hafta_sirasi"])[kolon].reset_index(drop=True).astype(str)
    b = ref.sort_values(["fold", "hafta_sirasi"])[kolon].reset_index(drop=True).astype(str)
    uyumlu = len(a) == len(b) == 200 and a.equals(b)
    if not uyumlu:
        raise RuntimeError("STOP_ONLY_IF_ARGMAX_MODEL14_UYUSMAZLIGI")
    return {"satir_argmax": len(a), "satir_model14": len(b), "birebir_uyumlu": True}


def yedili_degerlendir(model14_df, model15_df, model16_df, model17_df) -> dict:
    birlesik = pd.concat([model14_df, model15_df, model16_df, model17_df], ignore_index=True, sort=False)
    gercek, tahminler, aylar = m14._matrisler(birlesik)
    assert len(aylar) == 50 and set(YEDILI_AILE).issubset(tahminler)
    idx = rn.hareketli_blok_indeksleri(50, tekrar=TEKRAR, blok_uzunlugu=4, seed=420)
    blok = rn.ortak_indeksli_metrik_dagilimlari(gercek, tahminler, idx)
    genel = {ad: m14._nokta(gercek, tahminler[ad]) for ad in tahminler}
    fark = {ad: blok["dagilimlar"][ad]["mcc"] - blok["dagilimlar"][REF]["mcc"] for ad in YEDILI_AILE}
    p = {ad: float((1 + np.sum(fark[ad] <= 0)) / (TEKRAR + 1)) for ad in YEDILI_AILE}
    holm = rn.holm_bonferroni(p, alfa=0.05)
    for ad in YEDILI_AILE:
        holm[ad]["delta_mcc_nokta"] = genel[ad]["mcc"] - genel[REF]["mcc"]
        holm[ad]["delta_macro_f1_nokta"] = genel[ad]["macro_f1"] - genel[REF]["macro_f1"]
        holm[ad]["delta_mcc_holm_alt_sinir"] = float(np.quantile(fark[ad], holm[ad]["holm_esik"]))
    yillar = np.array([int(x[:4]) for x in aylar])
    yil = {}
    for y in sorted(set(yillar)):
        tut = yillar != y
        yil[str(y)] = m14._nokta(gercek[tut], tahminler[ADAY][tut])["mcc"] - m14._nokta(
            gercek[tut], tahminler[REF][tut]
        )["mcc"]
    return {
        "genel_metrikler": genel, "holm_yedili_aile": holm,
        "maliyet_yil_jackknife": {
            "yil_disarida_delta_mcc": yil,
            "isaret_her_yil_pozitif": all(x > 0 for x in yil.values()),
        },
        "aile_siniri_notu": "Prompt43-46 yerel FWER; proje-omru kumulatif FWER degildir.",
    }


def canli_referans_dogrula(model14_ozet, model15_df, model16_df) -> dict:
    d14 = m15.model14_canli_referans_dogrula(model14_ozet)
    g15, t15, _ = m14._matrisler(model15_df)
    n15 = m14._nokta(g15, t15[m15.ADAY])
    g16, t16, _ = m14._matrisler(model16_df)
    n16 = m14._nokta(g16, t16[m16.ADAY])
    fark15 = {k: abs(n15[k] - m16.MODEL15_REFERANS[k]) for k in ("mcc", "macro_f1")}
    fark16 = {k: abs(n16[k] - MODEL16_REFERANS[k]) for k in ("mcc", "macro_f1")}
    if any(x > 1e-12 for x in [*fark15.values(), *fark16.values()]):
        raise RuntimeError(f"STOP_ONLY_IF_CANLI_REFERANS_UYUSMAZLIGI: {fark15}, {fark16}")
    return {"model14": d14, "model15_abs_fark": fark15, "model16_abs_fark": fark16}


def kapi_hesapla(d: dict, argmax: dict) -> dict:
    genel, h = d["genel_metrikler"], d["holm_yedili_aile"][ADAY]
    o, cog = genel[ADAY], genel["train_cogunlugu"]
    k = {
        "a_holm7_alt_sinir_pozitif": bool(h["h0_reddedildi"] and h["delta_mcc_holm_alt_sinir"] > 0),
        "b_delta_mcc_en_az_005": bool(h["delta_mcc_nokta"] >= 0.05),
        "c_delta_macro_f1_pozitif": bool(h["delta_macro_f1_nokta"] > 0),
        "d_yil_disinda_isaret_korunuyor": bool(d["maliyet_yil_jackknife"]["isaret_her_yil_pozitif"]),
        "e_model14_en_iyiyi_iki_metrikte_asiyor": bool(
            o["mcc"] > m15.MODEL14_REFERANS["mcc"] and o["macro_f1"] > m15.MODEL14_REFERANS["macro_f1"]
        ),
        "f_train_cogunlugunu_iki_metrikte_asiyor": bool(
            o["mcc"] > cog["mcc"] and o["macro_f1"] > cog["macro_f1"]
        ),
        "g_argmax_model14_200de200": bool(argmax["birebir_uyumlu"] and argmax["satir_argmax"] == 200),
    }
    return {"kosullar": k, "terfi": all(k.values())}


def main() -> None:
    t0 = time.time()
    ortam = m15.ortam_dogrula()
    ham = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    ham["hedef_ay"] = pd.PeriodIndex(ham["hedef_ay"], freq="M")
    guvenli, kilitli = m14.kilitli_test_disla(ham)
    snapshot = m14.feature_hazirla(guvenli)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    model14_ozet, model14_df, _ = m14.kol_calistir(snapshot, m14.TEST_FEATURELAR, "model14_canli")
    model15_df, _, _ = m15.rolling_ordinal_tahminleri(snapshot)
    model16_df, _, _, _ = m16.rolling_hibrit_tahminleri(snapshot)
    canli = canli_referans_dogrula(model14_ozet, model15_df, model16_df)
    model17_df, argmax_df, originler = rolling_maliyet_tahminleri(snapshot)
    argmax = argmax_kontrol_dogrula(argmax_df, model14_df)
    d = yedili_degerlendir(model14_df, model15_df, model16_df, model17_df)
    kapi = kapi_hesapla(d, argmax)
    karar = "TERFI_ADAYI_BULUNDU_MODEL17" if kapi["terfi"] else "ASIMETRIK_MALIYET_TERFI_YOK"
    sonuc = {
        "yonetici": "Rota-2 + Pusula",
        "onkayit": "prompts/veri/46_model17_asimetrik_ordinal_maliyet_onkayit.md",
        "ortam": ortam, "origin_sayisi": len(originler), "embargo_ay_sayisi": 2,
        "bootstrap_tekrar": TEKRAR, "maliyet_matrisi": MALIYET.tolist(),
        "canli_referans": canli, "argmax_model14_kontrol": argmax,
        **d, "terfi_kapisi": kapi, "karar": karar,
        "kilitli_test_disarida_birakilan_satir_sayisi": kilitli,
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
        "calisma_suresi_saniye": round(time.time() - t0, 1),
    }
    model17_df.to_csv(MODEL_DIR / "model_17_asimetrik_maliyet_tahminleri.csv", index=False, encoding="utf-8-sig")
    (MODEL_DIR / "model_17_asimetrik_maliyet_ozet.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
