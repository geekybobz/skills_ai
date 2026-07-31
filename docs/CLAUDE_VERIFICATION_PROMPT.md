# Claude Verification Prompt

Use this prompt after the shared runtime and Codex-owned implementation pass
their repository tests.

```text
Work in /Users/billabobz/skills_ai.

Your responsibility is the Claude side of the shared Skills AI contract. Read
CLAUDE.md, docs/06_CHANGE_CONTROL.md, docs/04_RISK_MAP.md,
protocols/repository/UPDATE_MIGRATE.md,
protocols/repository/INSTALL_UNINSTALL.md, runtime/PROTOCOL.md, and
protocols/repository/EXTERNAL_CHANGE_REQUEST.md, runtime/API_CONTRACT.md.
Inspect live Git status and preserve unrelated work.

Verify the shared router contract read-only first. Do not implement, modify, or
certify Codex-specific invocation, timeout, terminal-session, installation, or
cancellation behavior. Report Codex-specific findings to the user with the
SCOPE_EXPANSION template and wait for permission before crossing that boundary.

Audit and test:
- adapters/claude/skills-ai-router.js;
- temporary Claude adapter install, check, migration, and idempotency;
- the 1-second Python-child and 3-second outer-hook timeout hierarchy;
- fail-open behavior for no match, invalid output, missing router, timeout, and
  cancellation;
- JSON arrays are invalid envelopes and do not route trigger text;
- no prompt, child stderr path, or skill-body leakage in diagnostics;
- realpath containment blocks an in-root symlink to an outside file;
- foreign regular hook files are preserved, the first settings backup remains
  immutable, and the latest replaced state uses the separate backup;
- no Python or Node process left after repeated failures;
- "What skills are saved in memory?" returns live active/manual/off registry
  metadata without loading a skill body;
- a Skills AI edit request from an external task receives the request-only
  boundary and creates no canonical edit;
- a fresh Claude session uses the hook and shared manifest rather than a copied
  skill catalog or remembered skill body.

"Remove skills from memory" means removing only an installer-managed duplicate
bootstrap or duplicated skill catalog/routing rules. Preserve canonical skills,
the registry, activation state, manifest, general user memory, foreign Claude
files, and user-authored instructions. Back up live configuration and request
explicit permission before changing it. If the hook is insufficient without a
bootstrap, show evidence and propose a protocol amendment instead of guessing.

Run repository tests relevant to Claude and report exact commands, timings,
process-cleanup evidence, configuration inventory, and unverified boundaries.
Do not edit shared or Codex-owned files merely to make a Claude test pass. Any
required expansion must state why it is needed, exact files, behavior, risks,
rollback, rechecks, protocol impact, and requested permission.
```
