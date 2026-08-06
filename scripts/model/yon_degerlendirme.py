"""
YON DEGERLENDIRME MODULU — egitim/model ICERMEYEN, TARGET-BAGIMSIZ, yeniden
kullanilabilir saf fonksiyonlar: (1) sabit yuzde esikli yon etiketleme,
(2) siniflandirma metrikleri (MCC, macro-F1, accuracy, sinif-bazinda P/R/
support, karisiklik matrisi), (3) olasilik dogrulama/karar yardimcilari,
(4) purge'li kronolojik split ve ay-agirligi yardimcilari.

Baglayici kararlar (docs/00_karar_kaydi.md, K9 — aktif Asama B karari):
- Stable bandi SABIT yuzde esiklidir (K2'deki oynaklik-uyarlamali/sigma
  tabanli yaklasim aktif hacim gorevi icin TERK EDILMISTIR — bkz. K9). Ana
  senaryo esik_yuzde=5.0; tam sinir degerleri ("==esik") KAPALI araliga
  dahildir -> "stable".
- N5/N12: birincil metrik sklearn.matthews_corrcoef ile hesaplanan COK
  SINIFLI GLOBAL (Gorodkin R_K) MCC + macro-F1; accuracy tanimlayicidir.
  Bu deger BILINCLI OLARAK "macro-MCC" DIYE ADLANDIRILMAZ - MCC'nin
  standart/kabul gormus bir "macro-averaged" versiyonu yoktur; sklearn
  dogrudan Gorodkin'in cok-sinifli genellemesini dondurur (tek, global bir
  sayidir, sinif basina hesaplanip ortalanmaz). Bu yuzden dondurulen anahtar
  acikca "mcc_gorodkin" olarak adlandirilmistir.
- Sabit sinif sirasi (fixed label order) her yerde: down, stable, up.
- Bu modul HANGI target'in (fiyat, hacim, ...) kullanildigini BILMEZ; cagiran
  taraf (ornegin scripts/model/model_06_hacim_yon_siniflandirma.py) hangi
  seriyi/esigi kullanacagina karar verir.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_fscore_support,
)

FIXED_LABEL_ORDER = ["down", "stable", "up"]


def yon_etiketi(yuzde_degisim, esik_yuzde: float = 5.0) -> str:
    """
    Sabit yuzde esikli yon etiketi. Sabit sinif sirasi: down < stable < up.
    Sinir deger (|yuzde_degisim| == esik_yuzde) KAPALI araliga dahildir ->
    "stable" (asirtici degil, esik-icinde sayilir).

    NaN/None girdi -> "eksik" (ayri bir bilgi durumu; FIXED_LABEL_ORDER'a
    dahil DEGILDIR, `degerlendir()` bu etiketi reddeder - cagiran taraf
    eksik ay/etiketleri onceden filtrelemelidir).
    """
    if yuzde_degisim is None or (isinstance(yuzde_degisim, float) and np.isnan(yuzde_degisim)):
        return "eksik"
    if yuzde_degisim > esik_yuzde:
        return "up"
    if yuzde_degisim < -esik_yuzde:
        return "down"
    return "stable"


def sonraki_ay_etiketleri(aylik_hacim: pd.Series, esik_yuzde: float = 5.0) -> pd.Series:
    """
    Ay index'li (pd.Period, freq="M") bir hacim serisinden, HER AY M icin
    "M'nin hacmi ile M+1'in (bir SONRAKI TAKVIM AYININ) hacmi karsilastirilarak"
    kurulan yon etiketi serisini dondurur (ayni index, deger=etiket string).

    Eksik ay/deger (aylik_hacim serisinde M+1 hic yoksa veya NaN ise, ya da
    M'nin kendisi NaN/0 ise -> bolme tanimsiz) -> "eksik". Serinin SON ayi
    (M+1 tanim geregi mevcut olamaz) her zaman "eksik" doner (labelsiz kalir).

    Girdi index'inde ay atlanmissa (takvimde bosluk) bu fonksiyon SESSIZCE
    bir sonraki SATIRI degil bir sonraki TAKVIM AYINI arar (pozisyonel kayma
    hatasi onlenir) - tam bir pd.period_range uzerine yeniden indexlenerek
    yapilir.
    """
    aylik_hacim = aylik_hacim.sort_index()
    if len(aylik_hacim) == 0:
        return aylik_hacim.astype(object)

    tam_takvim = pd.period_range(aylik_hacim.index.min(), aylik_hacim.index.max(), freq="M")
    tam_seri = aylik_hacim.reindex(tam_takvim)
    sonraki = tam_seri.shift(-1)

    with np.errstate(divide="ignore", invalid="ignore"):
        yuzde = (sonraki - tam_seri) / tam_seri * 100
    yuzde = yuzde.where(tam_seri != 0, np.nan)

    etiketler = yuzde.apply(lambda x: yon_etiketi(x, esik_yuzde))
    return etiketler.reindex(aylik_hacim.index)


def ay_agirligi(ay) -> float:
    """
    Bir takvim ayindaki (pd.Period freq="M", veya bu tipe donusturulebilir
    bir deger) her GUNLUK satira verilecek agirlik: 1 / o aydaki gun sayisi.
    Boylece bir ayin tum gunluk satirlarinin agirlik toplami TAM 1.0 olur -
    gunluk frekans korunurken aylar arasi esit temsil saglanir.
    """
    ay = pd.Period(ay, freq="M")
    return 1.0 / ay.days_in_month


def uc_parcali_split_olustur(
    train_baslangic,
    train_bitis,
    purge1_ay,
    val_baslangic,
    val_bitis,
    purge2_ay,
    test_baslangic,
    test_bitis,
) -> dict:
    """
    train -> purge1 (1 ay) -> validation -> purge2 (1 ay) -> test kronolojik,
    ARDISIK ve CAKISMAYAN ay kumelerini kurar ve dogrular. Etiket t+1 (bir
    sonraki takvim ayi) kullandigi icin train/validation ve validation/test
    sinirlarinda en az 1 aylik purge ZORUNLUDUR (aksi halde purge'e en yakin
    egitim/dogrulama satirinin etiketi, degerlendirme kumesinin ilk ayina ait
    bilgiyi sizdirabilir).

    Herhangi bir cakisma veya purge/komsuluk ihlali varsa ValueError.
    Donus: {"train":[...], "purge1":[...], "validation":[...],
            "purge2":[...], "test":[...]} - degerler pd.Period listesi.
    """
    train = list(pd.period_range(train_baslangic, train_bitis, freq="M"))
    purge1 = [pd.Period(purge1_ay, freq="M")]
    val = list(pd.period_range(val_baslangic, val_bitis, freq="M"))
    purge2 = [pd.Period(purge2_ay, freq="M")]
    test = list(pd.period_range(test_baslangic, test_bitis, freq="M"))

    kumeler = {"train": train, "purge1": purge1, "validation": val, "purge2": purge2, "test": test}
    for isim in kumeler:
        if len(kumeler[isim]) == 0:
            raise ValueError(f"uc_parcali_split_olustur: '{isim}' kumesi bos olamaz")

    gorulen: set = set()
    for isim, aylar in kumeler.items():
        cakisan = gorulen & set(aylar)
        if cakisan:
            raise ValueError(
                f"uc_parcali_split_olustur: '{isim}' kumesi daha once gorulen aylarla "
                f"cakisiyor: {sorted(str(a) for a in cakisan)}"
            )
        gorulen |= set(aylar)

    komsuluklar = [
        (train[-1], purge1[0], "train -> purge1"),
        (purge1[-1], val[0], "purge1 -> validation"),
        (val[-1], purge2[0], "validation -> purge2"),
        (purge2[-1], test[0], "purge2 -> test"),
    ]
    for onceki_son, sonraki_ilk, etiket in komsuluklar:
        if onceki_son + 1 != sonraki_ilk:
            raise ValueError(
                f"uc_parcali_split_olustur: '{etiket}' gecisi ardisik degil "
                f"({onceki_son} -> {sonraki_ilk}, aradaki bosluk purge kurallarini ihlal ediyor)"
            )

    return {"train": train, "purge1": purge1, "validation": val, "purge2": purge2, "test": test}


def olasiliklari_dogrula(p_down: float, p_stable: float, p_up: float, atol: float = 1e-6) -> None:
    """
    predict_proba ciktisi urun sozlesmesini dogrular: her olasilik [0,1]
    araliginda ve uc olasilik toplami ~1.0 olmali. Ihlalde ValueError.
    """
    for isim, deger in (("p_down", p_down), ("p_stable", p_stable), ("p_up", p_up)):
        if deger < -atol or deger > 1 + atol:
            raise ValueError(f"olasiliklari_dogrula: {isim}={deger} [0,1] araliginda degil")
    toplam = p_down + p_stable + p_up
    if abs(toplam - 1.0) > atol:
        raise ValueError(f"olasiliklari_dogrula: toplam={toplam} 1.0'a esit degil (atol={atol})")


def tahmin_sinifi_ve_guven(p_down: float, p_stable: float, p_up: float) -> tuple:
    """
    Urun ciktisi: (secilen_sinif, raw_confidence). raw_confidence = maksimum
    olasilik (KALIBRE EDILMEMIS - cagiran taraf bunu acikca "raw" olarak
    adlandirmalidir, bkz. modul docstring'i / K9).
    """
    olasiliklari_dogrula(p_down, p_stable, p_up)
    olasiliklar = {"down": p_down, "stable": p_stable, "up": p_up}
    sinif = max(olasiliklar, key=olasiliklar.get)
    return sinif, olasiliklar[sinif]


def _dogrula_etiketler(etiketler, izin_verilenler) -> None:
    bilinmeyen = sorted(set(etiketler) - set(izin_verilenler))
    if bilinmeyen:
        raise ValueError(
            f"Bilinmeyen/gecersiz etiket(ler): {bilinmeyen}. Izin verilen: {izin_verilenler} "
            "('eksik' dahil hicbir ek durum kabul edilmez; cagiran taraf onceden filtrelemeli)"
        )


def degerlendir(y_gercek, y_tahmin, label_sirasi=None, agirliklar=None) -> dict:
    """
    Saf fonksiyon - egitim/model YOK, yalnizca metrik hesabi.

    y_gercek / y_tahmin: esit uzunlukta, YALNIZCA FIXED_LABEL_ORDER
    icindeki etiketlerden olusan diziler ("eksik" dahil bilinmeyen deger
    varsa ValueError - cagiran taraf bu satirlari onceden cikarmali).

    agirliklar (opsiyonel): y_gercek ile ayni uzunlukta sayisal agirlik
    dizisi (ornegin gunluk-ay-hizali tekrarlari esitlemek icin
    `ay_agirligi` ile uretilen 1/gun-sayisi agirliklari). None ise tum
    gozlemler esit agirlikli sayilir (sklearn varsayilani).

    Donus: mcc_gorodkin (N5/N12 birincil, cok-sinifli global MCC - bkz. modul
    docstring'i), macro_f1 (birincil), accuracy (tanimlayici), per_class
    (P/R/support), confusion_matrix (satir=gercek, sutun=tahmin, sabit sira).
    """
    label_sirasi = list(label_sirasi) if label_sirasi is not None else list(FIXED_LABEL_ORDER)
    y_gercek = list(y_gercek)
    y_tahmin = list(y_tahmin)

    if len(y_gercek) == 0 or len(y_tahmin) == 0:
        raise ValueError("degerlendir: bos girdi kabul edilmez")
    if len(y_gercek) != len(y_tahmin):
        raise ValueError("degerlendir: y_gercek ve y_tahmin ayni uzunlukta olmali")
    if agirliklar is not None:
        agirliklar = list(agirliklar)
        if len(agirliklar) != len(y_gercek):
            raise ValueError("degerlendir: agirliklar, y_gercek ile ayni uzunlukta olmali")

    _dogrula_etiketler(y_gercek, label_sirasi)
    _dogrula_etiketler(y_tahmin, label_sirasi)

    mcc = matthews_corrcoef(y_gercek, y_tahmin, sample_weight=agirliklar)
    macro_f1 = f1_score(
        y_gercek, y_tahmin, labels=label_sirasi, average="macro", zero_division=0,
        sample_weight=agirliklar,
    )
    acc = accuracy_score(y_gercek, y_tahmin, sample_weight=agirliklar)
    precision, recall, _, support = precision_recall_fscore_support(
        y_gercek, y_tahmin, labels=label_sirasi, zero_division=0, sample_weight=agirliklar
    )
    cm = confusion_matrix(y_gercek, y_tahmin, labels=label_sirasi, sample_weight=agirliklar)

    per_class = {
        etiket: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "support": float(support[i]) if agirliklar is not None else int(support[i]),
        }
        for i, etiket in enumerate(label_sirasi)
    }

    return {
        "mcc_gorodkin": float(mcc),
        "macro_f1": float(macro_f1),
        "accuracy": float(acc),
        "per_class": per_class,
        "confusion_matrix": {
            "label_sirasi": label_sirasi,
            "matris": cm.tolist(),
        },
        "n": len(y_gercek),
        "agirlikli_mi": agirliklar is not None,
    }
