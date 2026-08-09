"""Model 15 ön-kayıt invariantları için odaklı testler."""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import model_15_frank_hall_ordinal as m15  # noqa: E402


def test_binary_hedefler_sabit_ordinal_sirayi_kullanir():
    z1, z2 = m15.binary_hedefler(pd.Series(["down", "stable", "up"]))
    assert z1.tolist() == [0, 1, 1]
    assert z2.tolist() == [0, 0, 1]


def test_monoton_projeksiyon_capraz_olmayan_degeri_korur():
    p = m15.monoton_olasiliklar([0.8], [0.3])
    assert p[0].tolist() == pytest.approx([0.2, 0.5, 0.3])


def test_monoton_projeksiyon_caprazi_ortalamayla_duzeltir():
    p = m15.monoton_olasiliklar([0.2], [0.8])
    assert p[0].tolist() == pytest.approx([0.5, 0.0, 0.5])
    assert p.sum() == pytest.approx(1.0)


def test_ordinal_tahmin_esitlikte_soldaki_sinifi_secer():
    tahmin = m15.ordinal_tahmin(np.array([[0.5, 0.0, 0.5], [0.1, 0.8, 0.1]]))
    assert tahmin.tolist() == ["down", "stable"]


def test_model15_tek_aday_ve_model14_featurelarini_birebir_kullanir():
    assert m15.ADAY == "frank_hall_l2_c01"
    assert len(m15.BESLI_AILE) == 5
    assert m15.MODEL14_ADAYLARI == list(m14.MODEL_ADLARI)
    assert len(m14.TEST_FEATURELAR) == 14


def test_origin_ve_kilitli_test_sozlesmesi():
    originler = m15.rn.genisleyen_originler(
        "2019-01", m15.SON_DEGERLENDIRME_AYI,
        ilk_train_ay_sayisi=24, embargo_ay_sayisi=2,
    )
    assert len(originler) == 50
    assert str(originler[-1]["degerlendirme"]) == "2025-04"
    assert all(o["degerlendirme"] < m15.KILITLI_TEST_BASLANGIC for o in originler)


def _sentetik_degerlendirme(**degisen):
    genel = {
        m15.ADAY: {"mcc": 0.10, "macro_f1": 0.38, "accuracy": 0.4},
        "train_cogunlugu": {"mcc": -0.07, "macro_f1": 0.28, "accuracy": 0.4},
    }
    h = {
        "h0_reddedildi": True, "delta_mcc_holm_alt_sinir": 0.01,
        "delta_mcc_nokta": 0.08, "delta_macro_f1_nokta": 0.02,
    }
    jack = {"isaret_her_yil_pozitif": True}
    for anahtar, deger in degisen.items():
        if anahtar in h:
            h[anahtar] = deger
        elif anahtar == "isaret_her_yil_pozitif":
            jack[anahtar] = deger
        elif anahtar.startswith("ordinal_"):
            genel[m15.ADAY][anahtar.removeprefix("ordinal_")] = deger
    return {
        "genel_metrikler": genel,
        "holm_besli_aile": {m15.ADAY: h},
        "ordinal_yil_jackknife": jack,
    }


def test_alti_kapi_hepsi_gecilmeden_terfi_olmaz():
    sonuc = m15.kapi_hesapla(_sentetik_degerlendirme())
    assert sonuc["terfi"] is True
    assert len(sonuc["kosullar"]) == 6
    for degisen in [
        {"h0_reddedildi": False},
        {"delta_mcc_nokta": 0.049},
        {"delta_macro_f1_nokta": 0.0},
        {"isaret_her_yil_pozitif": False},
        {"ordinal_mcc": m15.MODEL14_REFERANS["mcc"]},
        {"ordinal_macro_f1": 0.20},
    ]:
        assert m15.kapi_hesapla(_sentetik_degerlendirme(**degisen))["terfi"] is False


def test_ortam_kilidi_bu_proje_venvinde_gecer():
    meta = m15.ortam_dogrula()
    assert meta["scikit_learn"] == "1.7.2"
    assert meta["numpy"] == "2.3.5"
    assert meta["pandas"] == "2.3.3"
