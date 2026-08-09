# PM Raporu — Model 01–18 Tarihsel Gelişim Notebooku

## 1. Ne Yapıldı

Model 01’den Model 18’e kadar tüm numaralı aşamalar kronolojik olarak tek bir
ileri-seviye ders kitabı notebookunda birleştirildi. Her aşama için hedef/veri,
yöntem, değerlendirme protokolü, bir önceki aşamadan temel fark, sonuç, hüküm ve
kanıt dosyası kaydedildi.

“Model” adı taşımasına rağmen yeni model eğitmeyen aşamalar açıkça ayrıldı:
Model 03–05 yeniden değerlendirme, Model 07 veri sözleşmesi, Model 08 baseline,
Model 11–13 teşhis/üst tavan, Model 17 karar katmanı ve Model 18 prospektif
izleme olarak etiketlendi.

Üretilenler:

- `notebooks/model_tarihsel_gelisim_ve_farklar_ders_kitabi.ipynb`
- `scripts/model/model_tarihsel_gelisim_notebook_uret.py`
- `tests/test_model_tarihsel_gelisim_notebook.py`
- `prompts/veri/49_model_tarihsel_gelisim_notebook_prompt.md`

## 2. Sayısal Özet

- Kapsanan numaralı aşama: `18/18`.
- Notebook hücresi: `23` (`14` Markdown, `9` kod).
- Çalıştırılan kod hücresi: `9/9`; hata çıktısı: `0`.
- Gömülü ana kronoloji satırı: `18`.
- Görselleştirme: `3` — rol/zaman haritası, MASE seviye karşılaştırması,
  aynı-50-origin MCC/macro-F1 karşılaştırması.
- Ayrı metrik rejimi: `2` — Model 01/02 MASE; Model 06–18 MCC/macro-F1.
- Yeni model fit: `0`; kilitli test erişimi: `0`.
- Doğrulama: notebooka özel `8/8`, tam paket `169/169` test geçti.

## 3. Karşılaşılan Sorunlar

- Pusula’nın aynı kalıcı Sonnet/xhigh oturumundaki ilk geniş taraması terminal
  sınırında kesildi. Kapsam daraltılarak aynı oturumda yapılan son denetimde
  kronoloji, metrik rejimleri, rakamlar ve iddia sınırları doğrulandı; kritik veya
  yüksek öncelikli hata bulunmadı.
- Model 03–05 scriptleri kullanıcıya ait untracked dosyalardır. Kod niyetleri
  tarihçeye alındı; commitli/PM-onaylı metrik bulunmadığından sonuç iddiası
  yazılmadı.
- Model 03/04, tüm veriyle eğitilmiş kayıtlı predictor’ı geçmiş kesitlerde
  yeniden fit etmeden kullanır; gerçek walk-forward dış-örnek kanıtı değildir.
- Model 06 için erken README kaydı DF-B MCC’yi `+0,387`, sonraki sınıf-ağırlığı
  iterasyonu PM raporu `-0,387` verir. Notebook, nihai iterasyon raporunu esas
  aldı ve tarihsel farkı açıkça not etti.
- Notebook çalıştırılırken nbconvert `cwd` seçeneğini tanımadığına dair uyarı
  verdi; hücreler repo/notebooks çalışma dizinini otomatik algıladığı için 9/9
  tamamlandı. Çıktıda hücre hatası yoktur.

## 4. Veri Örneği

Ana kronoloji tablosundan ilk ve son satırların özeti:

```text
model,rol,hedef,sonuc,hukum
1,Eğitim,30 günlük ham seviye,"MASE 0,454","Seviye baseline'ı; yön protokolü değildir"
18,Prospektif izleme,Aylık yön,"2026-08 down p=0,4315; N=0/12","Performans sonucu yok"
```

## 5. Varsayımlar ve Kararlar

- Tracked PM raporları, README ve `docs/10–11` birincil denetim kaynağıdır.
- Gitignored model JSON/CSV dosyaları yalnız opsiyonel canlı kontrol içindir;
  notebookun ana anlatısı bunlara bağımlı değildir.
- MASE ile MCC aynı grafik/performans sıralamasında birleştirilmedi.
- Model 14 en iyi dengeli dondurulmuş aday; Model 17 yalnız en yüksek nokta
  MCC’ye sahiptir. Hiçbiri terfi etmiş model olarak sunulmadı.
- Model 18 ilk sinyali performans sonucu olarak yorumlanmadı.
- Mevcut kullanıcı notebooklarına dokunulmadı.

## 6. Açık Sorular / PM Onayı Gerekenler

Bağlayıcı hedef/K/N kararı gerekmiyor. Model 03–05’in ileride denetim zincirine
alınması istenirse, mevcut kodları çalıştırmak yeterli değildir: metodoloji
sızıntı açısından yeniden tasarlanmalı, ön-kaydedilmeli ve ayrı PM raporuyla
commitlenmelidir.

## 7. Önerilen Sonraki Adım

Notebook, yeni geliştirici onboarding ve model karar toplantılarında tek tarihçe
olarak kullanılabilir. Model 18’de 12 eksiksiz prospektif ay tamamlandığında,
terminal sonuç yeni bir bölüm olarak eklenmeli; o tarihe kadar performans grafiği
güncellenmemelidir.
