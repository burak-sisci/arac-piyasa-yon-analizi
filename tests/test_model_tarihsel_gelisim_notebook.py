"""Model 01–18 tarihsel gelişim notebookunun yapısal ve içerik testleri."""
from __future__ import annotations

import ast
from pathlib import Path

import nbformat
import pandas as pd


REPO_KOKU = Path(__file__).resolve().parents[1]
NOTEBOOK = REPO_KOKU / "notebooks" / "model_tarihsel_gelisim_ve_farklar_ders_kitabi.ipynb"
URETICI = REPO_KOKU / "scripts" / "model" / "model_tarihsel_gelisim_notebook_uret.py"


def _oku():
    return nbformat.read(NOTEBOOK, as_version=4)


def test_notebook_ve_uretici_mevcut():
    assert NOTEBOOK.exists()
    assert URETICI.exists()


def test_notebook_nbformat_dogrulamasindan_gecer():
    nb = _oku()
    nbformat.validate(nb)
    assert nb.nbformat == 4


def test_notebook_metadata_pusula_ve_kapsami_kilitler():
    proje = _oku().metadata["proje"]
    assert proje["kapsam"] == "Model 01–18 tarihsel gelişim ve farklar"
    assert proje["pusula_oturum"] == "019fd8ad-8e18-7b4e-a6d4-3c0214efc923"
    assert "Rota-2" in proje["hazirlayanlar"]


def test_tum_kod_hucreleri_python_olarak_derlenir_ve_hata_ciktisi_yoktur():
    nb = _oku()
    kodlar = [c for c in nb.cells if c.cell_type == "code"]
    assert len(kodlar) == 9
    for hucre in kodlar:
        ast.parse(hucre.source)
        assert not any(cikti.output_type == "error" for cikti in hucre.get("outputs", []))


def test_model_01_18_kronolojisi_eksiksiz_tekil_ve_siralidir():
    nb = _oku()
    kaynak = next(c.source for c in nb.cells if c.cell_type == "code" and "MODELLER = [" in c.source)
    alan = {"pd": pd}
    exec(compile(kaynak, str(NOTEBOOK), "exec"), alan)
    tarihce = alan["tarihce"]
    assert tarihce["model"].tolist() == list(range(1, 19))
    assert tarihce["model"].is_unique


def test_egitim_disindaki_kritik_roller_dogru_etiketlidir():
    nb = _oku()
    kaynak = next(c.source for c in nb.cells if c.cell_type == "code" and "MODELLER = [" in c.source)
    alan = {"pd": pd}
    exec(compile(kaynak, str(NOTEBOOK), "exec"), alan)
    tarihce = alan["tarihce"].set_index("model")
    assert tarihce.loc[3:5, "rol"].eq("Yeniden değerlendirme").all()
    assert tarihce.loc[7, "rol"] == "Veri sözleşmesi"
    assert tarihce.loc[8, "rol"] == "Baseline"
    assert tarihce.loc[11, "rol"] == "Teşhis / üst tavan"
    assert tarihce.loc[17, "rol"] == "Karar katmanı"
    assert tarihce.loc[18, "rol"] == "Prospektif izleme"


def test_mase_ile_mcc_ayni_karsilastirma_tablosuna_konmamistir():
    nb = _oku()
    kaynak = "\n".join(c.source for c in nb.cells)
    assert "MASE ile MCC doğrudan karşılaştırılmaz" in kaynak
    performans_hucresi = next(
        c.source for c in nb.cells if c.cell_type == "code" and "ayni_yuzey = pd.DataFrame" in c.source
    )
    assert "MASE" not in performans_hucresi


def test_kilitli_test_ve_model18_peeking_yasagi_acikca_yazilidir():
    kaynak = "\n".join(c.source for c in _oku().cells)
    assert "kilitli `2025-07..2026-06` test açılmadı" in kaynak
    assert "12 eksiksiz yeni bağımsız ay dolmadan performans metriği" in kaynak
