"""Model 10: Pusula yonetiminde test-disi rolling-origin performans olcumu."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_09_dusuk_kapasiteli_nowcast as m09  # noqa: E402
import nowcast_baseline as nb  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

TEKRAR = 2000
MODEL_ADLARI = list(m09._adaylar())
BASELINE_ADLARI = ["train_cogunlugu", "persistence_m_eksi_2", "seasonal_t_eksi_12"]


def _nokta(gercek: np.ndarray, tahmin: np.ndarray) -> dict:
    m = yd.degerlendir(gercek.reshape(-1), tahmin.reshape(-1))
    return {"mcc": m["mcc_gorodkin"], "macro_f1": m["macro_f1"], "accuracy": m["accuracy"]}


def _ci(dizi: np.ndarray, alfa: float = 0.05) -> list[float]:
    return [float(np.quantile(dizi, alfa / 2)), float(np.quantile(dizi, 1 - alfa / 2))]


def _matrisler(tahmin_df: pd.DataFrame) -> tuple[np.ndarray, dict[str, np.ndarray], list[str]]:
    aylar = sorted(tahmin_df["hedef_ay"].unique())
    yaklasimlar = tahmin_df["yaklasim"].drop_duplicates().tolist()
    gercek = None
    tahminler = {}
    for ad in yaklasimlar:
        alt = tahmin_df[tahmin_df["yaklasim"].eq(ad)].pivot(
            index="hedef_ay", columns="hafta_sirasi", values=["gercek", "tahmin"]
        ).reindex(aylar)
        if gercek is None:
            gercek = alt["gercek"][[1, 2, 3, 4]].to_numpy(dtype=object)
        tahminler[ad] = alt["tahmin"][[1, 2, 3, 4]].to_numpy(dtype=object)
    return gercek, tahminler, aylar


def _rolling_tahminleri(snapshot: pd.DataFrame) -> tuple[pd.DataFrame, list[dict], dict]:
    aylik_etiket = snapshot.drop_duplicates("hedef_ay").set_index("hedef_ay")["etiket"]
    originler = rn.genisleyen_originler(
        "2019-01", "2025-04", ilk_train_ay_sayisi=24, embargo_ay_sayisi=2
    )
    kayitlar = []
    denetim = {"on_isleme_fit_sayisi": 0, "model_fit_sayisi": 0}
    for fold_no, origin in enumerate(originler, start=1):
        assert max(origin["train"]) <= origin["degerlendirme"] - 3
        assert origin["embargo"] == [
            origin["degerlendirme"] - 2, origin["degerlendirme"] - 1
        ]
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
        xtr_imp = imputer.fit_transform(train[m09.FEATURELAR])
        xva_imp = imputer.transform(val[m09.FEATURELAR])
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


def main() -> None:
    snapshot = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    snapshot["hedef_ay"] = pd.PeriodIndex(snapshot["hedef_ay"], freq="M")
    snapshot = m09._feature_hazirla(snapshot)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    tahmin_df, originler, denetim = _rolling_tahminleri(snapshot)
    gercek, tahminler, aylar = _matrisler(tahmin_df)
    assert len(aylar) == 50 and max(aylar) == "2025-04"

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

    ref = "persistence_m_eksi_2"
    fark_dagilimlari = {
        ad: blok["dagilimlar"][ad]["mcc"] - blok["dagilimlar"][ref]["mcc"]
        for ad in MODEL_ADLARI
    }
    p_ham = {
        ad: float((1 + np.sum(fark_dagilimlari[ad] <= 0)) / (TEKRAR + 1))
        for ad in MODEL_ADLARI
    }
    holm = rn.holm_bonferroni(p_ham, alfa=0.05)
    # Holm rank'ine karsilik gelen tek-yonlu esik, eszamanli alt sinir olarak kaydedilir.
    for ad in MODEL_ADLARI:
        alfa_ad = holm[ad]["holm_esik"]
        holm[ad]["delta_mcc_nokta"] = genel[ad]["nokta"]["mcc"] - genel[ref]["nokta"]["mcc"]
        holm[ad]["delta_mcc_holm_alt_sinir"] = float(np.quantile(fark_dagilimlari[ad], alfa_ad))
        holm[ad]["delta_macro_f1_nokta"] = (
            genel[ad]["nokta"]["macro_f1"] - genel[ref]["nokta"]["macro_f1"]
        )

    # Bir-yil-disarida jackknife, havuzlanmis genel MCC farki.
    yillar = np.array([int(x[:4]) for x in aylar])
    jackknife = {}
    for ad in MODEL_ADLARI:
        farklar = {}
        for yil in sorted(set(yillar)):
            tut = yillar != yil
            farklar[str(yil)] = (
                _nokta(gercek[tut], tahminler[ad][tut])["mcc"]
                - _nokta(gercek[tut], tahminler[ref][tut])["mcc"]
            )
        jackknife[ad] = {"yil_disarida_delta_mcc": farklar,
                         "isaret_her_yil_pozitif": all(x > 0 for x in farklar.values())}

    # Hafta tanisi terfi ailesinin disindadir.
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
        kosullar = {
            "a_holm_alt_sinir_pozitif": holm[ad]["h0_reddedildi"] and holm[ad]["delta_mcc_holm_alt_sinir"] > 0,
            "b_delta_mcc_en_az_005": holm[ad]["delta_mcc_nokta"] >= 0.05,
            "c_macro_f1_farki_pozitif": holm[ad]["delta_macro_f1_nokta"] > 0,
            "d_jackknife_isaret_korunuyor": jackknife[ad]["isaret_her_yil_pozitif"],
        }
        terfi[ad] = {"kosullar": kosullar, "terfi": all(kosullar.values())}

    # CI yari genisligi: bu tasarimin pratik ayirma gucunun veri-temelli gostergesi.
    ci_yari_genislik = {
        ad: float((_ci(fark_dagilimlari[ad])[1] - _ci(fark_dagilimlari[ad])[0]) / 2)
        for ad in MODEL_ADLARI
    }
    sonuc = {
        "yonetici": "Pusula", "protokol": "effort=max karar kurallari",
        "durum": "test_disi_rolling_origin", "origin_sayisi": 50,
        "degerlendirme_ay_araligi": [aylar[0], aylar[-1]],
        "ilk_son_train_ay_sayisi": [len(originler[0]["train"]), len(originler[-1]["train"])],
        "embargo_ay_sayisi": 2, "bootstrap_tekrar": TEKRAR,
        "birincil_birim": "4 hafta havuzlu; her ay toplam agirlik=1",
        "assertion_denetimi": denetim,
        "gercek_sinif_eksik_cekilis_orani_blok4": blok["gercek_sinif_eksik_cekilis_orani"],
        "gercek_sinif_eksik_cekilis_orani_iid": iid["gercek_sinif_eksik_cekilis_orani"],
        "tahmin_dejenere_cekilis_orani_blok4": blok["tahmin_dejenere_cekilis_orani"],
        "bootstrap_sinir_notu": (
            "Hareketli bloklar dairesel degildir; son uc ay, blok baslangici olamadigi "
            "icin hafif eksik orneklenir. Ortak indeksli esli farklarda etkisi sinirlidir."
        ),
        "genel_metrikler": genel, "holm_aile_4_model": holm,
        "yil_jackknife": jackknife, "hafta_tanisi": hafta,
        "terfi_karari_ham": terfi,
        "ci_yari_genislik_saptama_gucu_gostergesi": ci_yari_genislik,
        "herhangi_terfi": any(x["terfi"] for x in terfi.values()),
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
    }
    tahmin_df.to_csv(MODEL_DIR / "model_10_rolling_origin_tahminleri.csv",
                     index=False, encoding="utf-8-sig")
    (MODEL_DIR / "model_10_rolling_origin_ozet.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
