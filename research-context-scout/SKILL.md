---
name: research-context-scout
description: Orient a new or evolving research project through a recorded supervisor-style dialogue, selective project reconstruction, current related-work and application discovery, evidence-graded research directions, and paper-potential assessment. Use when explicitly invoked with #> scout, #> scout-again, #> skill research-context-scout, or an exact request to use the research-context-scout skill. The initial mode asks consequential questions before deep research; the deepen mode revises an existing research-orientation.md after new ideas, derivations, results, constraints, or sources.
---

# Research Context Scout

Route into the compact shared workflow. Do not read `README.md` during task
execution; it is explanatory material for humans.

## Load the minimum path

1. Read `shared/SKILL.md` completely.
2. Read the platform wrapper for the active host:
   - Codex: `codex/SKILL.md`;
   - Claude: `claude/CLAUDE.md`.
3. Let the shared entry select one phase from the record state and load only
   rules it requires. Do not preload both phases. Load the other phase only for
   a late state-recovery explicitly declared by the selected phase.

## Resolve the mode

Read the injected `mode=` line when present; it is
`context.skill_invocation.mode` at the API layer. Alias and canonical directive
forms inject a validated `initial` or `deepen` mode. Without injected context:

- `#> scout ...` or `#> skill research-context-scout initial ...` means `initial`;
- `#> scout-again ...` or `#> skill research-context-scout deepen ...` means
  `deepen`;
- an existing `research-orientation.md` plus explicitly supplied new
  information means `deepen`; and
- no existing record means `initial`.

Invocation mode expresses user intent, but record completeness selects the
next phase. If the intake answers exist while the Research and application map
is still empty, run initial Cycle B even after `#> scout-again`; deepen only
after that map exists.

If the target path is missing or ambiguous, ask for the path and stop. Do not
search unrelated directories to guess it.

If the target argument is `research-orientation.md`, resolve its parent as the
project root. Otherwise resolve the named project directory before any write.

## Authority boundary

The routed access value `write-scoped:research-orientation.md` authorizes only
creation or update of that file in the resolved project root. Treat every
other supplied research file as read-only. It does not authorize edits to
derivations, code, papers, figures, data or configuration. Ask before any
broader write.
