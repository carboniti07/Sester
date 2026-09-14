# Dogfood plan — F1 fleet as Sester's first real tenant

> The highest-leverage growth move is not more code: it is one real user.
> The best candidate is our own F1 telemetry/agent fleet — external proof
> beats any landing page.

## Why dogfood first

- Real traffic → real failure-paths → public fixes (each one a credibility post).
- The S1 acceptance run already models this: `scripts/s1_dogfood.py`
  charges a fleet-agent against a daily band; moving it from test-harness to
  running service is mostly packaging.
- Content flywheel: every dogfood incident becomes a "we hit X, here's the
  fail-closed behavior, here's the pinned test" post — exactly the
  material HN/Reddit/dev.to audiences reward.

## Plan (2-week shape, no approval needed to start)

1. **Day 1–2 — productionize the demo into the fleet lane.** Run the demo
   middleware in front of one real internal endpoint; agents authenticate
   with per-agent HMAC secrets; policy: host allow-list + office-hours.
2. **Day 3–4 — quota tuning on real usage.** Pick daily_max from observed
   p95; enable burst caps; wire `/metrics` into an internal dashboard.
3. **Week 2 — receipts as the invoice.** Nightly evidence-bundle export →
   verify externally (bridge_receivers mirrors) → post the verified bundle
   hash in the team channel. This is the public "we eat our own receipts"
   screenshot.
4. **Continuous — incident loop.** Any denial/spike → root-cause → either a
   pinned test or a doc line. Monthly: a short "dogfood report" in
   Discussions → Show and tell.

## Success metric

Not stars: **one external project adopting the middleware** (even a hobby
bot). Everything in the launch-kit funnels toward that; dogfood is what makes
the claim credible when they ask "does this survive real traffic?".
