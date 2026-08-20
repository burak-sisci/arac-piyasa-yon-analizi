# -*- coding: utf-8 -*-
"""3 satis-hizi/donusum hedefi icin ortak, sizintiya karsi temkinli backtest pipeline'i.

Adimlar (her target icin ozdes metodoloji):
1) feature_master_aylik.csv (2015-01+, target icermeyen aylik feature'lar) + hedef target
   kolonunu arac_piyasasi_master_veri_seti.csv'den birlestir.
2) Sizinti riski tasiyan kolonlari cikar:
   - Bu hedefin tam kaynagi olan ham kolon (target = ham kolonun birebir kopyasi; r=1.0 -> kopya sizinti).
   - modelleme_sizinti_kisitlari.csv'deki "tum_targetlar" genel yasaklari (karisik reel degisim,
     otv sizinti riskli fark, audit kolonu).
   - indicata_*/arabam_*/betam_* aile kolonlarinin AYNI-AY (referans ayi) versiyonlari: bu raporlar
     referans ayindan sonra yayimlaniyor (proje README'sindeki "available_at <= forecast_cutoff"
     kisitiyla uyumlu); bunun yerine 1 ay gecikmeli (lag1) versiyonlari kullanilir.
3) |Pearson korelasyon| < 0.1 olan feature'lari ele (min_periods=12, projenin
   scripts/filtrele_dusuk_korelasyon.py esigiyle ayni).
4) Kalan feature'lar arasinda |korelasyon| > 0.9 olan ciftlerden target ile daha
   dusuk korelasyona sahip olani ele (union-find gruplama).
5) Rolling-origin backtest: son N ayi test alarak, her test ayi icin sadece o aydan
   ONCEKI veriyle AutoGluon TimeSeriesPredictor (prediction_length=1) egit, 1 ay ileri
   tahmin et. Ayni test ayi icin "gecen yilin ayni ayi" (t-12) naive baseline'i hesapla.
6) Model ve baseline icin ayni 6 metrigi hesapla: yon dogrulugu, MAE, RMSE, MASE, bias, sMAPE.

Kullanim:
    .venv-ag\\Scripts\\python.exe scripts\\hiz_target_backtest_pipeline.py --target target_betam_dom_gun
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from autogluon.timeseries import TimeSeriesDataFrame, TimeSeriesPredictor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURE_PATH = PROJECT_ROOT / "data" / "target_bazli_birlesik_setler" / "feature_master_aylik.csv"
MASTER_PATH = PROJECT_ROOT / "data" / "birlesik_veri_seti" / "arac_piyasasi_master_veri_seti.csv"
OUT_ROOT = PROJECT_ROOT / "outputs" / "hiz_target_backtest"
DATE_COL = "referans_ayi"

CORR_ESIK = 0.1
COLLIN_ESIK = 0.9
MIN_PERIODS = 12
MAX_BACKTEST_AY = 6
MIN_TRAIN_AY = 8
FIT_TIME_LIMIT = 45  # saniye / fold

# Bu hedefin dogrudan uretildigi ham kolon (birebir kopya -> zorunlu disla).
# feature_master_aylik.csv / arac_piyasasi_master_veri_seti.csv icinde bulunan hedefler icin.
TARGET_TO_SOURCE_COL = {
    "target_betam_dom_gun": "betam_dom_gun",
    "target_indicata_satis_hizi_gun": "indicata_ortalama_satis_hizi_gun",
    "target_indicata_satis_ilan_orani_pct": "indicata_satis_ilan_orani_pct",
}

# feature_master_aylik.csv / master veri setinde YOK olan, harici data/ klasorlerinden
# okunan yeni hedef adaylari icin kaynak dosya + kolon eslesmesi.
EXTERNAL_TARGET_SOURCES = {
    "target_quickfinans_dom_gun": {
        "csv": PROJECT_ROOT / "data" / "quickfinans_stokta_kalma" / "quickfinans_aylik_stokta_kalma.csv",
        "date_col": "referans_ayi",
        "value_col": "stokta_kalma_suresi_gun_pazar",
    },
}


def _formul_ikinciel_yeniarac_satis_orani(fm: pd.DataFrame) -> pd.Series:
    return fm["noter_devir_otomobil_adet"] / fm["odmd_otomobil_adet"]


def _formul_kuyruk_stok_seviyesi(fm: pd.DataFrame) -> pd.Series:
    # Little's Law (L = lambda * W): lambda gunluk akisa cevrilir (ay uzunlugu 28-31 gun
    # farkini gidermek icin), W = betam_dom_gun (gun). L_t = o an piyasada aktif tahmini
    # satilik arac sayisi. Buyume-hizi DEGIL, SEVIYE olarak tanimlanir - adversarial
    # dogrulamada buyume-hizi versiyonunun log(A*B)=log(A)+log(B) ozdesligi geregi
    # target_1ay_hiz + betam_dom_gun log-farkina cebirsel olarak esit ciktigi (fark<1e-13),
    # yani gercek bir etkilesim degil iki mevcut targetin toplami oldugu tespit edildi.
    gun_sayisi = pd.to_datetime(fm["referans_ayi"]).dt.days_in_month
    return (fm["noter_devir_otomobil_adet"] / gun_sayisi) * fm["betam_dom_gun"]


# Var olan HAM feature'lari matematiksel olarak capraz-referanslayarak (target_devir_orani
# ornegindeki gibi) uretilen yeni hedef adaylari. Workflow tabanli coklu-ajan uretim +
# adversarial dogrulama surecinden gecmislerdir (bkz. proje notlari); formul, o dogrulamada
# onerilen duzeltmelerle birlikte nihai halidir.
DERIVED_TARGET_FORMULAS = {
    "target_capraz_ikinciel_yeniarac_satis_orani": {
        "func": _formul_ikinciel_yeniarac_satis_orani,
        "kaynak_kolonlar": {"noter_devir_otomobil_adet", "odmd_otomobil_adet"},
    },
    "target_capraz_kuyruk_stok_seviyesi": {
        "func": _formul_kuyruk_stok_seviyesi,
        "kaynak_kolonlar": {"noter_devir_otomobil_adet", "betam_dom_gun"},
    },
}

# modelleme_sizinti_kisitlari.csv -> "tum_targetlar" satirlarindan
HARD_EXCLUDE_ALWAYS = {
    "betam_raporlanan_reel_degisim_pct_karisik",
    "otv_ay_farki_en_yakin_olay_sizinti_riski",
    "proxy_arabam_fiyat_referansi_audit",
}

# Ayni-ay (referans ayi) versiyonu sizinti riskli sayilan, lag1'e cevrilecek aile
LAGGED_FAMILY_PREFIXES = ("indicata_", "arabam_", "betam_")


def build_feature_table(target_col: str) -> tuple[pd.DataFrame, list[str], dict]:
    fm = pd.read_csv(FEATURE_PATH)

    if target_col in DERIVED_TARGET_FORMULAS:
        # Hedef, feature_master_aylik.csv'deki VAR OLAN ham kolonlarin matematiksel
        # capraz-referanslanmasiyla (oran/fark/carpim) turetilir - hicbir harici kaynak
        # veya master veri seti gerekmez.
        spec = DERIVED_TARGET_FORMULAS[target_col]
        target_series = spec["func"](fm)
        mv = pd.DataFrame({DATE_COL: fm[DATE_COL], target_col: target_series})
    elif target_col in EXTERNAL_TARGET_SOURCES:
        # Bu hedefin ham kaynagi feature_master_aylik.csv / master veri setinde YOK -
        # ayri bir data/ klasorunden okunup referans_ayi uzerinden birlestirilir.
        src = EXTERNAL_TARGET_SOURCES[target_col]
        ext = pd.read_csv(src["csv"])[[src["date_col"], src["value_col"]]]
        ext = ext.rename(columns={src["date_col"]: DATE_COL, src["value_col"]: target_col})
        mv = ext
    else:
        mv = pd.read_csv(MASTER_PATH)[[DATE_COL, target_col]]

    df = fm.merge(mv, on=DATE_COL, how="left")
    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    df = df.sort_values(DATE_COL).reset_index(drop=True)

    if target_col in DERIVED_TARGET_FORMULAS:
        excluded_self = set(DERIVED_TARGET_FORMULAS[target_col]["kaynak_kolonlar"])
    else:
        source_col = TARGET_TO_SOURCE_COL.get(target_col)
        excluded_self = {source_col} if source_col else set()
    excluded_hard = HARD_EXCLUDE_ALWAYS & set(df.columns)

    lagged_created = []
    raw_family_cols = [
        c for c in fm.columns
        if c != DATE_COL and c.startswith(LAGGED_FAMILY_PREFIXES) and c not in excluded_hard
    ]
    for col in raw_family_cols:
        lag_col = f"{col}_lag1"
        df[lag_col] = df[col].shift(1)
        lagged_created.append(lag_col)

    df["ay"] = df[DATE_COL].dt.month
    df["ceyrek"] = df[DATE_COL].dt.quarter
    df["sin_ay"] = np.sin(2 * np.pi * df["ay"] / 12.0)
    df["cos_ay"] = np.cos(2 * np.pi * df["ay"] / 12.0)
    calendar_cols = ["ay", "ceyrek", "sin_ay", "cos_ay"]

    drop_cols = excluded_self | excluded_hard | set(raw_family_cols)
    candidate_features = [
        c for c in df.columns
        if c not in drop_cols and c not in (DATE_COL, target_col) and c not in lagged_created
    ] + lagged_created + calendar_cols
    candidate_features = list(dict.fromkeys(candidate_features))  # sirali unique

    exclusion_log = {
        "hedefin_ham_kaynak_kolonu_disi": sorted(excluded_self),
        "genel_sizinti_yasaklari": sorted(excluded_hard),
        "ayni_ay_yerine_lag1_yapilan_aile_kolonlari": sorted(raw_family_cols),
    }
    return df, candidate_features, exclusion_log


def korelasyon_filtresi(df: pd.DataFrame, target_col: str, features: list[str]) -> tuple[list[str], pd.DataFrame]:
    sub = df.dropna(subset=[target_col])
    corr = sub[features + [target_col]].corr(min_periods=MIN_PERIODS)[target_col].drop(target_col)
    ozet = pd.DataFrame({
        "feature": corr.index,
        "korelasyon": corr.values,
        "karar": np.where(corr.abs() >= CORR_ESIK, "tutuldu", "elendi"),
    }).sort_values("korelasyon")
    tutulan = ozet.loc[ozet["karar"] == "tutuldu", "feature"].tolist()
    return tutulan, ozet


def coklu_dogrusallik_azalt(df: pd.DataFrame, target_col: str, features: list[str]) -> tuple[list[str], pd.DataFrame]:
    sub = df.dropna(subset=[target_col])
    if len(features) < 2:
        return features, pd.DataFrame(columns=["feature_a", "feature_b", "korelasyon", "elenen"])

    hedef_korr = sub[features + [target_col]].corr(min_periods=MIN_PERIODS)[target_col].drop(target_col)
    feat_korr = sub[features].corr(min_periods=MIN_PERIODS)

    ebeveyn = {f: f for f in features}

    def bul(f):
        while ebeveyn[f] != f:
            f = ebeveyn[f]
        return f

    def birlestir(a, b):
        ra, rb = bul(a), bul(b)
        if ra != rb:
            ebeveyn[ra] = rb

    pair_rows = []
    for i, a in enumerate(features):
        for b in features[i + 1:]:
            v = feat_korr.loc[a, b]
            if pd.notna(v) and abs(v) > COLLIN_ESIK:
                birlestir(a, b)
                pair_rows.append({"feature_a": a, "feature_b": b, "korelasyon": v})

    gruplar: dict[str, list[str]] = {}
    for f in features:
        gruplar.setdefault(bul(f), []).append(f)

    tutulan = list(features)
    elenen_set = set()
    for grup in gruplar.values():
        if len(grup) < 2:
            continue
        skorlu = [(f, abs(hedef_korr.get(f, np.nan))) for f in grup]
        skorlu = [(f, s if pd.notna(s) else -1.0) for f, s in skorlu]
        en_iyi = max(skorlu, key=lambda x: x[1])[0]
        for f in grup:
            if f != en_iyi:
                elenen_set.add(f)
                tutulan.remove(f)

    pair_df = pd.DataFrame(pair_rows)
    if not pair_df.empty:
        pair_df["elenen"] = pair_df.apply(
            lambda r: r["feature_a"] if r["feature_a"] in elenen_set else (r["feature_b"] if r["feature_b"] in elenen_set else ""),
            axis=1,
        )
    return tutulan, pair_df


def find_backtest_months(df: pd.DataFrame, target_col: str) -> list[pd.Timestamp]:
    valid = df.dropna(subset=[target_col])[[DATE_COL, target_col]].copy()
    valid = valid.set_index(DATE_COL)[target_col]
    aday_aylar = []
    for m in valid.index:
        t_minus_12 = m - pd.DateOffset(months=12)
        if t_minus_12 in valid.index:
            train_count = (valid.index < m).sum()
            if train_count >= MIN_TRAIN_AY:
                aday_aylar.append(m)
    return sorted(aday_aylar)[-MAX_BACKTEST_AY:]


def prev_actual_value(valid_series: pd.Series, origin_month: pd.Timestamp):
    onceki = valid_series[valid_series.index <= origin_month]
    if onceki.empty:
        return np.nan
    return onceki.iloc[-1]


def fit_predict_one_step(train_df: pd.DataFrame, target_col: str, features: list[str], forecast_month: pd.Timestamp, model_dir: Path):
    keep_cols = [DATE_COL, target_col, *features]
    clean = train_df[keep_cols].copy()
    clean = clean.sort_values(DATE_COL)
    clean = clean.ffill().bfill()
    clean["item_id"] = "TR_otomobil"

    ts_df = TimeSeriesDataFrame.from_data_frame(clean, id_column="item_id", timestamp_column=DATE_COL)

    if model_dir.exists():
        import shutil
        shutil.rmtree(model_dir, ignore_errors=True)

    predictor = TimeSeriesPredictor(
        target=target_col,
        prediction_length=1,
        eval_metric="MAE",
        freq="MS",
        path=str(model_dir),
        verbosity=0,
    )
    predictor.fit(train_data=ts_df, presets="medium_quality", time_limit=FIT_TIME_LIMIT)
    pred = predictor.predict(ts_df)
    pred_df = pred.loc["TR_otomobil"].reset_index()
    pred_df["timestamp"] = pd.to_datetime(pred_df["timestamp"])
    row = pred_df.loc[pred_df["timestamp"] == forecast_month]
    if row.empty:
        return np.nan, predictor.model_best
    return float(row["mean"].iloc[0]), predictor.model_best


def compute_metrics(actual: np.ndarray, pred: np.ndarray, prev_actual: np.ndarray, mase_scale: float) -> dict:
    err = pred - actual
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err ** 2)))
    bias = float(np.mean(err))
    mase = float(mae / mase_scale) if mase_scale and mase_scale > 0 else float("nan")
    # sMAPE: olcekten bagimsiz, yuzdesel hata - farkli birimdeki hedefleri karsilastirmaya
    # yarar. |actual|+|pred|=0 olan (ikisi de tam sifir) noktalar disariya birakilir.
    smape_payda = np.abs(actual) + np.abs(pred)
    smape_gecerli = smape_payda > 0
    if smape_gecerli.sum() > 0:
        smape = float(np.mean(200 * np.abs(err[smape_gecerli]) / smape_payda[smape_gecerli]))
    else:
        smape = float("nan")

    gercek_yon = np.sign(actual - prev_actual)
    tahmin_yon = np.sign(pred - prev_actual)
    gecerli = gercek_yon != 0
    if gecerli.sum() > 0:
        yon_dogrulugu = float(np.mean(tahmin_yon[gecerli] == gercek_yon[gecerli]))
    else:
        yon_dogrulugu = float("nan")

    return {
        "mae": mae,
        "rmse": rmse,
        "bias": bias,
        "mase": mase,
        "smape_pct": smape,
        "yon_dogrulugu": yon_dogrulugu,
        "n_test_ay": int(len(actual)),
    }


def run(target_col: str) -> dict:
    out_dir = OUT_ROOT / target_col
    out_dir.mkdir(parents=True, exist_ok=True)
    model_dir_base = out_dir / "ag_models"

    df, candidate_features, exclusion_log = build_feature_table(target_col)
    tutulan_corr, corr_ozet = korelasyon_filtresi(df, target_col, candidate_features)
    corr_ozet.to_csv(out_dir / "korelasyon_filtre_ozeti.csv", index=False, encoding="utf-8-sig")

    tutulan_final, pair_df = coklu_dogrusallik_azalt(df, target_col, tutulan_corr)
    pair_df.to_csv(out_dir / "coklu_dogrusallik_ciftleri.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({"feature": tutulan_final}).to_csv(out_dir / "final_feature_seti.csv", index=False, encoding="utf-8-sig")

    valid_series = df.dropna(subset=[target_col]).set_index(DATE_COL)[target_col]
    n_obs = len(valid_series)
    tarih_min = valid_series.index.min()
    tarih_max = valid_series.index.max()

    result = {
        "target": target_col,
        "n_obs_toplam": int(n_obs),
        "tarih_araligi": f"{tarih_min.strftime('%Y-%m') if pd.notna(tarih_min) else None} -> {tarih_max.strftime('%Y-%m') if pd.notna(tarih_max) else None}",
        "aday_feature_sayisi": len(candidate_features),
        "korelasyon_sonrasi_feature_sayisi": len(tutulan_corr),
        "final_feature_sayisi": len(tutulan_final),
        "final_feature_listesi": tutulan_final,
        "disislanan_kolonlar": exclusion_log,
    }

    backtest_months = find_backtest_months(df, target_col)
    result["backtest_ay_sayisi"] = len(backtest_months)
    result["backtest_aylari"] = [m.strftime("%Y-%m") for m in backtest_months]

    if len(tutulan_corr) == 0:
        result["durum"] = "VERI_YETERSIZ_KORELASYON_HESAPLANAMADI"
        result["not"] = (
            f"Bu hedef icin yalnizca {n_obs} gozlem var; min_periods={MIN_PERIODS} esigi "
            f"nedeniyle hicbir feature icin guvenilir korelasyon hesaplanamadi (tum degerler NaN). "
            f"Bu hedef mevcut veriyle modellenemez durumda."
        )
        (out_dir / "metrikler.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    if len(backtest_months) == 0:
        result["durum"] = "VERI_YETERSIZ_BACKTEST_YOK"
        result["not"] = (
            f"Bu hedef icin {n_obs} gozlem mevcut ({result['tarih_araligi']}), ancak serinin "
            f"tamami tek bir takvim yili icinde oldugundan (veya yeterli t-12 karsiligi bulunmadigindan) "
            f"'gecen yilin ayni ayi' referans karsilastirmasi ve rolling backtest yapilamiyor."
        )
        (out_dir / "metrikler.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    # MASE olcek paydasi: tum gecmis (t, t-12) ciftleri uzerinden ortalama mutlak mevsimsel fark
    tum_farklar = []
    for m in valid_series.index:
        t12 = m - pd.DateOffset(months=12)
        if t12 in valid_series.index:
            tum_farklar.append(abs(valid_series[m] - valid_series[t12]))
    mase_scale = float(np.mean(tum_farklar)) if tum_farklar else float("nan")
    result["mase_olcek_payda_ortalama_mutlak_mevsimsel_fark"] = mase_scale

    kayitlar = []
    for m in backtest_months:
        origin = m - pd.DateOffset(months=1)
        # Hedefin ilk gercek gozleminden ONCEKI satirlari kirp: aksi halde asagidaki
        # ffill/bfill, hedefin baslamadigi yillari ilk gercek degerle geriye doldurup
        # uydurma duz bir gecmis yaratir (bu bug bir kullanici sorusuyla yakalandi).
        train_df = df[(df[DATE_COL] <= origin) & (df[DATE_COL] >= tarih_min)]
        model_dir = model_dir_base / m.strftime("%Y%m")
        try:
            forecast, best_model = fit_predict_one_step(train_df, target_col, tutulan_final, m, model_dir)
        except Exception as e:
            print(f"[HATA] {target_col} {m.strftime('%Y-%m')} fit/predict basarisiz: {e}", file=sys.stderr)
            continue

        actual = float(valid_series.get(m, np.nan))
        t12 = m - pd.DateOffset(months=12)
        baseline = float(valid_series.get(t12, np.nan))
        prev_a = prev_actual_value(valid_series, origin)

        kayitlar.append({
            "ay": m.strftime("%Y-%m"),
            "gercek": actual,
            "model_tahmin": forecast,
            "baseline_gecen_yil_ayni_ay": baseline,
            "onceki_bilinen_gercek": prev_a,
            "en_iyi_model": best_model,
        })

    backtest_df = pd.DataFrame(kayitlar)
    backtest_df.to_csv(out_dir / "backtest_sonuclari.csv", index=False, encoding="utf-8-sig")

    if backtest_df.empty:
        result["durum"] = "MODEL_EGITIMI_BASARISIZ"
        (out_dir / "metrikler.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return result

    actual_arr = backtest_df["gercek"].values
    model_arr = backtest_df["model_tahmin"].values
    baseline_arr = backtest_df["baseline_gecen_yil_ayni_ay"].values
    prev_arr = backtest_df["onceki_bilinen_gercek"].values

    model_metrikleri = compute_metrics(actual_arr, model_arr, prev_arr, mase_scale)
    baseline_metrikleri = compute_metrics(actual_arr, baseline_arr, prev_arr, mase_scale)

    result["durum"] = "TAMAMLANDI"
    result["model_metrikleri"] = model_metrikleri
    result["baseline_metrikleri_gecen_yil_ayni_ay"] = baseline_metrikleri
    result["en_iyi_modeller_fold_bazinda"] = backtest_df["en_iyi_model"].tolist()

    (out_dir / "metrikler.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Grafik ---
    plt.figure(figsize=(11, 5.5))
    history_len = min(24, len(valid_series))
    hist = valid_series.iloc[-history_len:]
    plt.plot(hist.index, hist.values, label="Gercek (tum tarihce)", color="#1f77b4", linewidth=2, marker="o", markersize=4)
    bt_dates = pd.to_datetime(backtest_df["ay"])
    plt.plot(bt_dates, backtest_df["model_tahmin"], label="AutoGluon Tahmini (backtest, h=1)", color="#d62728", linestyle="--", marker="s", linewidth=2)
    plt.plot(bt_dates, backtest_df["baseline_gecen_yil_ayni_ay"], label="Baseline: Gecen Yilin Ayni Ayi", color="#2ca02c", linestyle=":", marker="^", linewidth=2)
    plt.title(f"{target_col} - Gercek vs AutoGluon vs Gecen-Yil-Ayni-Ay Baseline")
    plt.xlabel("Ay")
    plt.ylabel(target_col)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "tahmin_grafigi.png", dpi=150)
    plt.close()

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    res = run(args.target)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
