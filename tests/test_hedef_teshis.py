from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import hedef_teshis as ht  # noqa: E402


def test_permutasyon_null_sabit_seedle_deterministik():
    x = ["a", "b"] * 15
    y = ["down", "stable", "up"] * 10
    assert ht.permutasyon_cramer(x, y, tekrar=100, seed=9) == ht.permutasyon_cramer(
        x, y, tekrar=100, seed=9
    )


def test_oracle_doygunluk_ortalama_n8_altini_reddeder():
    durum = [f"s{i % 7}" for i in range(50)]
    y = ["down", "stable", "up", "up", "down"] * 10
    with pytest.raises(ValueError, match="doygunluk"):
        ht.oracle_durum_tahmini(durum, y)


def test_oracle_durum_tahmini_in_sample_modu_kullanir():
    durum = ["a"] * 10 + ["b"] * 10
    y = ["up"] * 8 + ["down"] * 2 + ["stable"] * 9 + ["up"]
    pred, meta = ht.oracle_durum_tahmini(durum, y)
    assert pred[:10] == ["up"] * 10
    assert pred[10:] == ["stable"] * 10
    assert meta["ortalama_hucre_n"] == 10


def test_bilgi_maskesi_m1_ve_cari_targeti_reddeder():
    with pytest.raises(ValueError, match="M-1/M"):
        ht.bilgi_maskesini_dogrula(["noter_devir_otomobil_adet_lag1ay"])
    with pytest.raises(ValueError, match="M-1/M"):
        ht.bilgi_maskesini_dogrula(["noter_devir_otomobil_adet"])
    ht.bilgi_maskesini_dogrula(["noter_devir_otomobil_adet_lag2ay", "usdtry_orta_son"])


def test_oracle_null_cifti_ve_hucre_bilgisi_doner():
    durum = ["a"] * 10 + ["b"] * 10 + ["c"] * 10
    y = ["down"] * 10 + ["stable"] * 10 + ["up"] * 10
    sonuc = ht.oracle_durum_null(durum, y, tekrar=100, seed=4)
    assert sonuc["tavan_gozlenen"] == pytest.approx(1.0)
    assert sonuc["null_tekrar"] == 100
    assert sonuc["minimum_hucre_n"] == 10


def test_gecis_orient_index_satirlarin_toplamini_korumaya_elverislidir():
    import pandas as pd
    tablo = pd.DataFrame([[1, 2], [3, 4]], index=["once_a", "once_b"],
                         columns=["cari_a", "cari_b"])
    kayit = tablo.div(tablo.sum(axis=1), axis=0).to_dict(orient="index")
    assert sum(kayit["once_a"].values()) == pytest.approx(1.0)
    assert sum(kayit["once_b"].values()) == pytest.approx(1.0)
