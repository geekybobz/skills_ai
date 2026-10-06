---
name: optimizer
description: Use this manual optimizer package only with #> optimizer, #> build-system, #> optimize, #> use optimizer, or an exact request to use the optimizer skill. Build a system from a TeX derivation against the live OLGS contract, run an adaptive evidence-led campaign on an existing verified system, or inspect and branch around unexpected optimization situations without silently changing the scientific problem.
---

# Optimizer

Use only after an exact manual invocation. Resolve the current route before
importing the optimizer; never hard-code a stable version or environment.

## Load the minimum path

1. The platform wrapper for the active host — Codex: `codex/CODEX.md`; Claude:
   `claude/CLAUDE.md`.
2. One workflow file for the resolved mode.
3. `situation-analysis.md` only when an operation or a checkpoint named by the
   loaded workflow requires it.

Resolve the mode from the exact leading directive (table below; the orchestrator
catalog lists the same aliases) instead of re-deriving it from prose.

| invocation | mode | load |
|---|---|---|
| `#> build-system <problem.tex>` | `build-system` | `build-system.md` |
| `#> optimize <system/project> <goal>` | `optimize` | `optimize.md` |
| `#> optimizer <operation> ...` | `route` | see operations below |

Do not treat `build-system` and `optimize` as one workflow. `build-system`
does not optimize. `optimize` does not silently design or edit a physical
system.

## Operations under `#> optimizer`

| operation | action |
|---|---|
| `#> optimizer status` | Report the resolved route and live version from the discovery helper. |
| `#> optimizer catalog <query>` | Answer from the narrow discovery helper or `opt.search(query)`. |
| `#> optimizer explore <system/project> <question>` | Read `situation-analysis.md`; rank viable routes before selecting an action. |
| `#> optimizer intervene <campaign> <proposal>` | Read `situation-analysis.md`; assess and record an explicit tactic change. |
| `#> optimizer continue <campaign>` | Read `situation-analysis.md`; continue only an identity-compatible problem. |
| `#> optimizer branch <campaign> <change>` | Read `situation-analysis.md`; open a tactic branch or a new-problem branch. |

`explore`, `intervene`, `continue`, and `branch` are operations of the one
manual `optimizer` route, not new router aliases or separate skills. They keep
the workflow adaptive; they do not grant silent system edits, unbounded runs,
or stronger scientific claims.

## Resolve first

```bash
python optimizer/scripts/optimizer_api.py status
python optimizer/scripts/optimizer_api.py discover <query>
python optimizer/scripts/optimizer_api.py contract
python optimizer/scripts/optimizer_api.py campaigns
python optimizer/scripts/optimizer_api.py tracker
```

The helper resolves the route and returns its `path` and `environment` beside
the payload; use those for every import. It does not import a project system,
evaluate controls, or run an optimizer. Once a system object is available, use
only targeted live calls:

```python
opt.system_info(system)
opt.context_info(system)
opt.info("lbfgs")
opt.path("debug_gradient")
```

Never infer physics, metrics, objective direction, or control semantics from a
class name or user prose. Those facts belong to the system and its declared
contract.
