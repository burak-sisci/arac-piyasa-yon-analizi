from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesPredictor


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "outputs" / "autogluon" / "ip7_devir_orani" / "ag_model"
OUTPUT_CSV = Path(__file__).with_name("recursive_tabular_native_feature_importance.csv")
OUTPUT_PNG = Path(__file__).with_name("recursive_tabular_feature_importance.png")

MODEL = "RecursiveTabular"

predictor = TimeSeriesPredictor.load(MODEL_DIR)
outer_model = predictor._trainer.load_model(MODEL)

# MultiWindow modelinin en güncel alt modeli W4'tür ve nihai tahminlerde kullanılır.
child_model = outer_model.get_child_model(4)
child_model = child_model.load(path=child_model.path)
tabular_model = child_model.get_tabular_model().model.model

native = pd.DataFrame(
    {
        "feature": tabular_model.feature_name(),
        "gain": tabular_model.feature_importance(importance_type="gain"),
        "split": tabular_model.feature_importance(importance_type="split"),
    }
)
total_gain = native["gain"].sum()
native["importance_pct"] = np.where(total_gain > 0, 100 * native["gain"] / total_gain, 0.0)
native.sort_values(["importance_pct", "feature"], ascending=[False, True]).to_csv(
    OUTPUT_CSV, index=False, encoding="utf-8-sig"
)

external_features = [
    "noter_devir_otomobil_adet_lag1",
    "eurtry_ortalama_lag1",
    "tufe_aylik_degisim_lag1",
    "tasit_kredisi_faiz_lag1",
    "indicata_ilan_yayinlanan_adet_lag1",
    "indicata_satisa_donen_adet_lag1",
    "indicata_satis_ilan_orani_pct_lag1",
    "indicata_perakende_fiyat_aylik_pct_lag1",
    "arabam_ortalama_ilan_fiyati_tl_lag1",
    "betam_ortalama_ilan_fiyati_tl_lag1",
    "betam_dom_gun_lag1",
]

tr_names = {
    "noter_devir_otomobil_adet_lag1": "Noter otomobil devir adedi (t−1)",
    "eurtry_ortalama_lag1": "EUR/TRY ortalaması (t−1)",
    "tufe_aylik_degisim_lag1": "Aylık TÜFE değişimi (t−1)",
    "tasit_kredisi_faiz_lag1": "Taşıt kredisi faizi (t−1)",
    "indicata_ilan_yayinlanan_adet_lag1": "Indicata yayımlanan ilan (t−1)",
    "indicata_satisa_donen_adet_lag1": "Indicata satışa dönen ilan (t−1)",
    "indicata_satis_ilan_orani_pct_lag1": "Indicata satış/ilan oranı (t−1)",
    "indicata_perakende_fiyat_aylik_pct_lag1": "Indicata aylık fiyat değişimi (t−1)",
    "arabam_ortalama_ilan_fiyati_tl_lag1": "arabam.com ortalama ilan fiyatı (t−1)",
    "betam_ortalama_ilan_fiyati_tl_lag1": "BETAM ortalama ilan fiyatı (t−1)",
    "betam_dom_gun_lag1": "BETAM ilanda kalma süresi (t−1)",
}

# Ham ve ölçeklenmiş ikiz sütunların gain değerlerini aynı iş değişkeninde birleştir.
external_rows = []
for feature in external_features:
    combined_gain = native.loc[
        native["feature"].isin([feature, f"__scaled_{feature}"]), "gain"
    ].sum()
    combined_pct = 100 * combined_gain / total_gain if total_gain > 0 else 0.0
    external_rows.append((tr_names[feature], combined_pct))

nonzero = native.loc[native["importance_pct"].gt(0)].copy()
display_names = {
    "lag1": "Model içi target gecikmesi: lag 1",
    "lag11": "Model içi target gecikmesi: lag 11",
}
nonzero["gosterim"] = nonzero["feature"].map(display_names).fillna(nonzero["feature"])
nonzero = nonzero.sort_values("importance_pct", ascending=True)

