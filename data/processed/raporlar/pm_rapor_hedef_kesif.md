---
başlık: PM Raporu — Hedef Keşif: Noter Devir Hacmi × DOM (Days-on-Market)
aşama: Genişletme Aşama 8 (keşifsel, K1 karar değişikliği DEĞİL)
tarih: 2026-07-27
girdi: data/processed/genisletme/veri_2018_bugun_etiketli.csv (102 satır, 2018-01 → 2026-06)
kaynak_kod: scripts/veri/genisletme_8_hedef_kesif_noter_dom.py
prompt_arşivi: prompts/veri/08_hedef_kesif_noter_dom_prompt.md
durum: tamamlandı (keşif) — karar PM/proje sahibine bırakıldı
---

## Önemli çerçeve hatırlatması

Bu görev bir **karar** değil, bir **keşif**tir. Hiçbir yerde hedef tanımı (K1)
değiştirilmedi, "şu hedef seçilmeli" denmedi. Aşağıdaki bulgular kanıttır,
karar değildir.

**Örneklem büyüklüğü uyarısı (rapor boyunca geçerli):** DOM (proxy_dom_gun) ve
ondan türeyen her şey (kompozit endeks dahil) yalnızca **n=25** geçerli aylık
geçişle sınırlı. Bu raporda toplam **39 korelasyon testi** (Görev 3: 13 lag,
Görev 5: 2 fiyat türü × 13 lag) çalıştırıldı; **hiçbiri Bonferroni-düzeltmeli
anlamlılık eşiğinden (α=0.05/39≈0.0013) sağ çıkmadı**. Bu raporun hiçbir
bulgusu "kanıtlanmış ilişki" değildir — en iyi ihtimalle "izlenmeye değer
sinyal"dir.

---

## 1) Kaynak güvenilirlik ve sürdürülebilirlik notu

**Noter devir hacmi:** Artık bülten-ID tahminine dayanmıyor. Güncel script
(`genisletme_2a_noter_devir.py`) 5 ayrı TÜİK "Motorlu Kara Taşıtları" aylık
bülteninin (Aralık 2019, Aralık 2021, Aralık 2023, Aralık 2025, Haziran 2026)
**resmi indirilebilir .xls tablosundan** (kaynak seviyesi B) birebir okunmuş,
her değer ilgili bültenin kendi metin cümlesiyle çapraz doğrulanmış, çakışan
yıllar (2020, 2022, 2025) komşu bültenlerde birebir eşleşmiş 102 satırlık
sabit (hardcoded) bir tablodur. **Bu, canlı/sorgulanabilir bir API değildir**
— TÜİK veri portalı (veriportali.tuik.gov.tr) JS-render bir SPA olduğu için
WebFetch ile okunamıyor, yalnızca tarayıcı destekli manuel gezinmeyle
bulunabiliyor; ayrıca portal "önceki bültenler" zincirini yalnızca 7 aylık
parçalar halinde geriye veriyor, doğrudan bir arama/arşiv API'si yok. Resmi
bir API'ye geçiş şu an İÇİN PRATİK DEĞİL (böyle bir API tespit edilmedi);
mevcut "bülten bul → indir → hardcode et → sonraki bültenle çapraz doğrula"
yöntemi, kırılgan olsa da bugüne kadar en güvenilir yöntem olarak kaldı. Bunun
somut sürdürülebilirlik maliyeti: **her yeni ay için scriptin elle
güncellenmesi gerekiyor**, otomatik değil (açık soru olarak Bölüm 7'de tekrar
not edildi).

**DOM (proxy_dom_gun):** BETAM sahibindex kaynaklı, 2024-01→2026-06 aralığında
30 ay potansiyelken yalnızca 28'i dolu — **2024-05 ve 2025-02** ayları için
BETAM hiç rapor yayımlamamış (bilinen, önceden belgelenmiş bir boşluk). Bu 2
boşluk ayı, aylık log-değişim serisinde **4 geçişi** (o aya giren + o aydan
çıkan) NaN yapıyor, bu yüzden bu raporun her yerinde n=30 değil **n=25**
kullanılıyor. Bu, zaten küçük olan örneklemi daha da küçültüyor ve aşağıdaki
tüm istatistiksel testlerin gücünü (özellikle mevsimsellik ve lag analizi)
ciddi biçimde sınırlıyor.

