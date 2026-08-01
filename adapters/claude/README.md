# Claude Adapter

Thin `UserPromptSubmit` adapter over the shared Python router. It receives the
Claude prompt, asks the shared runtime for `MATCH` or `NORMAL`, and injects the
compact response context plus only the selected skill body.

The repository-level `CLAUDE.md` is generated from
`runtime/AGENT_ENTRY_SHARED.md` plus `adapters/claude/ENTRY.md`. The overlay owns
only Claude hook and child-lifecycle differences. Edit the canonical sources and
run `scripts/compile_repository_views.py`; do not keep a duplicate catalog or
shared rule set in Claude memory.

Install or verify:

```bash
python3 scripts/install_runtime_adapter.py --adapter claude --dry-run
python3 scripts/install_runtime_adapter.py --adapter claude
python3 scripts/install_runtime_adapter.py --adapter claude --check
```

The installer:

- copies `skills-ai-router.js` into the Claude hooks directory;
- preserves foreign settings while adding one managed `UserPromptSubmit` hook;
- removes an obsolete Claude bootstrap only when it is a byte-for-byte
  installer-managed copy of `runtime/SKILL.md`;
- preserves the first `settings.json.skills-ai.bak` snapshot and writes a
  separate `.previous` snapshot before later changed installs;
- refuses to replace symlinks or unrecognized foreign hook files; and
- supports `CLAUDE_CONFIG_DIR` or `--config-dir`.

The hook is the Claude bootstrap. It sends a newline-framed request to the
shared router, gives the Python child a 1-second deadline inside the 3-second
Claude hook deadline, suppresses child stderr, resolves selected skill paths
through real paths, and fails open with prompt-free diagnostics. Claude does
not own or certify Codex-specific invocation and terminal cleanup.

This repository tests the hook protocol and shared routing core. A live Claude
session test remains a Claude-side acceptance step.

For explicit registry-discovery questions, the hook injects active, manual, and
off route metadata from the current manifest without loading skill bodies. For
write requests targeting Skills AI itself, it injects the shared external-task
request-only boundary and maintenance workspace.
