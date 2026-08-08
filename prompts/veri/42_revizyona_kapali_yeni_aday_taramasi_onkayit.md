# Prompt 42 — Revizyona Kapalı Yeni Öncü Aday Taraması Ön-Kaydı

**Tarih:** 2026-08-08

**Karar yöneticisi:** Pusula (`6f4c6fd0-6ddb-4b70-8e45-86d5b6d124c1`, Opus/max)

**Uygulayıcı:** Rota-2

**Tetikleyici:** Model 13 `KAPASITE_DUSUK_ISARET_YOK / HEURISTIK`;
commit `e966b0c`

## 1. Amaç

Prompt 38 kalıbında, mevcut temsilin kapatamadığı gerçek bilgi boşlukları için
yeni ve sınırlı bir masa başı taraması yapılır. En fazla üç aday kartı üretilir;
bu önkayıt anında hiçbir aday seçilmiş değildir.

Yapısı gereği revizyona kapalı seriler — ilk-yayımı nihai değer olan kaynaklar —
sıralamada önce gelir. Bu kaynaklarda as-of doğrulaması daha ucuzdur ve sonraki
ön-eleme, belgeyle doğrulanabilirse `HEURISTIK` yerine `KESIN` kesinlikte
yorumlanabilir.

## 2. Değişmeyen proje sözleşmesi

- Target: `noter_devir_otomobil_adet`.
- Sınıflar: `down / stable / up`; kapalı stable bandı ±%5.
- Ürün: haftalık güncellenen cari-ay kapanış yönü nowcast'i.
- Bilgi disiplini: M−2; iki aylık embargo.
- Kilitli test: `2025-07..2026-06`, açılmaz.
- Hedef/sınıf/band/ufuk/K kararı değişmez.

## 3. Yeniden taranmayacak adaylar

Aşağıdaki üç kart tüketilmiştir ve bu turda yeniden açılmaz:

1. BDDK haftalık taşıt kredisi — Model 12/13 sonunda normal yeniden-açma
   önceliğiyle `ONCELIK_DUSURULDU`.
2. BETAM–sahibindex — gerçek ilk-yayım geçmişi mevcut rolling-origin kapsamına
   yetmediği için elendi.
3. Google Trends — örnekleme/yeniden ölçekleme ve vintaj yeniden-üretim riski
   nedeniyle geriye dönük test için elendi.

Bu kaynakların kardeş göstergesi ancak ekonomik mekanizması ve revizyon niteliği
gerçekten farklıysa yeni aday sayılabilir; aynı serinin başka dönüşümü aday
değildir.

## 4. Gerçek bilgi boşluğu kapısı

Her aday `notebooks/karar_lab_02_bilgi_kumesi_genislet.ipynb` kapsam tablosunda
`mevcut_temsilde_var=False` olan bir aileye düşmelidir. Mevcut USD/EUR patikası,
faiz, TÜFE, hedef lagları, takvim veya ÖTV olay feature'larının yalnız başka bir
dönüşümü yeni aile sayılmaz.

Ekonomik mekanizma tek cümlede doğrudan hacim yönü nowcast problemine
bağlanmalıdır. Mekanizma belgelenemiyor veya mevcut feature'ın yeniden
ifadesiyse aday elenir.

## 5. Aday kartı şeması

Her kart şu alanları taşır; bulunmayan bilgi tahmin edilmez, `doğrulanmadı`
yazılır:

1. `aday_adi`
2. `kaynak_sahibi`
3. `ham_frekans`
4. `ilk_tarih`
5. `yayin_gecikmesi_gun`
6. `M_eksi_2_aninda_erisim`
7. `revizyon_politikasi`
8. `revizyona_kapali_mi` — `evet / hayır / doğrulanmadı`, kaynaklı
9. `kapatilan_bilgi_boslugu`
10. `mekanizma_bir_cumle`
11. `mevcut_featuredan_neden_farkli`
12. `hukuki/erişim_riski`
13. `as_of_vintage_riski`
14. `on_hukum`

## 6. İzin ve bütçe

- Yalnız kamuya açık dokümantasyon, metaveri ve yayın sayfası okunabilir.
- Toplam erişim bütçesi **en fazla 10 sayfa**dır.
- Kaynak başına mümkünse birincil/resmî sayfa kullanılır.
- Masa başı bulgusu tarih, kapsam, frekans ve revizyon iddialarında kaynakla
  desteklenir.

## 7. Yasaklar

- Veri indirme, dosya/seri çekme, scraping veya API çağrısı.
- Feature üretimi, model fit, permütasyon, bootstrap veya test erişimi.
- Ücretli/kimlikli servis, API anahtarı, dış kişi/kuruma mesaj.
- Hedef, sınıf, ±%5 band, ufuk veya K/N sözleşmesi değişikliği.
- BDDK/BETAM/Google Trends kartlarını yeniden tarama.
- Kullanıcının dirty/untracked dosyalarına dokunma.
- Dördüncü adayı zorla üretme.

## 8. Kabul kapıları ve stop

- En az bir, en fazla üç kaynaklı aday kartı üretilir.
- Her kart alanı dolu veya açıkça `doğrulanmadı`dır.
- Her aday gerçek bir `False` bilgi boşluğunu kapatır.
- `revizyona_kapali_mi` alanı kaynakla gerekçelendirilir; `doğrulanmadı`
  sonucu kabul edilebilir fakat sonraki as-of aşamasına koşullu taşınır.
- İlerletilen/elenecek adaylar gerekçeli ve karşılaştırmalı yazılır.
- Bu aşamada gerçek veri erişimi başlamaz.

Revizyona kapalı hiçbir uygun aile bulunamazsa aday zorlanmaz; `BU_TURDA_UYGUN_ADAY_YOK`
hükmü yazılır ve tarama durur.

## 9. Zorunlu artefaktlar

- Bu önkayıt — sonuçlardan önce ayrı commit.
- `data/processed/raporlar/revizyona_kapali_yeni_aday_kartlari.md`.
- `data/processed/raporlar/pm_rapor_revizyona_kapali_yeni_aday_taramasi.md`
  — yedi zorunlu başlık.
- `notebooks/revizyona_kapali_yeni_aday_taramasi_ders_kitabi.ipynb`.
- README Aşama B durum güncellemesi.

Masa başı taraması tamamlanınca Pusula Opus/max sonuç/öncelik denetimi yapar.
Gerçek veri erişimi, taramayı geçen aday için ayrı küçük aşama ve ayrı önkayıtla
başlatılır.
