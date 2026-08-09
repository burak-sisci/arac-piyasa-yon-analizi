"""Model 14: mevcut as-of feature genisletme — kontrol (10) vs test (14) kolu.

Onkayit: prompts/veri/43_model14_mevcut_asof_feature_genisletme_onkayit.md
(Pusula, commit 8a2e13a; Bolum 9 duzeltmesiyle guncellendi). Model 10'un
test-disi rolling-origin protokolu (50 origin, 2 ay embargo, sabit seed,
hareketli-blok bootstrap+Holm, yil-disi jackknife) birebir korunur. Tek
fark: test kolu, Model 07 snapshot'inda kesit tarihinde zaten bilinen ama
Model 09'un 10 feature'inda KULLANILMAYAN 4 sizintisiz kolondan kurulu
kucuk bir aile ekler (onkayit Bolum 2/3).

Kontrol kolu Model 09'un 10 feature'iyla birebir ayni hesaptir. Onkayit
Bolum 9 duzeltmesi geregi, dogrulama referansi git-ignored/eski yerel
model_10_rolling_origin_*.json/csv DOSYALARI DEGIL, ayni surecte ayni
HEAD'den CANLI cagrilan `model_10_rolling_origin_nowcast._rolling_tahminleri`
kod yoludur (bkz. `model10_kod_yolu_referansi`). Bu esitlik saglanmazsa
main() test kolunun metriklerini hic hesaplamadan/yorumlamadan
STOP_ONLY_IF_KONTROL_KOD_YOLU_UYUSMAZLIGI ile durur.

Kilitli test (2025-07..2026-06) bu script tarafindan hicbir asamada
okunmaz; ilk adim olarak snapshot'tan cikarilir ve originler ayrica
assert ile bu araligin disinda tutulur.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_09_dusuk_kapasiteli_nowcast as m09  # noqa: E402
import model_10_rolling_origin_nowcast as m10  # noqa: E402
import nowcast_baseline as nb  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

# Model 10 ile birebir sabitler — yeniden tanimlamak yerine dogrudan import
# edilir (uyusmazlik riskini yapisal olarak sifirlar).
TEKRAR = m10.TEKRAR
MODEL_ADLARI = m10.MODEL_ADLARI
BASELINE_ADLARI = m10.BASELINE_ADLARI
REF_BASELINE = "persistence_m_eksi_2"
_nokta = m10._nokta
_ci = m10._ci
_matrisler = m10._matrisler

SON_DEGERLENDIRME_AYI = "2025-04"
KILITLI_TEST_BASLANGIC = pd.Period("2025-07", freq="M")

# Onkayit Bolum 2/3: Model 09'un 10 feature'inda KULLANILMAYAN, Model 07
# snapshot'inda zaten kesit-tarihinde-bilinen 4 feature'lik kucuk aile.
YENI_FEATURELAR = [
    "usdtry_orta_std",
    "tuketici_guven_endeksi_lag2ay",
    "odmd_otomobil_adet_lag2ay",
    "reel_politika_faizi_lag2ay",
]
KONTROL_FEATURELAR = list(m09.FEATURELAR)
TEST_FEATURELAR = KONTROL_FEATURELAR + YENI_FEATURELAR


def feature_hazirla(df: pd.DataFrame) -> pd.DataFrame:
    """Model 09'un turevlerini + onkayitli tek yeni turetilmis feature'i ekler.

    reel_politika_faizi_lag2ay = politika_faizi_lag2ay - tufe_yillik_degisim_lag2ay
    (Fisher yaklasikligi; tam bilesik formul degildir — onkayit Bolum 3).
    Iki bileseni de zaten M-2 gecikmeli snapshot kolonu oldugundan fark alma
    bilgi-zamanini bozmaz.
    """
    sonuc = m09._feature_hazirla(df)
    gerekli_kaynak = {"politika_faizi_lag2ay", "tufe_yillik_degisim_lag2ay", *YENI_FEATURELAR[:3]}
    eksik = sorted(gerekli_kaynak - set(sonuc.columns))
    if eksik:
        raise KeyError(f"Yeni feature kaynak sutunlari snapshotta yok: {eksik}")
    sonuc["reel_politika_faizi_lag2ay"] = (
        sonuc["politika_faizi_lag2ay"] - sonuc["tufe_yillik_degisim_lag2ay"]
    )
    eksik_hedef = [c for c in YENI_FEATURELAR if c not in sonuc.columns]
    if eksik_hedef:
        raise KeyError(f"Yeni feature uretilemedi: {eksik_hedef}")
    return sonuc


def kilitli_test_disla(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Onkayit Bolum 1: kilitli test (2025-07..2026-06) hicbir asamada okunmaz.

    Bu fonksiyon cagirandan HEMEN sonra, hicbir feature/etiket islemi
    yapilmadan once calistirilmalidir. Donen dataframe'de kilitli test
    araligina ait TEK BIR satir bile kalmadigi assert ile kanitlanir.
    """
    if "hedef_ay" not in df.columns:
        raise KeyError("kilitli_test_disla: 'hedef_ay' sutunu bulunamadi")
    kilitli_maske = df["hedef_ay"] >= KILITLI_TEST_BASLANGIC
    kilitli_sayisi = int(kilitli_maske.sum())
    guvenli = df.loc[~kilitli_maske].copy()
    if (guvenli["hedef_ay"] >= KILITLI_TEST_BASLANGIC).any():
        raise AssertionError("kilitli_test_disla: filtre sonrasi hala kilitli-test satiri var")
    return guvenli, kilitli_sayisi


