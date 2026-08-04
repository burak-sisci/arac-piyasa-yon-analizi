"""
GENIŞLETME AŞAMA 41 — 4 final veri setinin (DF-A, DF-B, DF-A-log,
DF-B-log) korelasyon matrisi ısı haritalarını üretir.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla)

Standart Pearson korelasyon matrisi (df[sayisal_kolonlar].corr()),
target dahil TÜM final sütunlar üzerinden - 23 nolu görevdeki AYNI
görselleştirme yöntemi.

Girdi: data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
       data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
       data/processed/dataframes/df_a_log_degisim_2015_bugun.csv
       data/processed/dataframes/df_b_log_degisim_2024_bugun.csv
Cikti: data/processed/analiz/gorseller/final_korelasyon_<set>.png
       data/processed/analiz/final_korelasyon_<set>.csv
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"
GORSEL_DIR = ANALIZ_DIR / "gorseller"

SETLER = {
    "df_a": DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
    "df_b": DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
    "df_a_log": DF_DIR / "df_a_log_degisim_2015_bugun.csv",
    "df_b_log": DF_DIR / "df_b_log_degisim_2024_bugun.csv",
}


def main():
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    for set_adi, yol in SETLER.items():
        df = pd.read_csv(yol)
        sayisal = [c for c in df.columns if c != "tarih" and pd.api.types.is_numeric_dtype(df[c])]
        korr = df[sayisal].corr(method="pearson")

        korr.to_csv(ANALIZ_DIR / f"final_korelasyon_{set_adi}.csv", encoding="utf-8-sig")

        n_kolon = len(sayisal)
        boyut = max(6, n_kolon * 0.9)
        fig, ax = plt.subplots(figsize=(boyut, boyut * 0.85))
        im = ax.imshow(korr.values, cmap="RdBu_r", vmin=-1, vmax=1)

        ax.set_xticks(range(n_kolon))
        ax.set_yticks(range(n_kolon))
        ax.set_xticklabels(sayisal, rotation=90, fontsize=8)
        ax.set_yticklabels(sayisal, fontsize=8)

        for i in range(n_kolon):
            for j in range(n_kolon):
                deger = korr.values[i, j]
                renk = "white" if abs(deger) > 0.6 else "black"
                ax.text(j, i, f"{deger:.2f}", ha="center", va="center", color=renk, fontsize=7)

        ax.set_title(f"{set_adi.upper()} — Final Sütunlar Pearson Korelasyon Matrisi (n_sütun={n_kolon}, satır={df.shape[0]})")
        fig.colorbar(im, ax=ax, label="Pearson r")
        fig.tight_layout()

        cikti_png = GORSEL_DIR / f"final_korelasyon_{set_adi}.png"
        fig.savefig(cikti_png, dpi=150)
        plt.close(fig)
        print(f"Yazildi: {cikti_png}")


if __name__ == "__main__":
    main()
