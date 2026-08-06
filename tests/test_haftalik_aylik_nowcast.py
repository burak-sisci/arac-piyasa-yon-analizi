"""Haftalık güncellenen aylık yön nowcast veri sözleşmesi testleri."""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import haftalik_aylik_nowcast as hn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402
from turkiye_tatil_takvimi import turkiye_resmi_tatil_agirliklari  # noqa: E402


def _ornek_gunluk_df() -> pd.DataFrame:
    tarihler = pd.date_range("2024-01-01", "2024-04-30", freq="D")
    df = pd.DataFrame({"tarih": tarihler})
    df["ay"] = df["tarih"].dt.to_period("M")
    target = {
        pd.Period("2024-01", "M"): 100.0,
        pd.Period("2024-02", "M"): 110.0,
        pd.Period("2024-03", "M"): 108.0,
        pd.Period("2024-04", "M"): 90.0,
    }
    aylik = {
        pd.Period("2024-01", "M"): 10.0,
        pd.Period("2024-02", "M"): 20.0,
        pd.Period("2024-03", "M"): 30.0,
        pd.Period("2024-04", "M"): 40.0,
    }
    df["noter_devir_otomobil_adet"] = df["ay"].map(target)
    df["aylik_feature"] = df["ay"].map(aylik)
    df["gunluk_feature"] = np.arange(1, len(df) + 1, dtype=float)
    return df.drop(columns="ay")


def test_ay_sonu_etiketi_cari_ayi_onceki_ayla_karsilastirir():
    idx = pd.period_range("2024-01", "2024-04", freq="M")
    hacim = pd.Series([100.0, 110.0, 108.0, 90.0], index=idx)
    sonuc = hn.ay_sonu_nowcast_etiketleri(hacim, esik_yuzde=5.0)
    assert sonuc["2024-01"] == "eksik"
    assert sonuc["2024-02"] == "up"
    assert sonuc["2024-03"] == "stable"
    assert sonuc["2024-04"] == "down"


def test_ay_sonu_etiketi_takvim_boslugunu_atlamaz():
    idx = pd.PeriodIndex(["2024-01", "2024-03"], freq="M")
    sonuc = hn.ay_sonu_nowcast_etiketleri(pd.Series([100.0, 120.0], index=idx))
    assert sonuc["2024-03"] == "eksik"


def test_pazar_kesitleri_yalniz_gerceklesen_pazarlari_dondurur():
    sonuc = hn.pazar_kesit_tarihleri("2024-01-01", "2024-01-24")
    assert list(sonuc) == list(pd.to_datetime(["2024-01-07", "2024-01-14", "2024-01-21"]))
    assert all(x.weekday() == 6 for x in sonuc)


def test_snapshot_ay_esit_agirlik_ve_etiket_tekrari():
    sonuc = hn.haftalik_snapshot_uret(
        _ornek_gunluk_df(),
        gunluk_feature_sutunlari=["gunluk_feature"],
        aylik_feature_sutunlari=["aylik_feature"],
        target_lag_aylari=[2],
    )
    agirlik_toplamlari = sonuc.groupby("hedef_ay")["agirlik"].sum()
    assert np.allclose(agirlik_toplamlari.to_numpy(), 1.0)
    subat = sonuc[sonuc["hedef_ay"] == pd.Period("2024-02", "M")]
    assert set(subat["etiket"]) == {"up"}
    assert subat["hafta_sirasi"].tolist() == list(range(1, len(subat) + 1))
    assert (subat["gecen_is_gunu"] <= subat["aydaki_is_gunu"]).all()
    assert subat["is_gunu_ilerleme_orani"].between(0, 1).all()


def test_snapshot_gelecek_gunleri_gunluk_ozete_sizdirmaz():
    df = _ornek_gunluk_df()
    # 28 Ocak'taki dev sıçrama, 21 Ocak cut-off snapshot'ına girmemeli.
    df.loc[df["tarih"] == "2024-01-28", "gunluk_feature"] = 1_000_000.0
    sonuc = hn.haftalik_snapshot_uret(
        df,
        gunluk_feature_sutunlari=["gunluk_feature"],
        target_lag_aylari=[2],
    )
    satir_21 = sonuc[sonuc["kesit_tarihi"] == pd.Timestamp("2024-01-21")].iloc[0]
    assert satir_21["gunluk_feature_max"] < 1_000_000.0
    assert satir_21["gunluk_feature_gozlem_sayisi"] == 21


def test_snapshot_aylik_feature_ve_target_lag2_kullanir_lag1_yoktur():
    sonuc = hn.haftalik_snapshot_uret(
        _ornek_gunluk_df(),
        gunluk_feature_sutunlari=["gunluk_feature"],
        aylik_feature_sutunlari=["aylik_feature"],
        target_lag_aylari=[2, 3],
    )
    mart = sonuc[sonuc["hedef_ay"] == pd.Period("2024-03", "M")].iloc[0]
    assert mart["aylik_feature_lag2ay"] == pytest.approx(10.0)
    assert mart["noter_devir_otomobil_adet_lag2ay"] == pytest.approx(100.0)
    assert "noter_devir_otomobil_adet_lag1ay" not in sonuc.columns
    assert "noter_devir_otomobil_adet" not in hn.model_feature_sutunlari(sonuc)


