# Claude Uygulama Promptu — Günlük Hacim Yönü, Üç Sınıf

Bu görevde uygulayıcı ve PM raporu yazarı Claude Code'dur; Codex denetmen ve
karar/onay merciidir. Yalnız `denetim/hacim-yon-baseline` branch'inde çalış.
`main` branch'ine geçme, merge etme, commit veya push yapma.

## Bağlayıcı proje çerçevesi

- Somut target `noter_devir_otomobil_adet` sütunudur: gelecek dönemde el
  değiştiren ikinci el otomobil hacmi.
- Ana görev doğrudan üç sınıflı tahmindir: `up / stable / down` (ürün dilinde
  hızlanıyor / stabil / yavaşlıyor).
- Veri günlük frekansta kalacaktır. Aylık satırlara aggregate etme.
- Günlük tablolar ay-hizalı doldurma yöntemiyle hazırlanmıştır; bu işlemi
  forward-fill olarak adlandırma ve yeni global `ffill`/`bfill` uygulama.
- Ana stable eşiği ±%5'tir: tam +%5 ve -%5 `stable`; ±%3 ve ±%10 yalnız
  duyarlılık analizidir.
- Ürün çıktısı `p_down`, `p_stable`, `p_up`, seçilen sınıf ve maksimum olasılık
  tabanlı güven değerini içermelidir. Kalibre edilmemiş olasılıklar açıkça
  `raw` olarak adlandırılır.
- DF-A 2015-bugün geniş/dar-özellikli; DF-B 2024-bugün dar/zengin-özellikli
  paralel veri seti yaklaşımı korunur.
- Mevcut AutoGluon TimeSeries seviye tahminleri karşılaştırma baseline'ıdır.
  Doğrudan multiclass ana model için AutoGluon
  `TabularPredictor(problem_type="multiclass")` kullan.

## Önce düzeltilecek yarım çalışma

Önceki Claude çağrılarında yanlış fiyat target'ıyla oluşturulan şu iki dosyayı
kaldır:

- `scripts/model/model_06_ilan_fiyati_yon_hedef_deneyimi.py`
- `data/processed/raporlar/pm_rapor_ilan_fiyati_yon_hedef_protokolu.md`

`scripts/model/yon_degerlendirme.py` ve `tests/` içeriğini target-bağımsız yön
değerlendirme altyapısı olarak düzelt ve kullan. Mevcut yarım modüldeki
`OynaklikEsigi`, `gecmise_dayali_esik`, `expanding_yon_serisi` ve bunlara ait
K2/sigma testlerini kaldır; bunlar eski fiyat-target varsayımıdır ve aktif
hacim label tanımıyla çelişir. Yerine açık sabit yüzde eşikli
`yon_etiketi(yuzde_degisim, esik_yuzde=5.0)` saf fonksiyonunu koy; tam eşik
değerleri stable olmalıdır. MCC/macro-F1/per-class/confusion fonksiyonlarını
koru ve olasılık doğrulaması/split yardımcılarını ekle. `prompts/veri/27_*.md` yarım
fiyat promptunu kaldır; bu dosya görev arşividir.

`docs/00_karar_kaydi.md` içinde orijinal K8'i tarihsel karar olarak koru. Yarım
fiyat ekini düzelt ve yeni K9 ile aktif Aşama B kararını kaydet: target noter
devir otomobil adedi, günlük frekans, doğrudan üç sınıf ve olasılık/güven
çıktısı; gerekçe veri yeterliliği ve daha dengeli dağılım; sinyal fiyatlama
kararlarına girdidir ama doğrudan fiyat tahmini değildir. README Aşama B'yi
aynı doğrultuda güncelle; Aşama A checkbox'larına dokunma.

`CLAUDE.md` dosyasını da minimal ve gerekçeli biçimde güncelle: Aşama A'nın
fiyat-yön literatürü tarihsel referans olarak korunurken Aşama B'nin aktif
operasyonel target'ının günlük `noter_devir_otomobil_adet` üç-sınıf yönü
olduğunu yaz. Çalışma rolü hiyerarşisini kaydet: Codex denetmen ve karar/onay
merciidir; Claude Code "Kodcu" olarak onaylanan uygulama ve PM raporlarından,
Perplexity "Araştırmacı" olarak dış araştırmadan sorumludur; Codex onayından
geçmeyen yeni bağlayıcı karar uygulanmaz.

## Veri, etiket ve validasyon

1. `scripts/model/model_06_hacim_yon_siniflandirma.py` oluştur.
2. Her günlük satırın etiketi, bulunduğu referans ayın noter hacmi ile bir
   sonraki takvim ayının noter hacmi karşılaştırılarak oluşturulsun. Günlük
   satırlar korunur; son ay labelsız kalır.
3. Güncel/gelecek target ve target'tan türetilmiş sızıntılı sütunları
   feature'lardan çıkar. Geçmiş hacim bilgisi gerekiyorsa yalnız ay-takvimli
   lag1/2/3/12 üret. Ay-hizalı ham tabloyu değiştirme; fakat gerçek yayım
   gecikmesini model katmanında koru: günlük `usdtry_orta` kendi gününde
   kullanılabilir, aylık eşzamanlı covariate'ları en az bir takvim ayı
   gecikmeli feature'a dönüştür. Adında zaten `lag4ay`, `lag5ay`, `lag12ay`
   gibi açık gecikme bulunan sütunlara ikinci kez lag uygulama. Kullanılan her
   feature için ham sütun, uygulanan lag ve gerekçe listesini JSON'a yaz.
   Global `bfill` veya yeni `ffill` kullanma.
