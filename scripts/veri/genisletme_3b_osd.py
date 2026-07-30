"""
GENIŞLETME AŞAMA 3b — OSD (Otomotiv Sanayii Derneği) yerli üretim adetleri,
2024-01 -> bugün (kaynak seviyesi A, TCMB EVDS3).

ONCEKI DENEME (PM raporu pm_rapor_genisletme_asama2_5.md, Bolum 3.3): OSD'nin
kendi web sitesinde ODMD'dekine benzer bir "coklu-yil ozet PDF" bulunamamisti,
bu kalem HATA LISTESINE birakilmisti.

COZUM (bu turda): EVDS3 web arayuzunde ("Tum Seriler > Reel Sektor
Istatistikleri > Uretime Iliskin Diger Veriler > Otomotiv Sanayii Uretimi
(OSD)") TCMB'nin OSD verisini KENDI API'SINDEN dogrudan yayimladigi
gorulmustur - PDF taramaya HIC gerek kalmadi.

Seriler (arac tipine gore kirilim; ODMD'nin "otomobil + hafif ticari arac"
kapsamina en yakini Binek+Kamyonet):
- TP.UR.S08: Binek (otomobil)
- TP.UR.S11: Kamyonet (hafif ticari arac)
Diger kirilimlar (Cekici, Kamyon, Midibus, Minibus, Otobus, Traktor) bu
projenin kapsamina (K1: yolcu tasitlari piyasasi) girmedigi icin CEKILMEDI.
"""
import os
import sys
import json
from datetime import date
from pathlib import Path

import requests
import pandas as pd

BASLANGIC_AY = "2015-01"
BITIS_AY = date.today().strftime("%Y-%m")

EVDS_BASE_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
SERIES = {
    "osd_binek_adet": "TP.UR.S08",
    "osd_kamyonet_adet": "TP.UR.S11",
}

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "osd"
ENV_PATH = REPO_KOKU / ".env"


def _env_dosyasini_yukle():
    if not ENV_PATH.exists():
        return
    for satir in ENV_PATH.read_text(encoding="utf-8").splitlines():
        satir = satir.strip()
        if not satir or satir.startswith("#") or "=" not in satir:
            continue
        anahtar, deger = satir.split("=", 1)
        os.environ.setdefault(anahtar.strip(), deger.strip())


def _ay_baslangic_bitis_tarihleri(baslangic_ay: str, bitis_ay: str) -> tuple[str, str]:
    b_yil, b_ay = (int(x) for x in baslangic_ay.split("-"))
    e_yil, e_ay = (int(x) for x in bitis_ay.split("-"))
    ay_sonu_gun = pd.Period(f"{e_yil:04d}-{e_ay:02d}", freq="M").days_in_month
    start_date = f"01-{b_ay:02d}-{b_yil:04d}"
    end_date = f"{ay_sonu_gun:02d}-{e_ay:02d}-{e_yil:04d}"
    return start_date, end_date


def evds_aylik_seri_cek(api_key: str, seriler: list[str], baslangic_ay: str, bitis_ay: str):
    start_date, end_date = _ay_baslangic_bitis_tarihleri(baslangic_ay, bitis_ay)
    params = {"series": "-".join(seriler), "startDate": start_date, "endDate": end_date, "type": "json"}
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = EVDS_BASE_URL + query
    try:
        resp = requests.get(url, headers={"key": api_key}, timeout=60)
    except requests.RequestException as exc:
        print(f"[HATA] EVDS istegi basarisiz: {exc}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"[HATA] EVDS HTTP {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        return None
    try:
        payload = resp.json()
    except ValueError:
        print(f"[HATA] EVDS yaniti JSON degil: {resp.text[:300]}", file=sys.stderr)
        return None
    if "items" not in payload:
        print(f"[HATA] EVDS yanitinda 'items' yok: {payload}", file=sys.stderr)
        return None
    return payload


def main():
    _env_dosyasini_yukle()
    api_key = os.environ.get("EVDS_API_KEY")
    if not api_key:
        print("[HATA] EVDS_API_KEY bulunamadi.", file=sys.stderr)
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    payload = evds_aylik_seri_cek(api_key, list(SERIES.values()), BASLANGIC_AY, BITIS_AY)
    if payload is None:
        print("[UYARI] Veri cekilemedi.")
        sys.exit(1)

    ham_path = RAW_DIR / "osd_2024_bugun_raw.json"
    with open(ham_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(payload["items"])
    df = df.drop(columns=["UNIXTIME"], errors="ignore")
    kolon_haritasi = {kod.replace(".", "_"): ad for ad, kod in SERIES.items()}
    df = df.rename(columns={"Tarih": "tarih", **kolon_haritasi})
    for ad in SERIES:
        df[ad] = pd.to_numeric(df[ad], errors="coerce")
    yil_ay = df["tarih"].str.split("-", n=1, expand=True)
    df["referans_ayi"] = yil_ay[0] + "-" + yil_ay[1].str.zfill(2)
    df = df.sort_values("referans_ayi").reset_index(drop=True)
    df["osd_binek_kamyonet_toplam_adet"] = df["osd_binek_adet"] + df["osd_kamyonet_adet"]

    kolon_sirasi = ["referans_ayi", "osd_binek_adet", "osd_kamyonet_adet", "osd_binek_kamyonet_toplam_adet"]
    df = df[kolon_sirasi]

    hedef_csv = RAW_DIR / "osd_2024_bugun_aylik.csv"
    hedef_xlsx = RAW_DIR / "osd_2024_bugun_aylik.xlsx"
    df.to_csv(hedef_csv, index=False, encoding="utf-8-sig")
    df.to_excel(hedef_xlsx, index=False, sheet_name="osd_aylik")

    beklenen_aylar = pd.period_range(BASLANGIC_AY, BITIS_AY, freq="M").astype(str).tolist()
    gelen_aylar = df["referans_ayi"].tolist()
    eksik_aylar = [ay for ay in beklenen_aylar if ay not in gelen_aylar]

    print("=== GENISLETME 3b - OSD URETIM OZETI ===")
    print(f"Kapsam: {BASLANGIC_AY} .. {BITIS_AY}")
    print(f"Gelen ay: {len(gelen_aylar)}/{len(beklenen_aylar)}, eksik: {eksik_aylar if eksik_aylar else 'yok'}")
    print(df.to_string(index=False))
    print(f"\nCikti: {hedef_csv} , {hedef_xlsx}")


if __name__ == "__main__":
    main()
