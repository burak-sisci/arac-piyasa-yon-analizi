"""
GENIŞLETME AŞAMA 1b — TÜFE verisi, 2024-01 -> bugün (kaynak seviyesi A).

MVP scriptinden (asama2_tufe.py) FARKLI ciktilara yazar; MVP ciktilarinin
uzerine YAZMAZ. 2023-12 taban ayi da cekilir (2024-01'in aylik degisimi icin).

BAZ YILI DEGISIKLIGI (2026-01) VE ZINCIRLEME YONTEMI:
TUIK, Ocak 2026'dan itibaren TUFE baz yilini 2003=100'den 2025=100'e
degistirdi (ECOICOP v2, AB uyumu - kaynak: tcmbblog.org). Eski EVDS kodu
(TP.FG.J0) Ocak 2026'dan sonra guncellenmiyor; yeni kod EVDS3 web arayuzunden
(Tum Seriler > Fiyat Endeksleri > Tuketici Fiyat Endeksi (TUIK) > Tuketici
Fiyat Endeksi (2025=100) > "Genel Endeks") bulunmustur: TP.TUKFIY2025.GENEL
(API ile dogrulandi, 2026-01..06 icin 6/6 gozlem donuyor).

Iki seri FARKLI SAYISAL OLCEKTEDIR (2003=100 vs 2025=100), dogrudan
birlestirilemez. TUIK/istatistik pratiginde standart yontem olan ZINCIRLEME
(chaining) uygulanir: yeni serinin ilk ortak ayi (2026-01) referans alinarak
bir olcek katsayisi hesaplanir (eski_2026_01 / yeni_2026_01) ve yeni serinin
TUM degerleri bu katsayiyla eski olcege tasinir. Bu, sadece bir SAYISAL
OLCEK DONUSUMUDUR - yuzde degisimler (aylik/yillik) matematiksel olarak
DEGISMEZ (bir index'i sabit bir katsayiyla carpmak oransal degisimi etkilemez).
Sonuc: tufe_endeks sutunu 2024-01'den bugune KESINTISIZ ve TUTARLI tek bir
olcekte; ancak MUTLAK DUZEYI artik resmi "2025=100" veya "2003=100" olceginin
HICBIRIYLE birebir eslesmiyor (zincirlenmis/turetilmis bir olcek) - bu
docstring + PM raporunda acikca belirtilir (kural 3: kaynaksiz iddia yasak,
bu bir turetme oldugu icin ayrica isaretlenir).
"""
import os
import sys
import json
from datetime import date
from pathlib import Path

import requests
import pandas as pd

BASLANGIC_AY = "2018-01"  # genisletme hedefi: 2018-01'e kadar geriye git (taban ay, ilk ayin aylik degisimi icin gerekliyse ayrica -1 ay istenir)
BITIS_AY = date.today().strftime("%Y-%m")
HEDEF_BASLANGIC_AY = "2018-01"
HEDEF_BITIS_AY = BITIS_AY

EVDS_BASE_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
SERIES_ESKI = ["TP.FG.J0"]            # 2003=100, Ocak 2026'da kesiliyor
SERIES_YENI = ["TP.TUKFIY2025.GENEL"]  # 2025=100, Ocak 2026'dan itibaren
ORTAK_GECIS_AYI = "2026-01"  # her iki seride de mevcut olan ortak ay (zincirleme referansi)

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "tufe"
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


def _yaklasik_yayim_tarihi(referans_ayi: str) -> str:
    donem = pd.Period(referans_ayi, freq="M") + 1
    return date(donem.year, donem.month, 3).isoformat()


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


def _payload_df_yap(payload: dict, deger_kolonu: str) -> pd.DataFrame:
    df = pd.DataFrame(payload["items"])
    df = df.drop(columns=["UNIXTIME"], errors="ignore")
    orijinal_kolon = [c for c in df.columns if c != "Tarih"][0]
    df = df.rename(columns={"Tarih": "tarih", orijinal_kolon: deger_kolonu})
    df[deger_kolonu] = pd.to_numeric(df[deger_kolonu], errors="coerce")
    yil_ay = df["tarih"].str.split("-", n=1, expand=True)
    df["referans_ayi"] = yil_ay[0] + "-" + yil_ay[1].str.zfill(2)
    return df[["referans_ayi", deger_kolonu]].sort_values("referans_ayi").reset_index(drop=True)


