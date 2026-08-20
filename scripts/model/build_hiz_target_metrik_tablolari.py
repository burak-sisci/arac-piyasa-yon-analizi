# -*- coding: utf-8 -*-
"""3 satis-hizi hedefi icin, projenin mevcut "basari metrikleri tablosu" gorsel stiline
uygun, gercek metrikler.json degerlerinden uretilen PNG tablolari.

Kullanim:
    .venv-ag\\Scripts\\python.exe scripts\\build_hiz_target_metrik_tablolari.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = PROJECT_ROOT / "outputs" / "hiz_target_backtest"

plt.rcParams["font.family"] = "DejaVu Sans"

TARGETS = [
    {
        "target": "target_betam_dom_gun",
        "baslik": "BETAM Days on Market — İlanda Kalış Süresi",
        "birim": "gün",
        "birim_carpan": 1.0,
    },
    {
        "target": "target_quickfinans_dom_gun",
        "baslik": "Quick Finans / SmartIQ İkinci El Stokta Kalma Süresi",
        "birim": "gün",
        "birim_carpan": 1.0,
    },
    {
        "target": "target_capraz_ikinciel_yeniarac_satis_orani",
        "baslik": "Çapraz: İkinci El / Yeni Araç Satış Oranı",
        "birim": "oran",
        "birim_carpan": 1.0,
    },
    {
        "target": "target_capraz_kuyruk_stok_seviyesi",
        "baslik": "Çapraz: Kuyruk Teorisi (Little's Law) Tahmini Stok Seviyesi",
        "birim": "adet",
        "birim_carpan": 1.0,
    },
]


def build_table(cfg: dict) -> Path:
    target = cfg["target"]
    out_dir = OUT_ROOT / target
    data = json.loads((out_dir / "metrikler.json").read_text(encoding="utf-8"))

    model = data["model_metrikleri"]
    baseline = data["baseline_metrikleri_gecen_yil_ayni_ay"]
    n = model["n_test_ay"]
    carpan = cfg["birim_carpan"]
    birim = cfg["birim"]

    mae_skill = 100 * (1 - model["mae"] / baseline["mae"]) if baseline["mae"] else float("nan")
    rmse_skill = 100 * (1 - model["rmse"] / baseline["rmse"]) if baseline["rmse"] else float("nan")
    yon_delta_pp = (model["yon_dogrulugu"] - baseline["yon_dogrulugu"]) * 100

    rows = [
        [
            "AutoGluon (h=1)",
            f"%{model['yon_dogrulugu']*100:.1f}",
            f"{model['mae']*carpan:.2f}",
            f"{model['rmse']*carpan:.2f}",
            f"{model['mase']:.3f}",
            f"%{model['smape_pct']:.1f}",
            f"{model['bias']*carpan:+.2f}",
        ],
        [
            "Geçen yılın aynı ayı",
            f"%{baseline['yon_dogrulugu']*100:.1f}",
            f"{baseline['mae']*carpan:.2f}",
            f"{baseline['rmse']*carpan:.2f}",
            f"{baseline['mase']:.3f}",
            f"%{baseline['smape_pct']:.1f}",
            f"{baseline['bias']*carpan:+.2f}",
        ],
    ]
    headers = [
        "Yöntem",
        "Yön Doğruluğu",
        f"MAE\n({birim})",
        f"RMSE\n({birim})",
        "MASE",
        "sMAPE",
        f"Bias\n({birim})",
    ]

    low_n_warning = n <= 2

    fig = plt.figure(figsize=(15, 7.4 if not low_n_warning else 8.1), facecolor="#F7F8FA")
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.86])
    ax.axis("off")

    fig.text(0.5, 0.955, cfg["baslik"], ha="center", va="center", fontsize=21, fontweight="bold", color="#172B4D")
    fig.text(
        0.5, 0.905,
        f"{target}  |  Rolling-origin backtest: {n} ay  |  Tarih aralığı: {data['tarih_araligi']}",
        ha="center", fontsize=11.5, color="#5E6C84",
    )

    if low_n_warning:
        fig.text(
            0.5, 0.865,
            f"⚠ n={n} — İSTATİSTİKSEL OLARAK ANLAMSIZ ÖRNEKLEM. Bu sayılar bir eğilim değil, "
            f"{n} gözlemin anekdotal sonucudur.",
            ha="center", fontsize=12, fontweight="bold", color="#B23A48",
        )
        table_top = 0.42
        table_h = 0.32
    else:
        table_top = 0.46
        table_h = 0.34

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        colWidths=[0.20, 0.13, 0.13, 0.13, 0.11, 0.12, 0.13],
        cellLoc="center",
        bbox=[0.0, table_top, 1.0, table_h],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    model_better = {
        "yon": model["yon_dogrulugu"] >= baseline["yon_dogrulugu"],
        "mae": model["mae"] <= baseline["mae"],
        "rmse": model["rmse"] <= baseline["rmse"],
        "mase": model["mase"] <= baseline["mase"],
        "smape": model["smape_pct"] <= baseline["smape_pct"],
        "bias": abs(model["bias"]) <= abs(baseline["bias"]),
    }
    col_keys = [None, "yon", "mae", "rmse", "mase", "smape", "bias"]

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#D8DEE9")
        cell.set_linewidth(1.0)
        if row == 0:
            cell.set_facecolor("#234E70")
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
            cell.set_height(0.16)
            continue
        key = col_keys[col] if col < len(col_keys) else None
        is_model_row = row == 1
        better = model_better.get(key) if key else None
        if key is None:
            cell.set_facecolor("#FFF3E0" if is_model_row else "#E8F4EA")
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_ha("left")
            continue
        if is_model_row:
            good = better
        else:
            good = (better is False)
        cell.set_facecolor("#E8F4EA" if good else "#FDEBEC")
        cell.get_text().set_color("#1B6B36" if good else "#B23A48")
        cell.get_text().set_fontweight("bold")

    panel_y = table_top - 0.14
    ax.text(0.0, panel_y, "MAE beceri skoru", fontsize=12, fontweight="bold", color="#172B4D", transform=ax.transAxes)
    ax.text(
        0.0, panel_y - 0.075, f"{mae_skill:+.1f}%", fontsize=24, fontweight="bold",
        color="#B23A48" if mae_skill < 0 else "#1B6B36", transform=ax.transAxes,
    )
    ax.text(
        0.17, panel_y - 0.065,
        f"Model, geçen yılın aynı ayı yöntemine göre\nortalama mutlak hatayı "
        f"%{abs(mae_skill):.1f} {'azalttı' if mae_skill > 0 else 'artırdı'}.",
        fontsize=10.5, color="#5E6C84", va="center", transform=ax.transAxes,
    )

    ax.text(0.5, panel_y, "Yön doğruluğu farkı", fontsize=12, fontweight="bold", color="#172B4D", transform=ax.transAxes)
    ax.text(
        0.5, panel_y - 0.075, f"{yon_delta_pp:+.1f}pp", fontsize=24, fontweight="bold",
        color="#B23A48" if yon_delta_pp < 0 else "#1B6B36", transform=ax.transAxes,
    )
    yon_yorum = (
        "Model, baseline'dan daha sık doğru yön tahmin etti."
        if yon_delta_pp > 0
        else ("Model ile baseline aynı oranda doğru yön tuttu." if yon_delta_pp == 0
              else "Model, baseline'ın GERİSİNDE kaldı — yön tahmininde baseline daha güvenilir.")
    )
    ax.text(0.67, panel_y - 0.065, yon_yorum, fontsize=10.5, color="#5E6C84", va="center", transform=ax.transAxes, wrap=True)

    footer_y = 0.075 if not low_n_warning else 0.06
    ax.text(
        0.0, footer_y,
        "Yorum: Hata metriklerinde düşük değer, yön doğruluğunda yüksek değer daha iyidir. "
        "MASE < 1, yöntemin 12-aylık mevsimsel farktan daha iyi olduğunu gösterir. sMAPE, "
        "ölçekten bağımsız yüzdesel hata (hedefler arası karşılaştırılabilir). Bias, "
        "ortalama(tahmin − gerçek); |0|'a yakın olması iyidir.",
        fontsize=10, color="#5E6C84", transform=ax.transAxes,
    )
    ax.text(
        0.0, footer_y - 0.045,
        "Yeşil = o metrikte daha iyi taraf. Beceri skoru = 100 × (1 − model hatası / baseline hatası).",
        fontsize=10, color="#5E6C84", transform=ax.transAxes,
    )

    out_path = out_dir / "metrik_tablosu.png"
    fig.savefig(out_path, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_path


def main() -> None:
    paths = [build_table(cfg) for cfg in TARGETS]
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
