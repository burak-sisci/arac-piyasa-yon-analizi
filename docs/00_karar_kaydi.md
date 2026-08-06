---
dokuman_tipi: karar_kaydi
proje: "Araç Piyasası Fiyat Yönü Tahmini — Literatür Taraması"
tarih: 2026-07-13
revizyon: v9 — K9 eklendi: aktif Aşama B hedefi hacim yönüne kaydırıldı (2026-08-06, Codex denetimi)
iliskili_dokuman: 00_master_plan_literatur_taramasi.md
durum: onaylandi
---

# Karar Kaydı — Master Plan Açık Noktaları ve Faz Bulguları

Bu kararlar tüm faz promptlarına ve dökümanlarına bağlayıcıdır. Yeni fazlardan
çıkan bulgular yeni karar/not maddesi doğurabilir; her ekleme revizyon notuyla
işaretlenir.

## A. Kapsam Kararları (K)

**K1 — Tahmin ufku:** Faz 1 gerekçeli olarak **aylık ufku** önerdi (ikincil:
2-3 aylık proxy ufuk denenmeli — Label Horizon Paradox). Durum: aylık ufuk
çalışma varsayımıdır; geliştirici ekibin iş tarafı beklentisiyle teyit edilecektir.

**K2 — "Stable" bandı:** Faz 1 bulgusu: sabit yüzde eşiği yerine
**oynaklık-uyarlamalı bant** (segment bazlı, ±0.5σ–1σ taranarak) birincil
öneridir; quantile/tercile tabanlı bölme yedek seçenektir. Neutral sınıf oranı
%60'ı aşarsa quantile'a geçilir.

**K3 — İkinci el / yeni araç kapsamı:** Tarama İKİNCİ EL piyasası odaklıdır.
Yeni araç yalnızca Faz 2'de, ikinci eli etkileyen dışsal faktör (sıfır araç
zamları, kampanya yoğunluğu, arz kıtlığı) olarak ele alınır.

**K4 — Coğrafi kapsam (hibrit):** Metodoloji fazları (1, 3, 5, 6, 7, 8)
uluslararası literatürü tarar. Faz 2 Türkiye odaklıdır. Faz 4 uluslararasıdır,
Türkiye çalışmaları öncelikli raporlanır.

**K5 — Şirket bilgisi sınırı:** Çalışma Arabam.com'dan bağımsız, tamamen kamuya
açık kaynaklarla yürütülür; çıktılar sonra şirketteki geliştirici ekibe
sunulacaktır. Repo public'tir. Hiçbir faz dökümanına şirket içi veri, rapor,
metrik veya yayınlanmamış bilgi giremez.

**K6 — Kaynak türü kapsamı:** Geniş kapsam: peer-reviewed literatür + gri
literatür (arXiv/SSRN, tez) + resmi kurum yayınları (TÜİK, TCMB, ODMD, OSD,
Resmî Gazete) + nitelikli endüstri kaynakları. Sektör beyanları ve basın
haberleri kullanılabilir ancak dökümanda "düşük kanıt gücü" olarak işaretlenir.

**K7 — Faz çıktı uzunluğu:** Üst sınır yoktur. Derinlik hedef kaynak sayısıyla,
disiplin kalite kontrol listesiyle sağlanır.

**K8 — Model hedefi: İLAN FİYATI (Faz 2 bulgusu).** Türkiye'de kamuya açık tüm
ikinci el fiyat serileri **ilan (asking) fiyatıdır**; gerçekleşen işlem fiyatı
kamuya açık değildir (noter devir verisi yalnızca adet içerir).

KARAR: Projenin tahmin hedefi **ilan fiyatının yönü**dür (up/down/stable).
Bu bilinçli ve belgelenmiş bir tasarım tercihidir.
- Tüm dökümanlar "ilan fiyatı yönü" terminolojisini kullanır; "piyasa fiyatı"
  veya "işlem fiyatı" ifadeleri kullanılmaz.
