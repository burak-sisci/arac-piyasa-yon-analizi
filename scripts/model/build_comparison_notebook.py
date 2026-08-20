# -*- coding: utf-8 -*-
"""06_autogluon_tum_targetlar_karsilastirma.ipynb dosyasını oluşturan betik."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "06_autogluon_tum_targetlar_karsilastirma.ipynb"


def markdown(text: str) -> dict:
    return {
        "id": uuid4().hex[:8],
        "cell_type": "markdown",
        "metadata": {},
        "source": text.strip() + "\n",
    }


def code(text: str) -> dict:
    return {
        "id": uuid4().hex[:8],
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip() + "\n",
    }


def build_notebook() -> dict:
    cells = [
        markdown(
            """
# Araç Piyasası Satış Hızı ve Days on Market (DOM) Zaman Serisi Karşılaştırmalı Modelleme

Bu notebook, *"Araçlar ne kadar hızlı satışa dönüyor?"* sorusuna yanıt arayan 4 farklı hedef değişken (target) alternatifini **AutoGluon TimeSeries** modelleri ile karşılaştırır.

### Karşılaştırılan Hedef Değişkenler:
1. **`target_betam_dom_gun`**: BETAM / Sahibinden ortalama kapatılan ilan süresi (**Days on Market - Gün**).
2. **`target_indicata_satis_ilan_orani_pct`**: Indicata satılan araç / toplam ilan oranı (**Satışa Dönüşüm Oranı - %**).
3. **`target_devir_orani`**: Noter otomobil devri / Toplam otomobil parkı (**Hacimsel Devir Oranı**).
4. **`target_1ay_hiz`**: Noter işlem hacmi aylık büyüme ivmesi (**% Log Büyüme**).
"""
        ),
        code(
            """
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Stil ayarları
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 11

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
DATA_DIR = ROOT / "data" / "birlesik_veri_seti"
OUT_DIR = ROOT / "outputs" / "autogluon_target_karsilastirma"

print("Proje Kok:", ROOT)
"""
        ),
        markdown(
            """
## 1. Birleşik Master Veri Setinin Yüklenmesi ve Kapsam Özeti
"""
        ),
        code(
            """
master_df = pd.read_csv(DATA_DIR / "arac_piyasasi_master_veri_seti.csv")
coverage_df = pd.read_csv(DATA_DIR / "veri_kapsama_ve_eksik_deger_raporu.csv")

print(f"Master Tablo Boyutu: {master_df.shape[0]} ay, {master_df.shape[1]} sutun")
print(f"Tarih Araligi: {master_df['referans_ayi'].min()} -> {master_df['referans_ayi'].max()}")

# Target degiskenlerinin ozeti
target_coverage = coverage_df[coverage_df["kategori"] == "Target Adayı"]
display(target_coverage[["degisken", "dolu_ay_sayisi", "doluluk_orani_pct", "ilk_gecerli_ay", "son_gecerli_ay"]])
"""
        ),
        markdown(
            """
## 2. AutoGluon TimeSeries Karşılaştırma Özeti Tablosu
"""
        ),
        code(
            """
summary_df = pd.read_csv(OUT_DIR / "target_karsilastirma_ozeti.csv")
display(summary_df)
"""
        ),
        markdown(
            """
## 3. Karşılaştırmalı Performans Grafikleri (MAE, MAPE, R²)
"""
        ),
        code(
            """
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 1. MAPE (%)
sns.barplot(data=summary_df, x="Hedef Degisken", y="Test MAPE (%)", palette="viridis", ax=axes[0])
axes[0].set_title("Test MAPE (%) - Düşük Olması İyidir", fontsize=13, fontweight="bold")
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=30, ha="right")
for p in axes[0].patches:
    axes[0].annotate(f"%{p.get_height():.1f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')

# 2. Test R²
sns.barplot(data=summary_df, x="Hedef Degisken", y="Test R2", palette="magma", ax=axes[1])
axes[1].set_title("Test R² Skoru - Yüksek Olması İyidir", fontsize=13, fontweight="bold")
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=30, ha="right")
for p in axes[1].patches:
    axes[1].annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')

