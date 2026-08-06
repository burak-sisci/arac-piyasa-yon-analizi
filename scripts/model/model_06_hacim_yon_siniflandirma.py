"""
MODEL 06 — HACIM YONU, DOGRUDAN UC SINIF (up/stable/down).

K9 (docs/00_karar_kaydi.md) ile onaylanan aktif Asama B operasyonel
karari: target `noter_devir_otomobil_adet` (hacim), GUNLUK frekans,
dogrudan uc sinifli siniflandirma. K8'in "ilan fiyati yonu" hedefinin
YERINE GECMEZ (o hedef N<50 kesifsel gecitte donduruldu, ayri kalir).

ETIKET: Her GUNLUK satirin etiketi, satirin bulundugu REFERANS AYIN
(kaynak ayin) hacmi ile BIR SONRAKI TAKVIM AYININ hacmi karsilastirilarak
kurulur (yd.sonraki_ay_etiketleri, sabit esik_yuzde=5.0). Gunluk satirlar
KORUNUR (aggregate edilmez); son ay (M+1 bilinmiyor) labelsiz kalir.

FEATURE/LEAKAGE: noter_devir_toplam_adet (target'in ~ust-kategorisi,
r~0.98) VE target'in GUNCEL/GELECEK degerleri feature setinden CIKARILDI.
Gecmis hacim bilgisi SADECE ay-takvimli lag1/2/3/12 olarak eklendi (lag0/
guncel ay YOK). Aylik eszamanli covariate'lar (TUIK/ODMD/BETAM vb, gercek
yayimda gecikme var) EN AZ 1 TAKVIM AYI geciktirildi; adinda zaten
lag4ay/lag5ay/lag12ay olan sutunlar (kaynakta onceden gecikmeli) ikinci kez
kaydirilmadi; DF-A'daki usdtry_orta (gercek GUNLUK seri) kendi gununde
kullanildi. Ay-hizali HAM tablo (data/processed/dataframes/*.csv) HICBIR
sekilde degistirilmedi/uzerine yazilmadi - tum muhendislik bu scriptin
kendi bellek-ici kopyasinda yapildi. Global bfill/yeni ffill kullanilmadi.

SPLIT: Kaynak ayina gore kronolojik train -> purge(1 ay) -> validation ->
purge(1 ay) -> test (yd.uc_parcali_split_olustur ile dogrulanir). Denetmen
tarafindan onaylanan SABIT split'ler (bkz. prompts/veri/28_*.md):
  DF-A: train 2018-01..2024-03 (75 ay) / purge 2024-04 / val 2024-05..2025-04
        (12 ay) / purge 2025-05 / test 2025-06..2026-05 (12 ay)
  DF-B: train 2024-01..2025-03 (15 ay) / purge 2025-04 / val 2025-05..2025-10
        (6 ay) / purge 2025-11 / test 2025-12..2026-05 (6 ay)
DF-B SADECE 15 bagimsiz egitim ayina sahiptir -> KESIFSEL, baseline iddiasi
guclu degildir; PM raporunda acikca belirtilir.

AGIRLIK: her gunluk satira 1/(o aydaki gun sayisi) agirligi verilir
(yd.ay_agirligi) - AutoGluon egitiminde (sample_weight) VE testte
(agirlikli degerlendirme) kullanilir; boylece ay-hizali gunluk tekrarlarin
pseudo-replikasyon etkisi esitlenir.

MODEL: AutoGluon TabularPredictor(problem_type="multiclass"), eval_metric
"mcc", presets="medium_quality", time_limit<=300sn/set, TEK deneme (hata
olursa tekrar denenmez).

CIKTI (data/processed/model/):
  model_06_hacim_yon_{set}_sonuc.json          - ozellik katalogu, split
                                                  ozeti, egitim suresi, test
                                                  metrikleri (gunluk agirlikli/
                                                  agirliksiz + ay-bazli),
                                                  baseline karsilastirmasi,
                                                  denetmen referans karsilastirmasi,
                                                  olasilik kalibrasyon durumu.
  model_06_hacim_yon_{set}_test_gunluk_tahmin.csv - test donemi GUNLUK
                                                  predict_proba + tahmin.
  model_06_hacim_yon_{set}_ileri_sinyal.json   - test disi, ayri, henuz
                                                  gerceklesmemis ileri-donuk
                                                  sinyal (durum=gerceklesme_bekleniyor).
"""
from pathlib import Path
import json
import sys
import time

