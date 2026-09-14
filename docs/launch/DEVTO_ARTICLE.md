# dev.to article — full draft (canonical long-form; also drives SEO)

---
title: "One middleware that makes your AI-agent API charge, meter, and prove"
published: true
tags: python, ai, agents, payments
cover_image: <repo-raw .github/assets/og.png URL after going public>
---

## The gap

Agent-commerce rails (x402 and friends) solved the *handshake*: agent gets a
402, pays, retries. What nobody ships is the boring 90% — metering, quotas,
spend policy, and evidence you can hand to an auditor. Sester is one ASGI
middleware for exactly that layer, with zero required dependencies.

## The 3-minute tour

```python
# your existing ASGI app stays untouched
from sester.middleware import SesterMeter
app = SesterMeter(app, db="ledger.sqlite3", secret=b"...", policy="policy.json")
```

Unpaid call → 402 with a `X-Payment-Required` challenge. Paid call → 200 with
`X-Sester-Receipt`. Daily quota exhausted → 402 `quota_exceeded`. Burst → 402
`rate_limited`. And every one of those events lands in a hash-chained ledger:

```python
from sester.ledger import Ledger
Ledger("ledger.sqlite3").verify_chain()   # True — or fail loud
```

## Why fail-closed is the whole design

If you meter money, "fail open" is not a mode — it's a leak. Sester's rules:

| Failure | Behavior |
|---|---|
| Policy file corrupt/missing | `DENY_ALL` — all spend stops |
| Unknown payment scheme | 402, never a free pass |
| Tampered evidence bundle | loud RED in verification |
| Replay of a spent envelope | 402, pinned by test |

Each row is a named test in the suite. When someone reports a silent fallback,
we treat it as a security bug and pin it with a test the same day.

## Four protocols, one core

x402, AP2 (mandates), ACP (checkout sessions) and UCP (seller-signed carts)
all compile onto one wire-format core: `ChargeIntent` → `ChargeReceipt`.
Adding a fifth protocol is one adapter file. The receipts are hash-chained;
third parties verify bundles with nothing but `sha256`.

## Try it

```bash
pip install "sester[demo]"
uvicorn sester.demo_api:app --port 8402
# or
docker run --rm -p 8402:8402 ghcr.io/goun7/sester-demo:latest
```

Repo: https://github.com/goun7/Sester · PyPI: https://pypi.org/project/sester/

Ask: try to break the fail-closed paths and tell us what you find.