---

## 2) Her serinin tek başına davranışı (Görev 2)

### noter_devir_toplam_adet (n=102, 2018-01→2026-06, hiç eksik yok)

| Ölçüm | Değer |
|---|---|
| Ortalama | 799.762 adet/ay |
| Medyan | 821.193 adet/ay |
| Std sapma | 171.857 (değişim katsayısı ≈ %21) |
| Min | 348.678 (2020-04 — COVID kapanma ayı) |
| Maks | 1.158.490 (2025-12) |

- **Durağanlık (ADF):** Ham seviye BİLE durağan (ADF ist=-5.21, p<0.0001,
  %5 kritik değer -2.89). Log-değişim de durağan (ADF ist=-5.51, p<0.0001).
  Yani seri belirgin bir trend taşımıyor, sabit bir ortalama etrafında
  dalgalanıyor — bu, doğrudan seviye üzerinde çalışmayı da mümkün kılan
  olumlu bir sonuç.
- **Mevsimsellik:** Ay-dummy regresyonu (log-değişim ~ ay, n=101, 12 ay,
  ortalama ~8.4 gözlem/ay — güvenilir örneklem) **R²=%18.3**. Gerçek ama orta
  düzeyde bir mevsimsel bileşen var; varyansın %82'si mevsimsellik dışı
  etkenlerden geliyor.
- **ACF/PACF (12 lag):** Neredeyse tamamı güven bandı içinde — güçlü bir
  otokorelasyon yapısı yok. Lag-1'de hafif negatif (~-0.20, bandın sınırında,
  hafif ay-içi "geri dönüş" eğilimi) ve lag-12'de hafif pozitif (~0.25, bandın
  hafif dışında, yıllık yankı) — ikisi de zayıf ama mevsimsellik bulgusuyla
  tutarlı.

### proxy_dom_gun (n=28 dolu, 2024-01→2026-06 penceresi)

| Ölçüm | Değer |
|---|---|
| Ortalama | 22,1 gün |
| Medyan | 22,1 gün |
| Std sapma | 1,76 gün (değişim katsayısı ≈ %8 — noter'e göre çok daha az oynak) |
| Min | 19,1 gün |
| Maks | 25,6 gün |

- **Durağanlık (ADF):** Ham seviye durağan DEĞİL görünüyor (ADF ist=-2.39,
  p=0.145) — ama n=28 ile ADF testinin gücü zaten düşük, bu sonucu ihtiyatla
  okumak gerekir (ne "kesin trend var" ne de "kesin yok" diyebiliriz).
  Log-değişim durağan (ADF ist=-4.65, p=0.0001).
- **Mevsimsellik — DİKKAT, YANILTICI SAYI:** Ay-dummy regresyonu R²=%70,1
  çıkıyor ama bu rakam GÜVENİLMEZ: n=25 gözlem 12 ay kategorisine
  dağıtılıyor (ortalama ~2 gözlem/ay), model neredeyse doymuş (12 kategorik
  parametre, 25 gözlem) — bu koşullarda yüksek R² doğal bir overfitting
  sonucudur, gerçek bir mevsimsel örüntü KANITI olarak okunmamalı. Boxplot
  görsel olarak Ocak/Nisan/Haziran-Temmuz'da daha yüksek, Eylül-Kasım'da daha
  düşük DOM gösteriyor ama her kutu yalnızca ~2 noktadan oluşuyor — bu bir
  "dağılım" değil, iki nokta arasına çizilmiş bir çizgi. **Daha fazla ay
  biriktikçe yeniden ölçülmeli.**
- **ACF/PACF (11 lag, n azlığı nedeniyle güven bandı çok daha geniş):** Tüm
  lag'ler bandın içinde — tespit edilebilir bir otokorelasyon yok (ama bu,
  "yok" anlamına gelmiyor, "bu örneklemle tespit edilemedi" anlamına geliyor).

---

## 3) Noter devri × DOM ilişkisi (Görev 3)

