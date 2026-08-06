"""Model 08: kilitlenmemis validation'da aylik-nowcast baseline gecidi.

Test bolumune bakmaz, model egitmez ve performans terfisi yapmaz.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import haftalik_aylik_nowcast as hn  # noqa: E402
import nowcast_baseline as nb  # noqa: E402


def main() -> None:
    snapshot_yolu = MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv"
    snapshot = pd.read_csv(snapshot_yolu)
    aylik = snapshot.drop_duplicates("hedef_ay").copy()
    aylik["hedef_ay"] = pd.PeriodIndex(aylik["hedef_ay"], freq="M")
    etiketler = aylik.set_index("hedef_ay")["etiket"].sort_index()

    split = hn.nowcast_uc_parcali_split_olustur(
        "2019-01", "2024-02",
        "2024-05", "2025-04",
        "2025-07", "2026-06",
        embargo_ay_sayisi=2,
    )
    # Pusula karari: test henuz kilitli degil ve Model 08 tarafindan acilmaz.
    sonuc = nb.baseline_degerlendir(etiketler, split["train"], split["validation"])
    sonuc["split_durumu"] = {
        "train": [str(split["train"][0]), str(split["train"][-1]), len(split["train"])],
        "validation": [str(split["validation"][0]), str(split["validation"][-1]), len(split["validation"])],
        "embargo1": [str(x) for x in split["embargo1"]],
        "test": "ACILMADI_KILITLI_DEGIL",
    }
    sonuc["hafta_sirasi_kapsami"] = nb.snapshot_sirasi_kapsami(
        snapshot, split["validation"]
    )
    sonuc["haftalik_bilgi_kazanimi_durumu"] = (
        "Baseline'lar ay icinde sabittir; hafta-egirisi ancak as-of feature kullanan "
        "dusuk-kapasiteli adaylarla Model 09'da olculebilir."
    )
    sonuc["uyari"] = (
        "Yalniz 12 validation ayi vardir; metrikler yuksek belirsizlik tasir ve test sonucu degildir."
    )
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    cikti = MODEL_DIR / "model_08_nowcast_baseline_validation.json"
    cikti.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
