"""Model 18 odaklı testler — ön-kayıt (prompts/veri/48_*.md) invaryantları.

Kapsam: eğitim sınırının kilitli dönemi yapısal olarak üretememesi, gelecek
satırın etiketsiz inşası (ham lag ≠ etiket ayrımı), append-only/idempotent
defterler, N<12 terminal reddi ve Model 14 hareketli-blok kapısı.

Tamamı SENTETİK ve hızlıdır — hiçbir gerçek yerel CSV'ye bağımlı değildir.
En sonda, gerçek Model07 çıktısına bağımlı TEK bir isteğe bağlı/ayrı duman
testi vardır (dosyalar yoksa `pytest.skip`).
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "model"))
import model_18_gerceklesme_kaydet as m18g  # noqa: E402
import model_18_ileri_izleme as m18  # noqa: E402
import model_18_terminal_degerlendirme as m18t  # noqa: E402
import haftalik_aylik_nowcast as hn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

MODEL_DIR = Path(__file__).resolve().parents[1] / "data" / "processed" / "model"
GERCEK_SNAPSHOT_YOLU = MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv"


# ---------------------------------------------------------------------------
# Sentetik veri üretici — tüm testler bunu paylaşır (hızlı, gerçek veri yok)
# ---------------------------------------------------------------------------

def _ay_indeksi(ay: pd.Period) -> int:
    return (ay.year - 2015) * 12 + ay.month


def _sentetik_df_a_ve_karisik(baslangic="2017-01-01", bitis="2026-08-10"):
    """Model07/Model18'in ihtiyaç duyduğu tüm sütunları taşıyan, deterministik
    (rastgelesiz), günlük bir sentetik df_a + karisik çifti üretir. Target,
    gerçekçi biçimde yalnız 2026-06'ya kadar doludur (2026-07+ NaN — henüz
    yayımlanmamış); kilitli aralık (2025-07..2026-06) İÇİN GERÇEK (NaN
    olmayan) değerler taşır — tam da gerçek repo verisindeki durum budur."""
    gunler = pd.date_range(baslangic, bitis, freq="D")
    aylar = gunler.to_period("M")
    benzersiz_aylar = aylar.unique()
    son_dolu_ay = pd.Period("2026-06", freq="M")

    def ay_serisi(katsayi, taban):
        degerler = {ay: taban + katsayi * _ay_indeksi(ay) for ay in benzersiz_aylar}
        return pd.Series([degerler[ay] for ay in aylar], index=gunler)

    target_serisi = ay_serisi(15.0, 1000.0)
    target_serisi[aylar > son_dolu_ay] = np.nan

    df_a = pd.DataFrame({
        "tarih": gunler.strftime("%Y-%m-%d"),
        m18.m07.TARGET: target_serisi.to_numpy(),
        "usdtry_orta": np.linspace(10.0, 40.0, len(gunler)),
        "tufe_aylik_degisim": ay_serisi(0.01, 2.0).to_numpy(),
        "tufe_yillik_degisim": ay_serisi(0.05, 30.0).to_numpy(),
        "odmd_otomobil_adet": ay_serisi(100.0, 50000.0).to_numpy(),
        "tuketici_guven_endeksi": ay_serisi(0.02, 75.0).to_numpy(),
    })
    karisik = pd.DataFrame({
        "tarih": gunler.strftime("%Y-%m-%d"),
        "eurtry_orta": np.linspace(11.0, 44.0, len(gunler)),
        "otv_event_gunu_mu": 0,
        "faiz_referans_ay": aylar.astype(str),
        "tasit_kredisi_faiz": ay_serisi(0.03, 40.0).to_numpy(),
        "politika_faizi": ay_serisi(0.03, 45.0).to_numpy(),
    })
    return df_a, karisik


@pytest.fixture(scope="module")
def sentetik_ham():
    return _sentetik_df_a_ve_karisik()


@pytest.fixture(scope="module")
def sentetik_birlesmis(sentetik_ham):
    df_a, karisik = sentetik_ham
    return m18._df_a_birlestir(df_a, karisik, kesim_tarihi=None)


# ---------------------------------------------------------------------------
# 1) Eğitim sınırı — kilitli dönem yapısal olarak üretilemez
# ---------------------------------------------------------------------------

def test_egitim_sabitleri_onkayitla_tutarli():
    assert m18.EGITIM_KESIM_TARIHI == pd.Timestamp("2025-04-30")
    assert m18.ILK_EGITIM_AYI == pd.Period("2019-01", freq="M")
    assert m18.SON_EGITIM_AYI == pd.Period("2025-04", freq="M")


def test_egitim_snapshotu_kilitli_ay_uretemez_yapisal(sentetik_ham):
    """KRİTİK: ham veri kilitli dönem için GERÇEK target taşısa bile (yukarıdaki
    fixture tam olarak bunu yapıyor), eğitim snapshot'ında hedef_ay hiçbir
    zaman 2025-04'ü geçemez."""
    df_a, karisik = sentetik_ham
    egitim_df = m18.egitim_snapshotu_kur(df_a, karisik)
    assert egitim_df["hedef_ay"].max() == m18.SON_EGITIM_AYI
    assert egitim_df["hedef_ay"].min() == m18.ILK_EGITIM_AYI
    assert (egitim_df["hedef_ay"] <= m18.SON_EGITIM_AYI).all()
    # Kilitli/embargo aylarindan tek satir bile yok.
    kilitli_veya_embargo = egitim_df["hedef_ay"] >= pd.Period("2025-05", freq="M")
    assert not kilitli_veya_embargo.any()


