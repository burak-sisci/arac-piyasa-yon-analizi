"""Model 18 gerçekleşme kaydı: bir hedef ayın GERÇEK yön etiketi bilindiğinde
tahmin defterinden BAĞIMSIZ, ayrı bir append-only deftere yazar.

Ön-kayıt: prompts/veri/48_model18_prospektif_izleme_onkayit.md Bölüm 4.

Tahmin defterine (`model_18_ileri_izleme_defteri.csv`) HİÇBİR ŞEKİLDE
dokunmaz — olasılıklar/sınıf GERİYE DÖNÜK ASLA değişmez. Bağ, satır
güncellemesiyle değil `prediction_hash` üzerinden AYRI bir deftere tek
yönlü ekleme ile kurulur.

Bu script BUGÜN (2026-08-09) hiçbir gerçekleşme kaydetmez — 2026-08 hedef
ayının gerçek değeri henüz yayımlanmadı. Fonksiyonlar, gerçekleşme
yayımlandığında elle/otomatik çağrılmak üzere burada tanımlanır ve
testlerle doğrulanır.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_KOKU = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_KOKU / "data" / "processed" / "model"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import yon_degerlendirme as yd  # noqa: E402

GERCEKLESME_DEFTERI_YOLU = MODEL_DIR / "model_18_gerceklesme_defteri.csv"
GERCEKLESME_KOLONLARI = [
    "prediction_hash", "hedef_ay", "onceki_ay_degeri", "gercek_deger",
    "gercek_etiket", "kayit_tarihi",
]


def gercek_etiketi_hesapla(
    gercek_deger_m: float, gercek_deger_m_eksi_1: float, esik_yuzde: float = 5.0
) -> str:
    """K9/K10 sabit-yüzde-eşikli yön etiketi.

    `yon_degerlendirme.yon_etiketi` ile AYNI kuralı doğrudan çağırır (bağımsız
    bir kopya değil) — kilitli/prospektif ayrımından bağımsız, tek ve tutarlı
    bir sınıflandırma tanımı garanti eder.
    """
    if gercek_deger_m_eksi_1 is None or pd.isna(gercek_deger_m_eksi_1):
        raise ValueError("gercek_etiketi_hesapla: onceki ay degeri eksik")
    if gercek_deger_m_eksi_1 == 0:
        raise ValueError("gercek_etiketi_hesapla: onceki ay degeri sifir, yuzde degisim tanimsiz")
    yuzde = (gercek_deger_m - gercek_deger_m_eksi_1) / gercek_deger_m_eksi_1 * 100.0
    return yd.yon_etiketi(yuzde, esik_yuzde)


def gerceklesme_ekle(kayit: dict, defter_yolu: Path = GERCEKLESME_DEFTERI_YOLU) -> str:
    """Append-only + idempotent yazma.

    Tekil anahtar `prediction_hash`. Aynı hash + aynı içerik -> no-op. Aynı
    hash + farklı içerik -> RuntimeError (ön-kayıt STOP_ONLY_IF madde 6).
    """
    eksik = [k for k in GERCEKLESME_KOLONLARI if k not in kayit]
    if eksik:
        raise KeyError(f"gerceklesme_ekle: eksik alan(lar): {eksik}")

    if defter_yolu.exists():
        mevcut = pd.read_csv(defter_yolu, dtype=str, keep_default_na=False)
    else:
        mevcut = pd.DataFrame(columns=GERCEKLESME_KOLONLARI)

    yeni_satir = {k: ("" if kayit[k] is None else str(kayit[k])) for k in GERCEKLESME_KOLONLARI}

    if not mevcut.empty:
        maske = mevcut["prediction_hash"] == yeni_satir["prediction_hash"]
        if maske.any():
            eslesen = mevcut.loc[maske].iloc[0]
            for kolon in GERCEKLESME_KOLONLARI:
                if str(eslesen.get(kolon, "")) != yeni_satir[kolon]:
                    raise RuntimeError(
                        "STOP_ONLY_IF madde 6: ayni prediction_hash "
                        f"({kayit['prediction_hash']}) farkli icerikle yeniden "
                        f"yazilmak istendi (kolon={kolon})."
                    )
            return "no_op_zaten_kayitli"

    defter_yolu.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([yeni_satir])[GERCEKLESME_KOLONLARI].to_csv(
        defter_yolu,
        mode="a",
        header=not defter_yolu.exists(),
        index=False,
        encoding="utf-8",
    )
    return "eklendi"


def gerceklesmeyi_uret_ve_kaydet(
    *, prediction_hash: str, hedef_ay, gercek_deger_m: float,
    gercek_deger_m_eksi_1: float, kayit_tarihi,
    defter_yolu: Path = GERCEKLESME_DEFTERI_YOLU,
) -> dict:
    """Gerçek etiketi hesaplar ve deftere ekler. Tahmin defterini okumaz/
    değiştirmez — çağıran taraf `prediction_hash`i tahmin defterinden kendi
    getirmelidir (bu script kasıtlı olarak tahmin defterinden bağımsızdır)."""
    gercek_etiket = gercek_etiketi_hesapla(gercek_deger_m, gercek_deger_m_eksi_1)
    kayit = {
        "prediction_hash": prediction_hash,
        "hedef_ay": str(pd.Period(hedef_ay, freq="M")),
        "onceki_ay_degeri": gercek_deger_m_eksi_1,
        "gercek_deger": gercek_deger_m,
        "gercek_etiket": gercek_etiket,
        "kayit_tarihi": str(pd.Timestamp(kayit_tarihi).date()),
    }
    durum = gerceklesme_ekle(kayit, defter_yolu)
    return {"kayit": kayit, "durum": durum}


def main() -> None:
    raise SystemExit(
        "model_18_gerceklesme_kaydet.py bugun (2026-08-09) calistirilmaz: "
        "2026-08 hedef ayinin gercek noter devir degeri henuz yayimlanmadi. "
        "Gerceklesme yayimlandiginda 'gerceklesmeyi_uret_ve_kaydet' fonksiyonu "
        "ilgili prediction_hash ve gercek degerlerle elle/ayri bir cagriyla "
        "kullanilmalidir (onkayit Bolum 9)."
    )


if __name__ == "__main__":
    main()
