# Skills AI

Obsidian vault and routing registry for 52 tracked skill entries across four collections.
Skill files are never modified — the registry only points at them.

## Start

- Agent entry: [[docs/SKILLS|SKILLS]] → [[docs/00_SKILLS_HUB|00_SKILLS_HUB]]
- Fast runtime entry: `runtime/SKILL.md` → compiled manifest → one skill or `NORMAL`
- Graph colours: [[docs/05_COLOR_LAYERS|05_COLOR_LAYERS]]
- Change control: [[docs/06_CHANGE_CONTROL|06_CHANGE_CONTROL]]
- Build and release: [[docs/07_BUILD_AND_RELEASE|07_BUILD_AND_RELEASE]]
- Runtime protocol/API: [[runtime/PROTOCOL|PROTOCOL]] · [[runtime/API_CONTRACT|API_CONTRACT]]
- Claude verification: [[docs/CLAUDE_VERIFICATION_PROMPT|CLAUDE_VERIFICATION_PROMPT]]
- Legacy graph cards: [[cards/legacy/quantum-job-collector|quantum-job-collector]]
- Proposed interaction protocol: [[docs/TODO_INTERACTION_PROTOCOL_PLAN|TODO_INTERACTION_PROTOCOL_PLAN]]

## How it routes

```text
docs/00_SKILLS_HUB     global router, one table
  -> registry/activation active/manual/off switchboard
  -> registry/<family> one file per family: skills, triggers, "not for"
    -> the skill file  design-with-claude/*.md | caveman/skills/*/SKILL.md | theory-reference/ | external-skills/
```

Activation keeps disabled skills as plain paths and active skills as wikilinks,
so the Obsidian graph reflects what is routable.
Conditional side-reads: [[docs/03_COMBO_MAP|03_COMBO_MAP]] when a task spans
families, [[docs/04_RISK_MAP|04_RISK_MAP]] before anything that writes.

For fast runtime selection, `scripts/compile_registry.py` converts the human
registry into `runtime/router-manifest.json`. The platform-neutral
`scripts/route_skill.py` then returns one active skill or a fail-open `NORMAL`
decision with a compact, structured response context. Thin adapters give Codex
and Claude access to the same router, profile, manifest, and skill sources. No
match, disabled routes, and ambiguous matches continue with normal behavior.

## Families

| registry | skills | 2-read cost | source |
|---|---|---|---|
| [[registry/activation]] | gates | first pass | all families |
| [[registry/design]] | 17 | ~1,150 tok | `design-with-claude/` |
| [[registry/ui-patterns]] | 18 | ~1,100 tok | `design-with-claude/` |
| [[registry/build-ops]] | 7 | ~780 tok | `design-with-claude/` |
| [[registry/compression]] | 8 | ~850 tok | `caveman/skills/` |
| [[registry/theory]] | 1 (3 phases) | ~785 tok | `theory-reference/` submodule |
| `registry/career.md` | 1 parked | off | external Quantum Career Radar skill |

All 42 `design-with-claude` skills are routed — none orphaned. Every entry carries
a **`not for`** column, which is what stops near-miss routing (`color-specialist`
when the task was dark mode).

## Principle

The registry **describes**; it does not **inhabit**. No registry file lives inside
a skill collection — that is what lets `theory-reference` stay a clean submodule
and lets any collection be swapped without touching routing.

Registry files carry routing metadata only: what the task looks like, which skill
to load, what it is *not* for, and what write risk it carries. Never skill content.

## Repo layout

- `docs/` — routing, risk, change-control, build, graph, and interaction-protocol notes
- `protocols/repository/` — one-card procedures for add/edit/update/delete and scope control
- `registry/activation.md` — active/manual/off switchboard for families, skills, and components
- `cards/` — graph-visible cards for parked or legacy skills, without routing authority
- `scripts/toggle_registry.py` — validates and toggles activation rows
- `scripts/compile_registry.py` — atomically compiles the runtime manifest
- `scripts/route_skill.py` — returns one skill or normal fallback
- `scripts/validate_registry.py` — checks source and manifest consistency
- `scripts/benchmark_router.py` — measures route accuracy, latency, and context size
- `scripts/install_runtime_adapter.py` — installs thin Codex or Claude adapters
- `scripts/change_guard.py` — reports protected, external, generated, or out-of-scope changes
- `adapters/` — platform-specific access over the shared runtime core
- `runtime/` — shared entry, compact response profile, and generated router manifest
- `tests/` — deterministic routing cases and standard-library unit tests
- `external-skills/` — controlled pointers to skills whose source lives outside this vault
- `design-with-claude/` — 42 flat skill files, vendored, no upstream
- `caveman/` — vendored product repo from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman); canonical behavior lives in `skills/`, while manifests, tests, and distributions remain tracked for reproducibility
- `theory-reference/` — submodule, [geekybobz/theory-reference](https://github.com/geekybobz/theory-reference)
