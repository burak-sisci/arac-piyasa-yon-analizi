#!/usr/bin/env python3
"""Build and validate the auditable Indicata monthly market series.

The numeric rows below are transcribed from the named official report sections.
Use --verify-online to refresh HTTP status metadata without retaining the PDFs.
Use --download-raw explicitly if a local PDF archive is desired (about 80 MB).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import time
import urllib.error
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "indicata"
RAW = OUT / "raw"

SCOPE = (
    "Turkiye ikinci el online binek ve hafif ticari arac pazari; "
    "kurumsal ilanlar; bireysel ilanlar kapsam disi"
)
SALE_NOTE = "Ilandan tamamen kaldirilan kurumsal arac satisa donmus/satilmis kabul edilir; noter devri degildir."


REPORTS = [
    ("2024-01", "", "https://www.indicata.com.tr/download/Ocak2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "cached_pdf_404"),
    ("2024-02", "", "https://www.indicata.com.tr/download/Subat2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "cached_pdf_404"),
    ("2024-03", "", "https://www.indicata.com.tr/download/Mart2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "cached_pdf_404"),
    ("2024-04", "", "https://www.indicata.com.tr/download/Nisan2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "cached_pdf_404"),
    ("2024-05", "", "https://www.indicata.com.tr/download/Mayis2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "cached_pdf_404"),
    ("2024-06", "", "https://www.indicata.com.tr/download/Haziran2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "cached_pdf_404"),
    ("2024-07", "2024-08-30", "https://indicata.com.tr/wp-content/uploads/2024/08/Temmuz2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2024-08", "2024-09-05", "https://indicata.com.tr/wp-content/uploads/2024/09/Agustos2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2024-09", "2024-10-15", "https://indicata.com.tr/wp-content/uploads/2024/10/Eylul2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2024-10", "2024-11-22", "https://indicata.com.tr/wp-content/uploads/2024/10/Ekim2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2024-11", "2024-12-16", "https://indicata.com.tr/wp-content/uploads/2024/10/Kasim2024_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2024-12", "2025-01-08", "https://indicata.com.tr/wp-content/uploads/2025/01/Aralik2024_Turkiye_Otomotiv_2-El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf_annual"),
    ("2025-01", "2025-02-07", "https://indicata.com.tr/wp-content/uploads/2025/02/Ocak2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-02", "2025-03-10", "https://indicata.com.tr/wp-content/uploads/2025/03/Subat2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-03", "2025-04-04", "https://indicata.com.tr/wp-content/uploads/2024/10/Mart2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-04", "2025-05-06", "https://indicata.com.tr/wp-content/uploads/2025/05/Nisan2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-05", "2025-06-06", "https://indicata.com.tr/wp-content/uploads/2025/06/Mayis2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz-Raporu.pdf", "live_pdf"),
    ("2025-06", "2025-07-08", "https://indicata.com.tr/wp-content/uploads/2025/07/Haziran2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-07", "2025-08-06", "https://indicata.com.tr/wp-content/uploads/2025/08/Temmuz2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-08", "2025-09-04", "https://indicata.com.tr/wp-content/uploads/2024/10/Agustos2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-09", "2025-10-06", "https://indicata.com.tr/wp-content/uploads/2025/10/Eylul2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-10", "2025-11-06", "https://indicata.com.tr/wp-content/uploads/2024/10/Ekim2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-11", "2025-12-08", "https://indicata.com.tr/wp-content/uploads/2025/12/Kasim2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2025-12", "2026-01-05", "https://indicata.com.tr/wp-content/uploads/2025/12/Aralik2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2026-01", "2026-02-06", "https://indicata.com.tr/wp-content/uploads/2026/02/Ocak2026_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf", "live_pdf"),
    ("2026-02", "2026-03-06", "https://indicata.com.tr/wp-content/uploads/2026/03/Subat_2026_Turkiye_Otomotiv_2El_Online_Ozet_Pazar_Analiz_Raporu.pdf", "live_pdf_summary"),
    ("2026-03", "2026-04-07", "https://indicata.com.tr/wp-content/uploads/2026/03/Mart_2026_Turkiye_Otomotiv_2El_Online_Ozet_Pazar_Analiz_Raporu.pdf", "live_pdf_summary"),
    ("2026-04", "2026-05-11", "https://indicata.com.tr/wp-content/uploads/2026/05/Nisan_2026_Turkiye_Otomotiv_2El_Online_Ozet_Pazar_Analiz_Raporu.pdf", "live_pdf_summary"),
    ("2026-05", "2026-06-05", "https://indicata.com.tr/wp-content/uploads/2026/05/Mayis_2026_Turkiye_Otomotiv_2El_Online_Ozet_Pazar_Analiz_Raporu.pdf", "live_pdf_summary"),
    ("2026-06", "2026-07-06", "https://indicata.com.tr/wp-content/uploads/2026/06/Haziran_2026_Turkiye_Otomotiv_2El_Online_Ozet_Pazar_Analiz_Raporu-2.pdf", "live_pdf_summary"),
    ("2026-07", "2026-08-05", "https://indicata.com.tr/wp-content/uploads/2026/07/Temmuz-2026-Turkiye-Otomotiv-2.-El-Online-Pazar-Analiz-Raporu-OZET.pdf", "live_pdf_summary"),
]

ANNUAL_REPORTS = [
    ("2020-annual", "https://800c985b-78cc-4640-bb19-f793af8646d8.filesusr.com/ugd/61b3c3_3ea6b66abbef46278054972a30700ac9.pdf"),
    ("2021-annual", "https://800c985b-78cc-4640-bb19-f793af8646d8.filesusr.com/ugd/61b3c3_e7a77462375249ae9263898117b09836.pdf"),
    ("2022-annual", "https://800c985b-78cc-4640-bb19-f793af8646d8.filesusr.com/ugd/61b3c3_6c87de964b58478a8f1ba99c4f60e187.pdf"),
    ("2023-annual", "https://800c985b-78cc-4640-bb19-f793af8646d8.filesusr.com/ugd/61b3c3_be181617f1e544d0a02d018ee687d958.pdf"),
    ("2024-annual", "https://800c985b-78cc-4640-bb19-f793af8646d8.filesusr.com/ugd/61b3c3_5001e0d368d74c79a34c9ed7484cb2a4.pdf"),
    ("2025-annual", "https://odmd.org.tr/folders/2837/categorial1docs/6024/Aralik2025_Turkiye_Otomotiv_2El_Online_Pazar_Analiz_Raporu.pdf"),
]


def report_url(month: str) -> str:
    return next(url for ref, _, url, _ in REPORTS if ref == month)


def row(month, listings, sales, ratio=None, dom=None, retail=None, wholesale=None,
        method="v2024_full", source_month=None, status="official_pdf", quality="high", note=""):
    source_month = source_month or month
    pub_date = next((date for ref, date, _, _ in REPORTS if ref == source_month), "")
    return {
        "referans_ayi": month,
        "ilk_acik_yayin_tarihi": pub_date,
        "ilan_yayinlanan_adet": listings,
        "satisa_donen_adet": sales,
        "satis_ilan_orani_pct": round(100 * sales / listings, 2) if ratio is None and listings and sales else ratio,
        "ortalama_satis_hizi_gun": dom,
        "perakende_fiyat_aylik_pct": retail,
        "toptan_fiyat_aylik_pct": wholesale,
        "kapsam": SCOPE,
        "method_version": method,
        "metodoloji_notu": SALE_NOTE,
        "kaynak_url": report_url(source_month),
        "kaynak_dosya": pathlib.PurePosixPath(report_url(source_month)).name,
        "kaynak_baglami": note or "Rapor ozet/ilan-satis/fiyat bolumleri",
        "availability_status": "retrospective_only" if month.startswith("2023-") else "as_reported",
        "extraction_status": status,
        "extraction_quality": quality,
    }


ROWS = [
    row("2023-01", 388097, 163403, source_month="2024-01", method="v2024_comparative", status="official_cached_comparative", quality="medium", note="Ocak 2024 raporundaki Ocak'23 karsilastirma grafigi"),
    row("2023-02", 348330, 126043, source_month="2024-02", method="v2024_comparative", status="official_cached_comparative", quality="medium", note="Subat 2024 raporundaki Subat'23 karsilastirma grafigi"),
    row("2023-03", 360458, 189643, source_month="2024-03", method="v2024_comparative", status="official_cached_comparative", quality="medium", note="Mart 2024 raporundaki Mart'23 karsilastirma grafigi"),
    row("2023-04", 327273, 172450, source_month="2024-04", method="v2024_comparative", status="official_cached_comparative", quality="medium", note="Nisan 2024 raporundaki Nisan'23 karsilastirma grafigi"),
    row("2023-05", 326372, 172434, source_month="2024-05", method="v2024_comparative", status="official_cached_comparative", quality="medium", note="Mayis 2024 raporundaki Mayis'23 karsilastirma grafigi"),
    row("2023-06", 298004, 180748, source_month="2024-06", method="v2024_comparative", status="official_cached_comparative", quality="medium", note="Haziran 2024 raporundaki Haziran'23 karsilastirma grafigi"),
    row("2023-07", 266564, 162348, source_month="2024-07", method="v2024_comparative", note="Temmuz 2024 raporundaki Temmuz'23 karsilastirma grafigi"),
    row("2023-08", 360445, 125935, source_month="2024-08", method="v2024_comparative", note="Agustos 2024 raporundaki Agustos'23 karsilastirma grafigi"),
    row("2023-09", 378274, 141508, source_month="2024-09", method="v2024_comparative", note="Eylul 2024 raporundaki Eylul'23 karsilastirma grafigi"),
    row("2023-10", 388283, 134259, source_month="2024-10", method="v2024_comparative", note="Ekim 2024 raporundaki Ekim'23 karsilastirma grafigi"),
    row("2023-11", 331906, 143905, source_month="2024-11", method="v2024_comparative", note="Kasim 2024 raporundaki Kasim'23 karsilastirma grafigi"),
    row("2023-12", 377638, 168421, source_month="2024-12", method="v2024_comparative", status="derived_official_totals", note="2023 yil toplami eksi 2023 ilk 11 ay toplami; iki resmi toplamdan tam fark"),
    row("2024-01", 354743, 181774, 51, 45, -0.09, None, status="official_cached_pdf", quality="medium"),
    row("2024-02", 363001, 170457, 47, 45, 0.23, 2.46, status="official_cached_pdf", quality="medium"),
    row("2024-03", 397073, 187229, 47, 40, 1.34, 2.40, status="official_cached_pdf", quality="medium"),
    row("2024-04", 350588, 157463, 45, 47, 0.73, 0.37, status="official_cached_pdf", quality="medium"),
    row("2024-05", 411203, 160811, 39, 48, -0.35, -0.77, status="official_cached_pdf", quality="medium"),
    row("2024-06", 330405, 156974, 48, 51, -2.00, -3.41, status="official_cached_pdf", quality="medium"),
    row("2024-07", 368408, 175738, 48, 44, 0.95, 1.78),
    row("2024-08", 354948, 181438, 51, 37, 0.89, 1.05),
    row("2024-09", 357056, 173678, 49, 34, 2.55, 3.60),
    row("2024-10", 441572, 186583, 42, 35, 2.00, 3.40),
    row("2024-11", 387998, 176921, 46, 32, 1.00, 1.00),
    row("2024-12", 429334, 182852, None, None, -0.87, -1.12, status="derived_official_totals", note="Aylik ilan/satis, resmi yil toplami eksi ilk 11 ay toplami; DOM raporda yalniz yillik verildigi icin bos"),
    row("2025-01", 418164, 185203, retail=0.59, method="v2025_summary"),
    row("2025-02", 375974, 185834, retail=0.30, method="v2025_summary"),
    row("2025-03", 440887, 206387, retail=0.30, method="v2025_summary"),
    row("2025-04", 413633, 202698, retail=1.39, method="v2025_summary"),
    row("2025-05", 435917, 199948, retail=1.46, method="v2025_summary"),
    row("2025-06", 423119, 162541, retail=1.49, method="v2025_summary"),
    row("2025-07", 413824, 208323, retail=1.82, method="v2025_summary"),
    row("2025-08", 410807, 231822, retail=2.19, method="v2025_summary"),
    row("2025-09", 447586, 193049, retail=1.25, method="v2025_summary"),
    row("2025-10", 470394, 192033, retail=0.80, method="v2025_summary"),
    row("2025-11", 439809, 199255, retail=0.83, method="v2025_summary"),
    row("2025-12", 496986, 222140, retail=0.79, method="v2025_summary"),
    row("2026-01", 443535, 193802, method="v2026_summary_v2"),
    row("2026-02", 493325, 181234, method="v2026_summary_v2"),
    row("2026-03", 476545, 185710, method="v2026_summary_v2"),
    row("2026-04", 435316, 208165, method="v2026_summary_v2"),
    row("2026-05", 457185, 175316, method="v2026_summary_v2"),
    row("2026-06", 306642, 157705, method="v2026_summary_v2"),
    row("2026-07", 372638, 176613, method="v2026_summary_v2"),
]


def probe(url: str) -> tuple[str, str, str]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "market-research/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return str(resp.status), resp.headers.get_content_type(), resp.headers.get("Content-Length", "")
    except urllib.error.HTTPError as exc:
        return str(exc.code), exc.headers.get_content_type() if exc.headers else "", ""
    except Exception as exc:  # network diagnostics belong in manifest
        return "network_error", "", type(exc).__name__


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def validate(rows: list[dict]) -> None:
    months = [r["referans_ayi"] for r in rows]
    assert len(months) == len(set(months)), "Duplicate reference month"
    assert months == sorted(months), "Rows must be sorted"
    for r in rows:
        assert r["ilan_yayinlanan_adet"] > 0 and r["satisa_donen_adet"] > 0
        assert r["satisa_donen_adet"] <= r["ilan_yayinlanan_adet"]
        calc = 100 * r["satisa_donen_adet"] / r["ilan_yayinlanan_adet"]
        assert abs(calc - float(r["satis_ilan_orani_pct"])) <= 0.75, (r["referans_ayi"], calc)
        if r["ortalama_satis_hizi_gun"] not in (None, ""):
            assert 1 <= r["ortalama_satis_hizi_gun"] <= 365


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-online", action="store_true")
    parser.add_argument("--download-raw", action="store_true")
    args = parser.parse_args()
    validate(ROWS)
    write_csv(OUT / "indicata_aylik.csv", ROWS)

    checked = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    manifest = []
    for ref, pub_date, url, kind in REPORTS:
        status, mime, length = ("not_checked", "", "")
        if args.verify_online:
            status, mime, length = probe(url)
            time.sleep(0.2)
        extraction = "extracted_monthly"
        note = ""
        if kind == "cached_pdf_404":
            note = "Eski resmi URL bugun 404; degerler arama motorunda indekslenmis resmi PDF metninden denetlendi."
        if kind == "live_pdf_annual":
            note = "Aralik aylik ilan/satis degeri yil toplami eksi ilk 11 ay toplamindan turetildi."
        manifest.append({
            "rapor_referans_ayi": ref, "yayin_tarihi": pub_date, "kaynak_url": url,
            "http_durumu": status, "mime_type": mime, "content_length": length,
            "dosya_tipi": "pdf", "rapor_turu": kind,
            "extraction_durumu": extraction, "kontrol_zamani_utc": checked, "not": note,
        })
        if args.download_raw and status == "200" and "pdf" in mime:
            RAW.mkdir(parents=True, exist_ok=True)
            target = RAW / f"{ref}_{pathlib.PurePosixPath(url).name}"
            urllib.request.urlretrieve(url, target)
    for label, url in ANNUAL_REPORTS:
        status, mime, length = ("not_checked", "", "")
        if args.verify_online:
            status, mime, length = probe(url)
            time.sleep(0.2)
        manifest.append({
            "rapor_referans_ayi": label, "yayin_tarihi": "", "kaynak_url": url,
            "http_durumu": status, "mime_type": mime, "content_length": length,
            "dosya_tipi": "pdf", "rapor_turu": "official_odmd_annual_archive",
            "extraction_durumu": "annual_context_only", "kontrol_zamani_utc": checked,
            "not": "Aylik seri yerine yil sonu toplamlarini ve metodoloji surekliligini denetlemek icin tutuldu.",
        })
    write_csv(OUT / "indicata_manifest.csv", manifest)
    print(f"OK: {len(ROWS)} monthly rows, {len(manifest)} manifest rows")


if __name__ == "__main__":
    main()
