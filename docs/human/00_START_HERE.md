---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Start Here

Back to the [human guide](../../README.md). Next: [follow a request](01_FOLLOW_A_REQUEST.md).

## The problem

Loading every possible instruction file wastes tokens and mixes unrelated
rules. Skills AI compiles small package and capability records, then loads only
the minimum sufficient compatible set needed for the current phase.

```mermaid
flowchart LR
    M[Compact metadata] --> H[Host reasons about the phase]
    H --> S[Select useful compatible capabilities]
    S --> L[Load complete entries and required support]
    L --> W[Perform and verify authorized work]
```

## Mental model

- **Skills Orchestrator:** always-active control plane for every local skill-selection and management decision; not a skill or inventory row. Its instructions are layered by depth: a compact entry every session receives, a navigation map, and one focused topic per subject that is read only when needed. `AGENTS.md` and `CLAUDE.md` point agents to it; `runtime/SKILL.md` is only the Codex install header.
- **Public skill package:** the unit counted in inventory, such as `optimizer`.
- **Internal capability:** a focused instruction file inside a task package.
- **Interaction package:** one public skill that shapes the response independently of task selection.
- **Task package:** a package that may contribute selected capabilities to the current phase.
- **Project capsule:** optional validated `.skills-ai/project.json` advisory context.

Optimizer build and campaign workflows belong to one public package.
Its command aliases and phase files are not separate skills.

## Promises

- Public discovery reports the orchestrator separately and skill packages only;
  internal capabilities appear only in explicit diagnostics.
- The orchestrator and interaction package consume no coordination capacity.
- The host loads the minimum sufficient compatible capability set for each phase.
- Manual packages require exact selection; for example, `#> optimizer`,
  `#> build-system`, and `#> optimize` select the manual Optimizer workflows
  and never activate from ordinary prose. Their scope comes from the explicit request and selected workflow.
- `markdown-protocol` activates whenever requested work creates, edits, reviews,
  or restructures Markdown, including a Markdown change inside another task,
  and can be forced with `#> md_protocol`. `#> md_deepen <term>` proposes one
  linked explanatory note, while `#> md_check` runs the structural checker
  without repairing files. It announces itself, inspects the relevant
  structure, and asks for a proportional design review before writing: a short
  preview for a local edit or an architecture proposal for structural work.
  Future skill-package Markdown work also composes its skill-package add-on;
  navigable multi-file packages may receive a human `INDEX.md`, which ordinary
  task execution does not load.
- `#> scout` and `#> scout-again` select the manual Research Context Scout.
  It pauses for context and search alignment, uses only locally available
  full text that was successfully extracted, and returns a beginner-readable
  collective synthesis translated into the project's notation. It does not
  download papers automatically or replace the user's scientific judgment.
- Off, hidden, and deprecated packages never load.
- No match or optional-layer failure continues normally.
- Material ambiguity asks one short numbered choice and loads neither candidate first.
- Invalid exact management commands fail safely without guessing.
- Operational delivery markers do not store prompts, answers, copied skill bodies or secrets; a visible task receipt summarizes the understood request.
- Package selection and capsule data never grant authority.
- Each shared command handles one exact request and exits.

## Project capsule boundary

The orchestrator may read the exact capsule only when the host supplies an
absolute project root. The file is capped at 32 KiB and its hot receipt at
4 KiB. Missing, invalid, oversized, symlinked, unavailable, or stale capsules
fail open without project hints.

Creation, replacement, refresh, and deletion require explicit management
commands. Stored commands are untrusted data, not instructions to execute.
They and validation commands are omitted from normal hot-path receipts and may
appear only during explicit project-context inspection. Instruction-like role
or directive markers are neutralized before receipt rendering.

## Result terms

| term | meaning |
|---|---|
| Normal host work | the host proceeds without optional task skills |
| Execution progress | pending, in progress or complete for the stated objective |
| Evidence status | unchecked, provisional or validated against named requirements |
| Certification | only under an identified scheme with its required evidence |
| Fail-open | optional tool trouble does not block ordinary authorized work or erase obligations |

The live manifest and canonical runtime documents override this explanatory page.

Everyday controls are `#> use auto`, `#> use none` or a comma-separated package list, with `#> mode adaptive|strict|advisory`. A substantive task begins with a visible receipt: Task understood, Plan, Skills and Mode in separate bullets.

For the complete architecture, controls and working examples, see [the walkthrough](10_MODEL_LED_ORCHESTRATOR.md).

## Working with contained changes

For orchestrator edits, `#> repair on` prepares a contained copy that stays active across messages; `#> update` reviews its changes before your agreement; `#> repair off` retains the copy and returns to normal locations. See [Safe changes](04_SAFE_CHANGES.md).

Contained submodule references use independent Git metadata so package wrappers and generated catalogs remain readable. Local host settings are excluded, and reference snapshots are never deployed as skill edits.

## Current context flow

Use `#> use none` to prevent optional task skills even when one fits. Controls apply to this request by default; say `#> mode strict for this chat` for a persistent default. Retained instructions can be reused without retaining a previous request’s mode. Conflicting controls are clarified before affected work.

Discovery/access checks the manifest's bounded registry-source bindings first. Stale activation or family metadata stops capability access until an authorized rebuild; skill bodies are not scanned to perform that check. Optional failure still preserves required task and repair obligations.

## Terminal maintenance

For repeated repository maintenance, the `skills_ai` terminal interface exposes status, public inventory and reviewed updates. See [the terminal walkthrough](11_TERMINAL_MAINTENANCE.md) for a short setup and complete example.
