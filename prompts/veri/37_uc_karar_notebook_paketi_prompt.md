# Prompt Arşivi — Üç Karar Notebooku Paketi

**Tarih:** 2026-08-07

**İsteyen:** Proje sahibi

**Uygulayan:** Rota

**Karar ortağı:** Pusula, kalıcı session `6f4c6fd0-6ddb-4b70-8e45-86d5b6d124c1`

## Kullanıcı talebi

> öncelikle claude.md dosyasını .gitignore içine al.
>
> ardından pusulayı çağır. pusula /model-sonnet /effort-extra
>
> aşağıda bana sunduğun üç seçenek için ilk notebookları yazın. notebookları
> birlikte yazacaksınız. iş bölümünü aranızda halledin.
>
> 1. Negatif bulguyla bu hedef için projeyi kapatmak.
>
> 2. Target ve üç sınıfı koruyarak bilgi kümesini yeni öncü verilerle
> genişletmek.
>
> 3. Tahmin ufku/toplulaştırma veya sınıf sayısını değiştirmek.

## Teknik yorum

Claude Code CLI `extra` adlı bir effort değeri kabul etmemektedir. Desteklenen
en yakın karşılık `xhigh` olduğundan Pusula aynı kalıcı session içinde
`--model sonnet --effort xhigh` ile çağrıldı. Yeni session açılmadı.

## Ortak yazım iş bölümü

- Pusula: pedagojik omurga, karar mantığı, yanlış yorum uyarıları, ortak
  puanlama şeması ve karar kapıları.
- Rota: Model 09-11 çıktı şemalarının okunması, fallback sözleşmesi,
  çalıştırılabilir Python hücreleri, grafik ve tablolar, `.ipynb` montajı,
  execution/QA, repo belgeleri ve Git.
- Pusula iş bölümünü açıkça kabul etti; veto bildirmedi.
- Rota, Pusula taslağındaki keşifsel `3→2 MCC` hücresini ortak “yeni performans
  ölçümü yok” sınırıyla çeliştiği için uygulamadı. Yerine performans üretmeyen
  hedef sözleşmesi ve örneklem fizibilitesi hücreleri yazıldı.

## Sabit sınırlar

- Yeni veri çekilmez, yeni feature üretilmez, model fit edilmez.
- `2025-07..2026-06` kilitli test açılmaz.
- Yalnız Model 09, 10 ve 11'in resmî test-dışı kanıtı kullanılır.
- Notebooklar seçenekleri uygulamaz; ilk karar laboratuvarlarını oluşturur.
- Nihai seçenek ilan edilmez; karar proje sahibine bırakılır.
