# Model 11 — Hedef ve bilgi tavanı teşhisi ön-kayıt

Bu dosya sonuçlar görülmeden önce Pusula tarafından `effort=max` düzeyinde
kilitlenen uygulama sözleşmesidir. Ana target, üç sınıf ve ±%5 stable bandı
değiştirilmez. Test `2025-07..2026-06` açılmaz; `2025-05/06` embargo kalır.

## Sabit analiz penceresi ve rolling sözleşme

- Etiket penceresi: `2019-01..2025-04`.
- OOF teşhis penceresi: `2021-03..2025-04`, 50 origin.
- Her origin M için train en geç M-3'te biter; M-2/M-1 embargo.
- CI: dört aylık hareketli blok, 2.000 çekiliş, ortak indeks, sabit seed.

## Önceden ilan edilmiş dış kırılma adayları

Etiket serisine bakılmadan üç tarih seçilmiştir; serbest tarih taraması yoktur.

1. `2020-03`: WHO, 11 Mart 2020'de COVID-19'u pandemi olarak niteledi.
   Kaynak: https://www.who.int/docs/default-source/coronaviruse/transcripts/who-audio-emergencies-coronavirus-press-conference-full-and-final-11mar2020.pdf
2. `2021-12`: Türkiye'de kur korumalı mevduat uygulaması Aralık 2021'de başladı.
   Kaynak: https://www3.tcmb.gov.tr/yillikrapor/2021/tr/m-2-4.html
3. `2023-02`: 6 Şubat 2023 Kahramanmaraş merkezli depremler.
   Kaynak: https://www.afad.gov.tr/kahramanmarasta-meydana-gelen-depremler-hkbasin-bulteni22

Her tarih için 10.000 permütasyonlu ki-kare, Cramér's V ve üç tarih ailesinde
Holm α=0,05 uygulanır. Başka tarih eklenmez.

## Lag ve geçiş teşhisi

- Geçiş matrisi; 10.000 permütasyonlu bağımsızlık testi.
- Laglar: 1/2/3/12; Cramér's V, blok4 %95 CI, 10.000 permütasyon ve Holm.
- Aynı 50 originde lag-1/2/3/12 persistence MCC ve blok4 CI.
- Lag-1 her çıktıda `operasyonel_degil=true`; aday veya terfi yolu değildir.

## Stable-band duyarlılığı

Sabit liste: `±2,5 / ±3,5 / ±5,0 / ±7,5 / ±10,0`. Yalnız üç baseline
yeniden hesaplanır; dört model yeniden fit edilmez. Bir bant yalnız persistence
MCC'si ana ±%5 değerini en az 0,10 aşar ve blok4 CI alt sınırı >0 olursa
`maddi_farkli=true` alır. Stable payı >%60 ise `mcc_yorumlanamaz=true`.
Bu çıktı hedefi değiştirmez; yalnız olası K önerisi üretir.

## Oracle bilgi tavanı

Bilgi kümesi M-2'ye kadarki değer/etiketler ve cut-off snapshot feature'larıdır;
M-1/M yasaktır. Oracle yalnız 50 değerlendirme ayı üzerinde bilerek in-sample
fit edilir; Model 10 OOF performansıyla kıyaslanmaz, kendi permütasyon null95'i
ile kıyaslanır.

- Oracle-A S0 sabit, S1=`y(M-2)`, S2=`y(M-2)` × `y(M-3) stable/stable-değil`.
- Gözlenen durum sayısı ≤6 ve durum başına ortalama N≥8 zorunludur.
- Oracle-B aynı dört sabit Model 09 konfigürasyonunun in-sample tavanıdır.
- Null: outcome ay etiketi karıştırılır, aynı fit prosedürü yinelenir. A için
  2.000; B için hesap maliyeti nedeniyle önceden izin verilen 1.000 permütasyon.
- Her çıktı `(tavan_gozlenen, tavan_null95)` ve minimum hücre N ile yazılır.

## Önceden kilitli hüküm sırası

1. C — modelleme alanı: herhangi oracle, null95'i ≥0,15 marjla aşar.
2. B — bilgi gecikmesi: lag-1 persistence CI altı >0, lag-2/3 için değil.
3. D — hedef tanımı: en az bir alternatif bant `maddi_farkli=true`.
4. A — bilgi kısıtı/öngörülemez: oracle'lar null95'i aşmaz, lag-1 CI sıfırı
   içerir ve hiçbir bant maddi farklı değildir.

Birden fazla hüküm ateşlenirse tümü raporlanır; öncelik `C > B > D > A`.
Sonuç ne olursa olsun yeni model, test açma veya K değişikliği yapılmaz.
