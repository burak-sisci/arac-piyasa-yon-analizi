# Claude Uygulama Promptu — Hacim Yön Baseline Denetim Düzeltmeleri

Bu tur yalnız aşağıdaki dar düzeltmeleri uygula. Geniş tarama, model eğitimi,
yeni analiz, commit ve push yapma. Sonunda pytest çalıştır ve kısa özet ver.

1. `README.md`: “Nihai hedef tanımı proje sahibi bekliyor” satırını K9 aktif
   hedef kararıyla uyumlu yap. `model_01..05` dosyalarının tümünü PM onaysız
   gösterme: model_01/02 commitli, TimeSeries seviye baseline ve PM raporludur;
   yalnız untracked model_03/04/05 bu paketin dışındadır. Fiyat hedefindeki
   sayı “28 dolu fiyat ayı / yaklaşık 25 hesaplanabilir yön etiketi” olmalıdır.
2. `docs/00_karar_kaydi.md`: HEAD v8'den bu branch'te tek revizyon olduğu için
   metadata `v9` olmalı, `v10` değil. K8 altında hiç commitlenmemiş ve kaldırılmış
   fiyat scriptini tarihsel “uygulama” gibi gösterme; paragrafı sadeleştir ve
   yalnız `yon_degerlendirme.py` dosyasının K9 kapsamında target-bağımsız
   altyapıya dönüştürüldüğünü belirt.
3. `scripts/model/model_06_hacim_yon_siniflandirma.py`: `fit_weighted_ensemble=False`
   bir kök-neden düzeltmesi değil, gözlenen AutoGluon 1.5.0 ensemble aux
   çökmesini bypass eden geçici workaround olarak anlatılmalı. Kesin upstream
   kök nedenin kanıtlanmadığını yaz. İleri JSON'a splitten dinamik
   `model_egitim_son_ayi`, `kullanim_durumu: yalniz_pipeline_demonstrasyonu`
   ve modelin eski train kesiminde eğitildiğini, olasılığın raw olduğunu,
   üretim/fiyatlama kararında kullanılamayacağını belirten açık uyarı ekle.
4. Mevcut ignored `model_06_hacim_yon_*_ileri_sinyal.json` dosyalarını model
   eğitmeden aynı metadata/uyarı ile güncelle; olasılıkları değiştirme.
5. `pm_rapor_hacim_yon_3sinif_baseline.md`: workaround/kök neden dilini
   düzelt. İleri sinyallerin değerlendirme modellerinden geldiğini ve eğitim
   sonlarının DF-A 2024-03, DF-B 2025-03 olduğunu; stale, düşük raw güvenli ve
   operasyonel/fiyatlama kararında kullanılamaz olduklarını açıkça yaz.
6. PM raporu Bölüm 6'yı kullanıcıya bırakılan sorular yerine Codex kararlarıyla
   kapat: DF-A negatif baseline kabul, production yok; DF-B yalnız keşifsel;
   stable recall=0 operasyon için kabul edilemez ve sonraki iterasyonda ilk
   müdahale class weighting; workaround yalnız AutoGluon 1.5.0 için geçici.
7. `CLAUDE.md`, README ve karar kaydında yalnız bu maddelerle ilgili kalan
   çelişkileri düzelt.
8. `.venv312\\Scripts\\python.exe -m pytest tests/test_yon_degerlendirme.py -q`
   çalıştır. Model scriptini yeniden çalıştırma.

Dokunma: `notebooks/*.ipynb`, `AGENTS.md`, `urls_out.txt`, model_03/04/05,
`main` branch'i.
