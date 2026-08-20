from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "birlesik_target_setleri" / "target_devir_orani_tum_featurelar.csv"
OUTPUT = Path(__file__).with_name("noter_otomobil_devir_adedi.png")

plt.rcParams["font.family"] = "DejaVu Sans"

df = pd.read_csv(DATA)
df["referans_ayi"] = pd.to_datetime(df["referans_ayi"])
df = df.sort_values("referans_ayi")
df["hareketli_ortalama_12ay"] = df["noter_devir_otomobil_adet"].rolling(12).mean()

fig, ax = plt.subplots(figsize=(16, 7.5), facecolor="white")

ax.plot(
    df["referans_ayi"],
    df["noter_devir_otomobil_adet"],
    color="#2F6B9A",
    linewidth=2,
    marker="o",
    markersize=3,
    label="Aylık noter otomobil devir adedi",
)
ax.plot(
    df["referans_ayi"],
    df["hareketli_ortalama_12ay"],
    color="#F28E2B",
    linewidth=3,
    label="12 aylık hareketli ortalama",
)

max_row = df.loc[df["noter_devir_otomobil_adet"].idxmax()]
min_row = df.loc[df["noter_devir_otomobil_adet"].idxmin()]

for row, label, offset in [
    (max_row, "En yüksek", (18, 18)),
    (min_row, "En düşük", (18, 20)),
]:
    ax.scatter(
        row["referans_ayi"],
        row["noter_devir_otomobil_adet"],
        s=70,
        color="#B33A3A",
        edgecolor="white",
        linewidth=1.2,
        zorder=5,
    )
    ax.annotate(
        f"{label}: {row['noter_devir_otomobil_adet']:,.0f}".replace(",", "."),
        (row["referans_ayi"], row["noter_devir_otomobil_adet"]),
        xytext=offset,
        textcoords="offset points",
        fontsize=10,
        color="#7F1D1D",
        arrowprops=dict(arrowstyle="-", color="#B33A3A", linewidth=1),
    )

ax.set_title("Aylık Noter Otomobil Devir Adedi", fontsize=20, fontweight="bold", pad=18)
ax.set_xlabel("Tarih", fontsize=12)
ax.set_ylabel("Devir adedi", fontsize=12)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.yaxis.set_major_formatter(lambda value, _: f"{value / 1000:,.0f} bin".replace(",", "."))
ax.grid(axis="both", alpha=0.2)
ax.set_axisbelow(True)
ax.legend(loc="upper left", frameon=False, ncol=2)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.text(
    0.5,
    0.015,
    "Dönem: Ocak 2018 – Haziran 2026 | Kaynak sütun: noter_devir_otomobil_adet",
    ha="center",
    fontsize=10,
    color="#555555",
)
fig.tight_layout(rect=[0.02, 0.05, 0.99, 0.98])
fig.savefig(OUTPUT, dpi=180, bbox_inches="tight")
plt.close(fig)

print(OUTPUT)
