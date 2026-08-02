"""
GENIŞLETME AŞAMA 1a — USD/TRY kur verisi, 2018-01 -> bugün (kaynak seviyesi A).

MVP (yalnızca 2025) scriptinden (scripts/veri/asama1_usdtry.py) FARKLI ÇIKTI
DOSYALARINA yazar - MVP ciktilarinin uzerine YAZMAZ, o prototip asamasi ayri
kaydedilmis olarak kalir.

Kullanim: EVDS_API_KEY ortam degiskeni / .env (Asama 1 ile ayni).

Not (2026-07-27, 2018-01 genisletmesi sirasinda kesfedildi): EVDS3 API tek
istekte en fazla 1000 SATIR (gunluk gozlem) donduruyor - "totalCount" alani
1000'i gecmiyor ve istenen tarih araligi 1000 gunden uzunsa API HATA VERMEDEN
sessizce yalnizca aralijin EN SON (en guncel) 1000 gununu donduruyor, daha eski
gunleri sessizce dusuruyor (dogrudan evds3.tcmb.gov.tr'ye karsi 3 ayri test
istegiyle dogrulandi: 2018 tek yil -> totalCount=365 tam; 2018-2019 -> 730 tam;
2018-2020 -> totalCount=1000 ve donen ilk gun 07-04-2018 idi, yani 2018-01/02/03
sessizce dusmustu). Bu yuzden asagida genel istenen araligi <=~2 yillik
(<=700 gunluk) parcalara bolup ayri ayri cekiyoruz ve birlestiriyoruz.

DUZELTME (2026-07-31): BASLANGIC_AY daha once (2015 genisletmesi sirasinda)
"2018-01" -> "2015-01" olarak degistirilmis ama cikti dosya adlari yanlislikla
"_2018_bugun_" olarak kalmisti (diger script'lerde - odmd, noter_devir, otv -
yapilan yeniden adlandirma burada atlanmisti). Bu turda duzeltildi:
"_2018_bugun_" -> "_2015_bugun_". AYRICA kullanicinin talebiyle GUNLUK
periyottaki tablo (usdtry_..._gunluk.csv/.xlsx) ARTIK URETILMIYOR/KAYDEDILMIYOR
- yalnizca AYLIK tablo disariya yaziliyor (gunluk veri hala API'den cekiliyor
ve aylik ortalamayi hesaplamak icin yerelde kullaniliyor, sadece ayri bir
dosya olarak persist edilmiyor). Ham gunluk API yaniti (raw.json) audit/
izlenebilirlik amaciyla korunuyor (projedeki diger script'lerle tutarli).
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
SERIES = ["TP.DK.USD.A", "TP.DK.USD.S"]
EVDS_MAX_GUN_PARCA = 700  # API'nin ~1000 satir/istek sinirinin altinda guvenli pay

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "usdtry"
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
    """dd-mm-yyyy formatinda start/end araligini <= gun_araligi gunluk, ust uste
    binmeyen ardisik parcalara boler. EVDS'in ~1000 satir/istek sinirini asmamak icin."""
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
    params = {
        "series": "-".join(seriler),
        "startDate": start_date,
        "endDate": end_date,
        "type": "json",
    }
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
    """Istenen ay araligini EVDS'in ~1000 satir/istek sinirinin altinda kalacak
    parcalara bolup ayri ayri ceker, sonuclari tek bir payload'da birlestirir.
    (Bkz. dosya basindaki not: tek istekte 1000 gunu asan araliklar sessizce
    yalnizca en son 1000 gunu donduruyor.)"""
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
        parca_items = parca_payload.get("items", [])
        if len(parca_items) >= 1000:
            print(
                f"[UYARI] Parca {parca_start}..{parca_end} tam 1000+ satir dondurdu "
                f"({len(parca_items)}) - EVDS_MAX_GUN_PARCA kucultulmesi gerekebilir, "
                f"veri kirpilmis olabilir.",
                file=sys.stderr,
            )
        for item in parca_items:
            tarih = item.get("Tarih")
            if tarih in tum_tarihler_gorulen:
                continue  # parca siniri ust uste binmesi ihtimaline karsi guvenlik
            tum_tarihler_gorulen.add(tarih)
            tum_items.append(item)

    return {"totalCount": len(tum_items), "items": tum_items}


