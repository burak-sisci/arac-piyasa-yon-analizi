"""Model 12: BDDK taşıt kredisi için iki kollu heuristik ön-eleme.

Bu modül OOF performans üretmez. Model 11 Oracle-B in-sample/permutasyon
protokolünü kontrol kolunda yeniden üretir; ikinci kola M-2 kesimli dört BDDK
dönüşümü ekler. Cari/revize BDDK serisi ilk-yayım vintajının kesin üst sınırı
değildir; hüküm yalnız maliyet önceliklendiren heuristik bir taramadır.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Model nesneleri oluşturulmadan önce tek-thread belirlenimciliği.
for _degisken in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_degisken] = "1"

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import hedef_teshis as ht  # noqa: E402
import model_09_dusuk_kapasiteli_nowcast as m09  # noqa: E402
import model_11_hedef_bilgi_tavani as m11  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

BDDk_URL = (
    "https://www.bddk.org.tr/BultenHaftalik/tr/Gelismis/"
    "KiyaslamaJsonGetir"
)
BDDk_BASLANGIC = "3.01.2014 00:00:00"
BDDk_BITIS = "31.07.2026 00:00:00"
BDDk_FEATURELARI = [
    "bddk_tasit_bakiye_4h_degisim_pct",
    "bddk_tasit_bakiye_13h_degisim_pct",
    "bddk_tasit_bakiye_52h_degisim_pct",
    "bddk_tasit_bakiye_reel_4h_degisim_pct",
]
DOYGUN_MODELLER = {"random_forest_sigin", "hist_gradient_sigin"}
SEED = 410

# BDDK'nin Cuma yerine önceki iş gününde kapattığı haftalar. Eşleştirme yalnız
# veri-kalitesi denetimidir; feature hesaplarına veya karar kapısına girmez.
TATIL_KAYMALARI = {
    "2015-04-30": "1 Mayıs Emek ve Dayanışma Günü",
    "2015-07-16": "Ramazan Bayramı",
    "2015-09-23": "Kurban Bayramı",
    "2015-12-31": "Yılbaşı",
    "2017-05-18": "19 Mayıs Atatürk'ü Anma, Gençlik ve Spor Bayramı",
    "2017-08-31": "Kurban Bayramı",
    "2018-06-14": "Ramazan Bayramı",
    "2018-08-20": "Kurban Bayramı",
    "2019-08-29": "30 Ağustos Zafer Bayramı",
    "2020-04-30": "1 Mayıs Emek ve Dayanışma Günü",
    "2020-07-30": "Kurban Bayramı",
    "2020-12-31": "Yılbaşı",
    "2021-04-22": "23 Nisan Ulusal Egemenlik ve Çocuk Bayramı",
    "2021-05-12": "Ramazan Bayramı",
    "2021-07-19": "Kurban Bayramı",
    "2021-10-28": "29 Ekim Cumhuriyet Bayramı",
    "2022-07-14": "15 Temmuz Demokrasi ve Millî Birlik Günü",
    "2023-04-20": "Ramazan Bayramı",
    "2023-05-18": "19 Mayıs Atatürk'ü Anma, Gençlik ve Spor Bayramı",
    "2023-06-27": "Kurban Bayramı",
    "2024-04-09": "Ramazan Bayramı",
    "2024-08-29": "30 Ağustos Zafer Bayramı",
    "2025-06-05": "Kurban Bayramı",
    "2026-03-19": "Ramazan Bayramı",
    "2026-04-30": "1 Mayıs Emek ve Dayanışma Günü",
    "2026-05-26": "Kurban Bayramı",
}

REFERANS = {
    "lojistik_l2_c01": {
        "tavan_gozlenen": 0.2147571548065723,
        "tavan_null95": 0.4450343895977828,
    },
    "lojistik_l2_c1": {
        "tavan_gozlenen": 0.16897848477598726,
        "tavan_null95": 0.4683733695252251,
    },
    "random_forest_sigin": {
        "tavan_gozlenen": 0.9168817090818534,
        "tavan_null95": 0.9155435038620596,
    },
    "hist_gradient_sigin": {
        "tavan_gozlenen": 1.0,
        "tavan_null95": 1.0,
    },
}


def seri_takvimini_dogrula(seri: pd.DataFrame) -> dict:
    """Tekillik, sıralılık, haftalık aralık ve tatil kaymalarını denetler."""
    tarihler = pd.DatetimeIndex(seri["referans_hafta"])
    if not tarihler.is_unique or not tarihler.is_monotonic_increasing:
        raise RuntimeError("BDDK referans haftaları tekil ve kesin artan olmalı")
    araliklar = pd.Series(tarihler).diff().dropna().dt.days
    aralik_disi = araliklar.loc[~araliklar.between(4, 10)]
    if not aralik_disi.empty:
        raise RuntimeError(
            "BDDK ardışık referans haftası aralığı [4,10] gün dışında: "
            f"{aralik_disi.tolist()}"
        )
    kaymis = [t for t in tarihler if t.dayofweek != 4]
    eslesen = [
        {"referans_hafta": str(t.date()), "tatil": TATIL_KAYMALARI[str(t.date())]}
        for t in kaymis
        if str(t.date()) in TATIL_KAYMALARI
    ]
    eslesmeyen = [str(t.date()) for t in kaymis if str(t.date()) not in TATIL_KAYMALARI]
    return {
        "gozlem_sayisi": int(len(tarihler)),
        "ardisik_aralik_min_gun": int(araliklar.min()),
        "ardisik_aralik_maks_gun": int(araliklar.max()),
        "cuma_disi_hafta_sayisi": len(kaymis),
        "tatille_eslesen_haftalar": eslesen,
        "tatille_eslesmeyen_haftalar": eslesmeyen,
        "eslesmeyen_tatil_kaymasi_bayragi": bool(eslesmeyen),
    }


def bddk_serisini_cek(timeout: int = 30) -> tuple[pd.DataFrame, dict]:
    """BDDK sayfasının kendi ücretsiz JSON ucundan cari/revize seriyi alır."""
    govde = urlencode({
        "dil": "tr",
        "baslangicTarihi": BDDk_BASLANGIC,
        "bitisTarihi": BDDk_BITIS,
        "id": "1.0.5",
        "parabirimi": "TRY",
        "sutun": "3",
        "tarafKodu": "10001",
    }).encode("utf-8")
    istek = Request(
        BDDk_URL,
        data=govde,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "arac-piyasa-yon-analizi/Model12",
        },
    )
    with urlopen(istek, timeout=timeout) as yanit:  # noqa: S310 - sabit resmî URL
        nesne = json.loads(yanit.read().decode("utf-8-sig"))
    tarihler = pd.to_datetime(nesne["XEkseni"], dayfirst=True, errors="raise")
    degerler = pd.to_numeric(pd.Series(nesne["YEkseni"]), errors="raise")
    seri = pd.DataFrame({"referans_hafta": tarihler, "bakiye_milyon_tl": degerler})
    if seri["referans_hafta"].duplicated().any():
        raise RuntimeError("BDDK yanıtında yinelenen referans haftası bulundu")
    seri = seri.sort_values("referans_hafta").reset_index(drop=True)
    if len(seri) < 650:
        raise RuntimeError(f"BDDK kapsamı beklenenden kısa: {len(seri)} hafta")
    takvim_denetimi = seri_takvimini_dogrula(seri)
    if seri["bakiye_milyon_tl"].le(0).any():
        raise RuntimeError("BDDK taşıt kredisi bakiyesi pozitif olmalı")
    return seri, takvim_denetimi


def tufe_birim_ve_lag_dogrula(snapshot: pd.DataFrame) -> dict:
    """TÜFE'nin pct_change*100 ve snapshot'ta lag2 olduğunu kaynak koddan doğrular."""
    tufe_kodu = (REPO_KOKU / "scripts" / "veri" / "asama2_tufe.py").read_text(
        encoding="utf-8"
    )
    snapshot_kodu = (
        REPO_KOKU / "scripts" / "model" / "model_07_haftalik_nowcast_veri_hazirligi.py"
    ).read_text(encoding="utf-8")
    if 'df["tufe_aylik_degisim"] = df["tufe_endeks"].pct_change() * 100' not in tufe_kodu:
        raise RuntimeError("TÜFE yüzde-puan birim kanıtı kaynak kodda bulunamadı")
    if "en_kucuk_aylik_lag=2" not in snapshot_kodu:
        raise RuntimeError("Snapshot lag2 semantiği kaynak kodda bulunamadı")
    deger = pd.to_numeric(snapshot["tufe_aylik_degisim_lag2ay"], errors="coerce").dropna()
    if deger.empty or deger.abs().max() > 30:
        raise RuntimeError("TÜFE aylık değişim değerleri beklenen yüzde-puan aralığında değil")
    return {
        "birim": "yuzde_puani",
        "hesap": "pct_change()*100",
        "lag": "M-2",
        "minimum": float(deger.min()),
        "maksimum": float(deger.max()),
    }


def aylik_bddk_featurelari(
    seri: pd.DataFrame,
    aylar: list[pd.Period],
    tufe_m2: pd.Series,
) -> tuple[pd.DataFrame, dict]:
    """Haftalık seriyi konumsal geri indekslemeyle dört aylık feature'a çevirir."""
    if len(BDDk_FEATURELARI) != 4:
        raise AssertionError("Tam olarak dört BDDK feature'ı ön-kayıtlıdır")
    s = seri.set_index("referans_hafta")["bakiye_milyon_tl"].sort_index()
    if not s.index.is_monotonic_increasing or not s.index.is_unique:
        raise AssertionError("BDDK hafta indeksi sıralı ve tekil olmalı")

    satirlar = []
    for m in aylar:
        m2 = m - 2
        son_gun = m2.end_time.normalize()
        pos = int(s.index.searchsorted(son_gun, side="right") - 1)
        if pos < 52:
            raise AssertionError(f"{m}: 52 haftalık geri bakış yok")
        w0 = s.index[pos]
        if w0 > son_gun or w0.to_period("M") > m2:
            raise AssertionError(f"{m}: M-2 kesimi ihlali ({w0.date()})")

        gecmis = {k: s.index[pos - k] for k in (4, 13, 52)}
        nominal = {4: 28, 13: 91, 52: 364}
        aralik = {k: int((w0 - tarih).days) for k, tarih in gecmis.items()}
        sapma = {k: abs(aralik[k] - nominal[k]) for k in aralik}
        n4 = (float(s.iloc[pos]) / float(s.iloc[pos - 4]) - 1.0) * 100.0
        n13 = (float(s.iloc[pos]) / float(s.iloc[pos - 13]) - 1.0) * 100.0
        n52 = (float(s.iloc[pos]) / float(s.iloc[pos - 52]) - 1.0) * 100.0
        p = float(tufe_m2.loc[m])
        reel4 = ((1.0 + n4 / 100.0) / (1.0 + p / 100.0) - 1.0) * 100.0
        satirlar.append({
            "hedef_ay": m,
            "bddk_capa_haftasi": w0,
            "bddk_m2_son_gun": son_gun,
            "bddk_tasit_bakiye_4h_degisim_pct": n4,
            "bddk_tasit_bakiye_13h_degisim_pct": n13,
            "bddk_tasit_bakiye_52h_degisim_pct": n52,
            "bddk_tasit_bakiye_reel_4h_degisim_pct": reel4,
            "gerceklesen_aralik_4h_gun": aralik[4],
            "gerceklesen_aralik_13h_gun": aralik[13],
            "gerceklesen_aralik_52h_gun": aralik[52],
            "aralik_sapma_4h_7gun_ustu": sapma[4] > 7,
            "aralik_sapma_13h_7gun_ustu": sapma[13] > 7,
            "aralik_sapma_52h_7gun_ustu": sapma[52] > 7,
        })
    sonuc = pd.DataFrame(satirlar)
    nan = {c: int(sonuc[c].isna().sum()) for c in BDDk_FEATURELARI}
    if any(nan.values()):
        raise AssertionError(f"BDDK feature NaN bulundu: {nan}")
    if not sonuc["bddk_capa_haftasi"].le(sonuc["bddk_m2_son_gun"]).all():
        raise AssertionError("M-2 zaman kesimi toplu kontrolde geçmedi")
    denetim = {
        "feature_sayisi": len(BDDk_FEATURELARI),
        "featurelar": BDDk_FEATURELARI,
        "nan_sayilari": nan,
        "origin_sayisi": int(len(sonuc)),
        "ilk_origin": str(sonuc["hedef_ay"].min()),
        "son_origin": str(sonuc["hedef_ay"].max()),
        "ilk_capa": str(sonuc["bddk_capa_haftasi"].min().date()),
        "son_capa": str(sonuc["bddk_capa_haftasi"].max().date()),
        "m1_m_haftasi_kullanildi": False,
        "aralik_sapma_7gun_ustu": {
            "4h": int(sonuc["aralik_sapma_4h_7gun_ustu"].sum()),
            "13h": int(sonuc["aralik_sapma_13h_7gun_ustu"].sum()),
            "52h": int(sonuc["aralik_sapma_52h_7gun_ustu"].sum()),
        },
    }
    return sonuc, denetim


