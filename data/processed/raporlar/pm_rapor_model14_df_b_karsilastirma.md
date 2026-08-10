# PM Raporu — Model 14 DF-B Keşifsel Karşılaştırması

## 1. Ne Yapıldı

Kullanıcı talebi üzerine dondurulmuş Model 14 adayı olan **Lojistik L2
C=0,1**, DF-B haftalık snapshot'ı üzerinde ayrı bir karşılaştırma kolunda
çalıştırıldı. Model 14'ün 14 feature'ı, dengeli sınıf ağırlığı, her origin'de
train-içi median imputation + standardizasyon ve iki aylık embargo sözleşmesi
korundu.

DF-B snapshot'ında Model 14'ün iki feature'ı yoktu:
`tuketici_guven_endeksi_lag2ay` ve `odmd_otomobil_adet_lag2ay`. Bu iki sütun
aynı `kesit_tarihi + hedef_ay + hafta_sirasi` anahtarındaki DF-A snapshot'ından
`one_to_one` doğrulamasıyla aktarıldı. DF-B'ye özgü ENAG/BETAM feature'ları
kullanılmadı; onları eklemek dondurulmuş Model 14 değil, yeni bir model ailesi
olurdu.

Deney sözleşmesi sonuç görülmeden önce
`prompts/veri/50_model14_df_b_karsilastirma_onkayit.md` dosyasına yazıldı.
Temmuz 2025–Haziran 2026 kilitli test dönemi kullanılmadı.

## 2. Sayısal Özet

- DF-B kilit öncesi etiketli ay: **17** (`2024-02..2025-06`).
- İlk eğitim penceresi: **12 ay**.
- Embargo: **2 ay**.
- Bağımsız değerlendirme ayı: **3** (`2025-04`, `2025-05`, `2025-06`).
- Dört hafta havuzlu tahmin satırı: **12**; etkin bağımsız N yine **3 ay**dır.

| Metrik | DF-B sonucu |
|---|---:|
| Yön doğruluğu (accuracy) | **%0,0** |
| Macro-F1 | **0,0000** |
| MCC | **-0,6124** |

Yön doğruluğu matrisi; satırlar gerçek, sütunlar tahmindir. Sınıf sırası
`down / stable / up`:

| Gerçek \ Tahmin | down | stable | up |
|---|---:|---:|---:|
| down | 0 | 0 | 4 |
| stable | 4 | 0 | 0 |
| up | 4 | 0 | 0 |

Ay bazında dört haftanın tamamında aynı sonuç oluştu:

| Hedef ay | Gerçek | Tahmin (hafta 1–4) |
|---|---|---|
| 2025-04 | up | down / down / down / down |
| 2025-05 | stable | down / down / down / down |
| 2025-06 | down | up / up / up / up |

Yalnız dördüncü hafta kullanıldığında da MCC `-0,6124`, macro-F1 `0,0000` ve
accuracy `%0,0` oldu; bu, aynı üç ayın tek haftalık görünümüdür.

## 3. Karşılaşılan Sorunlar

1. **Etkin örneklem yalnız üç aydır.** Dört haftalık satırlar aynı aylık etiketi
   tekrar eder; N'yi 12'ye yükseltmez. Sonuç genellenebilir performans kanıtı
   değildir.
2. **DF-B Model 14 feature setini tek başına taşımıyor.** İki ortak ekonomik
   feature DF-A snapshot'ından aktarılmadan dondurulmuş 14-feature model
   çalışmıyordu.
3. İlk origin'in 12 aylık eğitiminde
   `hedef_m12_m13_degisim_pct` tamamen boştu. Model 14 ile aynı `SimpleImputer`
   davranışı korunarak bu feature ilk fit'te atlandı; sonraki iki originde dolu
   gözlem oluştu.
4. DF-B'nin zenginliğini oluşturan ENAG/BETAM sütunları bu deneyde avantaj
   sağlamadı, çünkü sabit Model 14 feature listesinde değiller.

## 4. Veri Örneği

Tahmin çıktısının ilk ve son satırları:

```text
fold,hedef_ay,train_ay_sayisi,hafta_sirasi,gercek,tahmin
1,2025-04,12,1,up,down
1,2025-04,12,2,up,down
...
3,2025-06,14,3,down,up
3,2025-06,14,4,down,up
```

Üretilen yerel çıktılar:

- `data/processed/model/model_14_df_b_karsilastirma_ozet.json`
- `data/processed/model/model_14_df_b_karsilastirma_tahminleri.csv`
- `data/processed/model/model_14_df_b_yon_dogrulugu_matrisi.csv`
- `data/processed/model/gorseller/model_14_df_b_yon_dogrulugu_matrisi.png`

## 5. Varsayımlar ve Kararlar

- Dondurulmuş ana Model 14 ve DF-A çıktıları değiştirilmedi.
- Kullanıcı talebi bir **karşılaştırma deneyi** olarak uygulandı; DF-B ana veri
  setine terfi ettirilmedi.
- Kilitli test açılmadı. Bu nedenle Model 14'ün özgün 24 ay train + 2 ay embargo
  sözleşmesi DF-B'de kurulamazdı; ön-kayıtlı yardımcı fonksiyonun izin verdiği
  minimum 12 aylık train kullanıldı.
- Metrik sırası ve confusion matrix, proje standardı `down / stable / up` ile
  hesaplandı.

## 6. Açık Sorular / PM Onayı Gerekenler

Bu sonuç DF-B'nin tüm bilgi değerini ölçmez; yalnız aynı Model 14 feature setinin
kısa DF-B penceresinde yeniden fit edilmesini ölçer. DF-B'ye özgü ENAG/BETAM
feature'larını kullanmak istenirse bunun ayrı, ön-kayıtlı yeni model ailesi
olarak tanımlanması gerekir. Mevcut görev kapsamında böyle bir arama
başlatılmadı.

## 7. Önerilen Sonraki Adım

Ana baseline olarak **DF-A üzerindeki dondurulmuş Model 14 korunmalıdır**.
DF-B'nin bu deneydeki `%0` doğruluğu yalnız üç ay nedeniyle kesin bir “DF-B
işe yaramaz” hükmü değildir; fakat DF-B'yi ana hatta alma lehine hiçbir kanıt da
üretmemiştir. Kilitli testi açmadan DF-B ile daha güvenilir bir Model 14 metriği
hesaplamak mümkün değildir.
