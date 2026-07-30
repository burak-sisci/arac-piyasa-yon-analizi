"""
GENIŞLETME AŞAMA 2b — Alım gücü proxy'si (brüt ücret-maaş endeksi),
2018-01 -> 2026-06 (kaynak seviyesi B — resmi TÜİK indirilebilir tablosu).

ONCEKI DENEME (pm_rapor_genisletme_asama2_5.md, Bolum 3.1): TÜİK veri portali
WebFetch ile okunamiyordu - HATA LISTESINE birakilmisti.

COZUM (ilk tur): TÜİK veri portali JS render eden tarayici araciyla
gezilerek "İstihdam, İşsizlik ve Ücret > İşgücü Girdi Endeksleri" bulteninde
(en guncel: "I. Çeyrek: Ocak-Mart 2026", Sayı 57966) "Dinamik Tablolar"
bolumunden indirilen "İşgücü Girdi Endeksleri (2021=100).xls" tablosu
bulundu. BU TEK TABLO 2009-2026 arasi TAM CEYREKLIK TARIHCEYI icerir (ODMD
tarzi cok-yillik tablo - tek belge yeterli oldu, noter devir'deki gibi 2.
bir belgeye gerek kalmadi). Ilk turda yalnizca 2024-Q1..2026-Q1 cikarilmisti.

GENISLETME (2. tur, 2018-2023 ekleme): AYNI URL / AYNI .xls tablosu tekrar
indirildi (JS render eden tarayici uzerinden bulten sayfasi acildi, "Dinamik
Tablolar" bolumundeki "İşgücü Girdi Endeksleri (2021=100)" linki --
/api/tr/data/downloads?... -- dogrudan herkese acik, oturum/cerez gerektirmeyen
bir uc nokta oldugu curl ile dogrulandi; indirilen .xls, pandas.read_excel ile
"t1" sayfasindan okunup B-N (Sanayi+insaat+ticaret-hizmet toplami) blogundaki
19. sutun ("Brüt ücret-maaş endeksi, Arındırılmamış") cekildi). 2024-Q1..
2026-Q1 icin cikan degerler, ilk turda elle girilmis olan degerlerle BIREBIR
AYNI cikti (ornegin 2024-Q1 = 693.111053) - bu, sutun/blok secimini ve
tablonun ayni kaynak/surum oldugunu dogrular. Boylece 2018-Q1..2023-Q4
(24 ceyrek) icin GERCEK degerler (uydurma/interpolasyon degil) ayni tablodan
eklendi.

DEGISKEN SECIMI: "Brüt ücret-maaş endeksi" (Arındırılmamış, B-N toplam
sektor: sanayi+insaat+ticaret-hizmet), NOMINAL bir ucret endeksidir
(2021=100). "Alim gucu" (satin alma gucu) icin bu, TÜFE'ye bolunerek
(reel deflate) kullanilmalidir - o hesaplama BU SCRIPT'TE YAPILMAZ (asama5
tarzi etiketleme/turetme adiminin isi), burada yalnizca HAM nominal endeks
CEKILIR.

2015-01'E GENISLETME DENEMESI (2026-07-30, BASARISIZ - ACIK BLOKAJ):
Ayni tablonun (2009-2026 tarihce) 2015-Q1..2017-Q4 satirlarini cekmek icin
TÜİK veri portali tekrar denendi, AMA bu turda "İşgücü Girdi Endeksleri
(2021=100)" indirme linki artik bir SPA (React) client-side route olarak
davraniyor - ne dogrudan curl/WebFetch (SPA kabugu HTML'i donuyor, gercek
.xls degil) ne de tarayici araciyla tiklama (network loglarinda YENI bir
istek tetiklenmiyor, site muhtemelen farkli bir indirme mekanizmasi -
blob/JS-taraf olusturma - kullaniyor) calisti. Onceki basarili turda
belgelenen "/api/tr/data/downloads?..." dogrudan uc noktasi bu oturumda
bulunamadi (site guncellenmis olabilir). WebSearch ile ikincil kaynak
aramasi da 2015-2017 icin bu spesifik ceyreklik rakamlari getirmedi.
SONUC: brut_ucret_maas_endeksi_2021_100 ve ondan tureyen erisim_endeksi
2015-2017 icin GENISLETILEMEDI, 2018-01'de baslamaya devam ediyor - bu bir
veri kaybi/hata degil, bu oturumdaki bir ERISIM ENGELIDIR (bkz.
pm_rapor_genisletme_2015.md, acik sorular).

FREKANS UYARISI (onemli, ay bazinda okurken dikkat): Bu veri ÇEYREKLIKTIR
(TÜİK bu anketi aylik degil, ceyreklik yayimlar). Aylik veri setine
eklenebilmesi icin HER CEYREGIN degeri, o ceyregin 3 ayina da AYNEN
TEKRARLANARAK (forward-fill benzeri, gercek aylik varyasyon UYDURULMADAN)
atanmistir - bu KESINLIKLE ay-ay degisim gostermez, yalnizca ceyrek-ceyrek
degisim yansitir. proxy_yayim_ayi mantigina benzer sekilde, `alim_gucu_ceyrek`
sutunu hangi ceyregin degeri oldugunu acikca isaretler (sizinti/karistirma
riskini onlemek icin).

KAPSAM SINIRI: 2026-Q2 (Nisan-Haziran) HENUZ YAYIMLANMADI (bir sonraki
bulten 21 Agustos 2026) - bu yuzden 2026-04, 2026-05, 2026-06 icin bu
degisken NaN'dir (yapisal/normal gecikme, diger serilerdeki 2026-07 NaN'i
gibi).
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_KOKU / "data" / "raw" / "alim_gucu"

# TÜİK "İşgücü Girdi Endeksleri (2021=100)" tablosunun B-N (toplam: sanayi+
# insaat+ticaret-hizmet) blogundan, "Brüt ücret-maaş endeksi (Arındırılmamış)"
# sutunundan birebir okunmustur.
KAYNAK_URL = "https://veriportali.tuik.gov.tr/tr/press/57966"  # İşgücü Girdi Endeksleri, I. Çeyrek 2026
CEYREK_DEGERLERI = {
    "2018-Q1": 55.077816,
    "2018-Q2": 56.141908,
    "2018-Q3": 57.799243,
    "2018-Q4": 57.641475,
    "2019-Q1": 63.311002,
    "2019-Q2": 66.580759,
    "2019-Q3": 68.769237,
    "2019-Q4": 69.595474,
    "2020-Q1": 74.415656,
    "2020-Q2": 61.235986,
    "2020-Q3": 73.433920,
    "2020-Q4": 77.724019,
    "2021-Q1": 87.049290,
    "2021-Q2": 93.567483,
    "2021-Q3": 105.637307,
    "2021-Q4": 113.745919,
    "2022-Q1": 146.177172,
    "2022-Q2": 162.872867,
    "2022-Q3": 212.872438,
    "2022-Q4": 230.426190,
    "2023-Q1": 320.122159,
    "2023-Q2": 344.355578,
    "2023-Q3": 455.890230,
    "2023-Q4": 486.201924,
    "2024-Q1": 693.111053,
    "2024-Q2": 741.916146,
    "2024-Q3": 796.607993,
    "2024-Q4": 839.337735,
    "2025-Q1": 1002.940987,
    "2025-Q2": 1069.033682,
    "2025-Q3": 1116.447515,
    "2025-Q4": 1147.643883,
    "2026-Q1": 1374.314470,
    # 2026-Q2: HENUZ YAYIMLANMADI (bir sonraki bulten 21 Agustos 2026)
}

CEYREK_AYLARI = {
    "Q1": ["01", "02", "03"],
    "Q2": ["04", "05", "06"],
    "Q3": ["07", "08", "09"],
    "Q4": ["10", "11", "12"],
}


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    satirlar = []
    for ceyrek_anahtari, deger in CEYREK_DEGERLERI.items():
        yil, ceyrek = ceyrek_anahtari.split("-")
        for ay in CEYREK_AYLARI[ceyrek]:
            satirlar.append(dict(
                referans_ayi=f"{yil}-{ay}",
                brut_ucret_maas_endeksi_2021_100=deger,
                alim_gucu_ceyrek=ceyrek_anahtari,
            ))

    df = pd.DataFrame(satirlar).sort_values("referans_ayi").reset_index(drop=True)
    df = df[(df["referans_ayi"] >= "2018-01") & (df["referans_ayi"] <= "2026-06")]
    df["kaynak_url"] = KAYNAK_URL

    # DOSYA ADI DEGISTI (2024_bugun -> 2018_bugun): kapsam 2018-01'e genisletildi,
    # bu odmd/usdtry serilerindeki "_2018_bugun_" adlandirma kalibiyla tutarlidir.
    # Eski "alim_gucu_2024_bugun_aylik.*" dosyalari artik gecersiz/eksik kapsamli
    # oldugundan silinir (GÖREV 3 - genisletme_5_birlestir.py - bu yeni dosya adini
    # kullanacak sekilde ayrica guncellenmelidir).
    eski_csv = RAW_DIR / "alim_gucu_2024_bugun_aylik.csv"
    eski_xlsx = RAW_DIR / "alim_gucu_2024_bugun_aylik.xlsx"
    for eski in (eski_csv, eski_xlsx):
        if eski.exists():
            eski.unlink()

    hedef_csv = RAW_DIR / "alim_gucu_2018_bugun_aylik.csv"
    hedef_xlsx = RAW_DIR / "alim_gucu_2018_bugun_aylik.xlsx"
    df.to_csv(hedef_csv, index=False, encoding="utf-8-sig")
    df.to_excel(hedef_xlsx, index=False, sheet_name="alim_gucu_aylik")

    beklenen_aylar = pd.period_range("2018-01", "2026-06", freq="M").astype(str).tolist()
    gelen_aylar = df["referans_ayi"].tolist()
    eksik_aylar = [ay for ay in beklenen_aylar if ay not in gelen_aylar]

    print("=== GENISLETME 2b - ALIM GUCU PROXY'Sİ (BRUT UCRET-MAAS ENDEKSI) OZETI ===")
    print("Kaynak seviyesi: B (resmi TÜİK indirilebilir .xls tablosu, ceyreklik -> aylik genisletildi)")
    print(f"Kapsam: 2018-01 .. 2026-06 ({len(df)} satir)")
    print(f"Eksik ay: {eksik_aylar if eksik_aylar else 'yok'} (2026-Q2 henuz yayimlanmadi)")
    print()
    print(df.to_string(index=False))
    print(f"\nCikti: {hedef_csv} , {hedef_xlsx}")


if __name__ == "__main__":
    main()
