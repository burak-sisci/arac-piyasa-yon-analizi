# Claude Uygulama Promptu — Hacim Yön Baseline Son Kabul Düzeltmeleri

Yalnız aşağıdaki son kabul düzeltmelerini yap. Model eğitimi, geniş tarama,
yeni analiz, commit veya push yok. Sonunda pytest çalıştır.

1. `README.md` üst bölümündeki “Açık durum: Nihai hedef tanımı ... proje
   sahibinin kararını bekliyor” metnini kaldır/düzelt. Aktif Aşama B target'ı
   K9 ile kararlaştırılmıştır: günlük granülerlikte `noter_devir_otomobil_adet`
   üç-sınıf yönü; K1 aylık tahmin ufku çalışma varsayımıdır. Durum listesindeki
   aynı “kullanıcı bekliyor” ifadesini de K9 kararıyla uyumlu `[x]` duruma getir.
2. PM raporu 6. zorunlu başlığını aynen koru ve karar kapanışını ekle:
   `## 6) Açık Sorular / PM Onayı Gerekenler — Codex Kararlarıyla Kapatıldı`.
3. PM raporu Bölüm 4'e model çıktı örneklerinden ÖNCE iki kaynak CSV'nin
   gerçekten ham ilk ve son üç satırından kısa örnek ekle:
   `df_a_v3_noter_penceresi_2015_bugun.csv` ve
   `df_b_v3_enag_betam_2024_bugun.csv`. En az `tarih`,
   `noter_devir_otomobil_adet` ve sette bulunan 2-3 ham feature göster;
   değerleri dosyadan oku, uydurma. Mevcut tahmin/JSON örneklerini koru.
4. PM raporundaki tüm `K12/N50` veya `N12/N50` yazımlarını doğru ifadeye
   çevir: `N12'nin N<50 keşifsel geçidi`.
5. PM raporunda “tek deneme kuralına aykırı tekrar yok / her set için tek fit”
   iddiasını dürüstçe düzelt. Geliştirme sırasında WeightedEnsemble hatasını
   teşhis ederken en az iki başarısız fit/config denemesi oldu (önce
   NeuralNetTorch, sonra LightGBMLarge belirtisi); nihai script çalıştırmasında
   workaround ile bir başarılı fit/set yapıldı. Başarısız denemeleri gizleme;
   nihai sonuç metriklerinin yalnız son sabit konfigürasyondan geldiğini yaz.
6. Geçici `scripts/claude_retry_hacim.ps1` zamanlayıcısını kaldır; teslimat
   artefaktı değildir.
7. `.venv312\\Scripts\\python.exe -m pytest tests/test_yon_degerlendirme.py -q`
   çalıştır. Model scriptini çalıştırma.

Dokunma: notebooks, AGENTS.md, urls_out.txt, model_03/04/05, main branch.
