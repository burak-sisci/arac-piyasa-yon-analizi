# PM Raporu — Model 14 Mevcut As-of Feature Genişletme

## 1. Ne Yapıldı

Model 09'un 10 feature'lı kontrol koluna, Model 07 snapshot'ında zaten bulunan
dört as-of sinyal eklendi: cari ay USD/TRY oynaklığı, M−2 tüketici güveni,
M−2 ODMD otomobil adedi ve M−2 yaklaşık reel politika faizi. Ön-kayıt
`prompts/veri/43_model14_mevcut_asof_feature_genisletme_onkayit.md` ile sonuç
görülmeden kilitlendi. Kontrol ve 14-feature test kolları 50 test-dışı
rolling origin, iki ay embargo ve 2.000 ortak hareketli-blok bootstrap ile
değerlendirildi. Kilitli test açılmadı.

## 2. Sayısal Özet

Referans M−2 persistence: MCC `0,0165`, macro-F1 `0,3642`, accuracy `0,3800`.

| Test kolu adayı | MCC | Macro-F1 | Accuracy | ΔMCC vs M−2 | Holm alt sınır | Yıl-dışı işaret | Terfi |
|---|---:|---:|---:|---:|---:|---|---|
| Lojistik L2 C=0,1 | **0,0886** | **0,3659** | 0,3850 | **+0,0721** | -0,2020 | 5/5 pozitif | Hayır |
| Lojistik L2 C=1 | 0,0041 | 0,3202 | 0,3500 | -0,0124 | -0,2758 | Hayır | Hayır |
| Sığ Random Forest | -0,0477 | 0,2898 | 0,3400 | -0,0642 | -0,3616 | Hayır | Hayır |
| Sığ HistGradient | 0,0125 | 0,3250 | 0,3950 | -0,0040 | -0,3468 | Hayır | Hayır |

En iyi aday dört terminal kapının üçünü geçti: ΔMCC≥0,05, Δmacro-F1>0 ve
leave-one-year-out işaret koruması. Eşli hareketli-blok/Holm alt sınırı pozitif
olmadığı için terfi etmedi. Karar: **SINYAL_YOK_14_FEATURE**. Bu ifade, nokta
tahminindeki iyileşmenin inkârı değil; doğrulayıcı belirsizlik kapısının
geçilemediği anlamına gelir.

Kontrol→test feature etkisi en iyi adayda MCC için `+0,1586`, macro-F1 için
`+0,1285` oldu (kontrol lojistik L2 C=0,1: MCC `-0,0700`, macro-F1 `0,2374` —
Model 10 ile birebir). Kontrol kod yolu, aynı HEAD'de çalışan Model 10 ile
1.400/1.400 tahminde birebir eşleşti. Çalışma süresi 73,4 saniyedir.

## 3. Karşılaşılan Sorunlar

- İlk kontrol testi, Git tarafından izlenmeyen eski yerel Model 10 JSON/CSV
  artefaktlarıyla uyuşmadı. Güncel Model 10 ve Model 14 kontrol kod yolları aynı
  süreçte birebir eşleşti. Sonuç görülmeden ön-kayıt Bölüm 9 ile referans güncel
  kod yoluna taşındı; eski yerel artefakt başarı kapısından çıkarıldı.
- Joblib fiziksel çekirdek sayısını Windows ortamında okuyamadı ve mantıksal
  çekirdeğe döndü. Sonuç üretimini veya deterministik tahmin eşitliğini bozmadı.
- 50 bağımsız origin ile eşli fark güven aralıkları geniştir. En iyi adayın
  pozitif nokta farkı ve 5/5 yıl işareti, Holm alt sınırını pozitife taşımaya
  yetmedi.

## 4. Veri Örneği

Model 14 yeni ham veri çekmedi. Test-dışı tahmin tablosunun ilk ve son kayıt
örnekleri:

```text
fold,hedef_ay,train_ay_sayisi,hafta_sirasi,yaklasim,gercek,tahmin
1,2021-03,24,1,train_cogunlugu,up,down
1,2021-03,24,1,persistence_m_eksi_2,up,down
50,2025-04,73,3,hist_gradient_sigin,up,down
50,2025-04,73,4,hist_gradient_sigin,up,down
```

Yerel denetim artefaktları:
`data/processed/model/model_14_mevcut_asof_feature_genisletme_ozet.json`,
`model_14_kontrol_10feature_tahminleri.csv` ve
`model_14_test_14feature_tahminleri.csv`. Veri/model artefakt politikası gereği
Git'e girmezler.

## 5. Varsayımlar ve Kararlar

- K9/K10 hedefi, üç sınıf, kapalı ±%5 bant ve haftalık cari-ay nowcast aynen
  korundu.
- Bütün aylık feature'lar M−2; cari ay kur oynaklığı yalnız kesit tarihine kadar
  gözlenen iş günlerinden hesaplandı.
- Imputer ve scaler her origin'in yalnız train bölümünde fit edildi.
- Model/feature/hiperparametreler sonuçtan önce sabitlendi; post-hoc ekleme
  yapılmadı.
- M−2 persistence birincil referans, MCC birincil metrik; hafta tanısı terfi
  gerekçesi değildir.
- `2025-07..2026-06` kilitli testten 57 snapshot satırı çalışma başında
  çıkarıldı ve hiçbir origin bu pencereye erişmedi.

## 6. Açık Sorular / PM Onayı Gerekenler

Model 14 ailesinde ek ad-hoc feature veya hiperparametre araması yapılmayacaktır.
En iyi adayın üç kapıyı geçip yalnız belirsizlik kapısında kalması, yeni ve tek
adaylı bir doğrulama hipotezini gerekçelendirebilir; ancak aynı 50 origin yeniden
kullanılırsa Model 14 ile birleşik çoklu-test ailesi açıkça korunmalıdır.

## 7. Önerilen Sonraki Adım

Model 14'ü yeniden taramak yerine, karar kaydında önceden ileri deneme olarak
yer alan Frank–Hall ordinal ayrıştırmasını 14 feature üzerinde **tek sabit
aday** olarak sonuçtan önce kaydetmek; Model 14'ün dört adayıyla birleşik beşli
hipotez ailesi üzerinden Holm kapısını uygulamak. Kilitli test açılmaz.