def _rolling_tahminleri(
    snapshot: pd.DataFrame, featurelar: list[str]
) -> tuple[pd.DataFrame, list[dict], dict]:
    """Model 10'daki _rolling_tahminleri ile birebir; feature listesi parametrik.

    Preprocessing (imputer+scaler) HER origin'in TREN kumesi icinde ayri
    ayri fit edilir; global fit yoktur. Her origin icin ayrica kilitli-test
    disi kalindigi assert ile dogrulanir.
    """
    aylik_etiket = snapshot.drop_duplicates("hedef_ay").set_index("hedef_ay")["etiket"]
    originler = rn.genisleyen_originler(
        "2019-01", SON_DEGERLENDIRME_AYI, ilk_train_ay_sayisi=24, embargo_ay_sayisi=2
    )
    kayitlar = []
    denetim = {"on_isleme_fit_sayisi": 0, "model_fit_sayisi": 0}
    for fold_no, origin in enumerate(originler, start=1):
        assert max(origin["train"]) <= origin["degerlendirme"] - 3
        assert origin["embargo"] == [
            origin["degerlendirme"] - 2, origin["degerlendirme"] - 1
        ]
        # Onkayit Bolum 1 / STOP_ONLY_IF: kilitli test hicbir origin'e girmez.
        assert origin["degerlendirme"] < KILITLI_TEST_BASLANGIC
        assert all(ay < KILITLI_TEST_BASLANGIC for ay in origin["train"])
        assert all(ay < KILITLI_TEST_BASLANGIC for ay in origin["embargo"])

        train = snapshot[snapshot["hedef_ay"].isin(origin["train"])].copy()
        val = snapshot[
            snapshot["hedef_ay"].eq(origin["degerlendirme"])
            & snapshot["hafta_sirasi"].isin([1, 2, 3, 4])
        ].sort_values("hafta_sirasi").copy()
        assert val["hafta_sirasi"].tolist() == [1, 2, 3, 4]
        assert val["etiket"].nunique() == 1

        # Her origin'de sifirdan fit; global on-isleme nesnesi yoktur.
        imputer = SimpleImputer(strategy="median", add_indicator=True)
        scaler = StandardScaler()
        xtr_imp = imputer.fit_transform(train[featurelar])
        xva_imp = imputer.transform(val[featurelar])
        xtr_scaled = scaler.fit_transform(xtr_imp)
        xva_scaled = scaler.transform(xva_imp)
        denetim["on_isleme_fit_sayisi"] += 1

        bt, _ = nb.baseline_tahminleri(
            aylik_etiket, origin["train"], [origin["degerlendirme"]]
        )
        gercek = str(val["etiket"].iloc[0])
        for hafta in (1, 2, 3, 4):
            for ad, tahmin in bt.items():
                kayitlar.append({"fold": fold_no, "hedef_ay": str(origin["degerlendirme"]),
                    "train_ay_sayisi": len(origin["train"]), "hafta_sirasi": hafta,
                    "yaklasim": ad, "gercek": gercek, "tahmin": tahmin[0]})

        for ad, model in m09._adaylar().items():
            lojistik = ad.startswith("lojistik")
            model.fit(xtr_scaled if lojistik else xtr_imp, train["etiket"],
                      sample_weight=train["agirlik"])
            denetim["model_fit_sayisi"] += 1
            yhat = model.predict(xva_scaled if lojistik else xva_imp)
            for hafta, tahmin in zip((1, 2, 3, 4), yhat):
                kayitlar.append({"fold": fold_no, "hedef_ay": str(origin["degerlendirme"]),
                    "train_ay_sayisi": len(origin["train"]), "hafta_sirasi": hafta,
                    "yaklasim": ad, "gercek": gercek, "tahmin": str(tahmin)})
    assert denetim == {"on_isleme_fit_sayisi": len(originler),
                       "model_fit_sayisi": len(originler) * len(MODEL_ADLARI)}
    return pd.DataFrame(kayitlar), originler, denetim


