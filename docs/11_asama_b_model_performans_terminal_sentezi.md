---
faz_no: 11
faz_adi: "Aşama B Model Performans Terminal Sentezi"
tarih: 2026-08-09
kapsam_ozeti: "Model 14-17 performans iterasyonlarının ortak kanıtı, dondurulan aday ve bilimsel durdurma sınırı"
bagimli_oldugu_fazlar: [10]
bagimli_model_asamalari: [14, 15, 16, 17]
durum: inceleniyor
hedef_kaynak_sayisi: 4
gerceklesen_kaynak_sayisi: 4
kaynak_arac: "Claude Code (Rota-2 uygulama; Pusula Sonnet/xhigh kırmızı-takım)"
son_guncelleme: 2026-08-09
---

# Aşama B — Model Performans Terminal Sentezi

## Yönetici sonucu

Mevcut 50 test-dışı origin ve K9/K10 bilgi sözleşmesinde **üretime/teste terfi
eden model yoktur**. Model 14 L2 C=0,1, geliştirme için dondurulan en iyi dengeli
adaydır; bu bir terfi veya gerçek sinyal iddiası değildir.

Kilitli `2025-07..2026-06` test penceresi açılmamıştır ve validation kapısı
geçilmediği için açılmamalıdır.

## Ortak karşılaştırma

| Yaklaşım | MCC | Macro-F1 | Accuracy | Persistence'a ΔMCC | Terminal sorun |
|---|---:|---:|---:|---:|---|
| M−2 persistence | 0,0165 | 0,3642 | 0,380 | — | Referans |
| Model 14 L2 C=0,1 | **0,0886** | **0,3659** | 0,385 | **+0,0721** | Holm alt sınır <0 |
| Model 15 Frank–Hall | 0,0857 | 0,3316 | **0,455** | +0,0692 | Macro-F1 ve yıl kararlılığı |
| Model 16 nested hibrit | 0,0031 | 0,3136 | 0,340 | -0,0134 | Train-içi seçim dışa taşınmadı |
| Model 17 maliyet 0/1/4 | **0,0896** | 0,2725 | 0,310 | +0,0731 | MCC için macro-F1/accuracy feda edildi |

Model 14'te Δmacro-F1 yalnız `+0,0017`; eşli hareketli-blok/Holm alt sınırı
Model 14 ailesinde `-0,2020`, yedili birleşik ailede `-0,2116` düzeyindedir.
Ham tek-yönlü p `0,3608` olduğundan başarısızlık yalnız Holm cezası değildir.

### Projeye uygulanabilirlik

Model 14 artefaktı gelecekte bağımsız ay/vintaj geldiğinde **tek dondurulmuş
aday** olarak kullanılabilir. Şimdi test/deploy edilmez; Model 14 üzerinde yeni
C, feature alt-kümesi, threshold veya karar kuralı seçilmez.

## Neden daha fazla algoritma durduruldu

1. Aynı 50 bağımsız ay Model 10'dan beri tekrar tekrar geliştirme yüzeyi oldu.
2. Prompt 43–46 sonuçtan önce kilitlense de yerel hipotez ailesi yedi adaya
   ulaştı; yeni aday aynı yüzeyde araştırmacı serbestlik derecesini artırır.
3. Üç farklı performans müdahalesi — ordinal eğitim, nested ensemble, asimetrik
   karar maliyeti — Model 14'ü iki birincil metrkte birlikte geçemedi.
4. Model 11 bilgi-tavanı ve Model 12/13 BDDK denemeleri, algoritmadan önce bilgi
   sınırlamasına işaret etmişti. Model 14'ün küçük nokta iyileşmesi bu terminal
   kanıtı tersine çevirecek belirsizlik gücüne sahip değildir.
5. Validation'da yeni feature/threshold aramak, performans artırmaktan çok
   validation madenciliği riskini artıracaktır.

Bu durdurma “hiçbir model çalışmaz” hükmü değildir. Şu veri-vintaj-hedef
sözleşmesinde başka bir algoritma denemesinin savunulabilir olmadığını söyler.

## Performansı gerçekten artırabilecek eksenler

### 1. Yeni revizyona-kapalı / ilk-yayım bilgi

En yüksek beklenen değerli eksendir; fakat Prompt 42'de kamuya açık temiz aday
bulunamamıştır. İleriye dönük gölge vintaj arşivi yeni çalışma türüdür ve
kullanıcı kararı gerektirir.

### 2. Yeni bağımsız aylar

İstatistiksel belirsizliği doğrudan azaltır. Kilitli test bu amaçla development
verisine çevrilemez. `2026-06` sonrasındaki yeni aylar biriktikçe, önceden
dondurulmuş Model 14 bağımsız bir pencerede değerlendirilebilir; birkaç ay tek
başına yeterli değildir.

### 3. Hedef/ufuk/sınıf sözleşmesi

Ufuk, toplulaştırma veya sınıf yapısı değişikliği bağlayıcı K/N kararıdır ve
kullanıcı olmadan başlatılamaz. Model 17'nin MCC–macro-F1 takası, yalnız karar
kuralıyla bu sorunun çözülemediğini gösterir.

### Projeye uygulanabilirlik

Bir sonraki model commit'i, yukarıdaki üç eksenden birinde yeni bağımsız bilgi
oluşmadan açılmamalıdır. Algoritma seçimi sonraki adımdır, ilk adım değil.

## Dondurulan aday sözleşmesi

- Aday: Model 14 `lojistik_l2_c01`.
- Feature: Prompt 43'teki sabit 14 feature.
- Ortam: `.venv312`, Python 3.12.7, sklearn 1.7.2, NumPy 2.3.5, pandas 2.3.3.
- Değerlendirme sonucu: MCC 0,088595; macro-F1 0,365891; accuracy 0,385.
- Referans: M−2 persistence.
- Statü: `DONDURULDU_GELISTIRME_ADAYI_TERFI_DEGIL`.
- Yasak: kilitli test, post-hoc C/feature/threshold/maliyet değişikliği.

## Açık kullanıcı kararları

1. İleriye dönük gölge vintaj arşivi başlatılsın mı?
2. Yeni bağımsız aylar birikene kadar Model 14 dondurulup beklenilsin mi?
3. Ufuk/toplulaştırma/sınıf sözleşmesi yeniden tasarlansın mı?

Varsayılan güvenli durum: Model 14 dondurulur, kilitli test kapalı kalır ve yeni
bağlayıcı karar gelene kadar başka model çalıştırılmaz.

## Kalite kontrol

- [x] Model 14–17 ön-kayıtları sonuçlardan önce commit edildi.
- [x] Her deney 50 origin / iki ay embargo / 2.000 blok bootstrap kullandı.
- [x] `.venv312` canlı referansları yeniden üretildi.
- [x] Tracked test paketi Model 17 sonunda 131/131 geçti.
- [x] Kilitli test açılmadı.
- [x] Negatif sonuçlar ve ortam sorunu saklanmadı.
- [ ] Proje sahibi terminal sentezi gözden geçirdi.

## Kaynakça / Denetim izi

- `pm_rapor_model14_mevcut_asof_feature_genisletme.md`
- `pm_rapor_model15_frank_hall_ordinal.md`
- `pm_rapor_model16_nested_persistence_lojistik_hibrit.md`
- `pm_rapor_model17_asimetrik_ordinal_maliyet.md`
