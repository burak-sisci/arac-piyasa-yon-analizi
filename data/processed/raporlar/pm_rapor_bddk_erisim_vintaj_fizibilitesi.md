# PM Raporu — BDDK Erişim ve Vintaj Fizibilitesi

**Tarih:** 2026-08-08

**Aşama:** Seçenek 2 / BDDK taşıt kredisi erişim ve vintaj denetimi

**Durum:** Tamamlandı — **KALDI**

**Karar yöneticisi:** Pusula

**Uygulayıcı:** Rota-2

## 1. Ne Yapıldı

Kullanıcı onayından sonra Pusula'nın örneklem, kaynak sırası, erişim bütçesi ve
karar eşikleri sonuçlardan önce `4e2b9ea` commit'iyle kilitlendi. BDDK'nın resmî
Haftalık Bülten sayfaları ve sayfanın kendi ücretsiz JSON rapor ucu incelendi.

- Ön-kayıtlı beş referans haftanın güncel değerleri çıkarıldı.
- Gelişmiş gösterimin tarih kapsamı ve taşıt kredisi kalem kodu doğrulandı.
- BDDK'nın resmî bağlantı envanterinde tarihli ilk-yayım PDF/Excel arşivi arandı.
- Canlı tarihsel seri ile ilk-yayım vintajı birbirine karıştırılmadı.
- Erişim bütçesi 15 resmî istekle sınırda durduruldu.
- Feature, CSV, model, oracle, permütasyon veya kilitli test erişimi yapılmadı.

Ayrıntılı denetim izi
`data/processed/raporlar/bddk_vintaj_karsilastirma.md` dosyasındadır.

## 2. Sayısal Özet

- Güncel tarihsel seri: **657 hafta**, 2014-01-03–2026-07-31.
- Ön-kayıtlı tarih: **5**.
- Güncel değer erişimi: **5/5**.
- İlk-yayım vintajı erişimi: **1/5**.
- İlk tarih vintajı: **erişilemedi**.
- Tarihsel yayın gecikmesi doğrulanan: **1/5**.
- Son hafta yayın gecikmesi: **6 gün**.
- Ölçülebilir delta: **1/5**, `%0`; dört tarih hesaplanamadı.
- Resmî BDDK erişimi: **15/15** bütçe.
- Üçüncü taraf/ücretli/kimlikli erişim: **0**.
- Veri/feature dosyası: **0**.
- Model fit/test/oracle: **0**.
- Kilitli test erişimi: **0**.

| Referans hafta | Güncel bakiye (milyon TL) | Vintaj | Delta % |
|---|---:|---:|---:|
| 2014-01-03 | 8.613,848 | Erişilemedi | — |
| 2019-01-04 | 6.506,118 | Erişilemedi | — |
| 2022-01-07 | 12.983,300 | Erişilemedi | — |
| 2025-04-25 | 64.040,300 | Erişilemedi | — |
| 2026-07-31 | 42.112,122 | 42.112,122 | %0,000 |

Ön-kayıt hükmü: **KALDI**. Vintaj çoğunlukta yoktur ve zorunlu ilk tarih
erişilememiştir.

## 3. Karşılaşılan Sorunlar (Saklanmaz)

1. **Canlı geçmiş, vintaj değildir.** Gelişmiş uç nokta eski haftaları döndürür;
   fakat BDDK revizyon politikası nedeniyle bunların ilk yayımlandığı değerler
   olduğu varsayılamaz.
2. **Tarihli arşiv bağlantısı yok.** Haftalık Bülten ana sayfası metaveri ve
   revizyon belgelerine bağlantı verir; eski ilk-yayım dosyalarını listelemez.
3. **En güncel hafta özel durumdur.** 31 Temmuz 2026 değeri yayından iki gün
   sonra yakalandığı için ilk-yayıma yakın kabul edildi. Bu, geçmiş dört tarihin
   eksikliğini gidermez ve revizyon davranışını genellemez.
4. **Yayın gecikmesi geçmişte doğrulanamadı.** Güncel 2026 takvimi son tarih için
   altı günü kanıtladı; 2014/2019/2022/2025 ilk hafta takvimleri mevcut resmî
   bağlantı zincirinde bulunamadı.
