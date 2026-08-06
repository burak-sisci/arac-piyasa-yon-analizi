# Haftalık güncellenen aylık hacim yönü nowcast geliştirmesi

## Proje sahibinin talebi

Target olarak noter otomobil satış/devir adedini taşıyan
`noter_devir_otomobil_adet` sütunu seçildi. Bu sütun üzerinden
`up/stable/down` olmak üzere üç sınıflı tahmin yürütülecek. Sinyal,
gelecekte araç piyasasının hızına ilişkin bilgi sağlayacak.

İlk talepte tahmin periyodu “bu haftaya göre gelecek hafta” olarak
tanımlandı. Rota ve salt-okunur karar ortağı Pusula, target'ın resmi olarak
aylık olması ve günlük tabloda aylık değerin günlere aynen kopyalanması
nedeniyle gerçek haftalık target üretimini veri uydurma/pseudo-replikasyon
riskiyle reddetti.

Proje sahibinin 2026-08-06 tarihli bağlayıcı seçimi:

> Her hafta tahmin üretelim; hedef, içinde bulunulan ayın sonunda noter
> otomobil devir yönünün up/stable/down olmasıdır. Yani haftalık güncellenen
> aylık nowcast.

## Sabit kararlar

- Target: `noter_devir_otomobil_adet`.
- Çıktı: `up`, `stable`, `down` olmak üzere üç sınıf.
- Tahmin ürünü: Her hafta, yalnız o tarihe kadar bilinen verilerle içinde
  bulunulan ayın kapanış yönü için nowcast.
- Aylık target haftalıkmış gibi bölünmeyecek veya enterpole edilmeyecek.
- Aynı aya ait haftalık snapshot'lar bağımsız target gözlemi sayılmayacak;
  split ay bazında ve değerlendirme ay-eşit yapılacak.
- Uzak repoya push yapılmayacak; `main` dalı değiştirilmeyecek.
- Çalışma yalnız yerel `gelistirme/haftalik-aylik-nowcast` dalında yürütülecek.
- Pusula yalnız karar desteği sunacak; kodlama, test, raporlama ve Git
  işlemlerinin tamamını Rota yapacak.

## İlk aşama

Pahalı model eğitiminden önce veri uygunluğu, gerçek yayın-zamanı/cut-off
kuralları, haftalık snapshot üretimi, etiket hizalaması, grup bazlı
kronolojik doğrulama ve naif baseline sözleşmesi tasarlanıp birim testlerle
doğrulanacak. Mevcut kullanıcı değişikliklerine dokunulmayacak.
