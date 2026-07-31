# Skills AI

Obsidian vault and routing registry for 51 local skills across three collections.
Skill files are never modified — the registry only points at them.

## Start

- Agent entry: [[docs/SKILLS|SKILLS]] → [[docs/00_SKILLS_HUB|00_SKILLS_HUB]]
- Graph colours: [[docs/05_COLOR_LAYERS|05_COLOR_LAYERS]]
- Proposed interaction protocol: [[docs/TODO_INTERACTION_PROTOCOL_PLAN|TODO_INTERACTION_PROTOCOL_PLAN]]

## How it routes

```text
docs/00_SKILLS_HUB     global router, one table
  -> registry/<family> one file per family: skills, triggers, "not for"
    -> the skill file  design-with-claude/*.md | caveman/skills/*/SKILL.md | theory-reference/
```

Two registry reads before any skill — 780-1,150 tokens depending on family.
Conditional side-reads: [[docs/03_COMBO_MAP|03_COMBO_MAP]] when a task spans
families, [[docs/04_RISK_MAP|04_RISK_MAP]] before anything that writes.

## Families

| registry | skills | 2-read cost | source |
|---|---|---|---|
| [[registry/design]] | 17 | ~1,150 tok | `design-with-claude/` |
| [[registry/ui-patterns]] | 18 | ~1,100 tok | `design-with-claude/` |
| [[registry/build-ops]] | 7 | ~780 tok | `design-with-claude/` |
| [[registry/compression]] | 8 | ~850 tok | `caveman/skills/` |
| [[registry/theory]] | 1 (3 phases) | ~785 tok | `theory-reference/` submodule |

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

- `docs/` — routing hub, combo map, risk map, graph layer notes, proposed interaction-protocol plan
- `design-with-claude/` — 42 flat skill files, vendored, no upstream
- `caveman/` — vendored product repo from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman); canonical behavior lives in `skills/`, while manifests, tests, and distributions remain tracked for reproducibility
- `theory-reference/` — submodule, [geekybobz/theory-reference](https://github.com/geekybobz/theory-reference)
