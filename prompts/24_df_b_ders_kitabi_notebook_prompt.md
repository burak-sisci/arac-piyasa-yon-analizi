ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinde bir EĞİTMEN rolündesin.
Görev: DF-B veri setini (data/processed/dataframes/
df_b_zengin_2024_bugun_v2.csv veya en güncel sürümü — pm_rapor_sutun_
temizlik_korelasyon.md'deki nihai hale göre 30 satır × 25 sütun) ele alan,
DERS KİTABI niteliğinde bir Jupyter Notebook (.ipynb) hazırlamak. Bu,
DF-A notebook'unun (23 numaralı görev) KARDEŞ dosyasıdır — aynı format
ilkelerini izler ama DF-B'nin KENDİNE ÖZGÜ konularına (BETAM, ENAG, az
gözlem) odaklanır.

HEDEF KİTLE: Projeye veri bilimi altyapısı olmayan ama öğrenmeye istekli
proje sahibi. DF-A notebook'unu daha önce okumuş olabileceğini varsay —
DF-A'da anlatılan temel kavramları (korelasyon, log-değişim, zaman serisi)
TEKRARLAMA, sadece kısa hatırlatma yap ve YENİ olan konulara (az gözlem,
BETAM/ENAG, iki kaynağın karşılaştırılması) derinlemesine gir.

KESİN KURAL: Notebook, ARTIK SİLİNMİŞ hiçbir sütuna (otv_aciklama,
proxy_yon_*, kullanilan_sigma_*, odmd_toplam_adet, odmd_hta_adet,
osd_binek_kamyonet_toplam_adet, osd_kamyonet_adet, erisim_endeksi,
brut_ucret_maas_endeksi_2021_100, otv_event_ay_mi,
otv_ay_farki_en_yakin_olay) REFERANS VERMEYECEK. Notebook'u yazmadan önce
DF-B'nin GERÇEK, GÜNCEL sütun listesini kodla oku ve ona göre yaz — varsayma.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/24_df_b_ders_kitabi_notebook_prompt.md olarak kaydet.

======================================================================
FORMAT İLKESİ (DF-A notebook'uyla AYNI, tekrar)
======================================================================
Her kavram/adım için üç aşamalı anlatım: (1) günlük dilde açıklama
(markdown), (2) kod (yorum satırlı), (3) yorum (çıktının altında, sade
dille "bu bize ne söylüyor"). Yeni terimler "📖 Terim" kutusuyla tanımlanır.

======================================================================
NOTEBOOK YAPISI (bölüm bölüm, tam sıra)
======================================================================

## BÖLÜM 1 — Bu Veri Seti Ne, DF-A'dan Farkı Ne
- DF-B'nin ne olduğu: 2024-01'den bugüne, BETAM'ın verilerinin (proxy
  fiyat, ilanda kalma süresi, satış oranı) VE ENAG'ın (bağımsız enflasyon
  ölçümü) dahil olduğu, ama daha kısa (30 ay) pencere.
- DF-A ile yan yana kıyaslama tablosu: "DF-A = uzun ama dar, DF-B = kısa
  ama geniş" — bir cümlede özetleyen basit bir görsel/tablo.
- İlk satırları göster, boyutunu göster.

## BÖLÜM 2 — 📖 Temel Kavram: Neden İki Ayrı Tablo Kullanıyoruz
- Bir örnekle anlat: "Bir arkadaşının son 30 günkü ruh halini çok detaylı
  biliyorsun ama 10 yıllık genel karakterini kabaca biliyorsun; bir
  başkasının 10 yıllık genel karakterini biliyorsun ama son 30 gününü
  bilmiyorsun. İkisi de değerli, farklı sorulara cevap verir."
- Bu ayrımın projeye faydası: kısa-ama-zengin veri (DF-B) ile "acaba fiyat
  ve piyasa hızı ile noter devri ilişkili mi" sorusunu; uzun-ama-dar veri
  (DF-A) ile "genel trend/mevsimsellik ne" sorusunu cevaplıyoruz.

