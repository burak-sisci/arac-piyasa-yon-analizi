# -*- coding: utf-8 -*-
"""Trafikteki otomobil parkina gore noter devir orani modeli.

Bu dosya uc isi birlikte ve yeniden uretilebilir bicimde yapar:
1. TUİK yakit cinsi dosyasini yalniz toplam otomobil parkina indirger.
2. Aylik kaynaklari birlestirir ve train-only korelasyon filtresi uygular.
3. AutoGluon TimeSeries best_quality ile h=1 modeli egitir ve test eder.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
TRAFFIC_DIR = DATA_DIR / "trafige_kayitli_otomobiller"
MERGED_DIR = DATA_DIR / "birlesik_target_setleri"
OUT = ROOT / "outputs" / "autogluon" / "ip7_devir_orani"
MODEL_DIR = OUT / "ag_model"

TARGET = "target_devir_orani"
DATE = "referans_ayi"
ITEM_ID = "TR_otomobil"
PREDICTION_LENGTH = 1
FREQ = "MS"
TEST_MONTHS = 6
VALIDATION_MONTHS = 6
MIN_PERIODS = 12
TARGET_CORR_THRESHOLD = 0.10
FEATURE_CORR_THRESHOLD = 0.90


def traffic_file() -> Path:
    files = sorted(TRAFFIC_DIR.glob("*.csv"))
    if len(files) != 1:
        raise RuntimeError(f"Trafik klasorunde tam bir CSV bekleniyordu, bulundu: {len(files)}")
    return files[0]


def parse_tr_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def clean_traffic_source() -> pd.DataFrame:
    """Kaynak CSV'yi kalici olarak iki sutunlu toplam otomobil serisine cevirir."""
    path = traffic_file()
    raw = pd.read_csv(path)
    clean_columns = {DATE, "trafige_kayitli_toplam_otomobil_adet"}

    if clean_columns.issubset(raw.columns) and len(raw.columns) == 2:
        clean = raw[[DATE, "trafige_kayitli_toplam_otomobil_adet"]].copy()
    else:
        required = {"YAKIT_TUR", "UNIT_MEASURE", "Zaman (TIME_PERIOD)", "Gözlem"}
        missing = required.difference(raw.columns)
        if missing:
            raise KeyError(f"Trafik dosyasinda eksik sutunlar: {sorted(missing)}")
        total = raw.loc[
            raw["YAKIT_TUR"].eq("_T") & raw["UNIT_MEASURE"].eq("PN"),
            ["Zaman (TIME_PERIOD)", "Gözlem"],
        ].copy()
        clean = total.rename(
            columns={
                "Zaman (TIME_PERIOD)": DATE,
                "Gözlem": "trafige_kayitli_toplam_otomobil_adet",
            }
        )
        clean["trafige_kayitli_toplam_otomobil_adet"] = parse_tr_number(
            clean["trafige_kayitli_toplam_otomobil_adet"]
        )

    clean[DATE] = pd.to_datetime(clean[DATE], errors="raise").dt.to_period("M").dt.to_timestamp()
    clean["trafige_kayitli_toplam_otomobil_adet"] = pd.to_numeric(
        clean["trafige_kayitli_toplam_otomobil_adet"], errors="raise"
    ).astype("int64")
    clean = clean.sort_values(DATE).drop_duplicates(DATE, keep="last").reset_index(drop=True)

    assert clean[DATE].is_monotonic_increasing
    assert not clean[DATE].duplicated().any()
    assert clean["trafige_kayitli_toplam_otomobil_adet"].gt(0).all()
    clean.assign(**{DATE: clean[DATE].dt.strftime("%Y-%m")}).to_csv(
        path, index=False, encoding="utf-8-sig"
    )
    return clean


