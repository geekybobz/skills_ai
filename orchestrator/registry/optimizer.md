# Optimizer Registry

Manual workflow for building a system from supplied theory or running an
evidence-led campaign on an existing verified system.

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · State:
[[orchestrator/registry/activation|Activation Register]]

## Package Capability

| capability | purpose | triggers | not for |
|---|---|---|---|
| [[skills/optimizer/SKILL\|optimizer]] | plan and build reviewed theory-derived OLGS and/or OLSS systems, then run reproducible low-energy multistart optimization through installed CLI or available MCP tools with independent verification, plus reviewed Bloch plotting through the shared library renderer | `#> optimizer`, `#> bloch`, `#> build-system` | automatic routing from ordinary prose, silently constructing physics, silently reusing results, silently changing a problem, or claiming globality from a numerical run |

The public package and its capability are `manual`. `build-system` and `optimize`
are independent package workflows, not separate public skills. `explore`,
`intervene`, `continue`, and `branch` are explicit operations under `#> optimizer`.

The registered construction shortcut is `#> build-system`; the host also interprets
the equivalent leading phrase `#> build system`. Bare `#> build` is not a trigger.
This is semantic interpretation, not a local keyword router or grammar change.

## Command aliases

| command | package | mode | boundary |
|---|---|---|---|
| `#> optimizer` | `optimizer` | `route` | first task directive; presentation controls may precede; an operation may follow |
| `#> bloch` | `optimizer` | `bloch` | first task directive; requires a reviewed plotting plan before propagation/rendering |
| `#> build-system` | `optimizer` | `build-system` | reviewed OLGS/OLSS/both construction shortcut; requires a theory/project target |

## Help operations

| kind | syntax | does | boundary |
|---|---|---|---|
| `chat` | `#> build-system <theory/project> [OLGS/OLSS/both]` | Route to the shared reviewed construction workflow. | Select OLGS/OLSS/both; plan and review before construction. |
| `chat` | `#> optimizer build-system <theory/project> [OLGS/OLSS/both]` | Build the reviewed OLGS, OLSS, or both formulations from supplied theory. | Produces a plan first; it does not optimize or silently construct physics. |
| `chat` | `#> optimizer optimize <system/project> <goal>` | Start an evidence-led campaign on an existing verified system. | Does not silently redesign the system or claim numerical globality. |
| `chat` | `#> bloch <trajectory/system/candidate>` | Plan and review a Bloch plot, then use the shared installed renderer. | Initial invocation does not authorize rendering; wait for review. |
| `chat` | `#> optimizer status` | Report the installed runtime and source context. | Read-only inspection. |
| `chat` | `#> optimizer catalog <query>` | Search the narrow optimizer catalog. | Discovery only; does not run optimization. |
| `chat` | `#> optimizer explore <system/project> <question>` | Rank viable responses to an unexpected situation. | No tactic or problem change is applied silently. |
| `chat` | `#> optimizer intervene <campaign> <proposal>` | Assess an explicit tactic change. | Requires an explicit proposal and preserves problem identity. |
| `chat` | `#> optimizer continue <campaign>` | Continue an identity-compatible campaign. | Refuses silent changes to the scientific problem. |
| `chat` | `#> optimizer branch <campaign> <change>` | Propose a tactic or new-problem branch. | Branch type and changed assumptions must remain explicit. |
| `terminal` | `python optimizer/scripts/optimizer_api.py status` | Inspect the installed optimizer version and source context. | Read-only; does not import or run a project system. |
| `terminal` | `python optimizer/scripts/optimizer_api.py discover <query>` | Search the installed optimizer catalog. | Read-only discovery. |
| `terminal` | `python optimizer/scripts/optimizer_api.py contract` | Display the installed OLGS contract; pass olss for shooting. | Read-only; contract display grants no run authority. |
