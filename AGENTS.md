# Skills registry — agent entry

For a request that might benefit from a local skill, use the fast runtime entry
in `runtime/SKILL.md`. Do not preload the Markdown hub, activation register, or
family registries on the normal task path.

- Send the request to `scripts/route_skill.py` as JSON on stdin.
- `MATCH` → load only the returned skill path.
- `NORMAL` → continue normally without a local skill.
- Never invent or substitute a skill. Disabled routes are not routable.
- Skill selection never grants write, credential, network, or account authority.
- For registry maintenance or a stale/broken manifest, read
  `docs/00_SKILLS_HUB.md`, then `registry/activation.md`, then one family file.
- Before registry writes or scripts, read `docs/04_RISK_MAP.md`.
- Never load a whole family. `design-with-claude/` alone is ~30k tokens.
- Never edit skill files under `design-with-claude/`, `caveman/`, or `theory-reference/`
  unless explicitly asked. The registry describes; it does not rewrite.
- Canonical caveman skills are `caveman/skills/*` only — ignore the packaged copies
  under `plugins/`, `.agents/`, `.roo/`, `.kiro/`, `.junie/`.
- `theory-reference/` is a git submodule. Never add registry files inside it.
