# Skills Hub

Human-readable routing authority and maintenance hub. Normal tasks use the
compiled entry at `runtime/SKILL.md`: the runtime returns one active skill or a
fail-open `NORMAL` result without loading this file into model context.

Shared response behavior: [[interaction-protocol/README|Interaction Protocol]].

When maintaining or auditing the registry, check [[registry/activation]], then
pick the enabled family registry and load the active skill or component.

## Route

| task looks like | if enabled in [[registry/activation]], read |
|---|---|
| poster, A0, HTML page, layout, spacing, hierarchy, colour, dark mode, type, brand, motion, chart, table, print, PDF | [[registry/design]] |
| form, nav, search, error state, onboarding, loading, drag, chat UI, a11y, mobile, i18n, saas, ecommerce, checkout, landing, auth UX, healthcare | [[registry/ui-patterns]] |
| install, node, `.env`, secret, database, supabase, deploy, vercel, domain, build error, explain this code | [[registry/build-ops]] |
| concise answer, direct context, equation-led reasoning, mathematical derivation, math first | [[registry/interaction]] |
| LaTeX, theory notes, math reference, chapter plan, outline, refresher | [[registry/theory]] |
| quantum jobs, career radar, update review queue, pending jobs, source coverage | `registry/career.md` (off in activation) |

## Rules

1. Read [[registry/activation]] first. If a matching family, skill, or component
   is `off`, `hidden`, or `deprecated`, do not route to it.
2. Read exactly one enabled family registry. Not two, not all.
3. Name the chosen active skill/component and why, then load it. One or two
   skill files maximum.
4. **No active row matches → load no local skill and continue normally. Never invent or substitute a skill.**
5. Two rows match → read [[03_COMBO_MAP]] before loading anything.
6. About to write files, run scripts, or overwrite → read [[04_RISK_MAP]] first.
7. Never load a whole family. The design family alone is ~30k tokens.

## Layers

[[05_COLOR_LAYERS]] — graph colour model.
L0 entry · L1 hubs and switchboards · L2 family registries · L3 cards · L4 skills · L5 support.

## Do Not

- Do not preload a family "to see what's there". The registry is the answer to that question.
- Interaction protocols shape responses and do not consume the one task-skill slot.
- Do not modify skill files unless the user explicitly asks.
