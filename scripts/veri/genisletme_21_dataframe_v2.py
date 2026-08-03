"""
GENIŞLETME AŞAMA 21 — DataFrame'lerin YENİ mantıkla yeniden kurulması
(prompts/21_dataframe_yeniden_kurulum_prompt.md).

Önceki tur (genisletme_19_iki_dataframe.py) "sütun kısmen doluysa NaN'larla
birlikte dahil et" mantığıyla çalışıyordu. Bu tur FARKLI bir mantık
kullanıyor: "sütun, hedef pencereyi TARİHSEL OLARAK KAPSIYOR mu (kaynağı
yeterince erken başlıyor mu) — kapsıyorsa dahil et (içindeki tekil/ara
boşluklar sorun değil), kapsamıyorsa (kaynağı o pencerede YAPISAL olarak
hiç yok, ör. BETAM'ın 2024 öncesi) sütunu HİÇ ALMA."

GÖREV 1 KARARI — NOTER DEVRİ BAŞLANGIÇ TARİHİ: Prompt "noter_devir_toplam_adet
(veya otomobile özgü varsa noter_devir_otomobil_adet)" diyordu. Omurgada HER
İKİSİ de var: noter_devir_toplam_adet 2015-01'den (138/138),
noter_devir_otomobil_adet 2018-01'den (102/138) dolu. Proje kapsamının
(K1: yolcu otomobili piyasası) otomobile özgü olması ve prompt'un
"otomobile özgü VARSA onu kullan" ifadesi nedeniyle ANKOR olarak
noter_devir_otomobil_adet (2018-01) SEÇİLDİ — bu, DF-A'nın başlangıcını
2015-01 değil 2018-01 yapıyor. Bu bir yorum kararıdır, PM raporunda
açıkça işaretlendi; toplam seri (2015-01) kullanılsaydı DF-A'nın kapsama
testi neredeyse hiçbir şeyi elemeyecekti (zaten tüm 2015-başlangıçlı
sütunlar geçerdi) - bu yüzden otomobile-özgü anlamlı bir pencere sağlıyor.

Bu script SADECE filtreleme/birleştirme yapar - enterpolasyon, yeni
feature türetme, hedef değişikliği YOK.
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
GENISLETME_DIR = REPO_KOKU / "data" / "processed" / "genisletme"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"
DATAFRAMES_DIR = REPO_KOKU / "data" / "processed" / "dataframes"

OMURGA_YOLU = GENISLETME_DIR / "veri_2015_bugun_etiketli.csv"
ENAG_YOLU = ANALIZ_DIR / "tufe_enag_karsilastirma.csv"

ENAG_SUTUN_HARITASI = {
    "enag_aylik": "enag_aylik",
    "enag_yillik": "enag_yillik",
    "fark_yillik": "enag_tufe_fark_yillik",
    "kaynak_seviyesi": "enag_kaynak_seviyesi",
    "kaynak_url": "enag_kaynak_url",
}

DF_B_BASLANGIC = "2024-01"  # BETAM'in gercek baslangici


def _sutun_ilk_dolu_ayi(df: pd.DataFrame, sutun: str) -> str | None:
    dolu = df[df[sutun].notna()]
    return dolu["referans_ayi"].min() if len(dolu) else None


def main():
    omurga = pd.read_csv(OMURGA_YOLU)
    enag_ham = pd.read_csv(ENAG_YOLU)
    enag = enag_ham[["referans_ayi", *ENAG_SUTUN_HARITASI.keys()]].rename(columns=ENAG_SUTUN_HARITASI)

    universe = omurga.merge(enag, on="referans_ayi", how="left").sort_values("referans_ayi").reset_index(drop=True)
    veri_sutunlari = [c for c in universe.columns if c != "referans_ayi"]

    # --- GOREV 1: noter devri baslangic tarihi ---
    noter_toplam_baslangic = _sutun_ilk_dolu_ayi(universe, "noter_devir_toplam_adet")
    noter_otomobil_baslangic = _sutun_ilk_dolu_ayi(universe, "noter_devir_otomobil_adet")
    df_a_baslangic = noter_otomobil_baslangic  # bkz. docstring - yorum karari

    # --- GOREV 2: DF-A - kapsama testi ---
    # "Hedef etiket" grubu - proxy fiyata TAMAMEN bagimli, gercek baslangici
    # kendi (placeholder ile dolu gorunen) sutunundan degil proxy_fiyat_cari_tl'den
    # okunur (Gorev 4).
    hedef_etiket_grubu = [
        "proxy_yon_nominal", "proxy_yon_reel", "proxy_yon_tercile",
        "kullanilan_esik_k", "kullanilan_sigma_nominal", "kullanilan_sigma_reel",
    ]
    proxy_fiyat_baslangic = _sutun_ilk_dolu_ayi(universe, "proxy_fiyat_cari_tl")

    df_a_gecen = []
    df_a_gecemeyen = []
    for sutun in veri_sutunlari:
        if sutun in hedef_etiket_grubu:
            gercek_baslangic = proxy_fiyat_baslangic
        else:
            gercek_baslangic = _sutun_ilk_dolu_ayi(universe, sutun)
        if gercek_baslangic is not None and gercek_baslangic <= df_a_baslangic:
            df_a_gecen.append(sutun)
        else:
            df_a_gecemeyen.append((sutun, gercek_baslangic))

    df_a = universe[universe["referans_ayi"] >= df_a_baslangic][["referans_ayi", *df_a_gecen]].reset_index(drop=True)

    df_a_csv = DATAFRAMES_DIR / "df_a_kapsama_testli_v2.csv"
    df_a_xlsx = DATAFRAMES_DIR / "df_a_kapsama_testli_v2.xlsx"
    df_a.to_csv(df_a_csv, index=False, encoding="utf-8-sig")
    df_a.to_excel(df_a_xlsx, index=False, sheet_name="df_a_v2")

    # --- GOREV 3: DF-B - tum sutunlar, 2024-01 -> bugun (tarih araligi, non-null filtresi degil) ---
    df_b = universe[universe["referans_ayi"] >= DF_B_BASLANGIC].reset_index(drop=True)

    df_b_csv = DATAFRAMES_DIR / "df_b_zengin_2024_bugun_v2.csv"
    df_b_xlsx = DATAFRAMES_DIR / "df_b_zengin_2024_bugun_v2.xlsx"
    df_b.to_csv(df_b_csv, index=False, encoding="utf-8-sig")
    df_b.to_excel(df_b_xlsx, index=False, sheet_name="df_b_v2")

    # --- ozet cikti ---
    print("=== GENISLETME 21 - DATAFRAME V2 KURULUMU OZETI ===")
    print(f"\nGOREV 1 - Noter devri baslangic tarihleri:")
    print(f"  noter_devir_toplam_adet   ilk dolu: {noter_toplam_baslangic}")
    print(f"  noter_devir_otomobil_adet ilk dolu: {noter_otomobil_baslangic}")
    print(f"  DF-A ankor olarak SECILEN: {df_a_baslangic} (noter_devir_otomobil_adet)")

    print(f"\nGOREV 2 - DF-A: {df_a.shape[0]} satir x {df_a.shape[1]} sutun, "
          f"{df_a['referans_ayi'].min()} .. {df_a['referans_ayi'].max()}")
    print(f"  Kapsama testini GECEN sutun sayisi: {len(df_a_gecen)}")
    print(f"  Kapsama testini GECEMEYEN sutun sayisi: {len(df_a_gecemeyen)}")
    for s, b in df_a_gecemeyen:
        print(f"    - {s}: gercek baslangic={b}")
    print(f"  Cikti: {df_a_csv} , {df_a_xlsx}")

    print(f"\nGOREV 3 - DF-B: {df_b.shape[0]} satir x {df_b.shape[1]} sutun, "
          f"{df_b['referans_ayi'].min()} .. {df_b['referans_ayi'].max()}")
    print(f"  Cikti: {df_b_csv} , {df_b_xlsx}")

    print("\nDF-A icindeki kalan eksik hucreler (sutun basina):")
    print(df_a.isna().sum()[df_a.isna().sum() > 0].to_string())

    print("\nDF-B icindeki kalan eksik hucreler (sutun basina):")
    print(df_b.isna().sum()[df_b.isna().sum() > 0].to_string())


if __name__ == "__main__":
    main()
