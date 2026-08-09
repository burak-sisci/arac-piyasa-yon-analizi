# Prompt 47 — Model 14–17 Performans Terminal Sentezi

**Tarih:** 2026-08-09

## Kullanıcı Talimatı

> model performansını artırma odaklı çalışalım. bize lazım olan performans
> metriklerinin çok altındayız.

> otonom bir çalışma istiyorum. ben dönene kadar durmayın.

## Görev

Model 14–17'nin ön-kayıt, kod, test ve test-dışı rolling-origin sonuçlarını tek
kanıt zincirinde sentezle. Aynı 50 origin üzerinde yeni algoritma/feature/
threshold denemesinin bilimsel durdurma sınırını yaz. En iyi geliştirme adayını
gelecekteki bağımsız doğrulama için dondur; kilitli testi açma. Yeni bilgi,
bağımsız ay veya hedef değişikliği seçeneklerinden hangilerinin kullanıcı
kararı gerektirdiğini açıkça ayır. PM raporu, doküman ve README üret; commit ve
`origin/main` push yap.

## Sınırlar

- K9/K10 ve kilitli test değişmez.
- Kullanıcının dirty/untracked dosyalarına dokunulmaz.
- Yeni model koşturulmaz.
- Pusula Sonnet/xhigh terminal incelemesi istenir; kota engeli varsa açıkça
  kaydedilir ve mevcut kanıtla Rota-2 sentezi tamamlanır.
