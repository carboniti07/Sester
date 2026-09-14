# F1 Filo-Rayı — üretim-şablonu

Sester'in ilk gerçek-kiracısı: kendi-iç-endpoint'ini Sester-metering'in
arkasına takmanın eksiksiz-örneği. 5 entegrasyon-testiyle pinlenmiştir
(`tests/test_fleet_lane.py`).

## Hızlı-başlangıç (60 saniye)

```bash
# 1) Ortam:
cp examples/fleet_lane/.env.example examples/fleet_lane/.env
#    .env'i düzenle (SECRET'ı sır-yöneticinden al), sonra:
set -a; source examples/fleet_lane/.env; set +a

# 2) Sunucu (repo-kökünden):
.venv/bin/uvicorn examples.fleet_lane.app:app --port 8410

# 3) Ücretli-istek (başka-terminal):
.venv/bin/python examples/fleet_lane/send_paid_request.py --agent f1-n1
# → 200 + X-Sester-Receipt

# 4) Replay (aynı zarf tekrar):
.venv/bin/python examples/fleet_lane/send_paid_request.py --agent f1-n1 --replay  # → 402
```

## Gerçek-endpoint'i bağlama

`app.py` içinde `ROUTES` sözlüğü: anahtar = yol, değer = async-fonksiyon.
Fonksiyon `(scope) -> (status, body_bytes)` döner. Mevcut `/telemetry` ve
`/history` örnek-telemetri'lerdir — kendi iş-mantığını oraya koy.

Politika: `policy.json` — `host_in` listesine yeni-yol eklenmeden hiçbir
yol harcama-kapsamına girmez (fail-closed: bilinmeyen → deny). Çalışma-
saatleri dışı istek otomatik-red (`hour_between`).

## Üretim-servisi (systemd)

`examples/fleet_lane/sester-fleet.service` dosyasını
`/etc/systemd/system/` altına kopyala:

```bash
sudo cp examples/fleet_lane/sester-fleet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sester-fleet
systemctl status sester-fleet       # active (running) beklenir
curl -s localhost:8410/healthz      # {"ok": true, ...}
```

## Üretim-kontrol-listesi

- [ ] `SESTER_FLEET_SECRET` sır-yöneticiden; `.env` git'te değil
- [ ] `SESTER_FLEET_DB` kalıcı-diskte (tmp değil); yedek-stratejisi: dosya-kopyası yeterli (WAL sayesinde tutarlı)
- [ ] Politika-dosyası sürüm-lenmiş (repo'da); canlı-değişim = PR + review
- [ ] `verify_chain()` cron'u: günde-bir `python -c "from sester.ledger import Ledger; ..."` → RED ise uyarı
- [ ] `/metrics` → iç-dashboard'a bağla (Prometheus-text)
- [ ] 5 entegrasyon-testi CI'da yeşil (zaten koşuyor)
