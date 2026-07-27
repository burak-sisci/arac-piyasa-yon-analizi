"""
GENIŞLETME AŞAMA 7 — Hedef-aday karşılaştırması ve korelasyon analizi.

Bu script MODEL KURMAZ, TAHMİN YAPMAZ, HEDEF TANIMINI DEĞİŞTİRMEZ. Yalnızca
keşifsel bir analiz üretir: 6 potansiyel hedef adayının her biri için aylık
log-değişim + oynaklık-uyarlamalı (k=0.5) bant etiketlemesi dener, ve TÜM
feature'ların aylık log-değişimleriyle TÜM hedef adaylarının aylık
log-değişimleri arasında Pearson + Spearman korelasyonu hesaplar.

AZ-GÖZLEM UYARISI (ZORUNLU, bkz. çıktı ve rapor): Bu projedeki p-değerleri
25-101 gözlemle hesaplanıyor. Bu, istatistiksel anlamlılık testleri için
KÜÇÜK bir örneklem — "düşük p-değeri" veya "yüksek korelasyon" burada
KANITLANMIŞ BİR NEDENSELLİK DEĞİLDİR, yalnızca bu örneklemdeki bir ilişki
sinyalidir. Çoklu-test problemi de var (çok sayıda çift test ediliyor);
sonuçlar kesin bulgu değil, ekip lideri toplantısı için başlangıç noktası
olarak okunmalıdır (bkz. karar kaydı N7, N12 - çoklu-test farkındalığı).

Girdi: data/processed/genisletme/veri_2018_bugun_etiketli.csv
Çıktı:
  - data/processed/analiz/hedef_aday_karsilastirma.csv
  - data/processed/analiz/korelasyon_matrisi.csv
  - data/processed/analiz/zaman_serileri.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO_KOKU = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_KOKU / "data" / "processed" / "genisletme"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"

ESIK_K = 0.5

# (hedef_adi, kaynak_kolon, ters_yorum_notu)
HEDEF_ADAYLARI = [
    ("proxy_nominal", "proxy_fiyat_cari_tl", None),
    ("proxy_reel", None, None),  # zaten proxy_reel_aylik_log_degisim var, ayrica hesaplanmaz
    ("noter_devir_hacim", "noter_devir_toplam_adet", None),
    ("proxy_dom_gun", "proxy_dom_gun", "TERS YORUM: dom dusuyorsa piyasa HIZLANIYOR (pozitif sinyal)"),
    ("proxy_satis_orani", "proxy_satis_orani_pct", None),
    ("odmd_toplam_satis", "odmd_toplam_adet", None),
]

# Bazi hedef adaylari dogrudan bir feature'dan turetiliyor (ayni/neredeyse ayni
# seri) - bu ciftleri korelasyondan HARIC TUT, aksi halde tautolojik (r~1.0)
# "sahte bulgu" uretilir (ornek: noter_devir_hacim hedefi = noter_devir_toplam_adet
# feature'inin log-degisimi; ikisini "korele" gostermek anlamsizdir).
TAUTOLOJIK_HARIC_TUT = {
    "noter_devir_hacim": {"noter_devir_toplam_adet", "noter_devir_otomobil_adet"},
    "odmd_toplam_satis": {"odmd_toplam_adet", "odmd_otomobil_adet"},
}

FEATURE_KOLONLARI = [
    "usdtry_aysonu", "usdtry_ortalama", "tufe_endeks",
    "tasit_kredisi_faiz", "politika_faizi",
    "odmd_toplam_adet", "odmd_otomobil_adet",
    "osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet",
    "tuketici_guven_endeksi", "otomobil_satinalma_ihtimali_endeksi",
    "noter_devir_toplam_adet", "noter_devir_otomobil_adet",
    "brut_ucret_maas_endeksi_2021_100", "erisim_endeksi",
]

# Beklenen iliski yonu (ekonomik hipotez, kanit degil) - yalniz raporlama/isaretleme icin.
# "belirsiz" = proje karar kaydinda (N2) rejime bagli cift-yonlu olarak isaretlenmis degiskenler.
BEKLENEN_YON = {
    "usdtry_aysonu": "pozitif (TL degeri kaybi -> nominal fiyat artar)",
    "usdtry_ortalama": "pozitif (TL degeri kaybi -> nominal fiyat artar)",
    "tufe_endeks": "pozitif (nominal fiyat genel enflasyonu takip eder)",
    "tasit_kredisi_faiz": "negatif (kredi maliyeti artar -> talep/fiyat baskisi asagi)",
    "politika_faizi": "negatif (genel kredi kosullari sikilasir -> talep/fiyat baskisi asagi)",
    "odmd_toplam_adet": "belirsiz (N2: arz degiskeni rejime bagli cift yonlu)",
    "odmd_otomobil_adet": "belirsiz (N2: arz degiskeni rejime bagli cift yonlu)",
    "osd_binek_adet": "belirsiz (N2: arz degiskeni rejime bagli cift yonlu)",
    "osd_kamyonet_adet": "belirsiz (N2: arz degiskeni rejime bagli cift yonlu)",
    "osd_binek_kamyonet_toplam_adet": "belirsiz (N2: arz degiskeni rejime bagli cift yonlu)",
    "tuketici_guven_endeksi": "pozitif (guven artar -> talep/fiyat artar)",
    "otomobil_satinalma_ihtimali_endeksi": "pozitif (dogrudan talep gostergesi)",
    "noter_devir_toplam_adet": "pozitif (islem hacmi/talep gostergesi)",
    "noter_devir_otomobil_adet": "pozitif (islem hacmi/talep gostergesi)",
    "brut_ucret_maas_endeksi_2021_100": "pozitif (alim gucu artar -> talep/fiyat artar)",
    "erisim_endeksi": "pozitif (erisilebilirlik/talep baskisi artar -> fiyat artar)",
}

# erisim_endeksi = noter_devir_toplam_adet / alim_gucu_endeksi - noter_devir_hacim
# hedefiyle karsilastirilirken PAYDA/PAY paylasimi nedeniyle mekanik olarak sisirilmis
# bir korelasyon bekleniyor (tam tautoloji degil ama guclu yapisal bag var).
YAPISAL_BAGIMLILIK_UYARISI = {
    ("erisim_endeksi", "noter_devir_hacim"): "erisim_endeksi'nin payi noter_devir_toplam_adet - mekanik olarak sisirilmis korelasyon beklenir, bagimsiz bir sinyal DEGIL",
    ("tufe_endeks", "proxy_reel"): "proxy_reel = proxy_fiyat_cari_tl / tufe_endeks olarak TANIMLANIYOR - bu korelasyon yari-mekanik/tanimsal, bagimsiz bir ekonomik bulgu olarak OKUNMAMALI",
}


def _log_degisim(seri: pd.Series) -> pd.Series:
    return np.log(seri / seri.shift(1))


def _oynaklik_bandi_etiket(log_degisim: pd.Series, k: float):
    sigma = log_degisim.std(ddof=1)
    esik = k * sigma

    def etiketle(x):
        if pd.isna(x):
            return "eksik"
        if x >= esik:
            return "up"
        if x <= -esik:
            return "down"
        return "stable"

    return log_degisim.map(etiketle), sigma


def main():
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)

    girdi = PROCESSED_DIR / "veri_2018_bugun_etiketli.csv"
    df = pd.read_csv(girdi).sort_values("referans_ayi").reset_index(drop=True)

    # --- 4a: hedef adaylari icin log-degisim + oynaklik-bandi etiketi ---
    hedef_log_kolonlari = {}
    hedef_ozet_satirlari = []

    for hedef_adi, kaynak_kolon, ters_not in HEDEF_ADAYLARI:
        if hedef_adi == "proxy_nominal":
            log_kolon = df["proxy_aylik_log_degisim"]
        elif hedef_adi == "proxy_reel":
            log_kolon = df["proxy_reel_aylik_log_degisim"]
        else:
            log_kolon = _log_degisim(df[kaynak_kolon])

        etiket, sigma = _oynaklik_bandi_etiket(log_kolon, ESIK_K)
        hedef_log_kolonlari[hedef_adi] = log_kolon

        gecerli_n = log_kolon.notna().sum()
        dagilim = etiket.value_counts().to_dict()
        hedef_ozet_satirlari.append({
            "hedef_adayi": hedef_adi,
            "gecerli_gozlem_n": int(gecerli_n),
            "toplam_ay": len(df),
            "sigma_log_degisim": round(float(sigma), 5) if pd.notna(sigma) else None,
            "esik_k": ESIK_K,
            "up_sayisi": dagilim.get("up", 0),
            "stable_sayisi": dagilim.get("stable", 0),
            "down_sayisi": dagilim.get("down", 0),
            "eksik_sayisi": dagilim.get("eksik", 0),
            "ters_yorum_notu": ters_not or "",
            "az_gozlem_uyarisi": "EVET" if gecerli_n < 50 else ("DIKKAT" if gecerli_n < 80 else "hayir"),
        })

    hedef_ozet = pd.DataFrame(hedef_ozet_satirlari)
    hedef_ozet_csv = ANALIZ_DIR / "hedef_aday_karsilastirma.csv"
    hedef_ozet.to_csv(hedef_ozet_csv, index=False, encoding="utf-8-sig")

    # --- 4b: feature log-degisimleri ---
    feature_log_kolonlari = {}
    for kol in FEATURE_KOLONLARI:
        feature_log_kolonlari[kol] = _log_degisim(df[kol])

    # --- korelasyon matrisi (feature x hedef, Pearson + Spearman) ---
    satirlar = []
    haric_toplam = 0
    for feat_adi, feat_seri in feature_log_kolonlari.items():
        for hedef_adi, hedef_seri in hedef_log_kolonlari.items():
            if feat_adi in TAUTOLOJIK_HARIC_TUT.get(hedef_adi, set()):
                haric_toplam += 1
                continue
            ortak = pd.concat([feat_seri, hedef_seri], axis=1).dropna()
            n = len(ortak)
            if n < 3:
                pearson_r = pearson_p = spearman_r = spearman_p = None
            else:
                pearson_r, pearson_p = stats.pearsonr(ortak.iloc[:, 0], ortak.iloc[:, 1])
                spearman_r, spearman_p = stats.spearmanr(ortak.iloc[:, 0], ortak.iloc[:, 1])
                pearson_r, pearson_p = round(float(pearson_r), 4), round(float(pearson_p), 4)
                spearman_r, spearman_p = round(float(spearman_r), 4), round(float(spearman_p), 4)

            beklenen = BEKLENEN_YON.get(feat_adi, "?")
            tutarli_mi = ""
            if pearson_r is not None and beklenen.startswith(("pozitif", "negatif")):
                beklenen_isaret = 1 if beklenen.startswith("pozitif") else -1
                gozlenen_isaret = 1 if pearson_r > 0 else (-1 if pearson_r < 0 else 0)
                tutarli_mi = "TUTARLI" if beklenen_isaret == gozlenen_isaret else "TUTARSIZ (beklenene AYKIRI)"

            satirlar.append({
                "feature": feat_adi,
                "hedef_adayi": hedef_adi,
                "pearson_r": pearson_r,
                "pearson_p": pearson_p,
                "spearman_r": spearman_r,
                "spearman_p": spearman_p,
                "n_ortak_gozlem": n,
                "az_gozlem_uyarisi": "EVET" if n < 50 else ("DIKKAT" if n < 80 else "hayir"),
                "beklenen_yon": beklenen,
                "beklenenle_tutarli_mi": tutarli_mi,
                "yapisal_bagimlilik_notu": YAPISAL_BAGIMLILIK_UYARISI.get((feat_adi, hedef_adi), ""),
            })

    korelasyon = pd.DataFrame(satirlar)
    korelasyon_csv = ANALIZ_DIR / "korelasyon_matrisi.csv"
    korelasyon.to_csv(korelasyon_csv, index=False, encoding="utf-8-sig")

    # --- zaman serileri (grafik-hazir, wide format) ---
    zaman_serileri = pd.DataFrame({"referans_ayi": df["referans_ayi"]})
    for feat_adi, seri in feature_log_kolonlari.items():
        zaman_serileri[f"feature__{feat_adi}__log_degisim"] = seri
    for hedef_adi, seri in hedef_log_kolonlari.items():
        zaman_serileri[f"hedef__{hedef_adi}__log_degisim"] = seri
    zaman_serileri_csv = ANALIZ_DIR / "zaman_serileri.csv"
    zaman_serileri.to_csv(zaman_serileri_csv, index=False, encoding="utf-8-sig")

    # --- ozet ciktisi ---
    print("=== GENISLETME 7 - KORELASYON VE HEDEF-ADAY ANALIZI OZETI ===")
    print()
    print("!!! AZ-GOZLEM UYARISI: p-degerleri 25-101 gozlemle hesaplandi. Bu KUCUK")
    print("!!! bir orneklem - 'yuksek korelasyon' KANITLANMIS NEDENSELLIK DEGILDIR.")
    print("!!! Coklu-test problemi de var (cok sayida cift test edildi). Sonuclar")
    print("!!! kesin bulgu degil, ekip lideri toplantisi icin baslangic noktasidir.")
    print()
    print("--- Hedef aday karsilastirmasi ---")
    print(hedef_ozet.to_string(index=False))
    print()
    print(f"(Not: {haric_toplam} feature-hedef cifti TAUTOLOJIK oldugu icin haric tutuldu - hedefin kendisinin turedigi feature'lar.)")
    print()
    print("--- En yuksek |Pearson r| gosteren 10 feature-hedef cifti ---")
    en_yuksek = korelasyon.dropna(subset=["pearson_r"]).reindex(
        korelasyon["pearson_r"].abs().sort_values(ascending=False).index
    ).head(10)
    print(en_yuksek[["feature", "hedef_adayi", "pearson_r", "pearson_p", "spearman_r",
                      "n_ortak_gozlem", "beklenenle_tutarli_mi"]].to_string(index=False))
    print()
    print(f"Cikti: {hedef_ozet_csv}")
    print(f"Cikti: {korelasyon_csv}")
    print(f"Cikti: {zaman_serileri_csv}")


if __name__ == "__main__":
    main()
