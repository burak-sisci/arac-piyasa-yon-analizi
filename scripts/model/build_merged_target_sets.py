from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "birlesik_target_setleri"


def read_monthly(relative_path, columns, rename=None):
    """Read selected numeric columns and normalize the timestamp to month start."""
    path = DATA_DIR / relative_path
    table = pd.read_csv(path)
    required = ["referans_ayi", *columns]
    missing = [column for column in required if column not in table.columns]
    if missing:
        raise KeyError(f"{path.name}: missing columns {missing}")

    table = table[required].copy()
    table["referans_ayi"] = (
        pd.to_datetime(table["referans_ayi"], errors="coerce")
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    for column in columns:
        table[column] = pd.to_numeric(table[column], errors="coerce")

    if rename:
        table = table.rename(columns=rename)

    table = table.dropna(subset=["referans_ayi"])
    if table["referans_ayi"].duplicated().any():
        duplicates = table.loc[
            table["referans_ayi"].duplicated(keep=False), "referans_ayi"
        ].dt.strftime("%Y-%m").tolist()
        raise ValueError(f"{path.name}: duplicate months {duplicates}")

    return table.sort_values("referans_ayi").reset_index(drop=True)


def build_sources():
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
            [
                "osd_binek_adet",
                "osd_kamyonet_adet",
                "osd_binek_kamyonet_toplam_adet",
            ],
        ),
        read_monthly(
            "tufe/tufe_2024_bugun_aylik.csv",
            ["tufe_endeks", "tufe_aylik_degisim"],
        ),
        read_monthly(
            "tuketici_guveni/tuketici_guveni_2024_bugun_aylik.csv",
            ["tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi"],
        ),
        read_monthly(
            "faiz/faizler_2024_bugun_aylik.csv",
            ["tasit_kredisi_faiz", "politika_faizi"],
        ),
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
        read_monthly(
            "altintry/altintry_aylik_2015_bugun.csv",
            ["altin_gram_try"],
        ),
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
            rename={
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
            rename={
                "ortalama_ilan_fiyati_tl": "arabam_ortalama_ilan_fiyati_tl",
                "reel_aylik_degisim_pct": "arabam_reel_aylik_degisim_pct",
            },
        ),
        read_monthly(
            "proxy_fiyat/proxy_fiyat_2024_bugun_raw.csv",
            [
                "proxy_fiyat_cari_tl",
                "proxy_talep_aylik_pct",
                "proxy_satis_orani_pct",
                "proxy_dom_gun",
            ],
            rename={
                "proxy_fiyat_cari_tl": "betam_ortalama_ilan_fiyati_tl",
                "proxy_talep_aylik_pct": "betam_talep_aylik_pct",
                "proxy_satis_orani_pct": "betam_satis_orani_pct",
                "proxy_dom_gun": "betam_dom_gun",
            },
        ),
        read_monthly(
            "otv/otv_olaylari_2015_bugun_aylik.csv",
            ["otv_event_ay_mi"],
        ),
    ]

    eur_daily = pd.read_csv(DATA_DIR / "eurtry/eurtry_gunluk_2015_bugun.csv")
    eur_daily["tarih"] = pd.to_datetime(eur_daily["tarih"], errors="coerce")
    eur_daily["eurtry_orta"] = pd.to_numeric(
        eur_daily["eurtry_orta"], errors="coerce"
    )
    eur_daily = eur_daily.dropna(subset=["tarih", "eurtry_orta"]).sort_values(
        "tarih"
    )
    eur_daily["referans_ayi"] = (
        eur_daily["tarih"].dt.to_period("M").dt.to_timestamp()
    )
    eur_monthly = (
        eur_daily.groupby("referans_ayi", as_index=False)
        .agg(
            eurtry_ortalama=("eurtry_orta", "mean"),
            eurtry_aysonu=("eurtry_orta", "last"),
        )
    )
    sources.append(eur_monthly)

    betam_2023 = read_monthly(
        "betam/betam_2023_eksik_tamamlayici.csv",
        ["ortalama_ilan_fiyati_tl"],
        rename={"ortalama_ilan_fiyati_tl": "betam_ortalama_ilan_fiyati_tl"},
    )
    betam_index = next(
        index
        for index, table in enumerate(sources)
        if "betam_ortalama_ilan_fiyati_tl" in table.columns
    )
    sources[betam_index] = (
        pd.concat([betam_2023, sources[betam_index]], ignore_index=True)
        .sort_values("referans_ayi")
        .drop_duplicates("referans_ayi", keep="last")
    )
    return sources


