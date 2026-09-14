# Reddit — three tailored posts (never cross-post identical text)

## r/Python (lead: engineering discipline)

**Title:** I built a zero-dependency ASGI middleware where every failure path denies spend — including "policy file is corrupt"

Body:
The doctrine behind Sester: if you're metering money, "fail open" isn't a mode,
it's a leak. So the design rules are strict:

- corrupt/missing policy file → `DENY_ALL` (all spend stops, not per-request errors)
- unknown payment scheme → 402, never a free pass
- tampered evidence bundle → loud RED in verification, never a receipt
- facilitator outage → 402, not a free call

Each of those is pinned by a named test in the suite (214 passing across two
backends — SQLite and Postgres-parity). Zero required dependencies: the core
is stdlib-only; optional extras are opt-in (`pip install "sester[demo]"`).

It's one ASGI middleware for AI-agent APIs: x402-style 402→payment→receipt
handshake, integer minor-unit metering, per-agent daily quotas, burst
limits, human-approval escalation, and a hash-chained receipt ledger that
third parties can verify with just sha256.

Repo: https://github.com/goun7/Sester · PyPI: https://pypi.org/project/sester/

What I'd love scrutiny on: the fail-closed paths. Find a silent fallback and
it's a security bug by definition.

## r/MachineLearning (lead: the agent-economy angle)

**Title:** Agents that pay per API call need receipts too — I open-sourced a middleware that meters and proves agent spending

Body:
x402-style protocols solved the "agent pays" handshake, but nobody ships the
boring 90%: who spent what, under whose limit, with proof that survives an
audit. Sester is an ASGI middleware you wrap your agent-facing API in:

- per-agent daily quotas + burst caps in integer minor units
- spend policy with allow-lists, time windows, and human-approval escalation
- every charge and denial lands in a hash-chained ledger; bundles verify
  with plain sha256 — no library needed on the auditor side
- x402 / AP2 / ACP / UCP compile onto one receipt core

Demo: `docker run --rm -p 8402:8402 ghcr.io/goun7/sester-demo:latest` then
open /panel. Repo: https://github.com/goun7/Sester

Interesting failure mode I engineered for: an agent that retries in a burst
after a payment failure — that's what the token-bucket second gate is for.

## r/selfhosted (lead: the panel + single binary feel)

**Title:** Sester: self-hosted metering + payment panel for AI APIs (one Docker container, SQLite, zero deps)

Body:
If you're exposing an AI API and want usage-based charging without standing
up a billing stack: Sester is one middleware + one panel. Docker single
container, SQLite inside, quota/burst/receipt out of the box, and the panel
shows who called, how much, and whether the receipt chain is intact.

    docker run --rm -p 8402:8402 ghcr.io/goun7/sester-demo:latest

Fail-closed by design: if anything is wrong (corrupt policy, unknown
scheme), it denies spend loudly instead of silently letting calls through.
Repo + docs: https://github.com/goun7/Sester
