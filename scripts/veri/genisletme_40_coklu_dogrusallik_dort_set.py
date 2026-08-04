"""
GENIŞLETME AŞAMA 40 — 4 veri setinin (DF-A, DF-B, DF-A-log, DF-B-log)
TAMAMINDA, feature'lar arasi (target HARIC) |Pearson r|>0.9 olan kumeler
bulunur; her kumede target ile EN YUKSEK korelasyona sahip olan sutun
TUTULUR, digerleri SILINIR.

(Korelasyon analizi fazı, proje sahibinin adım-adım talimatıyla,
Görev 35'in 4 sete genelleştirilmiş hali)

OZEL ISTISNA: matematiksel olarak BIREBIR AYNI iki sutun (r=1.0000,
farkli bir ekonomik ilişkiden degil, ayni buyuklugun iki farkli ifade
bicimi oldugundan - orn. yuzde degisim vs log degisim) icin target
korelasyonuna BAKILMAZ, veri setine SONRADAN eklenen sutun silinir:
  DF-B-log: proxy_nominal_aylik_pct (once eklendi, TUTULUR) vs
            proxy_aylik_log_degisim (sonra eklendi, SILINIR)
  (bkz. genisletme_26_forward_fill_gunluk.py -> _proxy_zenginlestirilmis,
  ham["proxy_nominal_aylik_pct"] = ... satiri, ham["proxy_aylik_log_degisim"]
  = ... satirindan ONCE yaziliyor)

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

ESIK = 0.9

SETLER = {
    "DF-A": (DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv", "noter_devir_toplam_adet"),
    "DF-B": (DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv", "noter_devir_toplam_adet"),
    "DF-A-log": (DF_DIR / "df_a_log_degisim_2015_bugun.csv", "noter_devir_toplam_adet_log_degisim"),
    "DF-B-log": (DF_DIR / "df_b_log_degisim_2024_bugun.csv", "noter_devir_toplam_adet_log_degisim"),
}

GUNLUK_DOGRUDAN_ONEKLERI = ["usdtry_orta", "eurtry_orta"]

# matematiksel-ozdes ciftler: (tutulan, silinen) - target korelasyonuna BAKILMAZ
OZDES_CIFTLER = {
    "DF-B-log": [("proxy_nominal_aylik_pct", "proxy_aylik_log_degisim")],
}


def _gunluk_mu(kolon: str) -> bool:
    return any(kolon == onek or kolon.startswith(onek) for onek in GUNLUK_DOGRUDAN_ONEKLERI)


def _aylik_collapse(df: pd.DataFrame, kolon: str) -> pd.DataFrame:
    calisma = df[["tarih", kolon]].copy()
    calisma["_ay_str"] = calisma["tarih"].dt.strftime("%Y-%m")
    aylik = calisma.dropna(subset=[kolon]).drop_duplicates(subset="_ay_str").sort_values("_ay_str").reset_index(drop=True)
    return aylik[["_ay_str", kolon]]


def _target_korelasyonu(df: pd.DataFrame, kolon: str, target_kolon: str, target_aylik: pd.DataFrame) -> float:
    if _gunluk_mu(kolon):
        gecerli = df[[kolon, target_kolon]].dropna()
    else:
        feature_aylik = _aylik_collapse(df, kolon)
        birlesik = feature_aylik.merge(target_aylik, on="_ay_str", how="inner")
        gecerli = birlesik[[kolon, target_kolon]].dropna()
    return gecerli[kolon].corr(gecerli[target_kolon], method="pearson")


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

    for set_adi, (yol, target_kolon) in SETLER.items():
        print(f"\n=== {set_adi} ===")
        df = pd.read_csv(yol, parse_dates=["tarih"])

        sayisal_kolonlar = [c for c in df.columns if c not in ("tarih", target_kolon) and pd.api.types.is_numeric_dtype(df[c])]

        korr = df[sayisal_kolonlar].corr(method="pearson")
        kenarlar = []
        for i, a in enumerate(sayisal_kolonlar):
            for b in sayisal_kolonlar[i + 1:]:
                r = korr.loc[a, b]
                if pd.notna(r) and abs(r) > ESIK:
                    kenarlar.append((a, b))

        kumeler = _baglantili_bilesenler(sayisal_kolonlar, kenarlar)
        print(f"  {len(kumeler)} kume bulundu")

        target_aylik = _aylik_collapse(df, target_kolon)
        ozdes_ciftler_bu_set = OZDES_CIFTLER.get(set_adi, [])

        silinecekler = []
        for kume in kumeler:
            ozel_islendi = False
            for tutulan, silinen in ozdes_ciftler_bu_set:
                if tutulan in kume and silinen in kume and len(kume) == 2:
                    print(f"  KUME (OZDES CIFT): {kume}")
                    print(f"    {tutulan}: TUTULDU (once eklenen)")
                    print(f"    {silinen}: SILINECEK (sonradan eklenen, matematiksel ozdes)")
                    silinecekler.append(silinen)
                    ozel_islendi = True
                    break
            if ozel_islendi:
                continue

            r_degerleri = {k: _target_korelasyonu(df, k, target_kolon, target_aylik) for k in kume}
            tutulan = max(r_degerleri, key=lambda k: abs(r_degerleri[k]))
            print(f"  KUME: {kume}")
            for k in kume:
                durum = "TUTULDU" if k == tutulan else "SILINECEK"
                print(f"    {k}: r_target={r_degerleri[k]:.4f} -> {durum}")
            silinecekler.extend([k for k in kume if k != tutulan])

        print(f"  Toplam silinecek: {len(silinecekler)} -> {silinecekler}")

        if silinecekler:
            yedek_yol = YEDEK_DIR / f"{yol.stem}_v40_oncesi.csv"
            shutil.copy2(yol, yedek_yol)
            df_guncel = df.drop(columns=silinecekler)
            df_guncel.to_csv(yol, index=False, encoding="utf-8-sig")
            print(f"  Yedek: {yedek_yol}")
            print(f"  Guncellendi: {yol} ({df_guncel.shape[0]} satir x {df_guncel.shape[1]} sutun)")


if __name__ == "__main__":
    main()