def test_egitim_snapshotu_etiket_fonksiyonu_kilitli_veriye_hic_ulasmiyor(sentetik_ham, monkeypatch):
    """`hn.ay_sonu_nowcast_etiketleri`ye giden serinin PeriodIndex'i her
    çağrıda 2025-04'ü aşarsa test kırılır -- yapısal kesmenin gerçekten işe
    yaradığının kanıtı (yalnızca çıktıyı filtrelemediğimizin kanıtı)."""
    df_a, karisik = sentetik_ham
    orijinal = hn.ay_sonu_nowcast_etiketleri

    def gozetlenen(aylik_hacim, esik_yuzde=5.0):
        assert aylik_hacim.index.max() <= m18.SON_EGITIM_AYI, (
            "ay_sonu_nowcast_etiketleri kilitli/embargo donemi iceren bir "
            "seriyle cagrildi"
        )
        return orijinal(aylik_hacim, esik_yuzde)

    monkeypatch.setattr(hn, "ay_sonu_nowcast_etiketleri", gozetlenen)
    m18.egitim_snapshotu_kur(df_a, karisik)


def test_egitim_snapshotu_feature_tamligi(sentetik_ham):
    df_a, karisik = sentetik_ham
    egitim_df = m18.egitim_snapshotu_kur(df_a, karisik)
    eksik = [c for c in m18.m14.TEST_FEATURELAR if c not in egitim_df.columns]
    assert eksik == []
    assert egitim_df["etiket"].isin(yd.FIXED_LABEL_ORDER).all()


# ---------------------------------------------------------------------------
# 2) Gelecek satır — etiketsiz inşa, ham-lag ≠ etiket ayrımı
# ---------------------------------------------------------------------------

def test_gelecek_kesit_etiket_sabit_eksik(sentetik_birlesmis):
    satir = m18.gelecek_kesit_satiri_uret(sentetik_birlesmis, "2026-08-02", "2026-08")
    assert satir["etiket"] == "eksik"


