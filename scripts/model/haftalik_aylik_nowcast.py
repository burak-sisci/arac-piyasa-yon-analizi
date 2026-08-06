"""Haftalık güncellenen aylık noter-devir yönü nowcast veri katmanı.

Bu modül model eğitmez. Aylık ``noter_devir_otomobil_adet`` target'ını
haftalıkmış gibi bölmeden, her pazartesi üretilecek tahmin için bir önceki
pazar gününü bilgi kesim tarihi (cut-off) kabul eden snapshot'lar üretir.

Temel sözleşme:

* Etiket, içinde bulunulan ayın noter otomobil devir adedinin bir önceki aya
  göre ``down/stable/up`` yönüdür.
* Aynı aya ait haftalık snapshot'lar aynı target gözlemini paylaşır; her
  snapshot'ın ağırlığı o aydaki snapshot sayısının tersidir. Böylece her ayın
  toplam eğitim/değerlendirme ağırlığı tam 1 olur.
* Günlük feature'lar yalnız cut-off tarihine kadar olan cari-ay verisinden
  hesaplanır.
* Tarihsel yayım takvimi eksik aylık feature'lar ve target geçmişi için
  varsayılan en küçük gecikme iki takvim ayıdır. Lag-1 bilinçli olarak yoktur.
* Target'ın cari ay değeri snapshot feature'larına hiçbir zaman girmez.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

import numpy as np
import pandas as pd

from yon_degerlendirme import FIXED_LABEL_ORDER, yon_etiketi


def _aylik_seri(df: pd.DataFrame, ay_sutunu: str, deger_sutunu: str) -> pd.Series:
    """Ay içinde tek değer taşıması gereken bir sütunu aylık seriye indirger."""
    benzersiz = df.groupby(ay_sutunu)[deger_sutunu].nunique(dropna=True)
    sorunlu = benzersiz[benzersiz > 1]
    if not sorunlu.empty:
        aylar = ", ".join(str(x) for x in sorunlu.index[:5])
        raise ValueError(
            f"{deger_sutunu!r} aynı ay içinde birden fazla değer taşıyor: {aylar}"
        )
    return df.groupby(ay_sutunu)[deger_sutunu].first().sort_index()


def ay_sonu_nowcast_etiketleri(
    aylik_hacim: pd.Series,
    esik_yuzde: float = 5.0,
) -> pd.Series:
    """Her ay M için M / M-1 değişiminden ay-sonu yön etiketini üretir.

    Eksik takvim ayları pozisyonel olarak atlanmaz. İlk ay, önceki takvim ayı
    bulunmadığı için ``eksik`` döner. Tam eşik değerleri ``stable`` sınıfına
    dahildir; davranış ``yon_degerlendirme.yon_etiketi`` ile aynıdır.
    """
    if len(aylik_hacim) == 0:
        return aylik_hacim.astype(object)

    seri = aylik_hacim.copy().sort_index()
    if not isinstance(seri.index, pd.PeriodIndex):
        seri.index = pd.PeriodIndex(seri.index, freq="M")
    else:
        seri.index = seri.index.asfreq("M")

    tam_takvim = pd.period_range(seri.index.min(), seri.index.max(), freq="M")
    tam_seri = seri.reindex(tam_takvim)
    onceki = tam_seri.shift(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        yuzde_degisim = (tam_seri - onceki) / onceki * 100.0
    yuzde_degisim = yuzde_degisim.where(onceki != 0, np.nan)
    etiket = yuzde_degisim.apply(lambda x: yon_etiketi(x, esik_yuzde))
    return etiket.reindex(seri.index)


def pazar_kesit_tarihleri(baslangic, bitis) -> pd.DatetimeIndex:
    """[başlangıç, bitiş] aralığındaki pazar günlerini döndürür.

    Tahmin operasyonu pazartesi çalışır; snapshot, bir önceki pazar kapanışına
    kadar bilinen veriyi temsil eder. ``bitis`` pazar değilse gelecekteki pazar
    eklenmez.
    """
    baslangic = pd.Timestamp(baslangic).normalize()
    bitis = pd.Timestamp(bitis).normalize()
    if bitis < baslangic:
        raise ValueError("bitis, baslangic tarihinden önce olamaz")
    gunler = pd.date_range(baslangic, bitis, freq="D")
    return gunler[gunler.weekday == 6]


def _gunluk_ozet(seri: pd.Series, onek: str) -> dict[str, float]:
    """Cut-off'a kadarki cari-ay günlük serisini sızıntısız özetler."""
    gecerli = pd.to_numeric(seri, errors="coerce").dropna()
    if gecerli.empty:
        return {
            f"{onek}_son": np.nan,
            f"{onek}_ortalama": np.nan,
            f"{onek}_std": np.nan,
            f"{onek}_min": np.nan,
            f"{onek}_max": np.nan,
            f"{onek}_ilk_son_degisim_pct": np.nan,
            f"{onek}_gozlem_sayisi": 0,
        }

    ilk = float(gecerli.iloc[0])
    son = float(gecerli.iloc[-1])
    degisim = (son / ilk - 1.0) * 100.0 if ilk != 0 else np.nan
    return {
        f"{onek}_son": son,
        f"{onek}_ortalama": float(gecerli.mean()),
        f"{onek}_std": float(gecerli.std(ddof=0)),
        f"{onek}_min": float(gecerli.min()),
        f"{onek}_max": float(gecerli.max()),
        f"{onek}_ilk_son_degisim_pct": float(degisim),
        f"{onek}_gozlem_sayisi": int(len(gecerli)),
    }


