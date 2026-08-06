"""
scripts/model/yon_degerlendirme.py icin pytest testleri.

Kapsam: sabit +-%5 sinirin stable olmasi, gelecek takvim ayi eslemesi, split
aylarinin cakismamasi ve purge, ay agirliklarinin esit toplami, bilinmeyen/
eksik etiket reddi, mukemmel/hep-stable metrik, olasilik toplami dogrulamasi.
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import yon_degerlendirme as yd  # noqa: E402


# --- yon_etiketi: sabit +-%5 sinir davranisi -------------------------------

def test_yon_etiketi_tam_sinir_kapali_araliktir_stable():
    assert yd.yon_etiketi(5.0, esik_yuzde=5.0) == "stable"
    assert yd.yon_etiketi(-5.0, esik_yuzde=5.0) == "stable"
    assert yd.yon_etiketi(0.0, esik_yuzde=5.0) == "stable"


def test_yon_etiketi_sinir_disi_up_down():
    assert yd.yon_etiketi(5.0 + 1e-9, esik_yuzde=5.0) == "up"
    assert yd.yon_etiketi(-5.0 - 1e-9, esik_yuzde=5.0) == "down"
    assert yd.yon_etiketi(20.0, esik_yuzde=5.0) == "up"
    assert yd.yon_etiketi(-20.0, esik_yuzde=5.0) == "down"


def test_yon_etiketi_nan_eksik_doner():
    assert yd.yon_etiketi(None, esik_yuzde=5.0) == "eksik"
    assert yd.yon_etiketi(np.nan, esik_yuzde=5.0) == "eksik"


# --- sonraki_ay_etiketleri: gelecek takvim ayi eslemesi ---------------------

def test_sonraki_ay_etiketleri_gelecek_takvim_ayi_eslemesi():
    index = pd.period_range("2024-01", "2024-06", freq="M")
    # M -> M+1 degisimleri: Ocak->Subat +%10 (up), Subat->Mart -%10 (down),
    # Mart->Nisan +%1 (stable), Nisan->Mayis +%6 (up), Mayis->Haziran +%2 (stable);
    # Haziran son ay - M+1 (Temmuz) seride yok -> eksik.
    hacim = pd.Series([100, 110, 99, 100.0, 106, 106 * 1.02], index=index)

    sonuc = yd.sonraki_ay_etiketleri(hacim, esik_yuzde=5.0)

    assert sonuc["2024-01"] == "up"
    assert sonuc["2024-02"] == "down"
    assert sonuc["2024-03"] == "stable"
    assert sonuc["2024-04"] == "up"
    assert sonuc["2024-05"] == "stable"
    assert sonuc["2024-06"] == "eksik"  # son ay: M+1 (2024-07) seride yok


def test_sonraki_ay_etiketleri_son_ay_her_zaman_eksik():
    index = pd.period_range("2020-01", "2020-12", freq="M")
    hacim = pd.Series(np.linspace(100, 200, 12), index=index)
    sonuc = yd.sonraki_ay_etiketleri(hacim, esik_yuzde=5.0)
    assert sonuc.iloc[-1] == "eksik"


def test_sonraki_ay_etiketleri_takvim_bosluguna_karsi_pozisyonel_degil_ay_bazli():
    # 2024-03 index'te YOK (takvim bosluğu) - shift'in POZISYONEL degil
    # gercek TAKVIM AYI farkina gore calistigini kanitlar.
    index = pd.PeriodIndex(["2024-01", "2024-02", "2024-04", "2024-05"], freq="M")
    hacim = pd.Series([100, 105, 200, 220.0], index=index)
    sonuc = yd.sonraki_ay_etiketleri(hacim, esik_yuzde=5.0)
    # 2024-02 -> 2024-03 (index'te yok, NaN) -> eksik (pozisyonel olsaydi 2024-04'e atlar, "up" olurdu)
    assert sonuc["2024-02"] == "eksik"


# --- ay_agirligi: esit ay agirligi toplami ----------------------------------

def test_ay_agirligi_gunluk_satirlar_toplami_bir():
    ay = pd.Period("2024-02", freq="M")  # artik yil, 29 gun
    agirlik = yd.ay_agirligi(ay)
    assert agirlik == pytest.approx(1.0 / 29.0)
    assert agirlik * 29 == pytest.approx(1.0)

    ay2 = pd.Period("2023-04", freq="M")  # 30 gun
    assert yd.ay_agirligi(ay2) * 30 == pytest.approx(1.0)


def test_ay_agirligi_farkli_ay_uzunluklarinda_toplam_esit_kalir():
    aylar_30_gun = pd.Period("2024-04", freq="M")
    aylar_31_gun = pd.Period("2024-05", freq="M")
    toplam_30 = yd.ay_agirligi(aylar_30_gun) * 30
    toplam_31 = yd.ay_agirligi(aylar_31_gun) * 31
    assert toplam_30 == pytest.approx(toplam_31)
    assert toplam_30 == pytest.approx(1.0)


# --- uc_parcali_split_olustur: cakisma + purge dogrulamasi ------------------

def test_split_gecerli_spec_hatasiz_kurulur():
    sonuc = yd.uc_parcali_split_olustur(
        "2018-01", "2024-03", "2024-04",
        "2024-05", "2025-04", "2025-05",
        "2025-06", "2026-05",
    )
    assert len(sonuc["train"]) == 75
    assert len(sonuc["validation"]) == 12
    assert len(sonuc["test"]) == 12
    assert sonuc["purge1"] == [pd.Period("2024-04", freq="M")]
    assert sonuc["purge2"] == [pd.Period("2025-05", freq="M")]


def test_split_cakisan_aylar_reddedilir():
    with pytest.raises(ValueError, match="cakisiyor"):
        yd.uc_parcali_split_olustur(
            "2018-01", "2024-04", "2024-04",  # train, purge1 ile CAKISIYOR (2024-04)
            "2024-05", "2025-04", "2025-05",
            "2025-06", "2026-05",
        )


def test_split_purge_eksikse_reddedilir():
    with pytest.raises(ValueError, match="ardisik degil"):
        yd.uc_parcali_split_olustur(
            "2018-01", "2024-03", "2024-04",
            "2024-06", "2025-04", "2025-05",  # validation 2024-06'dan basliyor, purge1 sonrasi (2024-05) atlaniyor
            "2025-06", "2026-05",
        )


def test_split_bos_kume_reddedilir():
    with pytest.raises(ValueError, match="bos olamaz"):
        yd.uc_parcali_split_olustur(
            "2018-01", "2017-12", "2024-04",  # train bos (bitis < baslangic)
            "2024-05", "2025-04", "2025-05",
            "2025-06", "2026-05",
        )


# --- olasilik toplami / karar yardimcilari ----------------------------------

def test_olasiliklari_dogrula_gecerli_toplam_kabul_edilir():
    yd.olasiliklari_dogrula(0.2, 0.3, 0.5)  # hata firlatmamali


def test_olasiliklari_dogrula_toplam_bir_degilse_reddedilir():
    with pytest.raises(ValueError, match="toplam"):
        yd.olasiliklari_dogrula(0.2, 0.3, 0.6)


def test_olasiliklari_dogrula_aralik_disi_deger_reddedilir():
    with pytest.raises(ValueError, match="araliginda"):
        yd.olasiliklari_dogrula(-0.1, 0.5, 0.6)


def test_tahmin_sinifi_ve_guven_dogru_sinifi_ve_guveni_dondurur():
    sinif, guven = yd.tahmin_sinifi_ve_guven(0.1, 0.15, 0.75)
    assert sinif == "up"
    assert guven == pytest.approx(0.75)


# --- sinif_agirliklari_hesapla: balanced (ters-frekans) sinif agirligi ------

def test_sinif_agirliklari_esit_sinif_sayisinda_hepsi_bir():
    etiketler = ["down", "stable", "up"] * 4  # her sinif esit sayida (12/3=4)
    sonuc = yd.sinif_agirliklari_hesapla(etiketler)
    for sinif in yd.FIXED_LABEL_ORDER:
        assert sonuc[sinif] == pytest.approx(1.0)


def test_sinif_agirliklari_dengesiz_agirliksiz_ters_frekansla_orantili():
    # down: 1, stable: 2, up: 6 -> toplam 9, n_sinif=3
    etiketler = ["down"] * 1 + ["stable"] * 2 + ["up"] * 6
    sonuc = yd.sinif_agirliklari_hesapla(etiketler)
    assert sonuc["down"] == pytest.approx(9 / (3 * 1))
    assert sonuc["stable"] == pytest.approx(9 / (3 * 2))
    assert sonuc["up"] == pytest.approx(9 / (3 * 6))
    # az gorulen sinif (down) en yuksek agirligi alir
    assert sonuc["down"] > sonuc["stable"] > sonuc["up"]


def test_sinif_agirliklari_agirlikli_frekans_ay_agirligi_birimini_kullanir():
    # ay_agirligi ile uretilmis kesirli agirliklar (pseudo-replikasyon
    # duzeltmesiyle tutarli) - frekans SATIR sayisi degil AGIRLIK toplamidir.
    etiketler = ["down", "down", "up"]
    agirliklar = [0.5, 0.5, 1.0]  # down toplam agirlik=1.0, up toplam agirlik=1.0
    sonuc = yd.sinif_agirliklari_hesapla(etiketler, agirliklar=agirliklar,
                                          label_sirasi=["down", "up"])
    assert sonuc["down"] == pytest.approx(sonuc["up"])


def test_sinif_agirliklari_egitimde_hic_gorulmeyen_sinif_reddedilir():
    etiketler = ["down", "down", "up"]
    with pytest.raises(ValueError, match="hic gorulmedi"):
        yd.sinif_agirliklari_hesapla(etiketler)  # "stable" hic yok


def test_sinif_agirliklari_uzunluk_uyumsuzlugu_reddedilir():
    with pytest.raises(ValueError, match="ayni uzunlukta"):
        yd.sinif_agirliklari_hesapla(["down", "up"], agirliklar=[1.0])


def test_sinif_agirliklari_bilinmeyen_etiket_reddedilir():
    with pytest.raises(ValueError, match="Bilinmeyen"):
        yd.sinif_agirliklari_hesapla(["down", "sideways", "up"])


# --- degerlendir: mukemmel / hep-stable / gecersiz etiket -------------------

def test_mukemmel_tahmin_tum_metrikler_maksimum():
    y = ["down", "stable", "up", "up", "down", "stable", "up", "stable", "down", "up"]
    sonuc = yd.degerlendir(y, y)
    assert sonuc["mcc_gorodkin"] == pytest.approx(1.0)
    assert sonuc["macro_f1"] == pytest.approx(1.0)
    assert sonuc["accuracy"] == pytest.approx(1.0)
    assert sonuc["n"] == len(y)
    for etiket in yd.FIXED_LABEL_ORDER:
        assert sonuc["per_class"][etiket]["precision"] == pytest.approx(1.0)
        assert sonuc["per_class"][etiket]["recall"] == pytest.approx(1.0)
    matris = np.array(sonuc["confusion_matrix"]["matris"])
    assert np.array_equal(matris, np.diag(np.diag(matris)))
    assert matris.sum() == len(y)


def test_hep_stable_dengesiz_ornek_mcc_sifir_degil_uydurma_bilgi():
    y_gercek = ["down", "stable", "up", "stable", "down", "stable", "up", "stable", "stable", "down"]
    y_tahmin = ["stable"] * len(y_gercek)

    sonuc = yd.degerlendir(y_gercek, y_tahmin)

    # tahminin varyansi sifir oldugunda MCC matematiksel olarak 0'dir (sinyal yok)
    assert sonuc["mcc_gorodkin"] == pytest.approx(0.0)
    beklenen_dogruluk = y_gercek.count("stable") / len(y_gercek)
    assert sonuc["accuracy"] == pytest.approx(beklenen_dogruluk)
    # tahmin edilmeyen siniflarin recall'u 0 olmali (uydurma/gizlenmis basari yok)
    assert sonuc["per_class"]["up"]["recall"] == pytest.approx(0.0)
    assert sonuc["per_class"]["down"]["recall"] == pytest.approx(0.0)
    assert sonuc["per_class"]["stable"]["recall"] == pytest.approx(1.0)
    assert np.isfinite(sonuc["macro_f1"])


def test_bilinmeyen_etiket_reddedilir():
    y_gercek = ["down", "stable", "up"]
    y_tahmin = ["down", "sideways", "up"]  # "sideways" fixed sette yok
    with pytest.raises(ValueError, match="Bilinmeyen"):
        yd.degerlendir(y_gercek, y_tahmin)


def test_degerlendir_agirlikli_ay_hizali_tekrari_esitler():
    # 2 ay: biri 2 kez, digeri 1 kez tekrarlanmis (ay-hizali gunluk tekrar simulasyonu).
    # Agirliksiz degerlendirmede tekrar sayisi metrikleri carpitir; agirlikli
    # degerlendirmede (agirlik=1/tekrar) sonuc, TEKRARSIZ (ay-bazli) sonuçla ayni olmalidir.
    y_gercek_gunluk = ["up", "up", "down"]
    y_tahmin_gunluk = ["up", "up", "stable"]
    agirlik_gunluk = [0.5, 0.5, 1.0]

    sonuc_agirlikli = yd.degerlendir(y_gercek_gunluk, y_tahmin_gunluk, agirliklar=agirlik_gunluk)
    sonuc_aybazli = yd.degerlendir(["up", "down"], ["up", "stable"])

    assert sonuc_agirlikli["accuracy"] == pytest.approx(sonuc_aybazli["accuracy"])
    assert sonuc_agirlikli["mcc_gorodkin"] == pytest.approx(sonuc_aybazli["mcc_gorodkin"])
    assert sonuc_agirlikli["macro_f1"] == pytest.approx(sonuc_aybazli["macro_f1"])
    assert sonuc_agirlikli["agirlikli_mi"] is True
    assert sonuc_aybazli["agirlikli_mi"] is False


def test_eksik_etiket_degerlendirmede_reddedilir():
    y_gercek = ["down", "eksik", "up"]
    y_tahmin = ["down", "stable", "up"]
    with pytest.raises(ValueError, match="Bilinmeyen"):
        yd.degerlendir(y_gercek, y_tahmin)


# --- sinif_agirliklari_hesapla: ek senaryolar (agirliksiz cagri) -----------

def test_sinif_agirliklari_azinlik_sinif_daha_yuksek_carpan_alir():
    # down: 1, stable: 2, up: 9 -> azinlik (down) en yuksek, cogunluk (up) en dusuk carpan
    etiketler = ["down"] + ["stable"] * 2 + ["up"] * 9
    agirliklar = yd.sinif_agirliklari_hesapla(etiketler)
    assert agirliklar["down"] > agirliklar["stable"] > agirliklar["up"]
    # frekans-agirlikli ortalama tam 1.0 kalmali (toplam agirlik carpitilmaz)
    n = len(etiketler)
    agirlikli_ortalama = sum(agirliklar[e] for e in etiketler) / n
    assert agirlikli_ortalama == pytest.approx(1.0)


def test_sinif_agirliklari_gorulmeyen_sinif_reddedilir():
    etiketler = ["down", "down", "up"]  # 'stable' hic yok
    with pytest.raises(ValueError, match="stable"):
        yd.sinif_agirliklari_hesapla(etiketler)


def test_sinif_agirliklari_bos_liste_reddedilir():
    with pytest.raises(ValueError, match="bos"):
        yd.sinif_agirliklari_hesapla([])


# --- en_iyi_aday_sec: mcc -> macro_f1 -> stable recall sirali secim --------

def test_en_iyi_aday_sec_mcc_farkli_ise_mcc_kazanir():
    adaylar = {
        "a": {"mcc_gorodkin": 0.5, "macro_f1": 0.1, "per_class": {"stable": {"recall": 0.0}}},
        "b": {"mcc_gorodkin": 0.6, "macro_f1": 0.05, "per_class": {"stable": {"recall": 0.0}}},
    }
    assert yd.en_iyi_aday_sec(adaylar) == "b"


def test_en_iyi_aday_sec_mcc_esitse_macro_f1_karar_verir():
    adaylar = {
        "a": {"mcc_gorodkin": 0.4, "macro_f1": 0.3, "per_class": {"stable": {"recall": 1.0}}},
        "b": {"mcc_gorodkin": 0.4, "macro_f1": 0.5, "per_class": {"stable": {"recall": 0.0}}},
    }
    assert yd.en_iyi_aday_sec(adaylar) == "b"


def test_en_iyi_aday_sec_mcc_ve_f1_esitse_stable_recall_karar_verir():
    adaylar = {
        "a": {"mcc_gorodkin": 0.4, "macro_f1": 0.3, "per_class": {"stable": {"recall": 0.2}}},
        "b": {"mcc_gorodkin": 0.4, "macro_f1": 0.3, "per_class": {"stable": {"recall": 0.6}}},
    }
    assert yd.en_iyi_aday_sec(adaylar) == "b"


def test_en_iyi_aday_sec_tam_esitlikte_ilk_aday_kazanir():
    adaylar = {
        "ilk": {"mcc_gorodkin": 0.4, "macro_f1": 0.3, "per_class": {"stable": {"recall": 0.2}}},
        "ikinci": {"mcc_gorodkin": 0.4, "macro_f1": 0.3, "per_class": {"stable": {"recall": 0.2}}},
    }
    assert yd.en_iyi_aday_sec(adaylar) == "ilk"


def test_en_iyi_aday_sec_bos_sozluk_reddedilir():
    with pytest.raises(ValueError, match="bos"):
        yd.en_iyi_aday_sec({})