def build_merged_table():
    sources = build_sources()
    notary = sources[0]
    valid_notary = notary["noter_devir_otomobil_adet"].notna()
    start = notary.loc[valid_notary, "referans_ayi"].min()
    end = notary.loc[valid_notary, "referans_ayi"].max()
    merged = pd.DataFrame(
        {"referans_ayi": pd.date_range(start=start, end=end, freq="MS")}
    )

    for source in sources:
        new_columns = [
            column
            for column in source.columns
            if column != "referans_ayi" and column not in merged.columns
        ]
        if new_columns:
            merged = merged.merge(
                source[["referans_ayi", *new_columns]],
                on="referans_ayi",
                how="left",
                validate="one_to_one",
            )
    return merged.sort_values("referans_ayi").reset_index(drop=True)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    merged = build_merged_table()
    feature_columns = [
        column for column in merged.columns if column != "referans_ayi"
    ]

    volume = merged["noter_devir_otomobil_adet"]
    rolling_three_month_volume = volume.rolling(3, min_periods=3).sum()
    merged["target_1ay_hiz"] = 100 * np.log(volume / volume.shift(1))
    merged["target_3ay_hiz"] = 100 * np.log(
        rolling_three_month_volume / rolling_three_month_volume.shift(3)
    )

    one_month = merged[
        ["referans_ayi", *feature_columns, "target_1ay_hiz"]
    ].dropna(subset=["target_1ay_hiz"])
    three_month = merged[
        ["referans_ayi", *feature_columns, "target_3ay_hiz"]
    ].dropna(subset=["target_3ay_hiz"])

    assert len(feature_columns) == 37
    assert len(one_month) == 101
    assert len(three_month) == 97
    assert one_month["target_1ay_hiz"].notna().all()
    assert three_month["target_3ay_hiz"].notna().all()

    csv_options = {"index": False, "encoding": "utf-8-sig"}
    one_month.to_csv(
        OUTPUT_DIR / "target_1ay_hiz_tum_featurelar.csv", **csv_options
    )
    three_month.to_csv(
        OUTPUT_DIR / "target_3ay_hiz_tum_featurelar.csv", **csv_options
    )

    coverage = pd.DataFrame(
        {
            "feature": feature_columns,
            "1ay_set_gecerli": [one_month[c].notna().sum() for c in feature_columns],
            "1ay_set_eksik": [one_month[c].isna().sum() for c in feature_columns],
            "3ay_set_gecerli": [
                three_month[c].notna().sum() for c in feature_columns
            ],
            "3ay_set_eksik": [three_month[c].isna().sum() for c in feature_columns],
        }
    )
    coverage.to_csv(
        OUTPUT_DIR / "feature_eksik_deger_ozeti.csv", **csv_options
    )

    with pd.ExcelWriter(
        OUTPUT_DIR / "iki_target_birlesik_setler.xlsx", engine="openpyxl"
    ) as writer:
        one_month.to_excel(writer, sheet_name="target_1ay_hiz", index=False)
        three_month.to_excel(writer, sheet_name="target_3ay_hiz", index=False)
        coverage.to_excel(writer, sheet_name="feature_eksik_ozeti", index=False)

    print(f"Feature count: {len(feature_columns)}")
    print(
        "target_1ay_hiz:",
        len(one_month),
        "rows,",
        one_month.shape[1],
        "columns,",
        one_month["referans_ayi"].min().strftime("%Y-%m"),
        "->",
        one_month["referans_ayi"].max().strftime("%Y-%m"),
    )
    print(
        "target_3ay_hiz:",
        len(three_month),
        "rows,",
        three_month.shape[1],
        "columns,",
        three_month["referans_ayi"].min().strftime("%Y-%m"),
        "->",
        three_month["referans_ayi"].max().strftime("%Y-%m"),
    )
    print("Output:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
