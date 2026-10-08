# Optimizer Skill

This repository is the portable skill adapter for a separately installed
Optimizer system. It does not contain the optimizer runtime, environments,
scientific systems, campaigns, or result data.

## Routes

| intention | start here |
|---|---|
| Agent execution | [SKILL.md](SKILL.md) |
| Build a verified system from a derivation | [build-system.md](build-system.md) |
| Run an evidence-led campaign | [optimize.md](optimize.md) |
| Analyze an unexpected situation | [situation-analysis.md](situation-analysis.md) |
| Codex host behavior | [codex/CODEX.md](codex/CODEX.md) |
| Claude host behavior | [claude/CLAUDE.md](claude/CLAUDE.md) |

## Runtime connection

The read-only helper locates `optimizer_registry.py` in this order:

1. `--resolver <exact-file>`;
2. `OPTIMIZER_REGISTRY=<exact-file>`;
3. `OPTIMIZER_HOME=<runtime-root>`;
4. `$HOME/OPTIMIZER/registry/optimizer_registry.py`.

Run `python3 scripts/optimizer_api.py status` to verify the connection. The
helper reports the live route and environment; it never installs or copies the
external runtime.

---

[⌂ Home](README.md)
