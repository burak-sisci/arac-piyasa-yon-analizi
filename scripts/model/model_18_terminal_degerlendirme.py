"""Model 18 terminal değerlendirmesi — N=12 EKSİKSİZ bağımsız hedef ay
birikmeden HİÇBİR metrik üretmez (ön-kayıt Bölüm 6, STOP_ONLY_IF madde 7).

Bu script BUGÜN (2026-08-09) ÇALIŞTIRILMAZ (ön-kayıt Bölüm 7/9). Yalnız
N>=12 olduğunda, proje sahibi/Codex onayıyla elle çalıştırılır. M−2 persistence
girdisi, Model 14'ün M−2/M−3 feature'ıyla aynı kamuya açık ham adetlerden sabit
±%5 kuralıyla kurulur; geçmiş bir kilitli ayın performansı ölçülmez.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import haftalik_aylik_nowcast as hn  # noqa: E402
import model_07_haftalik_nowcast_veri_hazirligi as m07  # noqa: E402
import model_18_ileri_izleme as m18  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

TAHMIN_DEFTERI_YOLU = MODEL_DIR / "model_18_ileri_izleme_defteri.csv"
GERCEKLESME_DEFTERI_YOLU = MODEL_DIR / "model_18_gerceklesme_defteri.csv"

TERMINAL_ESIK_AY = 12  # SABIT -- ikinci/esnetilebilir bir esik YOKTUR (onkayit Bolum 6).


def eksiksiz_aylari_belirle(
    tahmin_df: pd.DataFrame, gerceklesme_df: pd.DataFrame
) -> pd.DataFrame:
    """Bir hedef ayın 'eksiksiz' sayılması için: hafta_sırası 1-4'ün dördü de
    tahmin edilmiş ve tek bir gerçekleşme etiketiyle bağlanmış olmalıdır.
    Dönen tablo yalnız birincil (1-4) haftaları ve `gercek_etiket` sütununu
    içerir."""
    gerekli_tahmin = {"hedef_ay", "hafta_sirasi", "tahmin_sinifi", "prediction_hash"}
    gerekli_gercek = {"prediction_hash", "gercek_etiket"}
    if not gerekli_tahmin.issubset(tahmin_df.columns):
        raise ValueError(f"eksiksiz_aylari_belirle: tahmin_df eksik sutun: {gerekli_tahmin - set(tahmin_df.columns)}")
    if not gerekli_gercek.issubset(gerceklesme_df.columns):
        raise ValueError(f"eksiksiz_aylari_belirle: gerceklesme_df eksik sutun: {gerekli_gercek - set(gerceklesme_df.columns)}")

    birincil = tahmin_df[tahmin_df["hafta_sirasi"].isin([1, 2, 3, 4])].copy()
    if birincil.empty:
        return birincil
    if birincil["prediction_hash"].duplicated().any():
        raise ValueError("eksiksiz_aylari_belirle: tahmin prediction_hash tekil degil")
    if gerceklesme_df["prediction_hash"].duplicated().any():
        raise ValueError("eksiksiz_aylari_belirle: gerceklesme prediction_hash tekil degil")
    # CSV'den okunduğunda hedef_ay ham string kalır; downstream (yıl-jackknife,
    # ay_terfi_uygun_mu, persistence eşleşmesi) tutarlı Period tipi bekler.
    birincil["hedef_ay"] = pd.PeriodIndex(birincil["hedef_ay"], freq="M")

    dort_hafta_tam = (
        birincil.groupby("hedef_ay")["hafta_sirasi"]
        .apply(lambda s: sorted(set(s)) == [1, 2, 3, 4])
    )
    aylar_4hafta = set(dort_hafta_tam[dort_hafta_tam].index)

    birlesik = birincil.merge(
        gerceklesme_df[["prediction_hash", "gercek_etiket"]],
        on="prediction_hash", how="left",
    )
    gerceklesme_ozeti = birlesik.groupby("hedef_ay")["gercek_etiket"].agg(
        dolu_sayisi=lambda s: int(s.notna().sum()),
        benzersiz_sayisi=lambda s: int(s.dropna().nunique()),
    )
    # Bir ayin dort haftasi da AYNI tek gerceklesme etiketine baglanmalidir.
    uygun_gercek = (
        gerceklesme_ozeti["dolu_sayisi"].eq(4)
        & gerceklesme_ozeti["benzersiz_sayisi"].eq(1)
    )
    aylar_gerceklesmis = set(gerceklesme_ozeti[uygun_gercek].index)

    eksiksiz_aylar = aylar_4hafta & aylar_gerceklesmis
    eksiksiz = birlesik[birlesik["hedef_ay"].isin(eksiksiz_aylar)].copy()
    eksiksiz["agirlik"] = 1.0 / eksiksiz.groupby("hedef_ay")["hedef_ay"].transform("size")
    return eksiksiz.reset_index(drop=True)


def n_eksiksiz_bagimsiz_ay(tahmin_df: pd.DataFrame, gerceklesme_df: pd.DataFrame) -> int:
    eksiksiz = eksiksiz_aylari_belirle(tahmin_df, gerceklesme_df)
    return int(eksiksiz["hedef_ay"].nunique()) if not eksiksiz.empty else 0


def _persistence_referans_serisi(hedef_aylar: list) -> dict:
    """Her gelecek hedef ay için M−2 persistence girdisini ham M−2/M−3
    adetlerinden sabit ±%5 kuralıyla hesaplar. Bu, geçmiş ayda model performansı
    ölçmez; dondurulmuş baseline'ın gelecek hedef için ürettiği tahmindir."""
    df_a, karisik = m18._df_a_oku()
    df_a = m18._df_a_birlestir(df_a, karisik, kesim_tarihi=None)
    df_a["tarih"] = pd.to_datetime(df_a["tarih"], errors="raise")
    df_a["_ay"] = df_a["tarih"].dt.to_period("M")
    hedef_serisi = hn._aylik_seri(df_a, "_ay", m07.TARGET)

    sonuc = {}
    for hedef_ay in hedef_aylar:
        hedef_ay = pd.Period(hedef_ay, freq="M")
        m2 = hedef_ay - 2
        deger_m2 = hedef_serisi.get(m2, np.nan)
        deger_m3 = hedef_serisi.get(m2 - 1, np.nan)
        if pd.isna(deger_m2) or pd.isna(deger_m3) or deger_m3 == 0:
            sonuc[hedef_ay] = "eksik"
            continue
        yuzde = (deger_m2 - deger_m3) / deger_m3 * 100.0
        sonuc[hedef_ay] = yd.yon_etiketi(yuzde, m07.ESIK_YUZDE)
    return sonuc


