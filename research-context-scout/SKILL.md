---
name: research-context-scout
description: Orient a new or evolving research project through a recorded supervisor-style dialogue, selective project reconstruction, current related-work and application discovery, evidence-graded research directions, and paper-potential assessment. Use when explicitly invoked with /scout, /scout-again, /skill research-context-scout, or an exact request to use the research-context-scout skill. The initial mode asks consequential questions before deep research; the deepen mode revises an existing research-orientation.md after new ideas, derivations, results, constraints, or sources.
---

# Research Context Scout

Route into the compact shared workflow. Do not read `README.md` during task
execution; it is explanatory material for humans.

## Load the minimum path

1. Read `shared/SKILL.md` completely.
2. Read the platform wrapper for the active host:
   - Codex: `codex/SKILL.md`;
   - Claude: `claude/CLAUDE.md`.
3. Let the shared entry select exactly one phase and any rule it explicitly
   requires. Do not preload both phases, the template and all rules.

## Resolve the mode

Use the router's `context.skill_invocation.mode` when present. Otherwise:

- `/scout ...` or `/skill research-context-scout initial ...` means `initial`;
- `/scout-again ...` or `/skill research-context-scout deepen ...` means
  `deepen`;
- an existing `research-orientation.md` plus explicitly supplied new
  information means `deepen`; and
- no existing record means `initial`.

If the target path is missing or ambiguous, ask for the path and stop. Do not
search unrelated directories to guess it.

## Authority boundary

Treat supplied research files as read-only. An explicit scout command
authorizes creation or update of only the target project's
`research-orientation.md`. It does not authorize edits to derivations, code,
papers, figures, data or configuration. Ask before any broader write.
