"""
GENIŞLETME AŞAMA 5 — Tüm genişletilmiş serilerin birleştirilmesi, 2015-01 -> 2026-06.

Kapsam üst sınırı 2026-06'dır (proxy fiyat ve ODMD'nin kendi yapısal yayım
gecikmesi nedeniyle - bkz. ilgili script'lerin docstring'leri). Alt sınır
ÖNCE 2018-01'e cekilmisti (proje sahibinin talebiyle,
prompts/veri/06_genisletme_2018_korelasyon_prompt.md), SONRA 2015-01'e
genisletildi (prompts/veri/18_genisletme_2015_prompt.md, "NET KAPSAM KARARI"
- proxy fiyat/BETAM ve ENAG haric TUM diger feature'lar 2015'e cekildi).
proxy fiyat (BETAM) 2024-01'den once veri VERMEZ (bilinen kisit, bu genisletme
turunun kapsami DISINDA tutuldu - bkz. YAPMA maddeleri) - bu yuzden
proxy_fiyat_cari_tl ve ona bagli hedef etiket sutunlari 2015-01..2023-12
araliginda NaN kalacak.

BRUT UCRET-MAAS ENDEKSI / ERISIM ENDEKSI 2015'E CEKILEMEDI (ONEMLI, ayrica
asagida da not edilecek): TÜİK veri portalindaki indirme linki bu turda SPA
route'una donusmustu, 2015-2017 ceyreklerine erisilemedi (bkz.
genisletme_2b_alim_gucu.py docstring). Bu yuzden brut_ucret_maas_endeksi_2021_100
VE ondan turetilen erisim_endeksi 2015-01..2017-12 icin NaN kalacak, 2018-01'de
baslamaya devam ediyor - bu veri kaybi degil, ERISIM ENGELIDIR.

NOTER DEVIR ADEDI 2015-2017 ICIN metodoloji farkli (bkz. genisletme_2a_noter_devir.py):
36 ay icin TOPLAM devir TAM/guvenilir (bulten metninden), ama
noter_devir_otomobil_adet bilincli olarak NaN (yalnizca yuvarlanmis yuzde
mevcuttu, uydurulmadi).

DAHIL EDILEN: USD/TRY (A), TÜFE (A - 2026-01 baz degisikligi zincirleme
yontemiyle cozuldu, bkz. genisletme_1b_tufe.py), proxy fiyat/BETAM (C+D),
taşıt kredisi faizi + politika faizi (A), ODMD sıfır araç satışı (C),
ÖTV event-dummy (2015-2017 icin 1 yeni olay eklendi, bkz.
genisletme_4_otv_olaylari.py), OSD yerli uretim (A), tuketici guven endeksi +
otomobil satinalma ihtimali (A), noter devir adedi (B - TÜİK resmi tablo +
2015-2017 icin bulten metni, bkz. genisletme_2a_noter_devir.py), alim gucu
proxy'si / brut ucret-maas endeksi (B - TÜİK resmi tablo, ceyreklik->aylik
genisletildi, yalnizca 2018-01'den itibaren, bkz. genisletme_2b_alim_gucu.py).

ERISILEBILIRLIK ENDEKSI (2c) COZULDU: orijinal gorev promptu
(prompts/veri/03_genis_veri_cekme_prompt.md, Asama 2c) formulu zaten
tanimliyordu - "erisim_endeksi = noter_devir_adedi / alim_gucu_proxy".
Bu bir FEATURE'dir (K8: hedef degil, talep/likidite sinyali), yeni veri
cekmeye gerek yok - 2a+2b zaten birlesik tabloda oldugu icin burada
dogrudan turetiliyor (ancak alim_gucu 2018-01'den once NaN oldugundan,
erisim_endeksi de 2015-01..2017-12 icin NaN cikacaktir).

HEDEF ETIKET: Bu script SADECE BIRLESTIRIR; etiket uretimi (Asama 5'in
"HEDEF ETIKET" alt-basligi, k*sigma bandi vb.) ayrı bir onay/adimdir ve
burada YAPILMADI. Proxy fiyat donemi degismedigi icin hedef zinciri
(genisletme_6_hedef_etiket.py) mantigina DOKUNULMADI - yalnizca girdi dosya
adi (veri_2015_bugun_birlesik.csv) guncellenmesi gerekecek.
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw"
PROCESSED_DIR = REPO_KOKU / "data" / "processed" / "genisletme"

HEDEF_BASLANGIC = "2015-01"
HEDEF_BITIS = "2026-06"


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    usdtry = pd.read_csv(RAW_DIR / "usdtry" / "usdtry_2018_bugun_aylik.csv")[
        ["referans_ayi", "usdtry_aysonu", "usdtry_ortalama"]
    ]

    tufe = pd.read_csv(RAW_DIR / "tufe" / "tufe_2024_bugun_aylik.csv").rename(
        columns={"yayim_tarihi": "tufe_yayim_tarihi"}
    )[["referans_ayi", "tufe_endeks", "tufe_aylik_degisim", "tufe_yillik_degisim", "tufe_yayim_tarihi"]]

    proxy_ham = pd.read_csv(RAW_DIR / "proxy_fiyat" / "proxy_fiyat_2024_bugun_raw.csv")
    betam_maske = proxy_ham["kaynak"] == "BETAM sahibindex"
    proxy = proxy_ham[["referans_ayi", "proxy_dom_gun", "proxy_satis_orani_pct", "yayim_ayi"]].copy()
    proxy["proxy_fiyat_cari_tl"] = proxy_ham["proxy_fiyat_cari_tl"].where(betam_maske)
    proxy["proxy_kaynak"] = betam_maske.map({True: "BETAM sahibindex", False: "eksik (BETAM rapor yayımlamadı)"})
    proxy["proxy_fiyat_arabamcom_referans_tl"] = proxy_ham.get("proxy_fiyat_arabamcom_referans_tl")
    proxy = proxy.rename(columns={"yayim_ayi": "proxy_yayim_ayi"})

    faizler = pd.read_csv(RAW_DIR / "faiz" / "faizler_2024_bugun_aylik.csv")

    odmd = pd.read_csv(RAW_DIR / "odmd" / "odmd_2015_bugun_aylik.csv")

    otv = pd.read_csv(RAW_DIR / "otv" / "otv_olaylari_2015_bugun_aylik.csv")

    osd = pd.read_csv(RAW_DIR / "osd" / "osd_2024_bugun_aylik.csv")

    tuketici_guveni = pd.read_csv(RAW_DIR / "tuketici_guveni" / "tuketici_guveni_2024_bugun_aylik.csv")

    noter_devir = pd.read_csv(RAW_DIR / "noter_devir" / "noter_devir_2015_bugun_aylik.csv")[
        ["referans_ayi", "noter_devir_toplam_adet", "noter_devir_otomobil_adet"]
    ]

    alim_gucu = pd.read_csv(RAW_DIR / "alim_gucu" / "alim_gucu_2018_bugun_aylik.csv")[
        ["referans_ayi", "brut_ucret_maas_endeksi_2021_100", "alim_gucu_ceyrek"]
    ]

    birlesik = usdtry.merge(tufe, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(proxy, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(faizler, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(odmd, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(otv, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(osd, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(tuketici_guveni, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(noter_devir, on="referans_ayi", how="outer")
    birlesik = birlesik.merge(alim_gucu, on="referans_ayi", how="outer")

    birlesik = birlesik[
        (birlesik["referans_ayi"] >= HEDEF_BASLANGIC) & (birlesik["referans_ayi"] <= HEDEF_BITIS)
    ].sort_values("referans_ayi").reset_index(drop=True)

    # --- 2c: erisilebilirlik/talep orani (FEATURE, hedef degil - K8) ---
    # Formul, orijinal gorev promptunda (Asama 2c) tanimlanmisti:
    # erisim_endeksi = noter_devir_adedi / alim_gucu_proxy
    birlesik["erisim_endeksi"] = (
        birlesik["noter_devir_toplam_adet"] / birlesik["brut_ucret_maas_endeksi_2021_100"]
    )

    # ESKI DOSYALAR (kapsam artik 2015-01'den basladigi icin gecersiz) silinir.
    eski_csv = PROCESSED_DIR / "veri_2018_bugun_birlesik.csv"
    eski_xlsx = PROCESSED_DIR / "veri_2018_bugun_birlesik.xlsx"
    for eski in (eski_csv, eski_xlsx):
        if eski.exists():
            eski.unlink()

    csv_yolu = PROCESSED_DIR / "veri_2015_bugun_birlesik.csv"
    xlsx_yolu = PROCESSED_DIR / "veri_2015_bugun_birlesik.xlsx"
    birlesik.to_csv(csv_yolu, index=False, encoding="utf-8-sig")
    birlesik.to_excel(xlsx_yolu, index=False, sheet_name="veri_2015_bugun")

    print("=== GENISLETME 5 - BIRLESTIRME OZETI ===")
    print(f"Kapsam: {HEDEF_BASLANGIC} .. {HEDEF_BITIS} ({len(birlesik)} satir)")
    print(f"Toplam sutun: {birlesik.shape[1]}")
    print(f"Toplam eksik hucre: {int(birlesik.isna().sum().sum())} / {birlesik.size}")
    print()
    print("Sutun basina eksik:")
    print(birlesik.isna().sum().to_string())
    print(f"\nCikti: {csv_yolu} , {xlsx_yolu}")


if __name__ == "__main__":
    main()
