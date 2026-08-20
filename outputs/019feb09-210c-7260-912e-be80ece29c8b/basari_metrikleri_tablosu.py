from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import json


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "outputs" / "autogluon" / "ip7_devir_orani" / "test_siralama_tum_modeller.csv"
OUTPUT = Path(__file__).with_name("model_basari_metrikleri.png")

plt.rcParams["font.family"] = "DejaVu Sans"

results = pd.read_csv(RESULTS)
selected_name = (RESULTS.parent / "secili_model.txt").read_text(encoding="utf-8").strip()
splits = json.loads((RESULTS.parent / "splitler.json").read_text(encoding="utf-8"))
main = results.loc[results["model"].eq(selected_name)].iloc[0]
baseline = results.loc[results["model"].eq("MevsimselNaive12")].iloc[0]

mae_skill = 100 * (1 - main["MAE"] / baseline["MAE"])
rmse_skill = 100 * (1 - main["RMSE"] / baseline["RMSE"])

rows = [
    [
        f"Ana model ({selected_name})",
        f"{main['MAE'] * 100:.3f}",
        f"{main['RMSE'] * 100:.3f}",
        f"{main['MASE']:.3f}",
        f"%{main['yon_dogrulugu_yuzde']:.1f}",
        f"{main['bias'] * 100:+.3f}",
    ],
    [
        "Geçen yılın aynı ayı",
        f"{baseline['MAE'] * 100:.3f}",
        f"{baseline['RMSE'] * 100:.3f}",
        f"{baseline['MASE']:.3f}",
        f"%{baseline['yon_dogrulugu_yuzde']:.1f}",
        f"{baseline['bias'] * 100:+.3f}",
    ],
]

headers = [
    "Yöntem",
    "MAE\n(yüzde puanı)",
    "RMSE\n(yüzde puanı)",
    "MASE",
    "Yön doğruluğu",
    "Sapma / Bias\n(yüzde puanı)",
]

fig = plt.figure(figsize=(15, 7.6), facecolor="#F7F8FA")
ax = fig.add_axes([0.04, 0.08, 0.92, 0.84])
ax.axis("off")

fig.text(
    0.5,
    0.92,
    "Model Başarı Metrikleri",
    ha="center",
    va="center",
    fontsize=23,
    fontweight="bold",
    color="#172B4D",
)
fig.text(
    0.5,
    0.865,
    f"Test dönemi: {splits['test_start']} – {splits['test_end']} | {int(main['gozlem'])} aylık gerçekleşme",
    ha="center",
    fontsize=12,
    color="#5E6C84",
)

table = ax.table(
    cellText=rows,
    colLabels=headers,
    colWidths=[0.25, 0.15, 0.15, 0.11, 0.17, 0.17],
    cellLoc="center",
    bbox=[0.0, 0.43, 1.0, 0.34],
)
table.auto_set_font_size(False)
table.set_fontsize(12)

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#D8DEE9")
    cell.set_linewidth(1.0)
    if row == 0:
        cell.set_facecolor("#234E70")
        cell.get_text().set_color("white")
        cell.get_text().set_fontweight("bold")
        cell.set_height(0.16)
    elif row == 1:
        cell.set_facecolor("#FFF3E0")
        cell.get_text().set_color("#172B4D")
        if col in (1, 2, 3):
            cell.get_text().set_color("#B23A48")
            cell.get_text().set_fontweight("bold")
    else:
        cell.set_facecolor("#E8F4EA")
        cell.get_text().set_color("#172B4D")
        if col in (1, 2, 3):
            cell.get_text().set_color("#1B6B36")
            cell.get_text().set_fontweight("bold")
    if col == 0 and row > 0:
        cell.get_text().set_ha("left")
        cell.get_text().set_fontweight("bold")

ax.text(
    0.02,
    0.31,
    "MAE beceri skoru",
    fontsize=12,
    fontweight="bold",
    color="#172B4D",
    transform=ax.transAxes,
)
ax.text(
    0.02,
    0.235,
    f"{mae_skill:+.2f}%",
    fontsize=25,
    fontweight="bold",
    color="#B23A48" if mae_skill < 0 else "#1B6B36",
    transform=ax.transAxes,
)
ax.text(
    0.19,
    0.245,
    f"Ana model, geçen yılın aynı ayı yöntemine göre\n"
    f"ortalama mutlak hatayı %{abs(mae_skill):.2f} {'azalttı' if mae_skill > 0 else 'artırdı'}.",
    fontsize=12,
    color="#5E6C84",
    va="center",
    transform=ax.transAxes,
)

ax.text(
    0.62,
    0.31,
    "RMSE beceri skoru",
    fontsize=12,
    fontweight="bold",
    color="#172B4D",
    transform=ax.transAxes,
)
ax.text(
    0.62,
    0.235,
    f"{rmse_skill:+.2f}%",
    fontsize=25,
    fontweight="bold",
    color="#B23A48" if rmse_skill < 0 else "#1B6B36",
    transform=ax.transAxes,
)

ax.text(
    0.0,
    0.08,
    "Yorum: Hata metriklerinde düşük değer, yön doğruluğunda yüksek değer daha iyidir. "
    "MASE < 1, yöntemin bir-adım naif referanstan daha iyi olduğunu gösterir.",
    fontsize=10.5,
    color="#5E6C84",
    transform=ax.transAxes,
)
ax.text(
    0.0,
    0.02,
    "Beceri skoru = 100 × (1 − ana model hatası / geçen-yıl hatası). Negatif değer, geçen-yıl yönteminin üstün olduğunu gösterir.",
    fontsize=10.5,
    color="#5E6C84",
    transform=ax.transAxes,
)

fig.savefig(OUTPUT, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close(fig)
print(OUTPUT)
