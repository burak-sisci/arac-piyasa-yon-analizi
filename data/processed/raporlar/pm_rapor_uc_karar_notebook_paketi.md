# PM Raporu — Üç Karar Notebooku Paketi

**Tarih:** 2026-08-07

**Aşama:** Model 11 sonrası karar desteği

**Durum:** Tamamlandı; yeni deney başlatılmadı

**Karar yöneticisi/ortak yazar:** Pusula

**Uygulayıcı/ortak yazar:** Rota

## 1. Ne Yapıldı

Model 11 kapanışında açık bırakılan üç stratejik seçenek için ayrı, çalışır ve
öğretici karar notebookları üretildi:

1. `notebooks/karar_lab_01_hedefi_kapat.ipynb`
   - Model 09→10→11 kanıt zincirini kapatma merceğiyle birleştirir.
   - “Etki yok” ile “kullanılabilir beceri gösterilemedi” ayrımını zorunlu
     kılar.
   - Model 10 MCC/CI grafiği, Model 11 oracle-null tablosu ve yeniden açma
     koşulunu içerir.
2. `notebooks/karar_lab_02_bilgi_kumesi_genislet.ipynb`
   - Target ve up/stable/down sınıflarını sabit tutar.
   - Model 09'un on feature'ını bilgi ailelerine ayırır; temsil boşluklarını
     görünür kılar.
   - Aday veri kartı, as-of/yayın gecikmesi kapısı ve oracle null95+0,15 tavan
     standardını bir arama şartnamesi olarak sabitler.
3. `notebooks/karar_lab_03_ufuk_sinif_degisikligi.ipynb`
   - Stable-band değişimi, ufuk, toplulaştırma ve sınıf sayısını birbirinden
     ayırır.
   - Model 11 band/lag sonuçlarını yeniden çizer.
   - 76 aylık analiz penceresi için örtüşmesiz/hareketli toplulaştırmanın ham
     birim üst sınırlarını hesaplar; hiçbir yeni performans metriği üretmez.

Üç notebookta aynı 0-3 karar puanlama şeması ve doldurulabilir gerekçe tablosu
yer alır. Şema otomatik kazanan üretmez. Her notebook canlı yerel çıktı varsa
Model 09-11 JSON'larını okur; dosya yoksa yalnız resmî raporlarda sabitlenmiş
çekirdek sayıları açıkça etiketlenen fallback sözlüğünden kullanır.

### Pusula ile ortak çalışma

- Aynı kalıcı Pusula session'ı kullanıldı:
  `6f4c6fd0-6ddb-4b70-8e45-86d5b6d124c1`.
- Kullanıcının `/model-sonnet /effort-extra` talebi, Claude Code CLI'ın
  desteklediği teknik karşılık olan `--model sonnet --effort xhigh` ile
  yürütüldü. `extra` CLI'da geçerli bir değer değildir.
- İlk çağrı 120 saniyede terminal zaman aşımına uğradı ve karar teslim etmedi.
  Aynı session ikinci kez, daha uzun timeout ile devam ettirildi.
- Pusula önerilen iş bölümünü **KABUL** etti ve veto bildirmedi.
- Pusula anlatı/karar iskeletini; Rota kod, montaj, execution ve QA'yı yaptı.
- Pusula, tamamlanmış üç `.ipynb` dosyasını ve bu PM raporunu dosya bazında
  yeniden denetledi; sonuç **COMMIT KABUL**, veto yoktur. Üç kritik olmayan
  notundan kapatma kapısındaki B/D açıklaması ve commit zamanlaması metni aynı
  paket içinde netleştirildi.

### Git görünürlüğü değişikliği

Bu görev döngüsünün notebook yazımından önceki ilk adımında, kullanıcı
talebiyle `CLAUDE.md` `.gitignore` içine alındı ve dosya diskte korunarak Git
indeksinden çıkarıldı. Değişiklik bağımsız `a130fc6` commit'iyle geliştirme
branch'ine push edildi. Kullanıcıya ait diğer dirty/untracked dosyalar bu
commit'e veya notebook paketine alınmadı.

## 2. Sayısal Özet

### Üretilen artefaktlar

- Yeni notebook: **3**
- Toplam karar seçeneği: **3**
- Ortak puan ekseni: **4** (kanıt, maliyet/tersinirlik, belirsizlik azaltımı,
  kapsam sadakati)
