# Discussions setup — categories ↔ Sester mapping

Defaults are already enabled (`has_discussions=true`); GitHub ships 6 default
categories. Recommended usage mapping (no renames needed — just post in the
right one and pin this doc as the index):

| Default category | Sester use |
|---|---|
| **Announcements** | Release notes per version (start: v0.5.0, v0.6.0 threads linking `docs/RELEASE_NOTES/*`) |
| **Q&A** | Integration questions (FastAPI/Starlette wiring, policy DSL, facilitator transport) |
| **Ideas** | Roadmap input (PSP adapters, protocol #5, hosted-traffic) — triaged into the roadmap doc |
| **Show and tell** | Community integrations ("I metered my agent API with Sester") |
| **General** | Everything else; off-topic drifts here first |
| **Polls** | Occasionally: next-protocol priorities |

## Seed threads (create at public flip)

1. **Announcements** — "Sester v0.6.0 released" body = `docs/RELEASE_NOTES/0.6.0.md`
2. **Q&A** — "Getting help: read this first" — one ASGI example + link to README demo + SECURITY note (security issues → advisory, NOT discussion)
3. **Ideas** — "Roadmap candidates — vote with 👍" — list the ⏸ roadmap items (PSP rails, tx signing, hosted traffic, protocol #5)

## Maintenance rule

Launch-kit response doctrine applies here too: every failure-path question is
answered with a test name. Ideas get triaged weekly; accepted ones get a
roadmap row with acceptance criteria before any code.