def haftalik_snapshot_uret(
    gunluk_df: pd.DataFrame,
    *,
    target_sutunu: str = "noter_devir_otomobil_adet",
    tarih_sutunu: str = "tarih",
    gunluk_feature_sutunlari: Iterable[str] = (),
    olay_feature_sutunlari: Iterable[str] = (),
    aylik_feature_sutunlari: Iterable[str] = (),
    esik_yuzde: float = 5.0,
    en_kucuk_aylik_lag: int = 2,
    target_lag_aylari: Iterable[int] = (2, 3, 12),
    tatil_tarihleri: Iterable | Mapping = (),
) -> pd.DataFrame:
    """Günlük tablodan pazar cut-off'lu aylık yön nowcast snapshot'ları kurar.

    Dönen tabloda her satır tek bir haftalık tahmin anıdır. ``etiket`` eğitim
    ve geriye dönük değerlendirme için ay-sonu gerçekleşmesidir; ``eksik``
    etiketli son dönem satırları operasyonel ileri tahmin için korunur.
    """
    if en_kucuk_aylik_lag < 2:
        raise ValueError(
            "Tarihsel yayım takvimi olmadan aylık feature için lag<2 sızıntı riski taşır"
        )

    gunluk_feature_sutunlari = list(gunluk_feature_sutunlari)
    olay_feature_sutunlari = list(olay_feature_sutunlari)
    aylik_feature_sutunlari = list(aylik_feature_sutunlari)
    target_lag_aylari = sorted(set(int(x) for x in target_lag_aylari))
    if isinstance(tatil_tarihleri, Mapping):
        tatil_agirliklari = {
            pd.Timestamp(tarih).normalize(): float(oran)
            for tarih, oran in tatil_tarihleri.items()
        }
    else:
        tatil_agirliklari = {
            pd.Timestamp(tarih).normalize(): 1.0 for tarih in tatil_tarihleri
        }
    if any(oran < 0.0 or oran > 1.0 for oran in tatil_agirliklari.values()):
        raise ValueError("Tatil ağırlıkları [0,1] aralığında olmalıdır")
    if any(lag < 2 for lag in target_lag_aylari):
        raise ValueError("Target lagleri en az 2 takvim ayı olmalıdır")

    gerekli = {
        tarih_sutunu,
        target_sutunu,
        *gunluk_feature_sutunlari,
        *olay_feature_sutunlari,
        *aylik_feature_sutunlari,
    }
    eksik = sorted(gerekli - set(gunluk_df.columns))
    if eksik:
        raise ValueError(f"Gerekli sütunlar eksik: {eksik}")
    if (
        target_sutunu in gunluk_feature_sutunlari
        or target_sutunu in olay_feature_sutunlari
        or target_sutunu in aylik_feature_sutunlari
    ):
        raise ValueError("Cari target feature listesine eklenemez")

    df = gunluk_df[list(gerekli)].copy()
    df[tarih_sutunu] = pd.to_datetime(df[tarih_sutunu], errors="raise")
    df = df.sort_values(tarih_sutunu).reset_index(drop=True)
    if df[tarih_sutunu].duplicated().any():
        raise ValueError("tarih sütunu tekil olmalıdır")
    df["_ay"] = df[tarih_sutunu].dt.to_period("M")

    aylik_target = _aylik_seri(df, "_ay", target_sutunu)
    etiketler = ay_sonu_nowcast_etiketleri(aylik_target, esik_yuzde=esik_yuzde)
    aylik_feature_serileri = {
        sutun: _aylik_seri(df, "_ay", sutun) for sutun in aylik_feature_sutunlari
    }

    kesitler = pazar_kesit_tarihleri(df[tarih_sutunu].min(), df[tarih_sutunu].max())
    satirlar: list[dict] = []
    for kesit in kesitler:
        ay = kesit.to_period("M")
        ay_basi = kesit.to_period("M").start_time
        cari_ay_parcasi = df[
            (df[tarih_sutunu] >= ay_basi) & (df[tarih_sutunu] <= kesit)
        ]
        if cari_ay_parcasi.empty:
            continue

        satir: dict[str, object] = {
            "kesit_tarihi": kesit,
            "tahmin_tarihi": kesit + pd.Timedelta(days=1),
            "hedef_ay": ay,
            "ayin_gunu": int(kesit.day),
            "ay": int(ay.month),
            "ay_sin": float(np.sin(2.0 * np.pi * ay.month / 12.0)),
            "ay_cos": float(np.cos(2.0 * np.pi * ay.month / 12.0)),
            "etiket": etiketler.get(ay, "eksik"),
        }
        ay_sonu = ay.end_time.normalize()
        ay_gunleri = pd.date_range(ay_basi, ay_sonu, freq="D")
        is_gunu_esdegerleri = pd.Series(
            [
                (1.0 - tatil_agirliklari.get(gun.normalize(), 0.0))
                if gun.weekday() < 5 else 0.0
                for gun in ay_gunleri
            ],
            index=ay_gunleri,
            dtype=float,
        )
        aydaki_is_gunu = float(is_gunu_esdegerleri.sum())
        gecen_is_gunu = float(is_gunu_esdegerleri[is_gunu_esdegerleri.index <= kesit].sum())
        satir["gecen_is_gunu"] = gecen_is_gunu
        satir["aydaki_is_gunu"] = aydaki_is_gunu
        satir["is_gunu_ilerleme_orani"] = float(gecen_is_gunu / aydaki_is_gunu)
        for sutun in gunluk_feature_sutunlari:
            satir.update(_gunluk_ozet(cari_ay_parcasi[sutun], sutun))
        for sutun in olay_feature_sutunlari:
            olay = pd.to_numeric(cari_ay_parcasi[sutun], errors="coerce").fillna(0.0)
            if not olay.isin([0.0, 1.0]).all():
                raise ValueError(f"{sutun!r} olay feature'i yalniz 0/1 icermelidir")
            olayli = cari_ay_parcasi.loc[olay.eq(1.0), tarih_sutunu]
            satir[f"{sutun}_cari_ay_sayisi"] = int(olay.sum())
            satir[f"{sutun}_son_olaydan_gun"] = (
                int((kesit - olayli.max()).days) if not olayli.empty else np.nan
            )
        for sutun, aylik_seri in aylik_feature_serileri.items():
            satir[f"{sutun}_lag{en_kucuk_aylik_lag}ay"] = aylik_seri.get(
                ay - en_kucuk_aylik_lag, np.nan
            )
        for lag in target_lag_aylari:
            satir[f"{target_sutunu}_lag{lag}ay"] = aylik_target.get(ay - lag, np.nan)
        satirlar.append(satir)

    sonuc = pd.DataFrame(satirlar)
    if sonuc.empty:
        return sonuc

    sonuc["hafta_sirasi"] = sonuc.groupby("hedef_ay").cumcount() + 1
    ay_snapshot_sayisi = sonuc.groupby("hedef_ay")["hedef_ay"].transform("size")
    sonuc["agirlik"] = 1.0 / ay_snapshot_sayisi
    kolon_basi = [
        "kesit_tarihi",
        "tahmin_tarihi",
        "hedef_ay",
        "hafta_sirasi",
        "ayin_gunu",
        "etiket",
        "agirlik",
    ]
    kalan = [c for c in sonuc.columns if c not in kolon_basi]
    return sonuc[kolon_basi + kalan].reset_index(drop=True)


