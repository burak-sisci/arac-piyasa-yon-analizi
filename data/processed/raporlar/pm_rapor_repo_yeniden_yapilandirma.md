---
başlık: PM Raporu — Repo Yeniden Yapılandırma (Navigasyon/Dokümantasyon)
tarih: 2026-07-27
kapsam: Yalnızca üst düzey navigasyon (README.md, CLAUDE.md, prompts/README.md,
  data/README.md kontrolü). Hiçbir içerik dosyası silinmedi/taşınmadı/yeniden
  adlandırılmadı, yeni analiz başlatılmadı.
prompt_arşivi: prompts/09_repo_yeniden_yapilandirma_prompt.md
durum: tamamlandı
---

## 1) Envanter özeti (Görev 1 sonucu)

**docs/:** 11 dosya + 1 alt klasör.
- `00_master_plan_literatur_taramasi.md` (durum: tamamlandi)
- `00_karar_kaydi.md` (revizyon v8 — FİNAL, durum: onaylandi)
- `01`…`07` faz dosyaları — **hepsi durum: tamamlandi** (7 dosya)
- `08_basarisizlik_modlari_tuzaklar.md` — **durum: taslak**
- `09_sentez_ve_karar_dokumani.md` — **durum: taslak**
- `standards.md`
- `docs/sentez/` — **boş** (sentez dökümanı fiilen `docs/09_*.md`'de duruyor;
  klasör kullanılmıyor)

**prompts/ (kök):** 14 dosya — Faz 0-8 promptları (00, 01-04, 04a, 04b, 05-08),
sentez talimatı, pdf dönüştürme talimatı, + bu görevin promptu (09).

**prompts/veri/:** 10 dosya — MVP, temizleme/etiket, geniş veri çekme, veri
tanıma doluluk, 2018 genişletme+korelasyon, 3 fizibilite promptu (07a-c),
hedef keşfi (08), + eski `mvp_veri_seti_promptu.md`.

**data/raw/:** 10 kaynak alt klasörü (usdtry, tüfe, proxy_fiyat, faiz, odmd,
otv, osd, tüketici_güveni, noter_devir, alım_gücü).

**data/processed/:** 4 alt klasör.
- `mvp/`: 4 dosya (birleşik+etiketli, csv+xlsx)
- `genisletme/`: 8 dosya (2018 ve 2024 versiyonları, birleşik+etiketli, csv+xlsx)
- `analiz/`: 6 CSV (hedef-aday karşılaştırma, korelasyon matrisi, zaman
  serileri, piyasa aktivite endeksi, hedef-keşif tekli-seri istatistik, ccf)
  + `hedef_kesif_gorseller/` alt klasörü (11 PNG, Git-dışı)
- `raporlar/`: **11 .md dosyası** — `veri_sozlugu.md`, `temizleme_raporu.md`
  + 9 `pm_rapor_*.md` (asama5, genisletme_asama1, genisletme_asama2_5,
  genisletme_hata_listesi_cozumleri, genisletme_hedef_etiket,
  genisletme_noter_devir_alim_gucu, kosullu_genisletme,
  genisletme2018_korelasyon, hedef_kesif)

**exports/:** 9 PDF (Faz 1-8 + sentez) + 2 pptx.

**scripts/veri/:** 19 Python dosyası.

**Kritik bulgu (bu envanterde ortaya çıktı, ayrıca bkz. Bölüm 4):** README.md
daha önce Faz 8 ve Sentez'i `[x]` (tamamlandı) işaretliyordu, ama her iki
dökümanın kendi metadata'sı `durum: taslak`. CLAUDE.md kural 7 gereği
("dökümanın durum alanı taslak'a dönerse README'deki işaret de geri alınır")
bu, README'de düzeltildi (`[ ]`'e çevrildi).

## 2) Değiştirilen dosyalar

