#!/usr/bin/env python3
"""Write source-separated arabam.com and BETAM supplemental price tables."""

from __future__ import annotations

import csv
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[2]


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def a(month, nominal, real="", date="", url="", status="official_html", quality="high", note=""):
    return {
        "referans_ayi": month,
        "yayin_tarihi": date,
        "ortalama_ilan_fiyati_tl": nominal,
        "reel_aylik_degisim_pct": real,
        "seri_id": "arabamcom_aylik_fiyat_endeksi",
        "kapsam": "arabam.com ikinci el otomobil ilanlari; ilan fiyati, gerceklesen satis fiyati degildir",
        "method_version": "official_monthly_index_unspecified_basket",
        "kaynak_url": url,
        "extraction_status": status,
        "extraction_quality": quality,
        "not": note,
    }


ARABAM = [
    a("2024-01", 667952, date="", url="https://www.arabam.com/blog/otomobil-inceleme/ocak-ayinda-otomobil-fiyatlari-26-geriledi/"),
    a("2024-02", 675580, date="", url="https://www.arabam.com/blog/otomobil-inceleme/otomobil-fiyatlarindaki-gerileme-subat-ayinda-durdu/"),
    a("2024-04", 682576, date="", url="https://www.arabam.com/blog/otomobil-inceleme/nisan-ayinda-ikinci-el-arac-fiyatlari-yatay-seyretti/"),
    a("2024-05", 684042, -3.0, url="https://www.aa.com.tr/tr/isdunyasi/otomotiv/arabamcom-mayis-ayi-ikinci-el-ilan-verilerini-acikladi/688267", status="company_release_via_aa", quality="medium", note="Resmi sirket aciklamasinin AA dagitimi; mevcut proxy dosyasindaki 913190 degeri Mayis 2026'ya aittir."),
    a("2024-06", "", -1.8, url="https://www.arabam.com/blog/", quality="medium", note="Acik metinde kesin nominal ortalama yok; yalnız resmi yazidaki reel degisim kaydedildi."),
    a("2024-07", "", -3.7, url="https://www.arabam.com/blog/", quality="medium", note="Acik metinde kesin nominal ortalama yok; yalnız resmi yazidaki reel degisim kaydedildi."),
    a("2024-08", 680584, -2.1, url="https://www.arabam.com/blog/", quality="medium"),
    a("2024-09", 684094, url="https://www.arabam.com/blog/otomobil-inceleme/ikinci-el-arac-fiyatlari-eyluldeki-dusus-trendini-surduruyor/"),
    a("2024-10", 689864, url="https://www.arabam.com/blog/", quality="medium"),
    a("2024-11", 692624, url="https://www.arabam.com/blog/", quality="medium"),
    a("2024-12", 695524, url="https://www.arabam.com/blog/genel/ikinci-el-arac-fiyatlari-yil-boyunca-dusmeye-devam-etti/"),
    a("2025-01", 695831, url="https://www.arabam.com/blog/", quality="medium", note="Subat 2025'teki seri/kapsam kirilmasindan onceki son deger."),
    a("2025-02", 783068, -1.8, "2025-03-14", "https://www.arabam.com/blog/danisman/subatta-piyasa-sabit-kaldi-ancak-bayram-oncesi-talep-artisi-bekleniyor/", note="Ocaga gore nominal yaklasik %12,5 sicrama; metindeki 'ciddi degisim yok' ifadesiyle celisiyor, method_break_flag=1."),
    a("2025-03", 786737, -1.94, "2025-04-25", "https://www.arabam.com/blog/genel/martta-ikinci-el-arac-fiyatlari-yukseldi-ancak-reel-fiyatlarda-dusus-devam-ediyor/"),
    a("2025-04", 795578, -1.82, "2025-05-22", "https://www.arabam.com/blog/genel/arabam-com-nisan-raporu-ilan-fiyatlarinda-artis-reel-fiyatlarda-dusus-suruyor/"),
    a("2025-05", 805729, -0.25, "2025-06-20", "https://www.arabam.com/blog/danisman/arabam-com-mayis-raporu-ikinci-elde-fiyat-dususu-yavasladi/"),
    a("2025-06", 807159, -1.17, "2025-07-16", "https://www.arabam.com/blog/otomobil-inceleme/arabam-com-haziran-raporu-reel-fiyatlarda-dusus-devam-ediyor/"),
    a("2025-07", 817985, -0.70, "2025-08-12", "https://www.arabam.com/blog/otomobil-inceleme/arabam-com-temmuz-raporu/"),
    a("2025-08", 841782, 0.43, "2025-09-08", "https://www.arabam.com/blog/genel/arabam-com-agustos-raporu-fiyatlarda-yilin-ilk-artisi/"),
    a("2025-09", 855467, -1.51, "2025-10-13", "https://www.arabam.com/blog/genel/arabam-com-raporu-eylulde-reel-fiyatlar-tekrar-dususe-gecti/"),
    a("2025-10", 869106, -0.93, "2025-11-19", "https://www.arabam.com/blog/genel/arabam-com-raporu-ekimde-reel-fiyatlardaki-dusus-suruyor/"),
    a("2025-11", 871758, -0.56, "2025-12-15", "https://www.arabam.com/blog/danisman/arabam-comdan-2025-ikinci-el-otomotiv-karnesi/"),
    a("2025-12", 871777, url="https://www.arabam.com/blog/genel/ikinci-el-otomobilde-reel-fiyatlar-ocakta-geriledi/", quality="medium", note="Ocak 2026 resmi yazisinda onceki ay degeri olarak yer alir."),
    a("2026-01", 877029, url="https://www.arabam.com/blog/genel/ikinci-el-otomobilde-reel-fiyatlar-ocakta-geriledi/"),
    a("2026-02", 888689, -1.58, "2026-03-12", "https://www.arabam.com/blog/genel/ikinci-el-otomobilde-neler-oluyor-subat-verileri-aciklandi/", note="Mevcut proxy dosyasinda yanlislikla 2025-02 olarak kaydedilmistir."),
    a("2026-03", 901156, url="https://www.arabam.com/blog/genel/mart-ayinda-otomotiv-sektorunde-talep-yavasladi/"),
    a("2026-04", 912045, -2.85, url="https://www.aa.com.tr/tr/isdunyasi/otomotiv/arabamcom-nisan-ayi-ikinci-el-ilan-verilerini-paylasti/702340", status="company_release_via_aa", quality="medium"),
    a("2026-05", 913190, url="https://www.arabam.com/blog/genel/bayram-etkisiyle-mayis-ayinda-otomotiv-pazarinda-tempo-dustu/"),
    a("2026-06", 914918, url="https://www.arabam.com/blog/genel/otomotivde-haziran-duragan-gecti-reel-fiyatlar-dususte/"),
]


