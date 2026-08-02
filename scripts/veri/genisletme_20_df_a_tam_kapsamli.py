"""
GENIŞLETME AŞAMA 20 — DF-A'nın "tam kapsamlı" (2015-01'den itibaren kaynağı
kesintisiz olan) alt kümesi.

Kullanıcı talebi: DF-A'dan (2015-01 -> bugün, 46 sütun), kaynağı GERÇEKTEN
2015'ten SONRA başlayan tüm sütunları çıkarmak — sonuçta "BETAM/ENAG/alım
gücü içeren" (DF-A, DF-B) ile "bunları hiç içermeyen, 2015'ten beri tam"
(bu script'in çıktısı) arasında net bir ikilik oluşuyor.

KAPSAM KARARI (kullanıcıyla netleştirildi, bkz. oturum): "Kaynağı geç
başlayan" ile "kaynağı 2015'ten beri var ama TÜREV/HESAPLAMA ya da TASARIM
gereği ilk birkaç satırı boş olan" ayrıştırıldı — yalnızca İLKİ çıkarılıyor:

ÇIKARILAN (kaynağı gerçekten 2018 veya 2024'te başlıyor):
- proxy_* grubu (BETAM sahibindex, ilk dolu 2024-01/2024-02) - 10 sütun
- proxy_yon_nominal/reel/tercile + kullanilan_esik_k/sigma_nominal/sigma_reel
  (BETAM'a tamamen bağımlı hedef etiket/parametre sütunları - teknik olarak
  2015-01'den itibaren "eksik" metni/sabit sayıyla dolu göründükleri için
  NaN sayılmıyorlar, ama proxy_fiyat_cari_tl olmadan anlamsızlar, kullanıcı
  onayıyla bunlar da çıkarıldı) - 6 sütun
- enag_* grubu (ilk dolu 2024-01) - 5 sütun
- noter_devir_otomobil_adet, brut_ucret_maas_endeksi_2021_100,
  alim_gucu_ceyrek, erisim_endeksi (2015-2017 erişim engeli, ilk dolu
  2018-01) - 4 sütun

KALAN (kaynağı 2015-01'den itibaren kesintisiz VEYA yalnızca hesaplama/
tasarım gereği ilk birkaç satırı boş - kaynak sorunu değil, bkz. görüşme):
- tufe_aylik_degisim (ilk dolu 2015-02, 1 ay - önceki aya ihtiyaç duyar)
- tufe_yillik_degisim (ilk dolu 2016-01, 12 ay - yıllık karşılaştırma icin
  12 ay geriye bakar)
- otv_aciklama (ilk dolu 2016-11 - yalnızca ÖTV olayı olan ayda dolu,
  tasarım gereği, kaynak kesintisi değil)
- tüm diğer sütunlar (kur, TÜFE seviyesi, faiz, ODMD, ÖTV bayrak/ay-farkı,
  OSD, tüketici güveni, noter devir toplam)

DOSYA STRATEJISI: mevcut df_a_genis_2015_bugun.csv (46 sütun, BETAM/ENAG
dahil) DOKUNULMADI - bu script AYRI bir yeni dosya üretir.
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DATAFRAMES_DIR = REPO_KOKU / "data" / "processed" / "dataframes"

DF_A_YOLU = DATAFRAMES_DIR / "df_a_genis_2015_bugun.csv"

# Kaynağı gerçekten 2015-01'den sonra başlayan (kaynak boşluğu) sütunlar.
CIKARILACAK_SUTUNLAR = [
    # proxy fiyat / BETAM (ilk dolu 2024-01/02)
    "proxy_dom_gun", "proxy_satis_orani_pct", "proxy_yayim_ayi",
    "proxy_fiyat_cari_tl", "proxy_kaynak", "proxy_fiyat_arabamcom_referans_tl",
    "proxy_nominal_aylik_pct", "proxy_reel_aylik_pct",
    "proxy_aylik_log_degisim", "proxy_reel_aylik_log_degisim",
    # BETAM'a tamamen bagimli hedef etiket/parametre sutunlari
    "proxy_yon_nominal", "proxy_yon_reel", "proxy_yon_tercile",
    "kullanilan_esik_k", "kullanilan_sigma_nominal", "kullanilan_sigma_reel",
    # ENAG (ilk dolu 2024-01)
    "enag_aylik", "enag_yillik", "enag_tufe_fark_yillik",
    "enag_kaynak_seviyesi", "enag_kaynak_url",
    # 2015-2017 erisim engeli (ilk dolu 2018-01)
    "noter_devir_otomobil_adet", "brut_ucret_maas_endeksi_2021_100",
    "alim_gucu_ceyrek", "erisim_endeksi",
]


def main():
    df_a = pd.read_csv(DF_A_YOLU)

    eksik_sutunlar = [c for c in CIKARILACAK_SUTUNLAR if c not in df_a.columns]
    if eksik_sutunlar:
        raise SystemExit(f"[HATA] DF-A'da olmasi beklenen sutunlar bulunamadi: {eksik_sutunlar}")

    df_tam = df_a.drop(columns=CIKARILACAK_SUTUNLAR)

    csv_yolu = DATAFRAMES_DIR / "df_a_tam_kapsamli_2015_bugun.csv"
    xlsx_yolu = DATAFRAMES_DIR / "df_a_tam_kapsamli_2015_bugun.xlsx"
    df_tam.to_csv(csv_yolu, index=False, encoding="utf-8-sig")
    df_tam.to_excel(xlsx_yolu, index=False, sheet_name="df_a_tam_kapsamli")

    print("=== GENISLETME 20 - DF-A TAM KAPSAMLI ALT KUMESI ===")
    print(f"Girdi (DF-A genis): {df_a.shape[0]} satir x {df_a.shape[1]} sutun")
    print(f"Cikarilan sutun sayisi: {len(CIKARILACAK_SUTUNLAR)}")
    print(f"Cikti (DF-A tam kapsamli): {df_tam.shape[0]} satir x {df_tam.shape[1]} sutun")
    print()
    print("Kalan sutunlar:")
    print(list(df_tam.columns))
    print()
    eksik_hucre = df_tam.isna().sum()
    eksik_hucre = eksik_hucre[eksik_hucre > 0]
    print(f"Kalan sutunlarda hala eksik hucre olan {len(eksik_hucre)} sutun:")
    if len(eksik_hucre):
        print(eksik_hucre.to_string())
    else:
        print("(yok)")
    print(f"\nCikti: {csv_yolu} , {xlsx_yolu}")


if __name__ == "__main__":
    main()
