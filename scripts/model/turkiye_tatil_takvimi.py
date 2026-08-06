"""Türkiye resmî tatil takvimi (2018-2026), iş-günü eşdeğeri için.

Değer 1.0 tam gün, 0.5 yarım gün tatili ifade eder. Hafta sonuna denk gelen
tatiller iş-günü hesabında ayrıca düşülmez; tüketici fonksiyon takvim gününü
ve hafta içi/sonu durumunu birlikte değerlendirir.

Kaynaklar:
* 2429 sayılı Kanun (sabit tatiller ve bayram süreleri):
  https://vakithesaplama.diyanet.gov.tr/2429_kanun.php
* Diyanet yıllık dini/resmî gün listeleri:
  https://vakithesaplama.diyanet.gov.tr/resmitatiller.php?yil=YYYY
  (2018-2026; eski yılların mobil arşivi de aynı kurum alan adındadır.)
"""
from __future__ import annotations

from datetime import timedelta

import pandas as pd


RAMAZAN_ILK_GUN = {
    2018: "2018-06-15",
    2019: "2019-06-04",
    2020: "2020-05-24",
    2021: "2021-05-13",
    2022: "2022-05-02",
    2023: "2023-04-21",
    2024: "2024-04-10",
    2025: "2025-03-30",
    2026: "2026-03-20",
}

KURBAN_ILK_GUN = {
    2018: "2018-08-21",
    2019: "2019-08-11",
    2020: "2020-07-31",
    2021: "2021-07-20",
    2022: "2022-07-09",
    2023: "2023-06-28",
    2024: "2024-06-16",
    2025: "2025-06-06",
    2026: "2026-05-27",
}

KAYNAK_URLLERI = {
    "kanun_2429": "https://vakithesaplama.diyanet.gov.tr/2429_kanun.php",
    **{
        str(yil): f"https://vakithesaplama.diyanet.gov.tr/resmitatiller.php?yil={yil}"
        for yil in range(2018, 2027)
    },
}


def turkiye_resmi_tatil_agirliklari(
    baslangic_yil: int = 2018,
    bitis_yil: int = 2026,
) -> dict[pd.Timestamp, float]:
    """İstenen yıllar için {tarih: tatil_oranı} sözlüğü üretir."""
    if baslangic_yil > bitis_yil:
        raise ValueError("baslangic_yil bitis_yil'dan büyük olamaz")
    desteklenmeyen = [
        yil for yil in range(baslangic_yil, bitis_yil + 1)
        if yil not in RAMAZAN_ILK_GUN or yil not in KURBAN_ILK_GUN
    ]
    if desteklenmeyen:
        raise ValueError(f"Tatil takvimi bu yılları kapsamıyor: {desteklenmeyen}")

    sonuc: dict[pd.Timestamp, float] = {}

    def ekle(tarih, oran: float) -> None:
        ts = pd.Timestamp(tarih).normalize()
        sonuc[ts] = max(sonuc.get(ts, 0.0), float(oran))

    for yil in range(baslangic_yil, bitis_yil + 1):
        for ay_gun in ("01-01", "04-23", "05-01", "05-19", "07-15", "08-30"):
            ekle(f"{yil}-{ay_gun}", 1.0)
        ekle(f"{yil}-10-28", 0.5)
        ekle(f"{yil}-10-29", 1.0)

        ramazan = pd.Timestamp(RAMAZAN_ILK_GUN[yil])
        ekle(ramazan - timedelta(days=1), 0.5)
        for gun in range(3):
            ekle(ramazan + timedelta(days=gun), 1.0)

        kurban = pd.Timestamp(KURBAN_ILK_GUN[yil])
        ekle(kurban - timedelta(days=1), 0.5)
        for gun in range(4):
            ekle(kurban + timedelta(days=gun), 1.0)

    return dict(sorted(sonuc.items()))


__all__ = [
    "KAYNAK_URLLERI",
    "KURBAN_ILK_GUN",
    "RAMAZAN_ILK_GUN",
    "turkiye_resmi_tatil_agirliklari",
]
