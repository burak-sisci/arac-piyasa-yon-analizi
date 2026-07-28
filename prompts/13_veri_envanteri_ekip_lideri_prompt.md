ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Görev: ekip liderine sunulacak bir VERİ ENVANTERİ hazırlamak.
Bu bir analiz veya karar görevi DEĞİLDİR — sadece mevcut durumu doğru,
eksiksiz ve anlaşılır biçimde ÖZETLEMEK.

BAĞLAYICI İLKELER:
- Yeni veri çekme, model kurma, hedef değiştirme YOK — sadece MEVCUT
  dosyaları oku ve özetle.
- Uydurma yok: bir sütun/kaynak için istatistik hesaplayamıyorsan
  "hesaplanamadı" yaz, tahmin etme.
- data/processed/analiz/piyasa_aktivite_endeksi.csv dosyasını BU ENVANTERE
  DAHİL ETME — proje sahibi o veri setini ayrıca ele alacak.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/13_veri_envanteri_ekip_lideri_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — TARANACAK DOSYALAR
======================================================================
- data/processed/genisletme/veri_2018_bugun_etiketli.csv (ANA/omurga tablo)
- data/processed/analiz/tufe_enag_karsilastirma.csv (ENAG kontrol serisi —
  henüz ana tabloya eklenmemiş, AYRI bir başlık altında işaretle)
- Varsa data/processed/ altında bu ikisinin dışında kalan başka işlenmiş
  veri dosyası varsa onu da bul ve ekle.
- piyasa_aktivite_endeksi.csv HARİÇ TUT (yukarıda belirtildi).

======================================================================
GÖREV 2 — FORMAT (ÖNEMLİ, DİKKATLE UYGULA)
======================================================================
Her VERİ SETİ/KAYNAK bir BAŞLIK olacak (örn. "## Döviz Kuru (USD/TRY)",
"## TÜFE", "## ENAG E-TÜFE Kontrol Serisi", "## Taşıt Kredisi ve Politika
Faizi", "## ODMD Sıfır Araç Satışları", "## OSD Üretim", "## Noter Devir
Adedi", "## Tüketici Güven Endeksi", "## Alım Gücü Proxy'si", "## ÖTV
Olayları", "## Proxy Fiyat ve Hedef Etiketler", "## Erişim Endeksi" vb. —
veri setindeki gerçek gruplamaya göre).

Her başlığın ALTINDA, o kaynağın sütunları birer MADDE (liste öğesi) olarak
yazılacak. HER MADDENİN ALTINDA (kısaltılmadan, eksiksiz) şunlar bulunacak:
- Sütun adı (teknik adı, örn. usdtry_aysonu)
- Ne ölçtüğü (1-2 cümlelik açık anlaşılır açıklama)
- Kaynak kurum/site (TCMB EVDS, TÜİK, BETAM, ENAG, ODMD, OSD vb.)
- Tarih aralığı (ilk dolu tarih – son dolu tarih)
- Gözlem sayısı, dolu/boş sayısı, doluluk yüzdesi
- Temel istatistik: sayısal sütunlarsa ortalama/min/max/std sapma;
  kategorik/metin sütunlarsa benzersiz değerler ve frekansları
- Veri türü: GERÇEK ölçüm mü, yoksa TÜRETME/İNTERPOLASYON mu (önceki
  doluluk raporlarından — 05 numaralı analiz — bu bilgiyi devral, güncelle)

Hiçbir madde bu alt-bilgilerden eksik bırakılmasın; ekip lideri teknik
olmayabilir, o yüzden açıklamalar sade ama TAM olsun.

======================================================================
GÖREV 3 — DÖKÜMAN YAPISI (tam sıra)
======================================================================
1. KISA GİRİŞ (2-3 cümle): kaç veri seti, kaç sütun, genel tarih aralığı,
   genel veri kalitesi durumu.
2. Kaynak bazlı başlıklar (Görev 2'deki format) — sırasıyla tüm veri
   setleri.
3. GENEL ÖZET TABLOSU: kaynak | sütun sayısı | tarih aralığı | ortalama
   doluluk % | gerçek mi türetme mi.
4. BİLİNEN SINIRLAMALAR (madde madde): örn. "BETAM 2 ay rapor atlamış",
   "ENAG resmi sitesi erişilemiyor, C-seviyesi kaynaklarla doğrulanmış" vb.

======================================================================
GÖREV 4 — ÇIKTI VE KAYDETME (ÖNEMLİ)
======================================================================
- Dosyayı .md formatında oluştur: docs/veri_envanteri_ekip_lideri.md
- Bu dosyayı REPOYA COMMIT'LE (bu bir rapor/dokümantasyon dosyasıdır, veri
  dosyası değildir — .gitignore'daki veri-hariç-tutma kuralına takılmaz,
  normal şekilde commit edilir).
- AYRICA oturumda tamamını KOPYALANABİLİR DÜZ METİN (markdown kod bloğu)
  olarak göster — proje sahibi ekip liderine iletmeden önce gözden
  geçirecek.

YAPMA:
- Yeni veri toplama veya analiz önerisi sunma (bu envanter, analiz değil).
- Hedef veya model hakkında yorum/karar yazma.
- Sütun sayısını veya doluluk oranını tahminle geçiştirme — gerçekten
  dosyayı oku ve hesapla.
- piyasa_aktivite_endeksi.csv dosyasına dokunma veya bahsetme.

BİTİRİNCE: Kısa bir not düş — kaç veri seti, kaç sütun toplam, en zayıf/en
güçlü (en yüksek doluluk) kaynak hangisi, dosyanın repoya commit edildiğini
teyit et.
