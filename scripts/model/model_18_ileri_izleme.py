"""Model 18: Model 14'ün dondurulmuş konfigürasyonu için prospektif izleme hattı.

Ön-kayıt: prompts/veri/48_model18_prospektif_izleme_onkayit.md
(Rota-2 + Pusula, commit f4c4592). Model 18 YENİ BİR ADAY DEĞİLDİR — Model 14
`TEST_FEATURELAR` (14 feature, sıra sabit) + `lojistik_l2_c01` (C=0.1, L2,
lbfgs, max_iter=2000, class_weight=balanced, random_state=42) konfigürasyonu
hiçbir şekilde değişmez. Amaç bugün performans artışı değil, gerçekleşmeden
ÖNCE kaydedilen, validation-mining'den bağımsız yeni kanıt biriktirmektir.

İki ayrı kritik güvenlik mekanizması:

1. EĞİTİM SINIRI (ön-kayıt Bölüm 2): ham DF-A günlük verisi `2025-04-30`da
   FİZİKSEL olarak kesildikten SONRA Model 07'nin aynı bilgi-zamanı
   kurallarıyla (`hn.haftalik_snapshot_uret`) YENİDEN kurulur. Kilitli dönem
   (2025-07..2026-06) yön ETİKETLERİ bu yüzden önce üretilip sonra
   filtrelenmez — girdi verisi o tarihlerden sonrasını hiç içermediği için
   `ay_sonu_nowcast_etiketleri`nin ürettiği PeriodIndex yapısal olarak
   2025-04'ü geçemez (bkz. `egitim_snapshotu_kur` içindeki assertion'lar).

2. GELECEK SATIR (ön-kayıt Bölüm 3): `hn.haftalik_snapshot_uret` VE
   `hn.ay_sonu_nowcast_etiketleri` HİÇ çağrılmaz. Tek hedef ay / tek pazar
   kesiti için etiketsiz satır, aynı formüllerle ama dar/özel bir
   fonksiyonla (`gelecek_kesit_satiri_uret`) kurulur; "etiket" alanı
   HESAPLANMAZ, sabit "eksik" atanır.

İNCE AYRIM — ham lag değeri ≠ etiket: gelecek satırın `lag12`/`lag13` target
feature'ları (ör. 2026-08 hedefi için 2025-08/2025-07), kilitli aralığın
İÇİNDEKİ ham (sayısal) target değerlerini okur. Bu, K10'un başından beri var
olan M-2 lag mimarisinin doğal uzantısıdır (Model 09/10/14 de aynı mekanizmayı
kullanır) ve kilidi İHLAL ETMEZ: kilit, o ayların YÖN SINIFLANDIRMASININ
(up/down/stable) hesaplanmasını/okunmasını/raporlanmasını yasaklar — zaten
kamuya açık olan ham istatistiği feature olarak kullanmayı değil. Bu script
hiçbir noktada kilitli bir ay için etiket üretmez; bunu hem kod hem testler
kanıtlar.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import haftalik_aylik_nowcast as hn  # noqa: E402
import model_07_haftalik_nowcast_veri_hazirligi as m07  # noqa: E402
import model_14_mevcut_asof_feature_genisletme as m14  # noqa: E402
import yon_degerlendirme as yd  # noqa: E402
from turkiye_tatil_takvimi import turkiye_resmi_tatil_agirliklari  # noqa: E402

DF_DIR = m07.DF_DIR

# --- Ön-kayıt Bölüm 1: değişmeyen model/hedef sözleşmesi ------------------
AYLIK_A = [
    "tufe_aylik_degisim", "tufe_yillik_degisim", "odmd_otomobil_adet",
    "tuketici_guven_endeksi", "tasit_kredisi_faiz", "politika_faizi",
]
TARGET_LAG_AYLARI = (2, 3, 12, 13)
EN_KUCUK_AYLIK_LAG = 2
ESIK_YUZDE = 5.0
TATIL_YIL_ARALIGI = (2018, 2026)  # turkiye_tatil_takvimi.py'nin desteklediği ust sinir.

# --- Ön-kayıt Bölüm 2: eğitim kümesi — kapalı ve sabit sınır ----------------
EGITIM_KESIM_TARIHI = pd.Timestamp("2025-04-30")
ILK_EGITIM_AYI = pd.Period("2019-01", freq="M")
SON_EGITIM_AYI = pd.Period("2025-04", freq="M")

# --- Ön-kayıt Bölüm 4: değiştirilemez kayıt sözleşmesi ----------------------
TAHMIN_DEFTERI_YOLU = MODEL_DIR / "model_18_ileri_izleme_defteri.csv"
DEFTER_KOLONLARI = [
    "hedef_ay", "kesit_tarihi", "hafta_sirasi", "tahmin_tarihi", "kayit_tarihi",
    "gercek_zamanli_mi", "arsiv_gecikme_gun", "zaman_notu",
    "p_down", "p_stable", "p_up", "tahmin_sinifi",
    "raw_confidence", "konfig_hash", "train_veri_hash", "tahmin_satiri_hash",
    "prediction_hash",
]

SABIT_MODEL_PARAMETRELERI = {
    "C": 0.1, "penalty": "l2", "solver": "lbfgs", "max_iter": 2000,
    "class_weight": "balanced", "random_state": 42,
}

KONFIG_SOZLESMESI = {
    "onkayit": "prompts/veri/48_model18_prospektif_izleme_onkayit.md",
    "target": "noter_devir_otomobil_adet",
    "sinif_sirasi": list(yd.FIXED_LABEL_ORDER),
    "esik_yuzde": ESIK_YUZDE,
    "feature_sirasi": list(m14.TEST_FEATURELAR),
    "model_tipi": "LogisticRegression",
    "model_parametreleri": SABIT_MODEL_PARAMETRELERI,
    "onisleme": {"imputer": "median+add_indicator", "scaler": "standard"},
    "karar_kurali": "argmax",
    "egitim_araligi": [str(ILK_EGITIM_AYI), str(SON_EGITIM_AYI)],
    "egitim_kesim_tarihi": str(EGITIM_KESIM_TARIHI.date()),
    "target_lag_aylari": list(TARGET_LAG_AYLARI),
    "en_kucuk_aylik_lag": EN_KUCUK_AYLIK_LAG,
}


# ---------------------------------------------------------------------------
# Ortak veri birleştirme — Model 07'nin main() adımlarının birebir tekrarı
# (saf/test edilebilir hale getirmek için ham df/karisik parametre alır).
# ---------------------------------------------------------------------------

def _df_a_oku() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gerçek CSV'lerden DF-A ve karışık-frekans tablolarını okur (yan etkili)."""
    df_a = pd.read_csv(DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv", low_memory=False)
    karisik = pd.read_csv(DF_DIR / "df_gunluk_karisik_frekans_2015_bugun.csv", low_memory=False)
    return df_a, karisik


def _df_a_birlestir(
    df_a: pd.DataFrame, karisik: pd.DataFrame, *, kesim_tarihi=None
) -> pd.DataFrame:
    """Model 07 `main()` içindeki DF-A birleştirme adımlarını (eurtry/otv
    merge + faiz mapping) birebir tekrarlar — saf fonksiyon, dosya okumaz.

    `kesim_tarihi` verilirse, hedef ve karışık tablo birleşiminden ÖNCE ham
    günlük veri o tarihten sonraki HİÇBİR satırı içermeyecek şekilde kesilir.
    Bu, eğitim güvenliğinin (kilitli dönem etiketinin yapısal olarak hiç
    üretilememesinin) tek kaynağıdır.
    """
    df_a = m07._target_penceresini_kes(df_a)

    if kesim_tarihi is not None:
        kesim_tarihi = pd.Timestamp(kesim_tarihi)
        tarihler = pd.to_datetime(df_a["tarih"], errors="raise")
        df_a = df_a[tarihler <= kesim_tarihi].copy()

    yuksek_frekans = karisik[["tarih", "eurtry_orta", "otv_event_gunu_mu"]].copy()
    df_a = df_a.merge(yuksek_frekans, on="tarih", how="left", validate="one_to_one")

    faiz_satirlari = karisik.dropna(subset=["faiz_referans_ay"])[
        ["faiz_referans_ay", "tasit_kredisi_faiz", "politika_faizi"]
    ].drop_duplicates("faiz_referans_ay")
    faiz_haritasi = faiz_satirlari.set_index("faiz_referans_ay")
    ay_anahtari = pd.to_datetime(df_a["tarih"]).dt.to_period("M").astype(str)
    df_a["tasit_kredisi_faiz"] = ay_anahtari.map(faiz_haritasi["tasit_kredisi_faiz"])
    df_a["politika_faizi"] = ay_anahtari.map(faiz_haritasi["politika_faizi"])
    return df_a


# ---------------------------------------------------------------------------
# 1) EĞİTİM SNAPSHOT'I — yapısal olarak kilitli-dönem-üretemez
# ---------------------------------------------------------------------------

def egitim_snapshotu_kur(
    df_a: pd.DataFrame | None = None, karisik: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Yalnız `2019-01..2025-04` kapalı aralığındaki etiketli haftalık
    snapshot'ları döndürür.

    Ham günlük veri `hn.haftalik_snapshot_uret`'e verilmeden ÖNCE
    `2025-04-30`da kesilir; bu yüzden `ay_sonu_nowcast_etiketleri`'nin
    içindeki `tam_takvim = period_range(min, max)` yapısal olarak
    `2025-04`ü geçemez — kilitli dönem etiketleri üretilip sonra
    filtrelenmez, hiç var olmaz.
    """
    if df_a is None or karisik is None:
        df_a, karisik = _df_a_oku()

    df_a_kesilmis = _df_a_birlestir(df_a, karisik, kesim_tarihi=EGITIM_KESIM_TARIHI)
    # Ön-kayıt STOP_ONLY_IF madde 1 — girdi ön-koşulu.
    assert pd.to_datetime(df_a_kesilmis["tarih"]).max() <= EGITIM_KESIM_TARIHI, (
        "egitim_snapshotu_kur: girdi verisi kesim tarihinden sonrasini iceriyor"
    )

    snapshot = hn.haftalik_snapshot_uret(
        df_a_kesilmis,
        gunluk_feature_sutunlari=["usdtry_orta", "eurtry_orta"],
        olay_feature_sutunlari=["otv_event_gunu_mu"],
        aylik_feature_sutunlari=AYLIK_A,
        esik_yuzde=ESIK_YUZDE,
        en_kucuk_aylik_lag=EN_KUCUK_AYLIK_LAG,
        target_lag_aylari=list(TARGET_LAG_AYLARI),
        tatil_tarihleri=turkiye_resmi_tatil_agirliklari(*TATIL_YIL_ARALIGI),
    )
    if snapshot.empty:
        raise RuntimeError("egitim_snapshotu_kur: bos snapshot uretildi")

    # Yapisal invaryant (assertion olarak da kanitlanir, bkz. testler):
    # girdi 2025-04-30'da bittigi icin hicbir hedef_ay bunu asamaz.
    uretilen_max_ay = pd.PeriodIndex(snapshot["hedef_ay"], freq="M").max()
    assert uretilen_max_ay <= SON_EGITIM_AYI, (
        f"egitim_snapshotu_kur: STOP_ONLY_IF madde 1 ihlali — uretilen hedef_ay "
        f"{uretilen_max_ay} > {SON_EGITIM_AYI}"
    )

    snapshot = m14.feature_hazirla(snapshot)
    snapshot["hedef_ay"] = pd.PeriodIndex(snapshot["hedef_ay"], freq="M")
    snapshot = snapshot[snapshot["etiket"].isin(yd.FIXED_LABEL_ORDER)].copy()
    snapshot = snapshot[
        (snapshot["hedef_ay"] >= ILK_EGITIM_AYI) & (snapshot["hedef_ay"] <= SON_EGITIM_AYI)
    ].copy()

    if snapshot.empty:
        raise RuntimeError("egitim_snapshotu_kur: filtre sonrasi egitim kumesi bos")
    assert snapshot["hedef_ay"].min() >= ILK_EGITIM_AYI
    assert snapshot["hedef_ay"].max() <= SON_EGITIM_AYI
    beklenen_aylar = set(pd.period_range(ILK_EGITIM_AYI, SON_EGITIM_AYI, freq="M"))
    gercek_aylar = set(snapshot["hedef_ay"].unique())
    if gercek_aylar != beklenen_aylar:
        raise AssertionError(
            "egitim_snapshotu_kur: egitim ay kumesi on-kayitli kapali aralikla "
            f"birebir degil; eksik={sorted(beklenen_aylar - gercek_aylar)}, "
            f"fazla={sorted(gercek_aylar - beklenen_aylar)}"
        )
    ay_agirliklari = snapshot.groupby("hedef_ay")["agirlik"].sum().to_numpy()
    if not np.allclose(ay_agirliklari, 1.0):
        raise AssertionError("egitim_snapshotu_kur: ay-esit agirlik toplamlari 1 degil")
    eksik_feature = [c for c in m14.TEST_FEATURELAR if c not in snapshot.columns]
    if eksik_feature:
        raise KeyError(f"egitim_snapshotu_kur: eksik feature(lar): {eksik_feature}")
    return snapshot.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2) GELECEK SATIR — etiketsiz, dar/özel inşa (haftalik_snapshot_uret YOK)
# ---------------------------------------------------------------------------

def gelecek_kesit_satiri_uret(
    df_a: pd.DataFrame, kesit_tarihi, hedef_ay
) -> dict:
    """Tek pazar kesiti için ETİKETSİZ feature satırı kurar.

    `hn.haftalik_snapshot_uret` ve `hn.ay_sonu_nowcast_etiketleri` HİÇ
    çağrılmaz (ön-kayıt Bölüm 3). "etiket" alanı sabit "eksik"tir —
    hesaplanmaz. Yalnız saf, etiket-üretmeyen yardımcılar (`hn._aylik_seri`,
    `hn._gunluk_ozet`) kullanılır.
    """
    kesit_tarihi = pd.Timestamp(kesit_tarihi).normalize()
    hedef_ay = pd.Period(hedef_ay, freq="M")

    if kesit_tarihi.weekday() != 6:
        raise ValueError(
            f"gelecek_kesit_satiri_uret: kesit_tarihi ({kesit_tarihi.date()}) "
            "bir pazar gunu olmalidir (K10 kadansi)"
        )
    ay_basi = hedef_ay.start_time.normalize()
    ay_sonu = hedef_ay.end_time.normalize()
    if not (ay_basi <= kesit_tarihi <= ay_sonu):
        # STOP_ONLY_IF madde 4/genel tutarlilik: kesit hedef ayin disinda olamaz.
        raise ValueError(
            "gelecek_kesit_satiri_uret: kesit_tarihi hedef_ay disinda "
            f"({kesit_tarihi.date()} not in [{ay_basi.date()}, {ay_sonu.date()}])"
        )

    gerekli = {"tarih", m07.TARGET, "usdtry_orta", "eurtry_orta", "otv_event_gunu_mu", *AYLIK_A}
    eksik = sorted(gerekli - set(df_a.columns))
    if eksik:
        raise KeyError(f"gelecek_kesit_satiri_uret: gerekli sutunlar eksik: {eksik}")

    df = df_a[list(gerekli)].copy()
    df["tarih"] = pd.to_datetime(df["tarih"], errors="raise")
    df = df.sort_values("tarih").reset_index(drop=True)
    df["_ay"] = df["tarih"].dt.to_period("M")

    # STOP_ONLY_IF madde 4: hedef ayin GERCEK degeri zaten biliniyorsa bu artik
    # prospektif/kor bir tahmin degildir -- reddedilir.
    hedef_serisi = hn._aylik_seri(df, "_ay", m07.TARGET)
    if hedef_ay in hedef_serisi.index and pd.notna(hedef_serisi.get(hedef_ay)):
        raise RuntimeError(
            "STOP_ONLY_IF madde 4: hedef ayin gercek target degeri zaten "
            f"mevcut ({hedef_ay}); bu artik prospektif/kor bir tahmin degildir."
        )

    cari_ay_parcasi = df[(df["tarih"] >= ay_basi) & (df["tarih"] <= kesit_tarihi)]
    # STOP_ONLY_IF madde 5: kesit sonrasi gunluk bilgi asla feature'a giremez.
    assert (cari_ay_parcasi["tarih"] <= kesit_tarihi).all()
    if cari_ay_parcasi.empty:
        raise ValueError(
            "gelecek_kesit_satiri_uret: kesit tarihine kadar cari ay icin "
            "hic gunluk gozlem yok"
        )

    satir: dict = {
        "kesit_tarihi": kesit_tarihi,
        "tahmin_tarihi": kesit_tarihi + pd.Timedelta(days=1),
        "hedef_ay": hedef_ay,
        "ayin_gunu": int(kesit_tarihi.day),
        "ay": int(hedef_ay.month),
        "ay_sin": float(np.sin(2.0 * np.pi * hedef_ay.month / 12.0)),
        "ay_cos": float(np.cos(2.0 * np.pi * hedef_ay.month / 12.0)),
        # ETIKET HESAPLANMAZ: hedef ay henuz kapanmadi (ustteki assertion bunu
        # zaten kanitladi). ay_sonu_nowcast_etiketleri HICBIR YERDE cagirilmaz.
        "etiket": "eksik",
    }

    # is_gunu_ilerleme_orani -- Model07 haftalik_snapshot_uret ile BIREBIR
    # formul (tatil-agirlikli is-gunu esdegeri, yalniz kesit tarihine kadar).
    tatil_agirliklari = {
        pd.Timestamp(t).normalize(): float(o)
        for t, o in turkiye_resmi_tatil_agirliklari(*TATIL_YIL_ARALIGI).items()
    }
    ay_gunleri = pd.date_range(ay_basi, ay_sonu, freq="D")
    is_gunu_esdegerleri = pd.Series(
        [
            (1.0 - tatil_agirliklari.get(g.normalize(), 0.0)) if g.weekday() < 5 else 0.0
            for g in ay_gunleri
        ],
        index=ay_gunleri, dtype=float,
    )
    aydaki_is_gunu = float(is_gunu_esdegerleri.sum())
    gecen_is_gunu = float(is_gunu_esdegerleri[is_gunu_esdegerleri.index <= kesit_tarihi].sum())
    satir["gecen_is_gunu"] = gecen_is_gunu
    satir["aydaki_is_gunu"] = aydaki_is_gunu
    satir["is_gunu_ilerleme_orani"] = (
        gecen_is_gunu / aydaki_is_gunu if aydaki_is_gunu > 0 else np.nan
    )
    # Pazar sayisi (kesit dahil) -- Model07'deki gruplama-tabanli hafta_sirasi
    # ile ayni anlami tasir; tek-kesitlik bu script'te elle turetilir.
    satir["hafta_sirasi"] = int(((ay_gunleri.weekday == 6) & (ay_gunleri <= kesit_tarihi)).sum())

    for sutun in ("usdtry_orta", "eurtry_orta"):
        satir.update(hn._gunluk_ozet(cari_ay_parcasi[sutun], sutun))

    olay = pd.to_numeric(cari_ay_parcasi["otv_event_gunu_mu"], errors="coerce").fillna(0.0)
    if not olay.isin([0.0, 1.0]).all():
        raise ValueError("gelecek_kesit_satiri_uret: otv_event_gunu_mu yalniz 0/1 icermeli")
    olayli = cari_ay_parcasi.loc[olay.eq(1.0), "tarih"]
    satir["otv_event_gunu_mu_cari_ay_sayisi"] = int(olay.sum())
    satir["otv_event_gunu_mu_son_olaydan_gun"] = (
        int((kesit_tarihi - olayli.max()).days) if not olayli.empty else np.nan
    )

    # Aylik feature'lar (M-2) -- yalniz SAYISAL deger okur, siniflandirma yok.
    for sutun in AYLIK_A:
        seri = hn._aylik_seri(df, "_ay", sutun)
        satir[f"{sutun}_lag{EN_KUCUK_AYLIK_LAG}ay"] = seri.get(hedef_ay - EN_KUCUK_AYLIK_LAG, np.nan)

    # Target lag'lari (2/3/12/13) -- HAM sayisal deger. lag12/lag13, kilitli
    # araliktaki (2025-07..2026-06) ham target adedini okuyabilir; bu bir
    # SINIFLANDIRMA/ETIKET DEGILDIR (bkz. modul docstring'i "ince ayrim").
    for lag in TARGET_LAG_AYLARI:
        satir[f"{m07.TARGET}_lag{lag}ay"] = hedef_serisi.get(hedef_ay - lag, np.nan)

    return satir


def satiri_ozellik_cercevesine_donustur(satir: dict) -> pd.DataFrame:
    """Tek satırlık sözlüğü, `m14.feature_hazirla`nın türetilmiş feature'ları
    (hedef_m2_m3/hedef_m12_m13/reel_politika_faizi) ekleyebileceği bir
    DataFrame'e çevirir ve 14 feature'ın tamlığını doğrular."""
    df_satir = pd.DataFrame([satir])
    df_satir = m14.feature_hazirla(df_satir)
    eksik = [c for c in m14.TEST_FEATURELAR if c not in df_satir.columns]
    if eksik:
        raise KeyError(f"satiri_ozellik_cercevesine_donustur: eksik feature(lar): {eksik}")
    return df_satir


# ---------------------------------------------------------------------------
# 3) Kanonik hash'ler
# ---------------------------------------------------------------------------

def _yuvarla(deger, ondalik: int = 10):
    """Kanonik JSON'dan önce ondalık/tip normalizasyonu (hash kararlılığı)."""
    if isinstance(deger, dict):
        return {str(k): _yuvarla(v, ondalik) for k, v in sorted(deger.items(), key=lambda kv: str(kv[0]))}
    if isinstance(deger, (list, tuple)):
        return [_yuvarla(v, ondalik) for v in deger]
    if isinstance(deger, pd.Timestamp):
        return deger.isoformat()
    if isinstance(deger, pd.Period):
        return str(deger)
    if isinstance(deger, (np.integer,)):
        return int(deger)
    if isinstance(deger, np.bool_):
        return bool(deger)
    if isinstance(deger, (np.floating, float)):
        deger = float(deger)
        if np.isnan(deger):
            return None
        return round(deger, ondalik)
    if isinstance(deger, float) and np.isnan(deger):
        return None
    return deger


def _kanonik_json(obj) -> str:
    return json.dumps(_yuvarla(obj), sort_keys=True, ensure_ascii=False)


def _sha256(metin: str) -> str:
    return hashlib.sha256(metin.encode("utf-8")).hexdigest()


def konfig_hash_hesapla() -> str:
    """Tüm sabit model/hedef/eğitim/feature sözleşmesinin SHA-256'sı."""
    return _sha256(_kanonik_json(KONFIG_SOZLESMESI))


def train_veri_hash_hesapla(egitim_df: pd.DataFrame) -> str:
    """Eğitim meta+feature+etiket+ağırlık tablosunun kanonik SHA-256'sı."""
    kolonlar = ["hedef_ay", "hafta_sirasi", "etiket", "agirlik", *m14.TEST_FEATURELAR]
    alt = egitim_df[kolonlar].sort_values(["hedef_ay", "hafta_sirasi"]).reset_index(drop=True)
    kayitlar = []
    for _, satir in alt.iterrows():
        kayit = {k: satir[k] for k in kolonlar}
        kayit["hedef_ay"] = str(kayit["hedef_ay"])
        kayitlar.append(kayit)
    return _sha256(_kanonik_json(kayitlar))


def tahmin_satiri_hash_hesapla(ozellik_df: pd.DataFrame) -> str:
    """Etiketsiz gelecek meta+feature satırının kanonik SHA-256'sı."""
    kolonlar = ["hedef_ay", "kesit_tarihi", "hafta_sirasi", *m14.TEST_FEATURELAR]
    satir = ozellik_df.iloc[0]
    kanonik = {k: satir[k] for k in kolonlar}
    kanonik["hedef_ay"] = str(kanonik["hedef_ay"])
    kanonik["kesit_tarihi"] = str(kanonik["kesit_tarihi"])
    return _sha256(_kanonik_json(kanonik))


def prediction_hash_hesapla(
    *, hedef_ay, kesit_tarihi, p_down, p_stable, p_up, tahmin_sinifi,
    konfig_hash, train_veri_hash, tahmin_satiri_hash,
) -> str:
    """Hedef, kesit, olasılıklar, sınıf ve bileşen hash'lerini bağlayan anahtar."""
    kanonik = {
        "hedef_ay": str(hedef_ay), "kesit_tarihi": str(kesit_tarihi),
        "p_down": p_down, "p_stable": p_stable, "p_up": p_up,
        "tahmin_sinifi": tahmin_sinifi, "konfig_hash": konfig_hash,
        "train_veri_hash": train_veri_hash, "tahmin_satiri_hash": tahmin_satiri_hash,
    }
    return _sha256(_kanonik_json(kanonik))


# ---------------------------------------------------------------------------
# 4) Değiştirilemez tahmin defteri
# ---------------------------------------------------------------------------

def deftere_ekle(kayit: dict, defter_yolu: Path = TAHMIN_DEFTERI_YOLU) -> str:
    """Append-only + idempotent yazma.

    Tekil anahtar `(hedef_ay, kesit_tarihi, konfig_hash)`. Aynı anahtar +
    aynı içerik -> no-op. Aynı anahtar + farklı içerik -> RuntimeError
    (ön-kayıt STOP_ONLY_IF madde 6). Mevcut satır ASLA güncellenmez/silinmez.
    """
    eksik = [k for k in DEFTER_KOLONLARI if k not in kayit]
    if eksik:
        raise KeyError(f"deftere_ekle: eksik alan(lar): {eksik}")

    if defter_yolu.exists():
        mevcut = pd.read_csv(defter_yolu, dtype=str, keep_default_na=False)
    else:
        mevcut = pd.DataFrame(columns=DEFTER_KOLONLARI)

    yeni_satir = {k: ("" if kayit[k] is None else str(kayit[k])) for k in DEFTER_KOLONLARI}

    if not mevcut.empty:
        anahtar_maske = (
            (mevcut["hedef_ay"] == yeni_satir["hedef_ay"])
            & (mevcut["kesit_tarihi"] == yeni_satir["kesit_tarihi"])
            & (mevcut["konfig_hash"] == yeni_satir["konfig_hash"])
        )
        if anahtar_maske.any():
            eslesen = mevcut.loc[anahtar_maske].iloc[0]
            for kolon in DEFTER_KOLONLARI:
                if str(eslesen.get(kolon, "")) != yeni_satir[kolon]:
                    raise RuntimeError(
                        "STOP_ONLY_IF madde 6: ayni defter anahtari "
                        f"(hedef_ay={kayit['hedef_ay']}, kesit_tarihi={kayit['kesit_tarihi']}) "
                        f"farkli icerikle yeniden yazilmak istendi (kolon={kolon})."
                    )
            return "no_op_zaten_kayitli"

    defter_yolu.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([yeni_satir])[DEFTER_KOLONLARI].to_csv(
        defter_yolu,
        mode="a",
        header=not defter_yolu.exists(),
        index=False,
        encoding="utf-8",
    )
    return "eklendi"


# ---------------------------------------------------------------------------
# Ana akış — ilk kayıt: hedef_ay=2026-08, kavramsal kesit=2026-08-02
# ---------------------------------------------------------------------------

def ileri_tahmin_uret_ve_kaydet(
    *, hedef_ay="2026-08", kesit_tarihi="2026-08-02",
    tahmin_tarihi="2026-08-03", kayit_tarihi="2026-08-09",
    gercek_zamanli_mi: bool = False,
) -> dict:
    """Uçtan uca: güvenli eğitim + etiketsiz gelecek satır + fit + tahmin +
    hash + append-only kayıt. Hiçbir performans metriği üretmez/döndürmez."""
    hedef_ay = pd.Period(hedef_ay, freq="M")
    kesit_tarihi = pd.Timestamp(kesit_tarihi).normalize()
    tahmin_tarihi = pd.Timestamp(tahmin_tarihi).normalize()
    kayit_tarihi = pd.Timestamp(kayit_tarihi).normalize()
    if tahmin_tarihi != kesit_tarihi + pd.Timedelta(days=1):
        raise ValueError("tahmin_tarihi, kesit tarihinden sonraki pazartesi olmalidir")
    if kayit_tarihi < tahmin_tarihi:
        raise ValueError("kayit_tarihi tahmin_tarihinden once olamaz")

    egitim_df = egitim_snapshotu_kur()
    train_hash = train_veri_hash_hesapla(egitim_df)

    df_a_guncel, karisik_guncel = _df_a_oku()
    df_a_guncel = _df_a_birlestir(df_a_guncel, karisik_guncel, kesim_tarihi=None)
    satir = gelecek_kesit_satiri_uret(df_a_guncel, kesit_tarihi, hedef_ay)
    ozellik_df = satiri_ozellik_cercevesine_donustur(satir)
    tahmin_hash = tahmin_satiri_hash_hesapla(ozellik_df)

    imputer = SimpleImputer(strategy="median", add_indicator=True)
    scaler = StandardScaler()
    x_egitim = imputer.fit_transform(egitim_df[m14.TEST_FEATURELAR])
    x_egitim = scaler.fit_transform(x_egitim)

    model = LogisticRegression(**SABIT_MODEL_PARAMETRELERI)
    model.fit(x_egitim, egitim_df["etiket"], sample_weight=egitim_df["agirlik"])

    x_yeni = imputer.transform(ozellik_df[m14.TEST_FEATURELAR])
    x_yeni = scaler.transform(x_yeni)
    olasiliklar = model.predict_proba(x_yeni)[0]
    p = dict(zip(model.classes_, (float(x) for x in olasiliklar)))
    tahmin_sinifi, raw_confidence = yd.tahmin_sinifi_ve_guven(
        p["down"], p["stable"], p["up"]
    )

    konfig_hash = konfig_hash_hesapla()
    pred_hash = prediction_hash_hesapla(
        hedef_ay=hedef_ay, kesit_tarihi=kesit_tarihi.date(),
        p_down=p["down"], p_stable=p["stable"], p_up=p["up"],
        tahmin_sinifi=tahmin_sinifi, konfig_hash=konfig_hash,
        train_veri_hash=train_hash, tahmin_satiri_hash=tahmin_hash,
    )

    kayit = {
        "hedef_ay": str(hedef_ay), "kesit_tarihi": str(kesit_tarihi.date()),
        "hafta_sirasi": int(satir["hafta_sirasi"]),
        "tahmin_tarihi": str(tahmin_tarihi.date()),
        "kayit_tarihi": str(kayit_tarihi.date()),
        "gercek_zamanli_mi": bool(gercek_zamanli_mi),
        "arsiv_gecikme_gun": int((kayit_tarihi - kesit_tarihi).days),
        "zaman_notu": (
            "Veri kayit tarihinde yerel dosyalardan insa edildi; kesit tarihi "
            "kavramsal K10 kesitidir ve o tarihte fiziksel olarak dondurulmamistir."
            if not gercek_zamanli_mi else
            "Tahmin kesite yakin zamanda kaydedildi; girdi hashleriyle donduruldu."
        ),
        "p_down": p["down"], "p_stable": p["stable"], "p_up": p["up"],
        "tahmin_sinifi": tahmin_sinifi, "raw_confidence": raw_confidence,
        "konfig_hash": konfig_hash, "train_veri_hash": train_hash,
        "tahmin_satiri_hash": tahmin_hash, "prediction_hash": pred_hash,
    }
    durum = deftere_ekle(kayit)
    return {"kayit": kayit, "durum": durum}


def main() -> None:
    sonuc = ileri_tahmin_uret_ve_kaydet()
    kayit, durum = sonuc["kayit"], sonuc["durum"]
    print(
        f"Model 18 ileri izleme: hedef_ay={kayit['hedef_ay']} "
        f"kesit={kayit['kesit_tarihi']} -> {durum}"
    )
    print(json.dumps(kayit, ensure_ascii=False, indent=2, default=str))
    print(
        "NOT: gercek_zamanli_mi=False -- veri 2026-08-09'da yerel dosyalardan "
        "insa edildi; 2026-08-02 kavramsal K10 kesitidir, o tarihte dondurulmus "
        "bir goruntu degildir (onkayit Bolum 3)."
    )


if __name__ == "__main__":
    main()
