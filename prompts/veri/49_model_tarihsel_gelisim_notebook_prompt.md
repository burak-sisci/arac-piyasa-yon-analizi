# Prompt 49 — Model Tarihsel Gelişim Notebooku

**Tarih:** 2026-08-09
**Talep:** “Pusula’yı çağır. Şu ana kadarki eğittiğimiz tüm modellerin tarihsel
gelişimi ve her modelin birbirinden farkını kronolojik olarak ele alan bir
notebook yazın.”

## Uygulama sözleşmesi

- Pusula yalnız aynı kalıcı oturumda kullanılır:
  `019fd8ad-8e18-7b4e-a6d4-3c0214efc923`, Sonnet/xhigh.
- Notebook Türkçe ve ileri seviye geliştirici ekibe yönelik olacaktır.
- Model 01–18 kronolojik sırada ele alınacaktır.
- “Model” numarası taşısa da veri hazırlama, baseline, teşhis, karar katmanı veya
  prospektif izleme olan aşamalar eğitim yapan modellerden açıkça ayrılacaktır.
- Model 03–05 yerel/untracked ve PM-onaysız olduğundan kod niyeti anlatılabilir;
  metrikleri güvenilir proje kanıtı gibi sunulamaz.
- MASE ile MCC/macro-F1 aynı eksende kıyaslanmayacaktır.
- Kilitli test açılmayacak; yeni model eğitimi veya performans deneyi yapılmayacaktır.
- Notebook, gömülü denetim tabloları ve yeniden çalıştırılabilir görselleştirme
  hücreleri içerecektir; mevcut kullanıcı notebooklarına dokunulmayacaktır.

## Zorunlu çıktı

- `notebooks/model_tarihsel_gelisim_ve_farklar_ders_kitabi.ipynb`
- Üretilebilirlik için notebook üretici scripti
- README durum güncellemesi ve yedi başlıklı PM raporu
