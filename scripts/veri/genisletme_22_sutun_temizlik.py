"""
GENIŞLETME AŞAMA 22 — DF-A/DF-B sütun temizliği, "eksik" metin düzeltmesi,
proxy sütunları raporu ve korelasyon-uygunluk taraması.

(prompts/22_sutun_temizlik_ve_korelasyon_kontrol_prompt.md)

Bu script SADECE silme + metin düzeltmesi yapar (Görev 1-2); Görev 3-4
(proxy raporu, korelasyon uygunluk taraması) ayrıca bu script tarafından
konsol çıktısına yazdırılır ama DataFrame'lere hiçbir değişiklik yapmaz -
yalnızca rapor amaçlı.

SIRALAMA (önemli): Görev 2 ("eksik" -> NaN düzeltmesi) Görev 1'in (sütun
silme) HEMEN ÖNCESİNDE, aynı DataFrame üzerinde uygulanır - proxy_kaynak
ve proxy_yon_* sütunları düzeltildikten SONRA silinir (düzeltme, silinecek
olsa bile audit/yedek amaçlı ayrı bir adım olarak uygulanıp sayılır).
"""
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DATAFRAMES_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
YEDEK_DIR = DATAFRAMES_DIR / "yedek"

DF_A_CSV = DATAFRAMES_DIR / "df_a_kapsama_testli_v2.csv"
DF_A_XLSX = DATAFRAMES_DIR / "df_a_kapsama_testli_v2.xlsx"
DF_B_CSV = DATAFRAMES_DIR / "df_b_zengin_2024_bugun_v2.csv"
DF_B_XLSX = DATAFRAMES_DIR / "df_b_zengin_2024_bugun_v2.xlsx"

SILINECEK_SUTUNLAR = [
    "otv_aciklama",
    "proxy_yayim_ayi",
    "proxy_kaynak",
    "proxy_fiyat_arabamcom_referans_tl",
    "proxy_yon_nominal",
    "proxy_yon_reel",
    "proxy_yon_tercile",
    "kullanilan_esik_k",
    "enag_tufe_fark_yillik",
    "enag_kaynak_seviyesi",
    "enag_kaynak_url",
]


def _eksik_metni_duzelt(df: pd.DataFrame, ad: str) -> dict:
    """'eksik' icerigi tasiyan HER hucreyi (herhangi bir sutunda) NaN yapar.
    Doner: {sutun: duzeltilen_hucre_sayisi}."""
    duzeltmeler = {}
    for c in df.columns:
        try:
            mask = df[c].astype(str).str.contains("eksik", case=False, na=False)
        except Exception:
            continue
        n = int(mask.sum())
        if n > 0:
            df.loc[mask, c] = np.nan
            duzeltmeler[c] = n
    return duzeltmeler