def _hareketli_blok_delta_mcc(
    eksiksiz: pd.DataFrame, *, tekrar: int = 2000, seed: int = 420
) -> tuple[np.ndarray, dict]:
    """Model 14 ile birebir ay-hareketli-blok (uzunluk=4) eşli MCC farkı."""
    sirali_aylar = sorted(eksiksiz["hedef_ay"].unique())
    if len(sirali_aylar) < 4:
        raise ValueError("hareketli blok bootstrap icin en az 4 bagimsiz ay gerekir")

    gercek, aday, referans = [], [], []
    for ay in sirali_aylar:
        grup = eksiksiz[eksiksiz["hedef_ay"].eq(ay)].sort_values("hafta_sirasi")
        if grup["hafta_sirasi"].tolist() != [1, 2, 3, 4]:
            raise AssertionError(f"{ay}: hafta 1-4 matrisi eksik veya sirasi bozuk")
        gercek.append(grup["gercek_etiket"].tolist())
        aday.append(grup["tahmin_sinifi"].tolist())
        referans.append(grup["persistence_m_eksi_2"].tolist())

    indeksler = rn.hareketli_blok_indeksleri(
        len(sirali_aylar), tekrar=tekrar, blok_uzunlugu=4, seed=seed
    )
    dagilim = rn.ortak_indeksli_metrik_dagilimlari(
        np.asarray(gercek, dtype=object),
        {
            "model14_lojistik_l2_c01": np.asarray(aday, dtype=object),
            "persistence_m_eksi_2": np.asarray(referans, dtype=object),
        },
        indeksler,
    )
    farklar = (
        dagilim["dagilimlar"]["model14_lojistik_l2_c01"]["mcc"]
        - dagilim["dagilimlar"]["persistence_m_eksi_2"]["mcc"]
    )
    return farklar, dagilim


