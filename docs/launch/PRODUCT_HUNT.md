# Product Hunt — launch draft

## Tagline (≤60 chars)

    One middleware that meters and proves AI-agent payments

## Description (short)

Sester wraps your AI-agent API as a single ASGI middleware: x402-style
402→payment→receipt handshake, per-agent quotas and burst caps, fail-closed
spend policy, and a hash-chained receipt ledger that anyone can verify with
plain sha256. Zero required dependencies.

## First comment (maker)

We kept meeting teams building agent-commerce endpoints with three glued
services (billing, rate-limit, audit). Sester is that layer as one ASGI
middleware — and the design constraint is unusual: **every failure path
denies spend**. Corrupt policy → all spending stops. Unknown payment
scheme → 402, never a free pass. The suite pins each failure path with a
named test; a silent fallback is treated as a security bug.

Demo in 60 seconds (no signup):
`docker run --rm -p 8402:8402 ghcr.io/goun7/sester-demo:latest` → open /panel

Stack story for the PH crowd: Python 3.11–3.14, stdlib-only core, optional
extras for EVM/JWS/Postgres, 214 tests across SQLite + Postgres-parity,
Apache-2.0.

## Gallery assets

- `og.png` (1280×640) — main card
- panel screenshot (`/panel` with a few receipts + green chain badge)
- terminal GIF of the 402→receipt curl flow

## Timing

Tue–Thu 00:01–02:00 PT; maker online first 3 h; reply doctrine in
`../LAUNCH_KIT.md` (answer with test names).
