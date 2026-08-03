"""
GENIŞLETME AŞAMA 24 — Noter devri (araç el değiştirme) sütunlarının diğer
tüm özelliklerle korelasyonu, DF-A ve DF-B için ayrı ayrı.

Bu script SADECE Pearson korelasyonu hesaplar ve görselleştirir - hedef/
model değiştirmez, yorum/karar üretmez (PM raporu ayrıca istenecek).

Hedef sütunlar: noter_devir_toplam_adet, noter_devir_otomobil_adet.
"Diğer özellikler": HARIC_TUTULAN (tarih/kategorik) hariç, bu iki sütunun
dışındaki tüm sayısal sütunlar.

NOT (metodolojik): korelasyon, genisletme_23 ile tutarlı olacak şekilde HAM
SEVİYE (level) değerleri üzerinden hesaplandı - trend taşıyan seviye
serileri arasında SAHTE (spurious) korelasyon riski PM raporunda
detaylandırılacak.

Girdi:
  - data/processed/dataframes/df_a_kapsama_testli_v2.csv
  - data/processed/dataframes/df_b_zengin_2024_bugun_v2.csv
Çıktı:
  - data/processed/analiz/noter_devir_korelasyon_df_a.csv
  - data/processed/analiz/noter_devir_korelasyon_df_b.csv
  - data/processed/analiz/gorseller/noter_devir_korelasyon_df_a.png
  - data/processed/analiz/gorseller/noter_devir_korelasyon_df_b.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DATAFRAMES_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"
GORSEL_DIR = ANALIZ_DIR / "gorseller"

DF_A_YOLU = DATAFRAMES_DIR / "df_a_kapsama_testli_v2.csv"
DF_B_YOLU = DATAFRAMES_DIR / "df_b_zengin_2024_bugun_v2.csv"

HARIC_TUTULAN = {"referans_ayi", "tufe_yayim_tarihi", "alim_gucu_ceyrek"}
NOTER_SUTUNLARI = ["noter_devir_toplam_adet", "noter_devir_otomobil_adet"]


def _noter_korelasyon_ve_gorsel(df: pd.DataFrame, ad: str, dosya_soneki: str):
    numerik_kolonlar = [
        c for c in df.columns
        if c not in HARIC_TUTULAN and pd.api.types.is_numeric_dtype(df[c])
    ]
    diger_kolonlar = [c for c in numerik_kolonlar if c not in NOTER_SUTUNLARI]

    satirlar = []
    for hedef in NOTER_SUTUNLARI:
        for diger in diger_kolonlar:
            ortak = df[[hedef, diger]].dropna()
            n = len(ortak)
            r = ortak[hedef].corr(ortak[diger]) if n >= 3 else None
            satirlar.append({"noter_sutunu": hedef, "diger_ozellik": diger,
                              "pearson_r": round(r, 4) if r is not None else None,
                              "n": n})
    sonuc = pd.DataFrame(satirlar)
    csv_yolu = ANALIZ_DIR / f"noter_devir_korelasyon_{dosya_soneki}.csv"
    sonuc.to_csv(csv_yolu, index=False, encoding="utf-8-sig")

    # --- gorsel: iki noter sutunu icin yan yana yatay bar chart, |r|'e gore siralanmis ---
    toplam_pivot = sonuc[sonuc["noter_sutunu"] == "noter_devir_toplam_adet"].set_index("diger_ozellik")["pearson_r"]
    otomobil_pivot = sonuc[sonuc["noter_sutunu"] == "noter_devir_otomobil_adet"].set_index("diger_ozellik")["pearson_r"]
    sira = toplam_pivot.abs().sort_values(ascending=True).index

    fig_yukseklik = max(6, len(sira) * 0.4)
    fig, ax = plt.subplots(figsize=(9, fig_yukseklik))
    y = range(len(sira))
    bar_genislik = 0.38
    ax.barh([p - bar_genislik / 2 for p in y], toplam_pivot.loc[sira].values,
            height=bar_genislik, color="#2b6cb0", label="noter_devir_toplam_adet")
    ax.barh([p + bar_genislik / 2 for p in y], otomobil_pivot.loc[sira].values,
            height=bar_genislik, color="#dd6b20", label="noter_devir_otomobil_adet")
    ax.set_yticks(list(y))
    ax.set_yticklabels(sira, fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Pearson r")
    ax.set_title(f"{ad} — Noter Devri Sütunlarının Diğer Özelliklerle Korelasyonu (n={len(df)})")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xlim(-1, 1)
    fig.tight_layout()

    png_yolu = GORSEL_DIR / f"noter_devir_korelasyon_{dosya_soneki}.png"
    fig.savefig(png_yolu, dpi=150)
    plt.close(fig)

    return sonuc, csv_yolu, png_yolu


def main():
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    df_a = pd.read_csv(DF_A_YOLU)
    df_b = pd.read_csv(DF_B_YOLU)

    sonuc_a, csv_a, png_a = _noter_korelasyon_ve_gorsel(df_a, "DF-A", "df_a")
    sonuc_b, csv_b, png_b = _noter_korelasyon_ve_gorsel(df_b, "DF-B", "df_b")

    print("=== GENISLETME 24 - NOTER DEVRI KORELASYON ANALIZI ===")
    for ad, sonuc, csv_yolu, png_yolu, df in [("DF-A", sonuc_a, csv_a, png_a, df_a), ("DF-B", sonuc_b, csv_b, png_b, df_b)]:
        print(f"\n--- {ad} ({len(df)} satir) ---")
        print(f"Cikti: {csv_yolu}")
        print(f"Gorsel: {png_yolu}")
        for hedef in NOTER_SUTUNLARI:
            alt = sonuc[sonuc["noter_sutunu"] == hedef].copy()
            alt["abs_r"] = alt["pearson_r"].abs()
            alt = alt.sort_values("abs_r", ascending=False)
            print(f"\n  {hedef} - en yuksek |r| siraliyla:")
            for _, satir in alt.iterrows():
                print(f"    {satir['diger_ozellik']}: r={satir['pearson_r']} (n={satir['n']})")


if __name__ == "__main__":
    main()
