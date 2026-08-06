"""MODEL 07 — haftalık güncellenen aylık yön nowcast veri hazırlığı.

Model EĞİTMEZ. DF-A ve DF-B'den pazar cut-off'lu haftalık snapshot tabloları
üretir; bağımsız ay sayısını, sınıf dağılımını, ay-eşit ağırlıkları ve feature
yayım-gecikmesi sözleşmesini denetler.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import haftalik_aylik_nowcast as hn  # noqa: E402
from turkiye_tatil_takvimi import KAYNAK_URLLERI, turkiye_resmi_tatil_agirliklari  # noqa: E402


REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
TARGET = "noter_devir_otomobil_adet"
ESIK_YUZDE = 5.0


def _target_penceresini_kes(df: pd.DataFrame) -> pd.DataFrame:
    tarihler = pd.to_datetime(df["tarih"], errors="raise")
    dolu = df[TARGET].notna()
    if not dolu.any():
        raise ValueError(f"{TARGET} tamamen boş")
    ilk_target_ayi = tarihler[dolu].min().to_period("M")
    return df[tarihler.dt.to_period("M") >= ilk_target_ayi].copy()


def _ozetle(set_adi: str, snapshot: pd.DataFrame) -> dict:
    agirlik_toplamlari = snapshot.groupby("hedef_ay")["agirlik"].sum()
    if not np.allclose(agirlik_toplamlari.to_numpy(), 1.0):
        raise AssertionError(f"{set_adi}: ay ağırlıkları 1 toplamıyor")

    model_featurelari = hn.model_feature_sutunlari(snapshot)
    if TARGET in model_featurelari or any(c.endswith("_lag1ay") for c in model_featurelari):
        raise AssertionError(f"{set_adi}: cari target veya lag1 sızıntısı bulundu")

    ay_bazli = snapshot.sort_values("kesit_tarihi").groupby("hedef_ay").first()
    gecerli = ay_bazli[ay_bazli["etiket"].isin(hn.FIXED_LABEL_ORDER)]
    dagilim = gecerli["etiket"].value_counts().to_dict()
    snapshot_dagilimi = snapshot.groupby("hedef_ay").size().value_counts().sort_index().to_dict()
    etiketli_snapshot = snapshot[snapshot["etiket"].isin(hn.FIXED_LABEL_ORDER)]

    return {
        "veri_seti": set_adi,
        "snapshot_sayisi": int(len(snapshot)),
        "etiketli_snapshot_sayisi": int(len(etiketli_snapshot)),
        "bagimsiz_ay_sayisi": int(len(gecerli)),
        "hedef_ay_araligi": [str(snapshot["hedef_ay"].min()), str(snapshot["hedef_ay"].max())],
        "etiketli_ay_araligi": [str(gecerli.index.min()), str(gecerli.index.max())],
        "sinif_dagilimi_bagimsiz_ay": {
            sinif: int(dagilim.get(sinif, 0)) for sinif in hn.FIXED_LABEL_ORDER
        },
        "ay_basina_snapshot_sayisi_dagilimi": {
            str(int(k)): int(v) for k, v in snapshot_dagilimi.items()
        },
        "ay_agirligi_min_max": [
            float(agirlik_toplamlari.min()),
            float(agirlik_toplamlari.max()),
        ],
        "model_feature_sayisi": int(len(model_featurelari)),
        "model_featurelari": model_featurelari,
        "n50_durumu": "gecer" if len(gecerli) >= 50 else "kesifsel_n50_alti",
    }


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df_a = pd.read_csv(DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv", low_memory=False)
    df_b = pd.read_csv(DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv", low_memory=False)
    df_a = _target_penceresini_kes(df_a)
    df_b = _target_penceresini_kes(df_b)

    # DF-B'de gerçek günlük feature yoktu. Aynı tarihli DF-A USD/TRY serisi,
    # yalnız tarih anahtarıyla eklenir; target veya başka DF-A sütunu taşınmaz.
    usd = df_a[["tarih", "usdtry_orta"]].copy()
    df_b = df_b.merge(usd, on="tarih", how="left", validate="one_to_one")

    aylik_a = [
        "tufe_aylik_degisim",
        "tufe_yillik_degisim",
        "odmd_otomobil_adet",
        "tuketici_guven_endeksi",
    ]
    aylik_b = [
        c for c in df_b.columns
        if c not in {
            "tarih", TARGET, "noter_devir_toplam_adet", "usdtry_orta",
            # Ekonomik lag ile yayın lag'ini üst üste bindirmemek için bu
            # önceden gecikmeli sütunlar Stage 1 snapshot'ına alınmaz.
            "tasit_kredisi_faiz_lag4ay", "politika_faizi_lag5ay",
        }
    ]

    snapshots = {
        "DF-A": hn.haftalik_snapshot_uret(
            df_a,
            gunluk_feature_sutunlari=["usdtry_orta"],
            aylik_feature_sutunlari=aylik_a,
            esik_yuzde=ESIK_YUZDE,
            en_kucuk_aylik_lag=2,
            target_lag_aylari=[2, 3, 12],
            tatil_tarihleri=turkiye_resmi_tatil_agirliklari(2018, 2026),
        ),
        "DF-B": hn.haftalik_snapshot_uret(
            df_b,
            gunluk_feature_sutunlari=["usdtry_orta"],
            aylik_feature_sutunlari=aylik_b,
            esik_yuzde=ESIK_YUZDE,
            en_kucuk_aylik_lag=2,
            target_lag_aylari=[2, 3, 12],
            tatil_tarihleri=turkiye_resmi_tatil_agirliklari(2018, 2026),
        ),
    }

    ozetler = {}
    for set_adi, snapshot in snapshots.items():
        dosya_adi = f"model_07_haftalik_nowcast_{set_adi.lower().replace('-', '_')}_snapshot.csv"
        yazilacak = snapshot.copy()
        yazilacak["hedef_ay"] = yazilacak["hedef_ay"].astype(str)
        yazilacak.to_csv(MODEL_DIR / dosya_adi, index=False, encoding="utf-8-sig")
        ozetler[set_adi] = _ozetle(set_adi, snapshot)

    # DF-A için yalnız TASLAK geliştirme sözleşmesi. Pusula'nın açık reddi
    # nedeniyle test dönemi henüz kilitli değildir; tatil/yayım takvimi ve
    # etiket sözleşmesi kapandıktan sonra Model 08 öncesi yeniden onaylanır.
    split_a = hn.nowcast_uc_parcali_split_olustur(
        "2019-01", "2024-02",
        "2024-05", "2025-04",
        "2025-07", "2026-06",
        embargo_ay_sayisi=2,
    )
    ozetler["DF-A"]["taslak_split_kilitli_degil"] = {
        parca: [str(aylar[0]), str(aylar[-1]), len(aylar)]
        for parca, aylar in split_a.items()
    }
    ozetler["DF-B"]["split_durumu"] = (
        "Bağımsız ay N<50; doğrulayıcı sabit test ayrılmadı, yalnız keşifsel rolling analiz."
    )
    ozetler["feature_yayim_defteri"] = {
        "usdtry_orta": {
            "dogal_frekans": "gunluk_is_gunu",
            "snapshot_kurali": "cari ay başlangıcından pazar cut-off'una kadar",
            "as_of": "cut-off veya öncesindeki son dolu iş günü",
        },
        "aylik_featurelar": {
            "dogal_frekans": "aylik/ayliklastirilmis",
            "snapshot_kurali": "en az iki takvim ayı gecikmeli",
            "as_of": "tahmin ayı başlangıcından önce bilindiği varsayılan konservatif lag2",
        },
        TARGET: {
            "dogal_frekans": "aylik",
            "snapshot_kurali": "cari değer feature değildir; yalnız lag2/lag3/lag12",
            "etiket": "cari ay / önceki ay yüzde değişimi; ±%5 dahil stable",
        },
    }
    ozetler["tatil_takvimi"] = {
        "kapsam": "2018-2026",
        "tam_ve_yarim_gun_agirliklari": True,
        "kaynaklar": KAYNAK_URLLERI,
    }
    ozetler["uyarilar"] = [
        "Hafta snapshot'ları bağımsız örnek değildir; etkin N bağımsız ay sayısıdır.",
        "DF-B N<50 olduğu için keşifseldir.",
        "Tarihsel kesin yayın tarihleri veri setinde yoktur; lag2 güvenli ilk sürüm varsayımıdır.",
        "Taslak test dönemi kilitli değildir; Pusula bu aşamada kilitlemeyi açıkça reddetti.",
        "Bu script model eğitmez ve performans iddiası üretmez.",
    ]

    with open(MODEL_DIR / "model_07_haftalik_nowcast_veri_ozeti.json", "w", encoding="utf-8") as f:
        json.dump(ozetler, f, ensure_ascii=False, indent=2)

    print(json.dumps(ozetler, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
