"""
GENIŞLETME AŞAMA 6 — Hedef etiket üretimi (nominal + reel + tercile),
2024-01 -> 2026-06.

MVP scriptinin (asama5_temizle_etiketle.py) aynı oynaklık-uyarlamalı k*sigma
bandı + tercile mantığı, genişletilmiş (birleşik) tabloya uygulanır.

TEK METODOLOJİK FARK: sigma, MVP'nin yalnızca 9 geçerli geçişi yerine burada
25 geçerli geçişten (30 ay, 2 BETAM boşluğuna bağlı 4 NaN geçiş hariç)
hesaplanır — çok daha güvenilir bir tahmin. k SABİT (0.5) bırakıldı, MVP ile
metodolojik tutarlılık (karşılaştırılabilirlik) korunmuş oldu.

KRİTİK BULGU (PM onayıyla kaydedildi): Nominal ve reel etiketler ZIT yönde
skewed — nominal seri neredeyse hep "up" (TL değer kaybı/enflasyon nedeniyle
ham fiyat sürekli artıyor), reel seri ise neredeyse hep "down" (enflasyondan
arındırılınca piyasa aslında geriliyor). Bu, N1/K8'de zaten işaretlenen
"ilan fiyatı ham göstergedir" sınırının somut bir tezahürüdür; iki etiket
farklı sorulara cevap verir (TL bazlı yön vs. reel piyasa yönü).

Girdi: data/processed/genisletme/veri_2024_bugun_birlesik.csv (Aşama 5
çıktısı, zaten tüm kaynakları birleştirmiş).
Çıktı: data/processed/genisletme/veri_2024_bugun_etiketli.csv/.xlsx
"""
from pathlib import Path

import numpy as np
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
PROCESSED_DIR = REPO_KOKU / "data" / "processed" / "genisletme"

ESIK_K = 0.5
TERCILE_SAYISI = 3


def _log_degisim(seri: pd.Series) -> pd.Series:
    """ln(x_t / x_{t-1}); x veya x_{t-1} NaN ise sonuc NaN (dogal pandas davranisi)."""
    return np.log(seri / seri.shift(1))


def _oynaklik_bandi_etiket(log_degisim: pd.Series, k: float) -> tuple[pd.Series, float]:
    sigma = log_degisim.std(ddof=1)  # yalnizca gecerli (NaN olmayan) gozlemler uzerinden
    esik = k * sigma

    def etiketle(x):
        if pd.isna(x):
            return "eksik"
        if x >= esik:
            return "up"
        if x <= -esik:
            return "down"
        return "stable"

    return log_degisim.map(etiketle), sigma


def _tercile_etiket(log_degisim: pd.Series, n: int) -> pd.Series:
    gecerli = log_degisim.dropna()
    if len(gecerli) < n:
        return pd.Series("eksik", index=log_degisim.index)
    dilimler = pd.qcut(gecerli, n, labels=["down", "stable", "up"], duplicates="drop")
    sonuc = pd.Series("eksik", index=log_degisim.index, dtype=object)
    sonuc.loc[dilimler.index] = dilimler.astype(str)
    return sonuc


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    girdi_csv = PROCESSED_DIR / "veri_2018_bugun_birlesik.csv"
    birlesik = pd.read_csv(girdi_csv).sort_values("referans_ayi").reset_index(drop=True)

    # --- aylik nominal/reel % degisim - yerelde, ayni yontemle hesaplanir ---
    birlesik["proxy_nominal_aylik_pct"] = birlesik["proxy_fiyat_cari_tl"].pct_change() * 100
    birlesik["proxy_reel_gosterge"] = birlesik["proxy_fiyat_cari_tl"] / birlesik["tufe_endeks"]
    birlesik["proxy_reel_aylik_pct"] = birlesik["proxy_reel_gosterge"].pct_change() * 100

    # --- hedef degisken (log-degisim + oynaklik-uyarlamali bant + tercile) ---
    birlesik["proxy_aylik_log_degisim"] = _log_degisim(birlesik["proxy_fiyat_cari_tl"])
    birlesik["proxy_reel_aylik_log_degisim"] = _log_degisim(birlesik["proxy_reel_gosterge"])

    birlesik["proxy_yon_nominal"], sigma_nominal = _oynaklik_bandi_etiket(
        birlesik["proxy_aylik_log_degisim"], ESIK_K
    )
    birlesik["proxy_yon_reel"], sigma_reel = _oynaklik_bandi_etiket(
        birlesik["proxy_reel_aylik_log_degisim"], ESIK_K
    )
    birlesik["proxy_yon_tercile"] = _tercile_etiket(
        birlesik["proxy_aylik_log_degisim"], TERCILE_SAYISI
    )
    birlesik["kullanilan_esik_k"] = ESIK_K
    birlesik["kullanilan_sigma_nominal"] = sigma_nominal
    birlesik["kullanilan_sigma_reel"] = sigma_reel

    birlesik = birlesik.drop(columns=["proxy_reel_gosterge"])

    csv_yolu = PROCESSED_DIR / "veri_2018_bugun_etiketli.csv"
    xlsx_yolu = PROCESSED_DIR / "veri_2018_bugun_etiketli.xlsx"
    birlesik.to_csv(csv_yolu, index=False, encoding="utf-8-sig")
    birlesik.to_excel(xlsx_yolu, index=False, sheet_name="veri_2018_bugun_etiketli")

    gecerli_gecis = birlesik["proxy_aylik_log_degisim"].notna().sum()
    olasi_gecis = len(birlesik) - 1
    print("=== GENISLETME 6 - HEDEF ETIKET OZETI ===")
    print(f"Satir sayisi: {len(birlesik)}")
    print(f"Gecerli (NaN olmayan) aylik log-degisim gecisi sayisi: {gecerli_gecis} / {olasi_gecis} olasi gecis")
    print(f"Kullanilan esik: k={ESIK_K}")
    print(f"sigma (nominal log-degisim, gecerli gozlemler uzerinden): {sigma_nominal:.5f}")
    print(f"sigma (reel log-degisim, gecerli gozlemler uzerinden): {sigma_reel:.5f}")
    print()
    print("--- Sinif dagilimi: proxy_yon_nominal ---")
    print(birlesik["proxy_yon_nominal"].value_counts().to_string())
    print()
    print("--- Sinif dagilimi: proxy_yon_reel ---")
    print(birlesik["proxy_yon_reel"].value_counts().to_string())
    print()
    print("--- Sinif dagilimi: proxy_yon_tercile ---")
    print(birlesik["proxy_yon_tercile"].value_counts().to_string())
    print()
    print("--- Tablo (kilit sutunlar) ---")
    print(birlesik[["referans_ayi", "proxy_fiyat_cari_tl", "proxy_aylik_log_degisim",
                     "proxy_yon_nominal", "proxy_yon_reel", "proxy_yon_tercile"]].to_string(index=False))
    print()
    print(f"Cikti: {csv_yolu} , {xlsx_yolu}")


if __name__ == "__main__":
    main()
