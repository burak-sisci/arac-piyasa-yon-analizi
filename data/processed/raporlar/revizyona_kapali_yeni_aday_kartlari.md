# Revizyona Kapalı Yeni Öncü Aday Kartları

**Tarih:** 2026-08-08

**Önkayıt:** Prompt 42, commit `26a692b`

**Kapsam:** En fazla üç yeni aday; yalnız kamuya açık dokümantasyon/yayın sayfası

**Hüküm:** **BU_TURDA_UYGUN_ADAY_YOK**

## Sonuç özeti

| Aday | Gerçek boşluk | Revizyona kapalı mı? | Ön hüküm | Bağımsız düşme nedenleri |
|---|---|---|---|---|
| TCMB haftalık kart işlem adedi — kategori 02 | Fiyat pazarlığı ve satışa dönüşüm için ödeme/işlem vekili | Hayır | Elendi | Geçici/revizyona tabi; kartlı ödeme araç satışını temsil etmiyor; satış servis/parça/kiralama ile karışık |
| SBM trafik sigortası yazılan poliçe adedi | Satışa dönüşüm için poliçe-olayı vekili | Doğrulanmadı; aktif mutable | Elendi | Kamu kapsamı 2024–2026; iptal/zeyil güncellemeleri; yenileme ve satış karışık |
| TÜİK NACE 45 Ticaret Satış Hacim Endeksi | Gerçekleşmiş motorlu-taşıt ticareti vekili | Hayır | Elendi | Resmî revizyon geçmişi; hedef geçmişinin kaba/kirli kopyası; eşzamanlı ve geniş kapsamlı |

Hiçbir kart gerçek veri erişimine taşınmamıştır. TCMB operasyonel olarak en
zamanlı karttır; ekonomik olarak “en güçlü” ilan edilmemiştir.

## Aday kartı 1 — TCMB haftalık kart işlem adedi, kategori 02

| Alan | Kayıt |
|---|---|
| `aday_adi` | Banka ve kredi kartı işlem adedi — `02 ARAÇ KİRALAMA-SATIŞ/SERVİS/YEDEK PARÇA` |
| `kaynak_sahibi` | Türkiye Cumhuriyet Merkez Bankası; raporlayan bankalar |
| `ham_frekans` | Haftalık akım |
| `ilk_tarih` | Mart 2014 |
| `yayin_gecikmesi_gun` | Referans dönemi sonundan 4 iş günü; her Perşembe 14.30 |
| `M_eksi_2_aninda_erisim` | Evet, yayın takvimi düzeyinde |
| `revizyon_politikasi` | Her hafta geçici yayımlanır ve revizyona tabidir; büyüklük/yakınsama sınırı belgelenmedi |
| `revizyona_kapali_mi` | **Hayır** |
| `kapatilan_bilgi_boslugu` | Fiyat pazarlığı ve satışa dönüşüm için gerçekleşmiş ödeme/işlem vekili olma adayı |
| `mekanizma_bir_cumle` | İkinci el bayilerindeki kartlı işlem adedi, işlemin ödeme aşamasına gelmiş kısmını noter devrinden önce veya ona yakın zamanda kısmen yansıtabilir. |
| `mevcut_featuredan_neden_farkli` | Kur/faiz/makro koşulu değil, POS üzerinden gerçekleşmiş sektörel işlem sayısıdır. |
| `hukuki/erişim_riski` | Toplulaştırılmış resmî istatistik ve herkese eşzamanlı açık; bu aşamada veri/API kullanılmadı. |
| `as_of_vintage_riski` | **Yüksek.** Geçici/revizyona tabi seri; ilk-yayım arşivi bu aşamada doğrulanmadı. |
| `on_hukum` | **Elendi.** Revizyona-kapalılık kapısını kaybetti. Ayrıca kategori; yeni ve ikinci el satışla servis, tamir, parça ve kiralamayı birleştirir. Araç alımının kart dışı havale/kredi kısmını kapsamaz; bu nedenle mekanizma satış dönüşümüne temiz bağlanmaz. |

Kaynaklar:

