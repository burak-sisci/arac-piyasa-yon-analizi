# Prompt 38 — Öncü Bilgi Adayı Masa Başı Taraması

**Tarih:** 2026-08-08

**Kaynak kullanıcı talimatı:** “Projeye devam edeceğiz. Pusula ile çalışmaya başlayın.”

**Karar ortağı:** Pusula (`6f4c6fd0-6ddb-4b70-8e45-86d5b6d124c1`)

**Uygulayıcı:** Rota-2

## Bağlayıcı yön

Pusula, Model 11 sonrasında **Seçenek 2** yönünü seçti:

- `noter_devir_otomobil_adet` hedefi korunur.
- `down / stable / up` üç sınıfı ve ±%5 stable bandı korunur.
- Haftalık güncellenen cari-ay nowcast sözleşmesi korunur.
- Mevcut temsilde bulunmayan öncü bilgi aileleri masa başında araştırılır.

## Bu küçük aşamanın kapsamı

`notebooks/karar_lab_02_bilgi_kumesi_genislet.ipynb` içindeki
`mevcut_temsilde_var=False` boşluklardan en fazla üçü için aday kartı hazırlanır.

İzin verilenler:

- Kamuya açık kaynak ve dokümantasyon sayfalarını okumak.
- Kaynak sahibi, frekans, tarihsel kapsam, yayın gecikmesi, M−2 erişimi,
  revizyon/vintaj riski, mekanizma ve mevcut feature setinden farkı kaydetmek.
- Bilinmeyen alanları açıkça “doğrulanmadı” diye işaretlemek.
- Yalnız yeni dosyalarda notebook ve PM denetim izi üretmek.

Yasaklar:

- Veri indirme, scraping veya API çağrısı.
- Model fit'i, permütasyon veya bootstrap.
- Kilitli `2025-07..2026-06` testine erişim.
- Hedef, sınıf, ufuk, band veya K/N kararı değişikliği.
- Kullanıcıya ait mevcut dirty/untracked dosyalara dokunmak.

## Kabul kapıları

1. En az bir, en fazla üç kaynaklı aday kartı.
2. Her aday gerçek bir `False` bilgi ailesine karşılık gelmeli.
3. Bilinmeyen/as-of riski saklanmamalı.
4. Hangi adayın ilerletildiği veya elendiği gerekçeli olmalı.
5. Gerçek veri erişimi/toplama aşaması kullanıcı onayı olmadan başlamamalı.