plt.rcParams["font.family"] = "DejaVu Sans"
fig = plt.figure(figsize=(17, 9.5), facecolor="#F7F8FA")
grid = fig.add_gridspec(
    1,
    2,
    width_ratios=[1.08, 1.35],
    wspace=0.18,
    left=0.06,
    right=0.98,
    top=0.82,
    bottom=0.14,
)
ax = fig.add_subplot(grid[0, 0])
ax_table = fig.add_subplot(grid[0, 1])

fig.suptitle(
    "RecursiveTabular Özellik Önem Değerleri",
    fontsize=23,
    fontweight="bold",
    color="#172B4D",
    y=0.96,
)
fig.text(
    0.5,
    0.915,
    "Son model • LightGBM gain önemi • 6 ay validasyon / 6 ay test düzeni",
    ha="center",
    fontsize=12,
    color="#5E6C84",
)

colors = ["#F28E2B" if name == "lag11" else "#2F6B9A" for name in nonzero["feature"]]
bars = ax.barh(nonzero["gosterim"], nonzero["importance_pct"], color=colors, height=0.5)
ax.set_title("Modelin kullandığı sinyaller", fontsize=15, fontweight="bold", color="#172B4D", pad=16)
ax.set_xlabel("Toplam gain içindeki pay (%)", fontsize=11)
ax.set_xlim(0, max(65, nonzero["importance_pct"].max() * 1.18))
ax.grid(axis="x", alpha=0.2)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0, labelsize=11)
for bar, value in zip(bars, nonzero["importance_pct"]):
    ax.text(
        bar.get_width() + 1,
        bar.get_y() + bar.get_height() / 2,
        f"%{value:.2f}",
        va="center",
        fontsize=13,
        fontweight="bold",
        color="#172B4D",
    )

ax.text(
    0,
    -0.19,
    "Lag adları, modelin 12 dönemlik fark dönüşümü uygulanmış iç target serisine aittir.",
    transform=ax.transAxes,
    fontsize=10.5,
    color="#5E6C84",
)

ax_table.axis("off")
ax_table.set_title(
    "Modele verilen dış feature'lar",
    fontsize=15,
    fontweight="bold",
    color="#172B4D",
    pad=16,
)

table_data = [[name, f"%{value:.3f}"] for name, value in external_rows]
table = ax_table.table(
    cellText=table_data,
    colLabels=["Feature", "Gain payı"],
    cellLoc="left",
    colWidths=[0.78, 0.22],
    bbox=[0.0, 0.12, 1.0, 0.76],
)
table.auto_set_font_size(False)
table.set_fontsize(10.5)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#D8DEE9")
    cell.set_linewidth(0.8)
    if row == 0:
        cell.set_facecolor("#234E70")
        cell.get_text().set_color("white")
        cell.get_text().set_fontweight("bold")
        cell.get_text().set_ha("center" if col == 1 else "left")
    else:
        cell.set_facecolor("#FFFFFF" if row % 2 == 0 else "#EEF3F8")
        cell.get_text().set_color("#172B4D")
        if col == 1:
            cell.get_text().set_ha("right")

ax_table.text(
    0.0,
    0.055,
    "Bu modelde dış feature'ların hiçbiri ağaç bölünmelerinde kullanılmadı.",
    transform=ax_table.transAxes,
    fontsize=11,
    fontweight="bold",
    color="#B23A48",
)
ax_table.text(
    0.0,
    0.008,
    "AutoGluon permütasyon testi de altı test ayının tamamında bu feature'lar için 0 önem verdi.",
    transform=ax_table.transAxes,
    fontsize=9.8,
    color="#5E6C84",
)

fig.savefig(OUTPUT_PNG, dpi=185, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close(fig)

print(OUTPUT_PNG)
print(nonzero[["feature", "gain", "importance_pct"]].to_string(index=False))
