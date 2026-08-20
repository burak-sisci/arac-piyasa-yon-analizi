# -*- coding: utf-8 -*-
"""Aylik feature masterini ve birbirinden ayrilmis target veri setlerini uretir.

Bu betik model egitmez ve eksik deger doldurmaz. Ham birlesik tablolari, hedef
sizintisini onlemek icin targetlari ayri tutarak yeniden uretilebilir hale getirir.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = DATA / "target_bazli_birlesik_setler"
DATE = "referans_ayi"


def read_monthly(relative_path: str, columns: list[str], rename: dict[str, str] | None = None):
    """Secilen alanlari okur ve tarih anahtarini ay basina normalize eder."""
    path = DATA / relative_path
    frame = pd.read_csv(path)
    required = [DATE, *columns]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise KeyError(f"{path.name}: eksik sutunlar {missing}")

    frame = frame[required].copy()
    frame[DATE] = pd.to_datetime(frame[DATE], errors="coerce").dt.to_period("M").dt.to_timestamp()
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if rename:
        frame = frame.rename(columns=rename)
    frame = frame.dropna(subset=[DATE]).sort_values(DATE)
    if frame[DATE].duplicated().any():
        duplicate_months = frame.loc[frame[DATE].duplicated(keep=False), DATE].dt.strftime("%Y-%m")
        raise ValueError(f"{path.name}: tekrar eden aylar {duplicate_months.tolist()}")
    return frame.reset_index(drop=True)


def merge_new_columns(master: pd.DataFrame, source: pd.DataFrame) -> pd.DataFrame:
    source_columns = [column for column in source.columns if column != DATE]
    overlap = sorted(set(source_columns).intersection(master.columns))
    if overlap:
        raise ValueError(f"Birlesimde sessiz sutun cakismasi: {overlap}")
    new_columns = source_columns
    return master.merge(source[[DATE, *new_columns]], on=DATE, how="left", validate="one_to_one")


def build_interest_monthly() -> pd.DataFrame:
    """Yanlis adlandirilmis eski aylik dosya yerine ham EVDS kodlarini dogru adlarla toplar."""
    housing = pd.read_csv(DATA / "faiz/tasit_kredisi_faiz_2024_bugun_ham.csv")
    housing["tarih"] = pd.to_datetime(housing["tarih_parsed"], errors="coerce")
    housing["konut_kredisi_faiz_ktf12"] = pd.to_numeric(housing["deger"], errors="coerce")
    housing = housing.dropna(subset=["tarih"]).drop_duplicates(
        ["tarih", "konut_kredisi_faiz_ktf12"]
    )
    housing[DATE] = housing["tarih"].dt.to_period("M").dt.to_timestamp()
    housing_monthly = housing.groupby(DATE, as_index=False).agg(
        konut_kredisi_faiz_ktf12=("konut_kredisi_faiz_ktf12", "mean")
    )

    funding = pd.read_csv(DATA / "faiz/politika_faizi_2024_bugun_ham.csv")
    funding["tarih"] = pd.to_datetime(funding["tarih_parsed"], errors="coerce")
    funding["tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4"] = pd.to_numeric(
        funding["deger"], errors="coerce"
    )
    funding = funding.dropna(subset=["tarih"])
    funding[DATE] = funding["tarih"].dt.to_period("M").dt.to_timestamp()
    funding_monthly = funding.groupby(DATE, as_index=False).agg(
        tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4=(
            "tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4",
            "mean",
        )
    )
    return housing_monthly.merge(funding_monthly, on=DATE, how="outer", validate="one_to_one")


def build_sparse_oyder_monthly() -> pd.DataFrame:
    """Yalniz YYYY-MM olan OYDER kayitlarindaki gercek aylik sayisal alanlari tutar."""
    frame = pd.read_csv(DATA / "odmd_oyder/odmd_oyder_bultenler_ham.csv")
    frame = frame.loc[frame[DATE].astype(str).str.fullmatch(r"\d{4}-\d{2}")].copy()
    frame[DATE] = pd.to_datetime(frame[DATE], errors="coerce").dt.to_period("M").dt.to_timestamp()
    mapping = {"ilan_sayisi": "oyder_ilan_sayisi", "satis_adedi": "oyder_satis_adedi"}
    frame = frame[[DATE, *mapping]].rename(columns=mapping)
    for column in mapping.values():
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values(DATE).reset_index(drop=True)


def build_feature_master() -> pd.DataFrame:
    """Mevcut aylik kaynaklardaki kullanilabilir tum sayisal featurelari birlestirir."""
    sources = [
        read_monthly(
            "noter_devir/noter_devir_2015_bugun_aylik.csv",
            ["noter_devir_toplam_adet", "noter_devir_otomobil_adet"],
        ),
        read_monthly(
            "odmd/odmd_2015_bugun_aylik.csv",
            ["odmd_toplam_adet", "odmd_otomobil_adet", "odmd_hta_adet"],
        ),
        read_monthly(
            "osd/osd_2024_bugun_aylik.csv",
            ["osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet"],
        ),
        read_monthly(
            "tufe/tufe_2024_bugun_aylik.csv",
            ["tufe_endeks", "tufe_aylik_degisim", "tufe_yillik_degisim"],
        ),
        read_monthly(
            "enag/enag_aylik_2021_2026.csv",
            ["enag_aylik_degisim", "enag_yillik_degisim"],
        ),
        read_monthly(
            "tuketici_guveni/tuketici_guveni_2024_bugun_aylik.csv",
            ["tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi"],
        ),
        build_interest_monthly(),
        read_monthly(
            "usdtry/usdtry_2015_bugun_aylik.csv",
            [
                "usdtry_aysonu_alis",
                "usdtry_aysonu_satis",
                "usdtry_aysonu",
                "usdtry_ortalama_alis",
                "usdtry_ortalama_satis",
                "usdtry_ortalama",
            ],
        ),
        read_monthly("altintry/altintry_aylik_2015_bugun.csv", ["altin_gram_try"]),
        read_monthly(
            "alim_gucu/alim_gucu_2018_bugun_aylik.csv",
            ["brut_ucret_maas_endeksi_2021_100"],
        ),
        read_monthly(
            "indicata/indicata_aylik.csv",
            [
                "ilan_yayinlanan_adet",
                "satisa_donen_adet",
                "satis_ilan_orani_pct",
                "ortalama_satis_hizi_gun",
                "perakende_fiyat_aylik_pct",
                "toptan_fiyat_aylik_pct",
            ],
            {
                "ilan_yayinlanan_adet": "indicata_ilan_yayinlanan_adet",
                "satisa_donen_adet": "indicata_satisa_donen_adet",
                "satis_ilan_orani_pct": "indicata_satis_ilan_orani_pct",
                "ortalama_satis_hizi_gun": "indicata_ortalama_satis_hizi_gun",
                "perakende_fiyat_aylik_pct": "indicata_perakende_fiyat_aylik_pct",
                "toptan_fiyat_aylik_pct": "indicata_toptan_fiyat_aylik_pct",
            },
        ),
        read_monthly(
            "arabamcom/arabamcom_aylik_fiyat.csv",
            ["ortalama_ilan_fiyati_tl", "reel_aylik_degisim_pct"],
            {
                "ortalama_ilan_fiyati_tl": "arabam_ortalama_ilan_fiyati_tl",
                "reel_aylik_degisim_pct": "arabam_reel_aylik_degisim_pct",
            },
        ),
        read_monthly(
            "proxy_fiyat/proxy_fiyat_2024_bugun_raw.csv",
            [
                "proxy_fiyat_cari_tl",
                "proxy_reel_aylik_pct",
                "proxy_nominal_yillik_pct",
                "proxy_talep_aylik_pct",
                "proxy_satis_orani_pct",
                "proxy_dom_gun",
                "proxy_fiyat_arabamcom_referans_tl",
            ],
            {
                "proxy_fiyat_cari_tl": "betam_ortalama_ilan_fiyati_tl",
                "proxy_reel_aylik_pct": "betam_raporlanan_reel_degisim_pct_karisik",
                "proxy_nominal_yillik_pct": "betam_nominal_yillik_degisim_pct",
                "proxy_talep_aylik_pct": "betam_talep_aylik_pct",
                "proxy_satis_orani_pct": "betam_satis_orani_pct",
                "proxy_dom_gun": "betam_dom_gun",
                "proxy_fiyat_arabamcom_referans_tl": "proxy_arabam_fiyat_referansi_audit",
            },
        ),
        read_monthly(
            "otv/otv_olaylari_2015_bugun_aylik.csv",
            ["otv_event_ay_mi", "otv_ay_farki_en_yakin_olay"],
            {"otv_ay_farki_en_yakin_olay": "otv_ay_farki_en_yakin_olay_sizinti_riski"},
        ),
        read_monthly(
            "trafige_kayitli_otomobiller/Trafiğe Kayıtlı Otomobillerin Yakıt Cinsine Göre Dağılımı (TR,DF_MOTORLU_KARA_TASIT_YAKIT_CINSI_V4,1.0).csv",
            ["trafige_kayitli_toplam_otomobil_adet"],
        ),
        build_sparse_oyder_monthly(),
    ]

    # Master targettan bagimsizdir: noter toplam serisinin basladigi 2015-01'den,
    # aylik kaynaklardaki en son referans ayina kadar butun takvimi korur.
    notary = sources[0]
    start = notary[DATE].min()
    end = max(source[DATE].max() for source in sources)
    master = pd.DataFrame({DATE: pd.date_range(start, end, freq="MS")})
    for source in sources:
        master = merge_new_columns(master, source)

    eur = pd.read_csv(DATA / "eurtry/eurtry_gunluk_2015_bugun.csv")
    eur["tarih"] = pd.to_datetime(eur["tarih"], errors="coerce")
    eur["eurtry_orta"] = pd.to_numeric(eur["eurtry_orta"], errors="coerce")
    eur = eur.dropna(subset=["tarih", "eurtry_orta"]).sort_values("tarih")
    eur[DATE] = eur["tarih"].dt.to_period("M").dt.to_timestamp()
    eur_monthly = eur.groupby(DATE, as_index=False).agg(
        eurtry_ortalama=("eurtry_orta", "mean"),
        eurtry_aysonu=("eurtry_orta", "last"),
    )
    master = merge_new_columns(master, eur_monthly)

    supplement = read_monthly(
        "betam/betam_2023_eksik_tamamlayici.csv",
        ["ortalama_ilan_fiyati_tl"],
        {"ortalama_ilan_fiyati_tl": "betam_ortalama_ilan_fiyati_tl"},
    )
    supplement_map = supplement.set_index(DATE)["betam_ortalama_ilan_fiyati_tl"]
    target_index = master[DATE].map(supplement_map)
    master["betam_ortalama_ilan_fiyati_tl"] = master[
        "betam_ortalama_ilan_fiyati_tl"
    ].combine_first(target_index)

    if master[DATE].duplicated().any():
        raise AssertionError("Feature masterda tekrar eden tarih bulundu.")
    if master.drop(columns=[DATE]).isna().all().any():
        empty = master.drop(columns=[DATE]).columns[master.drop(columns=[DATE]).isna().all()].tolist()
        raise AssertionError(f"Tamamen bos feature bulundu: {empty}")
    return master.sort_values(DATE).reset_index(drop=True)


def build_daily_market_master() -> pd.DataFrame:
    """Gercek gunluk/haftalik dort piyasa serisini nedensel olarak ayni takvimde toplar."""
    usd_raw = json.loads((DATA / "usdtry/usdtry_2015_bugun_raw.json").read_text(encoding="utf-8"))
    usd = pd.DataFrame(usd_raw["items"])
    usd["tarih"] = pd.to_datetime(usd["Tarih"], format="%d-%m-%Y", errors="coerce")
    usd["usdtry_alis"] = pd.to_numeric(usd["TP_DK_USD_A"], errors="coerce")
    usd["usdtry_satis"] = pd.to_numeric(usd["TP_DK_USD_S"], errors="coerce")
    usd["usdtry_orta"] = (usd["usdtry_alis"] + usd["usdtry_satis"]) / 2.0
    usd = usd[["tarih", "usdtry_alis", "usdtry_satis", "usdtry_orta"]]

    eur = pd.read_csv(DATA / "eurtry/eurtry_gunluk_2015_bugun.csv")
    eur["tarih"] = pd.to_datetime(eur["tarih"], errors="coerce")
    for column in ["eurtry_alis", "eurtry_satis", "eurtry_orta"]:
        eur[column] = pd.to_numeric(eur[column], errors="coerce")

    funding = pd.read_csv(DATA / "faiz/politika_faizi_2024_bugun_ham.csv")
    funding["tarih"] = pd.to_datetime(funding["tarih_parsed"], errors="coerce")
    funding["tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4"] = pd.to_numeric(
        funding["deger"], errors="coerce"
    )
    funding = funding[["tarih", "tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4"]]

    housing = pd.read_csv(DATA / "faiz/tasit_kredisi_faiz_2024_bugun_ham.csv")
    housing["tarih"] = pd.to_datetime(housing["tarih_parsed"], errors="coerce")
    housing["konut_kredisi_faiz_ktf12"] = pd.to_numeric(housing["deger"], errors="coerce")
    housing = housing[["tarih", "konut_kredisi_faiz_ktf12"]].drop_duplicates(
        ["tarih", "konut_kredisi_faiz_ktf12"]
    )

    inputs = [usd, eur, funding, housing]
    for frame in inputs:
        frame.dropna(subset=["tarih"], inplace=True)
        if frame["tarih"].duplicated().any():
            raise AssertionError("Gunluk kaynakta ayni tarih icin farkli kayit bulundu.")
    start = min(frame["tarih"].min() for frame in inputs)
    end = max(frame["tarih"].max() for frame in inputs)
    daily = pd.DataFrame({"tarih": pd.date_range(start, end, freq="D")})
    for frame in inputs:
        daily = daily.merge(frame, on="tarih", how="left", validate="one_to_one")

    # Ham gozlem tarihleri korunur. Ozellikle haftalik kredi faizi yayin
    # gecikmesi bilinmeden ileri tasinmaz; as-of model tablosu daha sonra gercek
    # available_at tarihleriyle uretilmelidir.
    daily["haftanin_gunu"] = daily["tarih"].dt.dayofweek
    daily["hafta_sonu_mu"] = daily["haftanin_gunu"].ge(5).astype("int8")
    daily["ayin_gunu"] = daily["tarih"].dt.day
    daily["ay"] = daily["tarih"].dt.month
    daily["ceyrek"] = daily["tarih"].dt.quarter
    daily["yil"] = daily["tarih"].dt.year
    daily["ay_sonu_mu"] = daily["tarih"].dt.is_month_end.astype("int8")
    if daily["tarih"].duplicated().any():
        raise AssertionError("Gunluk feature masterda tekrar eden tarih bulundu.")
    return daily


def build_targets(master: pd.DataFrame) -> dict[str, pd.DataFrame]:
    volume = master["noter_devir_otomobil_adet"]
    stock = master["trafige_kayitli_toplam_otomobil_adet"]
    if volume.dropna().le(0).any() or stock.dropna().le(0).any():
        raise AssertionError("Log/oran targetinda sifir veya negatif girdi bulundu.")
    rolling_3m = volume.rolling(3, min_periods=3).sum()
    target_1m = 100.0 * np.log(volume / volume.shift(1))
    target_3m = 100.0 * np.log(rolling_3m / rolling_3m.shift(3))
    target_ratio = volume / stock
    targets = {
        "target_1ay_hiz": pd.DataFrame({DATE: master[DATE], "target_1ay_hiz": target_1m}).dropna(),
        "target_3ay_hiz": pd.DataFrame({DATE: master[DATE], "target_3ay_hiz": target_3m}).dropna(),
        "target_devir_orani": pd.DataFrame(
            {DATE: master[DATE], "target_devir_orani": target_ratio}
        ).dropna(),
    }
    for name, target in targets.items():
        if not np.isfinite(target[name]).all():
            raise AssertionError(f"{name}: sonsuz veya gecersiz target degeri bulundu.")
        if target[DATE].duplicated().any():
            raise AssertionError(f"{name}: tekrar eden tarih bulundu.")
    return targets


def dataset_for_target(master: pd.DataFrame, target: pd.DataFrame) -> pd.DataFrame:
    return target.merge(master, on=DATE, how="left", validate="one_to_one")


def csv_ready(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result[DATE] = pd.to_datetime(result[DATE]).dt.strftime("%Y-%m")
    return result


def longest_missing_run(series: pd.Series) -> int:
    missing = series.isna().astype("int8")
    if not missing.any():
        return 0
    groups = missing.ne(missing.shift()).cumsum()
    return int(missing.groupby(groups).sum().max())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    master = build_feature_master()
    daily_master = build_daily_market_master()
    targets = build_targets(master)
    datasets = {name: dataset_for_target(master, target) for name, target in targets.items()}

    csv_options = {"index": False, "encoding": "utf-8-sig"}
    csv_ready(master).to_csv(OUT / "feature_master_aylik.csv", **csv_options)
    daily_out = daily_master.copy()
    daily_out["tarih"] = daily_out["tarih"].dt.strftime("%Y-%m-%d")
    daily_out.to_csv(OUT / "feature_master_gunluk_piyasa.csv", **csv_options)
    for name, target in targets.items():
        csv_ready(target).to_csv(OUT / f"{name}.csv", **csv_options)
        csv_ready(datasets[name]).to_csv(OUT / f"{name}_tum_featurelar.csv", **csv_options)

    monthly_features = [column for column in master.columns if column != DATE]
    coverage_rows = []
    for column in monthly_features:
        valid = master.loc[master[column].notna(), DATE]
        coverage_rows.append(
            {
                "feature": column,
                "gecerli_gozlem": master[column].notna().sum(),
                "eksik_gozlem": master[column].isna().sum(),
                "kapsama_orani": master[column].notna().mean(),
                "ilk_gecerli_ay": valid.min().strftime("%Y-%m") if len(valid) else "",
                "son_gecerli_ay": valid.max().strftime("%Y-%m") if len(valid) else "",
                "en_uzun_eksik_ay_serisi": longest_missing_run(master[column]),
            }
        )
    coverage = pd.DataFrame(coverage_rows).sort_values(["kapsama_orani", "feature"])
    coverage.to_csv(OUT / "feature_kapsama_ozeti.csv", **csv_options)

    daily_features = [column for column in daily_master.columns if column != "tarih"]
    daily_coverage = pd.DataFrame(
        {
            "feature": daily_features,
            "gecerli_gozlem": [daily_master[column].notna().sum() for column in daily_features],
            "eksik_gozlem": [daily_master[column].isna().sum() for column in daily_features],
            "en_uzun_eksik_gun_serisi": [
                longest_missing_run(daily_master[column]) for column in daily_features
            ],
        }
    )
    daily_coverage.to_csv(OUT / "gunluk_feature_kapsama_ozeti.csv", **csv_options)

    dictionary_rows = [
        {"target": "target_1ay_hiz", "frekans": "aylik", "formul": "100*ln(V_t/V_t-1)", "durum": "hesaplandi"},
        {"target": "target_3ay_hiz", "frekans": "aylik", "formul": "100*ln(sum(V_t-2:t)/sum(V_t-5:t-3))", "durum": "hesaplandi"},
        {"target": "target_devir_orani", "frekans": "aylik", "formul": "noter_devir_otomobil_adet / trafige_kayitli_toplam_otomobil_adet", "durum": "hesaplandi"},
        {"target": "target_7g_absorpsiyon", "frekans": "gunluk", "formul": "7 gunde dogrulanmis satilan / t gunu aktif sabit-bilesimli kohort", "durum": "ham gunluk ilan verisi bekleniyor"},
        {"target": "target_7g_kalite_duzeltilmis_fiyat_getirisi", "frekans": "gunluk", "formul": "100*ln(I_t+7/I_t)", "durum": "ham gunluk fiyat paneli bekleniyor"},
    ]
    pd.DataFrame(dictionary_rows).to_csv(OUT / "target_veri_sozlugu.csv", **csv_options)
    pd.DataFrame(columns=["tarih", "target_7g_absorpsiyon"]).to_csv(
        OUT / "target_7g_absorpsiyon_sablon.csv", **csv_options
    )
    pd.DataFrame(columns=["tarih", "target_7g_kalite_duzeltilmis_fiyat_getirisi"]).to_csv(
        OUT / "target_7g_kalite_duzeltilmis_fiyat_getirisi_sablon.csv", **csv_options
    )

    restrictions = pd.DataFrame(
        [
            {
                "kapsam": "target_1ay_hiz",
                "riskli_veya_yasakli_sutunlar": "noter_devir_otomobil_adet; noter_devir_toplam_adet",
                "neden": "Target cari ve onceki ay noter hacminden uretilir; cari ay degeri tahmin aninda bilinmez.",
            },
            {
                "kapsam": "target_3ay_hiz",
                "riskli_veya_yasakli_sutunlar": "noter_devir_otomobil_adet; noter_devir_toplam_adet",
                "neden": "Target noter hacmi bloklarindan uretilir; origin t'de t+3 gerceklesmesi tahmin edilir.",
            },
            {
                "kapsam": "target_devir_orani",
                "riskli_veya_yasakli_sutunlar": "noter_devir_otomobil_adet; trafige_kayitli_toplam_otomobil_adet; noter_devir_toplam_adet",
                "neden": "Ilk iki alan targetin pay ve paydasidir; cari ay noter alanlari tahmin aninda bilinmez.",
            },
            {
                "kapsam": "tum_targetlar",
                "riskli_veya_yasakli_sutunlar": "betam_raporlanan_reel_degisim_pct_karisik",
                "neden": "Kaynak sutun farkli donemlerde aylik ve yillik reel degisimi karistiriyor; duzeltilmeden modele verilmemeli.",
            },
            {
                "kapsam": "tum_targetlar",
                "riskli_veya_yasakli_sutunlar": "otv_ay_farki_en_yakin_olay_sizinti_riski; proxy_arabam_fiyat_referansi_audit",
                "neden": "Ilki gelecekteki en yakin olayi kullanabilir; ikincisi iki satirlik audit alanidir. Model girdisi degildir.",
            },
            {
                "kapsam": "tum_targetlar",
                "riskli_veya_yasakli_sutunlar": "konut_kredisi_faiz_ktf12; tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4",
                "neden": "Bunlar sirasiyla TP.KTF12 konut faizi ve TP.APIFON4 fonlama maliyetidir; tasit kredisi veya politika faizi degildir. Gercek yayin gecikmeleriyle kullanilmalidir.",
            },
            {
                "kapsam": "tum_targetlar",
                "riskli_veya_yasakli_sutunlar": "indicata_*; arabam_*; betam_* ve diger aylik rapor alanlari",
                "neden": "Referans ayi bilgi tarihi degildir; yalniz gercek yayin tarihi forecast cutoff'tan onceyse kullanilabilir.",
            },
        ]
    )
    restrictions.to_csv(OUT / "modelleme_sizinti_kisitlari.csv", **csv_options)
    pd.DataFrame(
        [
            {
                "eski_yanlis_ad": "tasit_kredisi_faiz",
                "ham_evds_kodu": "TP.KTF12",
                "dogru_ad": "konut_kredisi_faiz_ktf12",
                "islem": "Yeni ciktilarda dogru adla tutuldu; gercek tasit serisi TP.KTF11 ham klasorde yok.",
            },
            {
                "eski_yanlis_ad": "politika_faizi",
                "ham_evds_kodu": "TP.APIFON4",
                "dogru_ad": "tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4",
                "islem": "Yeni ciktilarda dogru adla tutuldu; politika faizi olarak yorumlanmadi.",
            },
        ]
    ).to_csv(OUT / "kaynak_etiket_duzeltmeleri.csv", **csv_options)

    consistency = {}
    for total, parts in [
        ("odmd_toplam_adet", ["odmd_otomobil_adet", "odmd_hta_adet"]),
        ("osd_binek_kamyonet_toplam_adet", ["osd_binek_adet", "osd_kamyonet_adet"]),
    ]:
        complete = master[[total, *parts]].notna().all(axis=1)
        difference = master.loc[complete, total] - master.loc[complete, parts].sum(axis=1)
        mismatch = int(difference.abs().gt(1e-9).sum())
        consistency[total] = {"kontrol_edilen_ay": int(complete.sum()), "uyusmazlik": mismatch}
        if mismatch:
            raise AssertionError(f"{total}: alt bilesen toplami ile uyusmayan ay bulundu.")

    audit = {
        "feature_master": {
            "satir": len(master),
            "feature_sayisi": len(master.columns) - 1,
            "baslangic": master[DATE].min().strftime("%Y-%m"),
            "bitis": master[DATE].max().strftime("%Y-%m"),
            "tekrar_eden_tarih": int(master[DATE].duplicated().sum()),
            "tamamen_bos_feature": int(master.drop(columns=[DATE]).isna().all().sum()),
        },
        "gunluk_feature_master": {
            "satir": len(daily_master),
            "feature_sayisi": len(daily_master.columns) - 1,
            "baslangic": daily_master["tarih"].min().strftime("%Y-%m-%d"),
            "bitis": daily_master["tarih"].max().strftime("%Y-%m-%d"),
            "tekrar_eden_tarih": int(daily_master["tarih"].duplicated().sum()),
        },
        "targets": {
            name: {
                "satir": len(target),
                "baslangic": target[DATE].min().strftime("%Y-%m"),
                "bitis": target[DATE].max().strftime("%Y-%m"),
                "eksik_target": int(target[name].isna().sum()),
            }
            for name, target in targets.items()
        },
        "toplam_bilesen_kontrolleri": consistency,
        "modelleme_notlari": [
            "Ham feature master target icermez; targetlar ayri tutulmustur.",
            "Ayni ay featurelari dogrudan model girdisi degildir; release-date/as-of veya uygun lag uygulanmalidir.",
            "Eksik deger doldurma ve feature secimi yalniz egitim foldunun icinde yapilmalidir.",
            "Eski filtreli/final dosyalar yeni deneylerin ham kaynagi olarak kullanilmamalidir.",
            "target_7g_absorpsiyon ve target_7g_fiyat icin veri uydurulmamistir.",
        ],
    }
    (OUT / "kalite_kontrol_raporu.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
