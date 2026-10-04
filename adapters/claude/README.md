# Claude Adapter

The managed `SessionStart` hook injects the shared model-led coordination core and bounded untrusted metadata. Claude interprets the original request and selects capabilities with exact access tools; the hook never injects a selected candidate body.

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

- copies `skills-ai-context.js` into the Claude hooks directory;
- preserves foreign settings while adding one managed `SessionStart` and one selective `UserPromptSubmit` hook;
- removes an obsolete Claude bootstrap only when it is a byte-for-byte
  installer-managed copy of `runtime/SKILL.md`;
- preserves the first `settings.json.skills-ai.bak` snapshot and writes a
  separate `.previous` snapshot before later changed installs;
- refuses to replace symlinks or unrecognized foreign hook files; and
- supports `CLAUDE_CONFIG_DIR` or `--config-dir`.

The hook is the Claude bootstrap. It forwards the absolute project root for exact capsule access, runs one prompt-free context command and suppresses child stderr. Core instructions are read at a fixed path under the runtime root with symlink/realpath and file-size checks. Metadata is clearly labelled untrusted data, never executable instructions or permission.

The hook retains its bounded input/run budget, shorter Python child deadline, process-group timeout reaping, and prompt-free failure/cancellation diagnostics. It creates no background worker. A core over 32 KiB or expired deadline fails open. Tests cover framing, privacy, file bounds, installer preservation and child lifecycle. Live Claude semantic acceptance is required separately; Codex test results cannot certify it.

## Context lifecycle

SessionStart restores the complete bootstrap on startup, resume, clear, compact and fork. UserPromptSubmit supplies only changed sections; unchanged continuations produce no context. The exact session and source root identify private hash-only delivery markers. Missing session identity uses full read-only delivery. Markers never certify instruction presence or task state; uncertain context must be recovered. Core, discovery, capsule and repair changes are tracked separately. Installation preserves foreign hooks and settings and remains idempotent.

The hook acknowledges private section hashes only after its output has been emitted. Failure or cancellation before emission leaves delivery pending; a failed acknowledgment safely repeats context next time. This is a delivery receipt, never evidence the model retained instructions.
