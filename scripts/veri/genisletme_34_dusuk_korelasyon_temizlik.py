"""
GENIŞLETME AŞAMA 34 — target (noter_devir_toplam_adet) ile |Pearson r|<0.2
olan TÜM sayısal feature'ları DF-A ve DF-B'den kaldırır.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla)

YÖNTEM:
- Metin/tarih sutunlari (tarih, tum "..._referans_ay" sutunlari) zaten
  Pearson'a girmez - otomatik disarida tutulur (hesaplanamaz).
- Kendi "..._referans_ay" companion'i olan sutunlar (altin, tufe, enag,
  noter_devir_otomobil_adet, odmd, osd, tuketici, proxy, alim_gucu, faiz
  ve faiz-lag turevleri) ONCE AYLIGA COLLAPSE edilip target'in KENDI
  aylik collapse'iyle birlestirilir (pseudo-replikasyon onceki
  gorevlerle TUTARLI sekilde onlenir).
- Referans_ay'i olmayan GERCEK GUNLUK sutunlar (usdtry_*, eurtry_*) ve
  takvim sutunlari (yil, ay, gun, ceyrek, haftanin_gunu, yilin_gunu)
  DOGRUDAN gunluk satirlar uzerinden (pairwise dropna) hesaplanir - bu
  sutunlarin "aya collapse" edilecek bir referans_ay'i yok.
- |r| < 0.2 olan TUM sutunlar listelenir ve DF'den SILINIR (yedeklenerek).

Girdi/Cikti (yerinde guncellenir, YEDEKLENEREK):
  data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
  data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
"""
import shutil
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
YEDEK_DIR = DF_DIR / "yedek"

TARGET = "noter_devir_toplam_adet"
TARGET_REFERANS_AY = "noter_referans_ay"
ESIK = 0.2

DOSYALAR = {
    "DF-A": DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
    "DF-B": DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
}

# sutun_onek -> referans_ay_sutunu (bu onekle baslayan TUM sayisal
# sutunlar bu referans_ay ile aya collapse edilir)
REFERANS_AY_GRUPLARI = {
    "altin_": "altin_referans_ay",
    "tufe_": "tufe_referans_ay",
    "enag_": "enag_referans_ay",
    "noter_devir_otomobil_adet": "noter_referans_ay",
    "odmd_": "odmd_referans_ay",
    "osd_": "osd_referans_ay",
    "tuketici_": "tuketici_referans_ay",
    "otomobil_satinalma_ihtimali_endeksi": "tuketici_referans_ay",
    "proxy_": "proxy_referans_ay",
    "brut_ucret_maas_endeksi_2021_100": "alim_gucu_referans_ay",
    "tasit_kredisi_faiz": "faiz_referans_ay",
    "politika_faizi": "faiz_referans_ay",
}

GUNLUK_DOGRUDAN = [
    "usdtry_alis", "usdtry_satis", "usdtry_orta",
    "eurtry_alis", "eurtry_satis", "eurtry_orta",
    "yil", "ay", "gun", "ceyrek", "haftanin_gunu", "yilin_gunu",
]


def _referans_ay_bul(kolon: str):
    for onek, referans_ay in REFERANS_AY_GRUPLARI.items():
        if kolon == onek or kolon.startswith(onek):
            return referans_ay
    return None


def _aylik_collapse(df: pd.DataFrame, referans_ay_col: str, deger_kolonu: str) -> pd.DataFrame:
    aylik = df[[referans_ay_col, deger_kolonu]].dropna(subset=[referans_ay_col])
    aylik = aylik.drop_duplicates(subset=referans_ay_col).sort_values(referans_ay_col).reset_index(drop=True)
    return aylik


def main():
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)

    for df_adi, yol in DOSYALAR.items():
        print(f"\n=== {df_adi} ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])

        referans_ay_kolonlari = [c for c in df.columns if c.endswith("_referans_ay")]
        haric_tutulan = {"tarih", TARGET} | set(referans_ay_kolonlari)
        sayisal_kolonlar = [
            c for c in df.columns
            if c not in haric_tutulan and pd.api.types.is_numeric_dtype(df[c])
        ]

        target_aylik = _aylik_collapse(df, TARGET_REFERANS_AY, TARGET)

        sonuclar = []
        for kolon in sayisal_kolonlar:
            referans_ay = _referans_ay_bul(kolon)
            if referans_ay is not None:
                feature_aylik = _aylik_collapse(df, referans_ay, kolon)
                birlesik = feature_aylik.merge(
                    target_aylik, left_on=referans_ay, right_on=TARGET_REFERANS_AY, how="inner"
                )
                gecerli = birlesik[[kolon, TARGET]].dropna()
                yontem = "aylik-collapse"
            elif kolon in GUNLUK_DOGRUDAN:
                gecerli = df[[kolon, TARGET]].dropna()
                yontem = "gunluk-dogrudan"
            else:
                print(f"  [UYARI] {kolon} icin referans_ay grubu bulunamadi, atlanıyor")
                continue

            r = gecerli[kolon].corr(gecerli[TARGET], method="pearson")
            n = len(gecerli)
            sonuclar.append({"kolon": kolon, "r": r, "n": n, "yontem": yontem})

        sonuc_df = pd.DataFrame(sonuclar).sort_values("r", key=lambda s: s.abs(), ascending=False)
        print(sonuc_df.to_string(index=False))

        dusuk_korelasyonlu = sonuc_df[sonuc_df["r"].abs() < ESIK]["kolon"].tolist()
        print(f"\n  |r| < {ESIK} olan sutunlar ({len(dusuk_korelasyonlu)}): {dusuk_korelasyonlu}")

        if dusuk_korelasyonlu:
            yedek_yol = YEDEK_DIR / f"{yol.stem}_v34_oncesi.csv"
            shutil.copy2(yol, yedek_yol)
            print(f"  Yedek: {yedek_yol}")

            df_guncel = df.drop(columns=dusuk_korelasyonlu)
            df_guncel.to_csv(yol, index=False, encoding="utf-8-sig")
            print(f"  Guncellendi: {yol} ({df_guncel.shape[0]} satir x {df_guncel.shape[1]} sutun)")


if __name__ == "__main__":
    main()
