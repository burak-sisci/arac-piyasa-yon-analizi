"""Model 01–18 tarihçesini anlatan ders kitabı notebookunu deterministik üretir."""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


REPO_KOKU = Path(__file__).resolve().parents[2]
CIKTI = REPO_KOKU / "notebooks" / "model_tarihsel_gelisim_ve_farklar_ders_kitabi.ipynb"


def _md(metin: str):
    return nbf.v4.new_markdown_cell(dedent(metin).strip())


def _kod(metin: str):
    return nbf.v4.new_code_cell(dedent(metin).strip())


def notebook_uret():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3 (.venv312)",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.12"},
        "proje": {
            "ad": "Araç Piyasası Fiyat Yönü Tahmini",
            "kapsam": "Model 01–18 tarihsel gelişim ve farklar",
            "tarih": "2026-08-09",
            "hazirlayanlar": ["Rota-2", "Pusula (Sonnet/xhigh)"],
            "pusula_oturum": "019fd8ad-8e18-7b4e-a6d4-3c0214efc923",
        },
    }

    nb.cells = [
        _md("""
        # Model 01–18: Tarihsel Gelişim, Kırılmalar ve Birbirinden Farkları

        **Proje:** Araç Piyasası Fiyat Yönü Tahmini
        **Kapsam:** 2026-08-05 → 2026-08-09 modelleme zinciri
        **Hazırlayanlar:** Rota-2 + Pusula (Sonnet/xhigh, kalıcı oturum)
        **Durum:** Denetimli tarihçe; yeni model veya performans deneyi değildir.

        Bu notebook, numarası “Model” olsa da aynı tür işi yapmayan aşamaları
        bilinçli olarak ayırır. Seviye tahmini, doğrudan yön sınıflandırması,
        snapshot/veri sözleşmesi, baseline, bilgi-tavanı teşhisi, karar katmanı
        ve prospektif izleme aynı performans cetveline konulmaz.
        """),
        _md("""
        ## Okuma anahtarı

        | Rol | Anlamı |
        |---|---|
        | **Eğitim** | Yeni parametre öğrenen model veya model ailesi fit edildi. |
        | **Yeniden değerlendirme** | Kayıtlı model kullanıldı; yeni öğrenici fit edilmedi. |
        | **Veri sözleşmesi** | As-of snapshot, lag, ağırlık veya split yapısı kuruldu. |
        | **Baseline** | Parametresiz referans kuralları ölçüldü. |
        | **Teşhis / üst tavan** | Öğrenilebilirlik veya temsil kapasitesi sınandı; üretim adayı değildir. |
        | **Karar katmanı** | Aynı olasılıklardan farklı sınıf kararı üretildi; yeni temsil öğrenilmedi. |
        | **Prospektif izleme** | Dondurulmuş model gelecekteki bağımsız aylar için kayda alındı. |

        İki metrik rejimi ayrıdır:

        1. **Model 01–02:** günlük ham seviye tahmini; birincil ölçü MASE.
        2. **Model 06–18:** aylık `down/stable/up` yönü; birincil ölçü Gorodkin MCC,
           tamamlayıcı ölçü macro-F1.

        MASE ile MCC doğrudan karşılaştırılmaz.
        """),
        _kod("""
        from pathlib import Path
        import json
        import subprocess

        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd

        pd.set_option("display.max_colwidth", 100)
        pd.set_option("display.max_rows", 100)
        REPO_KOKU = Path.cwd()
        if not (REPO_KOKU / "scripts" / "model").exists():
            REPO_KOKU = Path.cwd().parent
        """),
        _md("""
        ## 1. Üç ana araştırma dönemi

        ### Dönem I — Seviye tahmini ve ölçüm hatalarının temizlenmesi (Model 01–05)

        İlk rota, noter otomobil devir adedinin günlük tekrarlı ham seviyesini
        30 gün ileri tahmin etmekti. Model 01/02 güçlü AutoGluon bileşimleri
        kurdu; fakat asıl katkı yalnız skor değil, tek-ay validation ve yanlış
        MASE mevsimsel periyodu gibi iki ciddi ölçüm kusurunun bulunmasıydı.
        Model 03–05 yeni model eğitmedi; kaydedilmiş ensemble’ları geriye dönük
        hata, yön doğruluğu ve feature importance için kullanmayı amaçlayan
        yerel analizlerdi.

        ### Dönem II — Doğrudan yön hedefi ve gerçek-zaman sözleşmesi (Model 06–10)

        Seviye tahmininden doğrudan üç-sınıf yön sınıflandırmasına geçildi.
        Model 06 günlük tekrarlı Tabular yaklaşımı denedi; Model 07–10 ise aylık
        targetı koruyan, haftalık bilgi kesitli ve M−2 gecikmeli nowcast
        protokolünü kurup tek validation yerine 50-origin rolling ölçüme taşıdı.

        ### Dönem III — Bilgi tavanı, kontrollü müdahaleler ve ileri kanıt (Model 11–18)

        Algoritma taraması yerine önce öğrenilebilirlik teşhis edildi. BDDK,
        mevcut as-of feature genişletmesi, ordinal yapı, nested hibrit ve
        asimetrik karar maliyeti tek tek ön-kaydedildi. Hiçbiri terfi kapısını
        geçmeyince Model 14 donduruldu ve Model 18 ile prospektif kanıt toplamaya
        geçildi.
        """),
        _kod("""
        MODELLER = [
            dict(model=1, tarih="2026-08-05", rol="Eğitim", izlek="Seviye",
                 hedef="30 günlük ham seviye", veri="DF-A / 2018–2026",
                 yontem="AutoGluon TimeSeries, high_quality, WeightedEnsemble",
                 protokol="4 validation penceresi; MASE seasonal_period=30",
                 oncekinden_fark="İlk modelleme hattı; toplam noter leakage covariate'i çıkarıldı.",
                 sonuc="Nihai MASE 0,454; %95 TFT + %5 Chronos2.",
                 hukum="Seviye baseline'ı; yön protokolü değildir.",
                 kanit="pm_rapor_modelleme_fazi_1/2.md"),
            dict(model=2, tarih="2026-08-05", rol="Eğitim", izlek="Seviye",
                 hedef="30 günlük ham seviye", veri="DF-B / 2024–2026",
                 yontem="AutoGluon TimeSeries, high_quality, WeightedEnsemble",
                 protokol="Model 01 ile aynı; score_val esas, MASE m=30",
                 oncekinden_fark="Daha kısa fakat zengin DF-B; metrik referansı ve preset düzeltildi.",
                 sonuc="Nihai MASE 0,449; %69 ChronosWithRegressor + %31 TFT.",
                 hukum="DF-A ile benzer seviye hatası; kısa pencere riski sürer.",
                 kanit="pm_rapor_modelleme_fazi_2.md"),
            dict(model=3, tarih="2026-08-05", rol="Yeniden değerlendirme", izlek="Yerel denetim",
                 hedef="30 günlük seviye hata profili", veri="DF-A/DF-B kesitleri",
                 yontem="Kayıtlı WeightedEnsemble ile geriye dönük tahmin",
                 protokol="Yerel untracked script; model yeniden fit edilmez",
                 oncekinden_fark="Tek leaderboard skorundan dönemsel hata profiline geçiş.",
                 sonuc="Denetlenmiş/commitli sonuç yok; tam-veride fit modelle geçmiş kesit riski var.",
                 hukum="PM-onaysız; güvenilir backtest kanıtı sayılmaz.",
                 kanit="scripts/model/model_03_geriye_donuk_test.py (untracked)"),
            dict(model=4, tarih="2026-08-05", rol="Yeniden değerlendirme", izlek="Yerel denetim",
                 hedef="±%5 yön doğruluğu", veri="Model 01/02 seviye tahminleri",
                 yontem="Seviye tahminini up/stable/down etiketine çevirme",
                 protokol="Yerel untracked script; kayıtlı model, yeni fit yok",
                 oncekinden_fark="Seviye hatasından yön doğruluğuna dönüşüm.",
                 sonuc="Denetlenmiş/commitli metrik yok.",
                 hukum="Sonraki K9/K10 yön protokolünün yerine geçmez.",
                 kanit="scripts/model/model_04_yon_dogrulugu.py (untracked)"),
            dict(model=5, tarih="2026-08-05", rol="Yeniden değerlendirme", izlek="Yerel denetim",
                 hedef="Seviye modelinde feature katkısı", veri="DF-A/DF-B",
                 yontem="Kayıtlı WeightedEnsemble permutation feature importance",
                 protokol="Yerel untracked script; model yeniden fit edilmez",
                 oncekinden_fark="Tahminden açıklayıcı değişken katkısı teşhisine geçiş.",
                 sonuc="Denetlenmiş/commitli sonuç yok.",
                 hukum="Keşifsel kod; model terfi kanıtı değildir.",
                 kanit="scripts/model/model_05_feature_importance.py (untracked)"),
            dict(model=6, tarih="2026-08-06", rol="Eğitim", izlek="Doğrudan yön",
                 hedef="Sonraki ay hacim yönü, ±%5", veri="DF-A ve DF-B günlük tekrarlı",
                 yontem="AutoGluon Tabular multiclass; ay/sınıf ağırlığı adayları",
                 protokol="Train–purge–validation–purge–test; test keşifsel",
                 oncekinden_fark="Seviyeden doğrudan üç-sınıf yön sınıflandırmasına geçiş.",
                 sonuc="DF-A MCC 0,242/F1 0,276; DF-B son iterasyon MCC -0,387/F1 0,095.",
                 hukum="Mevsimsel t−12 baseline geçilmedi; günlük tekrar ayrım gücü zayıf.",
                 kanit="pm_rapor_hacim_yon_sinif_agirligi_iterasyonu.md"),
            dict(model=7, tarih="2026-08-07", rol="Veri sözleşmesi", izlek="Nowcast",
                 hedef="Cari ay M/M−1 yönü", veri="DF-A 101 ay; DF-B 29 ay",
                 yontem="Pazar cut-off'lu haftalık snapshot, lag2, ay-eşit ağırlık",
                 protokol="Model eğitmez; as-of ve tatil takvimi üretir",
                 oncekinden_fark="Günlük pseudo-replikasyondan aylık bağımsız birime geçiş.",
                 sonuc="DF-A N≥50 geçti; DF-B yalnız keşifsel.",
                 hukum="Model 08–18'in ortak bilgi-zamanı omurgası.",
                 kanit="pm_rapor_haftalik_aylik_nowcast_veri_sozlesmesi.md"),
            dict(model=8, tarih="2026-08-07", rol="Baseline", izlek="Nowcast",
                 hedef="Cari ay yönü", veri="2024-05..2025-04 validation",
                 yontem="Train çoğunluğu, M−2 persistence, seasonal t−12",
                 protokol="Validation-only; test kapalı",
                 oncekinden_fark="Öğrenilmiş modelden önce gerçek-zaman uyumlu referansları sabitledi.",
                 sonuc="En iyi baseline M−2: MCC 0,110; macro-F1 0,415.",
                 hukum="Sonraki tüm adayların asgari referansı.",
                 kanit="pm_rapor_nowcast_baseline_ve_dusuk_kapasite.md"),
            dict(model=9, tarih="2026-08-07", rol="Eğitim", izlek="Nowcast",
                 hedef="Cari ay yönü", veri="62 train + 12 validation ayı",
                 yontem="2 lojistik + sığ RF + sığ HGB; 10 feature",
                 protokol="Tek validation; ay-eşit haftalık snapshot",
                 oncekinden_fark="Parametresiz Model 08'e karşı sınırlı düşük-kapasite aile.",
                 sonuc="En iyi aday RF: MCC 0,037; macro-F1 0,189.",
                 hukum="M−2 baseline geçilmedi; test açılmadı.",
                 kanit="pm_rapor_nowcast_baseline_ve_dusuk_kapasite.md"),
            dict(model=10, tarih="2026-08-08", rol="Eğitim", izlek="Rolling nowcast",
                 hedef="Cari ay yönü", veri="2021-03..2025-04, 50 origin",
                 yontem="Model 09'un aynı 4 adayı; her originde yeniden fit",
                 protokol="2 ay embargo; 2.000 hareketli-blok; Holm + jackknife",
                 oncekinden_fark="Tek validation'dan genişleyen rolling-origin kanıta geçiş.",
                 sonuc="Persistence MCC 0,0165; en iyi model MCC -0,0306.",
                 hukum="Dört adayın tüm delta-MCC'leri negatif; terfi yok.",
                 kanit="pm_rapor_nowcast_rolling_origin.md"),
            dict(model=11, tarih="2026-08-08", rol="Teşhis / üst tavan", izlek="Bilgi tavanı",
                 hedef="Aynı K9/K10 yönü", veri="76 ay + aynı 50 origin",
                 yontem="Kırılma, geçiş, lag, band ve permutation-null oracle",
                 protokol="Ön-kayıtlı; yeni üretim adayı yok; test kapalı",
                 oncekinden_fark="Algoritma aramak yerine hedefin öğrenilebilirliğini sorguladı.",
                 sonuc="Lag-2 MCC 0,0165; hiçbir oracle null95'i +0,15 aşmadı.",
                 hukum="Mevcut temsilde saptanabilir öngörü becerisi yok.",
                 kanit="pm_rapor_model11_hedef_bilgi_tavani.md"),
            dict(model=12, tarih="2026-08-08", rol="Teşhis / üst tavan", izlek="Yeni bilgi",
                 hedef="Aynı yön hedefi", veri="BDDK taşıt kredisi, M−2 as-of",
                 yontem="4/13/52 hafta + reel 4 hafta; C=1 ve sabit kontrol ailesi",
                 protokol="1.000 permutation; iki kollu kapasite/yararlılık tavanı",
                 oncekinden_fark="İlk dış resmî öncü bilgi ailesi eklendi.",
                 sonuc="C=1 delta marj +0,2402; mutlak marj -0,0592.",
                 hukum="ON_ELEME_ZAYIF / HEURISTIK; performans terfisi değil.",
                 kanit="pm_rapor_bddk_tavan_taramasi.md"),
            dict(model=13, tarih="2026-08-08", rol="Teşhis / üst tavan", izlek="Yeni bilgi",
                 hedef="Aynı yön hedefi", veri="Model 12 BDDK cache",
                 yontem="L2 lojistik C=0,01 kontrol ve BDDK kolu",
                 protokol="Model 12 harness birebir; düşük kapasite terminal tekrar",
                 oncekinden_fark="C=1 sinyalinin kapasiteye dayanıp dayanmadığını sınadı.",
                 sonuc="Delta marj +0,0268; mutlak kol2 marj -0,1815.",
                 hukum="KAPASITE_DUSUK_ISARET_YOK; daha fazla C taraması durdu.",
                 kanit="pm_rapor_bddk_kapasite_dusuk_tekrar.md"),
            dict(model=14, tarih="2026-08-09", rol="Eğitim", izlek="Feature genişletme",
                 hedef="Aynı yön hedefi", veri="Aynı 50 origin, DF-A",
                 yontem="Model 09 ailesi; 10→14 as-of feature",
                 protokol="Model 10 ile canlı kontrol; 2.000 blok + Holm",
                 oncekinden_fark="Yeni dış kaynak yerine mevcut snapshot'taki 4 kullanılmamış bilgi.",
                 sonuc="L2 C=0,1 MCC 0,0886; F1 0,3659; ΔMCC +0,0721.",
                 hukum="Holm altı -0,2020; dondurulmuş aday, terfi değil.",
                 kanit="pm_rapor_model14_mevcut_asof_feature_genisletme.md"),
            dict(model=15, tarih="2026-08-09", rol="Eğitim", izlek="Ordinal mimari",
                 hedef="Sıralı down<stable<up", veri="Model 14'ün 14 feature'ı / 50 origin",
                 yontem="Frank–Hall iki kümülatif L2 lojistik + monoton projeksiyon",
                 protokol="Model 14 canlı kontrol; aile 5 adaya genişletildi",
                 oncekinden_fark="Nominal multiclass yerine sınıf sırasını eğitimde kullandı.",
                 sonuc="MCC 0,0857; F1 0,3316; accuracy 0,455.",
                 hukum="Macro-F1 ve yıl kararlılığı düştü; terfi yok.",
                 kanit="pm_rapor_model15_frank_hall_ordinal.md"),
            dict(model=16, tarih="2026-08-09", rol="Eğitim", izlek="Nested hibrit",
                 hedef="Aynı yön hedefi", veri="Model 14 olasılığı + M−2 persistence",
                 yontem="İç rolling ile w∈{0,.25,.5,.75,1} seçimi",
                 protokol="1.725 iç + 50 dış fit; seçim yalnız dış-origin train'inde",
                 oncekinden_fark="Tek modelden baseline-model olasılık karışımına geçti.",
                 sonuc="MCC 0,0031; F1 0,3136; ΔMCC -0,0134.",
                 hukum="Train-içi seçim dışarı taşınmadı; terfi yok.",
                 kanit="pm_rapor_model16_nested_persistence_lojistik_hibrit.md"),
            dict(model=17, tarih="2026-08-09", rol="Karar katmanı", izlek="Maliyet duyarlı",
                 hedef="Aynı yön hedefi", veri="Model 14 L2 olasılıkları",
                 yontem="Sabit ordinal maliyet matrisi [[0,1,4],[1,0,1],[4,1,0]]",
                 protokol="Yeni fit yok; aynı 50 originde karar kuralı",
                 oncekinden_fark="Argmax yerine komşu/reversal maliyetini minimize etti.",
                 sonuc="MCC 0,0896; F1 0,2725; accuracy 0,310.",
                 hukum="En yüksek nokta MCC, ağır F1/accuracy kaybı; terfi yok.",
                 kanit="pm_rapor_model17_asimetrik_ordinal_maliyet.md"),
            dict(model=18, tarih="2026-08-09", rol="Prospektif izleme", izlek="Yeni kanıt",
                 hedef="Aynı yön hedefi", veri="2019-01..2025-04 fit; 2026-08+ ileri",
                 yontem="Dondurulmuş Model 14 L2 C=0,1; hash'li append-only defter",
                 protokol="İlk 4 hafta/ay; N=12'den önce performans metriği yasak",
                 oncekinden_fark="Retrospektif model aramasından gerçekleşmeden-önce kanıta geçti.",
                 sonuc="İlk 2026-08-02 sinyali down, p=0,4315; N=0/12.",
                 hukum="Performans sonucu yok; terminal değerlendirme kapalı.",
                 kanit="pm_rapor_model18_prospektif_izleme.md"),
        ]

        tarihce = pd.DataFrame(MODELLER)
        tarihce
        """),
        _md("""
        ## 2. Kronolojik ana tablo

        Aşağıdaki görünüm, her aşamanın önceki aşamaya getirdiği **tek temel
        farkı** öne çıkarır. Ayrıntılı veri/yöntem/protokol sütunları yukarıdaki
        `tarihce` DataFrame’inde tutulur.
        """),
        _kod("""
        tarihce[["model", "rol", "izlek", "oncekinden_fark", "sonuc", "hukum"]]
        """),
        _kod("""
        rol_sirasi = [
            "Eğitim", "Yeniden değerlendirme", "Veri sözleşmesi", "Baseline",
            "Teşhis / üst tavan", "Karar katmanı", "Prospektif izleme",
        ]
        rol_y = {rol: i for i, rol in enumerate(rol_sirasi)}
        renkler = {
            "Eğitim": "#2563eb", "Yeniden değerlendirme": "#64748b",
            "Veri sözleşmesi": "#0891b2", "Baseline": "#7c3aed",
            "Teşhis / üst tavan": "#d97706", "Karar katmanı": "#dc2626",
            "Prospektif izleme": "#059669",
        }

        fig, ax = plt.subplots(figsize=(15, 6))
        for rol, grup in tarihce.groupby("rol", sort=False):
            ax.scatter(grup["model"], [rol_y[rol]] * len(grup), s=130,
                       color=renkler[rol], label=rol, zorder=3)
            for model in grup["model"]:
                ax.text(model, rol_y[rol] + 0.12, f"M{model:02d}", ha="center", fontsize=8)
        ax.set_yticks(range(len(rol_sirasi)), rol_sirasi)
        ax.set_xticks(range(1, 19))
        ax.set_xlabel("Kronolojik model/aşama numarası")
        ax.set_title("Model 01–18: eğitim ile destekleyici araştırma aşamalarının ayrımı")
        ax.grid(axis="x", alpha=.2)
        ax.legend(loc="upper center", bbox_to_anchor=(.5, -0.14), ncol=4, frameon=False)
        plt.tight_layout()
        """),
        _md("""
        ## 3. Dönem I — Model 01–05: seviye tahmini hattı

        ### Model 01 — İlk AutoGluon TimeSeries baseline

        - DF-A üzerinde 30 günlük ham seviye tahmini yaptı.
        - İlk tek-pencere validation, aylık sabit target tekrarları nedeniyle
          yapay biçimde kolaydı; dört pencereye çıkarıldı.
        - Sonradan m=30 ile düzeltilen nihai DF-A WeightedEnsemble MASE’i `0,454`.
        - Bu başarı, yön sınıflandırması başarısı değildir.

        ### Model 02 — DF-B, doğru MASE referansı ve high_quality

        Model 01’den üç noktada ayrılır: daha kısa/zengin DF-B, `m=7→30`
        seasonal-period düzeltmesi ve `medium→high_quality`. DF-B kazananında
        ChronosWithRegressor ağırlığı baskın hale geldi; MASE `0,449`.

        ### Model 03–05 — Neden ana kanıt zincirinde değiller?

        Bu üç dosya yerel ve untracked’tir; PM onayı/commitli sonuçları yoktur.
        Ayrıca Model 03/04, tüm dönemle eğitilmiş kayıtlı predictor’ı geçmiş
        kesitlerde yeniden fit etmeden kullanır. Bu, kod niyetini “dönemsel
        hata/yön analizi” yapar; fakat gerçek walk-forward dış-örnek kanıtı
        yapmaz. Model 05 permutation importance da aynı kayıtlı ensemble’ın
        açıklayıcı analizidir, yeni model değildir.
        """),
        _kod("""
        mase = pd.DataFrame([
            {"model": "M01 / DF-A", "MASE": 0.454, "kazanan": "WeightedEnsemble"},
            {"model": "M02 / DF-B", "MASE": 0.449, "kazanan": "WeightedEnsemble"},
        ])
        ax = mase.plot.barh(x="model", y="MASE", figsize=(8, 3), legend=False,
                            color=["#2563eb", "#0891b2"])
        ax.axvline(1.0, color="black", linestyle="--", linewidth=1, label="MASE=1 referans")
        ax.set_title("Seviye tahmini izlegi — yalnız kendi metrik rejimi içinde")
        ax.set_xlabel("Validation MASE (düşük daha iyi)")
        ax.legend(frameon=False)
        plt.tight_layout()
        """),
        _md("""
        ## 4. Dönem II — Model 06–10: doğrudan yön ve nowcast disiplini

        ### Model 06 — Hedef dönüşümü

        İlk kez seviye tahmini sonrası eşikleme yerine doğrudan multiclass
        sınıflandırma yapıldı. Günlük satırlar korunup ay-eşit ağırlık verilse
        de feature’ların çoğu ay içinde sabit kaldı. Son sınıf-ağırlığı
        iterasyonunda DF-A `MCC=0,242`, DF-B `MCC=-0,387`; iki set de seasonal
        t−12’yi geçmedi. README’deki daha erken DF-B `+0,387` kaydı tarihsel ilk
        denemeye aittir; nihai iterasyon raporu negatif işaretli sonucu esas alır.

        ### Model 07 — Eğitim değil, bilgi-zamanı mimarisi

        Cari aylık target parçalanmadı. Her pazar kesitinde yalnız o ana kadarki
        günlük bilgi, aylık kaynaklarda M−2, target geçmişinde lag2/3/12/13 ve
        ay-eşit ağırlık üretildi. Bu adım sonraki model kıyaslarının ortak
        deneysel zeminidir.

        ### Model 08 → 09 → 10 — Referans, aday, genelleme

        - **M08:** Parametresiz baseline’ları sabitledi.
        - **M09:** Aynı 12-ay validation’da dört düşük-kapasiteli aday ekledi.
        - **M10:** Aynı adayları 50 expanding origin, 2-ay embargo, blok bootstrap,
          Holm ve year-out jackknife ile ölçtü.

        Model 09’un sığ RF nokta üstünlüğü Model 10’da taşınmadı. Bu, tek
        validation kazananının zaman boyunca genelleme kanıtı olmadığını gösterdi.
        """),
        _md("""
        ## 5. Dönem III-A — Model 11–13: algoritmadan önce bilgi

        ### Model 11 — Hedef/bilgi tavanı

        Yeni aday eklemek yerine şu soruyu sordu: M−2 bilgi sınırı altında bu
        hedefte saptanabilir yapı var mı? Kırılma, geçiş, lag, stable-band ve
        oracle-null analizleri “mevcut temsilde gösterilebilir beceri yok”
        sonucuna vardı. RF/HGB’nin in-sample oracle skorlarının yüksekliği beceri
        değildi; permütasyon null’ı da aynı seviyede ezberleniyordu.

        ### Model 12 — BDDK ile yeni bilgi ailesi

        Taşıt kredisi büyüme/faiz sinyalleri M−2 as-of kuralla eklendi. C=1
        lojistik kontrolüne göre delta marj güçlü görünse de mutlak null marjı
        negatif kaldı. Sonuç performans terfisi değil `ON_ELEME_ZAYIF` oldu.

        ### Model 13 — Kapasite düşürülmüş falsifikasyon

        C `1→0,01` düşürüldü. BDDK katkısı yalnız `+0,0268` delta marj verdi ve
        mutlak marj `-0,1815` kaldı. Böylece Model 12’nin işareti düşük-kapasite
        tekrarında doğrulanmadı; C taraması kapatıldı.
        """),
        _md("""
        ## 6. Dönem III-B — Model 14–17: aynı yüzeyde kontrollü müdahaleler

        Bu dört aşama aynı 50 test-dışı origin, aynı M−2 sözleşmesi ve aynı
        kilitli test altında kıyaslanabilir. Yine de Model 14–17 yerel aday
        ailesinin büyüdüğü unutulmamalıdır; nokta skorları tek başına terfi
        gerekçesi değildir.
        """),
        _kod("""
        ayni_yuzey = pd.DataFrame([
            {"yaklasim": "M−2 persistence", "MCC": 0.0165081, "Macro-F1": 0.3641522,
             "tur": "Baseline"},
            {"yaklasim": "M10 en iyi model (L2 C=1)", "MCC": -0.0306, "Macro-F1": 0.2946,
             "tur": "10 feature"},
            {"yaklasim": "M14 L2 C=0,1", "MCC": 0.0885950, "Macro-F1": 0.3658911,
             "tur": "14 feature"},
            {"yaklasim": "M15 Frank–Hall", "MCC": 0.0857050, "Macro-F1": 0.3316024,
             "tur": "Ordinal eğitim"},
            {"yaklasim": "M16 nested hibrit", "MCC": 0.0031242, "Macro-F1": 0.3135929,
             "tur": "Ensemble"},
            {"yaklasim": "M17 asimetrik maliyet", "MCC": 0.0895941, "Macro-F1": 0.2725454,
             "tur": "Karar katmanı"},
        ])
        ayni_yuzey
        """),
        _kod("""
        x = np.arange(len(ayni_yuzey))
        genislik = .36
        fig, ax = plt.subplots(figsize=(13, 5))
        ax.bar(x - genislik/2, ayni_yuzey["MCC"], genislik, label="MCC", color="#2563eb")
        ax.bar(x + genislik/2, ayni_yuzey["Macro-F1"], genislik, label="Macro-F1", color="#f59e0b")
        ax.axhline(0, color="black", linewidth=.8)
        ax.set_xticks(x, ayni_yuzey["yaklasim"], rotation=25, ha="right")
        ax.set_title("Aynı 50-origin yüzeyindeki nokta metrikler — belirsizlik/çoklu-test hariç")
        ax.set_ylabel("Skor")
        ax.legend(frameon=False)
        plt.tight_layout()
        """),
        _md("""
        ### Model 14 — Bilgi temsili genişledi

        10 feature’a cari-ay USD/TRY oynaklığı, M−2 tüketici güveni, M−2 ODMD
        adedi ve M−2 reel politika faizi eklendi. İki birincil metrkte en dengeli
        sonuç burada elde edildi. Ancak eşli/Holm alt sınırı negatif kaldı.

        ### Model 15 — Sınıf sırası eğitime girdi

        Frank–Hall ordinal ayrıştırma accuracy’yi artırdı fakat macro-F1’ı
        düşürdü. Sıralı yapı, azınlık sınıflarındaki denge sorununu çözmedi.

        ### Model 16 — Model ile persistence nested biçimde karıştırıldı

        Ağırlık dış origin’e bakmadan iç rolling ile seçildi. Buna rağmen seçim
        dış örneğe taşınmadı; model, baseline’ın hemen altına geri döndü.

        ### Model 17 — Eğitim değil karar maliyeti değişti

        Model 14 olasılıkları sabit kaldı; yalnız reversal hatasına 4 maliyet
        verildi. Nokta MCC en yüksek değere çıktı ama macro-F1 ve accuracy ağır
        düştü. Bu, “en yüksek MCC” ile “en dengeli yön modeli”nin aynı şey
        olmadığını gösterdi.
        """),
        _md("""
        ## 7. Model 18 — Skor aramaktan bağımsız kanıt üretmeye geçiş

        Model 18 yeni bir aday değildir. Model 14’ün 14 feature’ı, L2 C=0,1
        lojistiği, preprocessing’i ve argmax kararı hash ile donduruldu.

        - Eğitim yalnız `2019-01..2025-04`; embargo ve kilitli test etiketleri
          eğitime girmedi.
        - Tahminler gerçekleşmeden önce append-only deftere yazılır.
        - İlk dört hafta ay toplam ağırlığı 1 olacak biçimde değerlendirilir.
        - 12 eksiksiz yeni bağımsız ay dolmadan performans metriği teknik olarak
          üretilemez.
        - İlk 2026-08-02 kayıt `down`, raw confidence `0,4315`; arşiv yedi gün
          geciktiği için `gercek_zamanli_mi=false`.

        Dolayısıyla Model 18’in bugünkü çıktısı skor değil, gelecekte skorun
        güvenilir hesaplanabilmesi için zaman-damgalı kanıt altyapısıdır.
        """),
        _kod("""
        defter = REPO_KOKU / "data" / "processed" / "model" / "model_18_ileri_izleme_defteri.csv"
        if defter.exists():
            ileri = pd.read_csv(defter)
            display(ileri[["hedef_ay", "kesit_tarihi", "hafta_sirasi", "tahmin_sinifi",
                           "raw_confidence", "gercek_zamanli_mi", "prediction_hash"]])
        else:
            print("Yerel Model 18 defteri yok; notebook gömülü tarihçeyle çalışmaya devam eder.")
        """),
        _md("""
        ## 8. Ardışık farklar: tek satırlık geçiş defteri

        | Geçiş | Değişen ana eksen | Sabit kalan |
        |---|---|---|
        | M01→M02 | DF-A→DF-B, m=30 ve high_quality | 30 günlük seviye hedefi |
        | M02→M03 | Tek skor→dönemsel hata niyeti | Kayıtlı ensemble |
        | M03→M04 | Seviye hata→yön doğruluğu | Yeniden fit yok |
        | M04→M05 | Tahmin→açıklayıcı importance | Kayıtlı ensemble |
        | M05→M06 | Seviye→doğrudan üç sınıf | Noter otomobil hacmi |
        | M06→M07 | Günlük satır→aylık bağımsız snapshot | ±%5 yön |
        | M07→M08 | Veri sözleşmesi→parametresiz referans | As-of lag2 |
        | M08→M09 | Baseline→4 düşük-kapasiteli aday | Tek validation |
        | M09→M10 | Tek validation→50 rolling origin | Adaylar/10 feature |
        | M10→M11 | Model arama→öğrenilebilirlik teşhisi | Test-dışı yüzey |
        | M11→M12 | Mevcut bilgi→BDDK yeni bilgi | Target/K10 |
        | M12→M13 | C=1→C=0,01 falsifikasyonu | BDDK ailesi |
        | M13→M14 | Dış BDDK→mevcut snapshotta 4 yeni feature | 50 origin |
        | M14→M15 | Nominal multiclass→ordinal eğitim | 14 feature |
        | M15→M16 | Tek model→nested persistence hibriti | Dış originler |
        | M16→M17 | Eğitim/ensemble→sabit karar maliyeti | Model 14 olasılığı |
        | M17→M18 | Retrospektif arama→prospektif kayıt | Dondurulmuş Model 14 |
        """),
        _md("""
        ## 9. Ne öğrendik? Projeye bağlanan sonuçlar

        1. **Ölçüm tasarımı modelden önce gelir.** Model 01/02’de validation
           penceresi ve MASE periyodu, algoritma seçimi kadar sonucu değiştirdi.
        2. **Seviye başarısı yön başarısı değildir.** MASE<1, K9/K10 üç-sınıf
           nowcast performansını garanti etmedi.
        3. **Etkin N ay sayısıdır.** Haftalık/günlük tekrarlar bağımsız gözlem
           değildir; Model 07–10 bu pseudo-replikasyonu kapattı.
        4. **Tek validation kazananı kırılgandır.** Model 09’un RF üstünlüğü
           rolling-origin Model 10’da tersine döndü.
        5. **Sorun yalnız algoritma değildi.** Model 11–13 bilgi tavanı ve BDDK
           falsifikasyonları, sinyal temsilinin sınırını gösterdi.
        6. **En dengeli aday Model 14’tür; terfi etmiş model yoktur.** Model 17
           nokta MCC’si daha yüksek olsa da macro-F1 kaybı nedeniyle daha iyi
           bütüncül aday değildir.
        7. **Bir sonraki meşru performans artışı yeni bağımsız bilgiden gelir.**
           Aynı 50 origin’de sekizinci aday yerine Model 18 prospektif hattı
           seçildi.
        """),
        _md("""
        ## 10. Kanıt düzeyi ve kırmızı çizgiler

        - Model 03–05: yerel/untracked; sonuç iddiası kurulmaz.
        - Model 06 testleri: önceki iterasyonlar tarafından görülmüş keşifsel
          yüzey; doğrulayıcı test sayılmaz.
        - Model 08/09: 12-ay validation; rolling kanıt Model 10’dur.
        - Model 11–17: kilitli `2025-07..2026-06` test açılmadı.
        - Model 14–17: aynı 50 origin’de büyüyen yerel hipotez ailesi; nokta
          skoruyla yeni deneme seçilmez.
        - Model 18: `N<12` iken metrik veya ara performans yorumu yok.
        - `altin_gram_try` gibi kullanılmamış sinyaller mevcut 50 origin’de
          post-hoc test edilmez; gelecekte ayrı ön-kayıt/bağımsız yüzey gerekir.
        """),
        _kod("""
        beklenen = {f"model_{i:02d}" for i in range(1, 19)}
        tarihce_etiketleri = {f"model_{int(i):02d}" for i in tarihce["model"]}
        assert tarihce_etiketleri == beklenen
        assert tarihce["model"].is_monotonic_increasing
        assert tarihce["model"].is_unique
        assert tarihce.loc[tarihce["model"].isin([3, 4, 5]), "rol"].eq("Yeniden değerlendirme").all()
        assert tarihce.loc[tarihce["model"].eq(7), "rol"].iat[0] == "Veri sözleşmesi"
        assert tarihce.loc[tarihce["model"].eq(18), "rol"].iat[0] == "Prospektif izleme"
        print("Kronoloji denetimi geçti: Model 01–18 eksiksiz, sıralı ve tekil.")
        """),
        _md("""
        ## 11. Birincil repo kanıtları

        - `data/processed/raporlar/pm_rapor_modelleme_fazi_1.md`
        - `data/processed/raporlar/pm_rapor_modelleme_fazi_2.md`
        - `data/processed/raporlar/pm_rapor_hacim_yon_3sinif_baseline.md`
        - `data/processed/raporlar/pm_rapor_hacim_yon_sinif_agirligi_iterasyonu.md`
        - `data/processed/raporlar/pm_rapor_haftalik_aylik_nowcast_veri_sozlesmesi.md`
        - `data/processed/raporlar/pm_rapor_nowcast_baseline_ve_dusuk_kapasite.md`
        - `data/processed/raporlar/pm_rapor_nowcast_rolling_origin.md`
        - `data/processed/raporlar/pm_rapor_model11_hedef_bilgi_tavani.md`
        - `data/processed/raporlar/pm_rapor_bddk_tavan_taramasi.md`
        - `data/processed/raporlar/pm_rapor_bddk_kapasite_dusuk_tekrar.md`
        - `data/processed/raporlar/pm_rapor_model14_mevcut_asof_feature_genisletme.md`
        - `data/processed/raporlar/pm_rapor_model15_frank_hall_ordinal.md`
        - `data/processed/raporlar/pm_rapor_model16_nested_persistence_lojistik_hibrit.md`
        - `data/processed/raporlar/pm_rapor_model17_asimetrik_ordinal_maliyet.md`
        - `data/processed/raporlar/pm_rapor_model18_prospektif_izleme.md`
        - `docs/10_asama_b_nowcast_kapanis_sentezi.md`
        - `docs/11_asama_b_model_performans_terminal_sentezi.md`

        Notebooktaki sayılar bu tracked denetim zincirinden alınmıştır. Yerel
        `data/processed/model/*` dosyaları varsa canlı kontrol için kullanılabilir,
        fakat notebookun temel anlatısı gitignored artefaktlara bağımlı değildir.
        """),
    ]

    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, CIKTI)
    return CIKTI


if __name__ == "__main__":
    print(notebook_uret())
