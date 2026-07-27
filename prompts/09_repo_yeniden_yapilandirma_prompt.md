ROL VE BAĞLAM

Bu repo başlangıçta yalnızca literatür tarama projesi olarak kurulmuştu
(README, klasör yapısı buna göreydi). Proje o zamandan beri veri mühendisliği
aşamasına geçti: MVP veri seti, 2024-2026 genişletmesi, 2018'e geriye
genişletme, korelasyon analizi ve hedef keşfi tamamlandı/sürüyor. Repo
YAPISI ve README bu gerçek durumu yansıtmıyor — güncellenmesi gerekiyor.

BU BİR İÇERİK SİLME GÖREVİ DEĞİLDİR. Hiçbir mevcut dosya (docs/ altındaki
8 faz + sentez + karar kaydı, data/ altındaki veri çalışması, prompts/
altındaki arşiv) SİLİNMEYECEK veya taşınmayacak — yalnızca ÜST DÜZEY
NAVİGASYON (README, klasör açıklamaları) güncellenecek ki repo'ya yeni
bakan biri (veya gelecekteki proje sahibi/mentor) mevcut durumu doğru
okuyabilsin.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/09_repo_yeniden_yapilandirma_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — MEVCUT DURUMU ENVANTERLE
======================================================================
Değişiklik yapmadan önce, repo'nun şu anki gerçek içeriğini çıkar:
- docs/ altında kaç faz dosyası, sentez, karar kaydı (hangi versiyon) var.
- prompts/ altında kaç alt-klasör ve toplam kaç prompt arşivlenmiş
  (veri/ alt klasörü dahil).
- data/ altındaki yapı (raw/processed alt klasörleri, hangi kaynaklar).
- data/processed/analiz/ ve data/processed/raporlar/ içeriği (kaç analiz,
  kaç PM raporu üretilmiş).
Bu envanteri README güncellemesinde KULLAN, tahmin etme.

======================================================================
GÖREV 2 — README.md GÜNCELLEMESİ
======================================================================
Kök README.md'yi yeniden yaz (mevcut "Durum" bölümünü tamamen değiştir,
diğer bölümleri gerekirse güncelle). Yeni yapı:

1. Proje tanımı (1 paragraf, güncellenmiş): artık yalnızca "literatür tarama"
   değil, "literatür temelli, veri odaklı bir piyasa yönü tahmin projesi"
   olarak tanımla.
2. İKİ AŞAMALI YOL HARİTASI görünür olsun:
   - Aşama A (TAMAMLANDI): Literatür tarama ve sentez — 8 faz + karar kaydı
     + sentez dökümanı. docs/ klasörüne link.
   - Aşama B (AKTİF): Veri mühendisliği ve keşif — MVP → genişletme → 2018
     genişletmesi → korelasyon/hedef keşfi. data/ klasörüne link. Şu anki alt
     durumu (hangi adımda olunduğu, hedef tanımının hâlâ açık olduğu) net yaz.
3. Klasör yapısı tablosunu güncelle (docs/, prompts/ [alt klasörleri dahil],
   data/ [alt klasörleri dahil], exports/).
4. "Nasıl çalışır" bölümüne veri mühendisliği döngüsünü ekle: Claude Code
   ile prompt bazlı çalışma, PM raporu standardı, öz-arşivleme kuralı,
   otonomi sınırı (CLAUDE.md'ye link).
5. Güncel "Durum" listesi (checkbox), gerçek envanterden (Görev 1) üretilsin,
   uydurma olmasın.

======================================================================
GÖREV 3 — CLAUDE.md GÖZDEN GEÇİRME
======================================================================
CLAUDE.md'nin proje tanımı kısmı hâlâ "yalnızca literatür tarama" gibi
okunuyorsa güncelle (Otonomi Sınırı bölümüne DOKUNMA, o zaten güncel).
Proje artık iki aşamalı: tarama (tamamlandı, referans olarak kalıcı) +
veri mühendisliği (aktif). Bunu üstte net belirt.

======================================================================
GÖREV 4 — KLASÖR AÇIKLAMALARI (gerekirse yeni README'ler)
======================================================================
- data/README.md zaten varsa güncel mi kontrol et (K5 uyarısı, raw/processed
  ayrımı hâlâ doğru mu).
- prompts/ altına kısa bir README ekle (yoksa): hangi alt klasörün ne işe
  yaradığını listele (kök = tarama fazları, veri/ = veri mühendisliği).
- docs/ altına dokunma — zaten kendi içinde tutarlı.

======================================================================
YAPMA
======================================================================
- Hiçbir mevcut dosyayı silme, taşıma veya yeniden adlandırma.
- docs/ içindeki faz dökümanlarını veya karar kaydını değiştirme.
- data/ içindeki veri dosyalarını (zaten Git-dışı) etkileme.
- Yeni bir aşama/analiz başlatma — bu yalnızca navigasyon/dokümantasyon
  güncellemesi.

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_repo_yeniden_yapilandirma.md üret VE
oturumda KOPYALANABİLİR DÜZ METİN olarak göster. Başlıklar: (1) Envanter
özeti (Görev 1 sonucu). (2) Değiştirilen dosyalar. (3) Yeni README/CLAUDE.md
içeriğinin özeti. (4) Açık sorular/PM onayı gerekenler (varsa).