def terfi_kosullarini_hesapla(
    delta_mcc_nokta: float,
    delta_mcc_holm_alt_sinir: float,
    h0_reddedildi: bool,
    delta_macro_f1_nokta: float,
    jackknife_isaret_pozitif: bool,
) -> dict:
    """Onkayit Bolum 6 — terfi kapisi (=basari kurali), Model 10'dan gevsek DEGIL.

    Dort kosulun TUMU (a-d) zorunludur; hafta tanisi bu fonksiyona hicbir
    parametre olarak GIRMEZ (yapisal olarak terfi gerekcesi olamaz).
    """
    kosullar = {
        "a_holm_alt_sinir_pozitif": bool(h0_reddedildi and delta_mcc_holm_alt_sinir > 0),
        "b_delta_mcc_en_az_005": bool(delta_mcc_nokta >= 0.05),
        "c_macro_f1_farki_pozitif": bool(delta_macro_f1_nokta > 0),
        "d_jackknife_isaret_korunuyor": bool(jackknife_isaret_pozitif),
    }
    return {"kosullar": kosullar, "terfi": all(kosullar.values())}


def kol_calistir(snapshot: pd.DataFrame, featurelar: list[str], kol_adi: str):
    """Model 10'daki main() govdesini kol/feature parametrik hale getirir."""
    tahmin_df, originler, denetim = _rolling_tahminleri(snapshot, featurelar)
    gercek, tahminler, aylar = _matrisler(tahmin_df)
    assert len(aylar) == 50 and max(aylar) == SON_DEGERLENDIRME_AYI
    assert all(pd.Period(a, freq="M") < KILITLI_TEST_BASLANGIC for a in aylar)

    blok_idx = rn.hareketli_blok_indeksleri(50, tekrar=TEKRAR, blok_uzunlugu=4, seed=420)
    iid_idx = rn.iid_indeksleri(50, tekrar=TEKRAR, seed=420)
    blok = rn.ortak_indeksli_metrik_dagilimlari(gercek, tahminler, blok_idx)
    iid = rn.ortak_indeksli_metrik_dagilimlari(gercek, tahminler, iid_idx)

    genel = {}
    for ad in tahminler:
        genel[ad] = {
            "nokta": _nokta(gercek, tahminler[ad]),
            "hareketli_blok4_ci95": {
                "mcc": _ci(blok["dagilimlar"][ad]["mcc"]),
                "macro_f1": _ci(blok["dagilimlar"][ad]["macro_f1"]),
            },
            "iid_duyarlilik_ci95": {
                "mcc": _ci(iid["dagilimlar"][ad]["mcc"]),
                "macro_f1": _ci(iid["dagilimlar"][ad]["macro_f1"]),
            },
        }

    fark_dagilimlari = {
        ad: blok["dagilimlar"][ad]["mcc"] - blok["dagilimlar"][REF_BASELINE]["mcc"]
        for ad in MODEL_ADLARI
    }
    p_ham = {
        ad: float((1 + np.sum(fark_dagilimlari[ad] <= 0)) / (TEKRAR + 1))
        for ad in MODEL_ADLARI
    }
    holm = rn.holm_bonferroni(p_ham, alfa=0.05)
    for ad in MODEL_ADLARI:
        alfa_ad = holm[ad]["holm_esik"]
        holm[ad]["delta_mcc_nokta"] = genel[ad]["nokta"]["mcc"] - genel[REF_BASELINE]["nokta"]["mcc"]
        holm[ad]["delta_mcc_holm_alt_sinir"] = float(np.quantile(fark_dagilimlari[ad], alfa_ad))
        holm[ad]["delta_macro_f1_nokta"] = (
            genel[ad]["nokta"]["macro_f1"] - genel[REF_BASELINE]["nokta"]["macro_f1"]
        )

    yillar = np.array([int(x[:4]) for x in aylar])
    jackknife = {}
    for ad in MODEL_ADLARI:
        farklar = {}
        for yil in sorted(set(yillar)):
            tut = yillar != yil
            farklar[str(yil)] = (
                _nokta(gercek[tut], tahminler[ad][tut])["mcc"]
                - _nokta(gercek[tut], tahminler[REF_BASELINE][tut])["mcc"]
            )
        jackknife[ad] = {"yil_disarida_delta_mcc": farklar,
                         "isaret_her_yil_pozitif": all(x > 0 for x in farklar.values())}

    # Hafta tanisi terfi ailesinin disindadir (yalniz teshis).
    hafta = {}
    hafta_idx = rn.hareketli_blok_indeksleri(50, tekrar=TEKRAR, blok_uzunlugu=4, seed=421)
    for ad in MODEL_ADLARI:
        nokta = []
        for h in range(4):
            nokta.append(yd.degerlendir(gercek[:, h], tahminler[ad][:, h])["mcc_gorodkin"])
        h1 = rn.ortak_indeksli_metrik_dagilimlari(
            np.repeat(gercek[:, [0]], 4, axis=1),
            {ad: np.repeat(tahminler[ad][:, [0]], 4, axis=1)}, hafta_idx,
        )["dagilimlar"][ad]["mcc"]
        h4 = rn.ortak_indeksli_metrik_dagilimlari(
            np.repeat(gercek[:, [3]], 4, axis=1),
            {ad: np.repeat(tahminler[ad][:, [3]], 4, axis=1)}, hafta_idx,
        )["dagilimlar"][ad]["mcc"]
        delta = h4 - h1
        hafta[ad] = {
            "hafta_1_4_mcc": nokta,
            "azalmayan_nokta": all(b >= a for a, b in zip(nokta, nokta[1:])),
            "hafta4_eksi_hafta1_mcc_ci95": _ci(delta),
            "haftalik_bilgi_dogrulandi": (
                all(b >= a for a, b in zip(nokta, nokta[1:])) and _ci(delta)[0] > 0
            ),
            "terfi_gerekcesi_olamaz": True,
        }

    terfi = {}
    for ad in MODEL_ADLARI:
        terfi[ad] = terfi_kosullarini_hesapla(
            delta_mcc_nokta=holm[ad]["delta_mcc_nokta"],
            delta_mcc_holm_alt_sinir=holm[ad]["delta_mcc_holm_alt_sinir"],
            h0_reddedildi=holm[ad]["h0_reddedildi"],
            delta_macro_f1_nokta=holm[ad]["delta_macro_f1_nokta"],
            jackknife_isaret_pozitif=jackknife[ad]["isaret_her_yil_pozitif"],
        )

    ci_yari_genislik = {
        ad: float((_ci(fark_dagilimlari[ad])[1] - _ci(fark_dagilimlari[ad])[0]) / 2)
        for ad in MODEL_ADLARI
    }

    ozet = {
        "kol": kol_adi,
        "feature_sayisi": len(featurelar),
        "featurelar": list(featurelar),
        "origin_sayisi": 50,
        "degerlendirme_ay_araligi": [aylar[0], aylar[-1]],
        "ilk_son_train_ay_sayisi": [len(originler[0]["train"]), len(originler[-1]["train"])],
        "embargo_ay_sayisi": 2, "bootstrap_tekrar": TEKRAR,
        "birincil_birim": "4 hafta havuzlu; her ay toplam agirlik=1",
        "assertion_denetimi": denetim,
        "gercek_sinif_eksik_cekilis_orani_blok4": blok["gercek_sinif_eksik_cekilis_orani"],
        "gercek_sinif_eksik_cekilis_orani_iid": iid["gercek_sinif_eksik_cekilis_orani"],
        "tahmin_dejenere_cekilis_orani_blok4": blok["tahmin_dejenere_cekilis_orani"],
        "genel_metrikler": genel, "holm_aile_4_model": holm,
        "yil_jackknife": jackknife, "hafta_tanisi": hafta,
        "terfi_karari_ham": terfi,
        "ci_yari_genislik_saptama_gucu_gostergesi": ci_yari_genislik,
        "herhangi_terfi": any(x["terfi"] for x in terfi.values()),
    }
    return ozet, tahmin_df, originler


