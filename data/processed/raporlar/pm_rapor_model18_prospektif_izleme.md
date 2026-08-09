# PM Raporu — Model 18 Prospektif İzleme

## 1. Ne Yapıldı

Model 14’ün dondurulmuş `lojistik_l2_c01` adayı için yeni bir model aramadan,
aynı 50 origin’i yeniden kullanmadan ve kilitli testi değerlendirmeden
prospektif izleme hattı kuruldu.

- Prompt 48 sonuçtan önce `f4c4592` commit’iyle ön-kaydedildi.
- Eğitim verisi ham DF-A `2025-04-30` tarihinde fiziksel olarak kesildikten
  sonra yeniden kuruldu; böylece `2025-05` sonrası yön etiketleri eğitim kod
  yolunda üretilmedi.
- Gelecek satırı, genel snapshot/etiket fonksiyonunu çağırmayan ayrı etiketsiz
  inşa yoluyla üretildi.
- Tahmin ve gerçekleşme defterleri ayrı, fiziksel append-only ve idempotent
  tasarlandı.
- Terminal değerlendirme N<12 eksiksiz yeni ayda teknik olarak hata veriyor.
- İlk `2026-08-02` kesiti hedef ay kapanmadan kaydedildi.

Bu çalışma yeni aday, terfi veya performans sonucu değildir.

## 2. Sayısal Özet

- Dondurulmuş feature sayısı: `14`.
- Eğitim aralığı: `2019-01..2025-04`.
- Eğitim bağımsız ayı: `76`; haftalık snapshot: `330`.
- İlk hedef/kesit: `2026-08` / `2026-08-02` (`hafta_sirasi=1`).
- Arşivleme: `2026-08-09`; kesitten sonra `7` gün.
- İlk ham olasılıklar: `down=0,431460`, `stable=0,313891`, `up=0,254648`.
- İlk tahmin: `down`; raw confidence `0,431460`.
- Tamamlanmış prospektif bağımsız ay: `N=0/12`.
- Odaklı test: `30/30`; tam tracked test paketi: `161/161`.
- Konfig hash:
  `fb4883aaed0b82cbc98a5df65719e4b2d8641b6f62b6555efad46a588ba65eec`.
- Eğitim veri hash:
  `b2993ba4c53e5ed9bc407a1f6866a06d703078ad5e6fc1a7166f045cf735b66b`.
- Tahmin hash:
  `c5f9e8e44c14c170f82a3e8de184d14ad413c1fe2937d9226c32eda87285d011`.

## 3. Karşılaşılan Sorunlar

- Pusula’nın ilk taslağındaki “tüm mevcut etiketli veriyle fit” ifadesi kilitli
  test etiketlerini eğitime sokabilirdi. Rota-2 bunu uygulama öncesi yakaladı;
  sınır `2019-01..2025-04` olarak sabitlendi.
- Pusula’nın ilk terminal kodu, ön-kayıtta olmayan bir kuralla Ağustos 2026’yı
  N sayacından çıkarıyor ve IID benzeri %2,5 bootstrap kullanıyordu. Kod Model
  14’ün hareketli-blok uzunluğu 4, seed 420, tek-yönlü %5 kapısına düzeltildi.
- İlk kayıt gerçek kesit anında değil yedi gün sonra üretildi. Bu yüzden
  `gercek_zamanli_mi=false`; satır fiziksel 2 Ağustos vintajı iddiası taşımaz.
- İlk haftada dört feature eksikti ve eğitim medyanıyla impute edildi:
  `usdtry_orta_ilk_son_degisim_pct`, `eurtry_orta_ilk_son_degisim_pct`,
  `usdtry_orta_std`, `odmd_otomobil_adet_lag2ay`. İlk pazarın ayın ikinci günü
  olması kur gözlemi eksikliğini açıklıyor; ODMD M−2 eksikliği kaynak
  güncelliği sorunudur.
- Sentetik terminal testinde tek sınıflı örnek nedeniyle sklearn üç uyarı
  verdi; testler geçti ve gerçek performans metriği üretilmedi.
- Pusula Sonnet/xhigh kotası uygulama sırasında yeniden tükendi; Rota-2 yarım
  kalan bilimsel/kod düzeltmelerini tamamladı.

## 4. Veri Örneği

Yeni tahmin defterinin ilk satırının denetlenebilir özeti:

```text
hedef_ay,kesit_tarihi,hafta_sirasi,p_down,p_stable,p_up,tahmin_sinifi,gercek_zamanli_mi,arsiv_gecikme_gun
2026-08,2026-08-02,1,0.4314602776,0.3138913734,0.2546483490,down,false,7
```

Gerçekleşme defteri henüz yoktur; hedef ay kapanmadığı için gerçek etiket
üretilmedi.

## 5. Varsayımlar ve Kararlar

- K9/K10 target, ufuk, sınıf ve ±%5 sözleşmesi değişmedi.
- Kilitli `2025-07..2026-06` aylarında performans okunmadı. Bu dönemin kamuya
  açık ham noter adetleri yalnız gelecek hedefin dondurulmuş lag12/13 feature’ı
  olarak kullanılabilir; geçmiş yön performansı hesaplanmaz.
- Model, feature sırası, preprocessing, argmax ve seed Prompt 48 hash’iyle
  sabittir.
- İlk dört hafta birincil değerlendirmeye girer; ay toplam ağırlığı 1’dir.
- Eski 50 origin ile yeni prospektif aylar istatistiksel olarak birleştirilmez.
- N=12 tek terminal eşiktir; ara performans metriği/yorum yasaktır.
- Repo içinde kullanılmamış `altin_gram_try` bulundu, fakat mevcut doğrulama
  yüzeyinde sekizinci aday yaratmamak için Model 18’e eklenmedi.

## 6. Açık Sorular / PM Onayı Gerekenler

Bağlayıcı yeni K/N kararı yoktur. Operasyonel olarak haftalık çalıştırmanın
kalıcı zamanlayıcısı henüz kurulmadı; sonraki pazartesi kesitlerinin kaçırılmaması
için manuel çalıştırma veya ayrı bir zamanlayıcı kararı gerekecektir.

2027 kesitleri başlamadan önce resmî tatil takvimi 2027’ye kaynaklı biçimde
genişletilmelidir; mevcut yardımcı modül 2018–2026 ile sınırlıdır.

## 7. Önerilen Sonraki Adım

Veri kaynakları güncellendikten sonra `2026-08-09` pazar kesiti için ikinci
haftalık tahmin çalıştırılmalı ve aynı append-only deftere eklenmelidir. Bu adım
performans yorumu üretmeden yürütülür. Dört kesit ve gerçekleşme tamamlanana
kadar Ağustos yalnız açık bir hedef aydır; terminal sayaç `N=0/12` kalır.