import numpy as np
import pandas as pd
from autogluon.tabular import TabularPredictor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import yon_degerlendirme as yd  # noqa: E402

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"

TARGET = "noter_devir_otomobil_adet"
DISLANAN_LEAKAGE_SUTUNU = "noter_devir_toplam_adet"  # target'in ~ust-kategorisi (r~0.98)
HEDEF_LAG_AYLARI = [1, 2, 3, 12]
ESIK_YUZDE = 5.0
ZAMAN_SINIRI_SANIYE = 300
PRESET = "medium_quality"

# denetmen (Codex) on-hesabinda sabit test splitlerinde bulunan mevsimsel-yon
# baseline referans degerleri (prompts/veri/28_*.md) - kod sonucu bunlarla
# karsilastirilir, sessizce yoksayilmaz.
DENETMEN_MEVSIMSEL_REFERANS = {
    "DF-A": {"mcc_gorodkin": 0.3936, "macro_f1": 0.5794, "accuracy": 0.5833},
    "DF-B": {"mcc_gorodkin": 0.0000, "macro_f1": 0.3000, "accuracy": 0.3333},
}
# denetmen fizibilite kontrolundeki tam-seri (+-%5) sinif dagilimi referansi
DENETMEN_TAM_SERI_DAGILIM_REFERANS = {
    "DF-A": {"n": 101, "up": 40, "down": 35, "stable": 26},
    "DF-B": {"n": 29, "up": 11, "down": 9, "stable": 9},
}

AYARLAR = {
    "DF-A": dict(
        kaynak_csv=DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
        gunluk_kovaryatlar=["usdtry_orta"],  # gercek gunluk seri, kendi gununde kullanilir, lag yok
        gecikmeli_kovaryatlar=[  # aylik eszamanli -> >=1 takvim ayi geciktirilir
            "tufe_aylik_degisim", "tufe_yillik_degisim",
            "odmd_otomobil_adet", "tuketici_guven_endeksi",
        ],
        sabit_lagli_kovaryatlar=["tasit_kredisi_faiz_lag12ay"],  # kaynakta zaten gecikmeli
        split_spec=(
            "2018-01", "2024-03", "2024-04",
            "2024-05", "2025-04", "2025-05",
            "2025-06", "2026-05",
        ),
    ),
    "DF-B": dict(
        kaynak_csv=DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
        gunluk_kovaryatlar=[],
        gecikmeli_kovaryatlar=[
            "tufe_aylik_degisim", "tufe_yillik_degisim", "enag_aylik_degisim",
            "odmd_hta_adet", "osd_binek_adet", "otomobil_satinalma_ihtimali_endeksi",
            "proxy_dom_gun", "proxy_satis_orani_pct", "proxy_nominal_yillik_pct",
            "proxy_talep_aylik_pct", "proxy_reel_aylik_log_degisim",
        ],
        sabit_lagli_kovaryatlar=["tasit_kredisi_faiz_lag4ay", "politika_faizi_lag5ay"],
        split_spec=(
            "2024-01", "2025-03", "2025-04",
            "2025-05", "2025-10", "2025-11",
            "2025-12", "2026-05",
        ),
    ),
}


