"""
GENIŞLETME AŞAMA 35 — Feature'lar arasi (target HARIC) |Pearson r|>0.9
olan kumeler bulunur; her kumede target ile EN YUKSEK korelasyona sahip
olan sutun TUTULUR, digerleri SILINIR.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla)

YÖNTEM:
1. Mevcut sayisal feature'lar (tarih, target, referans_ay sutunlari
   haric) uzerinde standart Pearson korelasyon matrisi hesaplanir
   (df[features].corr()) - Gorev 35'teki (multicollinearity raporu)
   ile AYNI matris.
2. |r|>0.9 olan kenarlardan bir graf kurulur; BAGLI BILESENLER
   (connected components) "kume" olarak alinir - yalnizca ikili
   ciftler degil, ZINCIRLEME baglantili tum sutunlar TEK kume sayilir
   (ör. usdtry_alis-usdtry_satis-eurtry_alis-tufe_endeks hepsi tek kume).
3. Her feature'in target (noter_devir_toplam_adet) ile Pearson r'si,
   Gorev 34 ile AYNI metodolojiyle (referans_ay'i olan sutunlar aya
   collapse edilip target'in kendi aylik collapse'iyle birlestirilir;
   referans_ay'i olmayan gunluk/takvim sutunlari dogrudan gunluk
   satirlar uzerinden) hesaplanir.
4. Boyutu >1 olan her kumede, |r_target| EN YUKSEK olan sutun TUTULUR,
   digerleri SILINIR (yedeklenerek).

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
ESIK = 0.9

DOSYALAR = {
    "DF-A": DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv",
    "DF-B": DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv",
}

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


def _target_korelasyonu(df: pd.DataFrame, kolon: str, target_aylik: pd.DataFrame) -> float:
    referans_ay = _referans_ay_bul(kolon)
    if referans_ay is not None:
        feature_aylik = _aylik_collapse(df, referans_ay, kolon)
        birlesik = feature_aylik.merge(
            target_aylik, left_on=referans_ay, right_on=TARGET_REFERANS_AY, how="inner"
        )
        gecerli = birlesik[[kolon, TARGET]].dropna()
    else:
        gecerli = df[[kolon, TARGET]].dropna()
    return gecerli[kolon].corr(gecerli[TARGET], method="pearson")


def _baglantili_bilesenler(dugumler, kenarlar):
    ebeveyn = {d: d for d in dugumler}

    def bul(x):
        while ebeveyn[x] != x:
            ebeveyn[x] = ebeveyn[ebeveyn[x]]
            x = ebeveyn[x]
        return x

    def birlestir(x, y):
        rx, ry = bul(x), bul(y)
        if rx != ry:
            ebeveyn[rx] = ry

    for a, b in kenarlar:
        birlestir(a, b)

    kumeler = {}
    for d in dugumler:
        kok = bul(d)
        kumeler.setdefault(kok, []).append(d)
    return [uyeler for uyeler in kumeler.values() if len(uyeler) > 1]


def main():
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)

    for df_adi, yol in DOSYALAR.items():
        print(f"\n=== {df_adi} ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])

        referans_ay_kolonlari = [c for c in df.columns if c.endswith("_referans_ay")]
        haric = {"tarih", TARGET} | set(referans_ay_kolonlari)
        sayisal_kolonlar = [c for c in df.columns if c not in haric and pd.api.types.is_numeric_dtype(df[c])]

        korr = df[sayisal_kolonlar].corr(method="pearson")
        kenarlar = []
        for i, a in enumerate(sayisal_kolonlar):
            for b in sayisal_kolonlar[i + 1:]:
                r = korr.loc[a, b]
                if pd.notna(r) and abs(r) > ESIK:
                    kenarlar.append((a, b))

        kumeler = _baglantili_bilesenler(sayisal_kolonlar, kenarlar)
        print(f"  {len(kumeler)} kume bulundu (boyutu >1)")

        target_aylik = _aylik_collapse(df, TARGET_REFERANS_AY, TARGET)
        r_target_cache = {}

        def r_target(kolon):
            if kolon not in r_target_cache:
                r_target_cache[kolon] = _target_korelasyonu(df, kolon, target_aylik)
            return r_target_cache[kolon]

        silinecekler = []
        for kume in kumeler:
            r_degerleri = {k: r_target(k) for k in kume}
            tutulan = max(r_degerleri, key=lambda k: abs(r_degerleri[k]))
            print(f"  KUME: {kume}")
            for k in kume:
                durum = "TUTULDU" if k == tutulan else "SILINECEK"
                print(f"    {k}: r_target={r_degerleri[k]:.4f}  -> {durum}")
            silinecekler.extend([k for k in kume if k != tutulan])

        print(f"\n  Toplam silinecek: {len(silinecekler)} -> {silinecekler}")

        if silinecekler:
            yedek_yol = YEDEK_DIR / f"{yol.stem}_v35_coklu_dogrusallik_oncesi.csv"
            shutil.copy2(yol, yedek_yol)
            print(f"  Yedek: {yedek_yol}")

            df_guncel = df.drop(columns=silinecekler)
            df_guncel.to_csv(yol, index=False, encoding="utf-8-sig")
            print(f"  Guncellendi: {yol} ({df_guncel.shape[0]} satir x {df_guncel.shape[1]} sutun)")


if __name__ == "__main__":
    main()
