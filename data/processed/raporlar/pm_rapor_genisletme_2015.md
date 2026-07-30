# PM Raporu — Genişletme 2015 (kapsam 2018-01 → 2015-01)

**Tarih:** 2026-07-30

---

## 1. Ne Yapıldı

`prompts/veri/18_genisletme_2015_prompt.md` görevi kapsamında, proxy fiyat
(BETAM) ve ENAG **hariç** tüm dış özellikler 2018-01'den 2015-01'e geriye
genişletildi. Kaynak bazında özet:

| Seri | Kaynak | Genişletilen kapsam | Sonuç |
|---|---|---|---|
| USD/TRY (aysonu + aylık ort.) | TCMB EVDS3 (A) | 2015-01 → bugün | Tam, 0 eksik |
| TÜFE endeksi (zincirlenmiş) | TCMB EVDS3 (A) | 2015-01 → 2026-06 | Tam (2026-07 yapısal gecikme, ilgisiz) |
| Taşıt kredisi faizi + politika faizi | TCMB EVDS3 (A) | 2015-01 → bugün | Tam, 0 eksik |
| OSD üretim (binek+kamyonet) | TCMB EVDS3 (A) | 2015-01 → bugün | Tam, 0 eksik |
| Tüketici güven endeksi + oto satınalma ihtimali | TCMB EVDS3 (A) | 2015-01 → bugün | Tam, 0 eksik |
| ODMD sıfır araç satışı (toplam/otomobil/HTA) | ODMD bülteni "10 Yıllık Ortalama" tablosu (C) | 2015-01 → bugün | Tam (aynı PDF, 500 DPI yeniden okuma) |
| Noter devir adedi — **TOPLAM** | TÜİK "Motorlu Kara Taşıtları" bültenleri (B) | 2015-01 → bugün | Tam, 0 eksik |
| Noter devir adedi — **OTOMOBİL kırılımı** | aynı | yalnızca 2018-01 → bugün | 2015-2017 bilinçli NaN (bkz. §5) |
| ÖTV olay-dummy | Resmi Gazete + vergi sirküleri (çapraz doğrulamalı) | 2015-01 → bugün | 1 yeni olay eklendi (2016-11-25) |
| Alım gücü proxy'si (brüt ücret-maaş endeksi) | TÜİK İşgücü Girdi Endeksleri (B) | **YALNIZCA 2018-01 → bugün** | 2015-2017 BLOKE (erişim engeli, bkz. §5) |
| Erişim endeksi (türetilmiş: noter/alım gücü) | dahili hesap | **YALNIZCA 2018-01 → bugün** | Alım gücüne bağımlı olduğu için aynı kısıt |
| Proxy fiyat (BETAM) | — | **KAPSAM DIŞI** | Görev talimatı gereği dokunulmadı |
| ENAG | — | **KAPSAM DIŞI** | Görev talimatı gereği dokunulmadı |

Güncellenen script'ler: `genisletme_1a_usdtry.py`, `genisletme_1b_tufe.py`,
`genisletme_2a_noter_devir.py`, `genisletme_2b_alim_gucu.py` (yalnızca
docstring — kapsam değişmedi), `genisletme_3a_odmd.py`, `genisletme_3b_osd.py`,
`genisletme_3c_faiz.py`, `genisletme_3d_tuketici_guveni.py`,
`genisletme_4_otv_olaylari.py`, `genisletme_5_birlestir.py`,
`genisletme_6_hedef_etiket.py`. Hepsi yeniden çalıştırıldı ve doğrulandı.

Hedef etiket zinciri (K1, `genisletme_6_hedef_etiket.py`) **değiştirilmedi** —
yalnızca girdi/çıktı dosya adları (`veri_2018_bugun_*` → `veri_2015_bugun_*`)
güncellendi. k=0.5 sabit, sigma_nominal=0.01261, sigma_reel=0.01521 — proxy
fiyat dönemi (2024-01+) değişmediği için bu değerler **önceki turla birebir
aynı** çıktı (25/137 geçerli geçiş, aynen önceden olduğu gibi).

## 2. Sayısal Özet / Yeni Tablo Boyutu

- Birleşik tablo (`veri_2015_bugun_birlesik.csv`): **138 satır × 31 sütun**
  (2015-01 → 2026-06, tarih sürekliliği tam — eksik ay yok).