BETAM = [
    {
        "referans_ayi": "2023-11", "yayin_tarihi": "2023-12-15", "ortalama_ilan_fiyati_tl": 879146,
        "reel_aylik_degisim_pct": -6.0, "seri_id": "betam_sahibindex_ortalama_satilik_otomobil",
        "kapsam": "sahibinden.com satilik otomobil ilanlari; BETAM sahibindex metodolojisi",
        "kaynak_url": "https://betam.bahcesehir.edu.tr/2023/12/sahibindex-otomobil-piyasasi-gorunumu/",
        "extraction_quality": "high", "not": "Kamuya acik serinin kesin sayisal ilk gozlemi."
    },
    {
        "referans_ayi": "2023-12", "yayin_tarihi": "2024-01-25", "ortalama_ilan_fiyati_tl": 860480,
        "reel_aylik_degisim_pct": -5.0, "seri_id": "betam_sahibindex_ortalama_satilik_otomobil",
        "kapsam": "sahibinden.com satilik otomobil ilanlari; BETAM sahibindex metodolojisi",
        "kaynak_url": "https://betam.bahcesehir.edu.tr/2024/01/sahibindex-otomobil-piyasasi-gorunumu-ocak-2024/",
        "extraction_quality": "high", "not": "Mevcut 2024+ proxy serisine kaynak-tutarli on ek; arabam.com ile birlestirilmemeli."
    },
]


def validate_arabam(rows):
    months = [r["referans_ayi"] for r in rows]
    assert months == sorted(months) and len(months) == len(set(months))
    for r in rows:
        assert r["kaynak_url"], r["referans_ayi"]
        if r["ortalama_ilan_fiyati_tl"] not in ("", None):
            assert r["ortalama_ilan_fiyati_tl"] > 0


def main():
    validate_arabam(ARABAM)
    write_csv(ROOT / "data" / "arabamcom" / "arabamcom_aylik_fiyat.csv", ARABAM)
    manifest = [{
        "referans_ayi": r["referans_ayi"], "kaynak_url": r["kaynak_url"],
        "kaynak_turu": r["extraction_status"], "extraction_quality": r["extraction_quality"],
        "not": r["not"],
    } for r in ARABAM]
    write_csv(ROOT / "data" / "arabamcom" / "arabamcom_manifest.csv", manifest)
    write_csv(ROOT / "data" / "betam" / "betam_2023_eksik_tamamlayici.csv", BETAM)
    print(f"OK: {len(ARABAM)} arabam.com rows, {len(BETAM)} BETAM supplemental rows")


if __name__ == "__main__":
    main()