def test_gelecek_kesit_haftalik_snapshot_uret_ve_etiketleme_hic_cagrilmiyor(
    sentetik_birlesmis, monkeypatch
):
    """KRİTİK: hem haftalik_snapshot_uret hem ay_sonu_nowcast_etiketleri
    çağrılırsa exception fırlatacak şekilde monkeypatch edilir; gelecek satır
    üretimi hatasız tamamlanmalı (yani ikisi de HİÇ tetiklenmemeli). Kilitli
    aralıktaki (2025-07..2026-06) ham lag12/13 target değerleri doğru
    okunur ve bu, hiçbir sınıflandırma çağrısı gerektirmez."""
    def patlat(*a, **k):
        raise AssertionError("bu fonksiyon gelecek-satir insasinda cagrilmamali")

    monkeypatch.setattr(hn, "ay_sonu_nowcast_etiketleri", patlat)
    monkeypatch.setattr(hn, "haftalik_snapshot_uret", patlat)

    satir = m18.gelecek_kesit_satiri_uret(sentetik_birlesmis, "2026-08-02", "2026-08")

    # lag12 -> 2025-08, lag13 -> 2025-07 (ikisi de kilitli araliktaki HAM
    # target degerleri) -- formule gore beklenen sayisal degerlerle eslesir.
    beklenen_2025_08 = 1000.0 + 15.0 * _ay_indeksi(pd.Period("2025-08", freq="M"))
    beklenen_2025_07 = 1000.0 + 15.0 * _ay_indeksi(pd.Period("2025-07", freq="M"))
    assert satir[f"{m18.m07.TARGET}_lag12ay"] == pytest.approx(beklenen_2025_08)
    assert satir[f"{m18.m07.TARGET}_lag13ay"] == pytest.approx(beklenen_2025_07)
    assert satir["etiket"] == "eksik"


def test_gelecek_kesit_ozellik_cercevesi_14_feature_tamamlar(sentetik_birlesmis):
    satir = m18.gelecek_kesit_satiri_uret(sentetik_birlesmis, "2026-08-02", "2026-08")
    ozellik_df = m18.satiri_ozellik_cercevesine_donustur(satir)
    for kolon in m18.m14.TEST_FEATURELAR:
        assert kolon in ozellik_df.columns
    assert len(ozellik_df) == 1


def test_gelecek_kesit_pazar_disi_kesit_reddedilir(sentetik_birlesmis):
    with pytest.raises(ValueError, match="pazar"):
        m18.gelecek_kesit_satiri_uret(sentetik_birlesmis, "2026-08-03", "2026-08")


def test_gelecek_kesit_hedef_ay_disi_kesit_reddedilir(sentetik_birlesmis):
    with pytest.raises(ValueError, match="disinda"):
        m18.gelecek_kesit_satiri_uret(sentetik_birlesmis, "2026-08-02", "2026-09")


def test_gelecek_kesit_zaten_gerceklesmis_ay_reddedilir(sentetik_birlesmis):
    with pytest.raises(RuntimeError, match="STOP_ONLY_IF madde 4"):
        m18.gelecek_kesit_satiri_uret(sentetik_birlesmis, "2026-06-07", "2026-06")


def test_gelecek_kesit_sonrasi_gunluk_veri_asla_kullanilmiyor(sentetik_ham):
    """STOP_ONLY_IF madde 5: kesitten SONRAKI bir zehir-değer, cari-ay
    özetine hiçbir şekilde sızmamalı."""
    df_a, karisik = sentetik_ham
    df_a = df_a.copy()
    zehir_indeksi = df_a.index[df_a["tarih"] == "2026-08-05"]
    df_a.loc[zehir_indeksi, "usdtry_orta"] = 999999.0
    birlesmis = m18._df_a_birlestir(df_a, karisik, kesim_tarihi=None)
    satir = m18.gelecek_kesit_satiri_uret(birlesmis, "2026-08-02", "2026-08")
    assert satir["usdtry_orta_max"] != pytest.approx(999999.0)
    assert satir["usdtry_orta_son"] != pytest.approx(999999.0)


# ---------------------------------------------------------------------------
# 3) Hash sözleşmesi
# ---------------------------------------------------------------------------

def test_konfig_hash_deterministik():
    assert m18.konfig_hash_hesapla() == m18.konfig_hash_hesapla()


def test_konfig_hash_feature_sirasi_degisince_farklilasir():
    a = m18._kanonik_json({"feature_sirasi": ["x", "y"]})
    b = m18._kanonik_json({"feature_sirasi": ["y", "x"]})
    assert m18._sha256(a) != m18._sha256(b)


