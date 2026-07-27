"""
GENIŞLETME AŞAMA 8 — Hedef keşif: noter devir hacmi × DOM (proxy_dom_gun).

Bu script KARAR VERMEZ (K1 hedef tanımını değiştirmez), MODEL KURMAZ. Yalnızca
noter_devir_toplam_adet (2018-01->2026-06, 102 ay, hiç eksik yok) ve
proxy_dom_gun (BETAM, 2024-01->2026-06, 28 ay dolu; 2024-05 ve 2025-02
BETAM'in rapor yayimlamadigi aylar oldugu icin eksik) serilerinin tek basina
davranisini, birbirleriyle iliskisini, ve bu ikisinden (+ proxy_satis_orani_pct
+ odmd_toplam_adet) turetilen bir kompozit "piyasa aktivite endeksi"nin fiyat
yonuyle iliskisini arastirir.

METODOLOJIK NOT: Tum "degisim" olcumleri, projenin genelinde kullanilan
ln(x_t/x_{t-1}) log-degisimiyle yapilir (genisletme_6/7 ile tutarli). ADF ve
mevsimsellik-regresyonu HAM SEVIYE yerine (trend karisimi olmasin diye) esas
olarak log-degisim uzerinde de calistirilir; ham seviye ADF'i ayrica raporlanir
(klasik "seviye durağan degil, degisim durağan" karsilastirmasi icin).

DOM'un iki BETAM bosluk ayi (2024-05, 2025-02), bu aylara giren VE bu aylardan
cikan gecisi NaN yapar (2 bosluk ay -> 4 NaN gecis) - bu yuzden DOM'un
log-degisim serisinde 30 potansiyel gecisten yalnizca 25'i gecerlidir. Kompozit
endeks DOM'a bagimli oldugu icin ayni 25 aylik pencereyle sinirlidir.

Girdi: data/processed/genisletme/veri_2018_bugun_etiketli.csv
Cikti:
  - data/processed/analiz/piyasa_aktivite_endeksi.csv
  - data/processed/analiz/hedef_kesif_tekli_seri_istatistik.csv
  - data/processed/analiz/hedef_kesif_iliski_ccf.csv
  - data/processed/analiz/hedef_kesif_gorseller/*.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
import statsmodels.formula.api as smf

REPO_KOKU = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_KOKU / "data" / "processed" / "genisletme"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"
GORSEL_DIR = ANALIZ_DIR / "hedef_kesif_gorseller"

ESIK_K = 0.5
MAKS_LAG = 6


def _log_degisim(seri: pd.Series) -> pd.Series:
    return np.log(seri / seri.shift(1))


def _oynaklik_bandi_etiket(log_degisim: pd.Series, k: float):
    sigma = log_degisim.std(ddof=1)
    esik = k * sigma

    def etiketle(x):
        if pd.isna(x):
            return "eksik"
        if x >= esik:
            return "up"
        if x <= -esik:
            return "down"
        return "stable"

    return log_degisim.map(etiketle), sigma


def _tanimlayici(seri: pd.Series) -> dict:
    g = seri.dropna()
    return {
        "n": int(len(g)), "ortalama": round(float(g.mean()), 4),
        "medyan": round(float(g.median()), 4), "std": round(float(g.std(ddof=1)), 4),
        "min": round(float(g.min()), 4), "q25": round(float(g.quantile(0.25)), 4),
        "q75": round(float(g.quantile(0.75)), 4), "maks": round(float(g.max()), 4),
    }


def _adf_ozet(seri: pd.Series) -> dict:
    g = seri.dropna()
    if len(g) < 8:
        return {"n": int(len(g)), "adf_ist": None, "p_degeri": None, "kritik_5pct": None, "yorum": "n<8, ADF guvenilmez"}
    ist, p, _, n_kullanilan, kritikler, _ = adfuller(g, autolag="AIC")
    return {
        "n": int(len(g)), "adf_ist": round(float(ist), 4), "p_degeri": round(float(p), 4),
        "kritik_5pct": round(float(kritikler["5%"]), 4),
        "yorum": "DURAGAN (p<0.05)" if p < 0.05 else "DURAGAN DEGIL / birim kok olasi (p>=0.05)",
    }


def _ay_dummy_varyans_payi(df_ay_deger: pd.DataFrame) -> dict:
    g = df_ay_deger.dropna()
    if len(g) < 15 or g["ay_no"].nunique() < 6:
        return {"n": int(len(g)), "benzersiz_ay": int(g["ay_no"].nunique()), "r2": None, "yorum": "n veya ay cesitliligi yetersiz - guvenilmez"}
    model = smf.ols("deger ~ C(ay_no)", data=g).fit()
    return {"n": int(len(g)), "benzersiz_ay": int(g["ay_no"].nunique()), "r2": round(float(model.rsquared), 4),
            "yorum": f"ay-sabiti (mevsimsellik) varyansin %{model.rsquared*100:.1f}'ini aciklar"}


def _ccf(x: pd.Series, y: pd.Series, maks_lag: int) -> pd.DataFrame:
    """x(t) ile y(t+lag) arasindaki Pearson korelasyonu, lag=-maks_lag..+maks_lag.
    lag>0: y, x'i GECIKMELI takip ediyor demektir (x oncu). Ortak indeks (referans_ayi) uzerinden hizalanir."""
    ortak_idx = x.index.intersection(y.index)
    x, y = x.reindex(ortak_idx), y.reindex(ortak_idx)
    satirlar = []
    for lag in range(-maks_lag, maks_lag + 1):
        y_kaydirilmis = y.shift(-lag)
        cift = pd.concat([x, y_kaydirilmis], axis=1).dropna()
        n = len(cift)
        if n < 5:
            satirlar.append({"lag": lag, "r": None, "p": None, "n": n, "az_gozlem": "EVET"})
            continue
        r, p = stats.pearsonr(cift.iloc[:, 0], cift.iloc[:, 1])
        satirlar.append({"lag": lag, "r": round(float(r), 4), "p": round(float(p), 4), "n": n,
                          "az_gozlem": "EVET" if n < 15 else "DIKKAT" if n < 20 else "hayir"})
    return pd.DataFrame(satirlar)


