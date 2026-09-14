# X/Twitter thread — 7 tweets (post as one thread; attach OG image to #1)

**1/**
AI agents can now pay per API call (x402-style). But who meters it, limits it,
and PROVES what was spent?

We built Sester: one ASGI middleware that does all three. Zero required deps.
🧵 [og.png]

**2/**
The flow: unpaid call → 402 challenge. Paid call → 200 + a tamper-evident
receipt header. Quota exhausted → 402. Every event lands in a hash-chained
ledger anyone can verify with plain sha256. No Sester install needed to audit.

**3/**
The doctrine: every failure path DENIES SPEND.
Corrupt policy file → ALL spending stops.
Unknown scheme → 402, never a free pass.
Tampered evidence → loud red, never a receipt.
Each is a named test. Find a silent fallback = it's a security bug.

**4/**
Four agent-commerce protocols — x402, AP2, ACP, UCP — compile onto one
wire-format core. A fifth protocol is one adapter file, not a rewrite.

**5/**
Try it in 60 seconds:
docker run --rm -p 8402:8402 ghcr.io/goun7/sester-demo:latest
then open /panel — who called, how much, chain intact?
or: pip install "sester[demo]" && uvicorn sester.demo_api:app --port 8402

**6/**
Deliberate limits (documented, not hidden): no transaction signing
(non-custodial), no certified PSP rails yet. What IS there: metering,
quota, burst caps, human-approval escalation, verifiable evidence.

**7/**
Repo: github.com/goun7/Sester
PyPI: pypi.org/project/sester
Breaking the fail-closed paths is the most useful thing you can do today.