def degerlendir(
    tahmin_defteri_yolu: Path = TAHMIN_DEFTERI_YOLU,
    gerceklesme_defteri_yolu: Path = GERCEKLESME_DEFTERI_YOLU,
    *, tekrar: int = 2000, seed: int = 420,
) -> dict:
    """N>=12 eksiksiz bağımsız ay yoksa RuntimeError. Aksi halde Model 14
    a-d kapısını (tek aday, Holm gerekmez) M-2 persistence referansına karşı
    YENİ prospektif örneklemde uygular. Eski 50 origin ASLA eklenmez."""
    if not Path(tahmin_defteri_yolu).exists() or not Path(gerceklesme_defteri_yolu).exists():
        n = 0
        eksiksiz = pd.DataFrame()
    else:
        tahmin_df = pd.read_csv(tahmin_defteri_yolu)
        gerceklesme_df = pd.read_csv(gerceklesme_defteri_yolu)
        eksiksiz = eksiksiz_aylari_belirle(tahmin_df, gerceklesme_df)
        n = int(eksiksiz["hedef_ay"].nunique()) if not eksiksiz.empty else 0

    if n < TERMINAL_ESIK_AY:
        raise RuntimeError(
            f"STOP_ONLY_IF madde 7: N={n}/{TERMINAL_ESIK_AY} eksiksiz bagimsiz "
            "hedef ay ile terminal degerlendirme YAPILAMAZ (peeking yasagi, "
            "onkayit Bolum 6). Metrik uretilmedi."
        )

    # Ön-kayıt terminal N'si tam 12'dir. Çalıştırma operasyonel olarak gecikse
    # bile 13. ve sonraki aylar ilk terminal okumaya post-hoc eklenmez.
    ilk_terminal_aylari = sorted(eksiksiz["hedef_ay"].unique())[:TERMINAL_ESIK_AY]
    eksiksiz = eksiksiz[eksiksiz["hedef_ay"].isin(ilk_terminal_aylari)].copy()
    if eksiksiz["hedef_ay"].nunique() != TERMINAL_ESIK_AY:
        raise AssertionError("terminal orneklem tam 12 bagimsiz ay olmali")

    persistence = _persistence_referans_serisi(sorted(eksiksiz["hedef_ay"].unique()))
    eksiksiz = eksiksiz.copy()
    eksiksiz["persistence_m_eksi_2"] = eksiksiz["hedef_ay"].map(persistence)
    if (eksiksiz["persistence_m_eksi_2"] == "eksik").any():
        raise RuntimeError("degerlendir: persistence referansi eksik ay(lar) icin hesaplanamadi")

    aday_metrik = yd.degerlendir(
        eksiksiz["gercek_etiket"], eksiksiz["tahmin_sinifi"], agirliklar=eksiksiz["agirlik"]
    )
    ref_metrik = yd.degerlendir(
        eksiksiz["gercek_etiket"], eksiksiz["persistence_m_eksi_2"], agirliklar=eksiksiz["agirlik"]
    )
    delta_mcc_nokta = aday_metrik["mcc_gorodkin"] - ref_metrik["mcc_gorodkin"]
    delta_macro_f1_nokta = aday_metrik["macro_f1"] - ref_metrik["macro_f1"]

    farklar, blok_denetim = _hareketli_blok_delta_mcc(
        eksiksiz, tekrar=tekrar, seed=seed
    )
    p_ham_tek_yonlu = float((1 + np.sum(farklar <= 0)) / (tekrar + 1))
    delta_mcc_alt_sinir_95 = float(np.quantile(farklar, 0.05))
    h0_reddedildi = p_ham_tek_yonlu <= 0.05

    yillar = sorted({ay.year for ay in eksiksiz["hedef_ay"].unique()})
    jackknife = {}
    for yil in yillar:
        tut = eksiksiz[eksiksiz["hedef_ay"].apply(lambda a: a.year) != yil]
        if tut["hedef_ay"].nunique() < 1:
            continue
        a = yd.degerlendir(tut["gercek_etiket"], tut["tahmin_sinifi"], agirliklar=tut["agirlik"])
        r = yd.degerlendir(tut["gercek_etiket"], tut["persistence_m_eksi_2"], agirliklar=tut["agirlik"])
        jackknife[str(yil)] = a["mcc_gorodkin"] - r["mcc_gorodkin"]
    isaret_korunuyor = bool(jackknife) and all(v > 0 for v in jackknife.values())

    terfi_karari = m18.m14.terfi_kosullarini_hesapla(
        delta_mcc_nokta=delta_mcc_nokta,
        delta_mcc_holm_alt_sinir=delta_mcc_alt_sinir_95,
        h0_reddedildi=h0_reddedildi,
        delta_macro_f1_nokta=delta_macro_f1_nokta,
        jackknife_isaret_pozitif=isaret_korunuyor,
    )

    return {
        "n_mevcut_eksiksiz_bagimsiz_ay": n,
        "n_degerlendirilen_bagimsiz_ay": TERMINAL_ESIK_AY,
        "terminal_esik": TERMINAL_ESIK_AY,
        "aday_metrik": aday_metrik,
        "referans_metrik": ref_metrik,
        "delta_mcc_nokta": delta_mcc_nokta,
        "delta_mcc_hareketli_blok4_alt_sinir_tek_yonlu_95": delta_mcc_alt_sinir_95,
        "ham_p_tek_yonlu": p_ham_tek_yonlu,
        "h0_reddedildi": h0_reddedildi,
        "bootstrap_tekrar": tekrar,
        "bootstrap_seed": seed,
        "bootstrap_blok_uzunlugu": 4,
        "bootstrap_gercek_sinif_eksik_cekilis_orani": blok_denetim[
            "gercek_sinif_eksik_cekilis_orani"
        ],
        "delta_macro_f1_nokta": delta_macro_f1_nokta,
        "yil_jackknife_delta_mcc": jackknife,
        "kosullar": terfi_karari["kosullar"],
        "terfi": terfi_karari["terfi"],
        "referans": "persistence_m_eksi_2 (prospektif ornek icinde YENIDEN hesaplandi, 50 origin ile birlesmedi)",
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
    }


if __name__ == "__main__":
    raise SystemExit(
        "model_18_terminal_degerlendirme.py bugun (2026-08-09) calistirilmaz "
        "(onkayit Bolum 7/9, STOP_ONLY_IF madde 7). N>=12 eksiksiz bagimsiz ay "
        "birikince proje sahibi/Codex onayiyla elle calistirilir."
    )
