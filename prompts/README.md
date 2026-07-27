# prompts/ — Prompt Arşivi

Bu klasör iki farklı aşamaya ait prompt arşivlerini ayrı tutar.

## `prompts/` (kök) — Aşama A: Literatür Tarama

Master plan (`00_planlama_prompt.md`), Faz 1-8 tarama promptları
(`01_*_prompt.md` … `08_*_prompt.md`), sentez talimatı (`09_sentez_talimati.md`)
ve yardımcı dönüşüm talimatı (`pdf_donusturme_talimati.md`). Her dosya, ilgili
`docs/NN_*.md` çıktısını üreten claude.ai Deep Research promptudur.

Bu köke ayrıca, veri mühendisliği kapsamına girmeyen **repo-seviyesi
navigasyon/meta promptları** da eklenir (ör. `09_repo_yeniden_yapilandirma_prompt.md`)
— bunlar bir faz taraması değildir, repo yapısını/dokümantasyonunu günceller.

## `prompts/veri/` — Aşama B: Veri Mühendisliği

MVP veri seti, genişletme (2024-bugün ve 2018-bugün), fizibilite araştırmaları,
korelasyon analizi ve hedef keşfi promptlarının arşivi. Her dosya, ilgili
`data/processed/raporlar/pm_rapor_*.md` çıktısını üreten Claude Code görev
talimatıdır. Numaralandırma kronolojik, harf ekleri (`04a`, `07b` gibi) aynı
aşamanın paralel/alt-görevlerini gösterir.

Her iki alt klasörde de kural aynı: bir prompt kullanılmadan önce buraya
arşivlenir (öz-arşivleme), sonra çalışmaya başlanır — bkz. `CLAUDE.md`.
