# Sester Roadmap

Status at a glance — what shipped, what is in flight, and what we deliberately
do **not** build. Every release below passed the full test suite plus the
acceptance gate (`scripts/publish_gate.sh`) before publishing.

## Shipped

| Version | Highlights |
|---|---|
| **v0.1** | Metering middleware: x402-style 402 handshake, per-request pricing, per-agent daily quotas in integer minor units. Fail-closed policy DSL (host allow-lists, time windows, deny-by-default). Hash-chained SQLite receipt ledger with `verify_chain()`. |
| **v0.2** | Protocol adapters: AP2 mandates, ACP checkout sessions, UCP web-monetization → one `ChargeIntent`/`ChargeReceipt` core. Human-approval escalation (`then: escalate` → 402 ticket, one-time consumption, TTL). x402 v2 verify/settle facilitator with injectable transport. |
| **v0.3** | RFC 7515 JWS signing (HS256 stdlib, ES256 optional extra): mandates, checkout sessions. Owner-signed policy envelopes — tightening is instant, loosening is delayed 24 h. Postgres backend with hash-chain parity (identical heads across SQLite/PG). Hash-preserving migration tooling. |
| **v0.3.1** | Vendor-side ACP session issuing; SQLite → PG migration with `--plan/--dry-run/--verify`. |
| **v0.4** | On-chain settlement batches: pure-stdlib keccak-256, Merkle root recomputable in EVM, ABI-encoded `settle(...)` calldata — non-custodial (keys never touch Sester). `amount_minor` integer column with hash-preserving backfill. Deterministic EVM attribution. |
| **v0.5** | Hosted-facilitator service (FastAPI): verify/settle/refund + seller metering (free band, then 1% + $0.005 per event). Joint-acceptance runs with a sibling settlement system. Public release: identity migration, brand, English public surface. |
| **v0.6** | `GET /metrics` Prometheus-text observability. Per-agent burst limiting (token-bucket, independent of daily quota). HMAC-signed evidence webhooks with receiver-side verification and retry. **First public PyPI release.** |
| **v0.6.1** | Public-repo hygiene pass; README rendering fixes for PyPI. |

## In flight / next candidates

- **Transaction signing interface** — optional non-custodial signer for the
  facilitator's on-chain batches (key management stays entirely with the
  operator).
- **PSP adapters** — real payment-processor adapters behind the settlement-rail
  vocabulary; each stays dark until its sandbox acceptance run and signature
  vectors pass (no live rail without certification).
- **Live-traffic hardening** — rate/timeout/pool tuning plus a published
  load-acceptance report for the hosted facilitator.

Have an opinion on priorities? Vote in
[Discussions → Ideas](https://github.com/goun7/Sester/discussions) or open a
feature request.

## Deliberate non-goals

These are design decisions, not missing features (see the architecture decision
records):

- **No fail-open mode.** If the policy file is corrupt or missing, all spending
  stops (`DENY_ALL`). A metering layer that can fail open is a leak.
- **No custody.** Sester never holds spending keys. On-chain settlement is
  calldata preparation; broadcasting and keys belong to the operator.
- **No plug-in payment processor by default.** The core stays
  zero-dependency; anything that pulls in a network stack is an opt-in extra.
- **No silent recovery.** Every rejected request produces a ledger decision
  event — denials are auditable evidence, not noise.

## Compatibility promises

- Wire-format fields (`pugio0` scheme tag, `pugio_bundle_version`, envelope
  `source` values) are frozen through v1.x — external verifiers written today
  keep working.
- SQLite and Postgres backends produce **identical hash-chains** given the same
  secret and events; you can migrate and back without breaking evidence.
- Python 3.11–3.14, zero required dependencies (extras are strictly opt-in).
