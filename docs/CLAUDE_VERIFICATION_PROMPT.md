# Claude Verification Prompt

Use this prompt after the shared runtime and Codex-owned implementation pass
their repository tests.

```text
Work in /Users/billabobz/skills_ai.

Your responsibility is the Claude side of the shared Skills AI contract. Read
CLAUDE.md, docs/06_CHANGE_CONTROL.md, docs/04_RISK_MAP.md,
docs/SHARED_DOCUMENTATION_MODEL.md,
protocols/repository/UPDATE_MIGRATE.md,
protocols/repository/INSTALL_UNINSTALL.md, runtime/PROTOCOL.md, and
protocols/repository/EXTERNAL_CHANGE_REQUEST.md, runtime/API_CONTRACT.md, and
protocols/repository/DOCUMENTATION.json.
Inspect live Git status and preserve unrelated work.

Verify the shared router contract read-only first. Do not implement, modify, or
certify Codex-specific invocation, timeout, terminal-session, installation, or
cancellation behavior. Report Codex-specific findings to the user with the
SCOPE_EXPANSION template and wait for permission before crossing that boundary.

Audit and test:
- adapters/claude/skills-ai-router.js;
- temporary Claude adapter install, check, migration, and idempotency;
- the single whole-run hook budget: a timer bounds the input phase, and the
  child plus the one skill-body read are bounded by subtracting elapsed time
  from the same budget, keeping both inside the hook timeout in Claude
  settings;
- child cleanup through the child's own process group and through the deadline
  the child is given, including an interpreter shim and a host that ends the
  hook first;
- fail-open behavior for no match, invalid host payload, invalid router output,
  missing router, timeout, exhausted budget, and cancellation, with a reason
  code that names the layer that actually failed;
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
- CLAUDE.md exactly matches the generated shared agent-entry source plus the
  Claude overlay, while AGENTS.md differs only through its Codex overlay;
- `python3 scripts/compile_repository_views.py --check` passes and human live
  indexes remain outside the runtime manifest and ordinary prompt injection;
- the human skill catalog reflects live registry states and the repository
  index explains all tracked files without becoming routing authority;
- external skill symlinks are described but never traversed by documentation
  generation, and the theory-reference submodule remains read-only and separately owned;

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

Do not certify the human teaching quality merely because generated views are
fresh. Report whether the progression from illustration to folder, file, skill
anatomy, live catalog, and canonical source is understandable, but keep edits
behind the repository protocol and explicit user approval.
```