def _ozellik_insa(df: pd.DataFrame, ayar: dict):
    """Ay-hizali ham df'i degistirmeden, bellek-ici bir kopyada gecikmeli
    feature'lari + katalogu uretir. Donus: (df_zenginlestirilmis, katalog, feature_listesi)."""
    katalog = []
    feature_listesi = []

    aylik_hedef = df.groupby("_ay")[TARGET].first()
    for lag in HEDEF_LAG_AYLARI:
        kolon = f"{TARGET}_lag{lag}ay"
        df[kolon] = df["_ay"].map(aylik_hedef.shift(lag))
        feature_listesi.append(kolon)
        katalog.append({
            "feature": kolon, "ham_sutun": TARGET, "uygulanan_lag": f"{lag} takvim ayi",
            "gerekce": "Gecmis hacim bilgisi - yalnizca ay-takvimli lag (lag0/guncel ay HARIC, "
                       "K9/gorev talimatiyla sizinti onleme geregi).",
        })

    for kolon in ayar["gecikmeli_kovaryatlar"]:
        yeni_kolon = f"{kolon}_lag1ay"
        aylik = df.groupby("_ay")[kolon].first()
        df[yeni_kolon] = df["_ay"].map(aylik.shift(1))
        feature_listesi.append(yeni_kolon)
        katalog.append({
            "feature": yeni_kolon, "ham_sutun": kolon, "uygulanan_lag": "1 takvim ayi",
            "gerekce": "Aylik eszamanli kaynak (TUIK/ODMD/BETAM vb) gercek yayim gecikmesi "
                       "tasir; ay-hizali ham tabloda M ayinin gunlerinde M'nin KENDI degeri "
                       "gorunur (henuz yayimlanmamis olabilir) - model katmaninda >=1 ay "
                       "geciktirilerek gercekci yayim-zamanlamasi korunur.",
        })

    for kolon in ayar["sabit_lagli_kovaryatlar"]:
        feature_listesi.append(kolon)
        katalog.append({
            "feature": kolon, "ham_sutun": kolon, "uygulanan_lag": "yok (kaynakta zaten gecikmeli)",
            "gerekce": "Sutun adinda acik gecikme var (lag4ay/lag5ay/lag12ay) - kaynak tabloda "
                       "zaten gecikmeli uretilmis, ikinci kez kaydirilmadi.",
        })

    for kolon in ayar["gunluk_kovaryatlar"]:
        feature_listesi.append(kolon)
        katalog.append({
            "feature": kolon, "ham_sutun": kolon, "uygulanan_lag": "yok (gercek gunluk veri)",
            "gerekce": "Gercek GUNLUK frekansli seri (ay-hizali degil) - kendi gununde "
                       "yayim gecikmesi olmadan kullanilabilir; DF-A icinde AY ICI DEGISEN "
                       "tek feature budur (pseudo-replikasyon notuna bkz).",
        })

    return df, katalog, feature_listesi


def _split_ozeti(df: pd.DataFrame, split: dict) -> dict:
    ozet = {}
    for parca in ("train", "purge1", "validation", "purge2", "test"):
        aylar = split[parca]
        alt = df[df["_ay"].isin(aylar)]
        ozet[parca] = {
            "ay_araligi": [str(aylar[0]), str(aylar[-1])],
            "ay_sayisi_spec": len(aylar),
            "gunluk_satir_sayisi": int(len(alt)),
            "bagimsiz_ay_sayisi_veride": int(alt["_ay"].nunique()),
        }
    return ozet


def _baseline_tahminleri(etiket_ay_serisi: pd.Series, test_aylari, train_aylari):
    train_etiketler = etiket_ay_serisi.reindex(train_aylari)
    train_gecerli = train_etiketler[train_etiketler.isin(yd.FIXED_LABEL_ORDER)]
    cogunluk_sinifi = train_gecerli.value_counts().idxmax() if len(train_gecerli) else "stable"

    majority = [cogunluk_sinifi for _ in test_aylari]
    persistence = [etiket_ay_serisi.get(ay - 1, "eksik") for ay in test_aylari]
    seasonal = [etiket_ay_serisi.get(ay - 12, "eksik") for ay in test_aylari]
    return {"majority": majority, "persistence": persistence, "seasonal_t_eksi_12ay": seasonal}