## BÖLÜM 3 — YENİ Sütunlarla Tanışma (BETAM ve ENAG)
Yalnızca DF-A'da OLMAYAN, DF-B'ye ÖZGÜ sütunları ele al (GERÇEK, güncel
listeden doğrula — muhtemelen: proxy_dom_gun, proxy_satis_orani_pct,
proxy_fiyat_cari_tl, proxy_nominal_aylik_pct, proxy_reel_aylik_pct,
proxy_aylik_log_degisim, proxy_reel_aylik_log_degisim, enag_aylik,
enag_yillik). DF-A ile ortak olan sütunları (kur, TÜFE, faiz, ODMD, OSD,
güven, noter devri) SADECE İSİM OLARAK an, tekrar detaylandırma ("bunları
DF-A notebook'unda görmüştün" diye kısaca hatırlat).

Her YENİ sütun için:
- Ne ölçtüğü (BETAM nedir, ENAG nedir — kısaca kurumları tanıt).
- describe() + basit çizgi grafik + yorum.
- proxy_dom_gun, proxy_satis_orani_pct, proxy_fiyat_cari_tl'nin İKİ ay
  (2024-05, 2025-02) eksik olduğunu göster, NEDEN eksik olduğunu (BETAM o
  ay rapor yayımlamadı) anlat — grafikte bu boşluğu görsel olarak işaretle.

## BÖLÜM 4 — 📖 Temel Kavram: Az Gözlemle Çalışmanın Riski
- Basit bir örnekle anlat: "3 kere yazı-tura attın, 3'ü de yazı geldi diye
  'bu para hep yazı gelir' diyemezsin — çok az deneme yaptın. 1000 kere
  atsan daha güvenilir bir fikrin olur."
- DF-B'nin sadece 30 satır (ay) olduğunu, bunun bazı istatistiksel
  sonuçları (özellikle korelasyon) daha az güvenilir kıldığını anlat.
- 📖 Terim kutusu: "Gözlem sayısı (n)" — her satırın bir "gözlem" (bir
  ayın verisi) olduğunu, n arttıkça güvenin arttığını basitçe anlat.

## BÖLÜM 5 — İki Bağımsız Enflasyon Ölçümü: TÜİK ve ENAG
- ENAG'ın neden var olduğunu (resmi TÜİK rakamlarına bağımsız bir alternatif
  ölçüm) sade dille anlat — siyasi yorum yapmadan, sadece "iki farklı
  kurum, iki farklı yöntemle enflasyonu ölçüyor" çerçevesinde.
- İkisini aynı grafikte üst üste çiz (yıllık enflasyon oranları) — YORUM:
  aradaki fark ne kadar, zamanla yakınlaşıyor mu uzaklaşıyor mu.
- Bu iki ölçümün neden "birleştirilmediğini", ayrı sütunlar olarak
  tutulduğunu (çapraz kontrol amaçlı) anlat.

## BÖLÜM 6 — Log-Değişim Korelasyonu (DF-A'daki yöntemin DF-B'ye uygulanışı)
- DF-A notebook'unda öğrenilen yöntemi (ham seviye yerine log-değişim
  kullanma) burada KISACA hatırlat, tekrar öğretme.
- DF-B'nin TÜM sayısal sütunlarının log-değişim korelasyon matrisini
  hesapla, heatmap çiz.
- noter_devir_toplam_adet / noter_devir_otomobil_adet'in TÜM diğer
  sütunlarla (özellikle YENİ BETAM/ENAG sütunlarıyla) korelasyonunu ayrı
  bir tabloda vurgula.
- YORUM: en güçlü ilişkiler hangileri, az-gözlem uyarısını (Bölüm 4) bu
  sonuçlara nasıl uygulamamız gerektiğini hatırlat (yüksek korelasyon
  görünse bile 30 gözlemle temkinli yorumlanmalı).

## BÖLÜM 7 — Stratejik Çıkarımlar (Bu Bölüm Kritik)
- Bulgulara dayanarak sade dille: "Bu zengin ama kısa veriyle şunları
  yapabiliriz" listesi.
- DF-A ile DF-B'nin bulgularının TUTARLI olup olmadığını karşılaştır (aynı
  feature, iki farklı tabloda benzer bir ilişki gösteriyor mu — gösteriyorsa
  bu güven artırır, göstermiyorsa bu bir uyarı işaretidir).
- "Bir sonraki adım ne olabilir" önerisi (KARAR VERME, sadece olası
  yönleri listele).

======================================================================
YAPMA
======================================================================
- Silinen sütunlara referans verme.
- DF-A notebook'unda zaten öğretilen temel kavramları (korelasyon nedir,
  log-değişim nedir gibi) sıfırdan yeniden öğretme — kısa hatırlatma yeterli.
- Kalıcı veri dosyasını değiştirme.
- Hedef/model kararı verme.
- Aşırı teknik jargon kullanma.

======================================================================
ÇIKTI
======================================================================
- Dosya: notebooks/df_b_ders_kitabi.ipynb
- Repoya commit'le.
- PM raporu (data/processed/raporlar/pm_rapor_df_b_notebook.md) üret VE
  oturumda KOPYALANABİLİR DÜZ METİN olarak göster: (1) notebook'ta kaç
  bölüm/hücre var, (2) hangi YENİ sütunlar ele alındı, (3) DF-A ile
  tutarlılık karşılaştırması sonucu, (4) en çarpıcı 2-3 bulgu, (5)
  karşılaşılan sorunlar, (6) açık sorular.