def main():
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    girdi = PROCESSED_DIR / "veri_2018_bugun_etiketli.csv"
    df = pd.read_csv(girdi).sort_values("referans_ayi").reset_index(drop=True)
    df["ay_dt"] = pd.to_datetime(df["referans_ayi"], format="%Y-%m")
    df["ay_no"] = df["ay_dt"].dt.month
    df = df.set_index("referans_ayi", drop=False)

    tek_seri_satirlari = []
    ccf_satirlari = []

    # =========================================================
    # GOREV 2 - tek basina seri analizi (noter + DOM)
    # =========================================================
    seriler = {
        "noter_devir_toplam_adet": df["noter_devir_toplam_adet"],
        "proxy_dom_gun": df["proxy_dom_gun"],
    }
    log_degisimler = {ad: _log_degisim(s) for ad, s in seriler.items()}

    for ad, seri in seriler.items():
        desc = _tanimlayici(seri)
        desc_log = _tanimlayici(log_degisimler[ad])
        adf_seviye = _adf_ozet(seri)
        adf_log = _adf_ozet(log_degisimler[ad])
        mevsim_df = pd.DataFrame({"ay_no": df["ay_no"], "deger": log_degisimler[ad]})
        mevsim = _ay_dummy_varyans_payi(mevsim_df)

        for tur, d in [("ham_seviye_tanimlayici", desc), ("log_degisim_tanimlayici", desc_log),
                       ("adf_ham_seviye", adf_seviye), ("adf_log_degisim", adf_log),
                       ("mevsimsellik_ay_dummy_r2_logdegisim", mevsim)]:
            satir = {"seri": ad, "olcum_turu": tur}
            satir.update(d)
            tek_seri_satirlari.append(satir)

        # 2b: zaman serisi + 3 aylik hareketli ortalama
        gecerli = seri.dropna()
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.loc[gecerli.index, "ay_dt"], gecerli.values, color="#898781", linewidth=1, label="ham deger", alpha=0.7)
        ax.plot(df.loc[gecerli.index, "ay_dt"], gecerli.rolling(3, min_periods=2).mean().values, color="#2a78d6", linewidth=2, label="3 aylik hareketli ort.")
        ax.set_title(f"{ad} - zaman serisi")
        ax.legend()
        fig.tight_layout()
        fig.savefig(GORSEL_DIR / f"{ad}_zaman_serisi.png", dpi=110)
        plt.close(fig)

        # 2c: ay-bazli boxplot (ham seviye)
        gruplar = [seri[df["ay_no"] == ay].dropna().values for ay in range(1, 13)]
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.boxplot(gruplar, tick_labels=[str(a) for a in range(1, 13)])
        ax.set_xlabel("Ay (1-12)")
        ax.set_title(f"{ad} - ay bazli dagilim (ham seviye)" + (" [DIKKAT: az gozlem/ay]" if ad == "proxy_dom_gun" else ""))
        fig.tight_layout()
        fig.savefig(GORSEL_DIR / f"{ad}_ay_boxplot.png", dpi=110)
        plt.close(fig)

        # 2e: ACF/PACF (log-degisim uzerinde, ilk 12 lag)
        gecerli_log = log_degisimler[ad].dropna()
        nlags = min(12, len(gecerli_log) // 2 - 1)
        if nlags >= 2:
            fig, axes = plt.subplots(1, 2, figsize=(11, 4))
            plot_acf(gecerli_log, lags=nlags, ax=axes[0])
            axes[0].set_title(f"{ad} - ACF (log-degisim)")
            plot_pacf(gecerli_log, lags=nlags, ax=axes[1], method="ywm")
            axes[1].set_title(f"{ad} - PACF (log-degisim)")
            fig.tight_layout()
            fig.savefig(GORSEL_DIR / f"{ad}_acf_pacf.png", dpi=110)
            plt.close(fig)

    tek_seri_df = pd.DataFrame(tek_seri_satirlari)
    tek_seri_csv = ANALIZ_DIR / "hedef_kesif_tekli_seri_istatistik.csv"
    tek_seri_df.to_csv(tek_seri_csv, index=False, encoding="utf-8-sig")

    # =========================================================
    # GOREV 3 - noter x DOM iliskisi (ortusen donem)
    # =========================================================
    noter_log = log_degisimler["noter_devir_toplam_adet"]
    dom_log = log_degisimler["proxy_dom_gun"]
    ortak_3 = pd.concat([noter_log, dom_log], axis=1, keys=["noter", "dom"]).dropna()
    n3 = len(ortak_3)
    r3_p, p3_p = stats.pearsonr(ortak_3["noter"], ortak_3["dom"])
    r3_s, p3_s = stats.spearmanr(ortak_3["noter"], ortak_3["dom"])

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(ortak_3["dom"], ortak_3["noter"], color="#2a78d6")
    ax.set_xlabel("DOM aylik log-degisim")
    ax.set_ylabel("Noter devir aylik log-degisim")
    ax.set_title(f"Noter devri x DOM (n={n3}, pearson r={r3_p:.3f})")
    fig.tight_layout()
    fig.savefig(GORSEL_DIR / "noter_dom_scatter.png", dpi=110)
    plt.close(fig)

    ccf_noter_dom = _ccf(dom_log, noter_log, MAKS_LAG)
    ccf_noter_dom["cift"] = "dom_oncu -> noter (lag>0: dom, noter'i gecikmeli takip eder degil, noter dom'u takip eder)"
    ccf_satirlari.append(ccf_noter_dom)

    fig, ax = plt.subplots(figsize=(8, 4))
    renkler = ["#e34948" if (r is not None and abs(r) == ccf_noter_dom["r"].abs().max()) else "#2a78d6" for r in ccf_noter_dom["r"]]
    ax.bar(ccf_noter_dom["lag"], ccf_noter_dom["r"].fillna(0), color=renkler)
    ax.axhline(0, color="#898781", linewidth=0.8)
    ax.set_xlabel("Lag (ay) - pozitif: DOM, noter'den once hareket eder")
    ax.set_ylabel("Pearson r")
    ax.set_title("Capraz-korelasyon: DOM (t) x Noter devir (t+lag)")
    fig.tight_layout()
    fig.savefig(GORSEL_DIR / "cross_correlation_noter_dom.png", dpi=110)
    plt.close(fig)

    # =========================================================
    # GOREV 4 - kompozit "piyasa aktivite endeksi"
    # =========================================================
    satis_log = _log_degisim(df["proxy_satis_orani_pct"])
    odmd_log = _log_degisim(df["odmd_toplam_adet"])
    dom_flipped_log = -dom_log  # DOM azaliyor -> piyasa hizlaniyor -> pozitif katki

    bilesenler_3 = pd.concat(
        [noter_log, dom_flipped_log, satis_log], axis=1,
        keys=["noter_log_degisim", "dom_flipped_log_degisim", "satis_orani_log_degisim"],
    ).dropna()
    n4a = len(bilesenler_3)
    z_3 = (bilesenler_3 - bilesenler_3.mean()) / bilesenler_3.std(ddof=1)
    piyasa_aktivite_basit = z_3.mean(axis=1)

    # 4b: PCA (4 bilesen: + odmd)
    bilesenler_4 = pd.concat(
        [noter_log, dom_flipped_log, satis_log, odmd_log], axis=1,
        keys=["noter_log_degisim", "dom_flipped_log_degisim", "satis_orani_log_degisim", "odmd_log_degisim"],
    ).dropna()
    n4b = len(bilesenler_4)
    z_4 = (bilesenler_4 - bilesenler_4.mean()) / bilesenler_4.std(ddof=1)
    pca = PCA(n_components=min(4, n4b))
    pc_skorlari = pca.fit_transform(z_4.values)
    pc1_yuk = pca.components_[0]
    if pc1_yuk[0] < 0:  # noter_log_degisim referans - PC1 isaretini noter ile ayni yone cevir
        pc1_yuk = -pc1_yuk
        pc_skorlari[:, 0] = -pc_skorlari[:, 0]
    pca_aciklanan_varyans = pca.explained_variance_ratio_
    pc1_seri = pd.Series(pc_skorlari[:, 0], index=z_4.index)

    # 4c: kompozit endeksin kendi yonu (dogrudan, k*sigma bandi - endeks zaten "degisim" olcegi)
    piyasa_yon, sigma_piyasa = _oynaklik_bandi_etiket(piyasa_aktivite_basit, ESIK_K)
    dagilim_piyasa = piyasa_yon.value_counts().to_dict()

    # cikti tablosu (piyasa_aktivite_endeksi.csv)
    endeks_df = pd.DataFrame({"referans_ayi": bilesenler_3.index})
    endeks_df = endeks_df.merge(bilesenler_3.reset_index().rename(columns={"index": "referans_ayi"}), on="referans_ayi", how="left")
    endeks_df = endeks_df.merge(z_3.reset_index().rename(columns={"index": "referans_ayi", **{c: f"z_{c}" for c in z_3.columns}}), on="referans_ayi", how="left", suffixes=("", ""))
    endeks_df["piyasa_aktivite_endeksi_basit"] = piyasa_aktivite_basit.reindex(endeks_df["referans_ayi"]).values
    endeks_df["piyasa_aktivite_yon"] = piyasa_yon.reindex(endeks_df["referans_ayi"]).values
    endeks_df = endeks_df.merge(
        pd.DataFrame({"referans_ayi": pc1_seri.index, "pca_pc1_skoru": pc1_seri.values, "odmd_log_degisim": odmd_log.reindex(pc1_seri.index).values}),
        on="referans_ayi", how="left",
    )
    endeks_df["proxy_nominal_log_degisim"] = df["proxy_aylik_log_degisim"].reindex(endeks_df["referans_ayi"]).values
    endeks_df["proxy_reel_log_degisim"] = df["proxy_reel_aylik_log_degisim"].reindex(endeks_df["referans_ayi"]).values
    endeks_csv = ANALIZ_DIR / "piyasa_aktivite_endeksi.csv"
    endeks_df.to_csv(endeks_csv, index=False, encoding="utf-8-sig")

    # 4d: gorsel - kompozit + bilesenler, ortak z-score ekseni
    fig, ax = plt.subplots(figsize=(11, 5))
    aylar_dt = pd.to_datetime(bilesenler_3.index, format="%Y-%m")
    ax.plot(aylar_dt, z_3["noter_log_degisim"], color="#898781", linewidth=1, alpha=0.6, label="z(noter devir log-degisim)")
    ax.plot(aylar_dt, z_3["dom_flipped_log_degisim"], color="#eb6834", linewidth=1, alpha=0.6, label="z(-DOM log-degisim)")
    ax.plot(aylar_dt, z_3["satis_orani_log_degisim"], color="#d4b106", linewidth=1, alpha=0.6, label="z(satis orani log-degisim)")
    ax.plot(aylar_dt, piyasa_aktivite_basit.values, color="#2a78d6", linewidth=2.5, label="piyasa aktivite endeksi (kompozit)")
    ax.axhline(0, color="#0b0b0b", linewidth=0.6)
    ax.legend(fontsize=8)
    ax.set_title("Piyasa aktivite endeksi ve bilesenleri (z-score ortak eksen)")
    fig.tight_layout()
    fig.savefig(GORSEL_DIR / "kompozit_endeks_bilesenler.png", dpi=110)
    plt.close(fig)

    # =========================================================
    # GOREV 5 - fiyat hedefiyle capraz iliski
    # =========================================================
    fiyat_nominal = df["proxy_aylik_log_degisim"]
    fiyat_reel = df["proxy_reel_aylik_log_degisim"]

    sonuc_5 = {}
    for fiyat_ad, fiyat_seri in [("proxy_nominal", fiyat_nominal), ("proxy_reel", fiyat_reel)]:
        ortak = pd.concat([piyasa_aktivite_basit, fiyat_seri], axis=1, keys=["endeks", "fiyat"]).dropna()
        n5 = len(ortak)
        if n5 >= 3:
            r5_p, p5_p = stats.pearsonr(ortak["endeks"], ortak["fiyat"])
            r5_s, p5_s = stats.spearmanr(ortak["endeks"], ortak["fiyat"])
        else:
            r5_p = p5_p = r5_s = p5_s = None
        sonuc_5[fiyat_ad] = {"n": n5, "pearson_r": round(float(r5_p), 4) if r5_p is not None else None,
                              "pearson_p": round(float(p5_p), 4) if p5_p is not None else None,
                              "spearman_r": round(float(r5_s), 4) if r5_s is not None else None,
                              "spearman_p": round(float(p5_p), 4) if p5_p is not None else None}
        ccf_5 = _ccf(piyasa_aktivite_basit, fiyat_seri, MAKS_LAG)
        ccf_5["cift"] = f"piyasa_aktivite_endeksi(t) -> {fiyat_ad}(t+lag) [lag>0: endeks oncu]"
        ccf_satirlari.append(ccf_5)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(ccf_5["lag"], ccf_5["r"].fillna(0), color="#2a78d6")
        ax.axhline(0, color="#898781", linewidth=0.8)
        ax.set_xlabel("Lag (ay) - pozitif: endeks, fiyattan once hareket eder")
        ax.set_ylabel("Pearson r")
        ax.set_title(f"Capraz-korelasyon: piyasa aktivite endeksi (t) x {fiyat_ad} (t+lag)")
        fig.tight_layout()
        fig.savefig(GORSEL_DIR / f"kompozit_{fiyat_ad}_ccf.png", dpi=110)
        plt.close(fig)

    ccf_tum = pd.concat(ccf_satirlari, ignore_index=True)
    ccf_csv = ANALIZ_DIR / "hedef_kesif_iliski_ccf.csv"
    ccf_tum.to_csv(ccf_csv, index=False, encoding="utf-8-sig")

    # =========================================================
    # OZET CIKTISI (konsol - PM raporuna aktarilacak)
    # =========================================================
    print("=== GENISLETME 8 - HEDEF KESIF: NOTER DEVIR x DOM ===\n")
    print("--- GOREV 2: tekli seri istatistikleri ---")
    print(tek_seri_df.to_string(index=False))
    print()
    print(f"--- GOREV 3: noter x DOM (contemporaneous), n={n3} ---")
    print(f"Pearson r={r3_p:.4f} (p={p3_p:.4f})  Spearman r={r3_s:.4f} (p={p3_s:.4f})")
    print("Capraz-korelasyon (dom -> noter, lag -6..+6):")
    print(ccf_noter_dom[["lag", "r", "p", "n", "az_gozlem"]].to_string(index=False))
    print()
    print(f"--- GOREV 4: kompozit endeks ---")
    print(f"4a (z-score ortalama, 3 bilesen: noter, -dom, satis_orani), n={n4a}")
    print(f"4b (PCA, 4 bilesen: + odmd), n={n4b}")
    print(f"    PC1 aciklanan varyans: {pca_aciklanan_varyans[0]*100:.1f}%  |  tum bilesenlerin aciklanan varyansi: {[round(v*100,1) for v in pca_aciklanan_varyans]}")
    print(f"    PC1 yukleri (noter, -dom, satis_orani, odmd): {[round(float(x),4) for x in pc1_yuk]}")
    print(f"4c: sigma(kompozit)={sigma_piyasa:.4f}, esik=k*sigma={ESIK_K*sigma_piyasa:.4f}")
    print(f"    sinif dagilimi (piyasa_aktivite_yon): {dagilim_piyasa}")
    print()
    print("--- GOREV 5: kompozit endeks x fiyat yonu ---")
    for fiyat_ad, sonuc in sonuc_5.items():
        print(f"{fiyat_ad}: n={sonuc['n']}  pearson r={sonuc['pearson_r']} (p={sonuc['pearson_p']})  spearman r={sonuc['spearman_r']}")
    print()
    print("Capraz-korelasyon (endeks -> fiyat, lag -6..+6):")
    for fiyat_ad in sonuc_5:
        alt = ccf_tum[ccf_tum["cift"].str.contains(fiyat_ad)]
        print(f"  [{fiyat_ad}]")
        print(alt[["lag", "r", "p", "n", "az_gozlem"]].to_string(index=False))
    print()
    print(f"Cikti: {endeks_csv}")
    print(f"Cikti: {tek_seri_csv}")
    print(f"Cikti: {ccf_csv}")
    print(f"Gorseller: {GORSEL_DIR}")


if __name__ == "__main__":
    main()
