# Skills registry — agent entry

Before answering anything that might match a local skill, read `docs/00_SKILLS_HUB.md`.

Route: hub → **one** file in `registry/` → the skill file. Two registry reads, then stop.

- No route matches → say "no skill here covers this". Never invent a skill name.
- Task spans two families → `docs/03_COMBO_MAP.md` first.
- About to write files, run scripts, or touch credentials → `docs/04_RISK_MAP.md` first.
- Never load a whole family. `design-with-claude/` alone is ~30k tokens.
- Never edit skill files under `design-with-claude/`, `caveman/`, or `theory-reference/`
  unless explicitly asked. The registry describes; it does not rewrite.
- Canonical caveman skills are `caveman/skills/*` only — ignore the packaged copies
  under `plugins/`, `.agents/`, `.roo/`, `.kiro/`, `.junie/`.
- `theory-reference/` is a git submodule. Never add registry files inside it.
