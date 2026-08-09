"""Model 17 sabit maliyet ve kapı invariantları."""
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_17_asimetrik_ordinal_maliyet as m17  # noqa: E402


def test_maliyet_matrisi_onkayitla_birebir():
    assert m17.MALIYET.tolist() == [[0, 1, 4], [1, 0, 1], [4, 1, 0]]
    assert len(m17.YEDILI_AILE) == 7


def test_beklenen_maliyet_saf_siniflarda_diagonali_secer():
    p = np.eye(3)
    assert m17.maliyet_tahmin(p).tolist() == ["down", "stable", "up"]


def test_reversal_riski_stable_kararini_destekler():
    p = np.array([[0.5, 0.0, 0.5]])
    # down/up kararlarının beklenen maliyeti 2, stable kararı 1.
    assert m17.beklenen_maliyet(p)[0].tolist() == pytest.approx([2.0, 1.0, 2.0])
    assert m17.maliyet_tahmin(p)[0] == "stable"


def test_esitlikte_sabit_soldaki_sinif():
    p = np.array([[1.0, 0.0, 0.0]])
    assert m17.maliyet_tahmin(p)[0] == "down"


def test_ortam_kilidi():
    assert m17.m15.ortam_dogrula()["scikit_learn"] == "1.7.2"
