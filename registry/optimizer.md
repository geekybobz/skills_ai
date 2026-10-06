# Optimizer Registry

Manual workflow for building a system from a TeX derivation or running an
evidence-led campaign on an existing verified system.

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · State:
[[registry/activation|Activation Register]]

## Package Capability

| capability | purpose | triggers | not for |
|---|---|---|---|
| [[optimizer/SKILL\|optimizer]] | independently build a reviewed OLGS system from TeX, or adaptively optimize, explore, intervene, continue, and branch around a verified system through bounded live campaign modes and validation evidence | exact `#> optimizer`, `#> build-system`, `#> optimize`, `#> use optimizer`, or exact request to use the optimizer skill | automatic routing from ordinary prose, silently constructing physics, silently reusing results, silently changing a problem, or claiming globality from a numerical run |

The public package and its capability are `manual`. `build-system` and `optimize`
are independent package workflows, not separate public skills. `explore`,
`intervene`, `continue`, and `branch` are explicit operations under `#> optimizer`.

## Command aliases

| command | package | mode | boundary |
|---|---|---|---|
| `#> optimizer` | `optimizer` | `route` | first task directive; presentation controls may precede; an operation may follow |
| `#> build-system` | `optimizer` | `build-system` | first task directive; requires a user-pointed derivation/problem source |
| `#> optimize` | `optimizer` | `optimize` | first task directive; requires an existing system/project and stated goal |