def main():
    YEDEK_DIR.mkdir(parents=True, exist_ok=True)
    zaman_damgasi = "20260803_v22"  # tarih damgasi (Date.now yerine sabit - deterministik yeniden calisma icin)

    df_a = pd.read_csv(DF_A_CSV)
    df_b = pd.read_csv(DF_B_CSV)

    # --- YEDEK (Gorev 0'in baglayici ilkesi: silmeden once) ---
    yedek_a_csv = YEDEK_DIR / f"df_a_kapsama_testli_v2_{zaman_damgasi}.csv"
    yedek_b_csv = YEDEK_DIR / f"df_b_zengin_2024_bugun_v2_{zaman_damgasi}.csv"
    df_a.to_csv(yedek_a_csv, index=False, encoding="utf-8-sig")
    df_b.to_csv(yedek_b_csv, index=False, encoding="utf-8-sig")

    # --- GOREV 2: 'eksik' metin duzeltmesi (silmeden ONCE, ayni DataFrame'de) ---
    duzeltme_a = _eksik_metni_duzelt(df_a, "DF-A")
    duzeltme_b = _eksik_metni_duzelt(df_b, "DF-B")

    # --- GOREV 1: sutun silme (her iki DataFrame'de, mevcut olanlar) ---
    silinen_a = [c for c in SILINECEK_SUTUNLAR if c in df_a.columns]
    silinen_b = [c for c in SILINECEK_SUTUNLAR if c in df_b.columns]
    bulunamayan = [c for c in SILINECEK_SUTUNLAR if c not in df_a.columns and c not in df_b.columns]

    df_a_yeni = df_a.drop(columns=silinen_a)
    df_b_yeni = df_b.drop(columns=silinen_b)

    df_a_yeni.to_csv(DF_A_CSV, index=False, encoding="utf-8-sig")
    df_a_yeni.to_excel(DF_A_XLSX, index=False, sheet_name="df_a_v2")
    df_b_yeni.to_csv(DF_B_CSV, index=False, encoding="utf-8-sig")
    df_b_yeni.to_excel(DF_B_XLSX, index=False, sheet_name="df_b_v2")

    print("=== GENISLETME 22 - SUTUN TEMIZLIGI OZETI ===")
    print(f"\nYedekler: {yedek_a_csv} , {yedek_b_csv}")

    print(f"\n--- GOREV 1: Sutun silme ---")
    for c in SILINECEK_SUTUNLAR:
        yer = []
        if c in silinen_a:
            yer.append("DF-A")
        if c in silinen_b:
            yer.append("DF-B")
        if yer:
            print(f"  {c}: silindi ({', '.join(yer)})")
        else:
            print(f"  {c}: bulunamadi, atlandi")

    print(f"\n--- GOREV 2: 'eksik' metin duzeltmesi ---")
    print(f"  DF-A: {duzeltme_a if duzeltme_a else '(hic yok)'}")
    print(f"  DF-B: {duzeltme_b if duzeltme_b else '(hic yok)'}")

    print(f"\nDF-A yeni boyut: {df_a_yeni.shape[0]} satir x {df_a_yeni.shape[1]} sutun")
    print(f"DF-B yeni boyut: {df_b_yeni.shape[0]} satir x {df_b_yeni.shape[1]} sutun")

    # --- GOREV 3: 3 proxy sutunu detayli rapor (DF-B uzerinden, silme SONRASI ---
    print(f"\n--- GOREV 3: Proxy sutunlari detayli rapor (DF-B, {len(df_b_yeni)} satir) ---")
    for sutun in ["proxy_dom_gun", "proxy_satis_orani_pct", "proxy_fiyat_cari_tl"]:
        seri = df_b_yeni[sutun]
        n = len(seri)
        dolu = seri.notna().sum()
        bos_aylar = df_b_yeni.loc[seri.isna(), "referans_ayi"].tolist()
        print(f"\n  ## {sutun}")
        print(f"  Toplam={n}, dolu={dolu}, bos={n-dolu}, doluluk=%{dolu/n*100:.1f}")
        print(f"  Bos aylar: {bos_aylar}")
        gecerli = seri.dropna()
        print(f"  Ortalama={gecerli.mean():.4f}, min={gecerli.min():.4f}, max={gecerli.max():.4f}, "
              f"std={gecerli.std():.4f}")
        pct_degisim = gecerli.pct_change().abs().mean() * 100
        print(f"  Ortalama mutlak aylik yuzde degisim (yalniz gecerli geciler): %{pct_degisim:.2f}")
        for bos_ay in bos_aylar:
            idx = df_b_yeni.index[df_b_yeni["referans_ayi"] == bos_ay][0]
            onceki = df_b_yeni.loc[idx - 1, [ "referans_ayi", sutun]].to_dict() if idx > 0 else None
            sonraki = df_b_yeni.loc[idx + 1, ["referans_ayi", sutun]].to_dict() if idx < len(df_b_yeni) - 1 else None
            print(f"    {bos_ay}: onceki={onceki}, sonraki={sonraki}")

    # --- GOREV 4: korelasyon uygunluk taramasi (POST-silme DataFrame'lerde) ---
    print(f"\n--- GOREV 4: Korelasyon uygunluk taramasi ---")
    for ad, df in [("DF-A", df_a_yeni), ("DF-B", df_b_yeni)]:
        print(f"\n  == {ad} ({df.shape[0]} satir x {df.shape[1]} sutun) ==")
        for c in df.columns:
            n = len(df)
            eksik = df[c].isna().sum()
            eksik_oran = eksik / n * 100
            if c == "referans_ayi":
                print(f"    [c] {c}: tarih/zaman damgasi - korelasyona sokulmamali ama zaman-serisi indeksi icin gerekli")
                continue
            if not pd.api.types.is_numeric_dtype(df[c]):
                print(f"    [b] {c}: metin/kategorik/tarih, dtype={df[c].dtype}, korelasyona dogrudan sokulamaz")
                continue
            gecerli = df[c].dropna()
            if len(gecerli) > 1:
                std = gecerli.std()
                ortalama = gecerli.mean()
                cv = (std / abs(ortalama)) if ortalama != 0 else np.nan
                if std == 0 or (not np.isnan(cv) and abs(cv) < 0.0001):
                    print(f"    [a] {c}: sabit/neredeyse-degismeyen (std={std:.6g}, ortalama={ortalama:.6g})")
            if eksik_oran >= 70:
                print(f"    [d] {c}: asiri yuksek bos oran (%{eksik_oran:.1f}, {eksik}/{n})")


if __name__ == "__main__":
    main()
