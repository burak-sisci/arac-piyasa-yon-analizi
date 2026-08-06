# Nowcast rolling-origin değerlendirme gücü

Pusula'nın Aşama 2 son denetiminde kabul ettiği tek sonraki öncelik uygulanır:
test açmadan ve yeni model/feature eklemeden değerlendirme gücü artırılır.

- Dönem: `2019-01..2025-04`; taslak test `2025-07..2026-06` dışarıda kalır.
- İlk train: 24 ay; her origin genişleyen train, iki ay embargo, tek ay OOF.
- Toplam 50 OOF ay; hafta sırası 1–4 ayrı ölçülür.
- Aynı üç baseline ve aynı dört Model 09 adayı kullanılır; yeni deneme yoktur.
- Birincil birim dört hafta havuzlu ve ay başına toplam ağırlık 1'dir.
- Birincil CI 4 aylık hareketli-blok bootstrap, 2.000 ortak indeks çekilişidir;
  blok=1 i.i.d. yalnız duyarlılık olarak raporlanır.
- Dört modelin `M-2 persistence` karşılaştırmasına Holm–Bonferroni uygulanır.
- Terfi için Holm alt sınırı >0, ΔMCC≥0,05, macro-F1 farkı pozitif ve
  bir-yıl-dışarı jackknife işaretinin her çıkarmada pozitif olması birlikte gerekir.
- Hafta tanısı terfi ailesi dışındadır. Doğrulama için hafta 1→4 MCC azalmayan
  olmalı ve eşli hafta4−hafta1 MCC farkının blok-CI alt sınırı >0 olmalıdır.
- Eksik sınıflı bootstrap çekilişleri atılmaz; oranı ayrıca raporlanır.
