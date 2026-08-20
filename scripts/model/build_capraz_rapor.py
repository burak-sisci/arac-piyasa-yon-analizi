# -*- coding: utf-8 -*-
"""Capraz-feature target adaylari icin gorsel HTML raporu, metrik tablosu PNG'lerini
base64 olarak gomerek uretir. Bu script rapor metnini disaridan bir sablona yerlestirir."""

from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = ROOT / "outputs" / "hiz_target_backtest"
TEMPLATE_PATH = Path(__file__).with_name("capraz_rapor_template.html")

TARGETS = [
    "target_capraz_ikinciel_yeniarac_satis_orani",
    "target_capraz_kuyruk_stok_seviyesi",
]


def b64_img(target: str) -> str:
    p = OUT_ROOT / target / "metrik_tablosu.png"
    return base64.b64encode(p.read_bytes()).decode("ascii")


def main(output_path: str):
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    for t in TARGETS:
        placeholder = f"__B64_{t}__"
        template = template.replace(placeholder, b64_img(t))
    Path(output_path).write_text(template, encoding="utf-8")
    print("Yazildi:", output_path)


if __name__ == "__main__":
    import sys
    main(sys.argv[1])
