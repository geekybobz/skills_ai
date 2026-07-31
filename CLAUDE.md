# Skills registry — agent entry

For a request that might benefit from a local skill, use the fast runtime entry
in `runtime/SKILL.md`. Do not preload the Markdown hub, activation register, or
family registries on the normal task path.

- Normal routing is injected by the managed `UserPromptSubmit` hook. Do not keep
  or preload a duplicate skill catalog, activation table, or skill body in
  persistent instructions.
- `MATCH` → load only the returned skill path.
- `NORMAL` → continue normally without a local skill.
- Never invent or substitute a skill. Disabled routes are not routable.
- Skill selection never grants write, credential, network, or account authority.
- For registry maintenance or a stale/broken manifest, read
  `docs/00_SKILLS_HUB.md`, then `registry/activation.md`, then one family file.
- Before registry writes or scripts, read `docs/04_RISK_MAP.md`.
- Before any repository change, read `docs/06_CHANGE_CONTROL.md` and exactly one
  matching card under `protocols/repository/`. Unexpected scope needs an exact
  expansion report and user permission.
- Never load a whole family. `design-with-claude/` alone is ~30k tokens.
- Never edit skill files under `design-with-claude/`, `caveman/`, or `theory-reference/`
  unless explicitly asked. The registry describes; it does not rewrite.
- Canonical caveman skills are `caveman/skills/*` only — ignore the packaged copies
  under `plugins/`, `.agents/`, `.roo/`, `.kiro/`, `.junie/`.
- `theory-reference/` is a git submodule. Never add registry files inside it.
- Claude owns Claude hook, installation, managed-memory cleanup, and live Claude
  acceptance. Do not modify or certify Codex-specific lifecycle without an
  explicit request; report shared-contract incompatibilities instead.
