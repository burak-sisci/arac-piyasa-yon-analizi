ROL VE BAĞLAM
Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri mühendisisin. Mevcut durum: veri_2018_bugun_etiketli.csv (2018-01→2026-06, 102 ay) hazır. Görev: TÜM dışsal feature'ları (proxy fiyat ve ENAG HARİÇ) 2015-01'e kadar geriye çekmek.
NET KAPSAM KARARI (proje sahibi onayladı — sorgulamadan uygula):

* Proxy fiyat (BETAM): YENİ KAYNAK ARAYIŞI YOK. 2015-2023 için proxy fiyat aranmayacak. Bu sütunlar 2023-12 öncesinde NaN kalmaya devam edecek — bu zaten bilinen ve kabul edilmiş bir kısıt (2018 genişletmesinde de aynı karar verilmişti).
* ENAG: YENİ KAYNAK ARAYIŞI YOK. ENAG sütunları 2024-01 öncesinde NaN kalacak. ENAG'ın kendisini 2015'e çekme denemesi YAPILMAYACAK.
* TÜM DİĞER feature'lar (kur, TÜFE, taşıt kredisi faizi, politika faizi, ODMD satışları, OSD üretim, noter devir adedi, tüketici güven endeksi, alım gücü proxy'si, ÖTV olayları, erişim endeksi) 2015-01'e kadar GENİŞLETİLECEK.

BAĞLAYICI İLKELER (değişmedi):

* Yalnızca kamuya açık kaynaklar (K5).
* As-of date disiplini korunur; yayım tarihi sütunları tutulmaya devam eder.
* WebSearch/dış kaynaktan gelen rakamlar İKİNCİ bir kaynakla doğrulanmadan kullanılmaz.
* Farklı kaynakların serilerini kontrolsüz birleştirme; zincirleme gerekiyorsa (ör. TÜFE baz değişiklikleri) raporla.
* Veri Git-dışı, kod+rapor commit'lenir.
* EVDS'TEN UZUN ARALIK ÇEKERKEN DİKKAT: Önceki genişletmede (2018) EVDS API'sinin tek istekte dönebileceği satır sayısını sessizce 1000 ile sınırladığı keşfedilmişti (aralık bu sınırı aşarsa en eski kayıtlar sessizce düşüyordu). 2015'e kadar günlük seriler (özellikle USD/TRY ve politika faizi) çekerken bu SINIRI YENİDEN GÖZ ÖNÜNDE BULUNDUR — gerekirse tarih-parçalama (chunking) ile çek, sonucu satır sayısı üzerinden doğrula (beklenen gün sayısına yakın mı kontrol et).

