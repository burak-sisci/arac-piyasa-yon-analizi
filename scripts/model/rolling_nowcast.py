"""Nowcast icin test-disi genisleyen-origin ve ay-bootstrap yardimcilari."""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from yon_degerlendirme import FIXED_LABEL_ORDER, degerlendir


def genisleyen_originler(
    baslangic_ayi,
    son_degerlendirme_ayi,
    *,
    ilk_train_ay_sayisi: int = 24,
    embargo_ay_sayisi: int = 2,
) -> list[dict]:
    """Her sonraki ay icin genisleyen train + embargo + tek-ay origin kurar."""
    baslangic = pd.Period(baslangic_ayi, freq="M")
    son = pd.Period(son_degerlendirme_ayi, freq="M")
    if ilk_train_ay_sayisi < 12:
        raise ValueError("ilk_train_ay_sayisi en az 12 olmalidir")
    if embargo_ay_sayisi < 1:
        raise ValueError("embargo_ay_sayisi en az 1 olmalidir")
    ilk_degerlendirme = baslangic + ilk_train_ay_sayisi + embargo_ay_sayisi
    if ilk_degerlendirme > son:
        raise ValueError("Istenen aralikta degerlendirme origini olusmuyor")
    sonuc = []
    for ay in pd.period_range(ilk_degerlendirme, son, freq="M"):
        train_bitis = ay - embargo_ay_sayisi - 1
        train = list(pd.period_range(baslangic, train_bitis, freq="M"))
        embargo = [train_bitis + i for i in range(1, embargo_ay_sayisi + 1)]
        sonuc.append({"train": train, "embargo": embargo, "degerlendirme": ay})
    return sonuc


def bootstrap_metrik(
    y_gercek: Iterable[str],
    y_tahmin: Iterable[str],
    *,
    tekrar: int = 2000,
    seed: int = 42,
) -> dict:
    """Bagimsiz ay satirlarini yeniden ornekleyerek MCC/macro-F1 CI uretir."""
    gercek = np.asarray(list(y_gercek), dtype=object)
    tahmin = np.asarray(list(y_tahmin), dtype=object)
    if len(gercek) != len(tahmin) or len(gercek) < 2:
        raise ValueError("Bootstrap icin esit uzunlukta en az iki gozlem gerekir")
    if tekrar < 100:
        raise ValueError("Bootstrap tekrar sayisi en az 100 olmalidir")
    nokta = degerlendir(gercek, tahmin)
    rng = np.random.default_rng(seed)
    mcc, f1 = [], []
    for _ in range(tekrar):
        idx = rng.integers(0, len(gercek), size=len(gercek))
        metrik = degerlendir(gercek[idx], tahmin[idx])
        mcc.append(metrik["mcc_gorodkin"])
        f1.append(metrik["macro_f1"])
    return {
        "n_ay": len(gercek),
        "mcc_nokta": nokta["mcc_gorodkin"],
        "mcc_ci95": [float(np.quantile(mcc, 0.025)), float(np.quantile(mcc, 0.975))],
        "macro_f1_nokta": nokta["macro_f1"],
        "macro_f1_ci95": [float(np.quantile(f1, 0.025)), float(np.quantile(f1, 0.975))],
    }


def bootstrap_mcc_farki(
    y_gercek: Iterable[str],
    aday: Iterable[str],
    referans: Iterable[str],
    *,
    tekrar: int = 2000,
    seed: int = 42,
) -> dict:
    """Ayni ay ornekleriyle aday eksi referans MCC farkinin esli CI'ini kurar."""
    gercek = np.asarray(list(y_gercek), dtype=object)
    aday = np.asarray(list(aday), dtype=object)
    referans = np.asarray(list(referans), dtype=object)
    if not (len(gercek) == len(aday) == len(referans)) or len(gercek) < 2:
        raise ValueError("Esli bootstrap girdileri esit uzunlukta olmalidir")
    rng = np.random.default_rng(seed)
    farklar = []
    for _ in range(tekrar):
        idx = rng.integers(0, len(gercek), size=len(gercek))
        ma = degerlendir(gercek[idx], aday[idx])["mcc_gorodkin"]
        mr = degerlendir(gercek[idx], referans[idx])["mcc_gorodkin"]
        farklar.append(ma - mr)
    nokta = (
        degerlendir(gercek, aday)["mcc_gorodkin"]
        - degerlendir(gercek, referans)["mcc_gorodkin"]
    )
    return {
        "mcc_farki_nokta": float(nokta),
        "mcc_farki_ci95": [
            float(np.quantile(farklar, 0.025)),
            float(np.quantile(farklar, 0.975)),
        ],
    }


__all__ = ["bootstrap_mcc_farki", "bootstrap_metrik", "genisleyen_originler"]


def hareketli_blok_indeksleri(
    n_ay: int,
    *,
    tekrar: int = 2000,
    blok_uzunlugu: int = 4,
    seed: int = 42,
) -> np.ndarray:
    """Ortak kullanilacak hareketli-blok ay indeks matrisini uretir."""
    if n_ay < blok_uzunlugu or blok_uzunlugu < 1:
        raise ValueError("n_ay blok uzunlugundan kucuk olamaz")
    if tekrar < 100:
        raise ValueError("Bootstrap tekrar sayisi en az 100 olmalidir")
    rng = np.random.default_rng(seed)
    blok_sayisi = int(np.ceil(n_ay / blok_uzunlugu))
    baslangiclar = rng.integers(0, n_ay - blok_uzunlugu + 1, size=(tekrar, blok_sayisi))
    ofset = np.arange(blok_uzunlugu)
    return (baslangiclar[:, :, None] + ofset).reshape(tekrar, -1)[:, :n_ay]