def test_prediction_hash_deterministik_ve_hassas():
    ortak = dict(
        hedef_ay="2026-08", kesit_tarihi="2026-08-02", p_stable=0.3, p_up=0.3,
        tahmin_sinifi="down", konfig_hash="k", train_veri_hash="t",
        tahmin_satiri_hash="s",
    )
    a = m18.prediction_hash_hesapla(p_down=0.4, **ortak)
    b = m18.prediction_hash_hesapla(p_down=0.4, **ortak)
    c = m18.prediction_hash_hesapla(p_down=0.40000001, **ortak)
    assert a == b
    assert a != c


def test_yuvarla_nan_none_olur_ve_sayilari_sabitler():
    assert m18._yuvarla(float("nan")) is None
    assert m18._yuvarla(0.123456789012345) == round(0.123456789012345, 10)


# ---------------------------------------------------------------------------
# 4) Tahmin defteri — append-only + idempotent
# ---------------------------------------------------------------------------

def _ornek_kayit(**over):
    kayit = {
        "hedef_ay": "2026-08", "kesit_tarihi": "2026-08-02", "hafta_sirasi": 1,
        "tahmin_tarihi": "2026-08-03", "kayit_tarihi": "2026-08-09",
        "gercek_zamanli_mi": False, "arsiv_gecikme_gun": 7,
        "zaman_notu": "sentetik test", "p_down": 0.3, "p_stable": 0.3, "p_up": 0.4,
        "tahmin_sinifi": "up", "raw_confidence": 0.4, "konfig_hash": "kh1",
        "train_veri_hash": "tvh1", "tahmin_satiri_hash": "tsh1",
        "prediction_hash": "ph1",
    }
    kayit.update(over)
    return kayit


def test_deftere_ekle_yeni_kayit_eklenir(tmp_path):
    defter = tmp_path / "defter.csv"
    durum = m18.deftere_ekle(_ornek_kayit(), defter)
    assert durum == "eklendi"
    assert pd.read_csv(defter).shape[0] == 1


def test_deftere_ekle_ayni_anahtar_ayni_icerik_idempotent_no_op(tmp_path):
    defter = tmp_path / "defter.csv"
    m18.deftere_ekle(_ornek_kayit(), defter)
    durum2 = m18.deftere_ekle(_ornek_kayit(), defter)
    assert durum2 == "no_op_zaten_kayitli"
    assert pd.read_csv(defter).shape[0] == 1


def test_deftere_ekle_ayni_anahtar_farkli_icerik_hata_verir(tmp_path):
    defter = tmp_path / "defter.csv"
    m18.deftere_ekle(_ornek_kayit(), defter)
    with pytest.raises(RuntimeError, match="STOP_ONLY_IF madde 6"):
        m18.deftere_ekle(_ornek_kayit(p_down=0.99), defter)
    assert pd.read_csv(defter).shape[0] == 1  # eski satir bozulmadi


def test_deftere_ekle_farkli_hedef_ay_ayri_satir_eklenir(tmp_path):
    defter = tmp_path / "defter.csv"
    m18.deftere_ekle(_ornek_kayit(), defter)
    m18.deftere_ekle(_ornek_kayit(hedef_ay="2026-09", prediction_hash="ph2"), defter)
    assert pd.read_csv(defter).shape[0] == 2


# ---------------------------------------------------------------------------
# 5) Gerçekleşme defteri — ayrı, append-only, idempotent, prediction_hash ile
# ---------------------------------------------------------------------------

def test_gercek_etiketi_hesapla_yon_degerlendirme_ile_tutarli():
    assert m18g.gercek_etiketi_hesapla(110.0, 100.0) == yd.yon_etiketi(10.0, 5.0)
    assert m18g.gercek_etiketi_hesapla(102.0, 100.0) == "stable"
    assert m18g.gercek_etiketi_hesapla(90.0, 100.0) == "down"


def test_gerceklesme_ekle_idempotent_ve_hata(tmp_path):
    defter = tmp_path / "gerceklesme.csv"
    kayit = {
        "prediction_hash": "ph1", "hedef_ay": "2026-08", "onceki_ay_degeri": 100.0,
        "gercek_deger": 108.0, "gercek_etiket": "up", "kayit_tarihi": "2026-10-05",
    }
    assert m18g.gerceklesme_ekle(kayit, defter) == "eklendi"
    assert m18g.gerceklesme_ekle(kayit, defter) == "no_op_zaten_kayitli"
    assert pd.read_csv(defter).shape[0] == 1
    farkli = dict(kayit, gercek_etiket="stable")
    with pytest.raises(RuntimeError, match="STOP_ONLY_IF madde 6"):
        m18g.gerceklesme_ekle(farkli, defter)


