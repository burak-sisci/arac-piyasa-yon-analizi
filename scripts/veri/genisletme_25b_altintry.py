"""
GENIŞLETME AŞAMA 25b — Külçe Altın (TL/Gr) satış fiyatı, 2015-01 -> bugün.

(prompts/veri/25_gunluk_eur_altin_karisik_frekans_prompt.md, Görev 1-2)

GÖREV 1 SONUCU — ÖNEMLİ SAPMA (proaktif bildirim): Görev talimatı altını
"doğası gereği günlük" bir kaynak olarak varsayıyordu (döviz kurları gibi).
TCMB EVDS'te (mevcut EVDS_API_KEY ile, YENİ ANAHTAR GEREKMEDEN) erişilen
TEK gram-altın/TL serisi — "Altın Fiyatları (Ankara Kuyumcular ve Saatçiler
Odası)" grubu, kod TP.MK.KUL.YTL — sitenin kendi arayüzünde AÇIKÇA "(Aylık)"
olarak etiketlenmiştir ve dönen veri noktalarının Tarih alanı da bunu
doğrular ("2015-1", "2015-2" gibi - gün bilgisi YOK, tam bir ay damgası).
EVDS'in "DİĞER KIYMETLİ MADENLER VE EMTİA PİYASASI" kategorisinde yalnızca
Brent petrol fiyatı var, başka bir altın serisi YOK; kısa bir WebSearch
taraması da TCMB dışında genel-amaçlı, resmi/güvenilir, ücretsiz GÜNLÜK
bir TL/gram altın kaynağı ortaya çıkarmadı (zaman-maliyeti gözetilerek
derinlemesine aranmadı, bkz. PM raporu Görev 5).

SONUÇ: Bu script GÜNLÜK değil, kaynağın GERÇEK doğal frekansıyla (AYLIK)
veri üretir — görev talimatının "günlük tabloya nasıl dahil edilecek"
ilkesine göre bu seri data/raw/eurtry (günlük) ile AYNI kovaya değil,
TÜFE/ENAG/noter devri gibi AYLIK kaynaklar kovasına girer (Görev 3/4'te
böyle işlenir).

Diğer aylık EVDS serileri (TÜFE, OSD, tüketici güveni) gibi TEK bir
istekle çekilir - 137 satır, 1000-satır sınırının çok altında, chunking
gerekmez.
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
SERI_KODU = "TP.MK.KUL.YTL"  # Kulce Altin Satis Fiyati (TL/Gr), Ankara Kuyumcular ve Saatciler Odasi

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "altintry"
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


def main():
    _env_dosyasini_yukle()
    api_key = os.environ.get("EVDS_API_KEY")
    if not api_key:
        print("[HATA] EVDS_API_KEY bulunamadi.", file=sys.stderr)
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    start_date, end_date = _ay_baslangic_bitis_tarihleri(BASLANGIC_AY, BITIS_AY)
    params = {"series": SERI_KODU, "startDate": start_date, "endDate": end_date, "type": "json"}
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = EVDS_BASE_URL + query
    try:
        resp = requests.get(url, headers={"key": api_key}, timeout=60)
    except requests.RequestException as exc:
        print(f"[HATA] EVDS istegi basarisiz: {exc}", file=sys.stderr)
        sys.exit(1)
    if resp.status_code != 200:
        print(f"[HATA] EVDS HTTP {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        sys.exit(1)
    payload = resp.json()
    if "items" not in payload or not payload["items"]:
        print("[HATA] EVDS yanitinda veri yok.", file=sys.stderr)
        sys.exit(1)
    if len(payload["items"]) >= 1000:
        print("[UYARI] 1000+ satir dondu, veri kirpilmis olabilir - chunking gerekebilir.", file=sys.stderr)

    ham_path = RAW_DIR / "altintry_2015_bugun_raw.json"
    with open(ham_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    df = pd.DataFrame(payload["items"])
    df = df.rename(columns={"Tarih": "tarih_evds", "TP_MK_KUL_YTL": "altin_gram_try"})
    df = df.drop(columns=["UNIXTIME"], errors="ignore")
    df["altin_gram_try"] = pd.to_numeric(df["altin_gram_try"], errors="coerce")

    # EVDS "2015-1" formatinda ay damgasi donduruyor (gun bilgisi yok - dogal
    # aylik seri oldugunun bir kaniti daha). referans_ayi = "YYYY-MM".
    yil_ay = df["tarih_evds"].str.split("-", n=1, expand=True)
    df["referans_ayi"] = yil_ay[0] + "-" + yil_ay[1].str.zfill(2)
    df = df.sort_values("referans_ayi").reset_index(drop=True)

    # as-of gunu: kaynagin GERCEK yayim tarihi belgelenmedigi icin, seffaf bir
    # varsayimla ayin SON GUNU olarak sabitleniyor (bu bir tahmin degil, acikca
    # belgelenen bir ANKORLAMA kurali - Gorev 4'te bu sutun kullanilacak).
    df["as_of_ay_sonu"] = pd.PeriodIndex(df["referans_ayi"], freq="M").to_timestamp(how="end").normalize()

    kolon_sirasi = ["referans_ayi", "as_of_ay_sonu", "altin_gram_try"]
    df = df[kolon_sirasi]

    aylik_csv = RAW_DIR / "altintry_aylik_2015_bugun.csv"
    aylik_xlsx = RAW_DIR / "altintry_aylik_2015_bugun.xlsx"
    df.to_csv(aylik_csv, index=False, encoding="utf-8-sig")
    df.to_excel(aylik_xlsx, index=False, sheet_name="altintry_aylik")

    beklenen_aylar = pd.period_range(BASLANGIC_AY, BITIS_AY, freq="M").astype(str).tolist()
    gelen_aylar = df["referans_ayi"].tolist()
    eksik_aylar = [ay for ay in beklenen_aylar if ay not in gelen_aylar]

    print("=== GENISLETME 25b - ALTIN/TRY (AYLIK) OZET ===")
    print("!! DIKKAT: bu kaynak GUNLUK DEGIL, AYLIK - bkz. script docstring'i !!")
    print(f"Kapsam: {BASLANGIC_AY} .. {BITIS_AY}")
    print(f"Aylik satir: {len(df)}/{len(beklenen_aylar)}")
    print(f"Eksik aylar: {eksik_aylar if eksik_aylar else 'yok'}")
    print(df.head(3).to_string(index=False))
    print(df.tail(3).to_string(index=False))
    print(f"\nCikti: {aylik_csv} , {aylik_xlsx}")


if __name__ == "__main__":
    main()
