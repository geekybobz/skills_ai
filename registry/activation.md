# Activation Register

Read this after [[docs/00_SKILLS_HUB]] and before any family registry. It is the
switchboard for families, skills, and large-skill components.

## State Rules

| state | route behavior | use |
|---|---|---|
| `active` | wikilink route, may be selected by trigger | normal routing |
| `manual` | wikilink route, explicit user request only | optional tools and narrow modes |
| `off` | plain code path, do not route | disabled but visible |
| `hidden` | plain code path, do not route or surface | parked work |
| `deprecated` | plain code path, do not route | kept for history |

If a row is `off`, `hidden`, or `deprecated`, its route cell must be a
backticked path, not an Obsidian wikilink. This keeps the graph honest:
enabled routes are linked; disabled routes are visible but unlinked.

## Family Gates

| id | state | route | scope |
|---|---|---|---|
| design | active | [[registry/design\|design]] | visual, layout, color, typography, print |
| ui-patterns | active | [[registry/ui-patterns\|ui-patterns]] | forms, navigation, search, product UX |
| build-ops | active | [[registry/build-ops\|build-ops]] | setup, deploy, auth code, debugging |
| interaction | active | [[registry/interaction\|interaction]] | compact general responses and equation-led mathematical reasoning |
| theory | active | [[registry/theory\|theory]] | LaTeX theory reference and math notes |
| research | active | [[registry/research\|research]] | early project orientation, evidence, applications and paper direction |
| career | off | `registry/career.md` | career radar and job-search workflows |

## Skill Gates

| id | state | route | trigger boundary |
|---|---|---|---|
| research-context-scout | manual | [[research-context-scout/SKILL\|research-context-scout]] | exact skill request, `#> scout`, or `#> scout-again` only |
| quantum-job-collector | off | `external-skills/quantum-job-collector/SKILL.md` | exhaustive Quantum Career Radar job collection |

## Interaction Protocol Components

| id | state | route | effect |
|---|---|---|---|
| interaction.general | active | [[registry/interaction\|interaction.general]] | direct result plus adequate polished context on every request |
| interaction.math | active | [[registry/interaction\|interaction.math]] | automatic equation-led reasoning; `manual` requires an explicit math control |

## Quantum Job Collector Components

| id | state | route | effect |
|---|---|---|---|
| quantum-job-collector.full-run | off | `external-skills/quantum-job-collector/SKILL.md` | exhaustive all-tier run |
| quantum-job-collector.tier1-structured | off | `external-skills/quantum-job-collector/SKILL.md` | Greenhouse, Lever, Teamtailor structured pass |
| quantum-job-collector.unresolved-retry | off | `external-skills/quantum-job-collector/SKILL.md` | retry unresolved sources only |
| quantum-job-collector.source-evidence | off | `external-skills/quantum-job-collector/SKILL.md` | persist source result records and evidence |
| quantum-job-collector.append-pending | off | `external-skills/quantum-job-collector/SKILL.md` | write new jobs into pending queue |
| quantum-job-collector.browser-fallback | off | `external-skills/quantum-job-collector/SKILL.md` | use browser or JS fallback |
| quantum-job-collector.paid-fallback | off | `external-skills/quantum-job-collector/SKILL.md` | paid or remote fallback tools |
| quantum-job-collector.cron | off | `external-skills/quantum-job-collector/SKILL.md` | scheduled automation |

## Toggle

Use the script instead of hand-editing route cells:

```bash
python3 scripts/toggle_registry.py active interaction.general
python3 scripts/toggle_registry.py manual interaction.math
python3 scripts/toggle_registry.py off interaction.math
python3 scripts/toggle_registry.py --check
```

The script atomically updates the state, converts route cells between wikilinks
and plain paths, checks target files, rejects duplicate ids, refuses to activate
a component when its parent skill is off, and recompiles the runtime manifest.
Use `--dry-run` or `--json` for preview and machine-readable control.
