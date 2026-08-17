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
| `interaction-protocol` | active | interaction, no task slot |
| `design-with-claude` | active | task package |
| `theory-reference` | active | task package |
| `research-context-scout` | manual | task package |
| `optimizer` | manual | task package |
| `quantum-job-collector` | off | task package |

These six rows are the complete public skill count. Internal capability routes
are never added to it.

## Activation states

| state | behavior |
|---|---|
| `active` | may be selected automatically or exactly |
| `manual` | exact explicit selection only |
| `off` | visible in status, never routed |
| `hidden` | not routed or shown in ordinary discovery |
| `deprecated` | not routed; retained temporarily for history |

An internal capability cannot bypass its package or family state. Selection
changes availability only; it grants no authority.

## Discovery

```bash
python3 scripts/list_registry.py
python3 scripts/list_registry.py --catalog
python3 scripts/list_registry.py --routes
```

The first command lists public skills, the second adds package-level purpose and
trigger metadata, and the third intentionally lists internal technical
capability routes. None loads instruction bodies.

## Task and interaction controls

| control | effect |
|---|---|
| `#> skill auto` | select at most one active task-package capability |
| `#> skill normal` | use no local task package |
| `#> skill <package>` | select one exact enabled public package |
| `#> skill <package> <capability>` | select one exact internal capability within that package |
| `#> skill interaction-protocol general|math` | select the interaction package mode without using the task slot |
| `#> scout <project> [focus]` | start the manual research-context workflow: align project context, preview search lanes, acquire/extract selected papers, synthesize ideas and translate them into project notation |
| `#> scout-again <project> [new information]` | reopen only the affected Scout alignment, corpus, mapping or synthesis state |
| `#> optimizer [status\|catalog\|explore\|intervene\|continue\|branch]` | select the manual optimizer route, its narrow discovery actions, or an explicit adaptive campaign operation |
| `#> build-system <problem.tex>` | map a user-pointed derivation to the live OLGS contract, then stop for review |
| `#> optimize <system/project> <goal>` | run a bounded evidence-led campaign only on an existing verified system |
| `#> interaction general|math` | shorter interaction-mode control |
| `#> format mermaid+summary` | request known output forms |
| `#> depth brief|standard|detailed` | select explanation depth |
| `#> receipt auto|on|off` | control compact receipt visibility |

Exact controls win over project hints and automatic matching. Fit describes
route suitability, not answer correctness.

Scout pauses at context, search and corpus-readiness boundaries. Papers used in
its collective synthesis must be locally available as full text and extracted;
the route checks your reference library first, then supplies one acquisition
manifest for a single confirmation, and never authorizes automatic downloads. A
library that is simply switched off is reported as unreachable rather than
treated as a missing paper. Reading happens in two passes: a cheap structured
extraction of every incorporated paper, and full text only for the decisive
ones, so a paper read cheaply can inform context but never carry an
equation-level claim. Its beginner-facing orientation organizes evidence and
possible project-specific derivations while leaving final research judgment to
the user.

`#> skill` is exact only as the first task directive, optionally after leading
presentation controls. Quoted, embedded, code-block, URL, and later examples
are inert. A capability belonging to another package is reported as rejected
and is never silently substituted.

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

Target-requiring actions without a target and unsupported actions return
`INVALID_ORCHESTRATOR_ACTION`. Bare `#> sudo` is inert. Local sudo never overrides
higher authority, permissions, credentials, external actions, destructive
safety, package activation, or exact scope.
The deprecated `#> skill skills-supervisor ...` syntax remains a temporary
compatibility alias and is never treated as a skill selection.

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