- İlan–işlem farkı (pazarlık marjı) bir belirsizlik kaynağı olarak sentezde
  açıkça raporlanır; sıfır varsayılmaz.
- İlan verisinin yapısal sorunları (seçilim yanlılığı, ölü/tekrarlanan ilanlar,
  fiyat düşürme davranışı) Faz 4 ve Faz 8'de ele alınır.

**K8 — Operasyonel ek not (2026-08-06, Codex denetimi ile onaylandı):**
Aşama B veri mühendisliği çalışması sırasında ortaya çıkan üç operasyonel
netleştirme, K8'in yorumlanmasına bağlayıcıdır (yeni bir kaynak iddiası
eklemez, yalnızca mevcut K8 kararının uygulamadaki kapsamını netleştirir):

1. **Rol ayrımı:** K8'in operasyonel birincil hedefi BETAM/sahibindex
   `proxy_fiyat_cari_tl` serisinin **NOMİNAL** aylık ilan fiyatı yönüdür.
   **Reel** yön (TÜFE deflatörlü) ikincil bir sağlamlık/duyarlılık hedefidir,
   birincilin yerini almaz. `noter_devir_otomobil_adet` bir **hacim**
   serisidir — yalnızca yardımcı özellik (feature) veya ayrı, kendi başına
   keşifsel bir hacim görevi olarak ele alınır; fiyat baseline'ı olarak
   sunulamaz.
2. **N<50 keşifsel geçit:** `proxy_fiyat_cari_tl` serisinde şu an 28 dolu
   fiyat ayı / ~25 geçerli (hesaplanabilir) yön etiketi bulunmaktadır. N12
   eşiğine göre bu **N<50** demektir: bu veri hacmiyle yalnızca **keşifsel**
   analiz yapılabilir; başarı/baseline iddiası kurulamaz ve model eğitimi
   **başlatılamaz**. Eşik N≥50'ye ulaşana kadar geçerlidir.
