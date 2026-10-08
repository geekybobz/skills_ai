---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Skills and Controls

Back: [folder and platforms](02_FOLDER_AND_PLATFORMS.md). Next: [safe changes](04_SAFE_CHANGES.md).

## Public inventory

`skills-orchestrator` is the always-active control plane. It is not a skill and
does not appear in the table or count below.

| package | state | role |
|---|---|---|
| `interaction-protocol` | active | interaction independent of task selection |
| `markdown-protocol` | active | automatic Markdown creation/editing/review with proportional design approval |
| `theory-reference` | active | task package |
| `research-context-scout` | manual | task package |
| `optimizer` | manual | task package |
| `quantum-job-collector` | off | task package |

These six rows are the complete public skill count. Internal capability routes
are never added to it.

The Markdown package selectively adds education guidance for learning material
and codebase guidance for repository structure and workflows. These are
supporting references inside one package, not additional skills.

## Activation states

| state | behavior |
|---|---|
| `active` | may be selected automatically or exactly |
| `manual` | exact explicit selection only |
| `off` | visible in status, never loaded |
| `hidden` | not loaded or shown in ordinary discovery |
| `deprecated` | unavailable for execution; visible in explicit lifecycle inspection |

An internal capability cannot bypass its package or family state. Selection
chooses among available capabilities; it grants no authority.

## Discovery

```bash
python3 scripts/list_registry.py
python3 scripts/list_registry.py --catalog
python3 scripts/list_registry.py --routes
```

The first command lists public skills, the second adds package-level purpose and
trigger metadata, and the third intentionally lists internal technical
capability routes. None loads instruction bodies.

## Everyday request

```text
#> use optimizer, theory-reference
#> mode adaptive

Describe the task, inputs and allowed outputs here.
Prepare the proposal and wait before edits.
```

Replace the example package names with actual available packages. Use `#> use auto`
for automatic selection or `#> use none` to work without task skills. Each listed
package is explicitly requested; list order does not force a workflow or authorize
parallel agents. Required support and incompatible targets are resolved openly.
`mode` chooses method flexibility; ordinary language states the execution boundary.
The detailed controls below remain available when needed.

## Visible task receipt

At the beginning of a substantive task, expect a short block like this:

> **Task receipt**
>
> - **Task understood:** Review the supplied model and explain its assumptions and the requested outputs.
> - **Plan:** Inspect the relevant inputs, prepare the proposed approach and identify the checks needed before implementation.
> - **Skills:** Optimizer and Theory Reference, planned for their relevant phases.
> - **Mode:** Adaptive.
> - **Boundary:** Proposal only; wait before edits or numerical runs.

The task and plan are short paragraphs within separate bullets. Boundary is
optional. Planned selection does not claim instructions are already loaded.
`receipt auto` shows this once for substantive new work and skips trivial requests
and routine follow-ups. `on` shows it for each new request; `off` hides the block.
Material task changes update only affected fields. Equivalent visible native-host
fields are reused, with missing fields added. A receipt does not create an approval
pause or save memory; actual task boundaries still govern execution.

## Task and interaction controls

| control | effect |
|---|---|
| `#> use auto` | host selects the minimum sufficient compatible capability set |
| `#> use none` | use no task skill, even when one fits |
| `#> use <package>, <package>` | use exactly these enabled public packages |
| `#> md_protocol` | force Markdown Protocol review mode for the current request |
| `#> scout <project> [focus]` | start the manual research-context workflow: align project context, preview search lanes, acquire/extract selected papers, synthesize ideas and translate them into project notation |
| `#> scout-again <project> [new information]` | reopen only the affected Scout alignment, corpus, mapping or synthesis state |
| `#> optimizer [status\|catalog\|explore\|intervene\|continue\|branch]` | select the manual optimizer route, its narrow discovery actions, or an explicit adaptive campaign operation |
| `#> build-system <problem.tex>` | map a user-pointed derivation to the live OLGS contract, then stop for review |
| `#> optimize <system/project> <goal>` | run a bounded evidence-led campaign only on an existing verified system |
| `#> interaction general|math` | shorter interaction-mode control |
| `#> format mermaid+summary` | request known output forms |
| `#> depth compact|standard|deep` | select explanation depth |
| `#> receipt auto|on|off` | control compact receipt visibility |