def iid_indeksleri(n_ay: int, *, tekrar: int = 2000, seed: int = 42) -> np.ndarray:
    """Yalniz duyarlilik analizi icin blok=1 ay indeksleri."""
    if n_ay < 2 or tekrar < 100:
        raise ValueError("IID bootstrap icin n>=2 ve tekrar>=100 gerekir")
    return np.random.default_rng(seed).integers(0, n_ay, size=(tekrar, n_ay))


def _havuzla(matris: np.ndarray, ay_indeksleri: np.ndarray) -> np.ndarray:
    """[ay, hafta] matrisini bootstrap ay sirasi ile havuzlar."""
    return matris[ay_indeksleri].reshape(-1)


def ortak_indeksli_metrik_dagilimlari(
    gercek: np.ndarray,
    tahminler: dict[str, np.ndarray],
    indeksler: np.ndarray,
) -> dict:
    """Ayni ay indekslerini tum yaklasimlarda kullanarak MCC/F1 dagilimi kurar."""
    gercek = np.asarray(gercek, dtype=object)
    if gercek.ndim != 2 or gercek.shape[1] != 4:
        raise ValueError("gercek matrisi [ay, 4 hafta] biciminde olmalidir")
    for ad, tahmin in tahminler.items():
        if np.asarray(tahmin).shape != gercek.shape:
            raise ValueError(f"{ad} tahmin matrisi gercekle ayni bicimde degil")
    kod = {etiket: i for i, etiket in enumerate(FIXED_LABEL_ORDER)}
    try:
        yg = np.vectorize(kod.__getitem__)(gercek[indeksler]).reshape(len(indeksler), -1)
    except KeyError as exc:
        raise ValueError(f"Gecersiz etiket: {exc}") from exc
    gercek_sinif_sayilari = np.stack([(yg == k).sum(axis=1) for k in range(3)], axis=1)
    bozuk = (gercek_sinif_sayilari == 0).any(axis=1)
    dagilim = {}
    tahmin_dejenere_orani = {}
    for ad, tahmin in tahminler.items():
        yt = np.vectorize(kod.__getitem__)(
            np.asarray(tahmin, dtype=object)[indeksler]
        ).reshape(len(indeksler), -1)
        hucre_kodu = yg * 3 + yt
        cm = np.stack([(hucre_kodu == k).sum(axis=1) for k in range(9)], axis=1)
        cm = cm.reshape(-1, 3, 3).astype(float)
        toplam = cm.sum(axis=(1, 2))
        dogru = np.trace(cm, axis1=1, axis2=2)
        gercek_toplam = cm.sum(axis=2)
        tahmin_toplam = cm.sum(axis=1)
        pay = dogru * toplam - (gercek_toplam * tahmin_toplam).sum(axis=1)
        payda = np.sqrt(
            (toplam**2 - (tahmin_toplam**2).sum(axis=1))
            * (toplam**2 - (gercek_toplam**2).sum(axis=1))
        )
        mcc = np.divide(pay, payda, out=np.zeros_like(pay), where=payda != 0)
        tahmin_dejenere_orani[ad] = float((payda == 0).mean())
        tp = np.diagonal(cm, axis1=1, axis2=2)
        f1_payda = gercek_toplam + tahmin_toplam
        f1_sinif = np.divide(2 * tp, f1_payda, out=np.zeros_like(tp), where=f1_payda != 0)
        dagilim[ad] = {"mcc": mcc, "macro_f1": f1_sinif.mean(axis=1)}
    return {
        "dagilimlar": dagilim,
        "gercek_sinif_eksik_cekilis_orani": float(bozuk.mean()),
        "tahmin_dejenere_cekilis_orani": tahmin_dejenere_orani,
    }


def holm_bonferroni(p_degerleri: dict[str, float], alfa: float = 0.05) -> dict:
    """Dort aday ailesi icin Holm sirali karar ve duzeltilmis p degeri."""
    sirali = sorted(p_degerleri, key=p_degerleri.get)
    m = len(sirali)
    sonuc = {}
    onceki_duzeltilmis = 0.0
    red_zinciri_acik = True
    for rank, ad in enumerate(sirali, start=1):
        katsayi = m - rank + 1
        duzeltilmis = max(onceki_duzeltilmis, min(1.0, p_degerleri[ad] * katsayi))
        esik = alfa / katsayi
        reddedildi = red_zinciri_acik and p_degerleri[ad] <= esik
        if not reddedildi:
            red_zinciri_acik = False
        sonuc[ad] = {
            "rank": rank,
            "ham_p_tek_yonlu": float(p_degerleri[ad]),
            "holm_esik": float(esik),
            "holm_duzeltilmis_p": float(duzeltilmis),
            "h0_reddedildi": bool(reddedildi),
        }
        onceki_duzeltilmis = duzeltilmis
    return sonuc


__all__ = [
    "bootstrap_mcc_farki", "bootstrap_metrik", "genisleyen_originler",
    "hareketli_blok_indeksleri", "holm_bonferroni", "iid_indeksleri",
    "ortak_indeksli_metrik_dagilimlari",
]
