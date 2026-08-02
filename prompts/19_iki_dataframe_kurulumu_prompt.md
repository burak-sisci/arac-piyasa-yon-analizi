ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Ekip liderinin talimatıyla, bundan sonraki tüm deneylerin
üzerine kurulacağı İKİ AYRI, NET TANIMLI veri seti oluşturuyoruz. Bu bir
analiz görevi DEĞİLDİR — sadece iki temiz DataFrame'i üretip kaydetmek.

BAĞLAM (eksik_sutun_nedenleri.md raporundan): Omurga tabloda
(veri_2018_bugun_etiketli.csv) 74/102 ayda BETAM kaynaklı sütunlar
(proxy_fiyat_cari_tl, proxy_dom_gun, proxy_satis_orani_pct ve bunlardan
türeyen 4 değişim sütunu) eksik, çünkü BETAM verisi yalnızca 2023-12'den
itibaren düzenli yayımlanıyor. Bu, iki DataFrame ayrımının kök nedenidir.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/19_iki_dataframe_kurulumu_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — DF-A (GENİŞ): 2018-01 → BUGÜN
======================================================================
- Kaynak: data/processed/genisletme/veri_2018_bugun_etiketli.csv (olduğu
  gibi, satır/sütun eklemeden veya çıkarmadan).
- BETAM kaynaklı sütunlar (proxy_fiyat_cari_tl, proxy_dom_gun,
  proxy_satis_orani_pct, proxy_kaynak, proxy_yayim_ayi,
  proxy_fiyat_arabamcom_referans_tl, proxy_nominal_aylik_pct,
  proxy_reel_aylik_pct, proxy_aylik_log_degisim,
  proxy_reel_aylik_log_degisim) 2023-12 öncesinde NaN kalmaya devam
  edecek — BU BEKLENEN VE KORUNMASI GEREKEN BİR DURUM, doldurma/silme YOK.
- Bu DataFrame'i data/processed/dataframes/df_a_genis_2018_bugun.csv olarak
  kaydet.
- Kapsam: tüm feature'lar (kur, TÜFE, ENAG, faiz, ODMD, OSD, noter, güven,
  alım gücü, erişim endeksi, ÖTV olayları) + BETAM'lı sütunlar (kısmi dolu).

======================================================================
GÖREV 2 — DF-B (DAR/TEMİZ): BETAM BAŞLANGICI → BUGÜN
======================================================================
- DF-A'dan başlayarak, yalnızca BETAM'ın (proxy_fiyat_cari_tl bazlı)
  DOLU olduğu satırları (aylar) filtrele. BETAM'ın gerçek başlangıcı
  2023-12'dir — ama 2024-05 ve 2025-02'de BETAM rapor yayımlamadığı için
  bu iki ay da otomatik olarak dışarıda kalacak (proxy_fiyat_cari_tl NaN
  olduğu için filtre onları eler). BU DOĞRU VE BEKLENEN DAVRANIŞ —
  "temiz pencere" tanımı gereği, BETAM'ın olmadığı hiçbir ay bu tabloda
  YOK.
- Bu filtrelemeden SONRA, DF-B'deki TÜM sütunların gerçekten %100 dolu
  olup olmadığını DOĞRULA (özellikle ENAG sütunları — ENAG 2024-01'den
  itibaren dolu olduğundan BETAM'ın 2023-12 ayı için ENAG NaN kalabilir,
  bunu tespit et ve raporla).
- Bu DataFrame'i data/processed/dataframes/df_b_dar_betam_bugun.csv olarak
  kaydet.

======================================================================
GÖREV 3 — DOĞRULAMA VE RAPORLAMA
======================================================================
- DF-A boyutu: satır × sütun, tarih aralığı.
- DF-B boyutu: satır × sütun, tarih aralığı, kaç ay BETAM boşluğu nedeniyle
  dışarıda kaldı (isim isim listele: hangi aylar).
- DF-B'de HÂLÂ eksik kalan bir sütun varsa (yukarıdaki ENAG-2023-12 durumu
  gibi) bunu açıkça raporla — DF-B "tamamen eksiksiz" olmayabilir, gerçek
  durumu olduğu gibi göster.
- İki DataFrame'in de VERİ SÖZLÜĞÜNÜ güncelle (data/processed/dataframes/
  veri_sozlugu_df_a_df_b.md): hangi sütunlar hangi DataFrame'de tam,
  hangilerinde kısmi.

======================================================================
YAPMA
======================================================================
- Hiçbir boşluğu enterpolasyon/doldurma ile kapatma (bu ayrı bir karar,
  bu görevin kapsamında değil).
- Yeni feature türetme, korelasyon analizi, model kurma (sonraki adımlar).
- Hedef değişkeni değiştirme.
- Omurga tabloyu (veri_2018_bugun_etiketli.csv) değiştirme — yalnızca ondan
  türetilmiş iki YENİ dosya oluşturuluyor, kaynak dosya olduğu gibi kalır.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_iki_dataframe.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN (markdown kod bloğu) olarak göster.

Başlıklar: (1) Ne yapıldı. (2) DF-A boyutu ve kapsamı. (3) DF-B boyutu,
kapsamı, dışarıda kalan aylar (isim isim). (4) DF-B'de doğrulama sonrası
hâlâ eksik kalan sütun var mı (varsa hangileri, neden). (5) Karşılaşılan
sorunlar. (6) Veri örneği: DF-A'dan 3 satır (biri 2018, biri 2023 öncesi,
biri 2024 sonrası) + DF-B'den ilk 3 ve son 3 satır. (7) Açık sorular / PM
onayı gerekenler.
