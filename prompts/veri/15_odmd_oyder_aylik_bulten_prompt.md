ROL VE BAĞLAM

Sen, "Araç Piyasası Fiyat Yönü Tahmini" projesinin repo yöneticisi ve veri
mühendisisin. Önceki bir taramada ODMD/Indicata "İkinci El Online Sektör
Raporu"nun 2021-2023 için yalnızca YILDA BİR (Aralık) yayımlandığı
sanılmıştı. Bu YANLIŞ ÇIKTI — OYDER'in (Oto Yetkili Satıcıları Derneği)
kendi arşivinde 2024 için Ocak/Şubat/Mart gibi AYLIK bültenler bulundu.
Görev: bu kaynağı daha derin taramak ve 2021-2023 için gerçek kapsamı
netleştirmek.

BAĞLAYICI İLKELER:
- Yalnızca kamuya açık kaynaklar (K5).
- WebSearch/dış kaynaktan gelen rakamlar İKİNCİ bir kaynakla doğrulanmadan
  kullanılmaz (bu projede daha önce yıl-karışması hatası kanıtlanmıştı).
- Farklı kaynakların serilerini kontrolsüz birleştirme; her bülteni kendi
  kaynağıyla (ODMD doğrudan / OYDER arşivi / haber aktarımı) etiketle.
- Bu bir VERİ TOPLAMA görevi; hedef/model değiştirme yok.

======================================================================
GÖREV 0 — ÖZ-ARŞİVLEME
======================================================================
Bu talimatı prompts/veri/15_odmd_oyder_aylik_bulten_prompt.md olarak kaydet.

======================================================================
GÖREV 1 — ERİŞİM NOKTALARINI HARİTALA
======================================================================
İki ana erişim noktasını dene:
1. ODMD'nin kendi sitesi (odmd.org.tr) — önceki taramada JS-render olduğu
   için zor bulunmuştu. Tekrar dene; belki doğrudan URL kalıbı veya arama
   motoru üzerinden (site:odmd.org.tr "ikinci el" [ay] [yıl]) bulunabilir.
2. OYDER'in arşiv sayfası (oyder-tr.org/raporlar veya benzeri) — bu turda
   2024 aylık bültenlere buradan erişildiği görüldü. Bu sayfanın TAM
   arşivini (mümkün olduğunca geriye, ideal olarak 2021'e kadar) tara.

Her iki kaynaktan da ulaşılabilen TÜM ayları listele (yalnızca 2024 değil,
bulabildiğin her yıl/ay).

======================================================================
GÖREV 2 — 2021-2023 KAPSAMINI NET OLARAK DOĞRULA
======================================================================
Bu görevin ASIL SORUSU: 2021, 2022, 2023 için AYLIK bültenler gerçekten
var mı, yoksa sadece yıllık özet mi?

- Her yıl için ayrı ayrı kontrol et: "ODMD ikinci el online sektör raporu
  [ay] [yıl]" ve "OYDER ikinci el rapor [ay] [yıl]" gibi sorgularla.
- Haber ajansı aktarımlarını da tara (AA, Bloomberg HT, Dünya Gazetesi vb.)
  — bazı aylar doğrudan rapor bulunamasa bile haber aktarımından rakam
  çıkarılabilir.
- HER BULUNAN AY İÇİN: kaynak URL'si + kaynak türü (doğrudan rapor / haber
  aktarımı) + hangi rakamların mevcut olduğunu (ilan sayısı, satış adedi,
  fiyat değişimi, segment/yaş dağılımı) kaydet.
- Bulunamayan aylar için "bulunamadı" diye açıkça işaretle, boş bırakma
  veya tahmin etme.

======================================================================
GÖREV 3 — İÇERİK ÇIKARIMI (bulunan her bülten için)
======================================================================
Her bülteni içerik olarak şu alanlara ayır (varsa):
- Aylık ilan sayısı
- Aylık satış adedi (kaç ilan satışa dönüştü)
- Fiyat değişimi (% aylık, perakende ve/veya toptan — önceki taramada
  bu bir "% değişim" olarak bulunmuştu, mutlak seviye değil)
- Segment (A/B/C/D) bazlı satış dağılımı
- Yaş grubu (0-5, 6-10, 11+ yaş) bazlı satış dağılımı
- Yakıt tipi dağılımı (varsa)

======================================================================
GÖREV 4 — ÇIKTI
======================================================================
- data/raw/odmd_oyder/odmd_oyder_bultenler_ham.csv: her satır bir ay,
  yukarıdaki alanlar + kaynak URL + kaynak türü + bulunabilirlik durumu.
- data/processed/analiz/odmd_oyder_kapsam_ozeti.csv: yıl bazında kaç ay
  bulunabildi (2021: x/12, 2022: x/12, 2023: x/12, 2024: x/12, ...).

======================================================================
PM RAPORU — ZORUNLU
======================================================================
data/processed/raporlar/pm_rapor_odmd_oyder.md üret VE oturumda
KOPYALANABİLİR DÜZ METİN olarak göster.

Başlıklar: (1) Ne yapıldı. (2) EN KRİTİK SONUÇ: 2021-2023 için gerçek
kapsam nedir — yıl bazında kaç ay bulunabildi, net rakam. (3) Bulunan
bültenlerin içerik zenginliği (hangi alanlar mevcut, hangi yıllarda daha
zayıf). (4) Kaynak güvenilirliği (doğrudan rapor vs haber aktarımı oranı).
(5) Karşılaşılan sorunlar (JS-render, erişim engelleri vb.). (6) Veri
örneği. (7) Açık sorular / PM onayı gerekenler — özellikle "bu kaynak
BETAM'ın 2021-2023 açığını kapatmaya yeter mi" sorusuna dair kanıta dayalı
bir değerlendirme (karar değil, kanıt).

YAPMA:
- Hedef/model değiştirme.
- ODMD/OYDER verisini BETAM ile birleştirme (ayrı kaynak olarak kalacak,
  birleştirme kararı sonraki aşama).
- Bulunamayan ayları tahminle doldurma.