def test_gerceklesme_tahmin_defterine_dokunmuyor(tmp_path):
    tahmin_defteri = tmp_path / "tahmin.csv"
    m18.deftere_ekle(_ornek_kayit(), tahmin_defteri)
    onceki_icerik = tahmin_defteri.read_text(encoding="utf-8")

    gerceklesme_defteri = tmp_path / "gerceklesme.csv"
    m18g.gerceklesme_ekle(
        {"prediction_hash": "ph1", "hedef_ay": "2026-08", "onceki_ay_degeri": 100.0,
         "gercek_deger": 108.0, "gercek_etiket": "up", "kayit_tarihi": "2026-10-05"},
        gerceklesme_defteri,
    )
    assert tahmin_defteri.read_text(encoding="utf-8") == onceki_icerik


# ---------------------------------------------------------------------------
# 6) Terminal değerlendirme — N<12 sert kapı + hareketli blok
# ---------------------------------------------------------------------------

def test_terminal_degerlendirme_dosya_yoksa_n_sifir_hata_verir(tmp_path):
    with pytest.raises(RuntimeError, match=r"N=0/12"):
        m18t.degerlendir(tmp_path / "yok.csv", tmp_path / "yok2.csv")


def _sentetik_tahmin_ve_gerceklesme_defterleri(hedef_aylar, *, tam_mi=True):
    tahmin_satirlari, gerceklesme_satirlari = [], []
    for i, ay in enumerate(hedef_aylar):
        for hafta in (1, 2, 3, 4):
            ph = f"ph-{ay}-{hafta}"
            tahmin_satirlari.append({
                "hedef_ay": ay, "kesit_tarihi": f"{ay}-0{hafta}", "hafta_sirasi": hafta,
                "tahmin_sinifi": "up" if i % 2 == 0 else "down",
                "prediction_hash": ph,
            })
            if tam_mi:
                gerceklesme_satirlari.append({"prediction_hash": ph, "gercek_etiket": "up"})
    return pd.DataFrame(tahmin_satirlari), pd.DataFrame(gerceklesme_satirlari)


def test_eksiksiz_aylari_belirle_dort_haftasi_olmayan_ay_sayilmaz():
    tahmin_df = pd.DataFrame([
        {"hedef_ay": "2026-09", "hafta_sirasi": 1, "tahmin_sinifi": "up", "prediction_hash": "a"},
        {"hedef_ay": "2026-09", "hafta_sirasi": 2, "tahmin_sinifi": "up", "prediction_hash": "b"},
    ])
    gerceklesme_df = pd.DataFrame([
        {"prediction_hash": "a", "gercek_etiket": "up"},
        {"prediction_hash": "b", "gercek_etiket": "up"},
    ])
    assert m18t.n_eksiksiz_bagimsiz_ay(tahmin_df, gerceklesme_df) == 0


def test_eksiksiz_aylari_belirle_agustos_2026_yeni_ay_olarak_sayilir():
    tahmin_df, gerceklesme_df = _sentetik_tahmin_ve_gerceklesme_defterleri(["2026-08"])
    assert m18t.n_eksiksiz_bagimsiz_ay(tahmin_df, gerceklesme_df) == 1


def test_eksiksiz_aylari_belirle_uygun_ay_sayilir():
    tahmin_df, gerceklesme_df = _sentetik_tahmin_ve_gerceklesme_defterleri(["2026-09"])
    assert m18t.n_eksiksiz_bagimsiz_ay(tahmin_df, gerceklesme_df) == 1


