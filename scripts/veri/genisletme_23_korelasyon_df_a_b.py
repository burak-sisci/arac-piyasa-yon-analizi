"""
GENIŞLETME AŞAMA 23 — DF-A ve DF-B için korelasyon matrisi + ısı haritası
görseli.

Bu script SADECE Pearson korelasyon matrisi hesaplar ve görselleştirir.
Hedef/model değiştirmez, yorum/karar üretmez (PM raporu ayrıca istenecek).

NOT (metodolojik, ileride PM raporunda detaylandırılacak): Korelasyon,
sütunların HAM SEVİYE (level) değerleri üzerinden hesaplanmıştır - bazı
sütunlar zaten değişim/oran (ör. tufe_aylik_degisim, proxy_aylik_log_degisim,
enag_aylik) iken bazıları trend taşıyan seviye serileridir (ör. tufe_endeks,
usdtry_aysonu, brut_ucret_maas_endeksi_2021_100). İki trend taşıyan seviye
serisi arasındaki yüksek korelasyon, ortak zaman trendinden kaynaklanan
SAHTE (spurious) bir korelasyon olabilir - bu, ham sonuçları yorumlarken
akılda tutulmalı (bkz. daha önceki pm_rapor_sutun_temizlik_korelasyon.md
Bölüm 4e'deki benzer uyarı).

Girdi:
  - data/processed/dataframes/df_a_kapsama_testli_v2.csv
  - data/processed/dataframes/df_b_zengin_2024_bugun_v2.csv
Çıktı:
  - data/processed/analiz/korelasyon_matrisi_df_a.csv
  - data/processed/analiz/korelasyon_matrisi_df_b.csv
  - data/processed/analiz/gorseller/korelasyon_isi_haritasi_df_a.png
  - data/processed/analiz/gorseller/korelasyon_isi_haritasi_df_b.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DATAFRAMES_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"
GORSEL_DIR = ANALIZ_DIR / "gorseller"

DF_A_YOLU = DATAFRAMES_DIR / "df_a_kapsama_testli_v2.csv"
DF_B_YOLU = DATAFRAMES_DIR / "df_b_zengin_2024_bugun_v2.csv"

# Korelasyona sokulmayacak (tarih/kategorik) sutunlar - onceki uygunluk
# taramasinda (b)/(c) kategorisi olarak isaretlenmisti.
HARIC_TUTULAN = {"referans_ayi", "tufe_yayim_tarihi", "alim_gucu_ceyrek"}


def _korelasyon_ve_isi_haritasi(df: pd.DataFrame, ad: str, dosya_soneki: str):
    numerik_kolonlar = [
        c for c in df.columns
        if c not in HARIC_TUTULAN and pd.api.types.is_numeric_dtype(df[c])
    ]
    korelasyon = df[numerik_kolonlar].corr(method="pearson")

    csv_yolu = ANALIZ_DIR / f"korelasyon_matrisi_{dosya_soneki}.csv"
    korelasyon.to_csv(csv_yolu, encoding="utf-8-sig")

    n_kolon = len(numerik_kolonlar)
    fig_boyut = max(8, n_kolon * 0.55)
    fig, ax = plt.subplots(figsize=(fig_boyut, fig_boyut))
    im = ax.imshow(korelasyon.values, cmap="RdBu_r", vmin=-1, vmax=1)

    ax.set_xticks(range(n_kolon))
    ax.set_yticks(range(n_kolon))
    ax.set_xticklabels(numerik_kolonlar, rotation=90, fontsize=8)
    ax.set_yticklabels(numerik_kolonlar, fontsize=8)

    for i in range(n_kolon):
        for j in range(n_kolon):
            deger = korelasyon.values[i, j]
            renk = "white" if abs(deger) > 0.6 else "black"
            ax.text(j, i, f"{deger:.2f}", ha="center", va="center", color=renk, fontsize=6)

    ax.set_title(f"{ad} — Pearson Korelasyon Matrisi ({n_kolon} sayısal sütun, n={len(df)} satır)")
    fig.colorbar(im, ax=ax, shrink=0.8, label="Pearson r")
    fig.tight_layout()

    png_yolu = GORSEL_DIR / f"korelasyon_isi_haritasi_{dosya_soneki}.png"
    fig.savefig(png_yolu, dpi=150)
    plt.close(fig)

    return korelasyon, csv_yolu, png_yolu, numerik_kolonlar


def main():
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    df_a = pd.read_csv(DF_A_YOLU)
    df_b = pd.read_csv(DF_B_YOLU)

    kor_a, csv_a, png_a, kolon_a = _korelasyon_ve_isi_haritasi(df_a, "DF-A", "df_a")
    kor_b, csv_b, png_b, kolon_b = _korelasyon_ve_isi_haritasi(df_b, "DF-B", "df_b")

    print("=== GENISLETME 23 - DF-A/DF-B KORELASYON ANALIZI ===")
    print(f"\nDF-A: {len(df_a)} satir, {len(kolon_a)} sayisal sutun korelasyona sokuldu")
    print(f"  Sutunlar: {kolon_a}")
    print(f"  Cikti: {csv_a}")
    print(f"  Gorsel: {png_a}")

    print(f"\nDF-B: {len(df_b)} satir, {len(kolon_b)} sayisal sutun korelasyona sokuldu")
    print(f"  Sutunlar: {kolon_b}")
    print(f"  Cikti: {csv_b}")
    print(f"  Gorsel: {png_b}")

    # En yuksek mutlak korelasyonlu ciftleri (kendi-kendine haric) yazdir
    for ad, kor in [("DF-A", kor_a), ("DF-B", kor_b)]:
        print(f"\n--- {ad}: |r| > 0.8 olan ciftler (kendi-kendine haric) ---")
        kolonlar = kor.columns.tolist()
        ciftler = []
        for i, c1 in enumerate(kolonlar):
            for c2 in kolonlar[i + 1:]:
                r = kor.loc[c1, c2]
                if pd.notna(r) and abs(r) > 0.8:
                    ciftler.append((c1, c2, r))
        ciftler.sort(key=lambda x: -abs(x[2]))
        for c1, c2, r in ciftler:
            print(f"  {c1} <-> {c2}: r={r:.4f}")


if __name__ == "__main__":
    main()
