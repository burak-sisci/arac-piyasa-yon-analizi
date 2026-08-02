"""
GENIŞLETME AŞAMA 19 — İki ayrı, net tanımlı DataFrame kurulumu (DF-A geniş,
DF-B dar/temiz), prompts/19_iki_dataframe_kurulumu_prompt.md.

ÖNEMLİ SAPMA 1 (kaynak dosya adı artık geçersiz): Görev talimatı girdi olarak
`data/processed/genisletme/veri_2018_bugun_etiketli.csv` istiyordu (2018-01
başlangıçlı, 102 satır — eksik_sutun_nedenleri.md raporunun yazıldığı andaki
omurga). Bu dosya ARTIK YOK: aynı proje içinde daha sonraki bir görevle
("genişletme 2015") omurga 2015-01'e geriye genişletilip
`veri_2015_bugun_etiketli.csv` (138 satır) olarak yeniden adlandırıldı, eski
dosya silindi. Bu script GÜNCEL omurgayı (`veri_2015_bugun_etiketli.csv`)
kullanır — görevin RUHU (geniş omurga + BETAM-dar filtre) korunur, yalnızca
kapsam 2018 yerine 2015'ten başlar. Çıktı dosya adı da bu yüzden
`df_a_genis_2015_bugun.csv` olarak adlandırıldı (talimattaki
`df_a_genis_2018_bugun.csv` DEĞİL) — kapsamla tutarlı isimlendirme,
projenin diğer "_2015_bugun_" yeniden adlandırmalarıyla aynı ilkeye uygun.

ÖNEMLİ SAPMA 2 (ENAG omurgada değildi): Görev talimatı DF-A'nın kapsamına
ENAG'ı da sayıyordu ("kur, TÜFE, ENAG, faiz, ODMD..."), ama ENAG hiçbir zaman
omurga tabloya birleştirilmemişti (bkz. pm_rapor_enag_cekme.md — bilinçli
karar, "TÜİK ve ENAG TEK seri haline getirilmedi"), yalnızca ayrı bir
karşılaştırma dosyasında (`data/processed/analiz/tufe_enag_karsilastirma.csv`)
duruyordu. Görev metninin DF-B doğrulamasında "ENAG 2024-01'den itibaren dolu
olduğundan BETAM'ın ... ayı için ENAG NaN kalabilir" diye ENAG'ın zaten
DataFrame içinde olduğunu varsayması, bu görevin ENAG'ın omurgaya
eklenmesini de kapsadığını gösteriyor. Bu yüzden ENAG'a ÖZGÜ sütunlar
(enag_aylik, enag_yillik, fark_yillik, kaynak_seviyesi, kaynak_url —
TÜİK ile isim çakışmasını önlemek için `enag_` önekiyle) referans_ayi
üzerinden DF-A'ya outer-join ile eklendi. TÜFE'nin kendisi (tufe_endeks,
tufe_aylik_degisim, tufe_yillik_degisim) omurganın KENDİ sütunları olarak
kalır, ENAG dosyasındaki tufe_aylik/tufe_yillik yinelenen/karşılaştırma
amaçlı sütunları BİLEREK atlandı (iki farklı TÜFE hesaplama yöntemini
karıştırmamak için, bkz. PM raporu).

ÖNEMLİ SAPMA 3 (BETAM başlangıcı 2023-12 değil 2024-01): Görev talimatının
bağlam notu "BETAM verisi yalnızca 2023-12'den itibaren düzenli yayımlanıyor"
diyordu, ama omurga tablosunda `proxy_fiyat_cari_tl` sütunu GERÇEKTE ilk kez
2024-01'de doludur (2023-12 zaten omurga kapsamının dışında/NaN). Script bu
YAZILI VARSAYIMA değil, VERİNİN KENDİSİNE göre filtreler (`proxy_fiyat_cari_tl.notna()`)
— bu yüzden DF-B otomatik olarak doğru ayı (2024-01) baz alır, talimattaki
"2023-12" ifadesi güncel veriyle birebir örtüşmüyor (bkz. PM raporu Bölüm 5).

Bu script SADECE filtreleme/birleştirme yapar — enterpolasyon, yeni feature
türetme, hedef değişiklik YOK.
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
GENISLETME_DIR = REPO_KOKU / "data" / "processed" / "genisletme"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"
DATAFRAMES_DIR = REPO_KOKU / "data" / "processed" / "dataframes"

OMURGA_YOLU = GENISLETME_DIR / "veri_2015_bugun_etiketli.csv"
ENAG_YOLU = ANALIZ_DIR / "tufe_enag_karsilastirma.csv"

ENAG_SUTUN_HARITASI = {
    "enag_aylik": "enag_aylik",
    "enag_yillik": "enag_yillik",
    "fark_yillik": "enag_tufe_fark_yillik",
    "kaynak_seviyesi": "enag_kaynak_seviyesi",
    "kaynak_url": "enag_kaynak_url",
}


def main():
    DATAFRAMES_DIR.mkdir(parents=True, exist_ok=True)

    omurga = pd.read_csv(OMURGA_YOLU)
    enag_ham = pd.read_csv(ENAG_YOLU)
    enag = enag_ham[["referans_ayi", *ENAG_SUTUN_HARITASI.keys()]].rename(columns=ENAG_SUTUN_HARITASI)

    # --- DF-A: genis, 2015-01 -> bugun, omurga + ENAG-'e ozgu sutunlar ---
    df_a = omurga.merge(enag, on="referans_ayi", how="left").sort_values("referans_ayi").reset_index(drop=True)

    df_a_csv = DATAFRAMES_DIR / "df_a_genis_2015_bugun.csv"
    df_a_xlsx = DATAFRAMES_DIR / "df_a_genis_2015_bugun.xlsx"
    df_a.to_csv(df_a_csv, index=False, encoding="utf-8-sig")
    df_a.to_excel(df_a_xlsx, index=False, sheet_name="df_a_genis")

    # --- DF-B: dar/temiz, yalnizca proxy_fiyat_cari_tl dolu olan aylar ---
    df_b = df_a[df_a["proxy_fiyat_cari_tl"].notna()].sort_values("referans_ayi").reset_index(drop=True)

    df_b_csv = DATAFRAMES_DIR / "df_b_dar_betam_bugun.csv"
    df_b_xlsx = DATAFRAMES_DIR / "df_b_dar_betam_bugun.xlsx"
    df_b.to_csv(df_b_csv, index=False, encoding="utf-8-sig")
    df_b.to_excel(df_b_xlsx, index=False, sheet_name="df_b_dar")

    # --- Dogrulama: DF-B'de disarida kalan aylar (BETAM bosluklari) ---
    tum_aylar = pd.period_range(df_a["referans_ayi"].min(), df_a["referans_ayi"].max(), freq="M").astype(str).tolist()
    df_b_aylar = set(df_b["referans_ayi"].tolist())
    disarida_kalan_aylar = [ay for ay in tum_aylar if ay not in df_b_aylar]

    # --- Dogrulama: DF-B'de hala eksik kalan sutun var mi ---
    df_b_eksik = df_b.isna().sum()
    df_b_eksik = df_b_eksik[df_b_eksik > 0].sort_values(ascending=False)

    print("=== GENISLETME 19 - IKI DATAFRAME KURULUMU OZETI ===")
    print(f"\nDF-A (genis): {df_a.shape[0]} satir x {df_a.shape[1]} sutun, "
          f"{df_a['referans_ayi'].min()} .. {df_a['referans_ayi'].max()}")
    print(f"Cikti: {df_a_csv} , {df_a_xlsx}")

    print(f"\nDF-B (dar/temiz): {df_b.shape[0]} satir x {df_b.shape[1]} sutun, "
          f"{df_b['referans_ayi'].min()} .. {df_b['referans_ayi'].max()}")
    print(f"Disarida kalan ay sayisi: {len(disarida_kalan_aylar)}")
    print(f"Disarida kalan aylar: {disarida_kalan_aylar}")
    print(f"Cikti: {df_b_csv} , {df_b_xlsx}")

    print(f"\nDF-B'de hala eksik kalan sutunlar ({len(df_b_eksik)} adet):")
    if len(df_b_eksik):
        print(df_b_eksik.to_string())
    else:
        print("(yok - DF-B tamamen dolu)")


if __name__ == "__main__":
    main()
