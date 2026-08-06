from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import rolling_nowcast as rn  # noqa: E402


def test_genisleyen_origin_iki_ay_embargo_kurulur():
    o = rn.genisleyen_originler(
        "2019-01", "2021-04", ilk_train_ay_sayisi=24, embargo_ay_sayisi=2
    )
    assert len(o) == 2
    assert str(o[0]["train"][-1]) == "2020-12"
    assert [str(x) for x in o[0]["embargo"]] == ["2021-01", "2021-02"]
    assert str(o[0]["degerlendirme"]) == "2021-03"
    assert len(o[1]["train"]) == 25


def test_2019_2025_araligi_50_origin_verir():
    o = rn.genisleyen_originler(
        "2019-01", "2025-04", ilk_train_ay_sayisi=24, embargo_ay_sayisi=2
    )
    assert len(o) == 50
    assert str(o[-1]["degerlendirme"]) == "2025-04"


def test_bootstrap_deterministik_ve_mukemmel_tahmin_ci_ustte():
    y = ["down", "stable", "up"] * 10
    a = rn.bootstrap_metrik(y, y, tekrar=100, seed=7)
    b = rn.bootstrap_metrik(y, y, tekrar=100, seed=7)
    assert a == b
    assert a["mcc_nokta"] == pytest.approx(1.0)
    assert a["mcc_ci95"][0] == pytest.approx(1.0)


def test_bootstrap_az_gozlem_reddedilir():
    with pytest.raises(ValueError, match="en az iki"):
        rn.bootstrap_metrik(["up"], ["up"], tekrar=100)


def test_esli_fark_esit_tahminde_sifirdir():
    y = ["down", "stable", "up"] * 10
    sonuc = rn.bootstrap_mcc_farki(y, y, y, tekrar=100, seed=3)
    assert sonuc["mcc_farki_nokta"] == pytest.approx(0.0)
    assert sonuc["mcc_farki_ci95"] == pytest.approx([0.0, 0.0])


def test_hareketli_blok_indeksleri_ardisik_dortlu_kurulur():
    idx = rn.hareketli_blok_indeksleri(50, tekrar=100, blok_uzunlugu=4, seed=1)
    assert idx.shape == (100, 50)
    assert (idx[:, 1:4] - idx[:, :3] == 1).all()


def test_ortak_indeks_tum_yaklasimlara_ayni_cekilisi_uygular():
    import numpy as np
    gercek = np.array([["down", "down", "down", "down"],
                       ["stable", "stable", "stable", "stable"],
                       ["up", "up", "up", "up"],
                       ["down", "down", "down", "down"]], dtype=object)
    idx = rn.hareketli_blok_indeksleri(4, tekrar=100, blok_uzunlugu=2, seed=2)
    sonuc = rn.ortak_indeksli_metrik_dagilimlari(
        gercek, {"a": gercek.copy(), "b": gercek.copy()}, idx
    )
    assert (sonuc["dagilimlar"]["a"]["mcc"] == sonuc["dagilimlar"]["b"]["mcc"]).all()
    assert set(sonuc["tahmin_dejenere_cekilis_orani"]) == {"a", "b"}


def test_holm_bonferroni_red_zincirini_ilk_basarisizlikta_keser():
    h = rn.holm_bonferroni({"a": 0.001, "b": 0.02, "c": 0.021, "d": 0.9})
    assert h["a"]["h0_reddedildi"] is True
    assert h["b"]["h0_reddedildi"] is False
    assert h["c"]["h0_reddedildi"] is False


def test_vektor_metrikleri_sklearn_referansiyla_esdeger():
    import numpy as np
    import yon_degerlendirme as yd
    gercek = np.array((["down", "stable", "up", "down"] * 8), dtype=object).reshape(8, 4)
    tahmin = np.array((["down", "up", "up", "stable"] * 8), dtype=object).reshape(8, 4)
    idx = rn.iid_indeksleri(8, tekrar=100, seed=9)
    sonuc = rn.ortak_indeksli_metrik_dagilimlari(gercek, {"m": tahmin}, idx)
    for i in (0, 17, 99):
        ref = yd.degerlendir(gercek[idx[i]].reshape(-1), tahmin[idx[i]].reshape(-1))
        assert sonuc["dagilimlar"]["m"]["mcc"][i] == pytest.approx(ref["mcc_gorodkin"])
        assert sonuc["dagilimlar"]["m"]["macro_f1"][i] == pytest.approx(ref["macro_f1"])