def nowcast_uc_parcali_split_olustur(
    train_baslangic,
    train_bitis,
    validation_baslangic,
    validation_bitis,
    test_baslangic,
    test_bitis,
    *,
    embargo_ay_sayisi: int = 2,
) -> dict[str, list[pd.Period]]:
    """İki aylık embargo varsayılanlı ay-gruplu kronolojik split kurar.

    Snapshot satırları değil bağımsız hedef ayları bölünür. Train/validation
    ve validation/test arasındaki aylar otomatik embargo kümesine alınır.
    """
    if embargo_ay_sayisi < 1:
        raise ValueError("embargo_ay_sayisi en az 1 olmalıdır")

    train = list(pd.period_range(train_baslangic, train_bitis, freq="M"))
    validation = list(pd.period_range(validation_baslangic, validation_bitis, freq="M"))
    test = list(pd.period_range(test_baslangic, test_bitis, freq="M"))
    if not train or not validation or not test:
        raise ValueError("train, validation ve test kümeleri boş olamaz")

    if validation[0] != train[-1] + embargo_ay_sayisi + 1:
        raise ValueError(
            f"train-validation arasında tam {embargo_ay_sayisi} aylık embargo bulunmalıdır"
        )
    if test[0] != validation[-1] + embargo_ay_sayisi + 1:
        raise ValueError(
            f"validation-test arasında tam {embargo_ay_sayisi} aylık embargo bulunmalıdır"
        )

    embargo1 = [train[-1] + i for i in range(1, embargo_ay_sayisi + 1)]
    embargo2 = [validation[-1] + i for i in range(1, embargo_ay_sayisi + 1)]
    return {
        "train": train,
        "embargo1": embargo1,
        "validation": validation,
        "embargo2": embargo2,
        "test": test,
    }


