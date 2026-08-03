ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Önceki görevde (19 numaralı) kurulan DF-A ve DF-B artık
İSTENMİYOR — proje sahibi yeni bir mantıkla iki YENİ DataFrame istiyor.
ESKİ MANTIK: "sütun kısmen doluysa NaN'larla birlikte dahil et." YENİ
MANTIK: "sütun, hedef pencereyi TARİHSEL OLARAK KAPSIYOR mu (başlangıç
tarihi yeterince eski mi) — kapsıyorsa dahil et (içindeki tekil/ara
boşluklar sorun değil, sonra doldurulacak), kapsamıyorsa (o pencerede
YAPISAL olarak hiç var olmuyorsa, ör. BETAM'ın 2024 öncesi) sütunu HİÇ
ALMA."

======================================================================
GÖREV 0 — ESKİ DOSYALARI TEMİZLE
======================================================================
- data/processed/dataframes/df_a_genis_2015_bugun.csv (+ .xlsx) SİL.
- data/processed/dataframes/df_b_dar_betam_bugun.csv (+ .xlsx) SİL.
- data/processed/dataframes/veri_sozlugu_df_a_df_b.md SİL (yeniden
  üretilecek).
- Bu talimatı prompts/21_dataframe_yeniden_kurulum_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — NOTER DEVRİ SERİSİNİN BAŞLANGIÇ TARİHİNİ TESPİT ET
======================================================================
Omurga tablosunda (veri_2015_bugun_etiketli.csv) noter_devir_toplam_adet
(veya otomobile özgü varsa noter_devir_otomobil_adet) sütununun İLK DOLU
olduğu ayı bul. Bu tarih, DF-A'nın başlangıç noktası olacak. Raporla.

======================================================================
GÖREV 2 — DF-A: NOTER DEVRİ PENCERESİNDE, KAPSAMA TESTİNDEN GEÇEN SÜTUNLAR
======================================================================
Kural (dikkatle uygula):
- DF-A'nın tarih aralığı: [noter devrinin başlangıç ayı] → bugün.
- Bu pencerede HER SÜTUN için "kapsama testi" uygula: sütunun kendi
  başlangıç tarihi, noter devrinin başlangıç tarihinden EŞİT VEYA DAHA
  ERKEN mi?
  - EVET ise: sütun DF-A'ya ALINIR. İçinde ara sıra düşen tekil boşluklar
    (ör. BETAM'ın 2 ay atlaması, ODMD'nin bir ayda kırılım vermemesi gibi)
    OLABİLİR, bu sorun değil — bu görevde DOLDURULMAYACAK ama sütun
    dışlanmayacak, kaydı tutulacak (sonraki bir görevde doldurulacak).
  - HAYIR ise (sütun, noter devrinden DAHA GEÇ başlıyorsa — ör. proxy
    fiyat/BETAM 2024-01'den başlıyor, noter devri 2015'ten başlıyorsa):
    sütun DF-A'ya HİÇ ALINMAZ (proxy fiyat, proxy_dom_gun,
    proxy_satis_orani_pct, ENAG sütunları ve bunlardan türeyen TÜM
    sütunlar muhtemelen bu kategoriye girecek — ama VARSAYMA, her sütunun
    gerçek başlangıç tarihini TEK TEK kontrol ederek karar ver).
- Hedef etiket sütunları (proxy_yon_nominal, proxy_yon_reel vb.) proxy
  fiyata bağımlı olduğundan muhtemelen kapsama testini geçemeyecek —
  bunlar hakkında Görev 4'te ayrıca karar var (aşağıya bak).

======================================================================
GÖREV 3 — DF-B: DAHA KAPSAMLI SÜTUN, DAHA DAR TARİH (2024-01 → BUGÜN)
======================================================================
- DF-B'nin tarih aralığı: 2024-01 → bugün (BETAM'ın gerçek başlangıcı).
- Bu pencerede TÜM sütunlar (proxy fiyat, ENAG dahil — DF-A'da dışarıda
  kalanlar da dahil olmak üzere HERKES) dahil edilir; kapsama testi
  burada UYGULANMAZ, çünkü amaç zaten "daha az geçmiş ama daha zengin
  içerik" tanımı.
- Bu pencerede de tekil/ara boşluklar (ÖTV olayı gibi yapısal olarak
  seyrek dolu sütunlar, ODMD'nin tek bir ay kırılım vermemesi gibi)
  olabilir — bunlar da bu görevde DOLDURULMAYACAK, kaydı tutulacak.

======================================================================
GÖREV 4 — HEDEF ETİKET SÜTUNLARI İÇİN ÖZEL KARAR
======================================================================
Hedef etiket sütunları (proxy_yon_nominal, proxy_yon_reel, proxy_yon_tercile
ve ilgili aylık değişim sütunları) proxy fiyata bağımlı olduğu için DF-A'nın
kapsama testini muhtemelen geçemeyecek. Bunları DF-A'dan TAMAMEN ÇIKARMA —
onun yerine ayrıca raporla: "DF-A'da hedef etiket sütunları YOK çünkü proxy
fiyat DF-A'nın kapsama testini geçemedi." Bu, proje sahibinin bilmesi
gereken önemli bir sonuç (DF-A üzerinde hedef=fiyat yönü ile çalışılamaz,
yalnızca DF-B ile çalışılabilir; DF-A muhtemelen noter-devri-hedefli
deneyler için kullanılacak).

======================================================================
GÖREV 5 — RAPORLAMA
======================================================================
Her iki DataFrame için ayrı ayrı:
- Boyut (satır × sütun), tarih aralığı.
- DF-A: kapsama testini GEÇEN sütunların tam listesi + GEÇEMEYEN
  sütunların tam listesi (neden geçemediği — hangi tarihten başladığı).
- İçindeki kalan tekil/ara boşlukların dökümü (hangi sütun, hangi ay(lar),
  kaç tane) — bu, "doldurma" görevinin girdisi olacak, şimdi sadece
  belgele.
- Veri sözlüğünü yeniden oluştur: data/processed/dataframes/
  veri_sozlugu_df_a_df_b_v2.md

======================================================================
YAPMA
======================================================================
- Herhangi bir boşluğu doldurma/enterpolasyon (bu ayrı, sonraki bir görev).
- Omurga tabloyu (veri_2015_bugun_etiketli.csv) değiştirme.
- Kapsama testi sonucunu tahmin etme — her sütunun gerçek başlangıç
  tarihini veriden oku, varsayma.
- Model/hedef değiştirme.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_dataframe_v2.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN (markdown kod bloğu) olarak göster.

Başlıklar: (1) Ne yapıldı — eski dosyaların silindiği teyit edilsin.
(2) Noter devri başlangıç tarihi (Görev 1). (3) DF-A: boyut, kapsama
testini geçen/geçemeyen sütunlar (iki ayrı liste), içindeki kalan
boşluklar. (4) DF-B: boyut, tüm sütunlar, içindeki kalan boşluklar.
(5) Hedef etiket sütunlarının durumu (Görev 4). (6) Karşılaşılan sorunlar.
(7) Veri örneği (her iki DataFrame'den ilk/son birkaç satır).
(8) Açık sorular / PM onayı gerekenler.