3. **Stable bandı uygulaması (K2 netleştirmesi):** Oynaklık-uyarlamalı
   sigma/tercile eşiği **tüm seri üzerinden tek seferde** hesaplanıp sabit
   uygulanamaz (bu, gelecek gözlemleri görmüş olmak anlamına gelir —
   sızıntı). Her değerlendirme kesiminde eşik **yalnızca o ana kadarki
   geçmiş/eğitim penceresinden** (genişleyen pencere, N12 as-of ilkesi) fit
   edilir. Nominal ana senaryo **k=0.5**'tir; k=0.75 ve k=1.0 duyarlılık
   senaryolarıdır. Tercile tabanlı bölme yalnızca ikincil bir duyarlılık
   kontrolüdür (K2'deki yedek seçenek rolü değişmedi).

K9 kapsamında `scripts/model/yon_degerlendirme.py`, hiçbir commit'e girmemiş
ve artık kaldırılmış olan geçici bir keşifsel fiyat-denetim script'inin
yerine, **target-bağımsız bir değerlendirme altyapısına dönüştürüldü**
(ne fiyata ne hacme özel varsayım taşımıyor — hangi seriyi/eşiği
kullanacağına çağıran script karar verir). K8'in NOMİNAL ilan-fiyatı yönü
hedefi ve N<50 keşifsel geçidi bilgisi kalıcıdır (fiyat serisi hâlâ N<50
durumundadır), ancak Aşama B'nin şu anki aktif çalışması K9'da tanımlıdır.

**K9 — Aktif Aşama B kararı: hacim yönü, doğrudan üç sınıf (2026-08-06,
Codex denetimi ile onaylandı).** K8'in ilan-fiyatı yönü hedefi N<50 keşifsel
geçidinde takılı kaldığı için (bkz. yukarıdaki K8 operasyonel ek notu),
Aşama B'nin şu anki aktif operasyonel çalışması **hacim** hedefine kaydırıldı:

1. **Target:** `noter_devir_otomobil_adet` (noter devri ikinci el otomobil
   adedi) — bir **hacim** serisidir, ilan fiyatı DEĞİLDİR. K8'in "ilan fiyatı
   yönü" kararının yerini ALMAZ; K8 fiyat hedefi için hâlâ geçerli ve
   dondurulmuş (N<50) durumdadır. İki hedef PARALEL ve AYRI konulardır.
2. **Ufuk ve sınıflar:** doğrudan üç sınıflı (up/stable/down) aylık yön;
   etiket, bir günlük satırın bulunduğu referans ayın hacmi ile bir sonraki
   takvim ayının hacmi karşılaştırılarak kurulur. Frekans GÜNLÜK kalır (ay
   hizalı doldurma nedeniyle ay-içi tekrar var — pseudo-replikasyon riski
   PM raporunda açıkça işaretlenir).
3. **Stable bandı:** SABIT ±%5 (K2'deki oynaklık-uyarlamalı/sigma tabanlı
   yaklaşım bu görev için kullanılmaz — K2 fiyat hedefine özgü kalır, hacim
   hedefinde basit ve yorumlanabilir sabit eşik tercih edildi). ±%3/±%10
   yalnızca duyarlılık senaryosudur.
4. **Ürün çıktısı:** `p_down`/`p_stable`/`p_up` + seçilen sınıf + maksimum-
   olasılık tabanlı `raw_confidence`. Kalibre edilmemiş olasılıklar açıkça
   "raw" adlandırılır; validation örneklemi (özellikle DF-B'de) güvenilir
   kalibrasyon için yetersizse kalibre edilmiş gibi sunulmaz.
5. **Gerekçe:** (a) veri yeterliliği — hacim serisinde fiyat serisine göre
   çok daha fazla dolu/geçerli ay var (N<50 kapısını fiyattan farklı olarak
   büyük ölçüde aşıyor); (b) sınıf dağılımı fiyat serisine göre daha dengeli.
6. **Kapsam sınırı:** Bu sinyal fiyatlama kararlarına bir GİRDİ/yardımcı
   göstergedir — K8'in "ilan fiyatı yönü" hedefinin YERİNE GEÇMEZ ve
   doğrudan fiyat tahmini olarak sunulamaz.

Uygulama: `scripts/model/yon_degerlendirme.py` (target-bağımsız saf
fonksiyonlar: sabit-yüzde-eşikli etiketleme, purge'li kronolojik split,
ay-ağırlığı, olasılık doğrulama, MCC/macro-F1/accuracy/per-class metrikleri)
ve `scripts/model/model_06_hacim_yon_siniflandirma.py` (AutoGluon
`TabularPredictor(problem_type="multiclass")` ile DF-A/DF-B ayrı eğitim —
bkz. `data/processed/raporlar/pm_rapor_hacim_yon_3sinif_baseline.md`).

**K10 — Haftalık güncellenen aylık hacim yönü nowcast'i (2026-08-06,
proje sahibi kararı; Rota uygulayıcı, Pusula karar ortağı).** K9'un hedefi
ve üç sınıfı korunarak operasyonel tahmin sözleşmesi aşağıdaki biçimde
profesyonelleştirildi:

1. **Değişmeyen hedef ve sınıflar:** Target
   `noter_devir_otomobil_adet`; çıktı `down/stable/up`. Etiket, cari ay M'nin
   resmî noter otomobil devir adedinin bir önceki takvim ayı M-1'e göre yüzde
   değişimidir. Ana stable bandı K9 ile aynı, kapalı **±%5** aralığıdır.
2. **Tahmin ritmi ve ufuk:** Her pazartesi, yalnız önceki pazar cut-off'una
   kadar bilinen verilerle **içinde bulunulan ayın kapanış yönü** nowcast
   edilir. Aylık target haftalık target'mış gibi bölünmez, enterpole edilmez
   veya haftalara paylaştırılmaz.
3. **Bağımsız örnek birimi:** Aynı ayın 4-5 haftalık snapshot'ı tek bir aylık
   gerçekleşmeyi paylaşır. Tümü aynı kronolojik split/fold içinde tutulur ve
   snapshot ağırlıkları ay başına toplam 1 olacak biçimde kurulur. Etkin N,
   snapshot sayısı değil bağımsız etiketli ay sayısıdır.
4. **Gerçek-zaman/sızıntı kuralı:** Cari ay target değeri ve lag-1 target
   feature değildir. Tarihsel kesin yayın tarihleri eksik olduğu sürece aylık
   feature'lar konservatif olarak en az iki takvim ayı geciktirilir; target
   yalnız lag2/lag3/lag12 olarak kullanılabilir. Gerçek günlük göstergeler
   yalnız cari ay başlangıcından cut-off'a kadarki gözlemlerle özetlenir.
5. **Nowcast türü:** Kamuya açık noter serisinde ay-içi kümülatif target
   bulunmadığından bu çalışma **yüksek frekanslı öncü gösterge tabanlı cari-ay
   nowcast'idir**; kısmi noter target ekstrapolasyonu değildir. Ay-içi resmî
   target ileride bulunursa, as-of kanıtı olmadan sisteme eklenemez.
6. **Validasyon:** Ay-gruplu kronolojik/expanding değerlendirme, fold
   sınırlarında iki aylık embargo, birincil global/Gorodkin MCC ve macro-F1,
   ikincil accuracy/per-class recall; majority, persistence ve mevsimsel
   t-12 baseline'ları modelden önce sabitlenir. Test dönemi Stage 1'de
   **kilitlenmemiştir**; etiket/yayım/tatil sözleşmesi tamamlandıktan sonra
   ayrıca onaylanacaktır.
7. **Takvim:** 2429 sayılı Kanun ve Diyanet yıllık listeleriyle doğrulanan tam
   ve yarım gün resmî/dini tatiller, iş-günü eşdeğeri ve ay-içi ilerleme
   feature'larına dahil edilir.
8. **Veri yeterliliği:** DF-A 101 bağımsız etiketli ayla N≥50 geçidini aşar.
   DF-B 29 bağımsız ayla N<50'dir; yalnız keşifsel tutulur ve doğrulayıcı model
   karşılaştırmasına sokulmaz.

Uygulama sözleşmesi: `scripts/model/haftalik_aylik_nowcast.py`,
`scripts/model/turkiye_tatil_takvimi.py` ve
`scripts/model/model_07_haftalik_nowcast_veri_hazirligi.py`. K9'un eski
aylık-ileri sınıflandırma baseline'ı denetim izi olarak korunur; K10 onu
sessizce yeniden yazmaz.

## B. Faz Bulgularından Doğan Bağlayıcı Notlar (N)

**N1 (Faz 2) — Kompozisyon düzeltmesi modelin işidir.** Kamuya açık Türk
endeksleri (BETAM sahibindex, arabam.com) karma/kilometre/hedonik düzeltmesizdir.
Model kompozisyon düzeltmesini kendi içinde yapmalıdır. → Faz 5'te çözüldü (N10).

**N2 (Faz 2) — Arz değişkeni rejime bağlı çift yönlüdür.** Kıtlık → prim yukarı;
kampanya/bolluk → aşağı. Sabit katsayı dönem geçişlerinde hatalıdır. → Faz 5'te
rejim etkileşim feature'ı; Faz 6'da GBM split/etkileşim ile ele alındı.

**N3 (Faz 1) — Etiketleme literatüründe boşluk vardır.** Düşük frekanslı,
ilan-tabanlı piyasalar için doğrudan ampirik doğrulama YOKTUR. Projeye özgü
deney gerektirir.

**N4 (Faz 3) — SMOTE ve resampling KULLANILMAYACAKTIR.** (van den Goorbergh vd.
2022, JAMIA). ZORUNLU SIRALAMA: (1) class weighting → (2) threshold-moving →
(3) post-hoc kalibrasyon. Karşı-bulgu işaretli. → Faz 6'da uygulandı.

**N5 (Faz 3) — Metrik ve validasyon zorunlulukları.** Birincil metrik: MCC ve
macro-F1; accuracy tanımlayıcı. Rastgele k-fold CV YASAKTIR; kronolojik ayrım
zorunludur. → Faz 7'de protokole çevrildi (N12).

**N6 (Faz 3) — Başarı kriteri: naif baseline üzeri iyileşme.** Referans:
persistence + "her şeye stable". Geçilemezse "sinyal yok" değerli negatif
bulgudur. %70+ iddiaları hedef alınmaz. → Faz 7'de baseline seti + anlamlılık
testi olarak somutlaştı (N12).

**N7 (Faz 3) — Falsifikasyon audit'i zorunludur.** Null veri üzerinde pipeline
testi; denenen model sayısı kayıt + çoklu-test farkındalığı. → Faz 7'de somut
protokole çevrildi (N12: blok-permütasyon null + pozitif kontrol + deneme günlüğü).

**N8 (Faz 3) — Rejim izleme dışsal olay-tabanlıdır.** Yüksek-frekanslı algoritmik
drift-detection aylık ufka AKTARILAMAZ. Latent HMM yerine dışsal-değişken tabanlı
rejim. → Faz 6'da öznitelik olarak modele girdi; Faz 7'de rejim-ayrık değerlendirme
protokolü oldu (N12).

**N9 (Faz 4) — Projenin novelty konumu belgelendi.** Kümüle ilan-fiyat endeksinin
zaman serisi YÖN sınıflaması hakemli literatürde YOKTUR (en yakın Bukvić vd. 2022
kesitsel). Devşirilebilir çekirdek: prediktif öznitelik seti, residual value
asimetrik-maliyet çerçevesi (→ sınıf-ağırlıklı kayıp), Kaggle veri-temizlik.
Kritik varsayım (N9+K8): ilan-yönü ↔ gerçekleşen-yön ilişkisi pazarlık marjı
rejime göre değişirse bozulur. Projenin en kritik test edilecek varsayımıdır.
→ Faz 8'de hakemli kanıtla riskli bulundu ve test tasarımı verildi (N13).

**N10 (Faz 5) — Kompozisyon düzeltmesi ve feature üretimi reçeteye bağlandı.**
(1) BİRİNCİL: aylık hedonik imputation (log-fiyat ~ N9 seti), yön etiketi
mix-düzeltilmiş Δα_t'den. (2) DOĞRULAMA: Manheim-tarzı sabit-ağırlık endeksi;
diverjans = mix kayması teşhisi. (3) FEATURE: hedonik reziduel ε. Makro lag
ampirik (CCF + Granger, eğitim-içi); kur 1/3/6/12 ay, kısa lag'ler öncelikli
hipotez. Çift leakage kısıtı: yalnızca-geçmiş + fold-dışı. Teknik göstergeler
soyutlama düzeyinde (momentum/oynaklık); RSI/MACD kopyalanmaz. → Faz 6, 7 girdisi.

**N11 (Faz 6) — Model baseline kararı.** Birincil baseline: segment kimliği +
dışsal rejim değişkenlerini (N8) öznitelik alan, **class-weighted tek global
gradient boosting** (küçük segment → CatBoost / sıkı-düzenlileştirilmiş XGBoost;
büyük veri → LightGBM). N4 sırası uygulanır; post-hoc kalibrasyon az-gözlemde
**Platt/temperature scaling** (izotonik DEĞİL — overfit riski). Başarı ölçütü
naif baseline üzeri MCC (N6).

İLERİ DENEMELER (her biri GBM baseline'ı geçme eşiğiyle — N6):
- Frank & Hall (2001) ordinal 2-ikili-model ayrıştırması; QWK/MCC'de nominal'i
  geçerse benimse. 3 sınıfta kazanç garanti değil (literatürde net değil).
- Focal loss veya ordinal-farkında kuadratik maliyet matrisi (N9 asimetrik
  maliyet; reversal > off-by-one cezası).
- Hiyerarşik / partial-pooling (segment az ve heterojense).
- Çok-küçük veride TabPFN; gözlem büyür + global/cross-learning kurulursa DL.

DEEP LEARNING BASELINE DEĞİLDİR. Saf segment-başı lokal modeller önerilmez
(az-gözlem gürültüsü). → Faz 7 ve Faz 8 esas alır.

**N12 (Faz 7) — Validasyon ve raporlama protokolü.** Bir deneyin "güvenilir"
ilan edilmesi için 24-maddelik kontrol listesi (Faz 7 Bölüm 9) bağlayıcı
güvenilirlik sözleşmesidir. Çekirdek kararlar:

- OMURGA: genişleyen-pencere walk-forward + 1 ay ufuk + 1-2 ay purge/embargo;
  test dönemi gözlem bütçesine göre 6-24. "50-100 fold" YASAK (her fold'a ~1
  gözlem düşer). Eşik: N<50 → yalnızca keşifsel/negatif-bulgu; N≥80 → tam
  protokol; N≥150 → CPCV opsiyonel.
- AS-OF DATE MİMARİSİ: Tek merkezî bilgi-kesim tarihi; kronoloji (N5) + makro
  vintage/yayın-gecikmesi (en kritik leakage riski) tek noktadan garanti.
  Vintage yoksa pseudo-real-time +1/+2 ay lag. Ön-işleme/encoding/feature-
  selection fold-İÇİNDE fit.
- METRİK: macro-MCC (Gorodkin R_K, micro-MCC değil) + macro-F1 + per-class
  P/R/support; hepsine blok-bootstrap %95 CI (B≥1000, blok ~n^(1/3), seed
  raporlu). Accuracy tanımlayıcı.
- BASELINE + ANLAMLILIK: persistence, mevsimsel-naif, hep-stable, prior-oran;
  yön-anlamlılığı bootstrap-PT (Pesaran-Timmermann 2009 ruhu; asimptotik PT
  N<75'te over-sized). Fark CI'ı sıfırı içeriyorsa → "sinyal yok" (N6, geçerli).
- FALSİFİKASYON (BLOKE EDİCİ GEÇİT): blok-permütasyon hedef-shuffle null
  (B≥1000, tam pipeline); null ortalaması ≈0 DEĞİLSE DUR — leakage var. Ayrıca
  sentetik-sinyal pozitif kontrolü + random-walk benchmark.
- ÇOKLU-TEST: deneme günlüğü (her run kaydı) + denenen N raporu + permütasyon
  max-istatistik / FDR düzeltmesi + MinBTL kontrolü. Nested CV yerine katı
  hiperparametre bütçesi + kilitli hold-out (az-gözlem gerçekçiliği).
- REJİM-FARKINDALIK: şok takvimi ÖNCEDEN sabit (veriden keşfetme); rejim-ayrık
  MCC (sakin vs şok-sonrası); dağılım-kayması (covariate/temporal vs concept
  drift) ayrıştırılır.

İşaretli çelişki: Bergmeir & Benítez (2012) belirli koşulda blocked-CV'yi
standart önerir; ancak durağanlık varsayar, bu problemde rejim değişimi
nedeniyle ihlal edilir → N5 korunur, blocked-CV yalnızca purge+embargo ile
ikincil/yardımcı tahmin olarak. Boşluk: "deflated MCC" standart formülü yok;
permütasyon max-istatistik null'u muadil olarak kullanılır.

→ Faz 8 protokolün kaçırabileceği riskleri avlar.

**N13 (Faz 8) — Kritik varsayım riski ve önceden-ilan-edilen terk kriterleri.**

K8+N9 varsayımı (ilan fiyatı yönü ↔ gerçekleşen fiyat yönü) emlak literatüründe
HAKEMLİ KANITLA RİSKLİDİR: pazarlık marjı (sale-to-list oranı) pro-döngüseldir —
yükselişte daralır, düşüşte genişler; sinyal döngü DÖNÜM NOKTALARINDA sistematik
sapar (Anenberg & Laufer 2017, REStat 99(4):722-734; Anenberg 2016; Han & Strange
2016; Carrillo vd. 2015). Araç piyasasına transfer güçlü analojidir ama doğrudan
ölçülmemiştir.

ZORUNLU DOLAYLI TEST: (a) DOM medyanı + fiyat-düşürme oranı + conversion oranı
proxy paneli (ilan-yön sinyaliyle ters hareket = sapma alarmı); (b) bağımsız
işlem-tabanlı serilerle (TÜİK, BETAM/sahibindex) periyodik yönsel-uyum ölçümü;
(c) rejim-koşullu tutarlılık testi (yükseliş/düşüş dilimleri). Proxy verisi
çeyreğin 1-2. ayından alınır (3. ay forward-looking gürültü ekler; Trojanek vd.
2025).

BEŞ YÜKSEK×YÜKSEK RİSK (registri #1,4,5,6,9): (1) K8 ilan-yönü sapması,
(4) gizli leakage, (5) naif baseline'ı yenememenin gizlenmesi, (6) çoklu-test
şişmesi, (9) kur/ÖTV/arz şokunda rejim çöküşü.

BEŞ ÖNCEDEN-İLAN-EDİLEN TERK/YENİDEN-ÇERÇEVELEME EŞİĞİ (bağlayıcı — biri
karşılanırsa proje mevcut haliyle sürdürülmez):
1. Model, dokunulmamış holdout'ta iki naif baseline'ı (persistence + çoğunluk)
   güven aralığı örtüşmeden yenemiyorsa → sinyal yok.
2. İlan-yön sinyalinin işlem serisiyle yönsel uyumu şans üstü DEĞİL veya
   rejimler arası kararsızsa → hedef geçersiz; yeniden-çerçevele.
3. Performans yalnızca tek rejimde pozitif, diğerlerinde baseline-altıysa →
   genellenebilir sinyal yok.
4. İstatistiksel edge işlem maliyeti/karar frictions altında pozitif fayda
   üretmiyorsa → karar-faydası yok.
5. Leakage düzeltmesi sonrası performans naif seviyeye düşüyorsa → önceki
   sonuçlar artefakttı; terk.

YENİDEN-ÇERÇEVELEME SEÇENEĞİ: hedefi işlem-vekili olmaktan çıkarıp doğrudan
ilan-davranışı (DOM/fiyat-düşürme) tahminine kaydırmak; "sinyal yok"u dürüst
negatif-sonuç raporu olarak yayımlamak (N6 ile tutarlı). → Sentez bunları
projenin risk ve karar çerçevesi olarak sunar.

## C. Yapısal Kararlar (Y)

**Y1:** Sentez dökümanı `docs/09_sentez_ve_karar_dokumani.md` olarak numaralı
seride tutulur. Sunum kaynak dosyaları `docs/sentez/` altında kalır.

**Y2:** Faz dökümanlarının metadata bloğu master plandaki genişletilmiş YAML
şemasıdır (bkz. `docs/standards.md`).

**Y3:** Faz dökümanlarının yapısı Faz 1'de oluşan genişletilmiş şablonu izler:
TL;DR → Key Findings → Details (faz-özel iskelet) → Recommendations → Caveats →
Kaynakça → Kullanılan Arama Sorguları. Kaynakça tek listedir; düşük kanıt gücü
taşıyan kaynaklar (sektör beyanı, basın, hakem-öncesi preprint, endüstri/hakemsiz)
giriş içinde işaretlenir.
