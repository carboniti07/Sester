"""SESTER webhooks testleri — v0.6.0 adım-3 (kanıt-webhook).

Kapsam: üretici→alıcı çemberi (gerçek-kanıt-olayıyla), replay-penceresi,
kurcalanmış-gövde RED, bozuk-başlık RED, retry/backoff, ledger failure-log.
Alıcı-tarafı IMPORTSUZ doğrulama-vector'ü de pinlenir (K0 §7 disiplini).
"""
from __future__ import annotations

import hashlib
import hmac as hmac_mod
import json

import pytest

from sester.ledger import Ledger
from sester.webhooks import (
    build_webhook_payload,
    deliver_webhook,
    sign_webhook,
    verify_webhook,
)


@pytest.fixture()
def led(tmp_path):
    l = Ledger(tmp_path / "wh.sqlite3", secret="wh-secret")
    rec = l.append("charge_receipt", "ag-w", "/weather", 0.05,
                   payload={"nonce": "nw1", "paid": 0.05, "scheme": "pugio0"})
    yield l, rec
    l.close()


def _spec_verify(secret: str, body: bytes, header: str, *, now: float) -> tuple[bool, str]:
    """IMPORTSUZ alıcı-kopyası — karşı-tarafın göreceği tek-fonksiyon (spec-pin)."""
    parts = dict(p.strip().split("=", 1) for p in header.split(","))
    t = int(parts["t"])
    if abs(now - t) > 300:
        return False, "pencere"
    expected = hmac_mod.new(secret.encode(), f"{t}.".encode() + body,
                            hashlib.sha256).hexdigest()
    return hmac_mod.compare_digest(expected, parts["v1"]), "ok"


def test_producer_receiver_circle(led):
    l, rec = led
    payload = build_webhook_payload(rec)
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    header = sign_webhook("wh-joint", body, ts=1_700_000_000)
    ok, reason = _spec_verify("wh-joint", body, header, now=1_700_000_000)
    assert ok, reason
    # kütüphane-alıcısı da aynı kararı verir
    ok2, _ = verify_webhook("wh-joint", body, header, now=1_700_000_000)
    assert ok2


def test_replay_window_rejects_old_timestamp(led):
    _, rec = led
    body = json.dumps(build_webhook_payload(rec), sort_keys=True,
                      separators=(",", ":")).encode()
    header = sign_webhook("wh-joint", body, ts=1_700_000_000)
    ok, reason = verify_webhook("wh-joint", body, header,
                                now=1_700_000_000 + 301)
    assert not ok and "pencere-dışı" in reason


def test_tampered_body_rejected(led):
    l, rec = led
    # tam-satırı (kurcalanabilir-amount alanıyla) üret
    row = [e for e in l.export_events("ag-w") if e["seq"] == rec["seq"]][0]
    body = json.dumps(build_webhook_payload(row), sort_keys=True,
                      separators=(",", ":")).encode()
    header = sign_webhook("wh-joint", body)
    evil = body.replace(b"0.05", b"0.01")
    assert evil != body  # kurcalama gerçekten alan-değiştirdi
    ok, reason = verify_webhook("wh-joint", evil, header)
    assert not ok and "uyuşmuyor" in reason


def test_malformed_signature_headers(led):
    _, rec = led
    body = json.dumps(build_webhook_payload(rec), sort_keys=True,
                      separators=(",", ":")).encode()
    for bad in ("", "t=abc, v1=zz", "v1=" + "0" * 64, "x=1"):
        ok, reason = verify_webhook("wh-joint", body, bad)
        assert not ok
    # boş-secret üretimi de RED (fail-closed üretim-disiplini)
    with pytest.raises(ValueError):
        sign_webhook("", body)


def test_delivery_retry_then_success():
    calls = []

    def flaky_post(url, body, headers):
        calls.append(1)
        return 500 if len(calls) < 3 else 204

    ev = {"type": "charge_receipt", "agent": "a", "amount": 0.05,
          "seq": 1, "hash": "h" * 64, "ts": 1.0, "resource": "/w"}
    r = deliver_webhook("https://x/hook", "s", ev, post=flaky_post,
                        retries=3, backoff=0.0, sleep=lambda s: None)
    assert r == {"ok": True, "attempts": 3, "status": 204}


def test_delivery_failure_after_retries():
    def dead_post(url, body, headers):
        raise ConnectionError("hedef-kapalı")

    ev = {"type": "charge_receipt", "agent": "a", "amount": 0.05,
          "seq": 1, "hash": "h" * 64, "ts": 1.0, "resource": "/w"}
    sleeps: list[float] = []
    r = deliver_webhook("https://x/hook", "s", ev, post=dead_post,
                        retries=3, backoff=2.0, sleep=sleeps.append)
    assert not r["ok"] and r["attempts"] == 3 and "ConnectionError" in r["error"]
    assert sleeps == [2.0, 4.0]  # 1×, 2× backoff (3. deneme-sonrası uyku-yok)


def test_ledger_failure_log_on_delivery_failure(led, tmp_path):
    l, rec = led
    row = [e for e in l.export_events("ag-w") if e["seq"] == rec["seq"]][0]
    payload = build_webhook_payload(row)

    def dead_post(url, body, headers):
        raise OSError("network-down")

    r = deliver_webhook("https://x/hook", "wh-joint", payload, post=dead_post,
                        retries=2, backoff=0.0, sleep=lambda s: None)
    assert not r["ok"]
    # çağıran-tarafı disiplini: başarısızlık ledger'a webhook_delivery olarak düşer
    l.append("webhook_delivery", payload["agent"], payload["resource"], 0.0,
             payload={"url": "https://x/hook", "ok": False,
                      "attempts": r["attempts"], "error": r["error"],
                      "event_hash": payload["hash"]})
    kinds = [e["event_type"] for e in l.export_events("ag-w")]
    assert "webhook_delivery" in kinds
    assert l.verify_chain()
