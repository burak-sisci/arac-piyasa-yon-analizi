"""
GENIŞLETME AŞAMA 38 — Faiz gecikme (lag) korelasyonunu 4 veri setinin
TAMAMINDA (DF-A, DF-B, DF-A-log, DF-B-log) calistirir; her sette, her
faiz sutunu icin EN YUKSEK |r| veren gecikmeyi YENI sutun olarak ekler.
Orijinal faiz sutunlari SILINMEZ.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla)

FARK (onceki Gorev 31-33'e gore):
- DF-A / DF-A-log: gecikme araligi 1-12 AY (genis pencere, n yeterli).
- DF-B / DF-B-log: gecikme araligi 1-6 AY (dar pencere, n kisitli).
- Orijinal faiz sutunlari HICBIR ZAMAN silinmiyor - yalnizca kazanan
  gecikme YENI bir sutun olarak ekleniyor.
- DF-A/DF-B (ham seviye) VE DF-A-log/DF-B-log (log-degisim) AYRI AYRI
  calistiriliyor - hangisinin daha guvenilir sonuc verdigi karsilastirma
  icin.

YONTEM: her faiz sutunu ve target, kendi takvim ayina COLLAPSE edilip
(df['tarih'].dt.strftime('%Y-%m')), belirtilen gecikme araliginin HER
degeri icin faiz serisi o kadar ay GERIYE kaydirilip target ile Pearson
korelasyonu hesaplanir. En yuksek |r| veren gecikme, YENI bir sutun
olarak (takvim gunune geri yayilarak) eklenir.

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

# ad -> (dosya_yolu, target_kolonu, faiz_kolonlari, gecikme_araligi)
SETLER = {
    "DF-A": (DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
             "noter_devir_toplam_adet", ["tasit_kredisi_faiz", "politika_faizi"], range(1, 13)),
    "DF-B": (DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
             "noter_devir_toplam_adet", ["tasit_kredisi_faiz", "politika_faizi"], range(1, 7)),
    "DF-A-log": (DF_DIR / "df_a_log_degisim_2015_bugun.csv",
                 "noter_devir_toplam_adet_log_degisim",
                 ["tasit_kredisi_faiz_log_degisim", "politika_faizi_log_degisim"], range(1, 13)),
    "DF-B-log": (DF_DIR / "df_b_log_degisim_2024_bugun.csv",
                 "noter_devir_toplam_adet_log_degisim",
                 ["tasit_kredisi_faiz_log_degisim", "politika_faizi_log_degisim"], range(1, 7)),
}


def _aylik_collapse(df: pd.DataFrame, kolon: str) -> pd.DataFrame:
    calisma = df[["tarih", kolon]].copy()
    calisma["_ay_str"] = calisma["tarih"].dt.strftime("%Y-%m")
    aylik = calisma.dropna(subset=[kolon]).drop_duplicates(subset="_ay_str").sort_values("_ay_str").reset_index(drop=True)
    return aylik[["_ay_str", kolon]]


def main():
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)

    for set_adi, (yol, target_kolon, faiz_kolonlari, gecikmeler) in SETLER.items():
        print(f"\n=== {set_adi} (gecikme araligi: {gecikmeler.start}-{gecikmeler.stop - 1} ay) ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])
        df = df.sort_values("tarih").reset_index(drop=True)

        target_aylik = _aylik_collapse(df, target_kolon)
        yeni_sutunlar = {}

        for faiz_kolon in faiz_kolonlari:
            faiz_aylik = _aylik_collapse(df, faiz_kolon)

            en_iyi_r, en_iyi_gecikme, en_iyi_n = None, None, None
            for gecikme in gecikmeler:
                kaydirilmis = faiz_aylik.copy()
                kaydirilmis[faiz_kolon] = kaydirilmis[faiz_kolon].shift(gecikme)
                birlesik = kaydirilmis.merge(target_aylik, on="_ay_str", how="inner")
                gecerli = birlesik[[faiz_kolon, target_kolon]].dropna()
                if len(gecerli) < 5:
                    continue
                r = gecerli[faiz_kolon].corr(gecerli[target_kolon], method="pearson")
                if en_iyi_r is None or abs(r) > abs(en_iyi_r):
                    en_iyi_r, en_iyi_gecikme, en_iyi_n = r, gecikme, len(gecerli)

            print(f"  {faiz_kolon}: en iyi gecikme={en_iyi_gecikme} ay | r={en_iyi_r:.4f} | n={en_iyi_n}")

            kazanan_aylik = faiz_aylik.copy()
            kazanan_aylik[f"{faiz_kolon}_lag{en_iyi_gecikme}ay"] = kazanan_aylik[faiz_kolon].shift(en_iyi_gecikme)
            yeni_sutunlar[faiz_kolon] = (en_iyi_gecikme, kazanan_aylik[["_ay_str", f"{faiz_kolon}_lag{en_iyi_gecikme}ay"]])

        yedek_yol = YEDEK_DIR / f"{yol.stem}_v38_oncesi.csv"
        shutil.copy2(yol, yedek_yol)

        df["_ay_str"] = df["tarih"].dt.strftime("%Y-%m")
        for faiz_kolon, (gecikme, aylik_veri) in yeni_sutunlar.items():
            df = df.merge(aylik_veri, on="_ay_str", how="left")
        df = df.drop(columns=["_ay_str"])

        df.to_csv(yol, index=False, encoding="utf-8-sig")
        print(f"  Yedek: {yedek_yol}")
        print(f"  Guncellendi: {yol} ({df.shape[0]} satir x {df.shape[1]} sutun)")


if __name__ == "__main__":
    main()
