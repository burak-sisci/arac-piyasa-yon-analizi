ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Görev: df_gunluk_forward_fill_2015_bugun.csv (ay-hizalı
doldurulmuş, 28 numaralı görevde doğrulanmış) kaynağından İKİ YENİ
DataFrame kurmak. Bu, 21 numaralı görevdeki DF-A/DF-B mantığının
GÜNCELLENMİŞ halidir — aynı "kapsama testi" ilkesi geçerli, ama artık
ay-hizalı doldurulmuş veri kullanılıyor VE ÖTV olay sütunları hiç dahil
edilmiyor.

BAĞLAYICI İLKELER:
- Bu bir analiz/karar görevi değildir — DataFrame kurma ve belgeleme
  işidir. Korelasyon analizi bu görevde YAPILMAZ (proje sahibinin ayrı
  onayı bekleniyor).
- Veri Git-dışı, kod+rapor commit'lenir.
- Şüpheli/beklenmedik bulguları proaktif bildir.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/29_df_a_df_b_v3_ay_hizali_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — ÖTV SÜTUNLARINI BAŞTAN DIŞLA
======================================================================
Kaynak tablodaki (df_gunluk_forward_fill_2015_bugun.csv) TÜM "otv" geçen
sütunları (otv_referans_ay, otv_aciklama, otv_event_gunu_mu veya benzeri
gerçek adları koddan oku) bul. Bu sütunlar HİÇBİR ŞEKİLDE ne DF-A'ya ne
DF-B'ye dahil edilmeyecek — kapsama testinden bile geçirilmeyecek,
baştan eleniyor. Gerekçe: bu sütunlar hâlâ yalnızca olayın gerçekleştiği
tek günde 1, diğer tüm günlerde 0 döndürüyor; aşırı seyrek/dengesiz
oldukları için bu iki DataFrame'e katkısı yok.

Hangi sütunların dışlandığını tam liste olarak raporla.

======================================================================
GÖREV 2 — DF-A: NOTER DEVRİ PENCERESİ, ENAG/BETAM HARİÇ, 2015'E KADAR
======================================================================
- Noter devri serisinin (noter_devir_toplam_adet veya
  noter_devir_otomobil_adet — hangisi daha erken başlıyorsa) İLK DOLU
  olduğu tarihi tespit et (muhtemelen 2015-01 civarı, kodla doğrula).
- DF-A'nın tarih aralığı: [noter devrinin başlangıcı] → bugün.
- KAPSAMA TESTİ (21 numaralı görevdeki AYNI mantık): bu pencerede her
  sütun için, sütunun kendi başlangıç tarihi noter devrinin başlangıç
  tarihinden EŞİT VEYA DAHA ERKEN mi?
  - EVET → DF-A'ya alınır (içindeki ay-hizalı doldurma zaten mevcut,
    tekil/yapısal boşluklar olabilir, sorun değil).
  - HAYIR (ör. ENAG, proxy fiyat/BETAM kaynaklı TÜM sütunlar — bunlar
    2024-01'den başladığından muhtemelen bu testi GEÇEMEYECEK) → DF-A'ya
    ALINMAZ.
- ÖTV sütunları zaten Görev 1'de tamamen dışlandı, kapsama testine bile
  girmez.
- Her sütun için gerçek başlangıç tarihini KODLA DOĞRULA, varsayma.

======================================================================
GÖREV 3 — DF-B: ENAG + BETAM DAHİL, 2024-01'DEN BUGÜNE
======================================================================
- DF-B'nin tarih aralığı: 2024-01-01 → bugün (BETAM'ın gerçek başlangıcı).
- Bu pencerede TÜM sütunlar dahil edilir (ENAG, BETAM/proxy fiyat, ve
  DF-A'da bulunan her şey) — kapsama testi UYGULANMAZ.
- ÖTV sütunları burada da DAHİL EDİLMEZ (Görev 1'de zaten dışlanmıştı).

======================================================================
GÖREV 4 — GÜNLÜK Mİ KALSIN, AYA MI İNDİRİLSİN? (netleştir, sorma, işaretle)
======================================================================
Kaynak tablo GÜNLÜK satır yapısında (4234 satır, 2015-2026). Bu iki yeni
DataFrame'i de AYNI GÜNLÜK YAPIDA kur (satır bazında indirgeme/aya
toplama YAPMA) — proje sahibi korelasyon analizini ayrı bir adımda,
kendi belirleyeceği yöntemle (günlük veya aya-indirgenmiş) yapacak. Bu
görevin işi yalnızca DOĞRU SÜTUN SETİNİ ayırmak, satır granülerliğini
DEĞİŞTİRMEMEK.

======================================================================
GÖREV 5 — ÇIKTI VE VERİ SÖZLÜĞÜ (21 numaralı görevdeki FORMATLA AYNI)
======================================================================
- data/processed/dataframes/df_a_v3_noter_penceresi_2015_bugun.csv
- data/processed/dataframes/df_b_v3_enag_betam_2024_bugun.csv
- VERİ SÖZLÜĞÜ (data/processed/dataframes/veri_sozlugu_df_a_df_b_v3.md):
  HER SÜTUN için:
  1. Sütun adı
  2. Kısa açıklama (1-2 cümle, ne ölçtüğü)
  3. Doluluk oranı (dolu satır / toplam satır, yüzde)
  4. Veri tipi (sayısal/tarih/kategorik/bayrak) + 2-3 ÖRNEK DEĞER (gerçek
     tablodan alınmış, uydurma değil)
  Bu, DF-A ve DF-B için AYRI AYRI iki bölüm halinde (veya tek dosyada iki
  başlık altında) sunulacak.

======================================================================
GÖREV 6 — DOĞRULAMA
======================================================================
- DF-A: kapsama testini GEÇEN ve GEÇEMEYEN sütunların tam listesi
  (geçemeyenler için "hangi tarihten başladığı" gerekçesiyle).
- DF-B: toplam sütun sayısı, hangi grupların (ENAG, BETAM) dahil olduğu
  teyit.
- Her iki DataFrame'in de satır sayısının kaynak tabloyla (kendi tarih
  aralıklarına göre) tutarlı olduğunu doğrula.
- ÖTV sütunlarının HİÇBİRİNİN iki DataFrame'de de yer almadığını teyit et.

======================================================================
YAPMA
======================================================================
- Korelasyon analizi çalıştırma (proje sahibinin ayrı onayı bekleniyor).
- Günlük satırları aya indirgeme/toplama.
- Herhangi bir sütunu doldurma/enterpolasyon (kaynak tablo zaten
  ay-hizalı doldurulmuş durumda, ek işlem gerekmiyor).
- Hedef/model değiştirme.
- Kaynak tabloyu (df_gunluk_forward_fill_2015_bugun.csv) değiştirme.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_df_a_df_b_v3.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN olarak göster.

Başlıklar: (1) Ne yapıldı. (2) ÖTV dışlama listesi (Görev 1). (3) DF-A:
boyut, kapsama testini geçen/geçemeyen sütunlar (iki liste), tarih
aralığı. (4) DF-B: boyut, sütun listesi, tarih aralığı. (5) Veri sözlüğü
özeti (kaç sütun, örnek bir-iki giriş). (6) Karşılaşılan sorunlar.
(7) Veri örneği (her iki DataFrame'den ilk/son birkaç satır).
(8) Açık sorular / PM onayı gerekenler.

BİTİRİNCE: Kısa not — iki DataFrame hazır olduğunda proje sahibinin
onayıyla korelasyon aşamasına geçileceğini hatırlat, bu görevde
KORELASYON ÇALIŞTIRILMADI.