- Puan aralığı: eksen başına **0-3**, toplam **0-12**
- Yeni model fit: **0**
- Yeni veri kaynağı/çekimi: **0**
- Yeni bootstrap/permutasyon: **0**
- Kilitli test erişimi: **0**
- Notebook execution hatası: **0**

### Notebooklarda yeniden kullanılan resmî kanıt

- Model 09 en iyi baseline: M-2 persistence, MCC `0,110`, macro-F1 `0,415`.
- Model 09 en iyi aday: sığ Random Forest, MCC `0,037`, macro-F1 `0,189`.
- Model 10: `50` origin, `2` ay embargo, `2.000` hareketli blok bootstrap.
- Model 10 persistence: MCC `0,0165`, %95 GA `[-0,1464; 0,2344]`.
- Model 10 ΔMCC çözünürlük yarı genişliği: yaklaşık `0,21-0,28`.
- Model 11 lag-1: MCC `-0,0204`, %95 GA `[-0,2615; 0,1542]`.
- Model 11 geçiş bağımsızlığı: Cramér's V `0,0981`, permütasyon p `0,8450`.
- Stable band sayısı: `5`; `maddi_farkli=True` olan bant sayısı: `0`.
- Oracle-B aday sayısı: `4`; null95 üzerine `≥0,15` marj koyan: `0`.
- Analiz penceresi: `2019-01..2025-04`, `76` ay.
- Örtüşmesiz 3 aylık ham birim iyimser üst sınırı: `25`; eğitim/embargo henüz
  düşülmemiştir ve performans origin sayısı değildir.

## 3. Karşılaşılan Sorunlar (Saklanmaz)

1. **Effort adlandırması:** Claude CLI `extra` kabul etmiyor; geçerli değerler
   `low/medium/high/xhigh/max`. Kullanıcı niyetine en yakın `xhigh` kullanıldı.
2. **İlk Pusula timeout'u:** İlk Sonnet/xhigh çağrısı `124` saniyede exit 124
   ile kapandı; içerik teslim edilmedi. Aynı session devam ettirilerek ikinci
   çağrıda sonuç alındı. Yeni session açılmadı.
3. **Pusula taslağında iç çelişki:** Üçüncü notebook için keşifsel 3→2 MCC
   hücresi önerilmişti; aynı yanıtta “yeni performans ölçümü yasak” denmişti.
   Rota metrik hücresini çıkardı. Bu bir yön değişikliği değil, ortak üst
   sınırın uygulanmasıdır.
4. **`nbformat` doğrulama çağrısı:** `python -m nbformat` giriş noktası olmadığı
   için üç kez uyarı verdi. Ardından `jupyter nbconvert --execute --inplace`
   üç notebooku başarıyla okuyup çalıştırdı. Ayrıca ayrı Python API doğrulaması
   yapılacaktır; ilk uyarı notebook hatası değildir.
5. **Yerel çıktı bağımlılığı:** `data/processed/model/*.json` dosyaları yerelde
   mevcut olsa da veri/çıktı politikası nedeniyle her klonda bulunmayabilir.
   Bu yüzden açık kaynak etiketi veren fallback eklendi. Fallback yeni veya
   tahmini sayı içermez; yalnız PM raporlarındaki sabit çekirdek kanıttır.
6. **Mevcut notebook alanı tanımı:** `notebooks/README.md` klasörü eskiden yalnız
   proje sahibinin ad-hoc alanı olarak tanımlıyordu. Kullanıcının yeni kalıcı
   notebook kuralıyla çelişmemesi için üç karar laboratuvarı “yönetilen karar
   notebooku” istisnası olarak indekslendi. Kullanıcının mevcut iki ders kitabı
   notebookuna dokunulmadı.

## 4. Veri Örneği (Ham, İlk/Son Birkaç Satır)

Bu aşama yeni ham veri üretmedi. Aşağıdaki kayıtlar notebookların okuduğu
mevcut JSON çıktılarından değiştirilmeden seçilmiş denetim örnekleridir.

### Model 10 — metrik sözlüğünün ilk iki yöntemi

```text
train_cogunlugu      mcc=-0.06999699192944449  CI=[-0.29650844540586285, 0.12373189648352916]
persistence_m_eksi_2 mcc= 0.01650809955170020  CI=[-0.14638013212604967, 0.23438572750062464]
```

