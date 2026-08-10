"""Dondurulmuş Model 14 L2 C=0,1 adayının DF-B keşifsel karşılaştırması.

Ön kayıt: prompts/veri/50_model14_df_b_karsilastirma_onkayit.md

Kilitli 2025-07..2026-06 test dönemi kullanılmaz. DF-B'nin kısa kapsamı
nedeniyle yalnız 2025-04..2025-06 arasındaki üç rolling origin ölçülebilir;
çıktı model seçimi/terfi kanıtı değildir.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
GORSEL_DIR = MODEL_DIR / "gorseller"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import model_09_dusuk_kapasiteli_nowcast as m09  # noqa: E402
import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import rolling_nowcast as rn  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402

MODEL_ADI = "lojistik_l2_c01"
KILITLI_TEST_BASLANGIC = pd.Period("2025-07", freq="M")
BASLANGIC_AYI = "2024-02"
SON_DEGERLENDIRME_AYI = "2025-06"
ILK_TRAIN_AY_SAYISI = 12
EMBARGO_AY_SAYISI = 2
AKTARILAN_FEATURELAR = [
    "tuketici_guven_endeksi_lag2ay",
    "odmd_otomobil_adet_lag2ay",
]
ANAHTARLAR = ["kesit_tarihi", "hedef_ay", "hafta_sirasi"]


def _snapshot_oku(dosya_adi: str) -> pd.DataFrame:
    veri = pd.read_csv(MODEL_DIR / dosya_adi)
    veri["hedef_ay"] = pd.PeriodIndex(veri["hedef_ay"], freq="M")
    # Feature üretimi veya etiket değerlendirmesinden önce kilitli dönem çıkarılır.
    veri = veri.loc[veri["hedef_ay"] < KILITLI_TEST_BASLANGIC].copy()
    assert (veri["hedef_ay"] < KILITLI_TEST_BASLANGIC).all()
    return veri


def _df_b_model14_featurelarini_tamamla(df_b: pd.DataFrame, df_a: pd.DataFrame) -> pd.DataFrame:
    eksik = sorted(set(AKTARILAN_FEATURELAR) - set(df_b.columns))
    if eksik != sorted(AKTARILAN_FEATURELAR):
        raise AssertionError(f"Beklenen DF-B eksik feature sözleşmesi değişti: {eksik}")

    kaynak = df_a[ANAHTARLAR + AKTARILAN_FEATURELAR].copy()
    if kaynak.duplicated(ANAHTARLAR).any() or df_b.duplicated(ANAHTARLAR).any():
        raise AssertionError("Snapshot birleştirme anahtarları benzersiz değil")
    sonuc = df_b.merge(kaynak, on=ANAHTARLAR, how="left", validate="one_to_one")

    model_aylari = sonuc["hedef_ay"].between(
        pd.Period(BASLANGIC_AYI, freq="M"),
        pd.Period(SON_DEGERLENDIRME_AYI, freq="M"),
    )
    if sonuc.loc[model_aylari, AKTARILAN_FEATURELAR].isna().all(axis=0).any():
        raise AssertionError("Aktarılan Model 14 feature'larından biri tamamen boş")
    return sonuc


def _tahminleri_uret(
    snapshot: pd.DataFrame,
) -> tuple[pd.DataFrame, list[dict], list[dict]]:
    originler = rn.genisleyen_originler(
        BASLANGIC_AYI,
        SON_DEGERLENDIRME_AYI,
        ilk_train_ay_sayisi=ILK_TRAIN_AY_SAYISI,
        embargo_ay_sayisi=EMBARGO_AY_SAYISI,
    )
    kayitlar: list[dict] = []
    fit_denetimi: list[dict] = []

    for fold_no, origin in enumerate(originler, start=1):
        assert origin["degerlendirme"] < KILITLI_TEST_BASLANGIC
        assert max(origin["train"]) <= origin["degerlendirme"] - 3
        train = snapshot[snapshot["hedef_ay"].isin(origin["train"])].copy()
        val = snapshot[
            snapshot["hedef_ay"].eq(origin["degerlendirme"])
            & snapshot["hafta_sirasi"].isin([1, 2, 3, 4])
        ].sort_values("hafta_sirasi").copy()
        if val["hafta_sirasi"].tolist() != [1, 2, 3, 4]:
            raise AssertionError(f"{origin['degerlendirme']}: dört haftalık validation yok")
        if val["etiket"].nunique() != 1:
            raise AssertionError(f"{origin['degerlendirme']}: validation etiketi tekil değil")

        imputer = SimpleImputer(strategy="median", add_indicator=True)
        scaler = StandardScaler()
        tamamen_bos = [
            feature for feature in m14.TEST_FEATURELAR if train[feature].notna().sum() == 0
        ]
        xtr = scaler.fit_transform(imputer.fit_transform(train[m14.TEST_FEATURELAR]))
        xva = scaler.transform(imputer.transform(val[m14.TEST_FEATURELAR]))
        fit_denetimi.append(
            {
                "fold": fold_no,
                "degerlendirme_ayi": str(origin["degerlendirme"]),
                "train_ay_sayisi": len(origin["train"]),
                "train_tamamen_bos_featurelar": tamamen_bos,
                "imputer_cikti_sutun_sayisi": int(xtr.shape[1]),
            }
        )

        model = m09._adaylar()[MODEL_ADI]
        model.fit(xtr, train["etiket"], sample_weight=train["agirlik"])
        tahminler = model.predict(xva)
        for hafta, tahmin in zip(val["hafta_sirasi"], tahminler):
            kayitlar.append(
                {
                    "fold": fold_no,
                    "hedef_ay": str(origin["degerlendirme"]),
                    "train_ay_sayisi": len(origin["train"]),
                    "hafta_sirasi": int(hafta),
                    "gercek": str(val["etiket"].iloc[0]),
                    "tahmin": str(tahmin),
                }
            )
    return pd.DataFrame(kayitlar), originler, fit_denetimi


def _matris_gorseli(metrikler: dict, cikti: Path) -> None:
    etiketler = metrikler["confusion_matrix"]["label_sirasi"]
    matris = metrikler["confusion_matrix"]["matris"]
    fig, ax = plt.subplots(figsize=(7.2, 6.0))
    goruntu = ax.imshow(matris, cmap="Blues")
    ax.set_xticks(range(len(etiketler)), labels=etiketler)
    ax.set_yticks(range(len(etiketler)), labels=etiketler)
    ax.set_xlabel("Tahmin edilen yön")
    ax.set_ylabel("Gerçek yön")
    ax.set_title("Model 14 L2 C=0,1 — DF-B\nKeşifsel, 3 bağımsız ay / 12 haftalık tahmin")
    maksimum = max(max(satir) for satir in matris) if matris else 0
    for i, satir in enumerate(matris):
        for j, deger in enumerate(satir):
            ax.text(
                j,
                i,
                str(int(deger)),
                ha="center",
                va="center",
                color="white" if maksimum and deger > maksimum * 0.55 else "black",
                fontsize=15,
            )
    fig.colorbar(goruntu, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(cikti, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    df_b = _snapshot_oku("model_07_haftalik_nowcast_df_b_snapshot.csv")
    df_a = _snapshot_oku("model_07_haftalik_nowcast_df_a_snapshot.csv")
    birlesik = _df_b_model14_featurelarini_tamamla(df_b, df_a)
    snapshot = m14.feature_hazirla(birlesik)
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()

    tahminler, originler, fit_denetimi = _tahminleri_uret(snapshot)
    metrikler = yd.degerlendir(tahminler["gercek"], tahminler["tahmin"])
    hafta4 = tahminler[tahminler["hafta_sirasi"].eq(4)]
    hafta4_metrikleri = yd.degerlendir(hafta4["gercek"], hafta4["tahmin"])

    matris = pd.DataFrame(
        metrikler["confusion_matrix"]["matris"],
        index=[f"gercek_{x}" for x in yd.FIXED_LABEL_ORDER],
        columns=[f"tahmin_{x}" for x in yd.FIXED_LABEL_ORDER],
    )
    ozet = {
        "deney": "Model 14 L2 C=0,1 — DF-B keşifsel karşılaştırma",
        "durum": "KESIFSEL_DUSUK_N_TERFI_KANITI_DEGIL",
        "model": MODEL_ADI,
        "feature_sayisi": len(m14.TEST_FEATURELAR),
        "featurelar": m14.TEST_FEATURELAR,
        "df_b_eksik_oldugu_icin_df_a_snapshotindan_aktarilan_featurelar": AKTARILAN_FEATURELAR,
        "origin_sayisi_bagimsiz_ay": len(originler),
        "haftalik_tahmin_sayisi": len(tahminler),
        "degerlendirme_aylari": [str(x["degerlendirme"]) for x in originler],
        "ilk_son_train_ay_sayisi": [len(originler[0]["train"]), len(originler[-1]["train"])],
        "embargo_ay_sayisi": EMBARGO_AY_SAYISI,
        "fit_denetimi": fit_denetimi,
        "kilitli_test": "2025-07..2026-06 KULLANILMADI",
        "birincil_4_hafta_havuzlu": metrikler,
        "tanisal_yalniz_hafta4": hafta4_metrikleri,
        "yorum_siniri": (
            "Yalnız üç bağımsız değerlendirme ayı vardır. Dört haftanın havuzlanması "
            "etkin N'yi 12 yapmaz; metrikler genellenebilir performans kanıtı değildir."
        ),
    }

    tahminler.to_csv(
        MODEL_DIR / "model_14_df_b_karsilastirma_tahminleri.csv",
        index=False,
        encoding="utf-8-sig",
    )
    matris.to_csv(
        MODEL_DIR / "model_14_df_b_yon_dogrulugu_matrisi.csv",
        encoding="utf-8-sig",
    )
    (MODEL_DIR / "model_14_df_b_karsilastirma_ozet.json").write_text(
        json.dumps(ozet, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _matris_gorseli(
        metrikler,
        GORSEL_DIR / "model_14_df_b_yon_dogrulugu_matrisi.png",
    )
    print(json.dumps(ozet, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
