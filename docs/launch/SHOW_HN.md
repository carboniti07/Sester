# Show HN — draft (validate against https://news.ycombinator.com/showhn.html)

**Title (exactly one sentence, no fluff — HN punishes marketing):**

    Show HN: Sester – one ASGI middleware that meters and proves AI-agent payments

**Text post body (first comment is yours — lead with the demo, not the story):**

I kept hitting the same gap: agent APIs (x402-style "agent pays per call")
had payment handshakes but no metering/quota/evidence layer, and adding one
meant bolting three services together. Sester is one ASGI middleware that
does it with zero required dependencies (stdlib only in the core).

3-minute demo:
  pip install "sester[demo]" && uvicorn sester.demo_api:app --port 8402
  # or: docker run --rm -p 8402:8402 ghcr.io/goun7/sester-demo:latest

What the demo shows: unpaid call → 402 challenge; paid call → 200 + a
tamper-evident receipt header; 5th call → 402 quota exceeded; /panel shows
who paid what, with a live hash-chain integrity badge.

The design constraint I held myself to: every failure path denies spend.
Corrupt policy file → ALL spending stops (not per-request errors). Unknown
payment scheme → 402, never a free pass. Tampered evidence bundle → loud
red in verification, never a receipt. The suite pins each of these with a
named test — happy to walk through any of them.

Four agent-commerce protocols (x402, AP2, ACP, UCP) compile onto one
wire-format core, so a fifth protocol is one adapter file, not a rewrite.
Receipts are hash-chained; anyone can verify a bundle with nothing but
sha256 (no Sester install) — that's the part I'd most like feedback on.

Repo: https://github.com/goun7/Sester
PyPI: https://pypi.org/project/sester/

Known limits (deliberate, documented): no transaction signing (non-custodial),
no certified PSP rails yet, CLI surface minimal.

Ask: try to break the fail-closed paths. If you find a silent-fallback, it's
a security bug by definition and I'll pin it with a test the same day.