4. Aynı ayın günlerini farklı split'lere koyma. Kaynak ayına göre kronolojik
   train/validation/test kur; etiket t+1 kullandığından sınırlar arasında en az
   bir aylık purge bırak. Denetmen tarafından doğrulanan sabit splitleri kullan:
   DF-A train 2018-01..2024-03 (75 ay), purge 2024-04, validation
   2024-05..2025-04 (12 ay), purge 2025-05, test 2025-06..2026-05 (12 ay);
   DF-B train 2024-01..2025-03 (15 ay), purge 2025-04, validation
   2025-05..2025-10 (6 ay), purge 2025-11, test 2025-12..2026-05 (6 ay).
   Her splitte günlük satır sayısının yanında bağımsız target ayı sayısını da
   raporla. DF-B'nin 15 bağımsız eğitim ayı nedeniyle yalnız keşifsel olduğunu
   açıkça belirt.
5. Günlük frekans korunurken ayların ağırlığını eşitlemek için her satıra
   `1 / o aydaki gün sayısı` ağırlığı ver; AutoGluon eğitim ve değerlendirmede
   bunu kullan.
6. `.venv312` Python ile DF-A ve DF-B için ayrı AutoGluon Tabular modelleri
   eğit. Hızlı gerçek baseline kullan; en fazla 300 saniye/set ve tek deneme.
   Hata olursa saklama ve ağır tekrar yapma.
7. Testte global/Gorodkin R_K MCC (`sklearn.matthews_corrcoef`) ve macro-F1
   birincil; accuracy ikincil; per-class precision/recall/support ve sabit
   `down/stable/up` confusion matrix zorunlu. Majority ve kronolojik
   persistence baseline'larını aynı ortak örneklemde hesapla. Hacimdeki güçlü
   mevsimsellik nedeniyle ayrıca `yön(t-12 ay)` mevsimsel-yön baseline'ını
   zorunlu hesapla. Denetmen ön hesabında sabit test splitlerinde DF-A
   mevsimsel baseline MCC=0.3936, macro-F1=0.5794, accuracy=0.5833; DF-B
   MCC=0.0000, macro-F1=0.3000, accuracy=0.3333 bulundu. Kodun sonucu
   uyuşmazsa sessizce ilerleme; tanım/örneklem farkını araştır ve raporla.
8. Günlük metriklerin yanında her ayın son günlük tahmininden ay-bazlı metrik
   üret. Bu değerlendirme günlük veri frekansını değiştirmez.
9. `predict_proba` çıktısını küçük deterministik CSV/JSON olarak
   `data/processed/model/` altında sakla. Güvenilir multiclass calibration için
   validation yetersizse olasılıkları kalibre edilmiş diye sunma.
10. Test çıktısından ayrı bir ileri-sinyal artefaktı üret: her veri setinde son
    dolu `noter_devir_otomobil_adet` referans ayını dinamik bul, o ayın son
    günlük satırından bir sonraki takvim ayı için `p_down/p_stable/p_up`, tahmin
    sınıfı ve `raw_confidence` yaz. Gelecek gerçekleşmesi bulunmuyorsa bunu
    performans/test sonucu gibi sunma; `gerceklesme_bekleniyor` durumuyla
    işaretle. DF-A/DF-B sinyalleri ayrışırsa ikisini de sakla, keyfî birini seçme.

## Test, rapor ve sınırlar

Pytest testleri en az şunları kapsasın: ±%5 sınırlarının stable olması, gelecek
takvim ayı eşlemesi, split aylarının çakışmaması ve purge, ay ağırlıklarının
eşit toplamı, geçersiz etiket reddi, mükemmel/hep-stable metrik ve olasılık
toplamı.

`data/processed/raporlar/pm_rapor_hacim_yon_3sinif_baseline.md` dosyasında
AGENTS.md'deki yedi başlığı eksiksiz kullan. Günlük ay-hizalı tekrarların
pseudo-replikasyon riskini, DF-B küçük örneklemini, olasılık kalibrasyon
durumunu, leakage önlemlerini ve naif baseline karşılaştırmasını saklama.
"Sinyal yok" geçerli sonuçtur. Sonraki adımı yalnız öner.

Denetmen fizibilite kontrolündeki ±%5 sınıf dağılımları DF-A için 101 etiket
ayında `40 up / 35 down / 26 stable`, DF-B için 29 etiket ayında
`11 up / 9 down / 9 stable` olarak bulunmuştur. Kod çıktısı bunlarla uyuşmazsa
sessizce ilerleme; uyuşmazlığı hata olarak raporla. DF-A'da yalnız `usdtry_orta`
ay içinde değişirken DF-B feature'larının tamamının ay içinde sabit olduğu
gerçeğini pseudo-replikasyon/etkin örneklem uyarısında belirt.

Dokunma: `notebooks/*.ipynb`, `AGENTS.md`, `urls_out.txt`, mevcut
`scripts/model/model_03_geriye_donuk_test.py`, `model_04_yon_dogrulugu.py` ve
`model_05_feature_importance.py`.

Script ve testleri çalıştır. Bitince aktif branch'i, git status/diff özetini,
testleri, eğitim sürelerini, DF-A/DF-B günlük ve ay-bazlı metrikleri ve olasılık
kalibrasyon durumunu Türkçe bildir. Commit/push yapma; Codex inceleyecek.
