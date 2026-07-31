# Risk Map

Read before anything that writes files, runs scripts, touches credentials, or
takes account/network actions.

Back: [[00_SKILLS_HUB]] · Combos: [[03_COMBO_MAP]] · Layers: [[05_COLOR_LAYERS]]

## Risk table

| skill or family | risk | rule |
|---|---|---|
| [[registry/design]], [[registry/ui-patterns]] | guidance only by default | write files only when the user asks to build or edit |
| `poster-lead` | leads to generated HTML/CSS/PDF | propose the layout first; build only after the user picks one |
| `auth-implementation` | writes real auth code into a project | inspect the stack first; ask only if the provider is genuinely ambiguous |
| `database-setup` | creates database and client code | never echo keys; keep credentials in `.env`, never in committed files |
| `deploy-to-vercel` | account actions, network installs, live deploys | explicit approval before any external write or deploy |
| `environment-setup` | handles secrets by definition | never print real key values; never commit `.env` |
| `interaction.general` | response structure only | no file writes; adequate context is preserved rather than mechanically compressed |
| `interaction.math` | equation-led response structure only | no file writes; analytic reasoning precedes optional requested code |
| `registry/activation` toggle | rewrites routing state and Obsidian links | use `python3 scripts/toggle_registry.py --check` after changes |
| registry runtime compile | atomically rewrites `runtime/router-manifest.json` | compile after registry changes, then run validator and router tests |
| runtime adapter install | writes under `~/.codex/skills/` or Claude skills/hooks/settings | dry-run first; preserve foreign Claude settings and write a settings backup |
| repository change control | add/edit/update/delete can cross source, generated, submodule, or external boundaries | read [[06_CHANGE_CONTROL]] and one operation card; expansion and protocol amendments need explicit approval |
| external Skills AI change request | writes one Markdown intake packet | only `scripts/create_change_request.py`; target `requests/pending/`; no canonical edit, staging, commit, or launch from the external task |
| `career` | parked external workflow | keep off until the family is reworked |
| `quantum-job-collector` | network search plus writes under Quantum Career Radar `app/data/` | append via helper only; no browser, paid fallback, or cron unless the matching component is enabled |
| `theory-reference` planning | writes plan + outlines after approval | no LaTeX during planning |
| `theory-reference` chapter build | writes chapter LaTeX after approval | load rules and templates first |
| `theory-reference` evaluate | edits approved outlines only | no LaTeX, no plan reorder without explicit sign-off |

## Repo-level

| action | rule |
|---|---|
| editing any skill file | not without an explicit request — the registry describes, it does not rewrite |
| adding files under `theory-reference/` | it is a submodule; registry files belong in `registry/` instead |
| editing `interaction-protocol/` | update the shared contract, router tests, API docs, and mapped human guide together |
| staging or committing | run `scripts/change_guard.py check-staged` with declared paths; never mix unrelated dirty work |