- **Eşzamanlı (lag=0):** Pearson r=0,021 (p=0,92), Spearman r=-0,056
  (p=0,79) → **pratikte hiç ilişki yok**.
- **Çapraz-korelasyon (-6..+6 ay):** En yüksek |r| lag=+3'te (DOM, noter'i
  3 ay önden mi etkiliyor sorusu): r=0,389 (p=0,074, n=22) — tek başına bile
  anlamlı değil, 13 lag test edildiği için çoklu-test bağlamında daha da
  zayıflıyor.
- **Ekonomik yorum:** Bu örneklemde noter devri (işlem HACMİ) ile DOM (ilan
  SÜRESİ) arasında net bir eşzamanlı veya öncü-gecikmeli ilişki YOK. Bu,
  "ikisi aynı piyasa hareketliliği olgusunun iki yüzü" varsayımını
  DOĞRULAMIYOR. Aksine — Görev 4b'deki PCA bulgusuyla tutarlı biçimde (DOM'un
  ortak bileşene yükü neredeyse sıfır: 0,091) — DOM'un noter/satış-oranı/ODMD
  gibi "hacim" tabanlı göstergelerden **bağımsız, farklı bir bilgi** taşıdığı
  görülüyor. Bu bir dezavantaj değil: eğer DOM gerçekten ayrı bir sinyal
  taşıyorsa, onu bir hacim-kompozitine gömmek (Görev 4a) bilgi kaybına yol
  açabilir.

---

## 4) Kompozit "piyasa aktivite endeksi" (Görev 4)

- **4a — basit yaklaşım:** `piyasa_aktivite_endeksi_basit` = ortalama(
  z(noter log-değişim), z(-DOM log-değişim), z(satış-oranı log-değişim) ),
  n=25. (DOM işareti çevrildi: DOM düşerse piyasa hızlanıyor sayılır.)
- **4b — PCA (4 bileşen: noter, -DOM, satış-oranı, ODMD), n=25:**
  - PC1 açıklanan varyans: **%54,7** (PC2 %28,4, PC3 %13,8, PC4 %3,1).
  - PC1 yükleri: noter=0,639, **-DOM=0,091 (neredeyse sıfır)**,
    satış-oranı=0,585, ODMD=0,491.
  - Dürüst cevap — "tek bileşen bu 4 seriyi ne kadar iyi özetliyor?": **orta
    derecede (%54,7)**, ve esasen **DOM'u dışarıda bırakarak**. PC1 aslında
    noter+satış-oranı+ODMD üçlüsünün ortak "hacim" hareketi; DOM bu ortak
    harekete pratik olarak katkı vermiyor.
- **4c — kompozit endeksin kendi yönü:** sigma=0,7125, eşik=k·sigma=0,356
  (k=0,5, projedeki standart). Sınıf dağılımı (n=25): **stable=10 (%40),
  up=8 (%32), down=7 (%28)**. Bu, fiyat hedeflerinin çarpık dağılımlarına
  (nominal 17up/7stable/1down; reel 1up/8stable/16down) kıyasla **çok daha
  dengeli** — potansiyel bir hedef olarak istatistiksel açıdan çekici bir
  özellik (daha kolay öğrenilebilir sınıf dengesi).
- **4d — görsel:** `kompozit_endeks_bilesenler.png` — kompozit endeks (kalın
  mavi çizgi) ve 3 bileşeni (z-score ortak eksende) aynı grafikte. Kompozit,
  görsel olarak noter ve satış-oranıyla büyük ölçüde birlikte hareket ediyor;
  DOM (turuncu) zaman zaman belirgin biçimde ayrışıyor (ör. 2024-08/09
  civarı) — 4b'deki düşük PCA yükünün görsel karşılığı.

---

## 5) EN KRİTİK BÖLÜM — kompozit endeks × fiyat yönü ilişkisi (Görev 5)

- **proxy_nominal ile eşzamanlı:** n=25, Pearson r=**-0,392** (p=0,053,
  sınırda), Spearman r=-0,337. **İşaret, genisletme_7'de noter_devir_adedi
  için beklenen yönün (pozitif: hacim↑ → fiyat↑) TERSİ** — kompozitin DOM ve
  satış-oranı bileşenleri bu işareti karıştırmış olabilir, tek başına
  yorumlanmamalı.
