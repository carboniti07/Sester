"""SESTER v0.6.0 — yol-haritası adım-1 (metrics) + adım-2 (burst-limit).

Kabul-kriterleri (V060_YOL_HARITASI.md):
  · metrics: counter'lar gerçek-kararla birebir (replay-402, quota-402,
    charge-200); exempt-yollar sayılmaz; 0-bağımlılık Prometheus-text.
  · burst: token-bucket ikinci-kapı; 11. istek RED `rate_limited`;
    bucket middleware-arg; kota-tarafından BAĞIMSIZ (ikisi de fail-closed).
"""
from __future__ import annotations

import time

import pytest

from sester.ledger import Ledger
from sester.middleware import SesterMeter
from sester.panel import render_panel


def _mac_header(m: SesterMeter, agent: str, nonce: str, amount: str = "0.05",
                resource: str = "/weather") -> str:
    import hashlib
    import hmac as hmac_mod
    msg = f"{agent}|{nonce}|{amount}|{resource}".encode()
    mac = hmac_mod.new(m.secret, msg, hashlib.sha256).hexdigest()
    return f"{m.VERSION} {agent}:{nonce}:{amount}:{mac}"


class _ASGIRec:
    """Minimal ASGI recorder — status/headers/body toplar."""
    def __init__(self):
        self.status = None
        self.body = b""
        self.headers = []


async def _call(m: SesterMeter, path: str = "/weather", headers: list | None = None):
    rec = _ASGIRec()

    async def send(message):
        if message["type"] == "http.response.start":
            rec.status = message["status"]
            rec.headers = message.get("headers", [])
        elif message["type"] == "http.response.body":
            rec.body += message.get("body", b"")

    scope = {"type": "http", "path": path, "headers": headers or []}
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    await m(scope, receive, send)
    return rec


async def _inner_ok(scope, receive, send):
    """Handler-dublörü: 200 + gövde (middleware'in arkasındaki uygulama)."""
    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"ok"})


@pytest.fixture()
def env(tmp_path):
    led = Ledger(tmp_path / "v060.sqlite3", secret="v060")
    m = SesterMeter(_inner_ok, led, secret="v060-secret", daily_quota=25.0)
    return led, m


# ---------------------------------------------------------------- adım-1: metrics

def test_metrics_exposed_and_counters_exact(env):
    led, m = env

    async def run():
        # 2 başarılı charge + 1 replay + 1 kota-aşımı üret
        for i in (1, 2):
            await _call(m, headers=[(b"x-payment", _mac_header(m, "ag-m", f"n{i}").encode())])
        await _call(m, headers=[(b"x-payment", _mac_header(m, "ag-m", "n1").encode())])  # replay
        m.quota_minor = 5  # 0.05$-lık tek-çağrı sonrası kota-dolar
        await _call(m, headers=[(b"x-payment", _mac_header(m, "ag-m", "n3").encode())])
        # metrics-istemi (exempt)
        return await _call(m, path="/metrics")

    rec = _run_async(run())
    assert rec.status == 200, rec.body
    text = rec.body.decode()
    assert "sester_requests_total" in text
    assert "sester_charges_total 2" in text
    assert "sester_replay_402_total 1" in text
    assert "sester_quota_402_total 1" in text
    assert "sester_chain_valid 1" in text
    assert "# TYPE" in text  # Prometheus-text disiplini


def test_metrics_exempt_and_excluded_from_itself(env):
    led, m = env

    async def run():
        await _call(m, path="/metrics")     # exempt: sayaç-oluşturmaz
        await _call(m, path="/healthz")     # exempt
        return await _call(m, path="/metrics")

    rec = _run_async(run())
    text = rec.body.decode()
    # exempt-istekler sayaç-artırmaz: yalnız chain/metrics-varlık satırları
    assert "sester_charges_total 0" in text
    assert "sester_replay_402_total 0" in text


def _run_async(coro):
    import asyncio
    return asyncio.get_event_loop_policy().new_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------- adım-2: burst

def test_burst_limit_blocks_over_bucket(env):
    led, m = env
    m.burst_capacity = 3          # 3-token bucket
    m.burst_refill_per_sec = 0.0  # test-içi refill yok → deterministik

    async def run():
        out = []
        for i in range(5):
            out.append(await _call(
                m, headers=[(b"x-payment", _mac_header(m, "ag-b", f"bn{i}").encode())]))
        return out

    recs = _run_async(run())
    assert [r.status for r in recs[:3]] == [200, 200, 200]
    assert recs[3].status == 402
    assert b"rate_limited" in recs[3].body
    # ledger'a karar-düşüldü (fail-closed denetim-izi)
    kinds = [e["event_type"] for e in led.export_events("ag-b")]
    assert "permission_decision" in kinds


def test_burst_refills_with_time(env):
    led, m = env
    m.burst_capacity = 1
    m.burst_refill_per_sec = 1_000_000.0  # mikro-saniyede-dolar → pratikte sınırsız

    async def run():
        return [await _call(m, headers=[(b"x-payment", _mac_header(m, "ag-r", f"rn{i}").encode())])
                for i in range(4)]

    recs = _run_async(run())
    assert all(r.status == 200 for r in recs), [r.status for r in recs]


def test_burst_is_per_agent(env):
    led, m = env
    m.burst_capacity = 1
    m.burst_refill_per_sec = 0.0

    async def run():
        a1 = await _call(m, headers=[(b"x-payment", _mac_header(m, "ag-1", "x1").encode())])
        a2 = await _call(m, headers=[(b"x-payment", _mac_header(m, "ag-2", "x2").encode())])
        a1b = await _call(m, headers=[(b"x-payment", _mac_header(m, "ag-1", "x3").encode())])
        return a1, a2, a1b

    a1, a2, a1b = _run_async(run())
    assert a1.status == 200 and a2.status == 200   # farklı-ajanlar bağımsız bucket
    assert a1b.status == 402                        # ag-1 bucket'ı boş