def test_terminal_degerlendirme_n_11_hata_n_12_calisir(tmp_path, monkeypatch):
    on_bir_ay = [f"2026-{ay:02d}" if ay <= 12 else f"2027-{ay-12:02d}" for ay in range(9, 20)]
    assert len(on_bir_ay) == 11
    tahmin_df, gerceklesme_df = _sentetik_tahmin_ve_gerceklesme_defterleri(on_bir_ay)
    tahmin_yolu, gerceklesme_yolu = tmp_path / "tahmin.csv", tmp_path / "gerceklesme.csv"
    tahmin_df.to_csv(tahmin_yolu, index=False)
    gerceklesme_df.to_csv(gerceklesme_yolu, index=False)

    with pytest.raises(RuntimeError, match=r"N=11/12"):
        m18t.degerlendir(tahmin_yolu, gerceklesme_yolu)

    on_iki_ay = on_bir_ay + ["2027-08"]
    tahmin_df12, gerceklesme_df12 = _sentetik_tahmin_ve_gerceklesme_defterleri(on_iki_ay)
    tahmin_df12.to_csv(tahmin_yolu, index=False)
    gerceklesme_df12.to_csv(gerceklesme_yolu, index=False)

    def sahte_persistence(hedef_aylar):
        return {pd.Period(a, freq="M"): "up" for a in hedef_aylar}

    monkeypatch.setattr(m18t, "_persistence_referans_serisi", sahte_persistence)
    sonuc = m18t.degerlendir(tahmin_yolu, gerceklesme_yolu, tekrar=200, seed=1)
    assert sonuc["n_mevcut_eksiksiz_bagimsiz_ay"] == 12
    assert sonuc["n_degerlendirilen_bagimsiz_ay"] == 12
    assert set(sonuc["kosullar"]) == {
        "a_holm_alt_sinir_pozitif", "b_delta_mcc_en_az_005",
        "c_macro_f1_farki_pozitif", "d_jackknife_isaret_korunuyor",
    }
    assert sonuc["bootstrap_blok_uzunlugu"] == 4
    assert sonuc["bootstrap_seed"] == 1
    assert sonuc["test"] == "2025-07..2026-06 ACILMADI_KILITLI"


def test_terminal_gecikse_bile_yalniz_ilk_12_ayi_degerlendirir(tmp_path, monkeypatch):
    on_uc_ay = [
        str(pd.Period("2026-08", freq="M") + i) for i in range(13)
    ]
    tahmin_df, gerceklesme_df = _sentetik_tahmin_ve_gerceklesme_defterleri(on_uc_ay)
    tahmin_yolu, gerceklesme_yolu = tmp_path / "t.csv", tmp_path / "g.csv"
    tahmin_df.to_csv(tahmin_yolu, index=False)
    gerceklesme_df.to_csv(gerceklesme_yolu, index=False)
    monkeypatch.setattr(
        m18t,
        "_persistence_referans_serisi",
        lambda aylar: {pd.Period(a, freq="M"): "up" for a in aylar},
    )
    sonuc = m18t.degerlendir(tahmin_yolu, gerceklesme_yolu, tekrar=100, seed=2)
    assert sonuc["n_mevcut_eksiksiz_bagimsiz_ay"] == 13
    assert sonuc["n_degerlendirilen_bagimsiz_ay"] == 12


def test_ay_icinde_celiskili_gercek_etiket_eksiksiz_sayilmaz():
    tahmin_df, gerceklesme_df = _sentetik_tahmin_ve_gerceklesme_defterleri(["2026-08"])
    gerceklesme_df.loc[0, "gercek_etiket"] = "down"
    assert m18t.n_eksiksiz_bagimsiz_ay(tahmin_df, gerceklesme_df) == 0


# ---------------------------------------------------------------------------
# 7) İsteğe bağlı/ayrı gerçek-veri duman testi — dosya yoksa atlanır
# ---------------------------------------------------------------------------

def test_gercek_veriyle_egitim_snapshotu_sinir_dogru_gercek_veri():
    if not GERCEK_SNAPSHOT_YOLU.exists():
        pytest.skip("Gercek Model07 ciktisi yerelde yok (gitignored) -- atlaniyor")
    egitim_df = m18.egitim_snapshotu_kur()
    assert egitim_df["hedef_ay"].max() == m18.SON_EGITIM_AYI
    assert egitim_df["hedef_ay"].min() == m18.ILK_EGITIM_AYI
    assert len(egitim_df) > 0
