"""Model 14 odakli testler — onkayit (prompts/veri/43_*.md) invaryantlari.

Kapsam: feature formulu, tam feature sayisi, origin/embargo, train-only
preprocessing/fit sayisi, kontrol kolu Model10 ile birebir yeniden uretimi,
kilitli-test (2025-07..2026-06) disi kalma ve terfi kurali invaryantlari.
Agir (gercek veri) testler MODEL_DIR'deki Model07/Model10 ciktilarina
bagimlidir (gitignored); dosyalar yoksa test atlanir (pytest.skip) —
CI/tasima portakliligi icin.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_09_dusuk_kapasiteli_nowcast as m09  # noqa: E402
import model_10_rolling_origin_nowcast as m10  # noqa: E402
import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

MODEL_DIR = Path(__file__).resolve().parents[1] / "data" / "processed" / "model"
SNAPSHOT_YOLU = MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv"


# ---------------------------------------------------------------------------
# 1) Feature formulu
# ---------------------------------------------------------------------------

def test_reel_politika_faizi_formulu_fark_alir():
    df = pd.DataFrame({
        "politika_faizi_lag2ay": [50.0, 45.0, np.nan],
        "tufe_yillik_degisim_lag2ay": [33.0, 40.0, 10.0],
        "usdtry_orta_std": [0.1, 0.2, 0.3],
        "tuketici_guven_endeksi_lag2ay": [80.0, 81.0, 82.0],
        "odmd_otomobil_adet_lag2ay": [1000, 1100, 1200],
        "noter_devir_otomobil_adet_lag2ay": [100, 200, 300],
        "noter_devir_otomobil_adet_lag3ay": [100, 100, 300],
        "noter_devir_otomobil_adet_lag12ay": [90, 90, 90],
        "noter_devir_otomobil_adet_lag13ay": [90, 90, 90],
    })
    sonuc = m14.feature_hazirla(df)
    assert sonuc["reel_politika_faizi_lag2ay"].iloc[0] == pytest.approx(50.0 - 33.0)
    assert sonuc["reel_politika_faizi_lag2ay"].iloc[1] == pytest.approx(45.0 - 40.0)
    assert pd.isna(sonuc["reel_politika_faizi_lag2ay"].iloc[2])


def test_feature_hazirla_eksik_kaynak_kolonda_keyerror():
    df = pd.DataFrame({"politika_faizi_lag2ay": [1.0]})
    with pytest.raises(KeyError):
        m14.feature_hazirla(df)


# ---------------------------------------------------------------------------
# 2) Tam feature sayisi ve gercek yenilik
# ---------------------------------------------------------------------------

def test_kontrol_kolu_tam_10_feature():
    assert len(m14.KONTROL_FEATURELAR) == 10
    assert m14.KONTROL_FEATURELAR == m09.FEATURELAR


def test_yeni_aile_tam_4_feature():
    assert len(m14.YENI_FEATURELAR) == 4


def test_test_kolu_tam_14_feature_ve_ayrik():
    assert len(m14.TEST_FEATURELAR) == 14
    assert m14.TEST_FEATURELAR == m14.KONTROL_FEATURELAR + m14.YENI_FEATURELAR
    assert set(m14.YENI_FEATURELAR).isdisjoint(set(m14.KONTROL_FEATURELAR))


def test_yeni_feature_kaynak_kolonlari_model09da_yok():
    kaynak_kolonlari = {
        "usdtry_orta_std", "tuketici_guven_endeksi_lag2ay",
        "odmd_otomobil_adet_lag2ay", "politika_faizi_lag2ay",
        "tufe_yillik_degisim_lag2ay",
    }
    assert kaynak_kolonlari.isdisjoint(set(m09.FEATURELAR))


# ---------------------------------------------------------------------------
# 3) Origin / embargo yapisi (Model 10 ile birebir)
# ---------------------------------------------------------------------------

def test_origin_yapisi_50_origin_2_ay_embargo():
    import rolling_nowcast as rn
    originler = rn.genisleyen_originler(
        "2019-01", m14.SON_DEGERLENDIRME_AYI, ilk_train_ay_sayisi=24, embargo_ay_sayisi=2
    )
    assert len(originler) == 50
    assert str(originler[-1]["degerlendirme"]) == "2025-04"
    for origin in originler:
        assert len(origin["embargo"]) == 2
        assert origin["embargo"] == [
            origin["degerlendirme"] - 2, origin["degerlendirme"] - 1
        ]


def test_kilitli_test_baslangici_onkayitla_tutarli():
    assert str(m14.KILITLI_TEST_BASLANGIC) == "2025-07"
    assert pd.Period(m14.SON_DEGERLENDIRME_AYI, freq="M") < m14.KILITLI_TEST_BASLANGIC


# ---------------------------------------------------------------------------
# 4) Kilitli-test disi kalma (senteik veri)
# ---------------------------------------------------------------------------

def test_kilitli_test_disla_gelecek_aylari_kaldirir():
    df = pd.DataFrame({
        "hedef_ay": pd.PeriodIndex(
            ["2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2026-06"], freq="M"
        ),
        "deger": range(6),
    })
    guvenli, kilitli_sayisi = m14.kilitli_test_disla(df)
    assert kilitli_sayisi == 3
    assert (guvenli["hedef_ay"] < m14.KILITLI_TEST_BASLANGIC).all()
    assert sorted(guvenli["hedef_ay"].astype(str)) == ["2025-04", "2025-05", "2025-06"]


def test_kilitli_test_disla_hicbir_gelecek_ay_yoksa_sayim_sifir():
    df = pd.DataFrame({"hedef_ay": pd.PeriodIndex(["2020-01", "2020-02"], freq="M")})
    guvenli, kilitli_sayisi = m14.kilitli_test_disla(df)
    assert kilitli_sayisi == 0
    assert len(guvenli) == 2


# ---------------------------------------------------------------------------
# 5) Terfi kapisi invaryantlari (a-d hepsi zorunlu; hafta gerekce olamaz)
# ---------------------------------------------------------------------------

def test_terfi_kapisi_kosullarin_hepsi_saglaninca_terfi_true():
    sonuc = m14.terfi_kosullarini_hesapla(
        delta_mcc_nokta=0.06, delta_mcc_holm_alt_sinir=0.01,
        h0_reddedildi=True, delta_macro_f1_nokta=0.02,
        jackknife_isaret_pozitif=True,
    )
    assert sonuc["terfi"] is True
    assert all(sonuc["kosullar"].values())


@pytest.mark.parametrize("gevseyen_kosul", ["a", "b", "c", "d"])
def test_terfi_kapisi_tek_kosul_bile_gevserse_terfi_false(gevseyen_kosul):
    taban = dict(
        delta_mcc_nokta=0.06, delta_mcc_holm_alt_sinir=0.01,
        h0_reddedildi=True, delta_macro_f1_nokta=0.02,
        jackknife_isaret_pozitif=True,
    )
    if gevseyen_kosul == "a":
        taban["h0_reddedildi"] = False
    elif gevseyen_kosul == "b":
        taban["delta_mcc_nokta"] = 0.0499999
    elif gevseyen_kosul == "c":
        taban["delta_macro_f1_nokta"] = 0.0
    elif gevseyen_kosul == "d":
        taban["jackknife_isaret_pozitif"] = False
    sonuc = m14.terfi_kosullarini_hesapla(**taban)
    assert sonuc["terfi"] is False
    assert sonuc["kosullar"][{
        "a": "a_holm_alt_sinir_pozitif", "b": "b_delta_mcc_en_az_005",
        "c": "c_macro_f1_farki_pozitif", "d": "d_jackknife_isaret_korunuyor",
    }[gevseyen_kosul]] is False


def test_terfi_kapisi_delta_mcc_esik_deger_dahildir():
    sonuc = m14.terfi_kosullarini_hesapla(
        delta_mcc_nokta=0.05, delta_mcc_holm_alt_sinir=0.01,
        h0_reddedildi=True, delta_macro_f1_nokta=0.01,
        jackknife_isaret_pozitif=True,
    )
    assert sonuc["kosullar"]["b_delta_mcc_en_az_005"] is True
    assert sonuc["terfi"] is True


def test_terfi_kapisi_yalniz_dort_kosul_tasir_hafta_giremez():
    sonuc = m14.terfi_kosullarini_hesapla(
        delta_mcc_nokta=0.1, delta_mcc_holm_alt_sinir=0.1,
        h0_reddedildi=True, delta_macro_f1_nokta=0.1,
        jackknife_isaret_pozitif=True,
    )
    assert set(sonuc["kosullar"]) == {
        "a_holm_alt_sinir_pozitif", "b_delta_mcc_en_az_005",
        "c_macro_f1_farki_pozitif", "d_jackknife_isaret_korunuyor",
    }
    import inspect
    parametreler = set(inspect.signature(m14.terfi_kosullarini_hesapla).parameters)
    assert not any("hafta" in p or "week" in p for p in parametreler)


# ---------------------------------------------------------------------------
# 6) Deger-esitlik karsilastirici (dogrula_kontrol_model10_ile) — sentetik
# ---------------------------------------------------------------------------

def test_deger_esit_mi_ic_ice_yapida_kucuk_farki_yakalar():
    a = {"x": {"y": [1.0, 2.0]}, "z": 3}
    b = {"x": {"y": [1.0, 2.0000000001]}, "z": 3}
    assert m14._deger_esit_mi(a, b) is True
    c = {"x": {"y": [1.0, 2.1]}, "z": 3}
    assert m14._deger_esit_mi(a, c) is False


def test_dogrula_kontrol_model10_ile_uyumlu_ve_uyumsuz_durumlari_ayirir():
    taban = {alan: {"ornek": 1.0} for alan in m14.ORTAK_OZET_ALANLARI}
    taban["origin_sayisi"] = 50
    taban["embargo_ay_sayisi"] = 2
    taban["herhangi_terfi"] = False
    ayni = dict(taban)
    sonuc = m14.dogrula_kontrol_model10_ile(taban, ayni)
    assert sonuc["birebir_uyumlu"] is True
    assert sonuc["uyusmazlik"] == []

    farkli = dict(taban)
    farkli["origin_sayisi"] = 49
    sonuc2 = m14.dogrula_kontrol_model10_ile(taban, farkli)
    assert sonuc2["birebir_uyumlu"] is False
    assert "origin_sayisi" in sonuc2["uyusmazlik"]


# ---------------------------------------------------------------------------
# 7) Gercek veriyle agir dogrulama — train-only fit sayisi + kilitli-test disi
#    kalma + kontrol kolu Model10 ile birebir yeniden uretim
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def kontrol_gercek_calisma():
    if not SNAPSHOT_YOLU.exists():
        pytest.skip("Model07 gercek veri ciktisi yerelde yok (gitignored) — atlaniyor")
    ham = pd.read_csv(SNAPSHOT_YOLU)
    ham["hedef_ay"] = pd.PeriodIndex(ham["hedef_ay"], freq="M")
    guvenli, kilitli_disarida = m14.kilitli_test_disla(ham)
    snapshot = m14.feature_hazirla(guvenli)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    ozet, tahmin_df, originler = m14.kol_calistir(snapshot, m14.KONTROL_FEATURELAR, "kontrol_10_feature")
    model10_tahmin, model10_originler, model10_denetim = m10._rolling_tahminleri(snapshot)
    return {
        "ozet": ozet, "tahmin_df": tahmin_df, "originler": originler,
        "kilitli_disarida": kilitli_disarida,
        "model10_tahmin": model10_tahmin,
        "model10_originler": model10_originler,
        "model10_denetim": model10_denetim,
    }


def test_kontrol_kolu_train_only_fit_sayisi_50_ve_200(kontrol_gercek_calisma):
    denetim = kontrol_gercek_calisma["ozet"]["assertion_denetimi"]
    assert denetim == {"on_isleme_fit_sayisi": 50, "model_fit_sayisi": 200}


def test_kontrol_kolu_hicbir_origin_kilitli_test_ayina_dokunmuyor(kontrol_gercek_calisma):
    for origin in kontrol_gercek_calisma["originler"]:
        assert origin["degerlendirme"] < m14.KILITLI_TEST_BASLANGIC
        assert all(ay < m14.KILITLI_TEST_BASLANGIC for ay in origin["train"])
        assert all(ay < m14.KILITLI_TEST_BASLANGIC for ay in origin["embargo"])
    assert kontrol_gercek_calisma["ozet"]["degerlendirme_ay_araligi"][-1] == "2025-04"


def test_kontrol_kolu_guncel_model10_kod_yoluyla_birebir_uyumlu(kontrol_gercek_calisma):
    dogrulama = m14.dogrula_kontrol_tahmin_model10_ile(
        kontrol_gercek_calisma["tahmin_df"], kontrol_gercek_calisma["model10_tahmin"]
    )
    assert dogrulama["birebir_uyumlu"] is True
    assert dogrulama["satir_sayisi_kontrol"] == dogrulama["satir_sayisi_referans"]
    assert len(kontrol_gercek_calisma["model10_originler"]) == 50
    assert kontrol_gercek_calisma["model10_denetim"] == {
        "on_isleme_fit_sayisi": 50, "model_fit_sayisi": 200,
    }
