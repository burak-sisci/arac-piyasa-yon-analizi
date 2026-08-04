"""
GENIŞLETME AŞAMA 32 — Faiz oranlarının noter_devir_toplam_adet (target)
üzerindeki etkisinin GECİKMELİ (lag) olabileceği hipotezini test eder.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla)

YÖNTEM:
- Kaynak tablo (DF-A, DF-B) once AYLIGA COLLAPSE edilir (takvim-genisletme
  pseudo-replikasyonundan kacinmak icin - onceki adimlarla tutarli).
- Her faiz sutunu (tasit_kredisi_faiz, politika_faizi) HAM SEVIYE olarak
  0,1,2,3,4,5,6 ay GECIKTIRILIR (shift): gecikme=N -> o ayin target'i,
  N ay ONCEKI faiz degeriyle eslestirilir.
- Her gecikme icin Pearson r hesaplanir (target HAM SEVIYE, onceki
  adimda proje sahibinin sectigi form).
- Sonuc DF-A ve DF-B icin AYRI AYRI, gorsel (cizgi grafik) olarak sunulur.

Girdi: data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
       data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
Cikti: data/processed/analiz/gorseller/faiz_gecikme_korelasyon_df_a.png
       data/processed/analiz/gorseller/faiz_gecikme_korelasyon_df_b.png
       data/processed/analiz/faiz_gecikme_korelasyon.csv
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

DOSYALAR = {
    "DF-A": DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
    "DF-B": DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
}

FAIZ_SUTUNLARI = ["tasit_kredisi_faiz", "politika_faizi"]
TARGET = "noter_devir_toplam_adet"
GECIKMELER = range(0, 7)  # 0..6 ay


def _aylik_collapse(df: pd.DataFrame, referans_ay_col: str, deger_kolonlari: list) -> pd.DataFrame:
    aylik = df[[referans_ay_col] + deger_kolonlari].dropna(subset=[referans_ay_col])
    aylik = aylik.drop_duplicates(subset=referans_ay_col).sort_values(referans_ay_col).reset_index(drop=True)
    return aylik


def main():
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    tum_sonuclar = []

    for df_adi, yol in DOSYALAR.items():
        print(f"\n=== {df_adi} ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])

        faiz_aylik = _aylik_collapse(df, "faiz_referans_ay", FAIZ_SUTUNLARI)
        target_aylik = _aylik_collapse(df, "noter_referans_ay", [TARGET])

        birlesik = faiz_aylik.merge(
            target_aylik, left_on="faiz_referans_ay", right_on="noter_referans_ay", how="inner"
        ).sort_values("faiz_referans_ay").reset_index(drop=True)

        fig, ax = plt.subplots(figsize=(8, 5))
        for kolon in FAIZ_SUTUNLARI:
            r_degerleri = []
            for gecikme in GECIKMELER:
                faiz_kaydirilmis = birlesik[kolon].shift(gecikme)
                gecerli = pd.DataFrame({"faiz": faiz_kaydirilmis, "target": birlesik[TARGET]}).dropna()
                r = gecerli["faiz"].corr(gecerli["target"], method="pearson")
                n = len(gecerli)
                r_degerleri.append(r)
                tum_sonuclar.append({"df": df_adi, "faiz_sutunu": kolon, "gecikme_ay": gecikme, "pearson_r": r, "n": n})
                print(f"  {kolon} | gecikme={gecikme} ay | Pearson r={r:.4f} (n={n})")
            ax.plot(list(GECIKMELER), r_degerleri, marker="o", label=kolon)

        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_xlabel("Gecikme (ay) - faiz kac ay ONCEsinden aliniyor")
        ax.set_ylabel("Pearson r (faiz vs noter_devir_toplam_adet)")
        ax.set_title(f"{df_adi} — Faiz Gecikme (Lag) Korelasyonu")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        cikti_png = GORSEL_DIR / f"faiz_gecikme_korelasyon_{df_adi.lower().replace('-', '_')}.png"
        fig.savefig(cikti_png, dpi=150)
        plt.close(fig)
        print(f"  Gorsel: {cikti_png}")

    sonuc_df = pd.DataFrame(tum_sonuclar)
    cikti_csv = ANALIZ_DIR / "faiz_gecikme_korelasyon.csv"
    sonuc_df.to_csv(cikti_csv, index=False, encoding="utf-8-sig")
    print(f"\nCikti (tablo): {cikti_csv}")


if __name__ == "__main__":
    main()
