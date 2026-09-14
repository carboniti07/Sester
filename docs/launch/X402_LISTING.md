# x402 ecosystem listings + MCP registry — submission copy

## 1) x402 ecosystem listing (site/registry listing form fields)

- **Name:** Sester
- **Category:** Developer tooling / metering & settlement
- **One-liner:** x402-style metering, quotas, fail-closed policy and
  hash-chain receipts for AI-agent APIs — as one ASGI middleware.
- **Description:** Sester implements the boring 90% of agent commerce:
  per-agent daily quotas in integer minor units, token-burst caps, a
  fail-closed spend-policy engine (allow-lists, time windows, human-approval
  escalation), and a tamper-evident hash-chained receipt ledger. x402, AP2,
  ACP and UCP compile onto one wire-format core; evidence bundles verify
  with plain sha256 (no library on the verifier side). Apache-2.0, Python
  3.11–3.14, stdlib-only core.
- **Links:** https://github.com/goun7/Sester · https://pypi.org/project/sester/
- **Integration status:** seller-side metering + client-side facilitator
  (verify/settle transport) implemented; demo API included.

## 2) MCP server registry (if/when you expose an MCP surface)

Submission needs a running MCP endpoint. Fastest path: expose the demo as an
MCP server wrapper (`uvicorn sester.demo_api:app` behind an MCP adapter),
then submit:

- **Server name:** sester-demo
- **Transport:** HTTP
- **Endpoint:** https://goun7.github.io/Sester/ (landing) → link to hosted demo URL
- **Auth:** 402 challenge (x402/pugio0 HMAC scheme) — the registry's
  payment-flow test IS the demo.

## 3) Awesome-list PRs (one line each)

- awesome-x402 → `sester — ASGI middleware: x402 metering, quotas, fail-closed policy, hash-chain receipts`
- awesome-ai-agents (payments section) → same one-liner + "verifiable receipts (sha256)"
- awesome-fastapi → `sester — drop-in metering/payment middleware for FastAPI/Starlette`
