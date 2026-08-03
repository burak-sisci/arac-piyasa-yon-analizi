ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinde artık bir EĞİTMEN
rolündesin. Görev: DF-A veri setini (data/processed/dataframes/
df_a_kapsama_testli_v2.csv veya en güncel sürümü — pm_rapor_sutun_
temizlik_korelasyon.md'deki nihai hale göre 102 satır × 16 sütun) ele alan,
DERS KİTABI niteliğinde bir Jupyter Notebook (.ipynb) hazırlamak.

HEDEF KİTLE: Projeye veri bilimi altyapısı olmayan ama öğrenmeye istekli
proje sahibi. Notebook'u baştan sona okuyunca (a) bu verinin ne olduğunu,
(b) matematiksel/istatistiksel temelleri, (c) bu veriyle hangi stratejik
kararların alınabileceğini anlayabilmeli.

KESİN KURAL: Notebook, ARTIK SİLİNMİŞ hiçbir sütuna (otv_aciklama,
proxy_yon_*, kullanilan_sigma_*, odmd_toplam_adet, odmd_hta_adet,
osd_binek_kamyonet_toplam_adet, osd_kamyonet_adet, erisim_endeksi,
brut_ucret_maas_endeksi_2021_100, otv_event_ay_mi,
otv_ay_farki_en_yakin_olay) REFERANS VERMEYECEK. Notebook'u yazmadan önce
DF-A'nın GERÇEK, GÜNCEL sütun listesini kodla oku ve ona göre yaz — varsayma.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/23_df_a_ders_kitabi_notebook_prompt.md olarak kaydet.

======================================================================
FORMAT İLKESİ (HER BÖLÜM İÇİN GEÇERLİ)
======================================================================
Her kavram/adım için ÜÇ AŞAMALI anlatım kullan:
1. GÜNLÜK DİLDE AÇIKLAMA (markdown hücresi): "Şimdi ne yapıyoruz ve neden"
   — teknik terim kullanmadan, bir arkadaşına anlatır gibi.
2. KOD (kod hücresi): çalıştırılabilir, yorum satırlarıyla (# ...)
   açıklanmış Python kodu. Her satırın ne işe yaradığı kod içi yorumla
   belirtilsin.
3. YORUM (markdown hücresi, kod çıktısının hemen altında): "Bu sonuç bize
   ne söylüyor" — çıkan sayı/grafiği yorumla, "bu iyi mi kötü mü, ne
   anlama geliyor" diye açıkla.

Her yeni matematiksel/istatistiksel terim İLK GEÇTİĞİ YERDE bir "📖 Terim"
kutusu (markdown blockquote) ile tanımlansın — günlük dilde, örnekle.

======================================================================
NOTEBOOK YAPISI (bölüm bölüm, tam sıra)
======================================================================

## BÖLÜM 1 — Bu Veri Seti Ne, Neden Var
- DF-A'nın ne olduğu: 2015'ten bugüne, noter devrinin kapsadığı en geniş
  pencere, bu pencerede TAM DOLU olan sütunlardan oluşuyor (BETAM/ENAG
  kaynaklı sütunlar burada YOK çünkü onlar 2024'ten başlıyor — bunu açıkça
  anlat, DF-B'nin varlık sebebini de bir cümleyle bağla).
- Projenin genel amacı (araç piyasasını önden görmek) ile bu tablonun
  ilişkisi.
- İlk satırları göster (df.head()), boyutunu göster (kaç satır kaç sütun).

## BÖLÜM 2 — Sütun Sütun Tanışma
Her sütun için (GERÇEK, güncel listeden — muhtemelen: referans_ayi,
usdtry_aysonu, usdtry_ortalama, tufe_endeks, tufe_aylik_degisim,
tufe_yillik_degisim, tufe_yayim_tarihi, tasit_kredisi_faiz, politika_faizi,
odmd_otomobil_adet, osd_binek_adet, tuketici_guven_endeksi,
otomobil_satinalma_ihtimali_endeksi, noter_devir_toplam_adet,
noter_devir_otomobil_adet, alim_gucu_ceyrek — GERÇEK LİSTEYİ KODLA DOĞRULA):
- Ne ölçtüğü (1-2 cümle, günlük dil).
- Hangi kurumdan geldiği.
- Basit bir istatistik özet (df['sutun'].describe()) + YORUMU: "bu sayı
  normal mi, ne anlama geliyor".
- Basit bir çizgi grafik (zaman içinde bu sütunun seyri) + YORUMU.

## BÖLÜM 3 — 📖 Temel Kavram: Zaman Serisi Nedir
- Zaman serisinin ne olduğunu bir örnekle (örn. "her ay kilonu tartıp not
  etsen, bu bir zaman serisi olur") anlat.
- Neden bizim verimiz bir zaman serisi (aylık, sıralı, birbirine bağlı).
- Trend, mevsimsellik gibi kavramları BASİTÇE tanıt (örnek: "yıllar içinde
  genel olarak artıyor mu azalıyor mu — buna trend deriz").

## BÖLÜM 4 — Hedefimiz: Noter Devir Adedi
- noter_devir_toplam_adet ve noter_devir_otomobil_adet'i özel olarak ele al
  — bunlar neden HEDEF (bu ay kaç araç el değiştirdi, gelecekte artacak mı
  azalacak mı).
- Grafik: yıllar içindeki seyri (büyük, net bir çizgi grafik).
- 📖 Terim kutusu: "Trend" — grafiğe bakarak seri sürekli mi artıyor,
  YORUMLA (artıyorsa bunun projeye ne anlama geldiğini — "hep yukarı"
  tuzağı riskini — anlat, bkz. ekip lideri talimatı).

## BÖLÜM 5 — 📖 Temel Kavram: Korelasyon Nedir
- Günlük hayat örneğiyle anlat (örn. "dondurma satışı ile hava sıcaklığı
  birlikte artıyorsa, aralarında korelasyon var deriz").
- Korelasyon katsayısının (-1 ile +1 arası) ne anlama geldiğini basitçe
  anlat: +1 = birlikte artıyorlar, -1 = biri artarken diğeri azalıyor,
  0 = ilişki yok.
- 📖 Terim kutusu: "Sahte (spurious) korelasyon" — iki şeyin birlikte
  hareket etmesinin her zaman biri diğerini ETKİLİYOR anlamına gelmediğini,
  ikisinin de ayrı bir üçüncü sebepten (örn. genel zaman trendinden)
  etkilenebileceğini bir örnekle (basit ve tanıdık bir örnek seç) anlat.

## BÖLÜM 6 — Ham Seviye Korelasyon (ve Neden Tek Başına Yeterli Değil)
- DF-A'daki tüm sayısal sütunların HAM DEĞERLERİ üzerinden korelasyon
  matrisini hesapla, ısı haritası (heatmap) çiz.
- YORUM: hangi çiftler yüksek çıktı, bunun "gerçek" bir ilişki mi yoksa
  "ikisi de zamanla artıyor" sahte etkisi mi olabileceğini tartış (kur ve
  TÜFE örneğini kullan — ikisi de yıllar içinde büyüyor).

## BÖLÜM 7 — 📖 Temel Kavram: Aylık Değişim / Log-Değişim
- Neden "ham seviye" yerine "bir önceki aya göre ne kadar değişti"ye
  bakmanın daha doğru olduğunu anlat (trend etkisini elemek için).
- Yüzde değişim ile "log-değişim" arasındaki farkı BASİTÇE anlat (ikisi
  küçük değişimlerde neredeyse aynı sonucu verir, log-değişim matematiksel
  olarak biraz daha "adil" simetriye sahiptir — teknik detaya girmeden).
- Kod: her ana sayısal sütunun aylık log-değişimini hesapla, yeni geçici
  sütunlar oluştur (kalıcı dosyayı DEĞİŞTİRME, sadece notebook içinde
  göster).

## BÖLÜM 8 — Log-Değişim Korelasyonu (Asıl Anlamlı Analiz)
- Aynı korelasyon matrisini şimdi log-değişim serileriyle tekrar hesapla,
  heatmap çiz.
- YORUM: Bölüm 6'daki sonuçlarla karşılaştır — hangi ilişkiler "eridi"
  (sahte çıktı), hangileri hâlâ güçlü kaldı (muhtemelen gerçek ilişki).
- noter_devir_toplam_adet / noter_devir_otomobil_adet'in diğer TÜM
  sütunlarla log-değişim korelasyonunu ayrı bir tablo/grafikte özellikle
  vurgula (bu, hedefe en yakın sinyalleri gösterir).

## BÖLÜM 9 — Stratejik Çıkarımlar (Bu Bölüm Kritik)
- Bulgulara dayanarak, sade dille: "Bu veriyle şunları yapabiliriz" listesi.
- Hangi feature'lar hedefle (noter devri) en güçlü log-değişim ilişkisi
  gösteriyor — bunları öne çıkar.
- Az-gözlem/kısa-seri uyarısını (varsa) sade dille tekrarla.
- "Bir sonraki adım ne olabilir" önerisi (ama KARAR VERME, sadece olası
  yönleri listele — feature seçimi, model kurma gibi kararlar proje
  sahibine ait).

======================================================================
YAPMA
======================================================================
- Silinen sütunlara referans verme (yukarıda tekrar vurgulandı).
- Kalıcı veri dosyasını değiştirme (notebook salt-okunur bir keşif aracı).
- Hedef/model kararı verme — sadece bulguyu sun, yorumu sade dille yap,
  "ne yapmalı" kararını proje sahibine bırak.
- Aşırı teknik jargon kullanma; her terim ilk geçtiğinde tanımlanmalı.

======================================================================
ÇIKTI
======================================================================
- Dosya: notebooks/df_a_ders_kitabi.ipynb
- Repoya commit'le.
- PM raporu (data/processed/raporlar/pm_rapor_df_a_notebook.md) üret VE
  oturumda KOPYALANABİLİR DÜZ METİN olarak göster: (1) notebook'ta kaç
  bölüm/hücre var, (2) hangi sütunlar ele alındı (gerçek liste), (3) en
  çarpıcı 2-3 bulgu özet olarak, (4) karşılaşılan sorunlar, (5) açık
  sorular.