def main():
    _env_dosyasini_yukle()
    api_key = os.environ.get("EVDS_API_KEY")
    if not api_key:
        print("[HATA] EVDS_API_KEY bulunamadi.", file=sys.stderr)
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # ESKI DOSYALAR (yanlis "_2018_bugun_" adi + artik uretilmeyen gunluk
    # tablo) varsa silinir.
    eski_dosyalar = [
        "usdtry_2018_bugun_aylik.csv", "usdtry_2018_bugun_aylik.xlsx",
        "usdtry_2018_bugun_gunluk.csv", "usdtry_2018_bugun_gunluk.xlsx",
        "usdtry_2018_bugun_raw.json",
        "usdtry_2015_bugun_gunluk.csv", "usdtry_2015_bugun_gunluk.xlsx",
    ]
    for ad in eski_dosyalar:
        eski = RAW_DIR / ad
        if eski.exists():
            eski.unlink()

    payload = evds_gunluk_seri_cek(api_key, SERIES, BASLANGIC_AY, BITIS_AY)
    if payload is None:
        print("[UYARI] Veri cekilemedi.")
        sys.exit(1)

    ham_path = RAW_DIR / "usdtry_2015_bugun_raw.json"
    with open(ham_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(payload["items"])
    df = df.rename(columns={"Tarih": "tarih", "TP_DK_USD_A": "usdtry_alis", "TP_DK_USD_S": "usdtry_satis"})
    df = df.drop(columns=["UNIXTIME"], errors="ignore")
    df["tarih"] = pd.to_datetime(df["tarih"], format="%d-%m-%Y")
    df["usdtry_alis"] = pd.to_numeric(df["usdtry_alis"], errors="coerce")
    df["usdtry_satis"] = pd.to_numeric(df["usdtry_satis"], errors="coerce")
    df["usdtry_orta"] = (df["usdtry_alis"] + df["usdtry_satis"]) / 2
    df = df.sort_values("tarih").reset_index(drop=True)
    df["referans_ayi"] = df["tarih"].dt.to_period("M").astype(str)

    gunluk_dolu = df.dropna(subset=["usdtry_alis", "usdtry_satis"])

    # NOT: gunluk tablo (usdtry_..._gunluk.csv/.xlsx) ARTIK AYRI DOSYA OLARAK
    # KAYDEDILMIYOR (kullanici talebi) - gunluk veri yalnizca yereldeki aylik
    # ortalama/aysonu hesaplamasi icin kullanilir, disariya yazilmaz. Ham
    # gunluk API yaniti audit icin usdtry_2015_bugun_raw.json'da duruyor.

    aylik_ortalama = gunluk_dolu.groupby("referans_ayi")[["usdtry_alis", "usdtry_satis", "usdtry_orta"]].mean()
    aylik_ortalama = aylik_ortalama.rename(columns={
        "usdtry_alis": "usdtry_ortalama_alis", "usdtry_satis": "usdtry_ortalama_satis", "usdtry_orta": "usdtry_ortalama",
    })
    aylik_sonu = gunluk_dolu.sort_values("tarih").groupby("referans_ayi").last()[["usdtry_alis", "usdtry_satis", "usdtry_orta"]]
    aylik_sonu = aylik_sonu.rename(columns={
        "usdtry_alis": "usdtry_aysonu_alis", "usdtry_satis": "usdtry_aysonu_satis", "usdtry_orta": "usdtry_aysonu",
    })
    aylik_birlesik = aylik_sonu.join(aylik_ortalama, how="outer").reset_index().sort_values("referans_ayi").reset_index(drop=True)

    aylik_csv = RAW_DIR / "usdtry_2015_bugun_aylik.csv"
    aylik_xlsx = RAW_DIR / "usdtry_2015_bugun_aylik.xlsx"
    aylik_birlesik.to_csv(aylik_csv, index=False, encoding="utf-8-sig")
    aylik_birlesik.to_excel(aylik_xlsx, index=False, sheet_name="usdtry_aylik")

    beklenen_aylar = pd.period_range(BASLANGIC_AY, BITIS_AY, freq="M").astype(str).tolist()
    gelen_aylar = aylik_birlesik["referans_ayi"].tolist()
    eksik_aylar = [ay for ay in beklenen_aylar if ay not in gelen_aylar]

    print("=== GENISLETME 1a - USD/TRY OZET ===")
    print(f"Kapsam: {BASLANGIC_AY} .. {BITIS_AY}")
    print(f"Gunluk gozlem: {len(df)}, aylik satir: {len(gelen_aylar)}/{len(beklenen_aylar)}")
    print(f"Eksik aylar: {eksik_aylar if eksik_aylar else 'yok'}")
    print(aylik_birlesik.to_string(index=False))


if __name__ == "__main__":
    main()
