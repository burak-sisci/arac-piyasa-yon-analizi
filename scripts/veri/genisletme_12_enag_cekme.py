"""
GENIŞLETME AŞAMA 12 — ENAG (Enflasyon Araştırma Grubu) E-TÜFE kontrol serisi,
2024-01 -> 2026-06 (30 ay).

NEDEN: TÜİK TÜFE ile ENAG E-TÜFE arasında sistematik ve büyük bir fark var
(2026 Ocak-Mayıs: 20-24 puan bandı). Bu script TÜFE'yi DEĞİŞTİRMEZ, ENAG'ı
yalnızca KONTROL/PARALEL seri olarak paralel tutar (K1 alt kararı).

KAYNAK DURUMU (2026-07-27 itibarıyla): enagrup.org resmi sitesi Cloudflare
525 (SSL handshake failed) hatasıyla ERİŞİLEMEZ - geçici bir altyapı sorunu,
kaynak yokluğu değil (bülten arşivinin var olduğu, ör. enagrup.org/bulten/
202112.pdf gibi URL'lerin arama sonuçlarında göründüğü doğrulandı, ama içeriğe
şu an ulaşılamıyor). Bu yüzden KAYNAK ÖNCELİK KURALI B/C seviyesine düştü:
  A = enagrup.org resmi site/PDF (şu an 0/30 ay - erişilemez)
  B = ENAG'ın resmi X/Twitter hesabı (@ENAGRUP)                    - 9/30 ay
  C = saygın haber ajansı/medya, ENAG'a doğrudan atıfla            - 21/30 ay
  D = diğer/daha az güvenilir                                      - 0/30 ay
  bulunamadı                                                       - 0/30 ay

ÇAPRAZ DOĞRULAMA: 5 ay (2024-01, 2024-07, 2025-01, 2025-07, 2026-01) BAĞIMSIZ
ikinci bir arama+kaynak seti ile yeniden bulundu - 5/5 "EVET" (birebir uyum).

YIL-KARIŞMASI RİSKİ (bu projede TÜİK verisinde daha önce kanıtlanmıştı, ENAG
için de sistematik olarak karşılaşıldı ve elendi): WebSearch sorguları çoğu
ay için YANLIŞ YILA ait sonuçlar döndürdü (ör. "ENAG Mart 2025" araması Mart
2026 verisini döndürdü). Her ay için bulunan TÜİK yıllık rakamı, o ayın
BİLİNEN resmi TÜİK rakamıyla çapraz kontrol edilerek doğru yıl/ay teyit
edildi - uyuşmayan sonuçlar (4-6 ayda bir rastlanan) tespit edilip reddedildi.
Ayrıca birden çok ay için arama sonucu metninde OCR/render bozukluğu (ör.
"U,38", "q,23", "V,82" gibi bozuk basamaklar) tespit edildi - bu rakamlar
KULLANILMADI, temiz alternatif kaynaklarla değiştirildi.

Girdi: data/raw/tufe/tufe_2024_bugun_aylik.csv (mevcut TÜİK TÜFE serisi)
Çıktı:
  - data/raw/enag/enag_aylik_2024_2026.csv
  - data/processed/analiz/tufe_enag_karsilastirma.csv
  - data/processed/analiz/gorseller/tufe_vs_enag.png

NOT (2026-08-03): Bu script'in çıktısı, genisletme_20_enag_birlestirme.py
tarafından 2021-2023 genişletme verisiyle birleştirilerek
data/raw/enag/enag_aylik_2021_2026.csv'de tek dosya haline getirildi. Bu
script tarihsel kayıt olarak durur; ENAG ham verisi için GÜNCEL kaynak
enag_aylik_2021_2026.csv'dir (bu script'i yeniden çalıştırmak eski parçalı
enag_aylik_2024_2026.csv dosyasını geri getirir, birleşik dosyayı SİLMEZ ama
onu güncellemez).
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
ENAG_RAW_DIR = REPO_KOKU / "data" / "raw" / "enag"
TUFE_RAW_CSV = REPO_KOKU / "data" / "raw" / "tufe" / "tufe_2024_bugun_aylik.csv"
ANALIZ_DIR = REPO_KOKU / "data" / "processed" / "analiz"
GORSEL_DIR = ANALIZ_DIR / "gorseller"

# Her kayıt, Workflow ile 6 paralel ajanın topladığı ve (5 örneklem ayı için)
# bağımsız ikinci kaynakla çapraz doğrulanan ENAG E-TÜFE rakamıdır. Kaynak
# URL'i ve seviyesi (A-D) her ay için ayrı saklanır - izlenebilirlik için.
KAYITLAR = [
    dict(referans_ayi="2024-01", enag_aylik_degisim=9.38, enag_yillik_degisim=129.11, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.brandingturkiye.com/enag-ocak-2024-enflasyonunu-acikladi/"),
    dict(referans_ayi="2024-02", enag_aylik_degisim=4.32, enag_yillik_degisim=121.98, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.brandingturkiye.com/enag-subat-2024-enflasyonunu-acikladi/"),
    dict(referans_ayi="2024-03", enag_aylik_degisim=5.68, enag_yillik_degisim=124.63, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.brandingturkiye.com/enag-mart-2024-enflasyonunu-acikladi/"),
    dict(referans_ayi="2024-04", enag_aylik_degisim=5.02, enag_yillik_degisim=124.35, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.brandingturkiye.com/enag-nisan-2024-enflasyonunu-acikladi/"),
    dict(referans_ayi="2024-05", enag_aylik_degisim=5.66, enag_yillik_degisim=120.66, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.brandingturkiye.com/enag-mayis-2024-enflasyonunu-acikladi/"),
    dict(referans_ayi="2024-06", enag_aylik_degisim=4.27, enag_yillik_degisim=113.08, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.dunya.com/ekonomi/son-dakika-enflasyon-verisi-enag-enflasyon-rakamlarini-acikladi-enag-enflasyon-orani-haziran-2024-haberi-734991"),
    dict(referans_ayi="2024-07", enag_aylik_degisim=5.91, enag_yillik_degisim=100.88, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.dunya.com/ekonomi/son-dakika-enflasyon-rakamlari-enag-enflasyon-verilerini-duyurdu-enag-enflasyon-orani-temmuz-2024-haberi-739877"),
    dict(referans_ayi="2024-08", enag_aylik_degisim=3.47, enag_yillik_degisim=90.35, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1830852128165761448"),
    dict(referans_ayi="2024-09", enag_aylik_degisim=5.34, enag_yillik_degisim=88.63, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.brandingturkiye.com/enag-eylul-2024-enflasyonunu-acikladi/"),
    dict(referans_ayi="2024-10", enag_aylik_degisim=5.57, enag_yillik_degisim=89.77, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1853331678254465533"),
    dict(referans_ayi="2024-11", enag_aylik_degisim=4.06, enag_yillik_degisim=86.76, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/2024/12/03/kasim-ayi-enflasyonu-yillik-bazda-4709-olarak-aciklandi"),
    dict(referans_ayi="2024-12", enag_aylik_degisim=2.34, enag_yillik_degisim=83.40, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1875063179904237709"),
    dict(referans_ayi="2025-01", enag_aylik_degisim=8.22, enag_yillik_degisim=81.01, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/business/2025/02/03/ocak-ayinda-yillik-enflasyon-tuike-gore-yuzde-4212-enaga-gore-8101"),
    dict(referans_ayi="2025-02", enag_aylik_degisim=3.37, enag_yillik_degisim=79.51, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/2025/03/03/subat-ayinda-yillik-enflasyon-tuike-gore-yuzde-3905-enaga-gore-7951"),
    dict(referans_ayi="2025-03", enag_aylik_degisim=3.91, enag_yillik_degisim=75.20, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/2025/04/03/tuike-gore-mart-ayinda-yillik-enflasyon-yuzde-3810-enaga-gore-7520-kira-artis-orani-5126-o"),
    dict(referans_ayi="2025-04", enag_aylik_degisim=4.46, enag_yillik_degisim=73.88, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1919274592599687588"),
    dict(referans_ayi="2025-05", enag_aylik_degisim=3.66, enag_yillik_degisim=71.23, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1929783523218530778"),
    dict(referans_ayi="2025-06", enag_aylik_degisim=3.05, enag_yillik_degisim=68.68, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/business/2025/07/03/haziranda-yillik-enflasyon-tuik-yuzde-3505-enag-ise-yuzde-6868-acikladi"),
    dict(referans_ayi="2025-07", enag_aylik_degisim=3.75, enag_yillik_degisim=65.15, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/2025/08/04/temmuzda-yillik-enflasyon-tuik-yuzde-3352-enag-ise-yuzde-6515-acikladi"),
    dict(referans_ayi="2025-08", enag_aylik_degisim=3.23, enag_yillik_degisim=65.49, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1963123701089530034"),
    dict(referans_ayi="2025-09", enag_aylik_degisim=3.79, enag_yillik_degisim=63.23, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/business/2025/10/03/eylul-ayinda-yillik-enflasyon-tuik-yuzde-3329-enag-ise-yuzde-6323-acikladi"),
    dict(referans_ayi="2025-10", enag_aylik_degisim=3.74, enag_yillik_degisim=60.00, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1985229202124427767"),
    dict(referans_ayi="2025-11", enag_aylik_degisim=2.13, enag_yillik_degisim=56.82, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/1996101595629846658"),
    dict(referans_ayi="2025-12", enag_aylik_degisim=2.11, enag_yillik_degisim=56.14, enag_endeks=None, kaynak_seviyesi="B", kaynak_url="https://x.com/ENAGRUP/status/2008059692640063583"),
    dict(referans_ayi="2026-01", enag_aylik_degisim=6.32, enag_yillik_degisim=53.42, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/2026/02/03/ocakta-yillik-enflasyon-tuik-yuzde-3065-enag-ise-yuzde-5342-acikladi"),
    dict(referans_ayi="2026-02", enag_aylik_degisim=4.01, enag_yillik_degisim=54.14, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://tr.euronews.com/2026/03/03/subatta-yillik-enflasyon-tuik-yuzde-3153-enag-ise-yuzde-5414-acikladi"),
    dict(referans_ayi="2026-03", enag_aylik_degisim=4.10, enag_yillik_degisim=54.62, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/enag-mart-ayi-enflasyon-verilerini-acikladi-2491771"),
    dict(referans_ayi="2026-04", enag_aylik_degisim=5.07, enag_yillik_degisim=55.38, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.ensonolay.com.tr/ekonomi/enag-nisan-2026-enflasyon-rakamlarini-acikladi-aylik-enflasyon-orani-yuzde-kac/47108"),
    dict(referans_ayi="2026-05", enag_aylik_degisim=2.16, enag_yillik_degisim=53.13, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/enag-mayis-ayi-enflasyon-verilerini-acikladi-2508647"),
    dict(referans_ayi="2026-06", enag_aylik_degisim=1.94, enag_yillik_degisim=51.49, enag_endeks=None, kaynak_seviyesi="C", kaynak_url="https://www.24saatgazetesi.com/enag-haziran-2026-enflasyon-verilerini-acikladi-yillik-artis-yuzde-5149"),
]

# 5 ay icin, tamamen bagimsiz bir ikinci arama+kaynak seti ile capraz dogrulama
# yapildi (Workflow'un ayri bir "dogrulama" ajani, ilk bulguyu GORMEDEN once
# kendi aramasini yapti). Hepsi "EVET" (birebir uyum) sonucu verdi.
CAPRAZ_DOGRULAMA = [
    dict(referans_ayi="2024-01", sonuc="EVET", ikinci_kaynak_url="https://www.ekonomim.com/ekonomi/son-dakika-enag-ocak-ayi-enflasyon-rakamlarini-acikladi-haberi-728244"),
    dict(referans_ayi="2024-07", sonuc="EVET", ikinci_kaynak_url="https://tr.euronews.com/business/2024/08/05/enagin-yuzde-10088-olarak-acikladigi-yillik-enflasyon-tuike-gore-yuzde-6178"),
    dict(referans_ayi="2025-01", sonuc="EVET", ikinci_kaynak_url="https://www.brandingturkiye.com/enag-ocak-2025-enflasyonunu-acikladi/"),
    dict(referans_ayi="2025-07", sonuc="EVET", ikinci_kaynak_url="https://www.brandingturkiye.com/enag-temmuz-2025-enflasyonunu-acikladi/"),
    dict(referans_ayi="2026-01", sonuc="EVET", ikinci_kaynak_url="https://www.cumhuriyet.com.tr/ekonomi/enag-ocak-ayi-enflasyon-verilerini-acikladi-2475350"),
]


def main():
    ENAG_RAW_DIR.mkdir(parents=True, exist_ok=True)
    ANALIZ_DIR.mkdir(parents=True, exist_ok=True)
    GORSEL_DIR.mkdir(parents=True, exist_ok=True)

    enag = pd.DataFrame(KAYITLAR).sort_values("referans_ayi").reset_index(drop=True)
    enag_csv = ENAG_RAW_DIR / "enag_aylik_2024_2026.csv"
    enag.to_csv(enag_csv, index=False, encoding="utf-8-sig")

    # --- TUIK TUFE ile YAN YANA karsilastirma (birlestirme DEGIL, ayri sutunlar) ---
    tufe = pd.read_csv(TUFE_RAW_CSV)[["referans_ayi", "tufe_aylik_degisim", "tufe_yillik_degisim"]]
    karsilastirma = enag.merge(tufe, on="referans_ayi", how="left")
    karsilastirma = karsilastirma.rename(columns={
        "enag_aylik_degisim": "enag_aylik", "enag_yillik_degisim": "enag_yillik",
        "tufe_aylik_degisim": "tufe_aylik", "tufe_yillik_degisim": "tufe_yillik",
    })
    karsilastirma["fark_yillik"] = karsilastirma["enag_yillik"] - karsilastirma["tufe_yillik"]
    karsilastirma = karsilastirma[[
        "referans_ayi", "tufe_aylik", "tufe_yillik", "enag_aylik", "enag_yillik",
        "fark_yillik", "kaynak_seviyesi", "kaynak_url",
    ]]
    karsilastirma_csv = ANALIZ_DIR / "tufe_enag_karsilastirma.csv"
    karsilastirma.to_csv(karsilastirma_csv, index=False, encoding="utf-8-sig")

    # --- gorsel: iki serinin yillik enflasyonu ust uste ---
    fig, ax = plt.subplots(figsize=(11, 5))
    aylar_dt = pd.to_datetime(karsilastirma["referans_ayi"], format="%Y-%m")
    ax.plot(aylar_dt, karsilastirma["tufe_yillik"], color="#2a78d6", linewidth=2, label="TÜİK TÜFE (yıllık %)")
    ax.plot(aylar_dt, karsilastirma["enag_yillik"], color="#eb6834", linewidth=2, label="ENAG E-TÜFE (yıllık %)")
    ax.fill_between(aylar_dt, karsilastirma["tufe_yillik"], karsilastirma["enag_yillik"], color="#898781", alpha=0.15)
    ax.set_title("TÜİK TÜFE vs ENAG E-TÜFE — yıllık enflasyon (2024-01 → 2026-06)")
    ax.set_ylabel("Yıllık değişim (%)")
    ax.legend()
    fig.tight_layout()
    gorsel_yolu = GORSEL_DIR / "tufe_vs_enag.png"
    fig.savefig(gorsel_yolu, dpi=110)
    plt.close(fig)

    # --- ozet ---
    print("=== GENISLETME 12 - ENAG E-TUFE KONTROL SERISI OZETI ===\n")
    print(f"Kapsanan donem: {karsilastirma['referans_ayi'].min()} -> {karsilastirma['referans_ayi'].max()} ({len(karsilastirma)} ay)")
    print(f"Kaynak seviyesi dagilimi: {enag['kaynak_seviyesi'].value_counts().to_dict()}")
    print()
    print("--- Capraz dogrulama (5 ay, bagimsiz ikinci kaynak) ---")
    for d in CAPRAZ_DOGRULAMA:
        print(f"  {d['referans_ayi']}: {d['sonuc']}  (ikinci kaynak: {d['ikinci_kaynak_url']})")
    print()
    print("--- TUIK-ENAG yillik fark istatistigi ---")
    print(f"Ortalama fark: {karsilastirma['fark_yillik'].mean():.2f} puan")
    print(f"Min fark: {karsilastirma['fark_yillik'].min():.2f} puan ({karsilastirma.loc[karsilastirma['fark_yillik'].idxmin(), 'referans_ayi']})")
    print(f"Maks fark: {karsilastirma['fark_yillik'].max():.2f} puan ({karsilastirma.loc[karsilastirma['fark_yillik'].idxmax(), 'referans_ayi']})")
    print(f"Std sapma: {karsilastirma['fark_yillik'].std():.2f} puan")
    print()
    print("--- Tablo ---")
    print(karsilastirma[["referans_ayi", "tufe_yillik", "enag_yillik", "fark_yillik", "kaynak_seviyesi"]].to_string(index=False))
    print()
    print(f"Cikti: {enag_csv}")
    print(f"Cikti: {karsilastirma_csv}")
    print(f"Gorsel: {gorsel_yolu}")


if __name__ == "__main__":
    main()
