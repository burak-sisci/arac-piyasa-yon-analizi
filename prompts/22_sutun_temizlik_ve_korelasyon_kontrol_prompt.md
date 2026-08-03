ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. 21 numaralı görevde kurulan DF-A ve DF-B üzerinde üç ayrı iş
yapacaksın: (1) belirli sütunları sil, (2) bir metin hatasını düzelt ve
dört proxy sütunu için rapor hazırla, (3) tüm veri setini korelasyon
analizine uygunluk açısından tara.

BAĞLAYICI İLKELER:
- Bu bir analiz/karar görevi değildir — silme ve raporlama işidir. Hedef/
  model değiştirme yok.
- Silme işlemleri HER İKİ DataFrame'de de (DF-A ve DF-B, hangisinde
  mevcutsa) uygulanacak.
- Silmeden önce her iki DataFrame'in bir yedeğini al (data/processed/
  dataframes/yedek/ altına, tarih damgalı) — geri dönüş güvenliği için.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/22_sutun_temizlik_ve_korelasyon_kontrol_prompt.md
olarak kaydet.

======================================================================
GÖREV 1 — SÜTUN SİLME (her iki DataFrame'de, mevcut olan sütunlarda)
======================================================================
Aşağıdaki sütunları DF-A ve DF-B'den sil (hangisinde varsa):
- otv_aciklama
- proxy_yayim_ayi
- proxy_kaynak
- proxy_fiyat_arabamcom_referans_tl
- proxy_yon_nominal
- proxy_yon_reel
- proxy_yon_tercile
- kullanilan_esik_k
- enag_tufe_fark_yillik
- enag_kaynak_seviyesi
- enag_kaynak_url

Her sütun için: hangi DataFrame'de(lerde) bulunduğunu ve silindiğini
raporla. Bir sütun hiçbir DataFrame'de yoksa "bulunamadı, atlandı" yaz.

======================================================================
GÖREV 2 — METİN HATASI DÜZELTMESİ
======================================================================
proxy_kaynak sütunu Görev 1'de SİLİNDİ — ANCAK bu düzeltmeyi proxy_kaynak
silinmeden ÖNCE, ya da proxy_kaynak'ın türediği/ilişkili olduğu başka bir
sütunda ("eksik" string değeri geçen tüm sütunları tara) uygula: "eksik"
metin değerini gerçek boş (NaN/None) değere çevir. Bunu yaparken TÜM
DataFrame'lerde "eksik" string'i geçen HER sütunu kontrol et (sadece
proxy_kaynak ile sınırlı olmayabilir), bul ve düzelt. Kaç hücrede bu
düzeltme yapıldığını raporla.

======================================================================
GÖREV 3 — DÖRT PROXY SÜTUNU İÇİN RAPOR (karar değil, sadece rapor)
======================================================================
Şu dört sütun için ayrı ayrı, DETAYLI bir rapor hazırla — amaç, proje
sahibinin bu rapora bakarak boşlukları NASIL dolduracağına kendisinin
karar vermesi. Sen doldurma YAPMA, sadece bilgi ver:

1. proxy_dom_gun
2. proxy_satis_orani_pct
3. proxy_fiyat_cari_tl
4. (proxy_kaynak zaten silindi — bu sütun için rapor gerekmez, Görev 1/2
   yeterli)

Her sütun için:
- Toplam gözlem sayısı, dolu/boş sayısı, doluluk %.
- Boş olan AYLARIN tam listesi (hangi YYYY-MM'ler).
- Bu boşlukların NEDENİ (BETAM'ın rapor yayımlamadığı aylar mı, başka bir
  sebep mi — mevcut bilgiden çıkar, gerekirse ham veriye geri dön).
- Serinin GENEL KARAKTERİ: ortalama, min, max, standart sapma, aydan aya
  ne kadar değiştiği (volatilite hissi vermek için).
- Boşluğun ÖNCESİ VE SONRASI değerler (her boş ay için, komşu dolu
  aylardaki değerler) — proje sahibi enterpolasyon yapılabilir mi
  değerlendirebilsin diye.
- Bu sütunun BAŞKA hangi sütunlarla (özellikle diğer 3 proxy sütunuyla)
  ilişkili/türetilmiş olduğu (ör. proxy_fiyat_cari_tl boşsa ondan türeyen
  değişim sütunları da otomatik boş kalıyor mu).

======================================================================
GÖREV 4 — KORELASYON ANALİZİNE UYGUNLUK TARAMASI (TÜM sütunlar)
======================================================================
Her iki DataFrame'deki TÜM sütunları tara ve korelasyon analizi için
SORUNLU olabilecekleri işaretle. Şu kategorileri kontrol et:
a. SABİT/DEĞİŞMEYEN sütunlar (tüm değerler aynı veya neredeyse aynı —
   varyans ~0, korelasyon hesaplanamaz veya anlamsız çıkar).
b. METİN/KATEGORİK sütunlar (sayısal olmayan, doğrudan korelasyona
   sokulamaz — kaç tane var, hangileri).
c. TARİH/ZAMAN damgası sütunları (referans_ayi gibi — korelasyona
   doğrudan sokulmamalı, ama zaman-serisi indeksleme için gerekli,
   "hariç tut ama silme" olarak işaretle).
d. AŞIRI YÜKSEK ORANDA BOŞ sütunlar (örn. %70+ boş — korelasyon
   hesaplanacak gözlem sayısı çok azalır, güvenilirliği düşük olur).
e. BAŞKA BİR SÜTUNUN BİREBİR KOPYASI veya DOĞRUSAL TÜREVİ olan sütunlar
   (örn. bir sütun diğerinin sabit katsayıyla çarpımıysa, korelasyon
   analizinde gereksiz tekrar/çoklu-doğrusallık riski yaratır) — varsa
   çiftleri listele.
f. AŞIRI DEĞER (outlier) şüphesi taşıyan sütunlar — bir-iki gözlemin
   diğerlerinden çok uzak olduğu, korelasyonu tek bir noktanın domine
   edebileceği durumlar.

Her bulgu için: sütun adı, hangi DataFrame'de, kategori (a-f), kısa
gerekçe, ÖNERİ DEĞİL sadece bulgu (karar proje sahibine kalacak).

======================================================================
YAPMA
======================================================================
- Boşluk doldurma/enterpolasyon (Görev 3 sadece rapor, doldurma değil).
- Korelasyon analizinin kendisini çalıştırma (Görev 4 sadece uygunluk
  taraması, analiz değil).
- Sorunlu bulunan sütunları otomatik silme veya düzeltme (Görev 4 sadece
  rapor).
- Silme dışında herhangi bir sütun/veri değişikliği.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_sutun_temizlik_korelasyon.md üret VE
oturumda KOPYALANABİLİR DÜZ METİN (markdown kod bloğu) olarak göster.

Başlıklar: (1) Ne yapıldı — silinen sütunlar listesi + hangi DataFrame'de.
(2) "Eksik" metin düzeltmesi — kaç hücre, hangi sütun(lar). (3) Dört proxy
sütunu raporu (Görev 3, detaylı). (4) Korelasyon uygunluk taraması sonucu
(Görev 4, kategori bazlı liste). (5) Karşılaşılan sorunlar. (6) Yedek
dosyaların konumu. (7) Açık sorular / PM onayı gerekenler.
