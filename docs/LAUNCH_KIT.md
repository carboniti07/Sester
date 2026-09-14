# SESTER Launch Kit — visibility playbook (2026-09-14)

> Goal: first real users. Every asset below is copy-paste ready, with the
> single fact each channel cares about. Post order matters — see §Order.
>
> ⚠️ **Precondition:** the repo is still **private**. HN/Reddit/PH links to a
> 404 kill credibility. Flip public **before** posting (checklist below), or
> post PyPI/GitPages links only.

## Preconditions checklist (do before any post)

- [ ] Repo public: `gh repo edit goun7/Sester --visibility public --accept-visibility-change-consequences`
- [ ] Sweep green on the public tree: `python scripts/public_surface_sweep.py --repo .` (internal org-names = 0)
- [ ] Docker image public: GHCR package → Settings → change visibility to public (after first `docker.yml` run on a tag)
- [ ] Social preview set (console): Settings → Social preview → `.github/assets/og.png`
- [ ] Landing live: <https://goun7.github.io/Sester/>
- [ ] Discussions open (already `true`) with the 4 categories from `docs/DISCUSSION_SETUP.md`

## Assets in this kit

| File | Channel | Lead fact |
|---|---|---|
| `launch/SHOW_HN.md` | Hacker News | "one ASGI middleware; every failure path denies spend" |
| `launch/REDDIT.md` | r/Python · r/MachineLearning · r/selfhosted (3 tailored posts) | zero-dep engineering / agent-economy / self-host panel |
| `launch/DEVTO_ARTICLE.md` | dev.to (canonical long-form) | protocol→core compile story + code walkthrough |
| `launch/X_THREAD.md` | X/Twitter (7-tweet thread) | the 402→receipt flow in 7 beats |
| `launch/PRODUCT_HUNT.md` | Product Hunt | tagline + first-comment + maker-comment |
| `launch/LINKEDIN.md` | LinkedIn (founder/eng voice) | fintech-grade auditability angle (TR+EN) |
| `launch/X402_LISTING.md` | x402 ecosystem listings + MCP-registry submission | what to submit, where, with which copy |

## Order (highest-signal-per-effort first)

1. **Public flip + sweep + Docker-public** (preconditions above) — ~20 min
2. **Show HN** on a Tue–Thu, 07:00–09:00 US-East; first comment = `SHOW_HN.md` body
3. Same day: **r/Python** (engineering post), **X thread** (same assets)
4. Day 2: **dev.to article** (canonical; link it from HN follow-ups and X)
5. Day 3–7: **Product Hunt** (Tue–Thu), **LinkedIn**, then **x402 listings + MCP registry** (once public, these are the evergreen inbound)
6. Ongoing: `docs/DOGFOOD_PLAN.md` — F1 fleet as first real tenant (dogfood = first customer)

## Response doctrine (all channels)

- Every failure-path question gets answered with a **test name**, not adjectives.
- "Why not X?" → feature-map table + deliberate-v0-limits; no roadmap-promises.
- Bugs found during launch → issue + fix + CHANGELOG within the day; each fix
  is public proof of the fail-closed discipline.
- Never argue licensing/monetization publicly — one line: "open-core Apache-2.0;
  hosted facilitator is the commercial lane."