def _adaylar() -> dict:
    modeller = m09._adaylar()
    modeller["random_forest_sigin"].set_params(n_jobs=1)
    return modeller


def permutasyon_matrisi(y_ay: np.ndarray, tekrar: int) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    return np.stack([rng.permutation(y_ay) for _ in range(tekrar)])


def oracle_kolu(
    veri: pd.DataFrame,
    featurelar: list[str],
    perm_matris: np.ndarray,
) -> dict:
    ht.bilgi_maskesini_dogrula(featurelar)
    if any(c.endswith("lag1ay") for c in featurelar):
        raise AssertionError("M-1 feature yasak")
    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    xi = imputer.fit_transform(veri[featurelar])
    xs = scaler.fit_transform(xi)
    y_ay = veri.drop_duplicates("hedef_ay")["etiket"].to_numpy(dtype=object)
    y = np.repeat(y_ay, 4)
    agirlik = np.full(len(y), 0.25)
    cikti = {}
    for ad, model in _adaylar().items():
        x = xs if ad.startswith("lojistik") else xi
        model.fit(x, y, sample_weight=agirlik)
        gozlenen = yd.degerlendir(y, model.predict(x), agirliklar=agirlik)["mcc_gorodkin"]
        null = np.empty(len(perm_matris))
        for i, yp_ay in enumerate(perm_matris):
            yp = np.repeat(yp_ay, 4)
            mp = _adaylar()[ad]
            mp.fit(x, yp, sample_weight=agirlik)
            null[i] = yd.degerlendir(
                yp, mp.predict(x), agirliklar=agirlik
            )["mcc_gorodkin"]
        null95 = float(np.quantile(null, 0.95))
        cikti[ad] = {
            "tavan_gozlenen": float(gozlenen),
            "tavan_null95": null95,
            "marj": float(gozlenen - null95),
            "null_tekrar": int(len(perm_matris)),
            "doygun": ad in DOYGUN_MODELLER,
        }
    return cikti