def _deger_esit_mi(a, b, atol: float = 1e-9) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_deger_esit_mi(a[k], b[k], atol) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_deger_esit_mi(x, y, atol) for x, y in zip(a, b))
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(float(a), float(b), abs_tol=atol)
    return a == b


ORTAK_OZET_ALANLARI = [
    "origin_sayisi", "degerlendirme_ay_araligi", "ilk_son_train_ay_sayisi",
    "embargo_ay_sayisi", "bootstrap_tekrar", "assertion_denetimi",
    "gercek_sinif_eksik_cekilis_orani_blok4", "gercek_sinif_eksik_cekilis_orani_iid",
    "tahmin_dejenere_cekilis_orani_blok4", "genel_metrikler", "holm_aile_4_model",
    "yil_jackknife", "hafta_tanisi", "terfi_karari_ham",
    "ci_yari_genislik_saptama_gucu_gostergesi", "herhangi_terfi",
]


def dogrula_kontrol_model10_ile(kontrol_ozet: dict, model10_json: dict) -> dict:
    """Kontrol kolu (10 feature) ozetini committed Model10 ciktisiyla deger-esit karsilastirir."""
    uyusmazlik = [
        alan for alan in ORTAK_OZET_ALANLARI
        if not _deger_esit_mi(kontrol_ozet[alan], model10_json[alan])
    ]
    return {
        "alanlar_karsilastirildi": ORTAK_OZET_ALANLARI,
        "uyusmazlik": uyusmazlik,
        "birebir_uyumlu": not uyusmazlik,
    }


