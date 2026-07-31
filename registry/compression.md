# Compression Registry

Token-saving output modes, formula-first mathematics, compressed commit/review
text, and subagent delegation. Check [[registry/activation]] before loading any
row here.

Canonical skill sources are under `caveman/skills/*`. Packaged mirrors remain
tracked for installation but are hidden from Obsidian and never used for routing.

## Skills

| skill | does | trigger | not for |
|---|---|---|---|
| [[caveman/skills/caveman/SKILL\|caveman]] | persistent terse response mode, ~75% fewer output tokens; levels: lite, full, ultra, wenyan-* | be brief, fewer tokens, caveman mode, terse | compressing a *file* → `caveman-compress` |
| [[caveman/skills/caveman-math/SKILL\|caveman-math]] | formula-first mathematical pedagogy with local symbols, LaTeX derivation, insight, and optional verification | formula first, less story, derive mathematically, `/caveman math` | generic short prose → `caveman` |
| [[caveman/skills/caveman-compress/SKILL\|caveman-compress]] | compress a prose/memory file in place, backup to `FILE.original.md` | compress memory, `/caveman-compress FILE`, shrink CLAUDE.md | changing reply style → `caveman` |
| [[caveman/skills/caveman-commit/SKILL\|caveman-commit]] | Conventional Commits, subject ≤50 chars, body only when "why" is unclear | write commit, commit message | running `git commit` — it only drafts |
| [[caveman/skills/caveman-review/SKILL\|caveman-review]] | one line per finding: location, problem, fix | review this, code review, review diff | editing the code |
| [[caveman/skills/cavecrew/SKILL\|cavecrew]] | when to spawn compressed subagents (investigator / builder / reviewer) | delegate, subagent, save context, spawn | doing the work inline |
| [[caveman/skills/caveman-help/SKILL\|caveman-help]] | one-shot reference card for caveman modes and commands | caveman help, what caveman commands | activating a mode |
| [[caveman/skills/caveman-stats/SKILL\|caveman-stats]] | token usage and savings, supplied by a hook | token stats, `/caveman-stats` | model-side estimation — it does not compute |

## Components

Large skills can expose toggled components in [[registry/activation]]. For
`caveman`, current active components are base style, no-AI-trace hygiene,
answer-first structure, equation rendering, pedagogy, safety clarity, and code
preservation. Manual components include wenyan and statusline stats.

## Risk

`caveman-compress` **overwrites the target file** after writing a backup.
Confirm the path, never point it at secrets or at an existing `.original.md`.
See [[04_RISK_MAP]].

## Combines with

`caveman` stacks on top of any other family — activate the mode, then route
normally. See [[03_COMBO_MAP]].

## Rules

- Load one skill.
- Nothing above fits → say so. Do not substitute the nearest-sounding skill.
- Path: `caveman/skills/<skill>/SKILL.md`
