"""Haftalik guncellenen aylik nowcast icin sizintisiz naif baseline'lar.

Bu modul model egitmez. Tahmin ayi M icin operasyon aninda son kesin bilinen
target ayinin M-2 oldugu K10 sozlesmesini uygular. Bu nedenle persistence,
M-2 ayinin yon etiketini; mevsimsel baseline ise M-12 etiketini tasir.
"""
from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from yon_degerlendirme import FIXED_LABEL_ORDER, degerlendir


def _period_serisi(etiketler: pd.Series) -> pd.Series:
    sonuc = etiketler.copy().sort_index()
    sonuc.index = pd.PeriodIndex(sonuc.index, freq="M")
    return sonuc


def baseline_tahminleri(
    etiketler: pd.Series,
    train_aylari: Iterable,
    degerlendirme_aylari: Iterable,
) -> tuple[dict[str, list[str]], str]:
    """Train cogunlugu, as-of persistence M-2 ve seasonal M-12 tahminleri."""
    seri = _period_serisi(etiketler)
    train = [pd.Period(x, freq="M") for x in train_aylari]
    degerlendirme = [pd.Period(x, freq="M") for x in degerlendirme_aylari]
    train_etiket = seri.reindex(train)
    train_etiket = train_etiket[train_etiket.isin(FIXED_LABEL_ORDER)]
    if train_etiket.empty:
        raise ValueError("Train bolumunde gecerli etiket yok")
    sayilar = train_etiket.value_counts().reindex(FIXED_LABEL_ORDER, fill_value=0)
    # Esitlikte sabit label sirasi deterministik karar verir.
    cogunluk = str(sayilar.idxmax())

    tahminler = {
        "train_cogunlugu": [cogunluk] * len(degerlendirme),
        "persistence_m_eksi_2": [seri.get(ay - 2, "eksik") for ay in degerlendirme],
        "seasonal_t_eksi_12": [seri.get(ay - 12, "eksik") for ay in degerlendirme],
    }
    for ad, tahmin in tahminler.items():
        gecersiz = sorted(set(tahmin) - set(FIXED_LABEL_ORDER))
        if gecersiz:
            raise ValueError(f"{ad} icin gecersiz/eksik tahmin var: {gecersiz}")
    return tahminler, cogunluk


def baseline_degerlendir(
    etiketler: pd.Series,
    train_aylari: Iterable,
    degerlendirme_aylari: Iterable,
) -> dict:
    """Baseline'lari ay-esit birimde MCC, macro-F1 ve accuracy ile olcer."""
    seri = _period_serisi(etiketler)
    aylar = [pd.Period(x, freq="M") for x in degerlendirme_aylari]
    gercek = seri.reindex(aylar).tolist()
    if any(x not in FIXED_LABEL_ORDER for x in gercek):
        raise ValueError("Degerlendirme bolumunde eksik/gecersiz gercek etiket var")
    tahminler, cogunluk = baseline_tahminleri(seri, train_aylari, aylar)
    return {
        "train_cogunluk_sinifi": cogunluk,
        "degerlendirme_aylari": [str(x) for x in aylar],
        "gercek": gercek,
        "tahminler": tahminler,
        "metrikler": {ad: degerlendir(gercek, yhat) for ad, yhat in tahminler.items()},
    }


def snapshot_sirasi_kapsami(snapshot: pd.DataFrame, aylar: Iterable) -> dict:
    """Hafta sirasina gore karsilastirilabilir ay kapsamlarini raporlar.

    Baseline tahmini ay icinde degismedigi icin burada 'bilgi kazanimi' iddiasi
    uretilmez. Fonksiyon, ileride feature kullanan adaylarin adil hafta-egirisi
    icin hangi aylarin her sirada mevcut oldugunu denetlenebilir hale getirir.
    """
    gerekli = {"hedef_ay", "hafta_sirasi", "etiket"}
    if not gerekli.issubset(snapshot.columns):
        raise ValueError(f"Eksik snapshot sutunlari: {sorted(gerekli-set(snapshot.columns))}")
    veri = snapshot.copy()
    veri["hedef_ay"] = pd.PeriodIndex(veri["hedef_ay"], freq="M")
    secilen = {pd.Period(x, freq="M") for x in aylar}
    veri = veri[veri["hedef_ay"].isin(secilen)]
    sonuc = {}
    for sira, grup in veri.groupby("hafta_sirasi", sort=True):
        sonuc[str(int(sira))] = {
            "ay_sayisi": int(grup["hedef_ay"].nunique()),
            "aylar": sorted(grup["hedef_ay"].astype(str).unique().tolist()),
            "sinif_dagilimi": {
                sinif: int((grup.drop_duplicates("hedef_ay")["etiket"] == sinif).sum())
                for sinif in FIXED_LABEL_ORDER
            },
        }
    return sonuc


__all__ = ["baseline_degerlendir", "baseline_tahminleri", "snapshot_sirasi_kapsami"]
