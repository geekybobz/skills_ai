# Optimizer Registry

Manual workflow for building a system from a TeX derivation or running an
evidence-led campaign on an existing verified system.

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · State:
[[orchestrator/registry/activation|Activation Register]]

## Package Capability

| capability | purpose | triggers | not for |
|---|---|---|---|
| [[skills/optimizer/SKILL\|optimizer]] | independently build a reviewed OLGS system from TeX, or adaptively optimize, explore, intervene, continue, and branch around a verified system through bounded live campaign modes and validation evidence | exact `#> optimizer`, `#> build-system`, `#> optimize`, `#> use optimizer`, or exact request to use the optimizer skill | automatic routing from ordinary prose, silently constructing physics, silently reusing results, silently changing a problem, or claiming globality from a numerical run |

The public package and its capability are `manual`. `build-system` and `optimize`
are independent package workflows, not separate public skills. `explore`,
`intervene`, `continue`, and `branch` are explicit operations under `#> optimizer`.

## Command aliases

| command | package | mode | boundary |
|---|---|---|---|
| `#> optimizer` | `optimizer` | `route` | first task directive; presentation controls may precede; an operation may follow |
| `#> build-system` | `optimizer` | `build-system` | first task directive; requires a user-pointed derivation/problem source |
| `#> optimize` | `optimizer` | `optimize` | first task directive; requires an existing system/project and stated goal |

## Help operations

| kind | syntax | does | boundary |
|---|---|---|---|
| `chat` | `#> build-system <problem.tex>` | Build a reviewed OLGS system from a user-pointed derivation. | Produces a plan first; it does not optimize or silently construct physics. |
| `chat` | `#> optimize <system/project> <goal>` | Start an evidence-led campaign on an existing verified system. | Does not silently redesign the system or claim numerical globality. |
| `chat` | `#> optimizer status` | Report the resolved optimizer route and live version. | Read-only inspection. |
| `chat` | `#> optimizer catalog <query>` | Search the narrow optimizer catalog. | Discovery only; does not run optimization. |
| `chat` | `#> optimizer explore <system/project> <question>` | Rank viable responses to an unexpected situation. | No tactic or problem change is applied silently. |
| `chat` | `#> optimizer intervene <campaign> <proposal>` | Assess an explicit tactic change. | Requires an explicit proposal and preserves problem identity. |
| `chat` | `#> optimizer continue <campaign>` | Continue an identity-compatible campaign. | Refuses silent changes to the scientific problem. |
| `chat` | `#> optimizer branch <campaign> <change>` | Propose a tactic or new-problem branch. | Branch type and changed assumptions must remain explicit. |
| `terminal` | `python optimizer/scripts/optimizer_api.py status` | Resolve the active optimizer route and version. | Read-only; does not import or run a project system. |
| `terminal` | `python optimizer/scripts/optimizer_api.py discover <query>` | Search available optimizer routes. | Read-only discovery. |
| `terminal` | `python optimizer/scripts/optimizer_api.py contract` | Display the resolved optimizer contract. | Read-only; contract display grants no run authority. |
