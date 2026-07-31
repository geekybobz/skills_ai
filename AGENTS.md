# Skills registry — agent entry

`README.md` and `docs/human/` are human-facing explanations. Do not read them
during normal routing or task work; use them only when the user explicitly asks
about the human guide or when synchronizing it after a relevant approved change.

For a request that might benefit from a local skill, use the fast runtime entry
in `runtime/SKILL.md`. Do not preload the Markdown hub, activation register, or
family registries on the normal task path.

- Send one newline-terminated JSON request to `scripts/route_skill.py`; it must
  exit after one response without waiting for EOF.
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
- If this task's initial workspace is outside `/Users/billabobz/skills_ai`,
  treat this repository as read-only. Even an explicit Skills AI change request
  may only create one new packet through `scripts/create_change_request.py`,
  then hand off to a dedicated maintenance task rooted here. Read
  `protocols/repository/EXTERNAL_CHANGE_REQUEST.md`.
- Never load a whole family. `design-with-claude/` alone is ~30k tokens.
- Never edit skill files under `design-with-claude/`, `interaction-protocol/`, or `theory-reference/`
  unless explicitly asked. The registry describes; it does not rewrite.
- Interaction protocols shape the response context and do not consume the one
  selected task-skill slot.
- `theory-reference/` is a git submodule. Never add registry files inside it.
- Codex owns Codex-specific invocation and session cleanup. Claude-specific live
  acceptance belongs to Claude; shared runtime behavior belongs in `runtime/`.
