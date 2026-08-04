"""
GENIŞLETME AŞAMA 29 — DF-A / DF-B v3: df_gunluk_forward_fill_2015_bugun.csv
(ay-hizali doldurulmus, 28 nolu gorevde dogrulanmis) kaynagindan iki yeni
DataFrame kurma.

(prompts/29_df_a_df_b_v3_ay_hizali_prompt.md, Gorev 1-6)

TASARIM:
- Gorev 1: TUM "otv" gecen sutunlar (otv_referans_ay, otv_aciklama,
  otv_event_gunu_mu) HER IKI DataFrame'den de bastan disla - kapsama
  testine bile girmiyor.
- Gorev 2 (DF-A): Ankor = noter devri serisinin (toplam_adet vs
  otomobil_adet, hangisi daha erken basliyorsa) ilk dolu AYI. Kapsama
  testi (21 nolu gorevdeki AYNI mantik, AY GRANULERLIGINDE - bkz. asagida
  ONEMLI NOT): her sutunun kendi ilk dolu ayi, ankorun ayina esit ya da
  daha erken mi? Evet -> DF-A'ya alinir, Hayir -> alinmaz.
- Gorev 3 (DF-B): 2024-01-01 -> bugun, TUM sutunlar (ENAG + BETAM dahil,
  otv haric) - kapsama testi UYGULANMAZ.
- Gorev 4: Satir granulerligi GUNLUK kalir, aya indirgeme YOK.

ONEMLI NOT - KAPSAMA TESTI GRANULERLIGI (yorumlayici karar, 20/21 nolu
gorevlerdeki onceki karara tutarli):
Test, sutunun ilk dolu GUNU degil, ilk dolu AYI uzerinden yapiliyor.
Neden: usdtry_alis/eurtry_alis gibi GERCEK gunluk kaynaklarin ilk dolu
gunu 2015-01-02'dir (2015-01-01 Yilbasi tatili, borsa/kur islemi yok) -
bu bir "kaynak boslugu" DEGIL, rutin bir tatil-gunu bosluğu. Gun
granulerliginde test edilseydi bu sutunlar YANLISLIKLA elenirdi. Ay
granulerliginde ikisi de "2015-01" ayinda basliyor, ankorla (noter,
2015-01) esit -> GECER.

Ayni sekilde tufe_aylik_degisim (ilk dolu ay: 2015-02) ve
tufe_yillik_degisim (ilk dolu ay: 2016-01) HESAPLAMA GEREGI bir/oniki
aylik gecikmeyle basliyor (bir onceki ay/yil karsilastirmasi olmadan
hesaplanamazlar) - bu da "kaynak boslugu" degil, YAPISAL bir gecikme.
20 nolu gorevde ayni ayrim yapilmis ve bu sutunlar DF-A'da tutulmustu
(bkz. pm_rapor_sutun_temizlik_korelasyon.md ve sonraki notebook'lar) -
bu script AYNI ayrimi (yorumlayici istisna) uyguluyor: TÜFE'nin KENDI
ana sutunu (tufe_endeks) ankorla ayni ayda basladigi icin, ondan turetilen
degisim sutunlari da DF-A'da tutuluyor, gecikmeleri hesaplama geregi
kabul ediliyor.

BASKA HICBIR SUTUNDE bu istisna uygulanmadi - enag, proxy_fiyat, alim_gucu,
noter_devir_otomobil_adet TAMAMEN farkli/daha sonra baslayan KAYNAKLARDIR
(hesaplama gecikmesi degil, kaynagin kendisi o tarihte yoktu), coverage
testini GERCEKTEN basaramazlar.

Girdi: data/processed/dataframes/df_gunluk_forward_fill_2015_bugun.csv
  (SADECE OKUNUR, degistirilmez)
Cikti:
  data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
  data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
"""
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
DF_DIR = REPO_KOKU / "data" / "processed" / "dataframes"
KAYNAK_CSV = DF_DIR / "df_gunluk_forward_fill_2015_bugun.csv"
DF_A_CSV = DF_DIR / "df_a_v3_noter_penceresi_2015_bugun.csv"
DF_B_CSV = DF_DIR / "df_b_v3_enag_betam_2024_bugun.csv"

# hesaplama geregi (kaynak boslugu DEGIL) daha gec baslayan, istisna uygulanan sutunlar
HESAPLAMA_GECIKMELI_ISTISNA = {"tufe_aylik_degisim", "tufe_yillik_degisim"}

