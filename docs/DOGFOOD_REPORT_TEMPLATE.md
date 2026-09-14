# Dogfood Raporu — aylık şablon

> Her ay Discussions → **Show and tell** kategorisine bu şablonla rapor
> düşülür. Amaç: "kendi-ilacımızı-içiyoruz" iddiasını sayılarla ve olaylarla
> kanıtlamak — pazarlama-değil, operasyon-kaydı. Aşağıdaki her başlığı
> gerçek-sayılarla doldur; sıfır-olayı da rapordur (sessiz-ay = sağlam-ay).

---

## Sester Dogfood Raporu — {AY YIL}

**Kapsam:** filo-rayı (`examples/fleet_lane/`) · {N} ajan · {N} endpoint
**Dönem:** {başlangıç} – {bitiş}

### 1) Trafik ve harcama

| Metrik | Değer |
|---|---|
| Ücretli-istek (200) | {n} |
| Reddedilen (402) | {n} |
| — politika-red | {n} |
| — kota-aşımı | {n} |
| — replay | {n} |
| — burst-limit | {n} |
| Toplam-harcama | {x.xx} USDC-sim |
| Günlük-p95 harcama | {x.xx} |

### 2) Zincir-sağlığı

- `verify_chain()` günlük-cron sonuçları: {N}/{N} SAĞLAM
- En-uzun kesintisiz-zincir: {N} gün
- Bundle-export sayısı: {N} (dış-denetçi-doğrulaması: {N}/{N} SAĞLAM)

### 3) Olaylar (varsa)

| Tarih | Olay | Fail-closed davranışı | Sonuç |
|---|---|---|---|
| {tarih} | {kısa-tanım} | {ne-dedi: 402 + hangi-kural} | {fix/issue/pinned-test linki} |

*(Olay yoksa: "Bu ay olay yok — reddedilen {n} istek tümü politika-beklentisi
içinde reddedildi." yaz.)*

### 4) Bu-ayın öğrenesi

{1-3 cümle: gerçek-trafiğin hangi-kararı değiştirdi? Kota-tuning?
Yeni-kural? Hiçbir-şey-değişmediyse bunu da yaz — sabitlik de bilgidir.}

### 5) Kanıt

- Ledger-head: `{head-hash-in-ilk-16-hanesi}`
- Doğrulama-komutu (herkes koşabilir):
  `python scripts/dogrula.py adoption/{bundle}.json`

---

*Önceki-rapor: {link} · Rapor-takvimi: her-ayın ilk-salı.*
