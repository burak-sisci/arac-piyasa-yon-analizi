from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_13_bddk_kapasite_dusuk_tekrar as m13  # noqa: E402


def _sonuc(null95, marj):
    return {"tavan_null95": null95, "marj": marj}


def test_tam_besinci_config_yalniz_c001_eklenir():
    modeller = m13.adaylar()
    assert len(modeller) == 5
    assert list(modeller)[-1] == "lojistik_l2_c001"
    assert modeller["lojistik_l2_c001"].C == pytest.approx(0.01)


def test_manipulasyon_strict_esikte_etkisizdir():
    karar = m13.karar_ver(
        _sonuc(m13.MANIPULASYON_ESIGI, -0.2),
        _sonuc(0.3, 0.2),
    )
    assert karar["hukum"] == "KAPASITE_MANIPULASYONU_ETKISIZ"
    assert karar["daha_fazla_c_taramasi"] is False


def test_kapasite_dusuk_gecti_terminal_dali():
    karar = m13.karar_ver(_sonuc(0.3, -0.1), _sonuc(0.3, 0.15))
    assert karar["hukum"] == "KAPASITE_DUSUK_GECTI"
    assert karar["otomatik_sonraki_dal"] == "REVIZYON_KIRILMA_NOKTASI_ANALIZI"


def test_kapasite_dusuk_zayif_teyit_yuksek_yeniden_acma():
    karar = m13.karar_ver(_sonuc(0.3, -0.3), _sonuc(0.3, -0.14))
    assert karar["hukum"] == "KAPASITE_DUSUK_ZAYIF_TEYIT"
    assert karar["yeniden_acma_onceligi"] == "YUKSEK"


def test_kapasite_dusuk_isaret_yok_normal_yeniden_acma():
    karar = m13.karar_ver(_sonuc(0.3, -0.2), _sonuc(0.3, -0.06))
    assert karar["hukum"] == "KAPASITE_DUSUK_ISARET_YOK"
    assert karar["yeniden_acma_onceligi"] == "NORMAL"


def test_karar_yalniz_verilen_c001_ciftine_bakar():
    kontrol = _sonuc(0.3, -0.4)
    test = _sonuc(0.3, -0.24)
    assert m13.karar_ver(kontrol, test)["hukum"] == "KAPASITE_DUSUK_ZAYIF_TEYIT"
