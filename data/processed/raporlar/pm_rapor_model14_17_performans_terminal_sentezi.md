# PM Raporu — Model 14–17 Performans Terminal Sentezi

## 1. Ne Yapıldı

Model 14–17'nin aynı K9/K10 hedefi ve 50 test-dışı origin üzerindeki kanıtı
birleştirildi. En iyi dengeli aday donduruldu; aynı validation yüzeyinde yeni
algoritma/feature/threshold aramasının durdurma sınırı yazıldı. Yeni model
çalıştırılmadı ve kilitli test açılmadı.

## 2. Sayısal Özet

- Persistence: MCC `0,0165`, macro-F1 `0,3642`.
- Dondurulan Model 14: MCC `0,0886`, macro-F1 `0,3659`, ΔMCC `+0,0721`;
  Holm alt sınırı negatif.
- Model 15: MCC `0,0857`, macro-F1 `0,3316`.
- Model 16: MCC `0,0031`, macro-F1 `0,3136`.
- Model 17: MCC `0,0896`, macro-F1 `0,2725`.
- Son tracked test: `131/131`.

## 3. Karşılaşılan Sorunlar

- Anaconda ve `.venv312` sklearn sürümleri lojistik kontrol tahminlerini
  değiştirdi; doğrulanmış ortam `.venv312` olarak kilitlendi.
- Pusula'nın terminal Sonnet/xhigh çağrısı oturum kotasına takıldı; kota 11:10
  Europe/Istanbul'da yenilenecek. Model 15 öncesi kırmızı-takım katkısı ve tüm
  Pusula tasarım kayıtları korunmuştur.
- Aynı 50 origin üzerinde yedi adaylık yerel aile oluştu; yeni deneme
  validation madenciliği riskini artıracaktır.

## 4. Veri Örneği

Yeni ham veri yoktur. Terminal karşılaştırma satırı örneği:

```text
yaklasim,mcc,macro_f1,accuracy
M-2 persistence,0.0165,0.3642,0.380
Model14 L2 C=0.1,0.0886,0.3659,0.385
Model17 maliyet 0/1/4,0.0896,0.2725,0.310
```

## 5. Varsayımlar ve Kararlar

- Hedef, ufuk, üç sınıf, ±%5, M−2 ve embargo değişmedi.
- Model 14 yalnız geliştirme adayı olarak donduruldu; terfi ettirilmedi.
- Kilitli test validation açığını kapatmak için kullanılmadı.
- Yeni algoritma, bağımsız bilgi/ay/bağlayıcı hedef kararı olmadan açılmayacak.

## 6. Açık Sorular / PM Onayı Gerekenler

Kullanıcı üç yönden birini seçmelidir: gölge vintaj arşivi; yeni bağımsız ayları
bekleme; hedef/ufuk/sınıf sözleşmesini yeniden tasarlama.

## 7. Önerilen Sonraki Adım

Varsayılan güvenli yol Model 14'ü dondurup yeni bağımsız ay beklemektir. Daha
hızlı performans ilerlemesi isteniyorsa, algoritma yerine ilk-yayım korunmuş yeni
bilgi üretme kararı alınmalıdır.
