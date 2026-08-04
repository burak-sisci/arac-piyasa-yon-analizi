"""
GENIŞLETME AŞAMA 39 — 4 veri setinin (DF-A, DF-B, DF-A-log, DF-B-log)
TAMAMINDA, target ile |Pearson r|<0.2 olan TUM feature'lari kaldirir.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla,
Görev 34'ün 4 sete genelleştirilmiş hali)

YONTEM:
- usdtry_orta(_log_degisim), eurtry_orta(_log_degisim): GERCEK GUNLUK
  sutunlar, dogrudan gunluk satirlar uzerinden (pairwise dropna)
  hesaplanir.
- Diger TUM sutunlar: takvim ayina collapse edilip (referans_ay
  sutunlari yok ama takvim-ayi hizalama tasarimi geregi her gunun kendi
  ayi = degerin referans ayi) aylik Pearson r hesaplanir.
- |r| < 0.2 olanlar listelenip SILINIR (yedeklenerek).

Girdi/Cikti (yerinde guncellenir, YEDEKLENEREK):
  data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
  data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
  data/processed/dataframes/df_a_log_degisim_2015_bugun.csv
  data/processed/dataframes/df_b_log_degisim_2024_bugun.csv
"""
import shutil
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
YEDEK_DIR = DF_DIR / "yedek"

ESIK = 0.2

# ad -> (dosya_yolu, target_kolonu)
SETLER = {
    "DF-A": (DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv", "noter_devir_toplam_adet"),
    "DF-B": (DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv", "noter_devir_toplam_adet"),
    "DF-A-log": (DF_DIR / "df_a_log_degisim_2015_bugun.csv", "noter_devir_toplam_adet_log_degisim"),
    "DF-B-log": (DF_DIR / "df_b_log_degisim_2024_bugun.csv", "noter_devir_toplam_adet_log_degisim"),
}

GUNLUK_DOGRUDAN_ONEKLERI = ["usdtry_orta", "eurtry_orta"]


def _gunluk_mu(kolon: str) -> bool:
    return any(kolon == onek or kolon.startswith(onek) for onek in GUNLUK_DOGRUDAN_ONEKLERI)


def _aylik_collapse(df: pd.DataFrame, kolon: str) -> pd.DataFrame:
    calisma = df[["tarih", kolon]].copy()
    calisma["_ay_str"] = calisma["tarih"].dt.strftime("%Y-%m")
    aylik = calisma.dropna(subset=[kolon]).drop_duplicates(subset="_ay_str").sort_values("_ay_str").reset_index(drop=True)
    return aylik[["_ay_str", kolon]]


def main():
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)

    for set_adi, (yol, target_kolon) in SETLER.items():
        print(f"\n=== {set_adi} ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])
        df = df.sort_values("tarih").reset_index(drop=True)

        sayisal_kolonlar = [
            c for c in df.columns
            if c not in ("tarih", target_kolon) and pd.api.types.is_numeric_dtype(df[c])
        ]

        target_aylik = _aylik_collapse(df, target_kolon)

        sonuclar = []
        for kolon in sayisal_kolonlar:
            if _gunluk_mu(kolon):
                gecerli = df[[kolon, target_kolon]].dropna()
            else:
                feature_aylik = _aylik_collapse(df, kolon)
                birlesik = feature_aylik.merge(target_aylik, on="_ay_str", how="inner")
                gecerli = birlesik[[kolon, target_kolon]].dropna()
            r = gecerli[kolon].corr(gecerli[target_kolon], method="pearson")
            n = len(gecerli)
            sonuclar.append({"kolon": kolon, "r": r, "n": n})

        sonuc_df = pd.DataFrame(sonuclar).sort_values("r", key=lambda s: s.abs(), ascending=False)
        print(sonuc_df.to_string(index=False))

        dusuk = sonuc_df[sonuc_df["r"].abs() < ESIK]["kolon"].tolist()
        print(f"\n  |r| < {ESIK} olan sutunlar ({len(dusuk)}): {dusuk}")

        if dusuk:
            yedek_yol = YEDEK_DIR / f"{yol.stem}_v39_oncesi.csv"
            shutil.copy2(yol, yedek_yol)
            df_guncel = df.drop(columns=dusuk)
            df_guncel.to_csv(yol, index=False, encoding="utf-8-sig")
            print(f"  Yedek: {yedek_yol}")
            print(f"  Guncellendi: {yol} ({df_guncel.shape[0]} satir x {df_guncel.shape[1]} sutun)")


if __name__ == "__main__":
    main()
