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
| compression | active | [[registry/compression\|compression]] | terse output, Caveman, review, commit |
| theory | active | [[registry/theory\|theory]] | LaTeX theory reference and math notes |
| career | off | `registry/career.md` | career radar and job-search workflows |

## Skill Gates

| id | state | route | trigger boundary |
|---|---|---|---|
| caveman | active | [[caveman/skills/caveman/SKILL\|caveman]] | terse response mode |
| caveman-math | active | [[caveman/skills/caveman-math/SKILL\|caveman-math]] | formula-first mathematical pedagogy |
| caveman-compress | manual | [[caveman/skills/caveman-compress/SKILL\|caveman-compress]] | explicit file compression only |
| caveman-commit | manual | [[caveman/skills/caveman-commit/SKILL\|caveman-commit]] | commit message drafting |
| caveman-review | manual | [[caveman/skills/caveman-review/SKILL\|caveman-review]] | review output only |
| cavecrew | manual | [[caveman/skills/cavecrew/SKILL\|cavecrew]] | explicit delegation or subagent request |
| caveman-help | manual | [[caveman/skills/caveman-help/SKILL\|caveman-help]] | help card |
| caveman-stats | manual | [[caveman/skills/caveman-stats/SKILL\|caveman-stats]] | hook-provided token stats |
| quantum-job-collector | off | `external-skills/quantum-job-collector/SKILL.md` | exhaustive Quantum Career Radar job collection |

## Caveman Components

| id | state | route | effect |
|---|---|---|---|
| caveman.base-style | active | [[caveman/skills/caveman/SKILL\|caveman]] | terse output, preserve technical content |
| caveman.no-ai-traces | active | [[caveman/skills/caveman/SKILL\|caveman]] | no em dashes, no assistant openers, no filler transitions |
| caveman.answer-first | active | [[caveman/skills/caveman/SKILL\|caveman]] | start with answer, finding, equation, or action |
| caveman.equation-rendering | active | [[caveman/skills/caveman-math/SKILL\|caveman-math]] | rendered LaTeX display math for central equations |
| caveman.pedagogy | active | [[caveman/skills/caveman-math/SKILL\|caveman-math]] | setup, derivation, insight, boundary |
| caveman.safety-clarity | active | [[caveman/skills/caveman/SKILL\|caveman]] | normal prose for security and irreversible actions |
| caveman.code-preservation | active | [[caveman/skills/caveman/SKILL\|caveman]] | preserve code, commands, paths, URLs, errors |
| caveman.wenyan | manual | [[caveman/skills/caveman/SKILL\|caveman]] | classical Chinese compression levels |
| caveman.statusline-stats | manual | [[caveman/skills/caveman-stats/SKILL\|caveman-stats]] | statusline savings display |

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
python3 scripts/toggle_registry.py active caveman.no-ai-traces
python3 scripts/toggle_registry.py off caveman.statusline-stats
python3 scripts/toggle_registry.py manual cavecrew
python3 scripts/toggle_registry.py --check
```

The script atomically updates the state, converts route cells between wikilinks
and plain paths, checks target files, rejects duplicate ids, refuses to activate
a component when its parent skill is off, and recompiles the runtime manifest.
Use `--dry-run` or `--json` for preview and machine-readable control.