def test_lag1_istegi_sizinti_riskiyle_reddedilir():
    with pytest.raises(ValueError, match="en az 2"):
        hn.haftalik_snapshot_uret(_ornek_gunluk_df(), target_lag_aylari=[1, 2])
    with pytest.raises(ValueError, match="lag<2"):
        hn.haftalik_snapshot_uret(_ornek_gunluk_df(), en_kucuk_aylik_lag=1)


def test_resmi_tatil_is_gunu_sayimindan_cikarilir():
    df = _ornek_gunluk_df()
    tatil = pd.Timestamp("2024-02-12")  # Pazartesi; test için sentetik tatil girdisi
    tatilsiz = hn.haftalik_snapshot_uret(df, target_lag_aylari=[2])
    tatilli = hn.haftalik_snapshot_uret(df, target_lag_aylari=[2], tatil_tarihleri=[tatil])
    a = tatilsiz[tatilsiz["hedef_ay"] == pd.Period("2024-02", "M")].iloc[-1]
    b = tatilli[tatilli["hedef_ay"] == pd.Period("2024-02", "M")].iloc[-1]
    assert b["aydaki_is_gunu"] == a["aydaki_is_gunu"] - 1
    assert b["gecen_is_gunu"] == a["gecen_is_gunu"] - 1


def test_yarim_gun_tatil_is_gunu_esdegerinden_yarim_duser():
    df = _ornek_gunluk_df()
    normal = hn.haftalik_snapshot_uret(df, target_lag_aylari=[2])
    yarim = hn.haftalik_snapshot_uret(
        df, target_lag_aylari=[2], tatil_tarihleri={"2024-02-12": 0.5}
    )
    a = normal[normal["hedef_ay"] == pd.Period("2024-02", "M")].iloc[-1]
    b = yarim[yarim["hedef_ay"] == pd.Period("2024-02", "M")].iloc[-1]
    assert b["aydaki_is_gunu"] == pytest.approx(a["aydaki_is_gunu"] - 0.5)


def test_2024_resmi_tatil_takvimi_bilinen_tam_ve_yarim_gunler():
    tatiller = turkiye_resmi_tatil_agirliklari(2024, 2024)
    assert tatiller[pd.Timestamp("2024-04-09")] == pytest.approx(0.5)
    assert tatiller[pd.Timestamp("2024-04-10")] == pytest.approx(1.0)
    assert tatiller[pd.Timestamp("2024-06-17")] == pytest.approx(1.0)
    assert tatiller[pd.Timestamp("2024-10-28")] == pytest.approx(0.5)
    assert tatiller[pd.Timestamp("2024-10-29")] == pytest.approx(1.0)


def test_cari_target_feature_olarak_reddedilir():
    with pytest.raises(ValueError, match="Cari target"):
        hn.haftalik_snapshot_uret(
            _ornek_gunluk_df(),
            gunluk_feature_sutunlari=["noter_devir_otomobil_adet"],
        )


def test_snapshot_spliti_aylari_bolmez():
    sonuc = hn.haftalik_snapshot_uret(
        _ornek_gunluk_df(),
        gunluk_feature_sutunlari=["gunluk_feature"],
        target_lag_aylari=[2],
    )
    split = yd.uc_parcali_split_olustur(
        "2024-01", "2024-01", "2024-02",
        "2024-03", "2024-03", "2024-04",
        "2024-05", "2024-05",
    )
    atanan = hn.snapshot_splitlerine_ata(sonuc, split)
    for _, grup in atanan.dropna(subset=["split"]).groupby("hedef_ay"):
        assert grup["split"].nunique() == 1


def test_ay_icinde_birden_fazla_target_degeri_reddedilir():
    df = _ornek_gunluk_df()
    df.loc[df["tarih"] == "2024-02-15", "noter_devir_otomobil_adet"] = 999.0
    with pytest.raises(ValueError, match="birden fazla"):
        hn.haftalik_snapshot_uret(df, target_lag_aylari=[2])


def test_nowcast_split_iki_aylik_embargo_ve_ay_gruplari_kurulur():
    split = hn.nowcast_uc_parcali_split_olustur(
        "2019-01", "2022-12",
        "2023-03", "2023-12",
        "2024-03", "2024-12",
        embargo_ay_sayisi=2,
    )
    assert split["embargo1"] == [pd.Period("2023-01", "M"), pd.Period("2023-02", "M")]
    assert split["embargo2"] == [pd.Period("2024-01", "M"), pd.Period("2024-02", "M")]
    assert split["validation"][0] == pd.Period("2023-03", "M")
    assert split["test"][0] == pd.Period("2024-03", "M")


def test_nowcast_split_eksik_embargo_reddedilir():
    with pytest.raises(ValueError, match="tam 2 aylık embargo"):
        hn.nowcast_uc_parcali_split_olustur(
            "2019-01", "2022-12",
            "2023-02", "2023-12",  # yalnız 1 ay boşluk
            "2024-03", "2024-12",
            embargo_ay_sayisi=2,
        )
