# PM Raporu — Model 17 Asimetrik Ordinal Maliyet

## 1. Ne Yapıldı

Model 14 L2 C=0,1 olasılıklarına sabit ordinal maliyet kararı uygulandı:
diagonal 0, komşu sınıf hatası 1, down↔up reversal hatası 4. Katsayı, threshold,
feature veya model taranmadı. Model 14/15/16 aynı süreçte canlı üretildi ve
yedi aday ortak Holm ailesinde değerlendirildi. Kilitli test açılmadı.

## 2. Sayısal Özet

| Yaklaşım | MCC | Macro-F1 | Accuracy | ΔMCC vs M−2 | Δmacro-F1 | Holm-7 alt sınır |
|---|---:|---:|---:|---:|---:|---:|
| M−2 persistence | 0,0165 | **0,3642** | **0,380** | — | — | — |
| Model 14 L2 C=0,1 | 0,0886 | **0,3659** | 0,385 | +0,0721 | +0,0017 | -0,2116 |
| Model 17 maliyet 0/1/4 | **0,0896** | 0,2725 | 0,310 | +0,0731 | -0,0916 | -0,2711 |

MCC, Model 14'ten yalnız `+0,0010` yüksekken macro-F1 `-0,0933` ve accuracy
`-0,075` düştü. 2023 leave-one-year-out ΔMCC negatiftir. Yedi kapının yalnız
ΔMCC≥0,05 ve 200/200 argmax yeniden-üretim kontrolü geçti. Karar:
**ASIMETRIK_MALIYET_TERFI_YOK**.

## 3. Karşılaşılan Sorunlar

- Sabit maliyet kuralı reversal riskini azaltırken sınıf kapsamasını bozdu;
  MCC noktasındaki çok küçük artış, macro-F1/accuracy kaybıyla geldi.
- Holm-7 alt sınırı negatiftir ve ham tek-yönlü p `0,3923` düzeyindedir;
  başarısızlık yalnız aile büyüklüğünden kaynaklanmamaktadır.
- İlk ön-kayıtta argmax kontrolü yanlışlıkla toplam 1.400 satır diye yazıldı;
  sonuçtan önce aday-bazlı doğru sayı 200/200 olarak düzeltildi.
- Joblib fiziksel çekirdek uyarısı sonuçları etkilemedi.

## 4. Veri Örneği

Yeni ham veri çekilmedi. Tahmin artefaktı şeması:

```text
fold,hedef_ay,hafta_sirasi,gercek,tahmin,p_down,p_stable,p_up,
beklenen_maliyet_down,beklenen_maliyet_stable,beklenen_maliyet_up
```

Yerel artefaktlar `model_17_asimetrik_maliyet_ozet.json` ve
`model_17_asimetrik_maliyet_tahminleri.csv`; Git dışıdır.

## 5. Varsayımlar ve Kararlar

- K9/K10, 14 as-of feature, origin/embargo ve `.venv312` ortamı korundu.
- Maliyet matrisi sonuçtan önce sabitlendi; alternatif katsayı denenmedi.
- Argmax lojistik kontrolü Model 14 L2 ile 200/200 eşleşti.
- Model 14/15/16 canlı referans metrikleri sıfır farkla yeniden üretildi.
- Yedi aday ortak blok indeksleriyle yerel Holm ailesine girdi.
- Kilitli testten 57 snapshot satırı çalışma başında çıkarıldı.

## 6. Açık Sorular / PM Onayı Gerekenler

Asimetrik maliyet ailesinde ek katsayı/threshold taraması yapılmamalıdır.
Model 14-17 boyunca hiçbir yaklaşım MCC ve macro-F1'ı güvenilir biçimde birlikte
yükseltmemiştir.

## 7. Önerilen Sonraki Adım

Yeni algoritma denemesi başlatmadan Model 14-17 performans hattı terminal bir
sentezde kapatılmalı; hangi kapıların sistematik olarak kırıldığı, mevcut
örneklemde saptanabilir etki ve yeni bilgi gereksinimi yazılmalıdır. Yeni model
ancak bilgi kümesi veya veri vintajı konusunda bağlayıcı yön seçildikten sonra
başlatılmalıdır.
