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
shared router, suppresses child stderr, resolves selected skill paths through
real paths, and fails open with prompt-free diagnostics. Claude does not own or
certify Codex-specific invocation and terminal cleanup.

One budget covers the whole hook run: `SKILLS_AI_ADAPTER_TIMEOUT_MS`, default
2,500 ms, inside the `"timeout": 3` seconds the installer writes into Claude
settings. While the adapter waits for host input, a timer enforces that budget
and returns `ADAPTER_INPUT_TIMEOUT`. Once input ends, the blocking phases cannot
be interrupted by a timer, so the adapter enforces the same deadline by
arithmetic instead: the Python child receives whichever is smaller,
`SKILLS_AI_ROUTER_TIMEOUT_MS` (default 1,000 ms) or the budget left after a
250 ms reserve for reading one skill body and writing the reply. Slow host input
therefore shortens the child rather than overrunning the hook deadline. A
selected skill body over 1 MiB, or a run whose budget expires before the reply
is written, fails open with `ADAPTER_SKILL_TOO_LARGE` or
`ADAPTER_DEADLINE_EXCEEDED`.

This repository tests the hook protocol and shared routing core. A live Claude
session test remains a Claude-side acceptance step.

For explicit registry-discovery questions, the hook injects active, manual, and
off route metadata from the current manifest without loading skill bodies. For
write requests targeting Skills AI itself, it injects the shared external-task
request-only boundary and maintenance workspace.
