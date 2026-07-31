---
name: cavecrew
description: >
  Route bounded work to compressed investigator, builder, or reviewer
  subagents. Use for "delegate", "use cavecrew", "spawn investigator",
  "save context", or compressed subagent output. Do not use for broad design,
  cross-cutting refactors, or work that needs explanatory prose.
---

Choose one agent. Return its compact contract to the main thread.

| Task | Use |
|---|---|
| Locate definitions, callers, uses, or tests | `cavecrew-investigator` |
| Surgical edit with known scope of 1-2 files | `cavecrew-builder` |
| Review diff, branch, or file for bugs | `cavecrew-reviewer` |
| Architecture, new feature, 3+ files, or deep rationale | Main thread or full agent |

## Contracts

- Investigator: `path:line - symbol - note`, grouped by role; end with totals.
- Builder: `path:line-range - change`, then `verified: ...`; refuse 3+ files.
- Reviewer: `path:line: severity: problem. fix.`, sorted by file and line.
- Security or destructive output uses normal English.

Do not delegate a one-line answer. Do not use builder before target files are
known. Read [references/patterns.md](references/patterns.md) only for chaining,
parallel scouts, or refusal details.
