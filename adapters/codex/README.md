# Codex Adapter

Codex uses the shared `runtime/SKILL.md` as its compact entry skill. The entry
calls the same Python router used by every adapter and loads only a returned
skill path.

Install or verify:

```bash
python3 scripts/install_runtime_adapter.py --adapter codex --dry-run
python3 scripts/install_runtime_adapter.py --adapter codex
python3 scripts/install_runtime_adapter.py --adapter codex --check
```

The default target is `~/.codex/skills/skills-ai-registry/SKILL.md`. Use
`--config-dir` for an alternate Codex configuration directory.
