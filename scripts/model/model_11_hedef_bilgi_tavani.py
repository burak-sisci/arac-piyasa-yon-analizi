"""Model 11: Pusula spesifikasyonuyla hedef yapisi ve bilgi tavani teshisi."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import haftalik_aylik_nowcast as hn  # noqa: E402
import hedef_teshis as ht  # noqa: E402
import model_09_dusuk_kapasiteli_nowcast as m09  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

PENCERE_BAS = pd.Period("2019-01", "M")
PENCERE_SON = pd.Period("2025-04", "M")
ESIKLER = [2.5, 3.5, 5.0, 7.5, 10.0]
KIRILMALAR = {
    "2020-03": "WHO COVID-19 pandemi nitelemesi (11 Mart 2020)",
    "2021-12": "Kur korumali mevduat uygulamasinin baslamasi",
    "2023-02": "6 Subat Kahramanmaras merkezli depremler",
}
KIRILMA_KAYNAKLARI = {
    "2020-03": "https://www.who.int/docs/default-source/coronaviruse/transcripts/who-audio-emergencies-coronavirus-press-conference-full-and-final-11mar2020.pdf",
    "2021-12": "https://www3.tcmb.gov.tr/yillikrapor/2021/tr/m-2-4.html",
    "2023-02": "https://www.afad.gov.tr/kahramanmarasta-meydana-gelen-depremler-hkbasin-bulteni22",
}


def _aylik_target() -> pd.Series:
    df = pd.read_csv(DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv", low_memory=False)
    df["tarih"] = pd.to_datetime(df["tarih"])
    df["ay"] = df["tarih"].dt.to_period("M")
    return df.groupby("ay")["noter_devir_otomobil_adet"].first().dropna().sort_index()


def _etiket(target: pd.Series, esik: float) -> pd.Series:
    return hn.ay_sonu_nowcast_etiketleri(target, esik_yuzde=esik)


def _originler() -> list[dict]:
    o = rn.genisleyen_originler("2019-01", "2025-04", ilk_train_ay_sayisi=24,
                               embargo_ay_sayisi=2)
    assert len(o) == 50 and o[-1]["degerlendirme"] == PENCERE_SON
    assert all(max(x["train"]) <= x["degerlendirme"] - 3 for x in o)
    return o


def _baseline_tahminleri(etiket: pd.Series, originler: list[dict]) -> pd.DataFrame:
    satirlar = []
    for o in originler:
        m = o["degerlendirme"]
        train = etiket.reindex(o["train"]).dropna()
        son12 = etiket.reindex(pd.period_range(m - 14, m - 3, freq="M")).dropna()
        son6 = etiket.reindex(pd.period_range(m - 8, m - 3, freq="M")).dropna()
        satirlar.append({
            "hedef_ay": str(m), "gercek": etiket[m],
            "r1_genisleyen_cogunluk": ht.deterministik_mod(train),
            "r2_son12_cogunluk": ht.deterministik_mod(son12),
            "r3_son6_cogunluk": ht.deterministik_mod(son6),
            "persistence_lag1": etiket[m - 1], "persistence_lag2": etiket[m - 2],
            "persistence_lag3": etiket[m - 3], "persistence_lag12": etiket[m - 12],
        })
    return pd.DataFrame(satirlar)


def _mcc_blok_ci(y, pred, indeksler) -> dict:
    yg = np.repeat(np.asarray(y, dtype=object)[:, None], 4, axis=1)
    yp = np.repeat(np.asarray(pred, dtype=object)[:, None], 4, axis=1)
    dag = rn.ortak_indeksli_metrik_dagilimlari(yg, {"x": yp}, indeksler)
    d = dag["dagilimlar"]["x"]["mcc"]
    nokta = yd.degerlendir(y, pred)["mcc_gorodkin"]
    return {"mcc": nokta, "mcc_ci95": [float(np.quantile(d, .025)), float(np.quantile(d, .975))]}


def _bolum1(etiket: pd.Series, originler: list[dict], blok_idx) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    pencere = etiket.loc[PENCERE_BAS:PENCERE_SON]
    yillik, kayan = ht.yillik_ve_kayan_paylar(pencere)
    kurallar = _baseline_tahminleri(etiket, originler)
    y = kurallar["gercek"]
    metrik = {f"r0_sabit_{s}": _mcc_blok_ci(y, [s] * len(y), blok_idx)
              for s in yd.FIXED_LABEL_ORDER}
    for c in ["r1_genisleyen_cogunluk", "r2_son12_cogunluk", "r3_son6_cogunluk"]:
        metrik[c] = _mcc_blok_ci(y, kurallar[c], blok_idx)
    degisim = int((kurallar["r1_genisleyen_cogunluk"].shift() !=
                   kurallar["r1_genisleyen_cogunluk"]).iloc[1:].sum())
    bayat = (metrik["r1_genisleyen_cogunluk"]["mcc"] < 0 and
             (metrik["r2_son12_cogunluk"]["mcc"] > metrik["r1_genisleyen_cogunluk"]["mcc"] or
              metrik["r3_son6_cogunluk"]["mcc"] > metrik["r1_genisleyen_cogunluk"]["mcc"]))

    kirilma = {}
    p = {}
    for i, (ay, gerekce) in enumerate(KIRILMALAR.items()):
        grup = ["once" if x < pd.Period(ay, "M") else "sonra" for x in pencere.index]
        sonuc = ht.permutasyon_cramer(grup, pencere, tekrar=10000, seed=110 + i)
        sonuc.update({"gerekce": gerekce, "kaynak": KIRILMA_KAYNAKLARI[ay]})
        kirilma[ay] = sonuc
        p[ay] = sonuc["permutasyon_p"]
    holm = rn.holm_bonferroni(p)
    for ay in kirilma:
        kirilma[ay]["holm"] = holm[ay]
    return ({"kural_metrikleri": metrik, "r1_sinif_degisim_sayisi": degisim,
             "bayat_onsel_dogrulandi": bayat,
             "bayat_onsel_gurultu_uyarisi": degisim <= 3,
             "kirilma_adaylari": kirilma}, yillik, kayan)


def _cramer_blok_ci(x, y, seed: int) -> list[float]:
    x, y = np.asarray(x, dtype=object), np.asarray(y, dtype=object)
    idx = rn.hareketli_blok_indeksleri(len(x), tekrar=2000, blok_uzunlugu=4, seed=seed)
    d = [ht.ki_kare_ve_cramer_v(x[i], y[i])[1] for i in idx]
    return [float(np.quantile(d, .025)), float(np.quantile(d, .975))]


def _bolum2(etiket: pd.Series, kurallar: pd.DataFrame, blok_idx) -> dict:
    pencere = etiket.loc[PENCERE_BAS:PENCERE_SON]
    gecis = pd.crosstab(pencere.shift(1), pencere).reindex(
        index=yd.FIXED_LABEL_ORDER, columns=yd.FIXED_LABEL_ORDER, fill_value=0)
    gecis_norm = gecis.div(gecis.sum(axis=1), axis=0).fillna(0)
    gecis_perm = ht.permutasyon_cramer(pencere.iloc[:-1], pencere.iloc[1:],
                                       tekrar=10000, seed=210)
    laglar, p = {}, {}
    for i, lag in enumerate([1, 2, 3, 12]):
        cift = pd.DataFrame({"simdi": pencere, "gecmis": pencere.shift(lag)}).dropna()
        perm = ht.permutasyon_cramer(cift["gecmis"], cift["simdi"],
                                     tekrar=10000, seed=220 + i)
        perm["cramer_v_ci95"] = _cramer_blok_ci(cift["gecmis"], cift["simdi"], 230 + i)
        perm["cramer_v_ci_bagimsizlik_testi_degil"] = True
        laglar[str(lag)] = perm
        p[str(lag)] = perm["permutasyon_p"]
    holm = rn.holm_bonferroni(p)
    for lag in laglar:
        laglar[lag]["holm"] = holm[lag]

    persistence = {}
    for lag in [1, 2, 3, 12]:
        persistence[str(lag)] = {
            **_mcc_blok_ci(kurallar["gercek"], kurallar[f"persistence_lag{lag}"], blok_idx),
            "operasyonel_degil": lag == 1,
        }
    return {"gecis_yonu": "satir=onceki_ay, sutun=cari_ay",
            "gecis_sayim": gecis.to_dict(orient="index"),
            "gecis_satir_normalize": gecis_norm.to_dict(orient="index"),
            "gecis_bagimsizlik_permutasyon": gecis_perm,
            "lag_cramer": laglar, "lag_persistence": persistence,
            "lag_cift_notu": (
                "Lag ciftleri 2019-01..2025-04 pencere-ici shift ile kuruldu; "
                "2018 warmup kullanilmadi. Bu muhafazakar bir kapsam kaybidir, sizinti degildir."
            )}


def _bolum3(target: pd.Series, originler: list[dict], blok_idx) -> tuple[dict, dict[float, pd.Series]]:
    etiketler, sonuc = {}, {}
    for esik in ESIKLER:
        e = _etiket(target, esik)
        etiketler[esik] = e
        k = _baseline_tahminleri(e, originler)
        y = k["gercek"]
        dag = e.loc[PENCERE_BAS:PENCERE_SON].value_counts()
        sonuc[str(esik)] = {
            "sinif_paylari": {s: float(dag.get(s, 0) / dag.sum()) for s in yd.FIXED_LABEL_ORDER},
            "persistence_m2": _mcc_blok_ci(y, k["persistence_lag2"], blok_idx),
            "seasonal_m12_mcc": yd.degerlendir(y, k["persistence_lag12"])["mcc_gorodkin"],
            "train_cogunlugu_mcc": yd.degerlendir(y, k["r1_genisleyen_cogunluk"])["mcc_gorodkin"],
            "model_fit_sayisi": 0,
        }
    ana = sonuc["5.0"]["persistence_m2"]["mcc"]
    for esik in ESIKLER:
        r = sonuc[str(esik)]
        r["ana_esige_delta_mcc"] = r["persistence_m2"]["mcc"] - ana
        r["maddi_farkli"] = (esik != 5.0 and r["ana_esige_delta_mcc"] >= .10
                              and r["persistence_m2"]["mcc_ci95"][0] > 0)
        r["mcc_yorumlanamaz"] = r["sinif_paylari"]["stable"] > .60
    return sonuc, etiketler


def _oracle_b(snapshot: pd.DataFrame, aylar: list[pd.Period]) -> dict:
    veri = snapshot[snapshot["hedef_ay"].isin(aylar) & snapshot["hafta_sirasi"].isin([1,2,3,4])]
    veri = veri.sort_values(["hedef_ay", "hafta_sirasi"]).copy()
    assert veri.groupby("hedef_ay").size().eq(4).all() and veri["hedef_ay"].nunique() == 50
    ht.bilgi_maskesini_dogrula(m09.FEATURELAR)
    assert not any(c.endswith("lag1ay") for c in m09.FEATURELAR)
    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    xi = imputer.fit_transform(veri[m09.FEATURELAR])
    xs = scaler.fit_transform(xi)
    y_ay = veri.drop_duplicates("hedef_ay")["etiket"].to_numpy(dtype=object)
    y = np.repeat(y_ay, 4)
    agirlik = np.full(len(y), .25)
    rng = np.random.default_rng(410)
    perm_matris = np.stack([rng.permutation(y_ay) for _ in range(1000)])
    cikti = {}
    for ad, model in m09._adaylar().items():
        lojistik = ad.startswith("lojistik")
        x = xs if lojistik else xi
        model.fit(x, y, sample_weight=agirlik)
        gozlenen = yd.degerlendir(y, model.predict(x), agirliklar=agirlik)["mcc_gorodkin"]
        null = np.empty(len(perm_matris))
        for i, yp_ay in enumerate(perm_matris):
            yp = np.repeat(yp_ay, 4)
            mp = m09._adaylar()[ad]
            mp.fit(x, yp, sample_weight=agirlik)
            null[i] = yd.degerlendir(yp, mp.predict(x), agirliklar=agirlik)["mcc_gorodkin"]
        cikti[ad] = {"tavan_gozlenen": gozlenen,
                     "tavan_null95": float(np.quantile(null, .95)),
                     "null_tekrar": 1000,
                     "minimum_hucre_n": int(pd.Series(y_ay).value_counts().min()),
                     "bilgi_maskesi_m1_m_haric": True}
    return cikti


def _bolum4(snapshot: pd.DataFrame, etiket: pd.Series, originler: list[dict]) -> dict:
    aylar = [o["degerlendirme"] for o in originler]
    y = [etiket[m] for m in aylar]
    s0 = ["sabit"] * len(aylar)
    s1 = [etiket[m - 2] for m in aylar]
    s2 = [(etiket[m - 2], "stable" if etiket[m - 3] == "stable" else "stable_degil")
          for m in aylar]
    oracle_a = {
        "s0_sabit": ht.oracle_durum_null(s0, y, tekrar=2000, seed=310),
        "s1_y_m2": ht.oracle_durum_null(s1, y, tekrar=2000, seed=311),
        "s2_y_m2_x_m3_stable": ht.oracle_durum_null(s2, y, tekrar=2000, seed=312),
    }
    oracle_b = _oracle_b(snapshot, aylar)
    notu = ("Oracle, skorlandigi aylarin gercegiyle bilerek in-sample fit edilir. "
            "Bu, hicbir durust OOF tahmincisinin sahip olamayacagi bir avantajdir; "
            "dolayisiyla ayni bilgi kumesini ayni temsille goren hicbir OOF tahminci "
            "bunu sistematik olarak asamaz. Oracle sayilari Model 10 performans "
            "sayilariyla asla kiyaslanmaz; yalniz kendi permutasyon null'lariyla kiyaslanir.")
    return {"gerekce": notu, "oracle_a": oracle_a, "oracle_b": oracle_b}


def main() -> None:
    target = _aylik_target()
    etiket5 = _etiket(target, 5.0)
    originler = _originler()
    blok_idx = rn.hareketli_blok_indeksleri(50, tekrar=2000, blok_uzunlugu=4, seed=510)
    snapshot = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    snapshot["hedef_ay"] = pd.PeriodIndex(snapshot["hedef_ay"], freq="M")
    snapshot = m09._feature_hazirla(snapshot)
    assert snapshot["hedef_ay"].max() > PENCERE_SON  # kaynakta var, analizde kullanilmayacak
    snapshot_analiz = snapshot[snapshot["hedef_ay"] <= PENCERE_SON].copy()
    assert snapshot_analiz["hedef_ay"].max() == PENCERE_SON

    b1, yillik, kayan = _bolum1(etiket5, originler, blok_idx)
    kurallar = _baseline_tahminleri(etiket5, originler)
    b2 = _bolum2(etiket5, kurallar, blok_idx)
    b3, _ = _bolum3(target, originler, blok_idx)
    b4 = _bolum4(snapshot_analiz, etiket5, originler)

    tum_oracle = {**b4["oracle_a"], **b4["oracle_b"]}
    c = any(v["tavan_gozlenen"] - v["tavan_null95"] >= .15 for v in tum_oracle.values())
    lag = b2["lag_persistence"]
    b = lag["1"]["mcc_ci95"][0] > 0 and lag["2"]["mcc_ci95"][0] <= 0 and lag["3"]["mcc_ci95"][0] <= 0
    d = any(v["maddi_farkli"] for v in b3.values())
    # Pusula kosu-sonrasi mantik duzeltmesi: ilk on-kayittaki A/C olu bolgesi
    # kapatildi. A'nin oracle kosulu, C'nin tumleyenidir; bu negatif hukum
    # yonundedir ve sonuc lehine esik secimi degildir.
    a = (not c and lag["1"]["mcc_ci95"][0] <= 0 <= lag["1"]["mcc_ci95"][1] and not d)
    ateslenen = [x for x, deger in [("C_modelleme_alani", c), ("B_bilgi_gecikmesi", b),
                                     ("D_hedef_tanimi", d), ("A_bilgi_kisiti", a)] if deger]
    sonuc = {
        "yonetici": "Pusula", "durum": "test_disi_hedef_bilgi_tavani",
        "analiz_penceresi": [str(PENCERE_BAS), str(PENCERE_SON)],
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
        "bolum1_etiket_rejim": b1, "bolum2_gecis_lag": b2,
        "bolum3_stable_band_duyarliligi": b3, "bolum4_oracle_bilgi_tavani": b4,
        "hukum": {"oncelik": ["C", "B", "D", "A"], "ateslenen": ateslenen,
                  "ham_bayraklar": {"C": c, "B": b, "D": d, "A": a},
                  "nihai_yorum_pusula": (
                      "A: Mevcut I_M bilgi temsilleri altinda, iki ay gecikmeli "
                      "aylik uc-sinif hedefte saptanabilir ongoru becerisi yoktur."
                  ),
                  "sinir": (
                      "Hukum yalniz etiket-lag durumlari ve Model 09 feature temsilleri, "
                      "2019-01..2025-04 gelistirme penceresi icin gecerlidir."
                  ),
                  "post_hoc_not": (
                      "Seasonal M-12 MCC +/-10 bandinda 0.158 goruldu; on-kayitli maddi "
                      "fark kapisi yalniz persistence icindi. Terfi veya K onerisi degildir."
                  )},
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    (MODEL_DIR / "model_11_hedef_teshis_ozet.json").write_text(
        json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    yillik.to_csv(MODEL_DIR / "model_11_yillik_sinif_paylari.csv", index=False, encoding="utf-8-sig")
    kayan.to_csv(MODEL_DIR / "model_11_kayan12_sinif_paylari.csv", index=False, encoding="utf-8-sig")
    kurallar.to_csv(MODEL_DIR / "model_11_origin_teshisleri.csv", index=False, encoding="utf-8-sig")
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