- Etiketli tablo (`veri_2015_bugun_etiketli.csv`): **138 satır × 41 sütun**
  (10 türetilmiş hedef/yardımcı sütun eklendi).
- Önceki tur (2018-01 başlangıçlı) 96 satır idi → **42 ay (3.5 yıl) eklendi.**
- Toplam eksik hücre: 977 / 4278 (birleşik tabloda) — tamamı ya yapısal
  (proxy fiyat 2024 öncesi, alım gücü/erişim endeksi 2018 öncesi, TÜFE
  yıllık değişim ilk 12 ay, vb.) ya da bilinçli tasarım kararı
  (noter_devir_otomobil_adet 2015-2017); **beklenmeyen/açıklanamayan eksik
  hücre bulunmadı.**

## 3. Kırmızı Bayrak Sonucu

Kısa (dakikalar mertebesinde) bir tarama yapıldı, tam bir analiz değildir:

- **Tarih sürekliliği:** 2015-01 → 2026-06 arası 138 ay, hiçbir ay eksik değil. ✅
- **İmkânsız değerler:** Tüm sayım/oran sütunlarında (ODMD, OSD, noter devir,
  USD/TRY, TÜFE) negatif değer taraması yapıldı — **sıfır negatif değer.** ✅
- **ODMD iç tutarlılık:** `odmd_toplam_adet = odmd_otomobil_adet +
  odmd_hta_adet` özdeşliği 2015-2017 penceresinde de test edildi —
  **maksimum fark 0.0** (tam tutarlı). ✅
- **Aşırı aylık değişim (kaba eşik |%değişim| > %50):** ODMD toplamında ve
  OSD üretiminde 2015-2017 içinde birkaç ay bu eşiği aştı (ör. 2015-02,
  2015-12, 2016-01, 2017-08/09 — hep Ocak-Şubat düşüşü / Aralık-Ağustos
  sıçraması kalıbında). **Bu, YENİ bir anomali değil** — aynı kaba eşikle
  2018-2023 penceresi de tarandı ve orada da 15 (ODMD) ve 10 (OSD) ay bu
  eşiği aşıyor (Ocak-Şubat mevsimsel düşüşü, Ağustos fabrika-bakım
  kapanışı gibi bilinen kalıplar). Sonuç: **kırmızı bayrak yok**, mevsimsel
  norm ile tutarlı.

## 4. Noter Devir + TÜFE Baz-Geçişi Özel Notları