### Model 10 — metrik sözlüğünün son iki yöntemi

```text
random_forest_sigin mcc=-0.11927260430047538  CI=[-0.24282294372143237, 0.08635642971477196]
hist_gradient_sigin mcc=-0.10967316583521465  CI=[-0.27285509272934840, 0.10086722243838679]
```

### Model 11 — stable band ilk/son kayıt

```text
2.5:  down=0.4342105263 stable=0.0657894737 up=0.5000000000 persistence_mcc= 0.0099080592 maddi_farkli=false
10.0: down=0.3026315789 stable=0.3815789474 up=0.3157894737 persistence_mcc=-0.0996333263 maddi_farkli=false
```

### Kaynak sınırı

Notebooklar yalnız `model_09_dusuk_kapasiteli_nowcast_validation.json`,
`model_10_rolling_origin_ozet.json` ve `model_11_hedef_teshis_ozet.json`
dosyalarını okur. Kilitli test dönemindeki ham hedef satırlarını veya tahminleri
okuyan hiçbir hücre yoktur.

## 5. Varsayımlar ve Kararlar (K/N Kararlarına Uygunluk)

- Target sütunu hiçbir notebookta değiştirilmedi:
  `noter_devir_otomobil_adet`.
- Seçenek 1 ve 2 mevcut üç sınıflı hedefi aynen korur.
- Seçenek 3 yalnız alternatif sözleşmeleri açıklar; sınıf/ufuk değişikliği
  uygulamaz ve performans üretmez.
- Haftalık güncellenen aylık nowcast mevcut sözleşme olarak korunmuştur.
- M−2 bilgi kesimi ve iki aylık embargo mevcut sonuçların yorumunda korunur.
- Kilitli test (`2025-07..2026-06`) açılmamıştır.
- ±%10 seasonal MCC `0,158` post-hoc bulgu olarak uyarı metninde tutulur;
  karar veya terfi kanıtı yapılmaz.
- Oracle yüksek in-sample skorları beceri olarak sunulmaz; yalnız kendi
  permütasyon null95 değerleriyle gösterilir.
- Ortak puanlama tablosu boş bırakılır; kullanıcı adına otomatik tercih veya
  nihai kazanan yazılmaz.
- Üç notebookun üretimi yeni bir modelleme/veri toplama aşaması değildir;
  Model 11 sonrası karar desteği ve dokümantasyon aşamasıdır.

## 6. Açık Sorular / PM Onayı Gerekenler

Bu rapor onay beklemeden tamamlanmıştır; fakat seçeneklerin uygulanması için
aşağıdaki bağlayıcı kararlar hâlâ açıktır:

1. Mevcut hedef sözleşmesiyle hattın kapatılıp kapatılmayacağı.
2. Target ve üç sınıf korunacaksa hangi öncü bilgi ailesine erişim sağlanacağı;
   kaynak sahipliği, maliyet ve as-of geçmişi henüz doğrulanmamıştır.
3. Ufuk/toplulaştırma/sınıf sayısı değişecekse aynı anda hangi **tek** eksenin
   değişeceği ve yeni iş anlamı.
4. İki sınıfa geçiş düşünülürse stable gözlemlerinin dışlanması, abstain olarak
   korunması veya başka bir operasyonel katmana taşınması.
5. Yeni hedef sözleşmesinin minimum origin, embargo ve terfi eşiği.

Pusula bu pakette nihai seçenek seçmemiştir. Karar kapıları hazırlanmış,
uygulama başlatılmamıştır.

## 7. Önerilen Sonraki Adım (Başlatılmaz, Yalnızca Önerilir)

Proje sahibi üç notebooku aynı ortak puanlama tablosuyla değerlendirir ve tek
bir seçenek için bağlayıcı karar verir. Seçenek 2 seçilirse önce veri çekmek
yerine bir aday kartı tam doldurulmalı; as-of/yayın gecikmesi ve erişim
kanıtlanmalıdır. Seçenek 3 seçilirse önce hedef sözleşmesi ve origin
fizibilitesi ön-kayıt altına alınmalıdır. Seçenek 1 seçilirse kapanış kararı
yalnız mevcut temsil/ufuk/gecikme kapsamıyla yazılmalı ve yeniden açma koşulu
korunmalıdır.

Bu raporun parçası olarak hiçbir sonraki seçenek uygulanmamıştır.
