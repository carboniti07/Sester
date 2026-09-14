# SESTER — v0.6.0 Yol-Haritası (2026-09-14)

> Mevcut-durum: v0.5.0 canlı (GitHub Release; PyPI eşiği temiz — upload
> kullanıcı-eylemi). Bu harita **öncelik-sıralı**, her adım kabul-kriterli;
> IS_PLANI §7 geleneği: her adım test-önce + kapı-adımıyla kapanır.
> **Onay-sütunu:** ✓ = onay-beklemeden kodlanabilir (kullanıcı-falanı yok);
> ⏸ = kullanıcı-kararı/üçüncü-taraf-hesap şart.

## Öncelik-sırası

| # | Adım | Ne katar | Kabul-kriterleri | Onay |
|---|---|---|---|---|
| 1 | **Metering-metriği (PULL)** | `GET /metrics` — istek/402/kota/replay sayaçları (Prometheus-text; `statsd` yok, 0-bağımlılık) | counter'lar replay-402/kota-402/charge ile birebir; exempt-yollar saymaz; test ≤5 senaryo | ✓ |
| 2 | **Burst-limit (token-bucket)** | quota'nun yanına ikinci-kapı: saniye-içi patlama-dışı-yakalama (fail-closed) | 10 istek/1sn limit → 11. RED `rate_limited`; bucket-parametreleri middleware-arg | ✓ |
| 3 | **Webhook-imza (outbound kanıt-akışı)** | receipt/settlement olaylarını `HMAC-timestamp` imzayla POST-la (retry + failure-log ledger'da) | alıcı-side doğrulama-vector'ü testi; retry 3× backoff; imza-sız gönderim yok | ✓ |
| 4 | **PyPI-sonrası dev-bump** | `__init__`+pyproject → `0.6.0.dev0`; kapı-adımı-5 sürüm-parametrik | guard sürüm-senkronu yeşil; PyPI 0.5.0'a dokunulmaz | ⏸ (upload-sonrası) |
| 5 | **tx-imzalama (PSP-sız EVM)** | facilitator'a opsiyonel imzalayıcı-arayüzü (non-custodial korur: anahtar-envanter kullanıcıda) | imzalama-olmadan mevcut-akış değişmez; imzalayıcı takılıyken E2E batch→broadcast-mock | ⏸ (anahtar-yönetimi kararı) |
| 6 | **PSP-adaptörleri (PayTR/iyzico/Stripe)** | settlement_rail vokabülerine gerçek-adaptörler; 64'ün `LIVE_DISABLED_UNTIL_PSP_CERT` kapısı | her-PSP: sandbox-e2e + imza-vector testi; cert-olmadan canlı-yol açılmaz | ⏸ (PSP-sözleşmesi) |
| 7 | **Canlı-trafik sertleşmesi** | rate/timeout/pool ayarları facilitator_svc'de + load-kanıtı (k6/pyperf) | 100-rps 5dk'da p99<50ms, sıfır fail-open; yük-kanıtı rapor-doc | ⏸ (barındırma-kararı) |

## Bağımlılık-şeması

```
1 ─┬─→ 2 ─┬─→ 7 (canlı-trafik)
   └──────┴─→ 3 (kanıt-webhook'ları)
4 (PyPI-sonrası) → 5 → 6
```

## v0.6.0 sürüm-tanımlayıcı (öneri)

**İçerik:** #1 + #2 + #3 (+ #4 bump'ı) — hepsi onay-beklemeyen, çekirdek-doktrine
dokunmayan, kablo-donukluğunu koruyan adımlar. #5–#7 v0.7.0'a: PSP-sözleşmesi ve
barındırma-kararı kullanıcı-işleri.

## Disiplin (değişmez)

- Kablo-donukları (pugio0/pugio_bundle_version/source:sikke) korunur — v2'ye dek.
- Her adım: test-önce + publish_gate SWEEP=1 + CHANGELOG-girişi.
- Fail-closed: yeni-kapı da RED üretir, sessiz-geçiş yok.