Current request > session > project > global > automatic defaults. The host interprets controls and assesses suitability; metadata transport does not score answer correctness.

Scout pauses at context, search and corpus-readiness boundaries. Papers used in
its collective synthesis must be locally available as full text and extracted;
the skill checks your reference library first, then supplies one acquisition
manifest for a single confirmation, and never authorizes automatic downloads. A
library that is simply switched off is reported as unreachable rather than
treated as a missing paper. Reading happens in two passes: a cheap structured
extraction of every incorporated paper, and full text only for the decisive
ones, so a paper read cheaply can inform context but never carry an
equation-level claim. Its beginner-facing orientation organizes evidence and
possible project-specific derivations while leaving final research judgment to
the user.

The host honors explicit natural instructions and the leading directive block; quoted or retrieved controls are data. `#> use auto`, `#> use none` and `#> use <id>, <id>` cover selection; a natural-language exclusion such as "do not use the optimizer" is honored. Required manual support is disclosed and actual invocation scope resolved before loading.

`#> adherence advisory|adaptive|strict` chooses method flexibility. `#> autonomy review-first|standard|autonomous` chooses continuation behavior within actual authority. `#> composition auto|single|sequential|cooperative|parallel` guides topology; structured recovery applies independently. Controls apply to their own request: a follow-up without `#> mode` is Adaptive again unless you set a chat default such as `#> mode strict for this chat`. Persistent project controls require explicit storage authorization. See the integration contract for full meanings.

## Orchestrator management

| group | actions |
|---|---|
| inventory and diagnosis | `status`, `inspect`, `validate` |
| project context | `initialize-project`, `show-project-context`, `refresh-project`, `replace-project-context`, `forget-project-context` |
| lifecycle | `add`, `edit`, `delete`, `activate`, `deactivate`, `migrate`, `repair`, `document` |

```text
#> orchestrator status
#> orchestrator edit <exact-target>
#> orchestrator sudo <operation> <exact-target>
```

The host reports unsupported actions or missing exact targets without substitution. Bare `#> sudo` is inert. Local sudo never overrides
higher authority, permissions, credentials, external actions, destructive
safety, package activation, or exact scope.

## Project capsule commands

```bash
python3 runtime/project_context.py init --project <absolute-project>
python3 runtime/project_context.py inspect --project <absolute-project>
python3 runtime/project_context.py show --project <absolute-project>
python3 runtime/project_context.py check --project <absolute-project>
python3 runtime/project_context.py refresh --project <absolute-project>
```

Complete replacement requires `replace --stdin-json`. Deletion requires
`delete --confirm-delete`. No command is run merely because it is stored in the capsule.
Normal routing receipts omit stored commands and validation commands. Exact
`show-project-context` inspection may include their neutralized values.

The generated [live skill catalog](_LIVE_SKILL_CATALOG.md) shows the orchestrator
separately, then these six skills, then a separately labelled capability appendix.

For the complete architecture, controls and working examples, see [the walkthrough](10_MODEL_LED_ORCHESTRATOR.md).

## Working with contained changes

Use `#> repair on` once, continue work across messages, then `#> update` to review changes before agreement. `#> repair off` stops containment without deleting or deploying. These controls are independent of `#> use` and `#> mode`. See [Safe changes](04_SAFE_CHANGES.md).

Contained submodule references use independent Git metadata so package wrappers and generated catalogs remain readable. Local host settings are excluded, and reference snapshots are never deployed as skill edits.

Discovery can use compact text with explicit continuation and complete-metadata expansion. Metadata identity includes integration contracts and activation; it is separate from instruction-file identity. Interaction general/math are independently gated supporting capabilities, and their complete protocol is loaded when needed.

## Current context flow

Each request uses adaptive and automatic selection unless explicitly overridden or covered by a wider default. A request-only override does not erase a chat default. Equivalent aliases are harmless; conflicting selections/modes require clarification. `#> orchestrator status` shows effective scope, skills, catalog freshness, repair state and verification limits.

Discovery/access checks the manifest's bounded registry-source bindings first. Stale activation or family metadata stops capability access until an authorized rebuild; skill bodies are not scanned to perform that check. Optional failure still preserves required task and repair obligations.

## Terminal maintenance

`skills_ai skills` lists public packages without loading bodies; `skills_ai skills optimizer` expands exact capability metadata. Neither command selects a skill for a task, changes activation, or changes request/chat adherence controls.