def harness_dogrula(kontrol: dict) -> dict:
    denetim = {}
    for ad, ref in REFERANS.items():
        farklar = {
            alan: abs(float(kontrol[ad][alan]) - beklenen)
            for alan, beklenen in ref.items()
        }
        en_buyuk = max(farklar.values())
        if ad.startswith("lojistik"):
            gecti = en_buyuk <= 1e-6
            not_dus = 1e-9 < en_buyuk <= 1e-6
        elif ad == "random_forest_sigin":
            gecti = en_buyuk <= 1e-6
            not_dus = False
        else:
            gecti = en_buyuk <= 0.01
            not_dus = 1e-6 < en_buyuk <= 0.01
        denetim[ad] = {
            "farklar": farklar,
            "en_buyuk_mutlak_fark": en_buyuk,
            "gecti": gecti,
            "not_dusuldu": not_dus,
        }
    if not all(x["gecti"] for x in denetim.values()):
        raise RuntimeError(f"Model 11 kontrol harness toleransı aşıldı: {denetim}")
    return denetim


def karar_ver(kontrol: dict, test: dict, kesinlik: str) -> dict:
    birincil = ["lojistik_l2_c01", "lojistik_l2_c1"]
    karsilastirma = {}
    for ad in kontrol:
        delta = float(test[ad]["marj"] - kontrol[ad]["marj"])
        karsilastirma[ad] = {
            "kol1_marj": kontrol[ad]["marj"],
            "kol2_marj": test[ad]["marj"],
            "delta_marj": delta,
            "doygun": ad in DOYGUN_MODELLER,
        }
    gecti = any(test[ad]["marj"] >= 0.15 for ad in birincil)
    zayif = (not gecti) and any(karsilastirma[ad]["delta_marj"] >= 0.15 for ad in birincil)
    if gecti:
        hukum = "ON_ELEME_GECTI"
        sonraki = "VINTAJ_RISKINI_SINIRLA"
    elif zayif:
        hukum = "ON_ELEME_ZAYIF"
        sonraki = "KAPASITE_DUSURULMUS_TEKRAR"
    else:
        hukum = "ON_ELEME_ISARET_YOK"
        sonraki = "BDDk_ONCELIK_DUSURULDU_YENI_AILEYE_GEC"
    return {
        "hukum": hukum,
        "tarama_kesinligi": kesinlik,
        "karsilastirma": karsilastirma,
        "otomatik_sonraki_dal": sonraki,
        "performans_iddiasi": False,
        "bddk_kapandi": False,
    }


