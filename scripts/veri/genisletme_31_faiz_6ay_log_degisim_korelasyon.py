"""
GENIŞLETME AŞAMA 31 — Faiz sütunlarının 6 aylık log-değişiminin target
(noter_devir_toplam_adet, ham seviye) ile korelasyonu; en yüksek olan
sütun DF-A ve DF-B'de tutulur, diğeri silinir.

(Korelasyon analizi fazi, proje sahibinin adim-adim talimatiyla)

YONTEM:
- Kaynak tablo (DF-A veya DF-B) takvim-ayi bazli genisletilmis (her ay
  kendi gunlerine kopyalanmis) - pseudo-replikasyon riskinden kacinmak
  icin ONCE AYLIGA COLLAPSE edilir (her faiz_referans_ay / noter_referans_ay
  icin tek satir).
- tasit_kredisi_faiz ve politika_faizi icin 6 AYLIK log-degisim hesaplanir:
  ln(x_t / x_{t-6}) (aylik seride 6 satir geriye kaydirma).
- Target (noter_devir_toplam_adet) HAM SEVIYE olarak kullanilir (proje
  sahibinin acik tercihi).
- Iki faiz sutununun 6-aylik log-degisimi, target ile PEARSON korelasyonu
  ile ayri ayri olculur (mutlak deger buyuklugune gore karsilastirilir).
- Kazanan sutun (yuksek |r|) veri setinde KALIR, kaybeden SILINIR (yedek
  alinarak).

Girdi: data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
       data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
Cikti: ayni dosyalar (kaybeden faiz sutunu cikarilmis halde, YEDEKLENEREK)
"""
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
YEDEK_DIR = DF_DIR / "yedek"

DOSYALAR = {
    "DF-A": DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
    "DF-B": DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
}

FAIZ_SUTUNLARI = ["tasit_kredisi_faiz", "politika_faizi"]
TARGET = "noter_devir_toplam_adet"


def _aylik_collapse(df: pd.DataFrame, referans_ay_col: str, deger_kolonlari: list) -> pd.DataFrame:
    """Takvim-genisletilmis tabloyu, verilen referans_ay sutununa gore
    tek-satir-bir-ay haline indirger (pseudo-replikasyondan kacinmak icin)."""
    aylik = df[[referans_ay_col] + deger_kolonlari].dropna(subset=[referans_ay_col])
    aylik = aylik.drop_duplicates(subset=referans_ay_col).sort_values(referans_ay_col).reset_index(drop=True)
    return aylik


def _6ay_log_degisim(seri: pd.Series) -> pd.Series:
    return np.log(seri / seri.shift(6))


def main():
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)

    for df_adi, yol in DOSYALAR.items():
        print(f"\n=== {df_adi} ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])

        faiz_aylik = _aylik_collapse(df, "faiz_referans_ay", FAIZ_SUTUNLARI)
        for kolon in FAIZ_SUTUNLARI:
            faiz_aylik[f"{kolon}_6ay_log_degisim"] = _6ay_log_degisim(faiz_aylik[kolon])

        target_aylik = _aylik_collapse(df, "noter_referans_ay", [TARGET])

        birlesik = faiz_aylik.merge(
            target_aylik, left_on="faiz_referans_ay", right_on="noter_referans_ay", how="inner"
        )

        sonuclar = {}
        for kolon in FAIZ_SUTUNLARI:
            degisim_col = f"{kolon}_6ay_log_degisim"
            gecerli = birlesik[[degisim_col, TARGET]].dropna()
            r = gecerli[degisim_col].corr(gecerli[TARGET], method="pearson")
            sonuclar[kolon] = {"r": r, "n": len(gecerli)}
            print(f"  {kolon} (6 aylik log-degisim) vs {TARGET} (ham seviye): "
                  f"Pearson r={r:.4f} (n={len(gecerli)})")

        kazanan = max(sonuclar, key=lambda k: abs(sonuclar[k]["r"]))
        kaybeden = [k for k in FAIZ_SUTUNLARI if k != kazanan][0]
        print(f"  -> KAZANAN: {kazanan} (|r|={abs(sonuclar[kazanan]['r']):.4f}) - VERI SETINDE KALACAK")
        print(f"  -> KAYBEDEN: {kaybeden} (|r|={abs(sonuclar[kaybeden]['r']):.4f}) - SILINECEK")

        yedek_yol = YEDEK_DIR / f"{yol.stem}_v31_oncesi.csv"
        shutil.copy2(yol, yedek_yol)
        print(f"  Yedek: {yedek_yol}")

        df_guncel = df.drop(columns=[kaybeden])
        df_guncel.to_csv(yol, index=False, encoding="utf-8-sig")
        print(f"  Guncellendi: {yol} ({df_guncel.shape[0]} satir x {df_guncel.shape[1]} sutun)")


if __name__ == "__main__":
    main()
