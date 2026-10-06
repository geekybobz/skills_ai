---
name: research-context-scout
description: Orient a new or evolving research project through a recorded physics-objective-first workflow with user alignment checkpoints, bounded literature discovery and acquisition, mandatory extraction of every paper used, semantic relation mapping, collective mathematical synthesis, project-notation translation, evidence gates, and a concise beginner-facing report. Use when explicitly invoked with #> scout, #> scout-again, #> use research-context-scout, or an exact request to use the research-context-scout skill. The initial mode aligns context before broad research; the deepen mode revises an existing research-orientation.md after new ideas, derivations, results, constraints, sources, or user corrections.
---

# Research Context Scout

Route into the compact shared workflow. The skill is fail-closed: if an
inspected artifact or source does not support a claim, keep the claim as
`unknown`, `candidate`, or `hypothesis`; do not promote it into a research
direction. Scout organizes and translates research evidence; it does not
pretend to replace the user's subject-matter judgment. Do not read `README.md`
during task execution; it is explanatory material for humans.

## Load the minimum path

1. Read `shared/SKILL.md` completely.
2. Read the platform wrapper for the active host:
   - Codex: `codex/SKILL.md`;
   - Claude: `claude/CLAUDE.md`.
3. Let the shared entry select one phase from the record state and load only
   the phase and rules it requires. Do not preload every gate. Load another
   phase only for a state recovery or explicit user request declared by the
   selected phase.

## Resolve the mode

`#> scout` means `initial` and `#> scout-again` means `deepen`; the orchestrator
catalog lists both aliases with their modes. For any other invocation, read
`shared/rules/mode-resolution.md`.

Invocation mode expresses user intent, but record completeness selects the
next phase. If the intake answers exist while the physics objective,
existing-understanding ledger, relation map or gap verdict is still empty, run
initial Cycle B even after `#> scout-again`; deepen only after those exist.

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
