"""Model 14 DF-B keşifsel karşılaştırmasının sözleşme testleri."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_14_df_b_karsilastirma as karsilastirma  # noqa: E402
import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

MODEL_DIR = Path(__file__).resolve().parents[1] / "data" / "processed" / "model"


def test_df_b_kolu_dondurulmus_model14_sozlesmesini_korur():
    assert karsilastirma.MODEL_ADI == "lojistik_l2_c01"
    assert len(m14.TEST_FEATURELAR) == 14
    assert karsilastirma.ILK_TRAIN_AY_SAYISI == 12
    assert karsilastirma.EMBARGO_AY_SAYISI == 2
    assert str(karsilastirma.KILITLI_TEST_BASLANGIC) == "2025-07"


def test_df_b_kolu_yalniz_uc_kilit_oncesi_origin_uretir():
    originler = karsilastirma.rn.genisleyen_originler(
        karsilastirma.BASLANGIC_AYI,
        karsilastirma.SON_DEGERLENDIRME_AYI,
        ilk_train_ay_sayisi=karsilastirma.ILK_TRAIN_AY_SAYISI,
        embargo_ay_sayisi=karsilastirma.EMBARGO_AY_SAYISI,
    )
    assert [str(x["degerlendirme"]) for x in originler] == [
        "2025-04",
        "2025-05",
        "2025-06",
    ]
    assert all(x["degerlendirme"] < karsilastirma.KILITLI_TEST_BASLANGIC for x in originler)


def test_df_b_gercek_calisma_metrikleri_ve_matrisi_yeniden_uretilir():
    df_b_yolu = MODEL_DIR / "model_07_haftalik_nowcast_df_b_snapshot.csv"
    df_a_yolu = MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv"
    if not df_b_yolu.exists() or not df_a_yolu.exists():
        pytest.skip("Model07 snapshot çıktıları yerelde yok")

    df_b = karsilastirma._snapshot_oku(df_b_yolu.name)
    df_a = karsilastirma._snapshot_oku(df_a_yolu.name)
    birlesik = karsilastirma._df_b_model14_featurelarini_tamamla(df_b, df_a)
    snapshot = m14.feature_hazirla(birlesik)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    tahminler, originler, _ = karsilastirma._tahminleri_uret(snapshot)
    metrik = yd.degerlendir(tahminler["gercek"], tahminler["tahmin"])

    assert len(originler) == 3
    assert len(tahminler) == 12
    assert metrik["accuracy"] == pytest.approx(0.0)
    assert metrik["macro_f1"] == pytest.approx(0.0)
    assert metrik["mcc_gorodkin"] == pytest.approx(-0.6123724356957946)
    assert metrik["confusion_matrix"]["matris"] == [
        [0, 0, 4],
        [4, 0, 0],
        [4, 0, 0],
    ]