- TCMB, [Banka ve Kredi Kartı Sektörel Harcama İstatistikleri](https://www.tcmb.gov.tr/wps/wcm/connect/TR/TCMB%2BTR/Main%2BMenu/Istatistikler/Parasal%2Bve%2BFinansal%2BIstatistikler/Banka%2Bve%2BKredi%2BKarti%2BSektorel%2BHarcama%2BIstatistikleri/).
- TCMB, [Banka Kartı ve Kredi Kartı İşlem Adedi Metaverisi](https://www.tcmb.gov.tr/wps/wcm/connect/7c2e67d5-da93-4ee5-afc7-55c64aebc3c0/Metaveri_Banka%2BKart%C4%B1%2Bve%2BKredi%2BKart%C4%B1%2B%C4%B0%C5%9Flem%2BAdedi.pdf?MOD=AJPERES): haftalık akım, Mart 2014 başlangıcı, dört iş günü gecikme ve geçici/revizyona tabi yayın.
- TCMB, [Sektör Kategorileri](https://www.tcmb.gov.tr/wps/wcm/connect/c200acd7-9f50-465b-b79a-168b8c574ea6/Sekt%C3%B6r%2BKategorileri.pdf?MOD=AJPERES): kategori 02'nin satış/servis/parça/kiralama bileşimi.
- TCMB, [Revizyon Politikası](https://www.tcmb.gov.tr/wps/wcm/connect/e7a846dc-fc8b-4c27-a0f8-2a2c7e6c86a3/Revizyon%2BPolitikas%C4%B1.pdf?MOD=AJPERES).

### Gelecekte en ucuz keşfedilmemiş kontrol

Kullanıcı ileride açıkça isterse, ilk küçük soru revizyonların kaç yayında
yakınsadığını ve büyüklüğünü yalnız dokümantasyon/ilk-yayım arşivi üzerinden
sınamaktır. Olumlu sonuç mekanizma uyuşmazlığını tek başına gidermez; bu turda
başlatılmamıştır.

## Aday kartı 2 — SBM trafik sigortası yazılan poliçe adedi

| Alan | Kayıt |
|---|---|
| `aday_adi` | Trafik sigortası yazılan poliçe adedi ve aylık değişimi |
| `kaynak_sahibi` | Sigorta Bilgi ve Gözetim Merkezi (SBM) |
| `ham_frekans` | Kamu sayfasında aylık/kümülatif takvim-yılı raporları |
| `ilk_tarih` | Kamu sayfasındaki mevcut kapsam 2024–2026; daha eski karşılaştırılabilir dizi doğrulanmadı |
| `yayin_gecikmesi_gun` | Doğrulanmadı |
| `M_eksi_2_aninda_erisim` | Güncel rapor için muhtemel; tarihsel as-of dizi için doğrulanmadı |
| `revizyon_politikasi` | Ayrı politika doğrulanmadı; yazılan adet üretimden başlangıçtan iptalleri düşer, zeyil/poliçe başlangıç tarihine göre hesaplanır ve merkezî veri tabanı güncellenir |
| `revizyona_kapali_mi` | **Doğrulanmadı; aktif mutable kayıt yapısı ilk-yayım=nihai eşitliğini desteklemiyor** |
| `kapatilan_bilgi_boslugu` | Satışa dönüşüm için zorunlu sigorta poliçe-olayı vekili |
| `mekanizma_bir_cumle` | Araç sahipliği başlangıcına yakın trafik poliçesi üretimi, yeni kayıt veya mülkiyet değişiminin bir bölümünü yansıtabilir. |
| `mevcut_featuredan_neden_farkli` | Fiyat/makro değil, sigorta sözleşmesi olayıdır. |
| `hukuki/erişim_riski` | Kamu özetleri açık; ayrıntılı iş zekâsı portalı yetkili kullanıcılarla sınırlı. |
| `as_of_vintage_riski` | **Çok yüksek.** İptal/zeyil ve sürekli güncellenen kayıtlar; tarihli ilk-yayım dizisi doğrulanmadı. |
| `on_hukum` | **Elendi.** 2024–2026 kamu kapsamı N<50'dir; 50 origin ve 52-gözlem geri bakışı karşılamaz. Poliçe yenilemeleri satışlarla karışır ve ilk-yayım değerinin değişmezliği kurulamaz. |

Kaynak:

- SBM, [Trafik Sigortası Raporları](https://sbm.org.tr/tr/trafik-sigortasi-raporlari): yazılan poliçe/prim tanımı, iptal/zeyil mekaniği ve 2024–2026 kamu kapsamı.

## Aday kartı 3 — TÜİK NACE 45 Ticaret Satış Hacim Endeksi

| Alan | Kayıt |
|---|---|
| `aday_adi` | Motorlu kara taşıtları ve motosikletlerin toptan/perakende ticareti ve onarımı satış hacim endeksi (NACE 45) |
| `kaynak_sahibi` | Türkiye İstatistik Kurumu; KDV beyannamesi veren girişimler |
| `ham_frekans` | Aylık |
| `ilk_tarih` | Ocak 2010 |
| `yayin_gecikmesi_gun` | 2026 örneklerinde yaklaşık 39–41 takvim günü |
| `M_eksi_2_aninda_erisim` | Evet, örnek yayın takviminde |
| `revizyon_politikasi` | Veri Portalında ayrı `Revizyon Geçmişi` serisi yayımlanır |
| `revizyona_kapali_mi` | **Hayır** |
| `kapatilan_bilgi_boslugu` | Gerçekleşmiş motorlu-taşıt ticareti üzerinden satışa dönüşüm vekili olma adayı |
| `mekanizma_bir_cumle` | Faturalanmış motorlu-taşıt ticaret hacmi gerçekleşmiş satış faaliyetine eşzamanlı bir toplulaştırılmış ölçü sağlayabilir. |
| `mevcut_featuredan_neden_farkli` | Noter adetinden farklı idari kaynak ve sabit-fiyatlı ciro/hacim yapısıdır; ancak M−2'de hedef geçmişine yakın bilgi taşır. |
| `hukuki/erişim_riski` | Resmî ve kamuya açık; bu aşamada veri indirilmedi. |
| `as_of_vintage_riski` | **Yüksek.** Resmî revizyon geçmişi vardır; ilk-yayım=nihai değildir. |
| `on_hukum` | **Elendi.** Revizyona-kapalılık yoktur. NACE 45; yeni/ikinci el, toptan/perakende, onarım ve motosikleti karıştırır. M−2 kullanımı öncü yeni boşluk yerine mevcut hedef hafızasının daha kaba/eşzamanlı bir kopyasına yakındır. |

Kaynaklar:

- TÜİK, [Ticaret Satış Hacim Endeksi — Şubat 2026](https://veriportali.tuik.gov.tr/tr/press/58271): yayın tarihi, NACE 45 aylık değişimi ve kapsam.
- TÜİK, [Ticaret Satış Hacim Endeksi [2021=100] — Revizyon Geçmişi ve Metaveri](https://veriportali.tuik.gov.tr/tr/databrowser/tuik/categories/9/9_5/TR%2CDF_TICARET_SATIS_HACIM_ENDEKS_O%2C1.0): Ocak 2010 başlangıcı, KDV-beyanname kaynağı ve revizyon geçmişi.

## Yapısal bulgu

Seçenek 2 kapsamında altı aile tüketildi: BDDK, BETAM–sahibindex, Google
Trends, TCMB kart işlemleri, SBM poliçeleri ve TÜİK ticaret satış hacmi.
İncelenen altı ailenin hiçbirinde, hedefle temiz mekanizma bağı ve kamuya açık
as-of/ilk-yayım korunumu birlikte kurulamadı. Bazı adaylar ayrıca kapsam,
toplulaştırma veya mekanizma kapısında düştü.

Bu taramanın sınırları içinde ulaşılan hüküm:

> Mevcut kamuya açık Türkiye veri ortamı, bu hedef ve bu as-of disipliniyle,
> geriye dönük değerlendirmeye uygun öncü bilgi eklenmesini desteklememektedir.

Bu hüküm “Türkiye'de hiçbir veri yoktur” iddiası değildir; iki ön-kayıtlı,
sınırlı masa başı taramasında incelenen altı aileye ilişkin proje sonucudur.

## Sayfa bütçesi

Yedi farklı birincil/resmî dokümantasyon veya yayın sayfası kullanıldı; bütçe
`7/10`'da durduruldu. Kalan üç sayfa, bir aday geçene kadar aramayı sürdürmek
için kullanılmadı.
