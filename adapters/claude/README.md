# Claude Adapter

Thin `UserPromptSubmit` adapter over the shared Python router. It receives the
Claude prompt, asks the shared runtime for `MATCH` or `NORMAL`, and injects the
compact response context plus only the selected skill body.

Install or verify:

```bash
python3 scripts/install_runtime_adapter.py --adapter claude --dry-run
python3 scripts/install_runtime_adapter.py --adapter claude
python3 scripts/install_runtime_adapter.py --adapter claude --check
```

The installer:

- copies the shared `runtime/SKILL.md` into the Claude skills directory;
- copies `skills-ai-router.js` into the Claude hooks directory;
- preserves foreign settings while adding one managed `UserPromptSubmit` hook;
- backs up `settings.json` before changing it; and
- supports `CLAUDE_CONFIG_DIR` or `--config-dir`.

This repository tests the hook protocol and shared routing core. A live Claude
session test remains a Claude-side acceptance step.
