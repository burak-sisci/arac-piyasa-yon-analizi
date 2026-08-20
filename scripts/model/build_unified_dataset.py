# -*- coding: utf-8 -*-
"""Araç piyasası verilerini tek bir zaman serisi master veri setinde birleştiren betik.

Bu betik:
1. data/ altındaki tüm kaynakları (noter devir, ODMD, OSD, Indicata, Arabam, BETAM, TÜFE, ENAG, faizler, kurlar vb.) okur.
2. Tarihleri ay başına (YYYY-MM-01) normalize eder.
3. Days on Market (DOM), Satış Hızı, Devir Oranı gibi hedef değişken adaylarını hesaplar/ekler.
4. Hem CSV hem Excel olarak 'data/birlesik_veri_seti/' dizinine kaydeder.
5. Veri kapsamı, doluluk oranları ve korelasyon özetini çıkarır.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "birlesik_veri_seti"
DATE_COL = "referans_ayi"


def read_monthly(
    relative_path: str,
    columns: list[str],
    rename: dict[str, str] | None = None,
    encoding: str = "utf-8",
) -> pd.DataFrame:
    """Belirtilen aylık CSV dosyasını okur, tarih ve sayısal alanları normalize eder."""
    path = DATA_DIR / relative_path
    try:
        table = pd.read_csv(path, encoding=encoding)
    except UnicodeDecodeError:
        table = pd.read_csv(path, encoding="latin1")

    required = [DATE_COL, *columns]
    missing = [c for c in required if c not in table.columns]
    if missing:
        raise KeyError(f"{path.name}: eksik sütunlar {missing}")

    table = table[required].copy()
    table[DATE_COL] = (
        pd.to_datetime(table[DATE_COL], errors="coerce")
        .dt.to_period("M")
        .dt.to_timestamp()
    )
    for c in columns:
        table[c] = pd.to_numeric(table[c], errors="coerce")

    if rename:
        table = table.rename(columns=rename)

    table = table.dropna(subset=[DATE_COL]).sort_values(DATE_COL)
    if table[DATE_COL].duplicated().any():
        dups = table.loc[table[DATE_COL].duplicated(keep=False), DATE_COL].dt.strftime("%Y-%m").tolist()
        raise ValueError(f"{path.name}: tekrarlayan aylar {dups}")

    return table.reset_index(drop=True)


def build_interest_sources() -> pd.DataFrame:
    """Faiz verilerini hem özet tablodan hem ham EVDS serilerinden derler."""
    summary_path = DATA_DIR / "faiz/faizler_2024_bugun_aylik.csv"
    summary_df = pd.DataFrame()
    if summary_path.exists():
        summary_df = read_monthly(
            "faiz/faizler_2024_bugun_aylik.csv",
            ["tasit_kredisi_faiz", "politika_faizi"],
        )

    # Ham EVDS serileri
    housing_raw = DATA_DIR / "faiz/tasit_kredisi_faiz_2024_bugun_ham.csv"
    funding_raw = DATA_DIR / "faiz/politika_faizi_2024_bugun_ham.csv"

    housing_monthly = pd.DataFrame()
    if housing_raw.exists():
        h_df = pd.read_csv(housing_raw)
        h_df["tarih"] = pd.to_datetime(h_df["tarih_parsed"], errors="coerce")
        h_df["konut_kredisi_faiz_ktf12"] = pd.to_numeric(h_df["deger"], errors="coerce")
        h_df = h_df.dropna(subset=["tarih"]).drop_duplicates(["tarih", "konut_kredisi_faiz_ktf12"])
        h_df[DATE_COL] = h_df["tarih"].dt.to_period("M").dt.to_timestamp()
        housing_monthly = h_df.groupby(DATE_COL, as_index=False).agg(
            konut_kredisi_faiz_ktf12=("konut_kredisi_faiz_ktf12", "mean")
        )

    funding_monthly = pd.DataFrame()
    if funding_raw.exists():
        f_df = pd.read_csv(funding_raw)
        f_df["tarih"] = pd.to_datetime(f_df["tarih_parsed"], errors="coerce")
        f_df["tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4"] = pd.to_numeric(f_df["deger"], errors="coerce")
        f_df = f_df.dropna(subset=["tarih"])
        f_df[DATE_COL] = f_df["tarih"].dt.to_period("M").dt.to_timestamp()
        funding_monthly = f_df.groupby(DATE_COL, as_index=False).agg(
            tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4=("tcmb_agirlikli_ortalama_fonlama_maliyeti_apifon4", "mean")
        )

    # Birleştir
    merged_faiz = summary_df
    if not housing_monthly.empty:
        merged_faiz = merged_faiz.merge(housing_monthly, on=DATE_COL, how="outer") if not merged_faiz.empty else housing_monthly
    if not funding_monthly.empty:
        merged_faiz = merged_faiz.merge(funding_monthly, on=DATE_COL, how="outer") if not merged_faiz.empty else funding_monthly

    return merged_faiz.sort_values(DATE_COL).reset_index(drop=True)


def build_eur_monthly() -> pd.DataFrame:
    """Günlük EUR/TRY serisini aylık ortalama ve ay sonu olarak özetler."""
    eur = pd.read_csv(DATA_DIR / "eurtry/eurtry_gunluk_2015_bugun.csv")
    eur["tarih"] = pd.to_datetime(eur["tarih"], errors="coerce")
    eur["eurtry_orta"] = pd.to_numeric(eur["eurtry_orta"], errors="coerce")
    eur = eur.dropna(subset=["tarih", "eurtry_orta"]).sort_values("tarih")
    eur[DATE_COL] = eur["tarih"].dt.to_period("M").dt.to_timestamp()
    return eur.groupby(DATE_COL, as_index=False).agg(
        eurtry_ortalama=("eurtry_orta", "mean"),
        eurtry_aysonu=("eurtry_orta", "last"),
    )


def build_oyder_monthly() -> pd.DataFrame:
    """OYDER bültenlerinden düzenli aylık kayıtları derler."""
    path = DATA_DIR / "odmd_oyder/odmd_oyder_bultenler_ham.csv"
    if not path.exists():
        return pd.DataFrame(columns=[DATE_COL])
    df = pd.read_csv(path)
    df = df.loc[df[DATE_COL].astype(str).str.fullmatch(r"\d{4}-\d{2}")].copy()
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce").dt.to_period("M").dt.to_timestamp()
    mapping = {"ilan_sayisi": "oyder_ilan_sayisi", "satis_adedi": "oyder_satis_adedi"}
    df = df[[DATE_COL, *mapping.keys()]].rename(columns=mapping)
    for c in mapping.values():
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.sort_values(DATE_COL).reset_index(drop=True)


def collect_all_sources() -> list[pd.DataFrame]:
    """Tüm ham veri tablolarını standart formatta toplar."""
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
        build_interest_sources(),
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
        build_eur_monthly(),
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
                "proxy_nominal_yillik_pct",
                "proxy_talep_aylik_pct",
                "proxy_satis_orani_pct",
                "proxy_dom_gun",
            ],
            rename={
                "proxy_fiyat_cari_tl": "betam_ortalama_ilan_fiyati_tl",
                "proxy_nominal_yillik_pct": "betam_nominal_yillik_degisim_pct",
                "proxy_talep_aylik_pct": "betam_talep_aylik_pct",
                "proxy_satis_orani_pct": "betam_satis_orani_pct",
                "proxy_dom_gun": "betam_dom_gun",
            },
        ),
        read_monthly(
            "otv/otv_olaylari_2015_bugun_aylik.csv",
            ["otv_event_ay_mi"],
        ),
        read_monthly(
            "trafige_kayitli_otomobiller/Trafiğe Kayıtlı Otomobillerin Yakıt Cinsine Göre Dağılımı (TR,DF_MOTORLU_KARA_TASIT_YAKIT_CINSI_V4,1.0).csv",
            ["trafige_kayitli_toplam_otomobil_adet"],
        ),
        build_oyder_monthly(),
    ]

    # BETAM 2023 Tamamlayıcı
    betam_2023_path = DATA_DIR / "betam/betam_2023_eksik_tamamlayici.csv"
    if betam_2023_path.exists():
        betam_2023 = read_monthly(
            "betam/betam_2023_eksik_tamamlayici.csv",
            ["ortalama_ilan_fiyati_tl"],
            rename={"ortalama_ilan_fiyati_tl": "betam_ortalama_ilan_fiyati_tl"},
        )
        betam_idx = next(
            i for i, df in enumerate(sources) if "betam_ortalama_ilan_fiyati_tl" in df.columns
        )
        sources[betam_idx] = (
            pd.concat([betam_2023, sources[betam_idx]], ignore_index=True)
            .sort_values(DATE_COL)
            .drop_duplicates(DATE_COL, keep="last")
        )

    return sources


def build_master_dataset() -> pd.DataFrame:
    """Tüm kaynakları tek bir zaman serisi master tablosunda birleştirir."""
    sources = collect_all_sources()

    # Ortak tarih aralığı
    start_date = min(s[DATE_COL].min() for s in sources if not s.empty)
    end_date = max(s[DATE_COL].max() for s in sources if not s.empty)

    master = pd.DataFrame({DATE_COL: pd.date_range(start=start_date, end=end_date, freq="MS")})

    for s in sources:
        if s.empty:
            continue
        cols_to_add = [c for c in s.columns if c != DATE_COL and c not in master.columns]
        if cols_to_add:
            master = master.merge(
                s[[DATE_COL, *cols_to_add]],
                on=DATE_COL,
                how="left",
                validate="one_to_one",
            )

    # 1. Takvim ve Mevsimsellik Değişkenleri
    master["yil"] = master[DATE_COL].dt.year
    master["ay"] = master[DATE_COL].dt.month
    master["ceyrek"] = master[DATE_COL].dt.quarter
    master["sin_ay"] = np.sin(2 * np.pi * master["ay"] / 12.0)
    master["cos_ay"] = np.cos(2 * np.pi * master["ay"] / 12.0)

    # 2. Hedef Değişkenler (Target Candidates)
    # 2.1. Days on Market / Satış Hızı Hedefleri
    master["target_betam_dom_gun"] = master["betam_dom_gun"]
    master["target_indicata_satis_hizi_gun"] = master["indicata_ortalama_satis_hizi_gun"]
    master["target_indicata_satis_ilan_orani_pct"] = master["indicata_satis_ilan_orani_pct"]
    master["target_betam_satis_orani_pct"] = master["betam_satis_orani_pct"]
    master["target_indicata_satisa_donen_adet"] = master["indicata_satisa_donen_adet"]

    # 2.2. Hacimsel Devir Oranı Hedefi (Noter Devri / Araç Parkı)
    if "noter_devir_otomobil_adet" in master.columns and "trafige_kayitli_toplam_otomobil_adet" in master.columns:
        master["target_devir_orani"] = (
            master["noter_devir_otomobil_adet"] / master["trafige_kayitli_toplam_otomobil_adet"]
        )

    # 2.3. Hacim Log Büyüme Hızları (1 aylık ve 3 aylık)
    if "noter_devir_otomobil_adet" in master.columns:
        vol = master["noter_devir_otomobil_adet"]
        vol_3m = vol.rolling(3, min_periods=3).sum()
        master["target_1ay_hiz"] = 100.0 * np.log(vol / vol.shift(1))
        master["target_3ay_hiz"] = 100.0 * np.log(vol_3m / vol_3m.shift(3))

    return master.sort_values(DATE_COL).reset_index(drop=True)


def generate_coverage_report(df: pd.DataFrame) -> pd.DataFrame:
    """Her değişkenin veri kapsamını, doluluk oranını ve başlangıç/bitiş tarihlerini çıkarır."""
    rows = []
    total_months = len(df)
    for col in df.columns:
        if col == DATE_COL:
            continue
        valid_series = df.loc[df[col].notna(), DATE_COL]
        valid_count = int(df[col].notna().sum())
        missing_count = int(df[col].isna().sum())
        coverage_pct = round(100.0 * valid_count / total_months, 2)
        start_m = valid_series.min().strftime("%Y-%m") if len(valid_series) else "-"
        end_m = valid_series.max().strftime("%Y-%m") if len(valid_series) else "-"

        # Tür tespiti
        if col.startswith("target_"):
            var_type = "Target Adayı"
        elif col in ["yil", "ay", "ceyrek", "sin_ay", "cos_ay"]:
            var_type = "Takvim / Mevsimsellik"
        elif any(k in col for k in ["faiz", "fonlama"]):
            var_type = "Faiz / Para Politikası"
        elif any(k in col for k in ["usd", "eur", "altin"]):
            var_type = "Döviz / Emtia"
        elif any(k in col for k in ["tufe", "enag", "ucret", "alim"]):
            var_type = "Enflasyon / Gelir"
        elif any(k in col for k in ["noter", "odmd", "osd", "trafige"]):
            var_type = "Resmi Hacim & Araç Parkı"
        elif any(k in col for k in ["indicata", "arabam", "betam", "oyder"]):
            var_type = "İkinci El İlan & Arz/Talep"
        elif "otv" in col or "guven" in col:
            var_type = "Politika & Tüketici Güveni"
        else:
            var_type = "Diğer"

        rows.append(
            {
                "degisken": col,
                "kategori": var_type,
                "dolu_ay_sayisi": valid_count,
                "bos_ay_sayisi": missing_count,
                "doluluk_orani_pct": coverage_pct,
                "ilk_gecerli_ay": start_m,
                "son_gecerli_ay": end_m,
            }
        )
    return pd.DataFrame(rows).sort_values(by=["kategori", "degisken"]).reset_index(drop=True)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    master = build_master_dataset()

    # Tarihi string formatına çevrilmiş versiyon
    master_formatted = master.copy()
    master_formatted[DATE_COL] = master_formatted[DATE_COL].dt.strftime("%Y-%m")

    # CSV olarak kaydet
    csv_path = OUTPUT_DIR / "arac_piyasasi_master_veri_seti.csv"
    master_formatted.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # Kapsama Raporu
    coverage_df = generate_coverage_report(master)
    cov_path = OUTPUT_DIR / "veri_kapsama_ve_eksik_deger_raporu.csv"
    coverage_df.to_csv(cov_path, index=False, encoding="utf-8-sig")

    # Excel olarak kaydet (Master + Kapsama Raporu + Korelasyon)
    excel_path = OUTPUT_DIR / "arac_piyasasi_master_veri_seti.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        master_formatted.to_excel(writer, sheet_name="Master_Veri_Seti", index=False)
        coverage_df.to_excel(writer, sheet_name="Veri_Kapsama_Ozeti", index=False)

        # Target korelasyonları
        target_cols = [c for c in master.columns if c.startswith("target_")]
        num_cols = master.select_dtypes(include=[np.number]).columns
        corr = master[num_cols].corr()
        if target_cols:
            corr_targets = corr[target_cols].sort_values(by=target_cols[0], ascending=False)
            corr_targets.to_excel(writer, sheet_name="Target_Korelasyonlari")

    print("=== Master Veri Seti Başarıyla Oluşturuldu ===")
    print(f"Toplam Satır: {len(master)} ay ({master[DATE_COL].min().strftime('%Y-%m')} -> {master[DATE_COL].max().strftime('%Y-%m')})")
    print(f"Toplam Sütun: {len(master.columns)}")
    print(f"CSV Konumu: {csv_path}")
    print(f"Excel Konumu: {excel_path}")
    print(f"Kapsama Raporu: {cov_path}")
    print("\nHedef Değişken Kapsamları:")
    for t in [c for c in master.columns if c.startswith("target_")]:
        valid_cnt = master[t].notna().sum()
        sub = master.dropna(subset=[t])
        s_m = sub[DATE_COL].min().strftime("%Y-%m") if len(sub) else "-"
        e_m = sub[DATE_COL].max().strftime("%Y-%m") if len(sub) else "-"
        print(f" - {t}: {valid_cnt} ay dolu ({s_m} -> {e_m})")


if __name__ == "__main__":
    main()
