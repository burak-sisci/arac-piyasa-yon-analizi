"""
GENIŞLETME AŞAMA 33 — Görev 32'de bulunan kazanan faiz-gecikme (lag)
özelliklerini DF-A ve DF-B'ye YENİ sütun olarak ekler.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla)

Görev 32 sonucu (data/processed/analiz/faiz_gecikme_korelasyon.csv),
HER IKI faiz turu icin AYRI AYRI en yuksek |r| gecikmesi:
  DF-A -> tasit_kredisi_faiz, 6 ay gecikme, Pearson r=0.5446 (n=132)
  DF-A -> politika_faizi,     6 ay gecikme, Pearson r=0.5150 (n=132)
  DF-B -> tasit_kredisi_faiz, 4 ay gecikme, Pearson r=0.2585 (n=26)
  DF-B -> politika_faizi,     5 ay gecikme, Pearson r=0.2253 (n=25)

YÖNTEM: her DataFrame ve her faiz sutunu icin, deger AYLIGA collapse
edilip kendi kazanan gecikmesi kadar shift edilir (deger, N ay SONRAKI
referans aya tasinir - "bugunku faiz, N ay sonrasinin gunlerinde 'N ay
onceki faiz' olarak gorunecek"), sonra takvim gunune (referans_ay
eslemesiyle) geri yayilir - diger mevcut sutunlarla AYNI takvim-ayi
mantigi.

Orijinal tasit_kredisi_faiz VE politika_faizi HICBIR SEKILDE
SILINMEDI/DEGISTIRILMEDI - yalnizca YENI sutunlar EKLENDI.

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

# df_adi -> (dosya_yolu, [(kazanan_sutun, gecikme_ay), ...])
KAZANANLAR = {
    "DF-A": (DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv", [
        ("tasit_kredisi_faiz", 6),
        ("politika_faizi", 6),
    ]),
    "DF-B": (DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv", [
        ("tasit_kredisi_faiz", 4),
        ("politika_faizi", 5),
    ]),
}


def main():
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)

    for df_adi, (yol, kazanan_listesi) in KAZANANLAR.items():
        print(f"\n=== {df_adi} ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])

        yedek_yol = YEDEK_DIR / f"{yol.stem}_v33_oncesi.csv"
        shutil.copy2(yol, yedek_yol)
        print(f"  Yedek: {yedek_yol}")

        for kolon, gecikme in kazanan_listesi:
            aylik = df[["faiz_referans_ay", kolon]].dropna(subset=["faiz_referans_ay"])
            aylik = aylik.drop_duplicates(subset="faiz_referans_ay").sort_values("faiz_referans_ay").reset_index(drop=True)

            yeni_sutun = f"{kolon}_lag{gecikme}ay"
            # aylik[yeni_sutun] su anki satirda, GECIKME ay ONCEKI degeri tasir -
            # bu deger, o ayin gunlerine (referans_ay eslemesiyle) yayilacak.
            aylik[yeni_sutun] = aylik[kolon].shift(gecikme)

            df = df.merge(aylik[["faiz_referans_ay", yeni_sutun]], on="faiz_referans_ay", how="left")

            dolu = df[yeni_sutun].notna().sum()
            print(f"  {kolon}, {gecikme} ay gecikme -> Yeni sutun: {yeni_sutun} | dolu: {dolu}/{len(df)}")

        df.to_csv(yol, index=False, encoding="utf-8-sig")
        print(f"  Guncellendi: {yol} ({df.shape[0]} satir x {df.shape[1]} sutun)")


if __name__ == "__main__":
    main()
