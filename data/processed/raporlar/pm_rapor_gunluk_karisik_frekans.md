# PM Raporu — Günlük/Karışık-Frekans Tablosu (Görev 25)

**Tarih:** 2026-08-04
**Prompt arşivi:** `prompts/veri/25_gunluk_eur_altin_karisik_frekans_prompt.md`
**Kaynak scriptler:** `scripts/veri/genisletme_25a_eurtry.py`,
`scripts/veri/genisletme_25b_altintry.py`,
`scripts/veri/genisletme_25c_karisik_frekans_birlestir.py`
**Çıktı:** `data/processed/dataframes/df_gunluk_karisik_frekans_2015_bugun.csv`
(git-dışı, yalnızca kod + bu rapor commit'lenir)

---

## 1. Ne Yapıldı

Ekip toplantısında alınan "zaman çözünürlüğünü aylıktan günlüğe çek"
kararı, talimatın kesin kuralına göre uygulandı: **forward-fill YOK**.
Üç script yazıldı:

1. **25a** — EUR/TRY günlük kurunu (alış/satış/ortalama), USD/TRY ile
   aynı EVDS chunking yöntemiyle 2015-01-01 → bugün çekti.
2. **25b** — Altın/TRY'yi çekmeye çalıştı; EVDS'te yalnızca AYLIK bir
   seri bulundu (bkz. Bölüm 2/6) — bu, kaynağın gerçek doğal frekansına
   göre AYLIK kovaya alındı.
3. **25c** — Tüm `data/raw/` kaynaklarını tek bir GÜNLÜK tarih ekseninde
   (2015-01-01 → bugün, her takvim günü bir satır) birleştirdi: günlük
   kaynaklar her güne gerçek değerle, aylık/çeyreklik/olay-bazlı
   kaynaklar SADECE kendi as-of gününde dolu, geri kalan günlerde NaN.
   Her aylık kaynak grubunun kendi `..._referans_ay` yardımcı sütunu var.
   Tarih sütunu gerçek datetime tipinde korundu; `yil, ay, gun, ceyrek,
   haftanin_gunu, yilin_gunu` takvim sütunları eklendi.

Üretim sırasında iki veri kalitesi sorunu tespit edilip düzeltildi
(bkz. Bölüm 6) — tablo şu an satır bazında tutarlı (4234 takvim günü =
4234 benzersiz `tarih`, tekrar yok).

---

## 2. API Anahtarı Durumu

**Net sonuç: HİÇBİR yeni API anahtarı/hesap kaydı gerekmedi.** Hem
EUR/TRY hem Altın/TRY, USD/TRY'yi çekmek için zaten kullanılan mevcut
`EVDS_API_KEY` ile başarıyla çekildi.

- **EUR/TRY:** `TP.DK.EUR.A` / `TP.DK.EUR.S` — USD/TRY'nin
  `TP.DK.USD.A/S` kodlarıyla birebir aynı desen. Sorunsuz çalıştı.
- **Altın/TRY:** `TP.MK.KUL.YTL` (Külçe Altın Satış Fiyatı, TL/Gr,
  Ankara Kuyumcular ve Saatçiler Odası kaynaklı) — mevcut anahtarla
  çalıştı, ANCAK bu seri **AYLIK** (bkz. Bölüm 6'daki proaktif bulgu).

**Proje sahibinin herhangi bir kayıt açmasına gerek YOK.** Görev 5
(manuel aşama) bu nedenle fiilen boş — açılacak bir hesap yok, yalnızca
aşağıdaki frekans kısıtı bilgi amaçlı bildiriliyor.

---

## 3. `data/raw/` Envanteri — Doğal Frekans ve Dahil Ediliş Yöntemi

| Kaynak | Doğal frekans | Günlük tabloya nasıl dahil edildi |
|---|---|---|
| USD/TRY | Günlük (hafta sonu/tatilde yok) | Gerçek günlük değer, her güne |
| EUR/TRY | Günlük (hafta sonu/tatilde yok) | Gerçek günlük değer, her güne |
| Altın/TRY (TP.MK.KUL.YTL) | **Aylık** (beklenenin aksine) | As-of: referans ayın bir sonraki ayının 1. günü, yalnızca o gün dolu |
| TÜFE | Aylık | As-of: kaynağın KENDİ `yayim_tarihi` sütunu (gerçek yayım günü) |
| ENAG | Aylık | As-of: sonraki ayın 1. günü (gerçek yayım tarihi kayıtlı değil) |
| Noter devri (toplam/otomobil) | Aylık | As-of: sonraki ayın 1. günü |
| ODMD (toplam/otomobil/HTA) | Aylık | As-of: sonraki ayın 1. günü |
| OSD (binek/kamyonet/toplam) | Aylık | As-of: sonraki ayın 1. günü |
| Tüketici güveni + otomobil satın alma ihtimali | Aylık | As-of: sonraki ayın 1. günü |
| Proxy fiyat (BETAM: fiyat, dom gün, satış oranı) | Aylık (düzensiz yayım aralıklı) | As-of: kaynağın KENDİ `yayim_ayi` sütununun 1. günü; aynı as-of güne düşen çakışmalar tekilleştirildi (bkz. Bölüm 6) |
| Alım gücü (brüt ücret/maaş endeksi) | Çeyreklik (aylığa kopyalanmış kaynak) | As-of: sonraki ayın 1. günü |
| Faiz (taşıt kredisi + politika faizi) | Proje tasarımı gereği aylık ortalama (kaynağı günlük/haftalık olsa da) | As-of: sonraki ayın 1. günü |
| ÖTV olayları | Olay-bazlı | Gerçek yürürlük tarihi biliniyor (11 olayın hepsi) — o güne işaretlendi, ay başına yaklaştırma YAPILMADI |

Forward-fill hiçbir aylık/çeyreklik/olay-bazlı kaynak için kullanılmadı.

---

## 4. Karışık-Frekans Tablosu — Boyut ve Kapsam

- **Boyut: 4234 satır × 48 sütun.**
- **Tarih aralığı:** 2015-01-01 → 2026-08-04 (bugün), her takvim günü
  bir satır (hafta sonu/tatil dahil).
- `tarih` sütunu gerçek `datetime64` tipinde (string/sayısal indekse
  ÇEVRİLMEDİ).
- Takvim sütunları: `yil, ay, gun, ceyrek, haftanin_gunu` (0=Pazartesi
  … 6=Pazar, `.dt.dayofweek`), `yilin_gunu`.
- Sütun başına doluluk (özet):

| Sütun grubu | Dolu satır / 4234 | Not |
|---|---|---|
| usdtry_* | 2910 | hafta sonu/tatil NaN — beklenen |
| eurtry_* | 2912 | hafta sonu/tatil NaN — beklenen |
| altin_* | 137 | 2026-06/07/08 henüz yayımlanmadı (yapısal gecikme) |
| tufe_* | 138 (endeks) / 137 (aylık değişim) / 126 (yıllık değişim) | ilk ayda önceki-ay/yıl karşılaştırması yok |
| enag_* | 65 (değişim) | `enag_endeks` sütunu KALDIRILDI (bkz. Bölüm 6) |
| noter_* | 138 | kaynakla birebir eşleşiyor |
| odmd_* | 138 (toplam) / 137 (otomobil/HTA) | |
| osd_* | 138 | |
| tuketici_* | 139 | |
| proxy_* | 26 | 30 ham satırdan 1'i yayımlanmamış ("tahmini"), 3 çakışma tekilleştirildi → 26 (bkz. Bölüm 6) |
| alim_gucu_* | 99 | çeyreklik kaynağın aylığa taşınmış hali |
| faiz_* | 139 | |
| otv_* | 11 (referans_ay/açıklama) / 4234 (event_gunu_mu, 0/1 bayrak) | |

---

## 5. Manuel Aşama Bildirimi

Yok — Bölüm 2'de belirtildiği gibi yeni anahtar/hesap gerekmedi, bu
görevde proje sahibinden bir kayıt işlemi beklenmiyor.

---

## 6. Karşılaşılan Sorunlar (saklanmadı)

1. **[PROAKTİF BULGU] Altın/TRY, TCMB EVDS'te GÜNLÜK değil, AYLIK.**
   Görev talimatı altını "doğası gereği günlük" varsayıyordu (döviz
   kurları gibi). Mevcut anahtarla erişilen TEK gram-altın/TL serisi
   (`TP.MK.KUL.YTL`) sitenin kendi arayüzünde "(Aylık)" etiketli ve
   dönen veri noktalarının `Tarih` alanı da bunu doğruluyor ("2015-1"
   formatı, gün bilgisi yok). EVDS'in "Diğer Kıymetli Madenler ve Emtia
   Piyasası" kategorisinde yalnızca Brent petrol var, başka bir altın
   serisi yok; kısa bir WebSearch taraması da (zaman-maliyeti
   gözetilerek sınırlı tutuldu) resmi/güvenilir, ücretsiz GÜNLÜK bir
   TL/gram altın kaynağı ortaya çıkarmadı. **Karar:** altın, kendi
   gerçek doğal frekansına (aylık) göre AYLIK kovaya alındı — bu,
   görevin kendi tasarım ilkesiyle (kaynağın doğal frekansına saygı,
   forward-fill yasağı) tutarlı, ama görevin başlangıç varsayımından
   bir SAPMA. Ekip lideriyle görüşülmeye değer: gerekirse ücretli bir
   üçüncü-taraf günlük altın API'si (bir sonraki adımda K5 kapsamında
   değerlendirilebilir) araştırılabilir.

2. **[BULUNDU VE DÜZELTİLDİ] BETAM proxy_fiyat kaynağında as-of gün
   çakışması, tüm tabloda satır çoğalmasına (fan-out) yol açıyordu.**
   İlk çalıştırmada tablo 4237 satır × 49 sütun çıktı (beklenen 4234
   yerine 3 fazla satır) ve `noter_referans_ay` gibi ilgisiz sütunlarda
   bile 138 yerine 141 dolu değer görüldü. Kök neden araştırıldı:
   `noter_devir_2015_bugun_aylik.csv` kaynağının kendisinde HİÇBİR
   yinelenen `referans_ayi` olmadığı doğrulandı (138 satır, 138
   benzersiz) — yani sorun noter kaynağında değildi. Sistematik tarama
   sonucu gerçek kaynak bulundu: `proxy_fiyat_2024_bugun_raw.csv`'de
   BETAM zaman zaman İKİ referans ayını AYNI `yayim_ayi`'nda birlikte
   yayımlıyor (örn. 2024-01 VE 2024-02, ikisi de `yayim_ayi=2024-03`'te
   çıkmış; 2024-03/2024-04 ikisi de 2024-05'te). Bu, aynı as-of güne iki
   farklı satırın düşmesine, dolayısıyla o güne merge edilen TÜM diğer
   sütunların da yinelenmesine neden oluyordu. **Düzeltme:** aynı as-of
   güne düşen çakışmalarda, gerçek verisi OLAN ve en GÜNCEL (en son)
   referans_ayi'na ait satır tutulacak şekilde script güncellendi
   (`genisletme_25c_karisik_frekans_birlestir.py`, proxy bloğu). Üç
   çakışma grubunun ikisinde her iki taraf da gerçek veri içeriyordu
   (en yeni referans ay tutuldu); üçüncüsünde (2025-01 gerçek veri,
   2025-02 tamamen boş/henüz-yayımlanmamış "yer tutucu" satır) boş olan
   elendi. Düzeltme sonrası tablo tam 4234 satır (= benzersiz gün
   sayısı) çıktı, doğrulandı.

3. **[BULUNDU VE DÜZELTİLDİ] `enag_endeks` sütunu tamamen boştu (0/4234
   dolu).** Kaynak dosyada (`enag_aylik_2021_2026.csv`) bu sütun kayıtlı
   ama TÜM 65 satırda boş — merge/birleştirme hatası değil, ENAG'ın
   kendi doğası: yalnızca aylık/yıllık YÜZDE DEĞİŞİM yayımlıyor, endeks
   SEVİYESİ hiç yayımlamıyor. **Düzeltme:** boş sütun tablodan
   çıkarıldı (`enag_aylik_degisim`, `enag_yillik_degisim` kaldı).

---

## 7. Veri Örneği

**(a) Tamamen günlük-dolu bir satır** (hiçbir aylık kaynağın as-of
gününe denk gelmiyor, kur verisi dolu):

| tarih | usdtry_alis | eurtry_alis | noter_referans_ay | tufe_referans_ay |
|---|---|---|---|---|
| 2026-07-31 | 47.3274 | 54.2273 | NaN | NaN |

**(b) Aylık verinin düştüğü bir satır** (noter devri as-of günü,
2026-06 referans ayı, aynı gün kur verisi de dolu):

| tarih | noter_referans_ay | noter_devir_toplam_adet | usdtry_alis |
|---|---|---|---|
| 2026-07-01 | 2026-06 | 941964.0 | 46.5747 |

**(c) Ara gün — hiçbir aylık/çeyreklik/olay-bazlı verinin düşmediği**
(yalnızca günlük kur verisi dolu, tüm `..._referans_ay` sütunları NaN):

| tarih | usdtry_alis | eurtry_alis | tüm `..._referans_ay` sütunları |
|---|---|---|---|
| 2026-07-31 | 47.3274 | 54.2273 | NaN (hepsi) |

(Not: (a) ve (c) aynı örnek satıra denk geldi — 2026-07-31 hem
tamamen-günlük hem de "ara gün" tanımına birlikte uyuyor, bu iki farklı
kriterin kesişebileceğini gösteriyor; istenirse farklı bir tarihten
ikinci bir "ara gün" örneği ayrıca çıkarılabilir.)

---

## 8. Açık Sorular / PM Onayı Gerekenler

1. **Altın/TRY'nin aylık olması** (Bölüm 6, madde 1) — proje bunu
   günlük bir özellik olarak mı bekliyordu? Aylık kabul edilip devam mı
   edilsin, yoksa ücretli/alternatif bir günlük kaynak mı araştırılsın?
2. **BETAM'ın çift-ay yayım deseni** (Bölüm 6, madde 2) — bu tablo
   tasarımında "en güncel referans ayı tutulur" kuralı benimsendi;
   alternatif olarak "her iki ayı da ayrı sütunlarda tut" gibi bir
   yaklaşım tercih edilirse script kolayca uyarlanabilir.
3. **`enag_endeks`'in tamamen boş olması** (Bölüm 6, madde 3) — ENAG
   gerçekten endeks seviyesi yayımlamıyor mu, yoksa `data/raw/enag/`
   kaynağı daha zengin bir ENAG serisiyle mi güncellenmeli? (Önceki
   görevlerde de ENAG kapsamı sınırlıydı, bu tutarlı bir bulgu.)
4. **Sonraki adım önerisi (başlatılmadı, yalnızca öneri):** bu
   karışık-frekans tablosu üzerinde korelasyon analizi YAPILMADI (görev
   talimatının YAPMA listesine uygun) — istenirse ayrı bir görev olarak
   ele alınabilir.