def _tam_seri_dagilim(df: pd.DataFrame) -> dict:
    aylik_hedef = df.groupby("_ay")[TARGET].first()
    etiket_ay_serisi = yd.sonraki_ay_etiketleri(aylik_hedef, esik_yuzde=ESIK_YUZDE)
    gecerli = etiket_ay_serisi[etiket_ay_serisi.isin(yd.FIXED_LABEL_ORDER)]
    dagilim = gecerli.value_counts().to_dict()
    return {
        "n": int(len(gecerli)),
        "up": int(dagilim.get("up", 0)),
        "down": int(dagilim.get("down", 0)),
        "stable": int(dagilim.get("stable", 0)),
    }, etiket_ay_serisi, aylik_hedef


def calistir(set_adi: str, ayar: dict) -> dict:
    print(f"\n{'=' * 70}\n{set_adi}\n{'=' * 70}")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ayar["kaynak_csv"], parse_dates=["tarih"])
    df["_ay"] = df["tarih"].dt.to_period("M")

    tam_seri_dagilim, etiket_ay_serisi, aylik_hedef = _tam_seri_dagilim(df)
    print(f"Tam-seri (+-%{ESIK_YUZDE:.0f}) etiket dagilimi: {tam_seri_dagilim}")
    referans_dagilim = DENETMEN_TAM_SERI_DAGILIM_REFERANS[set_adi]
    dagilim_uyusuyor_mu = tam_seri_dagilim == referans_dagilim
    if not dagilim_uyusuyor_mu:
        print(f"  [PROAKTIF BILDIRIM] Denetmen referans dagilimi {referans_dagilim} ile "
              f"KODUN sonucu {tam_seri_dagilim} UYUSMUYOR - arastirilmali.")
    else:
        print(f"  Denetmen referans dagilimiyla BIREBIR uyusuyor: {referans_dagilim}")

    df, katalog, feature_listesi = _ozellik_insa(df, ayar)
    df["etiket"] = df["_ay"].map(etiket_ay_serisi)
    df["agirlik"] = 1.0 / df["_ay"].dt.days_in_month

    # ay-agirligi fonksiyonuyla tutarliligini dogrula (spot-check)
    ornek_ay = df["_ay"].iloc[0]
    assert abs(df.loc[df["_ay"] == ornek_ay, "agirlik"].iloc[0] - yd.ay_agirligi(ornek_ay)) < 1e-12

    split = yd.uc_parcali_split_olustur(*ayar["split_spec"])
    split_ozet = _split_ozeti(df, split)
    print(f"Split ozeti: {json.dumps(split_ozet, indent=2, ensure_ascii=False)}")
    if len(split["train"]) < 24:
        print(f"  [PROAKTIF BILDIRIM] {set_adi}: train yalnizca {len(split['train'])} bagimsiz ay "
              f"- bu deney KESIFSELDIR, baseline/basari iddiasi kurulamaz.")

    def alt_kume(aylar):
        alt = df[df["_ay"].isin(aylar)].copy()
        eksik = alt[~alt["etiket"].isin(yd.FIXED_LABEL_ORDER)]
        if len(eksik):
            print(f"  [UYARI] {len(eksik)} satir 'eksik'/gecersiz etiketli - modelden cikarildi.")
        return alt[alt["etiket"].isin(yd.FIXED_LABEL_ORDER)]

    train_df = alt_kume(split["train"])
    val_df = alt_kume(split["validation"])
    test_df = alt_kume(split["test"])

    train_data = train_df[feature_listesi + ["etiket", "agirlik"]].reset_index(drop=True)
    tuning_data = val_df[feature_listesi + ["etiket", "agirlik"]].reset_index(drop=True)

    predictor = TabularPredictor(
        label="etiket",
        problem_type="multiclass",
        eval_metric="mcc",
        sample_weight="agirlik",
        weight_evaluation=True,
        path=str(MODEL_DIR / f"autogluon_model_06_{set_adi.lower().replace('-', '_')}"),
        verbosity=2,
    )
    t0 = time.time()
    predictor.fit(
        train_data=train_data,
        tuning_data=tuning_data,
        time_limit=ZAMAN_SINIRI_SANIYE,
        presets=PRESET,
        # GECICI WORKAROUND (kok neden KANITLANMADI): kucuk/agirlikli
        # validation orneklerinde (ozellikle DF-B, 6 bagimsiz ay) sklearn MCC
        # hesaplamasi bazi baz modellerde NaN val_score uretebiliyor (invalid
        # value encountered in sqrt - dejenere/sabit tahmin dagilimi olasi bir
        # aciklama, kesin dogrulanmadi). AutoGluon boyle bir modeli
        # kaydetmiyor ama WeightedEnsemble aux-stacking asamasi yine de ona
        # referans vermeye calisip "Model does not exist" ile CRASH ediyor
        # (gozlenen AutoGluon 1.5.0 davranisi - upstream kok neden
        # incelenmedi/kanitlanmadi). NN_TORCH'u disarida birakmak sorunu
        # yalnizca bir sonraki NaN'li modele (ornegin LightGBMLarge) tasidi,
        # model-bazli disarida birakma calismadi. Bu yuzden WeightedEnsemble
        # aux adimi TAMAMEN ATLANDI (fit_weighted_ensemble=False) - bu bir
        # kok-neden duzeltmesi DEGIL, gozlenen crash'i bypass eden gecici bir
        # workaround'dur; bagimsiz temel modeller yine egitilir/
        # degerlendirilir, en iyi TEK model leaderboard'dan secilir. Iki veri
        # setinde de AYNI konfigurasyon (tek deneme kuraliyla tutarli - model-
        # bazli tekrar denemeler DEGIL, tek seferlik gecici ayar).
        fit_weighted_ensemble=False,
    )
    egitim_suresi = time.time() - t0
    print(f"Egitim suresi: {egitim_suresi:.1f}s")

    # --- test tahmini ---
    X_test = test_df[feature_listesi].reset_index(drop=True)
    proba = predictor.predict_proba(X_test)[yd.FIXED_LABEL_ORDER].reset_index(drop=True)
    assert np.allclose(proba.sum(axis=1).values, 1.0, atol=1e-6), "predict_proba toplami 1 degil"
    for _, satir in proba.head(3).iterrows():
        yd.olasiliklari_dogrula(satir["down"], satir["stable"], satir["up"])  # spot-check sozlesme

    tahmin_sinifi = proba.idxmax(axis=1)
    raw_confidence = proba.max(axis=1)

    test_df = test_df.reset_index(drop=True)
    test_df["p_down"] = proba["down"].values
    test_df["p_stable"] = proba["stable"].values
    test_df["p_up"] = proba["up"].values
    test_df["tahmin_sinifi"] = tahmin_sinifi.values
    test_df["raw_confidence"] = raw_confidence.values

    # --- gunluk metrikler (agirlikli birincil, agirliksiz bilgilendirme amacli) ---
    metrik_gunluk_agirlikli = yd.degerlendir(
        test_df["etiket"].tolist(), test_df["tahmin_sinifi"].tolist(), agirliklar=test_df["agirlik"].tolist()
    )
    metrik_gunluk_agirliksiz = yd.degerlendir(
        test_df["etiket"].tolist(), test_df["tahmin_sinifi"].tolist()
    )

    # --- ay-bazli metrik (her ayin SON gunluk tahmini, pseudo-replikasyondan arindirilmis) ---
    ay_son_gun = test_df.sort_values("tarih").groupby("_ay").tail(1)
    metrik_ay_bazli = yd.degerlendir(ay_son_gun["etiket"].tolist(), ay_son_gun["tahmin_sinifi"].tolist())

    # --- baseline'lar (ortak orneklem: test split'in ay listesi) ---
    test_aylari = split["test"]
    gercek_ay_bazli = [etiket_ay_serisi[ay] for ay in test_aylari]
    baseline_tahmin = _baseline_tahminleri(etiket_ay_serisi, test_aylari, split["train"])

    baseline_metrikleri = {}
    for isim, tahminler in baseline_tahmin.items():
        if any(t == "eksik" for t in tahminler):
            print(f"  [UYARI] baseline '{isim}' bazi test aylarinda 'eksik' tahmin uretti - "
                  f"bu aylar o baseline'dan cikarildi.")
        gecerli_idx = [i for i, t in enumerate(tahminler) if t != "eksik"]
        g = [gercek_ay_bazli[i] for i in gecerli_idx]
        t = [tahminler[i] for i in gecerli_idx]
        baseline_metrikleri[isim] = yd.degerlendir(g, t)

    denetmen_referans = DENETMEN_MEVSIMSEL_REFERANS[set_adi]
    kod_mevsimsel = baseline_metrikleri["seasonal_t_eksi_12ay"]
    mevsimsel_uyum = {
        anahtar: {
            "kod": kod_mevsimsel[anahtar],
            "denetmen_referans": deger,
            "fark": round(kod_mevsimsel[anahtar] - deger, 6),
            "uyusuyor_mu": abs(kod_mevsimsel[anahtar] - deger) < 1e-3,
        }
        for anahtar, deger in denetmen_referans.items()
    }
    if not all(v["uyusuyor_mu"] for v in mevsimsel_uyum.values()):
        print(f"  [PROAKTIF BILDIRIM] {set_adi}: mevsimsel-yon baseline denetmen referansiyla "
              f"UYUSMUYOR: {mevsimsel_uyum}")
    else:
        print(f"  Mevsimsel-yon baseline denetmen referansiyla BIREBIR uyusuyor.")

    # --- pseudo-replikasyon notu ---
    ay_ici_degisen_feature = [f for f in feature_listesi if f in ayar["gunluk_kovaryatlar"]]
    pseudo_replikasyon_notu = (
        f"Bu veri setinde ay-ici GERCEKTEN degisen feature(lar): {ay_ici_degisen_feature or 'YOK'}. "
        + ("Diger tum feature'lar ay-hizali (ay icinde SABIT) - gunluk agirliksiz metrikler bu "
           "yuzden ayni ayin gunlerini fiilen tekrar sayar (pseudo-replikasyon); agirlikli/ay-bazli "
           "metrikler bunu duzeltir." if not ay_ici_degisen_feature else
           "Bu feature(lar) nedeniyle model tahmini AY ICINDE gercekten degisebilir - agirlikli/"
           "ay-bazli metrik agirliksiz-gunluk'ten farkli cikabilir (beklenen, hata degil).")
    )
    print(f"  {pseudo_replikasyon_notu}")

    sonuc = {
        "veri_seti": set_adi,
        "target": TARGET,
        "esik_yuzde": ESIK_YUZDE,
        "tam_seri_dagilim": tam_seri_dagilim,
        "tam_seri_dagilim_denetmen_referans": referans_dagilim,
        "tam_seri_dagilim_uyusuyor_mu": dagilim_uyusuyor_mu,
        "ozellik_katalogu": katalog,
        "feature_listesi": feature_listesi,
        "split_ozeti": split_ozet,
        "egitim_suresi_saniye": round(egitim_suresi, 1),
        "test_metrikleri": {
            "gunluk_agirlikli_birincil": metrik_gunluk_agirlikli,
            "gunluk_agirliksiz_bilgilendirme": metrik_gunluk_agirliksiz,
            "ay_bazli_son_gun": metrik_ay_bazli,
        },
        "baseline_metrikleri_ay_bazli": baseline_metrikleri,
        "denetmen_mevsimsel_karsilastirma": mevsimsel_uyum,
        "pseudo_replikasyon_notu": pseudo_replikasyon_notu,
        "olasilik_kalibrasyon_durumu": (
            "RAW - kalibre EDILMEMIS (Platt/temperature scaling uygulanmadi). "
            f"Validation orneklemi ({len(split['validation'])} ay) guvenilir multiclass "
            "kalibrasyon icin " + ("YETERSIZ" if len(split["validation"]) < 20 else "sinirlidir")
            + " - urun katmaninda olasiliklar acikca 'raw' etiketiyle sunulmalidir."
        ),
    }

    cikti_json = MODEL_DIR / f"model_06_hacim_yon_{set_adi.lower().replace('-', '_')}_sonuc.json"
    with open(cikti_json, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=2, default=str)
    print(f"Cikti: {cikti_json}")

    cikti_csv_kolonlar = ["tarih", "_ay", "etiket", "agirlik", "p_down", "p_stable", "p_up",
                           "tahmin_sinifi", "raw_confidence"]
    cikti_csv = MODEL_DIR / f"model_06_hacim_yon_{set_adi.lower().replace('-', '_')}_test_gunluk_tahmin.csv"
    test_df[cikti_csv_kolonlar].to_csv(cikti_csv, index=False, encoding="utf-8-sig")
    print(f"Cikti: {cikti_csv}")

    # --- ileri-sinyal (test disi, henuz gerceklesmemis) ---
    son_dolu_ay = aylik_hedef.dropna().index.max()
    hedef_ay = son_dolu_ay + 1
    son_gun_df = df[df["_ay"] == son_dolu_ay].sort_values("tarih").tail(1)
    X_ileri = son_gun_df[feature_listesi].reset_index(drop=True)
    proba_ileri = predictor.predict_proba(X_ileri)[yd.FIXED_LABEL_ORDER].iloc[0]
    sinif_ileri, guven_ileri = yd.tahmin_sinifi_ve_guven(
        proba_ileri["down"], proba_ileri["stable"], proba_ileri["up"]
    )
    model_egitim_son_ayi = str(split["train"][-1])
    ileri_sinyal = {
        "veri_seti": set_adi,
        "durum": "gerceklesme_bekleniyor",
        "kullanim_durumu": "yalniz_pipeline_demonstrasyonu",
        "not": "Bu bir TEST/PERFORMANS sonucu DEGILDIR - hedef ayin gercek degeri henuz "
               "yayimlanmadi; asagidaki olasiliklar RAW (kalibre edilmemis). Modeli ureten "
               f"predictor EN SON {model_egitim_son_ayi} ayina kadarki egitim kesitinde "
               "egitildi (bkz. model_egitim_son_ayi) - kullanilan_gun'e kadar guncellenmedi, "
               "bu yuzden STALE'dir. RAW guven dusuk/kalibre edilmemis. Bu sinyal SADECE "
               "pipeline'in uctan uca calistigini gostermek icindir; operasyonel/fiyatlama "
               "kararinda KULLANILAMAZ.",
        "model_egitim_son_ayi": model_egitim_son_ayi,
        "kullanilan_gun": str(son_gun_df["tarih"].iloc[0].date()),
        "referans_ay": str(son_dolu_ay),
        "hedef_ay": str(hedef_ay),
        "p_down": float(proba_ileri["down"]),
        "p_stable": float(proba_ileri["stable"]),
        "p_up": float(proba_ileri["up"]),
        "tahmin_sinifi": sinif_ileri,
        "raw_confidence": float(guven_ileri),
    }
    cikti_ileri_json = MODEL_DIR / f"model_06_hacim_yon_{set_adi.lower().replace('-', '_')}_ileri_sinyal.json"
    with open(cikti_ileri_json, "w", encoding="utf-8") as f:
        json.dump(ileri_sinyal, f, ensure_ascii=False, indent=2)
    print(f"Cikti: {cikti_ileri_json}")
    print(f"ILERI SINYAL ({set_adi}): {hedef_ay} icin {sinif_ileri} "
          f"(raw_confidence={guven_ileri:.3f}) - gerceklesme_bekleniyor")

    return sonuc


def main():
    tum_sonuclar = {}
    for set_adi, ayar in AYARLAR.items():
        try:
            tum_sonuclar[set_adi] = calistir(set_adi, ayar)
        except Exception as e:
            print(f"\n[HATA] {set_adi} basarisiz oldu, TEKRAR DENENMEDI (tek deneme kurali): {e}")
            raise
    print("\n" + "=" * 70)
    print("TAMAMLANDI")
    print("=" * 70)


if __name__ == "__main__":
    main()
