from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_12_bddk_tavan_taramasi as m12  # noqa: E402


def _sentetik_seri():
    tarihler = pd.date_range("2019-01-04", periods=130, freq="W-FRI")
    return pd.DataFrame({
        "referans_hafta": tarihler,
        "bakiye_milyon_tl": np.arange(100.0, 230.0),
    })


def test_m2_capa_ve_konumsal_geri_indeksleme():
    seri = _sentetik_seri()
    ay = pd.Period("2021-06", "M")
    tufe = pd.Series({ay: 2.0})
    sonuc, meta = m12.aylik_bddk_featurelari(seri, [ay], tufe)
    satir = sonuc.iloc[0]
    assert satir["bddk_capa_haftasi"] <= pd.Timestamp("2021-04-30")
    assert satir["bddk_capa_haftasi"].to_period("M") <= ay - 2
    assert meta["feature_sayisi"] == 4
    assert meta["m1_m_haftasi_kullanildi"] is False


def test_tatil_kaymasinda_capa_ve_konumsal_geri_indeksleme():
    tarihler = pd.date_range("2014-01-03", periods=130, freq="W-FRI")
    tarihler = tarihler.where(tarihler != pd.Timestamp("2015-05-01"), pd.Timestamp("2015-04-30"))
    seri = pd.DataFrame({
        "referans_hafta": tarihler,
        "bakiye_milyon_tl": np.arange(100.0, 230.0),
    })
    takvim = m12.seri_takvimini_dogrula(seri, tam_resmi_seri=False)
    ay = pd.Period("2015-06", "M")
    sonuc, _ = m12.aylik_bddk_featurelari(seri, [ay], pd.Series({ay: 1.0}))
    satir = sonuc.iloc[0]
    pos = seri.index[seri["referans_hafta"].eq(pd.Timestamp("2015-04-30"))][0]
    beklenen_4h = (
        seri.loc[pos, "bakiye_milyon_tl"] / seri.loc[pos - 4, "bakiye_milyon_tl"] - 1
    ) * 100
    assert satir["bddk_capa_haftasi"] == pd.Timestamp("2015-04-30")
    assert satir["bddk_tasit_bakiye_4h_degisim_pct"] == pytest.approx(beklenen_4h)
    assert takvim["cuma_disi_hafta_sayisi"] == 1
    assert takvim["tatille_eslesmeyen_haftalar"] == []


def test_takvim_denetimi_haftalik_boslukta_durur():
    seri = _sentetik_seri().drop(index=10).reset_index(drop=True)
    with pytest.raises(RuntimeError, match=r"\[4,10\]"):
        m12.seri_takvimini_dogrula(seri)


def test_exact_3_11_bayram_ciftleri_tuketilir_ve_14_gun_korunur():
    tarihler = pd.date_range("2014-01-03", "2026-07-31", freq="W-FRI")
    tarihler = tarihler.where(tarihler != pd.Timestamp("2018-08-24"), pd.Timestamp("2018-08-20"))
    tarihler = tarihler.where(tarihler != pd.Timestamp("2021-07-23"), pd.Timestamp("2021-07-19"))
    seri = pd.DataFrame({
        "referans_hafta": tarihler,
        "bakiye_milyon_tl": np.arange(1.0, len(tarihler) + 1.0),
    })
    denetim = m12.seri_takvimini_dogrula(seri, tam_resmi_seri=True)
    assert denetim["izinli_istisna_sayisi"] == 4
    assert denetim["ardisik_aralik_min_gun"] == 3
    assert denetim["ardisik_aralik_maks_gun"] == 11


def test_cache_hash_uyusmazliginda_durur(tmp_path):
    sahte = tmp_path / "bddk.csv"
    sahte.write_text("referans_hafta,bakiye_milyon_tl\n2026-01-02,1\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="SHA-256"):
        m12.bddk_serisini_cacheden_oku(sahte)


def test_dort_feature_formulu_carpimsal_reel():
    seri = _sentetik_seri()
    ay = pd.Period("2021-06", "M")
    tufe = pd.Series({ay: 2.0})
    sonuc, _ = m12.aylik_bddk_featurelari(seri, [ay], tufe)
    satir = sonuc.iloc[0]
    n = satir["bddk_tasit_bakiye_4h_degisim_pct"]
    beklenen = ((1 + n / 100) / 1.02 - 1) * 100
    assert satir["bddk_tasit_bakiye_reel_4h_degisim_pct"] == pytest.approx(beklenen)
    assert set(m12.BDDk_FEATURELARI) == {
        "bddk_tasit_bakiye_4h_degisim_pct",
        "bddk_tasit_bakiye_13h_degisim_pct",
        "bddk_tasit_bakiye_52h_degisim_pct",
        "bddk_tasit_bakiye_reel_4h_degisim_pct",
    }


def _kol(marj_c01, marj_c1):
    return {
        "lojistik_l2_c01": {"marj": marj_c01},
        "lojistik_l2_c1": {"marj": marj_c1},
        "random_forest_sigin": {"marj": 1.0},
        "hist_gradient_sigin": {"marj": 1.0},
    }


def test_doygun_modeller_karar_kapisina_girmez():
    karar = m12.karar_ver(_kol(0.0, 0.0), _kol(0.01, 0.02), "HEURISTIK")
    assert karar["hukum"] == "ON_ELEME_ISARET_YOK"
    assert karar["bddk_kapandi"] is False


def test_on_eleme_gecti_ve_zayif_kapilari():
    gecti = m12.karar_ver(_kol(0.0, 0.0), _kol(0.15, 0.01), "HEURISTIK")
    assert gecti["hukum"] == "ON_ELEME_GECTI"
    zayif = m12.karar_ver(_kol(-0.4, -0.4), _kol(-0.24, -0.39), "HEURISTIK")
    assert zayif["hukum"] == "ON_ELEME_ZAYIF"


def test_harness_toleransi_asimetrik_esikleri_uygular():
    kontrol = {
        ad: {
            "tavan_gozlenen": ref["tavan_gozlenen"],
            "tavan_null95": ref["tavan_null95"],
        }
        for ad, ref in m12.REFERANS.items()
    }
    assert all(x["gecti"] for x in m12.harness_dogrula(kontrol).values())
    kontrol["lojistik_l2_c01"]["tavan_null95"] += 1e-4
    with pytest.raises(RuntimeError, match="harness"):
        m12.harness_dogrula(kontrol)