5. **İki ayrıştırma denemesi başarısız oldu.** Bir HTML seçim regex'i tarih
   bloğunu bulamadı; bir regex'te kaçış hatası çıktı. Her ikisi de erişim
   bütçesine sayıldı, saklanmadı ve sonuç seçimini değiştirmedi.
6. **Gelişmiş JSON kalem kimliği iki biçimde göründü.** UI seçim ağacında iç ID
   `5691`, rapor uç noktasında işlevsel seri kodu `1.0.5` idi. Yanlış iç ID ile
   yapılan çağrı sıfır gözlem döndürdü ve bütçeye sayıldı.
7. **Arşiv yokluğu sınırlı bir hükümdür.** BDDK dışı ayna veya doğrudan kurumsal
   veri talebi ön-kayıt gereği denenmedi; “dünyada hiçbir vintaj yok” denmedi.
8. **Çalışma ağacı kirliydi.** Kullanıcının dört değiştirilmiş notebooku ve diğer
   untracked dosyaları korunarak yalnız bu aşamanın yeni artefaktları üretildi.

## 4. Veri Örneği (Ham, İlk/Son Birkaç Satır)

Resmî JSON cevabındaki 657 haftalık canlı seriden ön-kayıtlı ilk/orta/son
gözlemler:

```text
3.01.2014|8613.848
4.01.2019|6506.118
7.01.2022|12983.30
25.04.2025|64040.30
31.07.2026|42112.122
```

Kaynak başlığı:

```text
b) Taşıt (TRY) [Toplam]
```

Birim Haftalık Bülten tablosunda milyon TL'dir. Bu değerler feature dosyasına
yazılmadı; yalnız erişim/vintaj denetiminin kanıt satırlarıdır.

## 5. Varsayımlar ve Kararlar (K/N Kararlarına Uygunluk)

- Target `noter_devir_otomobil_adet`, üç sınıf ve ±%5 bandı değişmedi.
- Haftalık güncellenen cari-ay nowcast sözleşmesi değişmedi.
- İki aylık bilgi disiplini ve kilitli test sınırı korundu.
- Güncel tarihsel değerler eski originlerde bilinen değer sayılmadı.
- Eksik vintajlar güncel değerle doldurulmadı; delta hesaplanmadı.
- 31 Temmuz 2026 canlı değeri yalnız yayın anına yakın yakalama olarak kabul
  edildi; değişmez tarihsel vintaj arşivi ilan edilmedi.
- `KALDI`, ekonomik sinyal yok hükmü değildir; as-of erişim hükmüdür.
- Hiçbir yeni K/N kararı yazılmadı.
- Kullanıcıya ait mevcut dirty/untracked dosyalar değiştirilmedi veya stage
  edilmedi.

## 6. Açık Sorular / PM Onayı Gerekenler

BDDK adayı mevcut resmî web erişimiyle feature üretimine taşınamaz. Yeniden
açılabilmesi için kullanıcı kararı gerektiren seçenekler şunlardır:

1. BDDK'dan veya resmî veri sahibinden tarihli ilk-yayım dosyalarını doğrudan
   talep etmek.
2. Kurumsal olarak arşivlenmiş, hukuken kullanılabilir bir vintaj kaynağı
   sağlamak.
3. Geriye dönük performans iddiasından vazgeçmeden yalnız bugünden başlayan
   ileriye dönük gölge vintaj arşivi kurmak; bu yeni bir aşama türüdür ve kısa
   vadede rolling-origin kanıtı üretmez.

Üçüncü taraf arşiv, ücretli sağlayıcı veya veri sahibiyle iletişim bu onayın
kapsamında değildi ve başlatılmadı.

## 7. Önerilen Sonraki Adım

Mevcut BDDK adayında feature/model aşamasına **geçilmemesi** önerilir. Proje
Seçenek 2 yönünde devam edecekse Pusula ve kullanıcı birlikte şu iki yoldan
birini seçmelidir:

- Resmî/kurumsal ilk-yayım vintajı temin edilebilecek yeni bir erişim yolu
  sağlamak; veya
- Farklı, tarihli ilk-yayım arşivi bulunan yeni bir öncü bilgi ailesini aynı
  masa başı kapılardan geçirmek.

Bu rapor yalnız önerir; sonraki aşama başlatılmamıştır.