def snapshot_splitlerine_ata(snapshot_df: pd.DataFrame, split: dict) -> pd.DataFrame:
    """Ay bazlı split'i snapshot'lara uygular; aynı ayı asla bölmez."""
    if "hedef_ay" not in snapshot_df.columns:
        raise ValueError("snapshot_df 'hedef_ay' sütununu içermelidir")
    sonuc = snapshot_df.copy()
    sonuc["hedef_ay"] = pd.PeriodIndex(sonuc["hedef_ay"], freq="M")
    ay_to_parca: dict[pd.Period, str] = {}
    for parca, aylar in split.items():
        for ay in aylar:
            ay = pd.Period(ay, freq="M")
            if ay in ay_to_parca:
                raise ValueError(f"{ay} birden fazla split parçasında bulunuyor")
            ay_to_parca[ay] = parca
    sonuc["split"] = sonuc["hedef_ay"].map(ay_to_parca)
    return sonuc


def model_feature_sutunlari(snapshot_df: pd.DataFrame) -> list[str]:
    """Metadata/etiket hariç güvenli model feature listesini döndürür."""
    dislanan = {
        "kesit_tarihi",
        "tahmin_tarihi",
        "hedef_ay",
        "etiket",
        "agirlik",
        "split",
    }
    featurelar = [c for c in snapshot_df.columns if c not in dislanan]
    gecersiz = [c for c in featurelar if c == "noter_devir_otomobil_adet"]
    if gecersiz:
        raise ValueError("Cari target model feature'ları arasında olamaz")
    return featurelar


__all__ = [
    "FIXED_LABEL_ORDER",
    "ay_sonu_nowcast_etiketleri",
    "haftalik_snapshot_uret",
    "model_feature_sutunlari",
    "nowcast_uc_parcali_split_olustur",
    "pazar_kesit_tarihleri",
    "snapshot_splitlerine_ata",
]
