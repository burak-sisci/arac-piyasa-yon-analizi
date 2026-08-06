"""Model 11 hedef yapisi ve bilgi tavani icin saf istatistik yardimcilari."""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

import numpy as np
import pandas as pd

from yon_degerlendirme import FIXED_LABEL_ORDER, degerlendir


def deterministik_mod(etiketler: Iterable[str]) -> str:
    sayim = Counter(etiketler)
    if not sayim:
        raise ValueError("Bos etiketlerde mod hesaplanamaz")
    return max(FIXED_LABEL_ORDER, key=lambda x: (sayim[x], -FIXED_LABEL_ORDER.index(x)))


def capraz_tablo(x: Iterable[str], y: Iterable[str]) -> np.ndarray:
    x, y = list(x), list(y)
    if len(x) != len(y) or not x:
        raise ValueError("Capraz tablo girdileri esit ve bos olmayan uzunlukta olmali")
    x_sinif = sorted(set(x), key=str)
    y_sinif = sorted(set(y), key=str)
    xi = {v: i for i, v in enumerate(x_sinif)}
    yi = {v: i for i, v in enumerate(y_sinif)}
    tablo = np.zeros((len(x_sinif), len(y_sinif)), dtype=int)
    for a, b in zip(x, y):
        tablo[xi[a], yi[b]] += 1
    return tablo


def ki_kare_ve_cramer_v(x: Iterable[str], y: Iterable[str]) -> tuple[float, float]:
    tablo = capraz_tablo(x, y).astype(float)
    n = tablo.sum()
    satir, sutun = tablo.sum(axis=1), tablo.sum(axis=0)
    beklenen = np.outer(satir, sutun) / n
    gecerli = beklenen > 0
    ki2 = float((((tablo - beklenen) ** 2)[gecerli] / beklenen[gecerli]).sum())
    payda = n * min(tablo.shape[0] - 1, tablo.shape[1] - 1)
    v = float(np.sqrt(ki2 / payda)) if payda > 0 else 0.0
    return ki2, v


def permutasyon_cramer(
    x: Iterable[str], y: Iterable[str], *, tekrar: int = 10000, seed: int = 42
) -> dict:
    x, y = np.asarray(list(x), dtype=object), np.asarray(list(y), dtype=object)
    if len(x) != len(y):
        raise ValueError("Permutasyon girdileri esit uzunlukta olmali")
    goz_ki2, goz_v = ki_kare_ve_cramer_v(x, y)
    rng = np.random.default_rng(seed)
    asan = 0
    for _ in range(tekrar):
        ki2, _ = ki_kare_ve_cramer_v(x, rng.permutation(y))
        asan += ki2 >= goz_ki2
    return {"ki_kare": goz_ki2, "cramer_v": goz_v,
            "permutasyon_p": float((1 + asan) / (tekrar + 1)), "tekrar": tekrar}


def oracle_durum_tahmini(
    durumlar: Iterable, y: Iterable[str], *, ortalama_hucre_min: float = 8.0
) -> tuple[list[str], dict]:
    durumlar, y = list(durumlar), list(y)
    if len(durumlar) != len(y) or not y:
        raise ValueError("Oracle durum/y girdileri esit ve bos olmayan olmali")
    sayim = Counter(durumlar)
    ortalama = len(y) / len(sayim)
    if len(sayim) > 6 or ortalama < ortalama_hucre_min:
        raise ValueError("Oracle durum uzayi doygunluk kisitini ihlal ediyor")
    modlar = {}
    for durum in sayim:
        modlar[durum] = deterministik_mod([e for d, e in zip(durumlar, y) if d == durum])
    return [modlar[d] for d in durumlar], {
        "durum_sayisi": len(sayim), "ortalama_hucre_n": ortalama,
        "minimum_hucre_n": min(sayim.values()),
        "hucre_sayilari": {str(k): int(v) for k, v in sayim.items()},
    }


def oracle_durum_null(
    durumlar: Iterable,
    y: Iterable[str],
    *,
    tekrar: int = 2000,
    seed: int = 42,
) -> dict:
    durumlar, y = list(durumlar), np.asarray(list(y), dtype=object)
    tahmin, hucre = oracle_durum_tahmini(durumlar, y)
    gozlenen = degerlendir(y, tahmin)["mcc_gorodkin"]
    rng = np.random.default_rng(seed)
    null = np.empty(tekrar)
    for i in range(tekrar):
        yp = rng.permutation(y)
        pred, _ = oracle_durum_tahmini(durumlar, yp)
        null[i] = degerlendir(yp, pred)["mcc_gorodkin"]
    return {"tavan_gozlenen": gozlenen, "tavan_null95": float(np.quantile(null, 0.95)),
            "null_tekrar": tekrar, **hucre}


def bilgi_maskesini_dogrula(featurelar: Iterable[str]) -> None:
    featurelar = list(featurelar)
    yasak_tam = {"noter_devir_otomobil_adet", "noter_devir_otomobil_adet_lag1ay"}
    bulunan = sorted(yasak_tam & set(featurelar))
    if bulunan:
        raise ValueError(f"M-1/M bilgi maskesi ihlali: {bulunan}")


def yillik_ve_kayan_paylar(etiket: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    seri = etiket.copy()
    seri.index = pd.PeriodIndex(seri.index, freq="M")
    yillik = []
    for yil, grup in seri.groupby(seri.index.year):
        yillik.append({"yil": int(yil), "n": len(grup), **{
            f"{s}_pay": float((grup == s).mean()) for s in FIXED_LABEL_ORDER}})
    kayan = pd.DataFrame(index=seri.index)
    for s in FIXED_LABEL_ORDER:
        kayan[f"{s}_pay_12ay"] = seri.eq(s).astype(float).rolling(12, min_periods=12).mean()
    return pd.DataFrame(yillik), kayan.reset_index(names="hedef_ay")


__all__ = ["bilgi_maskesini_dogrula", "deterministik_mod", "ki_kare_ve_cramer_v",
           "oracle_durum_null", "oracle_durum_tahmini", "permutasyon_cramer",
           "yillik_ve_kayan_paylar"]
