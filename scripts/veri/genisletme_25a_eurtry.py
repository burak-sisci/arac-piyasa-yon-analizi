"""
GENIŞLETME AŞAMA 25a — EUR/TRY kur verisi, 2015-01 -> bugün (kaynak seviyesi A).

(prompts/veri/25_gunluk_eur_altin_karisik_frekans_prompt.md, Görev 1-2)

GÖREV 1 SONUCU: EUR/TRY, mevcut EVDS_API_KEY ile (USD/TRY'yi çeken aynı
anahtar) doğrudan çekilebildi — YENİ ANAHTAR GEREKMEDİ. Seri kodları
TP.DK.EUR.A (alış) / TP.DK.EUR.S (satış), USD/TRY'nin TP.DK.USD.A/S
kodlarıyla birebir aynı desende. Bir deneme çağrısıyla (2026-07 ayı)
doğrulandı.

Bu script, genisletme_1a_usdtry.py ile AYNI mantığı (tarih-parçalama/
chunking, EVDS'in 1000-satır sessiz kesme davranışına karşı) izler -
DOĞASI GEREĞİ GÜNLÜK bir kaynak, forward-fill YOK, gerçek günlük değerler.
"""
import os
import sys
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
import pandas as pd

BASLANGIC_AY = "2015-01"
BITIS_AY = date.today().strftime("%Y-%m")

EVDS_BASE_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
SERIES = ["TP.DK.EUR.A", "TP.DK.EUR.S"]
EVDS_MAX_GUN_PARCA = 700

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "eurtry"
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
    bugun = date.today()
    if e_yil == bugun.year and e_ay == bugun.month:
        end_date = bugun.strftime("%d-%m-%Y")
    else:
        ay_sonu_gun = pd.Period(f"{e_yil:04d}-{e_ay:02d}", freq="M").days_in_month
        end_date = f"{ay_sonu_gun:02d}-{e_ay:02d}-{e_yil:04d}"
    start_date = f"01-{b_ay:02d}-{b_yil:04d}"
    return start_date, end_date


def _tarih_araliklarini_parcala(start_date: str, end_date: str, gun_araligi: int = EVDS_MAX_GUN_PARCA):
    start = datetime.strptime(start_date, "%d-%m-%Y").date()
    end = datetime.strptime(end_date, "%d-%m-%Y").date()
    araliklar = []
    cur = start
    while cur <= end:
        parca_bitis = min(cur + timedelta(days=gun_araligi - 1), end)
        araliklar.append((cur.strftime("%d-%m-%Y"), parca_bitis.strftime("%d-%m-%Y")))
        cur = parca_bitis + timedelta(days=1)
    return araliklar


def _evds_tek_istek(api_key: str, seriler: list[str], start_date: str, end_date: str):
    params = {"series": "-".join(seriler), "startDate": start_date, "endDate": end_date, "type": "json"}
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = EVDS_BASE_URL + query
    try:
        resp = requests.get(url, headers={"key": api_key}, timeout=60)
    except requests.RequestException as exc:
        print(f"[HATA] EVDS istegi basarisiz ({start_date}..{end_date}): {exc}", file=sys.stderr)
        return None
    if resp.status_code != 200:
        print(f"[HATA] EVDS HTTP {resp.status_code} ({start_date}..{end_date}): {resp.text[:300]}", file=sys.stderr)
        return None
    try:
        payload = resp.json()
    except ValueError:
        print(f"[HATA] EVDS yaniti JSON degil ({start_date}..{end_date}): {resp.text[:300]}", file=sys.stderr)
        return None
    if "items" not in payload:
        print(f"[HATA] EVDS yanitinda 'items' yok ({start_date}..{end_date}): {payload}", file=sys.stderr)
        return None
    return payload


def evds_gunluk_seri_cek(api_key: str, seriler: list[str], baslangic_ay: str, bitis_ay: str):
    start_date, end_date = _ay_baslangic_bitis_tarihleri(baslangic_ay, bitis_ay)
    araliklar = _tarih_araliklarini_parcala(start_date, end_date)

    tum_items = []
    tum_tarihler_gorulen = set()
    for parca_start, parca_end in araliklar:
        print(f"[BILGI] EVDS istegi: {parca_start} .. {parca_end}")
        parca_payload = _evds_tek_istek(api_key, seriler, parca_start, parca_end)
        if parca_payload is None:
            print(f"[HATA] Parca basarisiz, genisletme durduruluyor: {parca_start}..{parca_end}", file=sys.stderr)
            return None
        parca_itemlar = parca_payload.get("items", [])
        if len(parca_itemlar) >= 1000:
            print(
                f"[UYARI] {parca_start}..{parca_end} tam 1000+ satir dondurdu "
                f"({len(parca_itemlar)}) - veri kirpilmis olabilir.",
                file=sys.stderr,
            )
        for item in parca_itemlar:
            tarih = item.get("Tarih")
            if tarih in tum_tarihler_gorulen:
                continue
            tum_tarihler_gorulen.add(tarih)
            tum_items.append(item)

    if not tum_items:
        return None
    return {"totalCount": len(tum_items), "items": tum_items}


def main():
    _env_dosyasini_yukle()
    api_key = os.environ.get("EVDS_API_KEY")
    if not api_key:
        print("[HATA] EVDS_API_KEY bulunamadi.", file=sys.stderr)
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    payload = evds_gunluk_seri_cek(api_key, SERIES, BASLANGIC_AY, BITIS_AY)
    if payload is None:
        print("[UYARI] Veri cekilemedi.")
        sys.exit(1)

    ham_path = RAW_DIR / "eurtry_2015_bugun_raw.json"
    with open(ham_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(payload["items"])
    df = df.rename(columns={"Tarih": "tarih", "TP_DK_EUR_A": "eurtry_alis", "TP_DK_EUR_S": "eurtry_satis"})
    df = df.drop(columns=["UNIXTIME"], errors="ignore")
    df["tarih"] = pd.to_datetime(df["tarih"], format="%d-%m-%Y")
    df["eurtry_alis"] = pd.to_numeric(df["eurtry_alis"], errors="coerce")
    df["eurtry_satis"] = pd.to_numeric(df["eurtry_satis"], errors="coerce")
    df["eurtry_orta"] = (df["eurtry_alis"] + df["eurtry_satis"]) / 2
    df = df.sort_values("tarih").reset_index(drop=True)

    gunluk_csv = RAW_DIR / "eurtry_gunluk_2015_bugun.csv"
    gunluk_xlsx = RAW_DIR / "eurtry_gunluk_2015_bugun.xlsx"
    df.to_csv(gunluk_csv, index=False, encoding="utf-8-sig")
    df.to_excel(gunluk_xlsx, index=False, sheet_name="eurtry_gunluk")

    print("=== GENISLETME 25a - EUR/TRY GUNLUK OZET ===")
    print(f"Kapsam: {BASLANGIC_AY} .. {BITIS_AY}")
    print(f"Gunluk gozlem: {len(df)}")
    print(f"Ilk tarih: {df['tarih'].min()}, son tarih: {df['tarih'].max()}")
    print(df.head(3).to_string(index=False))
    print(df.tail(3).to_string(index=False))
    print(f"\nCikti: {gunluk_csv} , {gunluk_xlsx}")


if __name__ == "__main__":
    main()