def dogrula_kontrol_tahmin_model10_ile(
    kontrol_tahmin: pd.DataFrame, referans: pd.DataFrame
) -> dict:
    """Kontrol tahminlerini ayni HEAD'de calisan Model 10 kod yoluyla karsilastirir."""
    ortak_kolonlar = ["fold", "hedef_ay", "train_ay_sayisi", "hafta_sirasi", "yaklasim", "gercek", "tahmin"]
    a = kontrol_tahmin.sort_values(["fold", "yaklasim", "hafta_sirasi"])[ortak_kolonlar].reset_index(drop=True)
    b = referans.sort_values(["fold", "yaklasim", "hafta_sirasi"])[ortak_kolonlar].reset_index(drop=True)
    birebir = len(a) == len(b) and a.astype(str).equals(b.astype(str))
    return {
        "satir_sayisi_kontrol": int(len(a)),
        "satir_sayisi_referans": int(len(b)),
        "birebir_uyumlu": bool(birebir),
    }


def model10_kod_yolu_referansi(snapshot: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Ayni surec ve HEAD'deki Model 10 kod yolundan kontrol referansi uretir."""
    referans, originler, denetim = m10._rolling_tahminleri(snapshot)
    beklenen = {
        "on_isleme_fit_sayisi": 50,
        "model_fit_sayisi": 50 * len(MODEL_ADLARI),
    }
    if len(originler) != 50 or denetim != beklenen:
        raise AssertionError("Guncel Model 10 kod yolu origin/fit sozlesmesinden sapti")
    return referans, denetim


def main() -> None:
    t0 = time.time()
    ham = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    ham["hedef_ay"] = pd.PeriodIndex(ham["hedef_ay"], freq="M")

    guvenli, kilitli_disarida = kilitli_test_disla(ham)
    snapshot = feature_hazirla(guvenli)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    assert (snapshot["hedef_ay"] < KILITLI_TEST_BASLANGIC).all(), "kilitli test satiri sizdi"

    kontrol_ozet, kontrol_tahmin, _ = kol_calistir(snapshot, KONTROL_FEATURELAR, "kontrol_10_feature")
    model10_referans, model10_denetim = model10_kod_yolu_referansi(snapshot)
    tahmin_dogrulama = dogrula_kontrol_tahmin_model10_ile(
        kontrol_tahmin, model10_referans
    )
    if not tahmin_dogrulama["birebir_uyumlu"]:
        raise AssertionError(
            "STOP_ONLY_IF_KONTROL_KOD_YOLU_UYUSMAZLIGI: kontrol kolu, ayni surecte "
            "canli cagrilan Model 10 kod yoluyla birebir uyusmuyor; test kolu "
            "hesaplanmadan/yorumlanmadan duruldu (onkayit Bolum 9)."
        )

    test_ozet, test_tahmin, _ = kol_calistir(snapshot, TEST_FEATURELAR, "test_14_feature")

    for ad in BASELINE_ADLARI:
        if kontrol_ozet["genel_metrikler"][ad] != test_ozet["genel_metrikler"][ad]:
            raise AssertionError(
                f"Baseline {ad} feature'dan bagimsiz olmali; kontrol/test kolu arasinda fark bulundu"
            )

    ikincil_delta = {
        ad: {
            "delta_mcc_test_eksi_kontrol": (
                test_ozet["genel_metrikler"][ad]["nokta"]["mcc"]
                - kontrol_ozet["genel_metrikler"][ad]["nokta"]["mcc"]
            ),
            "delta_macro_f1_test_eksi_kontrol": (
                test_ozet["genel_metrikler"][ad]["nokta"]["macro_f1"]
                - kontrol_ozet["genel_metrikler"][ad]["nokta"]["macro_f1"]
            ),
        }
        for ad in MODEL_ADLARI
    }

    herhangi_terfi = test_ozet["herhangi_terfi"]
    karar = "TERFI_ADAYI_BULUNDU" if herhangi_terfi else "SINYAL_YOK_14_FEATURE"

    sonuc = {
        "yonetici": "Pusula",
        "onkayit": "prompts/veri/43_model14_mevcut_asof_feature_genisletme_onkayit.md",
        "durum": "test_disi_rolling_origin_iki_kollu",
        "yeni_featurelar": YENI_FEATURELAR,
        "kilitli_test_disarida_birakilan_satir_sayisi": kilitli_disarida,
        "kontrol_kolu": kontrol_ozet,
        "test_kolu": test_ozet,
        "kontrol_model10_kod_yolu_dogrulama": {
            **tahmin_dogrulama,
            "referans": "ayni_HEAD_ayni_surec_model10__rolling_tahminleri",
            "model10_assertion_denetimi": model10_denetim,
        },
        "ikincil_kontrol_test_delta_bilgi_amacli_terfi_kapisi_disinda": ikincil_delta,
        "terfi_kapisi_referans": REF_BASELINE,
        "karar": karar,
        "calisma_suresi_saniye": round(time.time() - t0, 1),
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
    }

    kontrol_tahmin.to_csv(
        MODEL_DIR / "model_14_kontrol_10feature_tahminleri.csv", index=False, encoding="utf-8-sig"
    )
    test_tahmin.to_csv(
        MODEL_DIR / "model_14_test_14feature_tahminleri.csv", index=False, encoding="utf-8-sig"
    )
    (MODEL_DIR / "model_14_mevcut_asof_feature_genisletme_ozet.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