- **proxy_reel ile eşzamanlı:** n=25, Pearson r=-0,194 (p=0,352, anlamsız),
  Spearman r=-0,119.
- **Lag analizi:** En dikkat çekici tek nokta **lag=+1** (endeks, fiyatı 1 ay
  önden mi yönlendiriyor): proxy_nominal için r=**+0,451** (p=0,027, n=24) —
  tek başına anlamlı görünüyor. **AMA:** (i) bu görevde 26 test yapıldı
  (2 fiyat türü × 13 lag), α=0,05 ile şans eseri ~1,3 "anlamlı" sonuç
  beklenir; Bonferroni'yle (α≈0,0019) bu p-değeri anlamlılığını kaybediyor.
  (ii) İşaret tutarsız: lag=0'da NEGATİF (-0,392), lag=+1'de POZİTİF
  (+0,451) — aynı ilişkinin "önce ters sonra düz" yön değiştirmesi zayıf bir
  ekonomik hikaye, tek örneklemin gürültüsüne işaret ediyor.

**5b) AÇIK DEĞERLENDİRME (karar değil):**

| | HEDEF olarak | ÖNCÜ FEATURE olarak |
|---|---|---|
| **Lehine** | Dengeli sınıf dağılımı (4c); PCA'nın gösterdiği gerçek ortak varyans (%54,7); tek başına yorumlanabilir bir "piyasa hareketliliği" ölçüsü | lag=+1'de bir sinyal var (istatistiksel olarak kırılgan da olsa); DOM'un PCA'da düşük yük vermesi, "gürültü+gerçek sinyal karışımı" bir feature seti olarak modele eklenip feature-importance ile test edilebileceğini düşündürüyor |
| **Aleyhine** | Fiyat yönüyle ilişkisi zayıf/anlamsız (en iyi p=0,053) — nihai amaç fiyat yönü tahminiyse, endeksin kendisi fiyatla güçlü bağlantılı değil | n=25 ile hiçbir bulgu çoklu-test düzeltmesinden sağ çıkmıyor; "feature olarak değerli" demek de şu an erken |

**Dürüst sonuç:** Bu örneklem büyüklüğüyle (n=25) ne "kompozit endeks bağımsız
bir HEDEF olmalı" ne de "güçlü bir ÖNCÜ FEATURE'dır" iddiası kanıtla
desteklenmiyor. En sağlam ve tekrarlanabilir bulgu, **DOM'un noter/satış-
oranı/ODMD'den bağımsız bilgi taşıdığı** (Görev 3 + PCA, iki farklı yöntemle
tutarlı) — bu da DOM'u kompozite gömmek yerine **ayrı bir feature** olarak
tutmanın daha savunulabilir olduğunu düşündürüyor.

**5c) K11 kararına ampirik dayanak:** Bulunamadı. lag=+1 bulgusu (r=0,45,
p=0,027) tek başına umut verici görünse de çoklu-test bağlamında güvenilir
değil. Bu, K11'i ("hacim = güven düzeyi/destekleyici sinyal") **çürütmüyor**
ama **doğrulamıyor da** — "veri henüz yetersiz, proxy fiyat serisi
uzadıkça (n arttıkça) yeniden test edilmeli" şeklinde okunmalı.

---

## 6) Görsel envanteri (data/processed/analiz/hedef_kesif_gorseller/)