def _snapshot_ve_feature_hazirla(
    seri: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict, dict]:
    snapshot = pd.read_csv(MODEL_DIR / "model_07_haftalik_nowcast_df_a_snapshot.csv")
    snapshot["hedef_ay"] = pd.PeriodIndex(snapshot["hedef_ay"], freq="M")
    snapshot = m09._feature_hazirla(snapshot)
    # Kilitli test satırları hesap hattına alınmaz.
    snapshot = snapshot[snapshot["hedef_ay"] <= m11.PENCERE_SON].copy()
    aylar = [o["degerlendirme"] for o in m11._originler()]
    veri = snapshot[
        snapshot["hedef_ay"].isin(aylar) & snapshot["hafta_sirasi"].isin([1, 2, 3, 4])
    ].sort_values(["hedef_ay", "hafta_sirasi"]).copy()
    if not (veri.groupby("hedef_ay").size().eq(4).all() and veri["hedef_ay"].nunique() == 50):
        raise AssertionError("Model 12 tam 50 ay × 4 snapshot kullanmalı")
    tufe_meta = tufe_birim_ve_lag_dogrula(veri)
    tufe = veri.groupby("hedef_ay")["tufe_aylik_degisim_lag2ay"].first()
    if tufe.isna().any():
        raise AssertionError("TÜFE M-2 feature'ında eksik origin var")
    features, feature_meta = aylik_bddk_featurelari(seri, aylar, tufe)
    veri = veri.merge(features[["hedef_ay", *BDDk_FEATURELARI]], on="hedef_ay", how="left", validate="many_to_one")
    if veri[BDDk_FEATURELARI].isna().any().any():
        raise AssertionError("Snapshot birleşiminde BDDK feature eksik")
    return veri, features, feature_meta, tufe_meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tekrar", type=int, default=1000, choices=(500, 1000))
    args = parser.parse_args()
    basla = time.perf_counter()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    seri, takvim_meta = bddk_serisini_cek()
    seri.to_csv(MODEL_DIR / "model_12_bddk_tasit_haftalik_cari.csv", index=False, encoding="utf-8-sig")
    veri, features, feature_meta, tufe_meta = _snapshot_ve_feature_hazirla(seri)
    features_yaz = features.copy()
    features_yaz["hedef_ay"] = features_yaz["hedef_ay"].astype(str)
    features_yaz.to_csv(MODEL_DIR / "model_12_bddk_aylik_features.csv", index=False, encoding="utf-8-sig")

    y_ay = veri.drop_duplicates("hedef_ay")["etiket"].to_numpy(dtype=object)
    perm = permutasyon_matrisi(y_ay, args.tekrar)
    kontrol = oracle_kolu(veri, m09.FEATURELAR, perm)
    harness = harness_dogrula(kontrol)
    test = oracle_kolu(veri, [*m09.FEATURELAR, *BDDk_FEATURELARI], perm)
    karar = karar_ver(kontrol, test, "HEURISTIK")

    sonuc = {
        "model": "Model 12 BDDK heuristik on-eleme",
        "durum": "test_disi_in_sample_permutasyon_taramasi",
        "on_kayit_commit": "061996c",
        "analiz_penceresi": ["2021-03", "2025-04"],
        "test": "2025-07..2026-06 ACILMADI_KILITLI",
        "ag_erisim": {
            "seri_http_cagrisi": 1,
            "revizyon_belgesi_erisim": 2,
            "toplam": 3,
            "butce": 8,
        },
        "bddk_serisi": {
            "gozlem": int(len(seri)),
            "ilk_hafta": str(seri["referans_hafta"].min().date()),
            "son_hafta": str(seri["referans_hafta"].max().date()),
            "birim": "milyon_TL",
            "ilk_yayim_vintaji": False,
            "kaynak": BDDk_URL,
            "takvim_denetimi": takvim_meta,
        },
        "revizyon_bulgusu": {
            "tarama_kesinligi": "HEURISTIK",
            "bulgu": (
                "Genel BDDK politikası haftalık tabloların geriye dönük rutin ve ana "
                "revizyona açık olduğunu söylüyor; taşıt kredisi kalemi için istisna "
                "veya sayısal revizyon sınırı bulunamadı. Revizyon takvimi sayfası "
                "inceleme anında 502 döndürdü."
            ),
            "kaynaklar": [
                "https://www.bddk.org.tr/BultenDosyalari/Home/Index/Haftalik-RevizyonPolitikas%C4%B1",
                "https://www.bddk.org.tr/BultenDosyalari/Home/Index/Haftalik-RevizyonTakvimi",
            ],
        },
        "tufe_birim_lag_denetimi": tufe_meta,
        "feature_denetimi": feature_meta,
        "featurelar_kontrol": m09.FEATURELAR,
        "featurelar_test_ek": BDDk_FEATURELARI,
        "seed": SEED,
        "permutasyon_tekrar": args.tekrar,
        "thread_sayisi": 1,
        "kol1_kontrol": kontrol,
        "harness": harness,
        "kol2_bddk_ekli": test,
        "karar": karar,
        "yorum_siniri": {
            "izinli": (
                "Cari/revize seri ve dört sabit dönüşüm bu protokolde kendi null'ına "
                "karşı tarandı; sonuç yalnız vintaj maliyeti önceliğini etkiler."
            ),
            "yasak": [
                "Temiz vintaj da aynı sonucu verirdi.",
                "BDDK sinyal taşımıyor.",
                "BDDK adayı kapandı.",
                "Bu bir OOF performans veya üretim becerisidir.",
            ],
        },
        "sure_saniye": float(time.perf_counter() - basla),
    }
    yol = MODEL_DIR / "model_12_bddk_tavan_ozet.json"
    yol.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
