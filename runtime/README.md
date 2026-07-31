# Shared Runtime

Platform-neutral hot path for Skills AI.

```text
human registry sources
  -> scripts/compile_registry.py
  -> router-manifest.json
  -> scripts/route_skill.py
  -> MATCH(one skill) | NORMAL(fail-open)
  -> thin Codex or Claude adapter
```

Shared components:

- `profile.json`: compact professional response contract.
- `router-manifest.json`: generated activation and routing data.
- `SKILL.md`: compact entry contract usable by platform adapters.
- `scripts/registry_runtime.py`: compilation, deterministic selection, and
  structured context assembly.

Platform code stays in `adapters/`. Adapters may translate lifecycle events and
install locations, but must not duplicate route rules, profile rules, or skill
selection logic.

No-match, disabled, hidden, deprecated, and ambiguous decisions are fail-open:
the task continues normally without a local skill. Skill selection never grants
permission to write files, use credentials, access networks, or change accounts.