| Dosya | Değişiklik |
|---|---|
| `README.md` | Tamamen yeniden yazıldı: iki aşamalı (A/tarama, B/veri mühendisliği) yapı, güncel klasör tablosu, gerçek envanterden üretilmiş Durum listesi (Faz 8 + Sentez artık `[ ]`) |
| `CLAUDE.md` | "Proje Kimliği" bölümü iki aşamalı hale getirildi ("bu repo yazılım projesi değildir" ifadesi kaldırıldı — Aşama B için artık doğru değil); "Depo Yapısı" ağacı güncellendi (prompts/veri, scripts/veri, data/, karar_kaydi eklendi; yanlış `00_master_plan.md` dosya adı düzeltildi); "Çalışma Modeli"ne Aşama B döngüsüne tek satır referans eklendi. **Otonomi Sınırı bölümüne dokunulmadı** (talimat gereği). |
| `prompts/README.md` | **Yeni dosya** — kök vs `veri/` alt klasör ayrımını açıklıyor |
| `data/README.md` | Kontrol edildi, güncel bulundu (bir önceki görevde zaten güncellenmişti — K5 uyarısı ve raw/processed ayrımı doğru) |
| `docs/` | **Dokunulmadı** (talimat gereği) |

Hiçbir dosya silinmedi, taşınmadı veya yeniden adlandırılmadı.

## 3) Yeni README/CLAUDE.md içeriğinin özeti

**README.md:** Proje artık "literatür temelli, veri odaklı piyasa yönü tahmin
projesi" olarak tanımlanıyor. İki bölüm: Aşama A (tarama, Faz 0-7 tamamlandı,
Faz 8 + sentez taslak) ve Aşama B (veri mühendisliği, aktif — MVP → genişletme
→ 2018 genişletmesi → korelasyon → hedef keşfi tamamlandı, K1 hedef tanımı
hâlâ açık). Klasör tablosu artık `prompts/veri/`, `scripts/veri/`,
`data/raw|processed/{mvp,genisletme,analiz,raporlar}` içeriyor. "Nasıl çalışır"
bölümüne veri mühendisliği döngüsü (prompt → öz-arşiv → çalışma → PM raporu)
eklendi.

**CLAUDE.md:** Proje Kimliği artık açıkça iki aşamalı: Aşama A "yazılım
projesi değildir" (eskisi gibi), Aşama B "artık bir yazılım projesidir" diye
açıkça belirtiliyor — bu, önceki metnin "Bu repo bir yazılım projesi
DEĞİLDİR" cümlesiyle doğrudan çelişiyordu, düzeltildi. Depo Yapısı ağacı
gerçek yapıyla eşleşiyor.

## 4) Açık sorular / PM onayı gerekenler

1. **Faz 8 ve Sentez raporu hâlâ taslak.** README bunu artık doğru
   yansıtıyor (`[ ]`), ama bu durum daha önce (yanlışlıkla) `[x]` işaretliydi
   — proje sahibinin bu iki dökümanın gerçekten tamamlanıp tamamlanmadığını
   teyit etmesi, ve tamamlandıysa ilgili dökümanların kendi `durum:` alanının
   da güncellenmesi gerekiyor (bu görev kapsamında **docs/ içeriğine
   dokunulmadı**, yalnızca README'deki yansıması düzeltildi).
2. **`docs/sentez/` klasörü boş.** README bunu artık açıkça belirtiyor
   ("şu an boş — sentez dökümanı docs/09'da duruyor"). Bu, klasörün hiç
   kullanılmadığı anlamına mı geliyor, yoksa gelecekte sentez kaynak
   dosyaları (ör. sunum taslakları) buraya mı taşınacak — bu bir tasarım
   sorusu, PM'e bırakılıyor.
3. **`prompts/veri/mvp_veri_seti_promptu.md`** ile `prompts/veri/
   01_mvp_cekirdek_veri_prompt.md` arasındaki ilişki incelenmedi (iki ayrı
   MVP promptu mu, biri diğerinin taslağı mı) — bu görev kapsamı dışında
   bırakıldı, içerik karşılaştırması yapılmadı.
