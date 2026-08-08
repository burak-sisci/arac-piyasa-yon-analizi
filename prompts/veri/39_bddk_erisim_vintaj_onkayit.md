# Prompt 39 — BDDK Erişim ve Vintaj Fizibilitesi Ön-Kaydı

**Tarih:** 2026-08-08

**Kullanıcı onayı:** BDDK erişim ve vintaj fizibilitesi aşaması açıkça onaylandı.

**Karar yöneticisi:** Pusula (`6f4c6fd0-6ddb-4b70-8e45-86d5b6d124c1`, Sonnet/xhigh)

**Uygulayıcı:** Rota-2

## 1. Kapsam

Tek aday BDDK Haftalık Bülten taşıt kredisi bakiyesi/değişimidir. Bu aşama
yalnız erişimi, referans hafta–yayın tarihi eşlemesini, ilk-yayım vintajının
korunup korunmadığını, revizyon davranışını ve tarihsel kapsamı sınar.

Feature üretimi, model/oracle/permütasyon hesabı, rolling-origin hattına ekleme,
hedef/sınıf/band/ufuk/K değişikliği ve kilitli test dosyalarını okuma yasaktır.

## 2. Sonuçtan Önce Kilitlenen Beş Tarih

1. Metaveride iddia edilen ilk hafta: Ocak 2014 sınırında yayımlanan ilk hafta.
2. 2019 takvim yılının ilk yayımlanan haftası.
3. 2022 takvim yılının ilk yayımlanan haftası.
4. 2025-04 ayının son yayımlanan haftası.
5. 2026-08-08 itibarıyla en güncel yayımlanmış hafta.

Tam tarih yayımlanmamışsa o tarihe eşit veya öncesindeki en yakın yayımlanmış
hafta alınır. Bu beş tarih dışında sonuçlara bakarak ek tarih seçilmez.

## 3. Kaynak Hiyerarşisi

1. BDDK Haftalık Bülten gelişmiş gösterim — tarihli haftanın döneminde
   yayımlanmış tablosu.
2. Varsa tarihli resmî BDDK Haftalık Bülten PDF/Excel arşiv dosyası.
3. Yalnız güncel karşılaştırma tarafı için BDDK'nın bugünkü indirilebilir zaman
   serisi; ilk-yayım vintajı yerine kullanılamaz.
4. Yayın takvimi ve BDDK revizyon açıklaması yalnız doğrulama metnidir.

Yalnız BDDK'nın ücretsiz ve kimliksiz genel ağ kaynakları kullanılabilir. BDDK
dışı ayna, Wayback Machine, ücretli/kimlikli uç nokta, toplu scraping ve döngüsel
crawling yasaktır. Toplam manuel erişim bütçesi en fazla 15 sayfa/dosyadır.

## 4. Karşılaştırma Şeması

Her tarih için:

- `referans_hafta`
- `yayin_tarihi`
- `yayin_gecikmesi_gun`
- `vintaj_degeri`: ilk-yayım tarihli tablodan; yoksa `vintaj_erisilemedi`
- `guncel_deger`: bugünkü canlı seride aynı referans haftanın değeri
- `delta_mutlak = abs(guncel_deger - vintaj_degeri)`
- `delta_yuzde = delta_mutlak / abs(vintaj_degeri) * 100`
- `kaynak_url`
- `erisilebilirlik_notu`

İki değer birlikte yoksa delta hesaplanmaz. Güncel değer, vintaj alanına
kopyalanamaz.

## 5. Karar Kapıları

### GEÇTİ

- Vintaj en az 4/5 tarihte erişilebilir; ilk ve en güncel tarih mutlaka dahil.
- Yayın gecikmesi beş tarihte tutarlı veya yalnız küçük takvim sapmaları gösterir.
- Ölçülebilen her tarihte `delta_yuzde < %5`.
- Erişim ücretsiz, kimliksiz ve tekrarlanabilir.

### KOŞULLU

- Vintaj 3–4/5 tarihte erişilebilir; veya
- En fazla iki tarihte `delta_yuzde %5–%15`; veya
- Yayın gecikmesi değişken fakat ek embargo tamponuyla sınırlanabilir.

Bu sonuç feature üretimine otomatik izin vermez; ek güvenlik payı ön-kaydı gerekir.

### KALDI

- İlk tarih veya tarihlerin çoğunluğu için vintaj erişilemiyor (`<3/5`); veya
- Herhangi bir tarihte `delta_yuzde >= %15`; veya
- Erişim ücretli/kimlikli; veya
- Yayın gecikmesi doğrulanamıyor ya da sınırlandırılamayacak kadar tutarsız.

## 6. Stop Kuralları

- BDDK arayüzünde tarihli/arşivlenmiş bülten yoksa ve yalnız bugünkü canlı tablo
  varsa çalışma durur; üçüncü taraf workaround denenmeden `KALDI` yazılır.
- Giriş/ödeme isteyen erişimde çalışma durur.
- En fazla 15 manuel erişimde üçten az tarihe ulaşılırsa bütçe büyütülmez; kısmi
  sonuç raporlanır.

## 7. Zorunlu Çıktılar

- `data/processed/raporlar/bddk_vintaj_karsilastirma.md`
- `data/processed/raporlar/pm_rapor_bddk_erisim_vintaj_fizibilitesi.md`
- `notebooks/bddk_erisim_vintaj_fizibilitesi_ders_kitabi.ipynb`

Hiçbir CSV feature dosyası veya model artefaktı üretilmez. Sonuç ne olursa olsun
feature üretimi başlatılmaz; Pusula ve kullanıcı kararı beklenir.
