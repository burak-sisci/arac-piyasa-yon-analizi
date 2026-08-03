# notebooks/ — Serbest/Keşifsel Analiz Alanı

Bu klasör, proje sahibinin **kendi başına, ad-hoc** Jupyter notebook
analizleri için ayrılmıştır — `scripts/veri/`'den FARKLI bir amaca hizmet
eder:

| | `scripts/veri/` | `notebooks/` |
|---|---|---|
| Amaç | Yeniden çalıştırılabilir veri pipeline'ı (çekme/temizleme/birleştirme) | Serbest keşif, deneme-yanılma, görselleştirme |
| Kim üretir | Claude Code, görev talimatlarına (prompt) bağlı | Proje sahibi, doğrudan |
| Çıktısı | `data/raw/`, `data/processed/` altına yazılan dosyalar | Yalnızca notebook içindeki analiz/görsel |
| Versiyon kontrolü | Her zaman commit'lenir | İsteğe bağlı (bkz. aşağıda) |

## Kullanım

Mevcut işlenmiş veriyi (DF-A / DF-B) bir notebook'ta yüklemek için:

```python
import pandas as pd

df_a = pd.read_csv("../data/processed/dataframes/df_a_kapsama_testli_v2.csv")
df_b = pd.read_csv("../data/processed/dataframes/df_b_zengin_2024_bugun_v2.csv")
```

Veri sözlüğü için: `../data/processed/dataframes/veri_sozlugu_df_a_df_b_v2.md`
Bu iki DataFrame'in güncel sütun/silme geçmişi için:
`../data/processed/raporlar/pm_rapor_sutun_temizlik_korelasyon.md`

## Jupyter kurulumu

Bu ortamda Jupyter henüz kurulu değil. Açmak için:

```bash
pip install jupyterlab
jupyter lab
```

(Veya VS Code'un Jupyter eklentisiyle `.ipynb` dosyaları doğrudan
açılabilir — yalnızca `ipykernel` gerekir: `pip install ipykernel`.)

## Versiyon kontrolü notu

`.ipynb` dosyaları Git'e girer (kod olarak) ama **hücre çıktıları** (grafikler,
büyük tablo dumpları) diff'leri şişirebilir. Commit etmeden önce
"Restart & Clear Output" yapman önerilir — zorunlu değil, bu proje
otonomi sınırının dışında, senin tercihin.