====================================================================== GÖREV 0 — ÖZ-ARŞİVLEME
Bu talimatı prompts/veri/18_genisletme_2015_prompt.md olarak kaydet.
====================================================================== GÖREV 1 — OTONOM: TÜM FEATURE'LARI 2015-01'E GENİŞLET
Aşağıdaki her seri için 2015-01 → 2017-12 arası boşluğu doldur (2018-01 sonrası zaten mevcut):
1a. USD/TRY (TCMB EVDS) — ay sonu + ay ortalaması. Günlük seriden hesaplanıyorsa 1000-satır sınırına dikkat (yukarıdaki uyarı). 1b. TÜFE (TÜİK/EVDS) — endeks + aylık değişim + yayım tarihi. Bu dönemde baz değişikliği varsa (2015-2018 arası TÜİK baz güncellemesi olabilir) tespit et ve ÖNCEKİ genişletmede kullanılan zincirleme yöntemiyle (2025 baz geçişinde uygulanan) tutarlı şekilde ele al. 1c. Taşıt kredisi faizi + politika faizi (TCMB EVDS). 1d. ODMD sıfır araç satışları (toplam/otomobil/HTA). 1e. OSD üretim (binek + kamyonet). 1f. Noter devir adedi (TÜİK) — ÖNEMLİ: önceki genişletmede bu verinin TÜİK bülten-ID tahminine dayandığı ve kırılgan olduğu not edilmişti (Faz 8 raporunda "bülten bul → indir → hardcode et → çapraz doğrula" yöntemi kullanılmıştı). Aynı titiz yöntemi uygula: her bülteni indir, kendi metin cümlesiyle çapraz doğrula, çakışan yıllarda komşu bültenlerle eşleştiğini teyit et. 1g. Tüketici güven endeksi + oto satın alma ihtimali (TÜİK) — önceki genişletmede bu serinin zaten 2012'ye kadar gittiği görülmüştü, yani 2015'e genişletmek muhtemelen sorunsuz olacak, teyit et. 1h. ÖTV/vergi düzenleme olayları (Resmî Gazete) — 2015-2017 arası TÜM düzenlemeleri tarihli event olarak ekle (bu dönemde ÖTV değişikliği olup olmadığını araştır, varsa hepsini bul). 1i. Brüt ücret-maaş endeksi (TÜİK, çeyreklik→aylık) — 2015'e kadar genişlet; ÇEYREKLİKTEN AYLIĞA KOPYALAMA olduğunu (gerçek ay-ay varyasyon olmadığını) veri sözlüğünde tekrar açıkça belirt.
Her seri için kaynak seviyesini (A-E) ve kapsanan gerçek aralığı raporla. Bir seri 2015'e gidemiyorsa (kaynak o tarihte başlamıyorsa), NEREDEN başladığını raporla, uydurma.
====================================================================== GÖREV 2 — ERİŞİM ENDEKSİNİ YENİDEN TÜRET
erisim_endeksi = noter_devir_adedi / alim_gucu_proxy formülü ile, artık 2015'e kadar uzanan iki serinin ORANI olarak yeniden hesapla. Bu türetilmiş bir sütun olduğundan yeni veri çekme gerektirmez, sadece genişletilmiş girdilerle yeniden hesaplama.
====================================================================== GÖREV 3 — BİRLEŞTİRME

* Tüm serileri referans_ayi ile birleştir, tek tablo: 2015-01 → 2026-06 (138 ay).
* Proxy fiyat ve hedef etiket sütunları (nominal/reel/tercile) 2015-2023 arasında NaN kalacak — bu BEKLENEN bir durum, hata değil.
* ENAG sütunları 2015-2023 arasında NaN kalacak — aynı şekilde beklenen.
* Doluluk dökümünü (önceki 05 ve 13 numaralı analizlerdeki format) tüm yeni tabloda güncelle.

====================================================================== GÖREV 4 — KISA KIRMIZI BAYRAK TARAMASI
Yeni eklenen 2015-2017 bölümünde: tarih sürekliliği (36 ay eksiksiz mi), imkânsız değerler (negatif/sıfır), aşırı aylık değişim var mı — kısa kontrol (dakikalar, tam analiz değil).
====================================================================== PM RAPORU — ZORUNLU
data/processed/raporlar/pm_rapor_genisletme_2015.md üret VE oturumda KOPYALANABİLİR DÜZ METİN (markdown kod bloğu) olarak göster.
Başlıklar: (1) Ne yapıldı — her serinin kapsadığı gerçek aralık (tablo). (2) Kırmızı bayrak sonucu. (3) Yeni tablo boyutu (satır×sütun, 2015-01→ 2026-06). (4) Noter devir adedi ve TÜFE baz-geçişi için özel notlar (bu ikisi en kırılgan seriler). (5) Karşılaşılan sorunlar (gizleme). (6) Veri örneği (2015-01, 2015-06, 2017-12, 2018-01 satırları — geçiş noktasını göstermek için). (7) Açık sorular / PM onayı gerekenler.
YAPMA:

* Proxy fiyat (BETAM) için yeni kaynak arama.
* ENAG için yeni kaynak arama veya ENAG'ı 2015'e çekme denemesi.
* Hedef etiketi yeniden üretme (proxy fiyat dönemi değişmediği için hedef zinciri aynı kalır, dokunma).
* Farklı kaynakların serilerini kontrolsüz birleştirme.
* Model/hedef tanımını değiştirme.