**Noter devir (en kırılgan kalem):** 2018+ döneminde kaynak, TÜİK'in
"cari yıl + önceki yıl" xls tablosuydu (Aralık bültenleri, 5 farklı bülten
2 yıllık bloklar halinde). 2015-2017 için bu tarz çok-yıllık bir özet tablo
YOKTU; bunun yerine **36 ayrı aylık bültenin** ("Motorlu Kara Taşıtları -
Ocak 2015" ... "Aralık 2017") gövde metnindeki "{Ay} ayında {X} adet
taşıtın devri yapıldı" cümlesi tek tek okundu. Bu cümle TAM (yuvarlanmamış)
bir sayı verdiği için `noter_devir_toplam_adet` 2015-2017 için de GÜVENİLİR/
TAM kabul edildi. Ancak aynı bültenlerde otomobilin devir içindeki payı
YALNIZCA yuvarlanmış yüzde olarak verilir (ör. "%69,4 ile ilk sırada") —
2018+'in xls tablosundaki TAM SAYI kırılımının aksine. Yüzdeden geriye
çarparak "yaklaşık" bir otomobil adedi üretmek CLAUDE.md Kural 3'e aykırı
olacağından, **`noter_devir_otomobil_adet` 2015-01→2017-12 için bilinçli
olarak NaN bırakıldı** (36 ay). Bu bir veri kaybı değil, hassasiyet/kaynak
sınırlamasıdır.

**TÜFE baz-geçişi:** Mevcut zincirleme yöntemi (2003=100 seri TP.FG.J0 →
2025=100 seri TP.TUKFIY2025.GENEL, tek bir katsayıyla — bkz.
`genisletme_1b_tufe.py`) 2015-2017 penceresinin TAMAMEN 2003=100 rejiminin
içinde kaldığı doğrulandı; **bu pencere için EK bir zincirleme katsayısına
gerek yoktu**, mevcut kod hiç değiştirilmeden (yalnızca `BASLANGIC_AY`
güncellenerek) doğru sonuç verdi.

## 5. Karşılaşılan Sorunlar

1. **Alım gücü (brüt ücret-maaş endeksi) 2015-2017'ye GENİŞLETİLEMEDİ —
   erişim engeli.** Aynı TÜİK "İşgücü Girdi Endeksleri (2021=100)" tablosu
   (2009-2026 tam tarihçeyi içerdiği zaten bilinen belge) tekrar denendi,
   ancak bu turda indirme linki bir SPA (React) client-side route olarak
   davranıyordu — ne doğrudan curl/WebFetch (SPA kabuğu HTML dönüyor) ne de
   tarayıcı aracıyla tıklama (network loglarında yeni istek tetiklenmiyor)
   çalıştı. Önceki turda belgelenen doğrudan `/api/tr/data/downloads?...`
   uç noktası bu oturumda bulunamadı (site güncellenmiş olabilir).
   WebSearch ile ikincil kaynak araması da bu spesifik çeyreklik rakamları
   getirmedi. **Sonuç: `brut_ucret_maas_endeksi_2021_100` ve ondan türeyen
   `erisim_endeksi`, 2015-01→2017-12 için NaN kalıyor** — bu bir veri kaybı
   değil, bu oturumdaki bir erişim engelidir; ileride site tekrar
   denenebilir.
2. Noter devir 2015-2017 için 36 ayrı bültene tek tek navigasyon gerekti
   (tek bir çok-yıllık özet tablo yoktu) — zaman maliyeti daha yüksekti ama
   sorunsuz tamamlandı.
3. Otomobil kırılımı hassasiyet farkı (yukarıda §4'te detaylandırıldı) —
   bir "sorun" değil ama açıkça işaretlenmesi gereken bir kaynak sınırı.

## 6. Veri Örneği (geçiş noktası: 2015-01, 2015-06, 2017-12, 2018-01)

Aşağıdaki dört satır, `veri_2015_bugun_birlesik.csv` dosyasından ham olarak
alınmıştır (geçiş noktasını göstermek için — 2017-12→2018-01 arası
`noter_devir_otomobil_adet`, `brut_ucret_maas_endeksi_2021_100` ve
`erisim_endeksi` sütunlarının NaN'dan dolu değere geçişine dikkat):

```
--- 2015-01 ---
usdtry_aysonu: 2.4035 | tufe_endeks: 250.45 | tasit_kredisi_faiz: 11.006
odmd_toplam_adet: 34615.0 | odmd_otomobil_adet: 24498.0
osd_binek_kamyonet_toplam_adet: 94706.0
tuketici_guven_endeksi: 89.34781946
noter_devir_toplam_adet: 462576.0 | noter_devir_otomobil_adet: NaN
brut_ucret_maas_endeksi_2021_100: NaN | erisim_endeksi: NaN

--- 2015-06 ---
usdtry_aysonu: 2.6887 | tufe_endeks: 259.51 | tasit_kredisi_faiz: 11.865
odmd_toplam_adet: 86158.0 | odmd_otomobil_adet: 67766.0
osd_binek_kamyonet_toplam_adet: 116042.0
tuketici_guven_endeksi: 89.62664021
noter_devir_toplam_adet: 533624.0 | noter_devir_otomobil_adet: NaN
brut_ucret_maas_endeksi_2021_100: NaN | erisim_endeksi: NaN

--- 2017-12 ---
usdtry_aysonu: 3.81385 | tufe_endeks: 327.41 | tasit_kredisi_faiz: 13.524
odmd_toplam_adet: 136240.0 | odmd_otomobil_adet: 99694.0
osd_binek_kamyonet_toplam_adet: 121689.0
tuketici_guven_endeksi: 87.80834831
noter_devir_toplam_adet: 673141.0 | noter_devir_otomobil_adet: NaN
brut_ucret_maas_endeksi_2021_100: NaN | erisim_endeksi: NaN

--- 2018-01 ---
usdtry_aysonu: 3.7829 | tufe_endeks: 330.75 | tasit_kredisi_faiz: 14.17
odmd_toplam_adet: 35076.0 | odmd_otomobil_adet: 26611.0
osd_binek_kamyonet_toplam_adet: 117590.0
tuketici_guven_endeksi: 92.38315817
noter_devir_toplam_adet: 631823.0 | noter_devir_otomobil_adet: 445255.0
brut_ucret_maas_endeksi_2021_100: 55.077816 | alim_gucu_ceyrek: 2018-Q1
erisim_endeksi: 11471.46066939183
```

Geçiş temiz ve beklenen şekilde: TÜM sayısal seriler 2015-01'den itibaren
zaten dolu; yalnızca (a) noter devir otomobil kırılımı ve (b) alım gücü/
erişim endeksi ikilisi, kaynak sınırlamaları nedeniyle 2018-01'de
başlıyor.

## 7. Varsayımlar ve Kararlar (K/N kararlarına uygunluk)

- **K1 (hedef tanımı) DEĞİŞTİRİLMEDİ** — hedef etiket zinciri dokunulmadan
  yeniden çalıştırıldı, aynı sigma/eşik/sınıf dağılımı elde edildi.
- **NET KAPSAM KARARI'na (proxy fiyat + ENAG hariç tutma) uyuldu** —
  ikisine de yeni kaynak arama veya genişletme denemesi yapılmadı.
- Noter devir otomobil kırılımını 2015-2017 için NaN bırakma kararı, bu
  oturumda proje sahibi onayı ALINMADAN, CLAUDE.md Kural 3'ün ("kaynaksız
  iddia yazılmaz... tahmin yürütülmez") doğrudan uygulanması olarak
  verildi — bu, §8'de proje sahibinin onayına/itirazına açık bir madde
  olarak da tekrar işaretleniyor.
- Farklı kaynakların serileri KONTROLSÜZ birleştirilmedi — her seri kendi
  `referans_ayi` anahtarıyla outer-join edildi, hiçbir enterpolasyon/
  doldurma yapılmadı.

## 8. Açık Sorular / PM Onayı Gerekenler

1. **Noter devir otomobil kırılımı (2015-2017, 36 ay) NaN mı kalmalı, yoksa
   bülten yüzdelerinden "yaklaşık" bir sayı mı türetilmeli?** Mevcut karar
   NaN yönünde (kesinlik kaybı fark edilir şekilde işaretlensin diye) —
   ancak modelleme aşamasında bu 36 ayın tamamen dışarıda kalması
   (otomobile özgü noter devir sinyali için) istenmiyorsa, PM onayıyla
   yüzde-bazlı yaklaşık değer üretimi ayrı bir görev olarak açılabilir.
2. **Alım gücü/erişim endeksi 2015-2017 için başka bir kaynaktan (örn.
   TÜİK'in farklı bir tablosu, SGK/Hazine verisi) aranmalı mı?** Bu
   oturumda zaman-maliyeti gözetilerek (Kural 9) tek bir ek deneme yapılıp
   bırakıldı; PM isterse ayrı bir küçük görev olarak yeniden denenebilir.
3. **ÖTV 2015-2017 taraması yalnızca 1 olay (2016-11-25) buldu** — bu,
   2018-2025 arası ortalama ~1.5 olay/yıl temposuyla kabaca tutarlı (3 yıl
   için 1 olay biraz düşük ama mantıksız değil, çünkü 2014'teki büyük
   reform sonrası 2016'ya kadar sistem zaten görece durağandı). Yine de bu
   bir "negatif kanıt" (yokluk kanıtı değil) olduğundan, PM'in kendi
   bilgisiyle çelişen bir nokta varsa belirtmesi faydalı olur.

## 9. Önerilen Sonraki Adım (başlatılmadı, yalnızca öneri)

- Alım gücü/erişim endeksi 2015-2017 blokajı için TÜİK veri portalının
  API/route yapısı zaman içinde değişebileceğinden, birkaç ay sonra tek
  seferlik bir yeniden deneme (mevcut `genisletme_2b_alim_gucu.py`
  script'i küçük bir düzeltmeyle) düşük maliyetli bir sonraki adım olabilir.
- Modelleme aşamasına geçilmeden önce, yeni 138 satırlık tablonun (özellikle
  2015-2017 penceresinin) EDA/görselleştirmesi (Faz 8 hedef keşif tarzı)
  yapılırsa, otomobil kırılımı NaN'ının pratikte ne kadar sorun yarattığı
  somut olarak görülebilir.