| Dosya | Ne gösteriyor |
|---|---|
| `noter_devir_toplam_adet_zaman_serisi.png` | 2018-2026 ham seviye + 3 aylık hareketli ortalama |
| `proxy_dom_gun_zaman_serisi.png` | 2024-2026 ham seviye + 3 aylık hareketli ortalama, 2 boşluk ayı çizgide görünmez bırakılıyor |
| `noter_devir_toplam_adet_ay_boxplot.png` | Ay-bazlı dağılım (n≈8-9/ay, güvenilir) |
| `proxy_dom_gun_ay_boxplot.png` | Ay-bazlı dağılım (n≈2/ay, DİKKAT etiketiyle işaretli, güvenilmez) |
| `noter_devir_toplam_adet_acf_pacf.png` | Log-değişim otokorelasyonu — zayıf lag-1/lag-12 sinyali |
| `proxy_dom_gun_acf_pacf.png` | Log-değişim otokorelasyonu — tespit edilebilir yapı yok (geniş güven bandı) |
| `noter_dom_scatter.png` | Eşzamanlı log-değişim saçılımı, r≈0,02 (ilişkisiz) |
| `cross_correlation_noter_dom.png` | -6..+6 lag çapraz-korelasyon çubuk grafiği, en yüksek |r| lag+3'te ama anlamsız |
| `kompozit_endeks_bilesenler.png` | Kompozit endeks + 3 bileşeni, ortak z-score ekseninde |
| `kompozit_proxy_nominal_ccf.png` | Kompozit → nominal fiyat, -6..+6 lag |
| `kompozit_proxy_reel_ccf.png` | Kompozit → reel fiyat, -6..+6 lag |

---

## 7) Açık sorular / PM onayı gerekenler

1. **Noter devir sürdürülebilirliği:** Veri canlı bir API'den değil, elle
   güncellenen TÜİK bültenlerinden hardcode ediliyor — her yeni ay scriptin
   manuel güncellenmesini gerektiriyor. İşletim maliyeti olarak not edilmeli.
2. **DOM kompozite dahil mi, ayrı mı kalmalı?** PCA bulgusu DOM'un ayrı bir
   sinyal taşıdığını gösteriyor; kompozite gömmek bilgi kaybına yol açabilir.
   Ayrı feature mi, ayrı bir "piyasa hızı" alt-endeksi mi — tasarım kararı,
   PM'e bırakılıyor.
3. **Kompozit endeks HEDEF mi FEATURE mi?** Görev 5 bulguları hiçbirini kesin
   desteklemiyor (bkz. Bölüm 5b tablosu). n arttıkça yeniden test edilmesi
   öneriliyor.
4. **Çoklu-test:** Bu raporda 39 korelasyon testi çalıştırıldı, hiçbiri
   Bonferroni-düzeltmesinden sağ çıkmadı — projenin genel "az-gözlem
   uyarısı" kültürüyle tutarlı, ayrıca kayda geçirilir.
5. **DOM mevsimsellik R²=%70,1 rakamı** overfitting nedeniyle yanıltıcı —
   "gerçek mevsimsellik" olarak değil, "örneklem küçüklüğü nedeniyle
   güvenilmez" olarak okunmalı; n arttıkça yeniden ölçülmeli.

---

## 8) Veri örneği (ham, piyasa_aktivite_endeksi.csv)

İlk 3 satır:

```
referans_ayi,noter_log_degisim,dom_flipped_log_degisim,satis_orani_log_degisim,piyasa_aktivite_endeksi_basit,piyasa_aktivite_yon,pca_pc1_skoru,proxy_nominal_log_degisim,proxy_reel_log_degisim
2024-02,0.080109,0.074414,0.070874,0.752269,up,1.269903,-0.005433,-0.049729
2024-03,0.020179,0.034938,0.000000,0.163397,stable,0.117989,0.003795,-0.027342
2024-04,-0.076487,-0.085158,-0.105361,-1.030399,down,-1.761154,0.010167,-0.021136
```

Son 3 satır:

```
referans_ayi,noter_log_degisim,dom_flipped_log_degisim,satis_orani_log_degisim,piyasa_aktivite_endeksi_basit,piyasa_aktivite_yon,pca_pc1_skoru,proxy_nominal_log_degisim,proxy_reel_log_degisim
2026-04,0.054628,-0.009050,-0.019324,-0.048780,stable,0.057757,0.006873,-0.034097
2026-05,-0.201325,-0.069593,-0.055152,-1.041856,down,-1.714003,0.005975,-0.011027
2026-06,0.225031,-0.057158,0.005141,0.180220,stable,1.191163,-0.005119,-0.014937
```

(Dosyanın tamamı `data/processed/analiz/piyasa_aktivite_endeksi.csv` içinde
25 satır olarak mevcuttur.)