YAPISAL_SUTUNLAR = ["tarih", "yil", "ay", "gun", "ceyrek", "haftanin_gunu", "yilin_gunu"]


def main():
    df = pd.read_csv(KAYNAK_CSV, parse_dates=["tarih"])
    df = df.sort_values("tarih").reset_index(drop=True)

    # ---- GOREV 1: OTV sutunlarini bastan disla ----
    otv_kolonlari = [c for c in df.columns if "otv" in c.lower()]
    print("=== GOREV 1 - OTV DISLAMA ===")
    print("Dislanan sutunlar:", otv_kolonlari)
    print()

    calisma_kolonlari = [c for c in df.columns if c not in otv_kolonlari]

    # ---- her sutunun ilk dolu AYI (gun degil) ----
    ilk_dolu_ay = {}
    for c in calisma_kolonlari:
        if c in YAPISAL_SUTUNLAR:
            continue
        ilk_gun = df.loc[df[c].notna(), "tarih"].min()
        ilk_dolu_ay[c] = ilk_gun.strftime("%Y-%m") if pd.notna(ilk_gun) else None

    # ---- GOREV 2: DF-A - noter devri ankoru ----
    noter_adaylari = {
        "noter_devir_toplam_adet": ilk_dolu_ay["noter_devir_toplam_adet"],
        "noter_devir_otomobil_adet": ilk_dolu_ay["noter_devir_otomobil_adet"],
    }
    ankor_sutun = min(noter_adaylari, key=noter_adaylari.get)
    ankor_ay = noter_adaylari[ankor_sutun]
    print("=== GOREV 2 - DF-A ANKOR ===")
    print(f"noter_devir_toplam_adet ilk dolu ay: {noter_adaylari['noter_devir_toplam_adet']}")
    print(f"noter_devir_otomobil_adet ilk dolu ay: {noter_adaylari['noter_devir_otomobil_adet']}")
    print(f"-> Ankor: {ankor_sutun} ({ankor_ay})")
    print()

    gecen_sutunlar, gecemeyen_sutunlar = [], []
    for c, ay in ilk_dolu_ay.items():
        if ay is None:
            gecemeyen_sutunlar.append((c, ay))
            continue
        if ay <= ankor_ay or c in HESAPLAMA_GECIKMELI_ISTISNA:
            gecen_sutunlar.append((c, ay))
        else:
            gecemeyen_sutunlar.append((c, ay))

    df_a_kolonlari = YAPISAL_SUTUNLAR + [c for c, _ in gecen_sutunlar]
    df_a_baslangic = pd.Timestamp(ankor_ay + "-01")
    df_a = df[df["tarih"] >= df_a_baslangic][df_a_kolonlari].reset_index(drop=True)

    print("=== KAPSAMA TESTI SONUCU ===")
    print(f"GECEN ({len(gecen_sutunlar)}):")
    for c, ay in sorted(gecen_sutunlar):
        istisna_notu = " [ISTISNA: hesaplama gecikmesi]" if c in HESAPLAMA_GECIKMELI_ISTISNA else ""
        print(f"  {c}: ilk dolu ay={ay}{istisna_notu}")
    print(f"GECEMEYEN ({len(gecemeyen_sutunlar)}):")
    for c, ay in sorted(gecemeyen_sutunlar, key=lambda x: (x[1] or "", x[0])):
        print(f"  {c}: ilk dolu ay={ay}")
    print()

    # ---- GOREV 3: DF-B - 2024-01-01 -> bugun, TUM sutunlar (otv haric) ----
    df_b_baslangic = pd.Timestamp("2024-01-01")
    df_b = df[df["tarih"] >= df_b_baslangic][calisma_kolonlari].reset_index(drop=True)

    df_a.to_csv(DF_A_CSV, index=False, encoding="utf-8-sig")
    df_b.to_csv(DF_B_CSV, index=False, encoding="utf-8-sig")

    print("=== SONUC ===")
    print(f"DF-A: {df_a.shape[0]} satir x {df_a.shape[1]} sutun | {df_a['tarih'].min().date()} -> {df_a['tarih'].max().date()}")
    print(f"DF-B: {df_b.shape[0]} satir x {df_b.shape[1]} sutun | {df_b['tarih'].min().date()} -> {df_b['tarih'].max().date()}")
    print(f"\nCikti: {DF_A_CSV}\nCikti: {DF_B_CSV}")


if __name__ == "__main__":
    main()
