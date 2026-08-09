# PM Raporu — Model 15 Frank–Hall Ordinal Tek Aday

## 1. Ne Yapıldı

Model 14'ün 14 as-of feature'ı değiştirilmeden, `down < stable < up` sırasını
kullanan tek Frank–Hall adayı çalıştırıldı. İki L2 lojistik alt-model her
origin'in yalnız train bölümünde fit edildi. Çapraz kümülatif olasılıklar,
ön-kayıtlı iki-nokta L2-isotonic projeksiyonla monotonlaştırıldı. Model 14'ün
dört adayı aynı süreçte canlı yeniden üretildi ve beş aday ortak bootstrap
evreninde Holm düzeltmesine girdi. Kilitli test açılmadı.

## 2. Sayısal Özet

| Yaklaşım | MCC | Macro-F1 | Accuracy | ΔMCC vs M−2 | Δmacro-F1 | Holm-5 alt sınır |
|---|---:|---:|---:|---:|---:|---:|
| M−2 persistence | 0,0165 | 0,3642 | 0,380 | — | — | — |
| Model 14 L2 C=0,1 | **0,0886** | **0,3659** | 0,385 | +0,0721 | +0,0017 | -0,2051 |
| Model 15 Frank–Hall | 0,0857 | 0,3316 | **0,455** | +0,0692 | -0,0325 | -0,3340 |

Model 15'in altı terminal kapısı:

| Kapı | Sonuç |
|---|---|
| Holm-5 alt sınırı >0 | Hayır |
| ΔMCC≥0,05 | Evet |
| Δmacro-F1>0 | Hayır |
| Yıl-dışı işaret 5/5 pozitif | Hayır; 2023 negatif |
| Model 14 en iyisini MCC ve macro-F1'da aşma | Hayır |
| Train-çoğunluğunu iki metrkte aşma | Evet |

Karar: **ORDINAL_TEK_ADAY_TERFI_YOK**. 50 origin × iki ikili model = 100 fit;
200 haftalık satırın 77'sinde ham kümülatif olasılıklar çaprazdı ve ön-kayıtlı
projeksiyon uygulandı. Çalışma süresi 27,9 saniyedir.

## 3. Karşılaşılan Sorunlar

- Pusula kırmızı-takımı ilk taslağı, monoton projeksiyon ve canlı Model 14
  kontrolü açık olmadığı için NO-GO verdi. Dokuz engelleyici düzeltme sonuçtan
  önce Prompt 44'e işlendi.
- Sistem Anaconda ortamı ile proje `.venv312` ortamı farklı scikit-learn
  sürümleri taşıyor ve lojistik kontrol tahminlerini değiştirebiliyor. Model 15
  `.venv312`: Python 3.12.7, sklearn 1.7.2, NumPy 2.3.5, pandas 2.3.3 ile
  kilitlendi. Canlı Model 14 dört referans metriğinde sıfır farkla eşleşti.
- Ordinal yapı accuracy'yi artırırken stable/up ayrımında macro-F1 kaybetti.
  Bu, accuracy artışının terfi gerekçesi sayılamayacağını doğruladı.
- Joblib fiziksel çekirdek sayısını okuyamadı ve mantıksal çekirdeğe döndü;
  sonuç veya deterministik kontrol etkilenmedi.

## 4. Veri Örneği

Yeni ham veri çekilmedi. Test-dışı tahmin artefaktından örnek:

```text
fold,hedef_ay,hafta_sirasi,yaklasim,gercek,tahmin
1,2021-03,1,frank_hall_l2_c01,up,down
1,2021-03,2,frank_hall_l2_c01,up,down
50,2025-04,3,frank_hall_l2_c01,up,down
50,2025-04,4,frank_hall_l2_c01,up,down
```

Yerel artefaktlar `model_15_frank_hall_ordinal_ozet.json` ve
`model_15_frank_hall_ordinal_tahminleri.csv` altında, Git dışındadır.

## 5. Varsayımlar ve Kararlar

- K9/K10, üç sınıf, ±%5 bant, M−2, iki ay embargo ve ay-eşit ağırlık korundu.
- Model 14 feature üretimi/listesi birebir import edildi.
- İki binary alt-model aynı train matrisi ve sample weight kullandı.
- `q1<q2` durumunda iki kümülatif olasılık aritmetik ortalamaya projekte edildi;
  alternatif projeksiyon veya threshold denenmedi.
- Holm-5, aynı seed=420 blok indekslerinde canlı üretilen beş adayla kuruldu.
  Bu yerel FWER kontrolüdür; proje ömrü kümülatif FWER iddiası değildir.
- `2025-07..2026-06` kilitli testten 57 snapshot satırı başta çıkarıldı.

## 6. Açık Sorular / PM Onayı Gerekenler

Ordinal aile kapatılmıştır; ek C, threshold veya projeksiyon taraması
yapılmamalıdır. Model 14 L2 C=0,1 hâlâ en yüksek dengeli nokta performansıdır,
ancak inferential kapıyı geçmemektedir.

## 7. Önerilen Sonraki Adım

Dış 50 origin üzerinde ağırlık seçmeden, her dış origin'in yalnız train
bölümünde nested rolling seçim yapan tek bir persistence–Model 14 lojistik
hibrit algoritması ön-kaydedilebilir. Amaç zayıf model sinyalini korurken düşük
güvenli aylarda güçlü M−2 baseline'a dönmektir. Dış değerlendirmede Model 14/15
adaylarıyla genişletilmiş açık bir çoklu-test ailesi kullanılmalıdır.