# 3. Gözlem Sayısı
sns.barplot(data=summary_df, x="Hedef Degisken", y="Gozlem Sayisi", palette="Blues_r", ax=axes[2])
axes[2].set_title("Gözlem Sayısı (Ay)", fontsize=13, fontweight="bold")
axes[2].set_xticklabels(axes[2].get_xticklabels(), rotation=30, ha="right")
for p in axes[2].patches:
    axes[2].annotate(f"{int(p.get_height())} ay", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')

plt.tight_layout()
plt.show()
"""
        ),
        markdown(
            """
## 4. Hedef Değişken Bazında Ayrıntılı İnceleme ve Tahmin Grafikleri
"""
        ),
        markdown(
            """
### 4.1. Days on Market (BETAM DOM - Ortalama İlan Satış Süresi Gün)
"""
        ),
        code(
            """
from IPython.display import Image

lb_dom = pd.read_csv(OUT_DIR / "target_betam_dom_gun" / "leaderboard.csv")
print("=== Days on Market (BETAM) - Liderlik Tablosu ===")
display(lb_dom.head(8))

preds_dom = pd.read_csv(OUT_DIR / "target_betam_dom_gun" / "test_tahminleri_karsilastirma.csv")
display(preds_dom)

Image(filename=str(OUT_DIR / "target_betam_dom_gun" / "gercek_vs_tahmin_grafigi.png"))
"""
        ),
        markdown(
            """
### 4.2. İkinci El Satış / İlan Oranı (Indicata %)
"""
        ),
        code(
            """
lb_ind = pd.read_csv(OUT_DIR / "target_indicata_satis_ilan_orani_pct" / "leaderboard.csv")
print("=== Satış / İlan Oranı (Indicata) - Liderlik Tablosu ===")
display(lb_ind.head(8))

preds_ind = pd.read_csv(OUT_DIR / "target_indicata_satis_ilan_orani_pct" / "test_tahminleri_karsilastirma.csv")
display(preds_ind)

Image(filename=str(OUT_DIR / "target_indicata_satis_ilan_orani_pct" / "gercek_vs_tahmin_grafigi.png"))
"""
        ),
        markdown(
            """
### 4.3. Piyasa Devir Oranı (Noter Devri / Toplam Otomobil Parkı)
"""
        ),
        code(
            """
lb_devir = pd.read_csv(OUT_DIR / "target_devir_orani" / "leaderboard.csv")
print("=== Noter Devir Oranı - Liderlik Tablosu ===")
display(lb_devir.head(8))

preds_devir = pd.read_csv(OUT_DIR / "target_devir_orani" / "test_tahminleri_karsilastirma.csv")
display(preds_devir)

Image(filename=str(OUT_DIR / "target_devir_orani" / "gercek_vs_tahmin_grafigi.png"))
"""
        ),
        markdown(
            """
### 4.4. 1 Aylık Noter Hacim Büyüme Hızı (% Log)
"""
        ),
        code(
            """
lb_hiz = pd.read_csv(OUT_DIR / "target_1ay_hiz" / "leaderboard.csv")
print("=== 1 Aylık Hacim Büyüme Hızı - Liderlik Tablosu ===")
display(lb_hiz.head(8))

preds_hiz = pd.read_csv(OUT_DIR / "target_1ay_hiz" / "test_tahminleri_karsilastirma.csv")
display(preds_hiz)

Image(filename=str(OUT_DIR / "target_1ay_hiz" / "gercek_vs_tahmin_grafigi.png"))
"""
        ),
        markdown(
            """
## 5. Sonuç ve Stratejik Değerlendirme

- **`target_betam_dom_gun`**: Doğrudan "Araçlar ne kadar sürede satılıyor?" sorusunun yanıtıdır. Ortalama hata payı (MAE) ~1.0 gün düzeyindedir.
- **`target_indicata_satis_ilan_orani_pct`**: Pazarın absorpsiyon kapasitesini ölçer, mevsimsellik ve talep şoklarına duyarlıdır.
- **`target_devir_orani`**: 102 aylık uzun geçmişi sayesinde en stabil ve makroekonomik döngüleri en iyi yansıtan göstergedir.
"""
        ),
    ]

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (.venv-ag)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return nb


def main():
    nb = build_notebook()
    NOTEBOOK_PATH.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Notebook oluşturuldu: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