def main():
    _env_dosyasini_yukle()
    api_key = os.environ.get("EVDS_API_KEY")
    if not api_key:
        print("[HATA] EVDS_API_KEY bulunamadi.", file=sys.stderr)
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    payload_eski = evds_aylik_seri_cek(api_key, SERIES_ESKI, BASLANGIC_AY, ORTAK_GECIS_AYI)
    payload_yeni = evds_aylik_seri_cek(api_key, SERIES_YENI, ORTAK_GECIS_AYI, BITIS_AY)
    if payload_eski is None or payload_yeni is None:
        print("[UYARI] Veri cekilemedi.")
        sys.exit(1)

    ham_path = RAW_DIR / "tufe_2024_bugun_raw.json"
    with open(ham_path, "w", encoding="utf-8") as f:
        json.dump({"eski_2003_100_TP_FG_J0": payload_eski,
                    "yeni_2025_100_TP_TUKFIY2025_GENEL": payload_yeni}, f, ensure_ascii=False, indent=2)

    df_eski = _payload_df_yap(payload_eski, "tufe_endeks_ham_2003_100")
    df_yeni = _payload_df_yap(payload_yeni, "tufe_endeks_ham_2025_100")

    # Zincirleme: ORTAK_GECIS_AYI'nde (2026-01) iki seri de mevcut -> olcek katsayisi.
    eski_ortak = df_eski.loc[df_eski["referans_ayi"] == ORTAK_GECIS_AYI, "tufe_endeks_ham_2003_100"]
    yeni_ortak = df_yeni.loc[df_yeni["referans_ayi"] == ORTAK_GECIS_AYI, "tufe_endeks_ham_2025_100"]
    if eski_ortak.empty or yeni_ortak.empty:
        print(f"[HATA] Zincirleme icin ortak ay ({ORTAK_GECIS_AYI}) her iki seride de bulunamadi.", file=sys.stderr)
        sys.exit(1)
    olcek_katsayisi = float(eski_ortak.iloc[0]) / float(yeni_ortak.iloc[0])

    df_eski_kullan = df_eski.rename(columns={"tufe_endeks_ham_2003_100": "tufe_endeks"})
    df_eski_kullan["tufe_baz_kaynagi"] = "TP.FG.J0 (2003=100), ham"
    df_yeni_devam = df_yeni[df_yeni["referans_ayi"] > ORTAK_GECIS_AYI].copy()
    df_yeni_devam["tufe_endeks"] = df_yeni_devam["tufe_endeks_ham_2025_100"] * olcek_katsayisi
    df_yeni_devam["tufe_baz_kaynagi"] = (
        f"TP.TUKFIY2025.GENEL (2025=100) x {olcek_katsayisi:.6f} zincirleme katsayisi"
    )
    df_yeni_devam = df_yeni_devam.drop(columns=["tufe_endeks_ham_2025_100"])

    df = pd.concat([df_eski_kullan, df_yeni_devam], ignore_index=True)
    df = df.sort_values("referans_ayi").reset_index(drop=True)

    df["tufe_aylik_degisim"] = df["tufe_endeks"].pct_change() * 100
    df["tufe_yillik_degisim"] = df["tufe_endeks"].pct_change(12) * 100
    df["yayim_tarihi"] = df["referans_ayi"].map(_yaklasik_yayim_tarihi)

    tam_csv = RAW_DIR / "tufe_2024_bugun_tam_donem.csv"
    tam_xlsx = RAW_DIR / "tufe_2024_bugun_tam_donem.xlsx"
    df.to_csv(tam_csv, index=False, encoding="utf-8-sig")
    df.to_excel(tam_xlsx, index=False, sheet_name="tufe_tam_donem")

    hedef = df[(df["referans_ayi"] >= HEDEF_BASLANGIC_AY) & (df["referans_ayi"] <= HEDEF_BITIS_AY)].copy()
    hedef = hedef[["referans_ayi", "tufe_endeks", "tufe_aylik_degisim", "tufe_yillik_degisim",
                    "yayim_tarihi", "tufe_baz_kaynagi"]].reset_index(drop=True)

    hedef_csv = RAW_DIR / "tufe_2024_bugun_aylik.csv"
    hedef_xlsx = RAW_DIR / "tufe_2024_bugun_aylik.xlsx"
    hedef.to_csv(hedef_csv, index=False, encoding="utf-8-sig")
    hedef.to_excel(hedef_xlsx, index=False, sheet_name="tufe_aylik")

    beklenen_aylar = pd.period_range(HEDEF_BASLANGIC_AY, HEDEF_BITIS_AY, freq="M").astype(str).tolist()
    gelen_aylar = hedef["referans_ayi"].tolist()
    eksik_aylar = [ay for ay in beklenen_aylar if ay not in gelen_aylar]

    print("=== GENISLETME 1b - TUFE OZET ===")
    print(f"Kapsam (hedef): {HEDEF_BASLANGIC_AY} .. {HEDEF_BITIS_AY}")
    print(f"Gelen ay: {len(gelen_aylar)}/{len(beklenen_aylar)}, eksik: {eksik_aylar if eksik_aylar else 'yok'}")
    print(f"Zincirleme katsayisi (TP.FG.J0[{ORTAK_GECIS_AYI}] / TP.TUKFIY2025.GENEL[{ORTAK_GECIS_AYI}]): {olcek_katsayisi:.6f}")
    print(hedef.to_string(index=False))


if __name__ == "__main__":
    main()
