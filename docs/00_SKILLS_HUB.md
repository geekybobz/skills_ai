# Skills Hub

Global router. Read this, pick **one** registry file, read it, load the skill.
Two registry reads before any skill. Never more.

## Route

| task looks like | read |
|---|---|
| poster, A0, HTML page, layout, spacing, hierarchy, colour, dark mode, type, brand, motion, chart, table, print, PDF | [[registry/design]] |
| form, nav, search, error state, onboarding, loading, drag, chat UI, a11y, mobile, i18n, saas, ecommerce, checkout, landing, auth UX, healthcare | [[registry/ui-patterns]] |
| install, node, `.env`, secret, database, supabase, deploy, vercel, domain, build error, explain this code | [[registry/build-ops]] |
| be brief, fewer tokens, caveman, formula first, less story, mathematical derivation, compress memory, commit message, review diff, delegate to subagent | [[registry/compression]] |
| LaTeX, theory notes, math reference, chapter plan, outline, refresher | [[registry/theory]] |

## Rules

1. Read exactly one registry file. Not two, not all.
2. Name the chosen skill and why, then load it. One or two skill files maximum.
3. **No row matches → say "no skill here covers this" and stop. Never invent a skill name.**
4. Two rows match → read [[03_COMBO_MAP]] before loading anything.
5. About to write files, run scripts, or overwrite → read [[04_RISK_MAP]] first.
6. Never load a whole family. The design family alone is ~30k tokens.

## Layers

[[05_COLOR_LAYERS]] — graph colour model.
L0 entry · L1 global · L2 registry · L3 cards · L4 skills · L5 support.

## Do Not

- Do not preload a family "to see what's there". The registry is the answer to that question.
- Do not route through packaged duplicates in `caveman/plugins/`, `.agents/`, `.roo/`, `.kiro/`, `.junie/`. Canonical caveman skills are `caveman/skills/*` only.
- Do not modify skill files unless the user explicitly asks.
