# -*- coding: utf-8 -*-
"""Birlesik target setlerinden, target ile |korelasyon| < esik olan (veya
yetersiz gozlem nedeniyle korelasyonu hesaplanamayan) feature'lari eler."""

from pathlib import Path

import pandas as pd

PROJE_KOKU = Path(__file__).resolve().parent.parent
VERI_DIR = PROJE_KOKU / "data" / "birlesik_target_setleri"
ESIK = 0.1
MIN_PERIODS = 12

HEDEFLER = ["target_1ay_hiz", "target_3ay_hiz"]
COKLU_DOGRUSALLIK_ESIK = 0.9


def filtrele(target):
    girdi = VERI_DIR / f"{target}_tum_featurelar.csv"
    df = pd.read_csv(girdi)
    feats = [c for c in df.columns if c not in ("referans_ayi", target)]

    corr = df[feats + [target]].corr(min_periods=MIN_PERIODS)[target].drop(target)

    tutulan = corr[corr.abs() >= ESIK].sort_values()
    elenen = corr[(corr.abs() < ESIK) | corr.isna()].sort_values()

    ozet = pd.DataFrame({
        "feature": corr.index,
        "korelasyon": corr.values,
        "karar": ["tutuldu" if f in tutulan.index else "elendi" for f in corr.index],
    }).sort_values("korelasyon")
    ozet_yolu = VERI_DIR / f"{target}_korelasyon_filtre_ozeti.csv"
    ozet.to_csv(ozet_yolu, index=False)

    kalan_kolonlar = ["referans_ayi", *tutulan.index.tolist(), target]
    filtreli = df[kalan_kolonlar]
    cikti_yolu = VERI_DIR / f"{target}_tum_featurelar_filtreli.csv"
    filtreli.to_csv(cikti_yolu, index=False)

    print(f"=== {target} ===")
    print(f"Toplam feature: {len(feats)} | Tutulan: {len(tutulan)} | Elenen: {len(elenen)}")
    print("Elenenler:")
    print(elenen.to_string())
    print(f"Filtreli veri: {cikti_yolu.name} ({filtreli.shape[0]} satir, {len(tutulan)} feature + target)")
    print(f"Ozet: {ozet_yolu.name}")
    print()


def coklu_dogrusalligi_azalt(target):
    """Filtreli veride birbirine >esik korele feature ciftlerinden target ile
    en yuksek |korelasyona| sahip olani tutar, digerlerini eler."""
    girdi = VERI_DIR / f"{target}_tum_featurelar_filtreli.csv"
    df = pd.read_csv(girdi)
    feats = [c for c in df.columns if c not in ("referans_ayi", target)]

    hedef_korr = df[feats + [target]].corr(min_periods=MIN_PERIODS)[target].drop(target)
    feat_korr = df[feats].corr(min_periods=MIN_PERIODS)

    # Baglanti bilesenleri (union-find) ile >esik korele feature gruplarini bul
    ebeveyn = {f: f for f in feats}

    def bul(f):
        while ebeveyn[f] != f:
            f = ebeveyn[f]
        return f

    def birlestir(a, b):
        ra, rb = bul(a), bul(b)
        if ra != rb:
            ebeveyn[ra] = rb

    ciftler = []
    for i, a in enumerate(feats):
        for b in feats[i + 1:]:
            v = feat_korr.loc[a, b]
            if pd.notna(v) and abs(v) > COKLU_DOGRUSALLIK_ESIK:
                ciftler.append((a, b, v))
                birlestir(a, b)

    gruplar = {}
    for f in feats:
        gruplar.setdefault(bul(f), []).append(f)

    elenen = []
    tutulan = list(feats)
    for kok, grup in gruplar.items():
        if len(grup) < 2:
            continue
        en_iyi = max(grup, key=lambda f: abs(hedef_korr[f]))
        for f in grup:
            if f != en_iyi:
                elenen.append(f)
                tutulan.remove(f)

    print(f"=== {target}: coklu dogrusallik filtresi (>{COKLU_DOGRUSALLIK_ESIK}) ===")
    print(f"Bulunan yuksek-korelasyon ciftleri:")
    for a, b, v in sorted(ciftler, key=lambda x: -abs(x[2])):
        print(f"  {a:38s} {b:38s} {v:.4f}")
    print(f"Elenenler (grup icinde target korelasyonu daha dusuk olanlar):")
    for f in elenen:
        print(f"  {f:38s} hedef_korr={hedef_korr[f]:.4f}")
    print(f"Toplam feature: {len(feats)} | Tutulan: {len(tutulan)} | Elenen: {len(elenen)}")

    kalan_kolonlar = ["referans_ayi", *tutulan, target]
    nihai = df[kalan_kolonlar]
    cikti_yolu = VERI_DIR / f"{target}_tum_featurelar_final.csv"
    nihai.to_csv(cikti_yolu, index=False)
    print(f"Nihai veri: {cikti_yolu.name} ({nihai.shape[0]} satir, {len(tutulan)} feature + target)")
    print()


if __name__ == "__main__":
    import sys
    hedefler = sys.argv[1:] if len(sys.argv) > 1 else ["target_3ay_hiz"]
    for hedef in hedefler:
        filtrele(hedef)
        coklu_dogrusalligi_azalt(hedef)