def build_integrated_data(traffic: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from build_merged_target_sets import build_merged_table

    merged = build_merged_table().merge(traffic, on=DATE, how="left", validate="one_to_one")
    numerator = "noter_devir_otomobil_adet"
    denominator = "trafige_kayitli_toplam_otomobil_adet"
    merged[TARGET] = merged[numerator] / merged[denominator]

    raw_features = [c for c in merged.columns if c not in {DATE, TARGET}]
    lagged = merged[raw_features].shift(1).add_suffix("_lag1")
    model_base = pd.concat([merged[[DATE, TARGET]], lagged], axis=1)
    model_base = model_base.dropna(subset=[TARGET]).reset_index(drop=True)
    integrated = merged.dropna(subset=[TARGET]).reset_index(drop=True)

    expected = pd.date_range(integrated[DATE].min(), integrated[DATE].max(), freq=FREQ)
    assert integrated[DATE].equals(pd.Series(expected, name=DATE))
    assert integrated[numerator].notna().all()
    assert integrated[denominator].notna().all()
    assert np.isfinite(integrated[TARGET]).all()
    return integrated, model_base


def split_dates(frame: pd.DataFrame) -> dict[str, pd.Timestamp]:
    n = len(frame)
    test_start_i = n - TEST_MONTHS
    val_start_i = test_start_i - VALIDATION_MONTHS
    if val_start_i < 36:
        raise ValueError("Egitim penceresi modelleme icin cok kisa.")
    return {
        "train_start": frame.loc[0, DATE],
        "train_end": frame.loc[val_start_i - 1, DATE],
        "validation_start": frame.loc[val_start_i, DATE],
        "validation_end": frame.loc[test_start_i - 1, DATE],
        "test_start": frame.loc[test_start_i, DATE],
        "test_end": frame.loc[n - 1, DATE],
    }


def union_find_components(features: list[str], corr: pd.DataFrame) -> list[list[str]]:
    parent = {f: f for f in features}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, a in enumerate(features):
        for b in features[i + 1 :]:
            value = corr.loc[a, b]
            if pd.notna(value) and abs(value) > FEATURE_CORR_THRESHOLD:
                union(a, b)

    groups: dict[str, list[str]] = {}
    for feature in features:
        groups.setdefault(find(feature), []).append(feature)
    return list(groups.values())


def select_features(model_base: pd.DataFrame, dates: dict[str, pd.Timestamp]):
    feature_cols = [c for c in model_base.columns if c not in {DATE, TARGET}]
    train = model_base[model_base[DATE].le(dates["train_end"])]

    pearson = train[feature_cols + [TARGET]].corr(
        method="pearson", min_periods=MIN_PERIODS
    )[TARGET].drop(TARGET)
    spearman = train[feature_cols + [TARGET]].corr(
        method="spearman", min_periods=MIN_PERIODS
    )[TARGET].drop(TARGET)

    low = pearson.index[pearson.isna() | pearson.abs().lt(TARGET_CORR_THRESHOLD)].tolist()
    eligible = [f for f in feature_cols if f not in low]
    feature_corr = train[eligible].corr(method="pearson", min_periods=MIN_PERIODS)
    components = union_find_components(eligible, feature_corr)

    kept, collinear_drop, group_id = [], [], {}
    for number, group in enumerate(components, start=1):
        winner = max(group, key=lambda f: (abs(pearson[f]), f))
        kept.append(winner)
        if len(group) > 1:
            for feature in group:
                group_id[feature] = number
                if feature != winner:
                    collinear_drop.append(feature)

    dropped = set(low) | set(collinear_drop)
    summary = pd.DataFrame(
        {
            "feature": feature_cols,
            "pearson_target_train": [pearson.get(f, np.nan) for f in feature_cols],
            "spearman_target_train": [spearman.get(f, np.nan) for f in feature_cols],
            "karar": ["tutuldu" if f in kept else "ayrildi" for f in feature_cols],
            "neden": [
                "tutuldu"
                if f in kept
                else "target_abs_pearson_0.1_altinda_veya_hesaplanamadi"
                if f in low
                else "feature_abs_pearson_0.9_ustu_grupta_daha_zayif"
                for f in feature_cols
            ],
            "korelasyon_grubu": [group_id.get(f, np.nan) for f in feature_cols],
        }
    ).sort_values(["karar", "pearson_target_train"], ascending=[False, False])
    return kept, sorted(dropped), summary, feature_corr


def causal_impute(frame: pd.DataFrame, features: list[str], train_end: pd.Timestamp) -> pd.DataFrame:
    result = frame[[DATE, TARGET, *features]].copy()
    for feature in features:
        result[feature] = pd.to_numeric(result[feature], errors="coerce").ffill()
        train_values = result.loc[result[DATE].le(train_end), feature]
        fill = float(train_values.median()) if train_values.notna().any() else 0.0
        result[feature] = result[feature].fillna(fill)
    assert result[[TARGET, *features]].notna().all().all()
    return result


def tsdf(frame: pd.DataFrame, features: list[str]):
    from autogluon.timeseries import TimeSeriesDataFrame

    data = frame[[DATE, TARGET, *features]].rename(columns={DATE: "timestamp"}).copy()
    data.insert(0, "item_id", ITEM_ID)
    return TimeSeriesDataFrame.from_data_frame(
        data, id_column="item_id", timestamp_column="timestamp"
    )


def q50(prediction, month: pd.Timestamp) -> float:
    column = "0.5" if "0.5" in prediction.columns else 0.5
    return float(prediction.loc[(ITEM_ID, month), column])


def rolling_predictions(predictor, frame: pd.DataFrame, features: list[str], months: pd.DatetimeIndex):
    rows = []
    for model in predictor.model_names():
        for month in months:
            context = frame[frame[DATE].lt(month)]
            future = frame[frame[DATE].eq(month)]
            if context.empty or len(future) != 1:
                continue
            context_ts = tsdf(context, features)
            future_ts = tsdf(future, features).drop(columns=[TARGET])
            try:
                pred = predictor.predict(
                    context_ts,
                    known_covariates=future_ts,
                    model=model,
                    random_seed=42,
                )
                value = q50(pred, month)
            except Exception as exc:
                rows.append({"model": model, "hedef_ay": month, "hata": repr(exc)})
                break
            previous_actual = float(context.iloc[-1][TARGET])
            rows.append(
                {
                    "model": model,
                    "hedef_ay": month,
                    "y_true": float(future.iloc[0][TARGET]),
                    "y_pred": value,
                    "onceki_gercek": previous_actual,
                    "hata": "",
                }
            )
    return pd.DataFrame(rows)


def add_baselines(predictions: pd.DataFrame, frame: pd.DataFrame, months: pd.DatetimeIndex):
    rows = []
    indexed = frame.set_index(DATE)[TARGET]
    for month in months:
        history = indexed[indexed.index < month]
        actual = float(indexed.loc[month])
        previous = float(history.iloc[-1])
        baselines = {
            "NaiveSonDeger": previous,
            "Son12Ortalama": float(history.tail(12).mean()),
        }
        if month - pd.DateOffset(months=12) in indexed.index:
            baselines["MevsimselNaive12"] = float(indexed.loc[month - pd.DateOffset(months=12)])
        for model, pred in baselines.items():
            rows.append(
                {
                    "model": model,
                    "hedef_ay": month,
                    "y_true": actual,
                    "y_pred": pred,
                    "onceki_gercek": previous,
                    "hata": "",
                }
            )
    return pd.concat([predictions, pd.DataFrame(rows)], ignore_index=True)


def score(predictions: pd.DataFrame, mase_scale: float) -> pd.DataFrame:
    valid = predictions[predictions["hata"].fillna("").eq("")].dropna(
        subset=["y_true", "y_pred"]
    ).copy()
    valid["abs_error"] = (valid["y_true"] - valid["y_pred"]).abs()
    valid["sq_error"] = (valid["y_true"] - valid["y_pred"]) ** 2
    valid["bias_error"] = valid["y_pred"] - valid["y_true"]
    valid["yon_dogru"] = (
        np.sign(valid["y_pred"] - valid["onceki_gercek"])
        == np.sign(valid["y_true"] - valid["onceki_gercek"])
    ).astype(int)
    table = (
        valid.groupby("model")
        .agg(
            gozlem=("y_true", "size"),
            MAE=("abs_error", "mean"),
            RMSE=("sq_error", lambda x: float(np.sqrt(x.mean()))),
            bias=("bias_error", "mean"),
            yon_dogrulugu_yuzde=("yon_dogru", lambda x: 100.0 * x.mean()),
        )
        .reset_index()
    )
    table["MASE"] = table["MAE"] / mase_scale
    return table.sort_values(["MAE", "RMSE", "model"]).reset_index(drop=True)


def prepare_outputs():
    TRAFFIC_DIR.mkdir(parents=True, exist_ok=True)
    MERGED_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    traffic = clean_traffic_source()
    integrated, model_base = build_integrated_data(traffic)
    dates = split_dates(model_base)
    selected, dropped, summary, feature_corr = select_features(model_base, dates)
    model_ready = causal_impute(model_base, selected, dates["train_end"])

    formula_ok = np.allclose(
        integrated[TARGET],
        integrated["noter_devir_otomobil_adet"]
        / integrated["trafige_kayitli_toplam_otomobil_adet"],
        rtol=0,
        atol=1e-12,
    )
    assert formula_ok
    audit = {
        "target_formulu": "noter_devir_otomobil_adet / trafige_kayitli_toplam_otomobil_adet",
        "yuz_ile_carpildi": False,
        "target_formulu_dogrulandi": bool(formula_ok),
        "feature_secimi_yalniz_train_doneminde": True,
        "secilen_feature_sayisi": len(selected),
        "ayrilan_feature_sayisi": len(dropped),
    }

    integrated.assign(**{DATE: integrated[DATE].dt.strftime("%Y-%m")}).to_csv(
        MERGED_DIR / "target_devir_orani_tum_featurelar.csv", index=False, encoding="utf-8-sig"
    )
    model_ready.assign(**{DATE: model_ready[DATE].dt.strftime("%Y-%m")}).to_csv(
        MERGED_DIR / "target_devir_orani_model_final.csv", index=False, encoding="utf-8-sig"
    )
    separated = model_base[[DATE, TARGET, *dropped]].copy()
    separated.assign(**{DATE: separated[DATE].dt.strftime("%Y-%m")}).to_csv(
        MERGED_DIR / "target_devir_orani_ayrilan_featurelar.csv", index=False, encoding="utf-8-sig"
    )
    summary.to_csv(
        MERGED_DIR / "target_devir_orani_feature_secim_ozeti.csv", index=False, encoding="utf-8-sig"
    )
    feature_corr.to_csv(
        MERGED_DIR / "target_devir_orani_train_feature_korelasyon.csv", encoding="utf-8-sig"
    )
    (OUT / "splitler.json").write_text(
        json.dumps({k: v.strftime("%Y-%m") for k, v in dates.items()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT / "olcek_duzeltme_denetimi.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return traffic, integrated, model_ready, selected, dropped, summary, dates


def train_and_evaluate(model_ready, selected, dates, time_limit: int):
    from autogluon.timeseries import TimeSeriesPredictor

    if MODEL_DIR.exists():
        shutil.rmtree(MODEL_DIR)
    train = model_ready[model_ready[DATE].le(dates["train_end"])]
    train_data = tsdf(train, selected)
    predictor = TimeSeriesPredictor(
        prediction_length=PREDICTION_LENGTH,
        freq=FREQ,
        target=TARGET,
        known_covariates_names=selected,
        eval_metric="MASE",
        eval_metric_seasonal_period=1,
        path=MODEL_DIR,
        verbosity=2,
        log_to_file=True,
    )
    predictor.fit(
        train_data=train_data,
        presets="best_quality",
        time_limit=time_limit,
        num_val_windows=5,
        refit_full=False,
        random_seed=42,
        verbosity=2,
    )

    train_scale = float(train[TARGET].diff().abs().dropna().mean())
    val_months = pd.date_range(dates["validation_start"], dates["validation_end"], freq=FREQ)
    test_months = pd.date_range(dates["test_start"], dates["test_end"], freq=FREQ)

    val_pred = add_baselines(rolling_predictions(predictor, model_ready, selected, val_months), model_ready, val_months)
    val_rank = score(val_pred, train_scale)
    ag_models = set(predictor.model_names())
    chosen = val_rank[val_rank["model"].isin(ag_models)].iloc[0]["model"]

    test_all = add_baselines(rolling_predictions(predictor, model_ready, selected, test_months), model_ready, test_months)
    test_rank = score(test_all, train_scale)
    test_selected = test_all[test_all["model"].isin([chosen, "NaiveSonDeger", "Son12Ortalama", "MevsimselNaive12"])]
    test_selected_rank = score(test_selected, train_scale)

    val_pred.to_csv(OUT / "validasyon_tahminleri.csv", index=False, encoding="utf-8-sig")
    val_rank.to_csv(OUT / "validasyon_siralama.csv", index=False, encoding="utf-8-sig")
    test_all.to_csv(OUT / "test_tahminleri_tum_modeller.csv", index=False, encoding="utf-8-sig")
    test_rank.to_csv(OUT / "test_siralama_tum_modeller.csv", index=False, encoding="utf-8-sig")
    test_selected_rank.to_csv(OUT / "test_sonuc_secili_model.csv", index=False, encoding="utf-8-sig")
    predictor.leaderboard(train_data).to_csv(
        OUT / "autogluon_leaderboard.csv", index=False, encoding="utf-8-sig"
    )
    (OUT / "secili_model.txt").write_text(str(chosen), encoding="utf-8")

    return predictor, chosen, val_rank, test_rank, test_selected_rank


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--time-limit", type=int, default=900)
    args = parser.parse_args()

    traffic, integrated, model_ready, selected, dropped, summary, dates = prepare_outputs()
    print(f"Trafik serisi: {len(traffic)} satir, {traffic[DATE].min():%Y-%m} -> {traffic[DATE].max():%Y-%m}")
    print(f"Tumlesik hedef seti: {len(integrated)} satir, {integrated.shape[1]} sutun")
    print(f"Target: {TARGET} = noter_devir_otomobil_adet / trafige_kayitli_toplam_otomobil_adet")
    print(f"Secilen feature: {len(selected)} | Ayrilan feature: {len(dropped)}")
    print("Splitler:", {k: v.strftime('%Y-%m') for k, v in dates.items()})
    print("Secilenler:", selected)
    if args.prepare_only:
        return

    _, chosen, val_rank, test_rank, test_selected_rank = train_and_evaluate(
        model_ready, selected, dates, args.time_limit
    )
    print("\nVALIDASYON ILK 10")
    print(val_rank.head(10).to_string(index=False))
    print(f"\nSECILEN MODEL: {chosen}")
    print("\nNIHAI TEST")
    print(test_selected_rank.to_string(index=False))


if __name__ == "__main__":
    main()
