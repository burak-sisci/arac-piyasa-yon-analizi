from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import nowcast_baseline as nb  # noqa: E402


def _etiketler():
    idx = pd.period_range("2022-01", "2024-12", freq="M")
    deger = (["down", "stable", "up"] * 12)[: len(idx)]
    return pd.Series(deger, index=idx)


def test_baseline_as_of_persistence_m_eksi_2_kullanir():
    s = _etiketler()
    tahmin, _ = nb.baseline_tahminleri(s, pd.period_range("2022-01", "2023-12", freq="M"), ["2024-06"])
    assert tahmin["persistence_m_eksi_2"] == [s[pd.Period("2024-04", freq="M")]]


def test_mevsimsel_tahmin_t_eksi_12_kullanir():
    s = _etiketler()
    tahmin, _ = nb.baseline_tahminleri(s, pd.period_range("2022-01", "2023-12", freq="M"), ["2024-06"])
    assert tahmin["seasonal_t_eksi_12"] == [s[pd.Period("2023-06", freq="M")]]


def test_cogunluk_yalniz_train_verisinden_hesaplanir():
    s = _etiketler()
    train = pd.period_range("2022-01", "2022-05", freq="M")
    _, cogunluk = nb.baseline_tahminleri(s, train, ["2024-06"])
    assert cogunluk == "down"


def test_eksik_gecmis_baseline_reddedilir():
    s = _etiketler()
    with pytest.raises(ValueError, match="gecersiz/eksik"):
        nb.baseline_tahminleri(s, pd.period_range("2022-01", "2022-12", freq="M"), ["2022-02"])


def test_degerlendirme_ay_esit_ve_uc_baseline_dondurur():
    s = _etiketler()
    sonuc = nb.baseline_degerlendir(
        s, pd.period_range("2022-01", "2023-12", freq="M"), pd.period_range("2024-01", "2024-12", freq="M")
    )
    assert set(sonuc["metrikler"]) == {
        "train_cogunlugu", "persistence_m_eksi_2", "seasonal_t_eksi_12"
    }
    assert all(m["n"] == 12 for m in sonuc["metrikler"].values())
    assert all(m["agirlikli_mi"] is False for m in sonuc["metrikler"].values())


def test_snapshot_sirasi_kapsami_aylari_tekillestirir():
    df = pd.DataFrame({
        "hedef_ay": ["2024-01", "2024-01", "2024-02"],
        "hafta_sirasi": [1, 2, 1],
        "etiket": ["up", "up", "down"],
    })
    sonuc = nb.snapshot_sirasi_kapsami(df, ["2024-01", "2024-02"])
    assert sonuc["1"]["ay_sayisi"] == 2
    assert sonuc["2"]["ay_sayisi"] == 1
    assert sonuc["1"]["sinif_dagilimi"] == {"down": 1, "stable": 0, "up": 1}


def test_snapshot_eksik_sutun_reddedilir():
    with pytest.raises(ValueError, match="Eksik snapshot"):
        nb.snapshot_sirasi_kapsami(pd.DataFrame({"hedef_ay": ["2024-01"]}), ["2024-01"])
