"""
MODEL 05 — Baseline modellerin FEATURE IMPORTANCE (ozellik onemi) analizi.

Yontem: PERMUTASYON onemi - her ozellik sirayla rastgele karistirilir ve
modelin performansindaki (MASE) DUSUS olculur. Yuksek skor = o ozellik
model icin onemli. NEGATIF skor = ozellik modele ZARAR veriyor olabilir
(o ozellik cikarilsa model daha iyi calisirdi).

Modeller YENIDEN EGITILMEZ - baseline (high_quality, m=30) kayitli
modelleri yuklenir, WeightedEnsemble uzerinden hesaplanir.

Girdi: data/processed/model/autogluon_model_0{1,2}_baseline_m30/
Cikti: data/processed/model/feature_importance_df_{a,b}.csv
       data/processed/model/gorseller/feature_importance_*.png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
GORSEL_DIR = MODEL_DIR / "gorseller"

TARGET = "noter_devir_otomobil_adet"
MODEL_ADI = "WeightedEnsemble"
NUM_ITERATIONS = 10  # her ozellik icin kac kez karistirilacak (guven araligi icin)

SETLER = {
    "DF-A": dict(
        kaynak_csv=DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
        model_yolu=MODEL_DIR / "autogluon_model_01_baseline_m30",
        baslangic="2018-01-01", bitis="2026-06-30",
        covariate_sutunlari=["usdtry_orta", "tufe_aylik_degisim", "tufe_yillik_degisim",
                              "odmd_otomobil_adet", "tuketici_guven_endeksi", "tasit_kredisi_faiz_lag12ay"],
    ),
    "DF-B": dict(
        kaynak_csv=DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
        model_yolu=MODEL_DIR / "autogluon_model_02_baseline_m30",
        baslangic="2024-01-01", bitis="2026-06-30",
        covariate_sutunlari=["tufe_aylik_degisim", "tufe_yillik_degisim", "enag_aylik_degisim",
                              "odmd_hta_adet", "osd_binek_adet", "otomobil_satinalma_ihtimali_endeksi",
                              "proxy_dom_gun", "proxy_satis_orani_pct", "proxy_nominal_yillik_pct",
                              "proxy_talep_aylik_pct", "proxy_reel_aylik_log_degisim",
                              "tasit_kredisi_faiz_lag4ay", "politika_faizi_lag5ay"],
    ),
}


def main():
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    for set_adi, ayar in SETLER.items():
        print(f"\n=== {set_adi} ===")
        df = pd.read_csv(ayar["kaynak_csv"], parse_dates=["tarih"])
        df = df[(df["tarih"] >= ayar["baslangic"]) & (df["tarih"] <= ayar["bitis"])].reset_index(drop=True)
        for kolon in ayar["covariate_sutunlari"]:
            df[kolon] = df[kolon].ffill().bfill()
        df["item_id"] = "TR_arac_piyasasi"

        kolonlar = ["item_id", "tarih", TARGET] + ayar["covariate_sutunlari"]
        veri = df[kolonlar].rename(columns={"tarih": "timestamp"})
        tsdf = TimeSeriesDataFrame.from_data_frame(veri, id_column="item_id", timestamp_column="timestamp")

        predictor = TimeSeriesPredictor.load(str(ayar["model_yolu"]))

        print(f"  Permutasyon onemi hesaplaniyor ({len(ayar['covariate_sutunlari'])} ozellik x {NUM_ITERATIONS} tekrar)...")
        onem = predictor.feature_importance(
            data=tsdf,
            model=MODEL_ADI,
            method="permutation",
            num_iterations=NUM_ITERATIONS,
            random_seed=123,
        )
        print(onem.to_string())

        cikti_csv = MODEL_DIR / f"feature_importance_{set_adi.lower().replace('-', '_')}.csv"
        onem.to_csv(cikti_csv, encoding="utf-8-sig")

        cizim = onem.sort_values("importance")
        fig, ax = plt.subplots(figsize=(9, max(4, len(cizim) * 0.5)))
        renkler = ["#c62828" if v < 0 else "#2e7d32" for v in cizim["importance"]]
        ax.barh(cizim.index, cizim["importance"], color=renkler)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("Onem (MASE'deki bozulma - yuksek = daha onemli)")
        ax.set_title(f"{set_adi} — Feature Importance (permutasyon, {MODEL_ADI})")
        ax.grid(alpha=0.3, axis="x")
        fig.tight_layout()
        cikti_png = GORSEL_DIR / f"feature_importance_{set_adi.lower().replace('-', '_')}.png"
        fig.savefig(cikti_png, dpi=150)
        plt.close(fig)
        print(f"\n  Cikti: {cikti_csv}\n  Gorsel: {cikti_png}")


if __name__ == "__main__":
    main()
