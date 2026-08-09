"""Model 16 nested hibrit ön-kayıt invariant testleri."""
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_16_nested_persistence_lojistik_hibrit as m16  # noqa: E402


def test_agirlik_izgarasi_sabit_ve_altili_aile():
    assert m16.AGIRLIKLAR == (0.0, 0.25, 0.5, 0.75, 1.0)
    assert len(m16.ALTI_AILE) == 6
    assert len(set(m16.ALTI_AILE)) == 6


def test_hibrit_olasilik_uc_nokta():
    p = np.array([[0.2, 0.3, 0.5]])
    assert m16.hibrit_olasilik(p, "down", 0.0)[0].tolist() == [1.0, 0.0, 0.0]
    assert m16.hibrit_olasilik(p, "down", 1.0)[0].tolist() == pytest.approx(p[0])
    assert m16.hibrit_olasilik(p, "down", 0.5)[0].tolist() == pytest.approx([0.6, 0.15, 0.25])


def test_agirlik_sec_pareto_yoksa_sifir():
    m = {
        0.0: {"mcc": 0.1, "macro_f1": 0.4},
        0.25: {"mcc": 0.2, "macro_f1": 0.3},
        0.5: {"mcc": 0.0, "macro_f1": 0.5},
        0.75: {"mcc": 0.0, "macro_f1": 0.3},
        1.0: {"mcc": -0.1, "macro_f1": 0.2},
    }
    assert m16.agirlik_sec(m)[0] == 0.0


def test_agirlik_sec_lexicographic_ve_kucuk_w_tie_break():
    m = {w: {"mcc": 0.1, "macro_f1": 0.4} for w in m16.AGIRLIKLAR}
    m[0.25] = {"mcc": 0.2, "macro_f1": 0.45}
    m[0.5] = {"mcc": 0.2, "macro_f1": 0.45}
    m[0.75] = {"mcc": 0.15, "macro_f1": 0.5}
    assert m16.agirlik_sec(m)[0] == 0.25


def test_ic_originler_dis_train_sinirinda_kalir():
    dis = m16.rn.genisleyen_originler(
        "2019-01", "2021-03", ilk_train_ay_sayisi=24, embargo_ay_sayisi=2
    )[0]
    ic = m16.rn.genisleyen_originler(
        dis["train"][0], dis["train"][-1], ilk_train_ay_sayisi=12, embargo_ay_sayisi=2
    )
    dis_set = set(dis["train"])
    assert len(ic) == 10
    assert all(set(o["train"] + o["embargo"] + [o["degerlendirme"]]).issubset(dis_set) for o in ic)


def test_yedi_kapi_hepsi_gerekli():
    genel = {
        m16.ADAY: {"mcc": 0.10, "macro_f1": 0.38, "accuracy": 0.4},
        "train_cogunlugu": {"mcc": -0.07, "macro_f1": 0.28, "accuracy": 0.4},
    }
    d = {
        "genel_metrikler": genel,
        "holm_altili_aile": {m16.ADAY: {
            "h0_reddedildi": True, "delta_mcc_holm_alt_sinir": 0.01,
            "delta_mcc_nokta": 0.08, "delta_macro_f1_nokta": 0.02,
        }},
        "hibrit_yil_jackknife": {"isaret_her_yil_pozitif": True},
    }
    sayac = {"dis_origin": 50, "dis_model_fit": 50}
    assert m16.kapi_hesapla(d, sayac)["terfi"] is True
    sayac["dis_origin"] = 49
    sonuc = m16.kapi_hesapla(d, sayac)
    assert sonuc["terfi"] is False
    assert len(sonuc["kosullar"]) == 7


def test_ortam_model15_kilidiyle_ayni():
    assert m16.m15.ortam_dogrula()["scikit_learn"] == "1.7.2"
