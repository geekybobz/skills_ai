# Project Memory Registry

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · Package:
[[skills/project-manager/SKILL|Project Manager]] · Activation:
[[orchestrator/registry/activation|Activation Register]]

This is one active public supporting package. It is mandatory for every
project or repository task and remains active when `#> use none` disables
optional task skills. The package keeps important context portable through a
small `.ai-memory/` collection and one replaceable active HANDOFF.

## Skills

| skill | does | selection | not for |
|---|---|---|---|
| [[skills/project-manager/SKILL\|project-manager]] | reads and validates portable project memory, maintains one active task HANDOFF, proposes durable rules and preferences, captures bounded feedback, and exposes deterministic terminal operations | every project or repository task; explicit memory, save, handoff, resume, feedback, initialization, or recovery request | conversation with no project or working directory, transcript logging, hidden reasoning storage, background watching, or carrying action approval |

## Command aliases

| command | package | mode | boundary |
|---|---|---|---|
| `#> memory` | `project-manager` | `route` | optional `init` or `save` text follows; every write is previewed and explicitly approved |
| `#> handoff` | `project-manager` | `handoff` | propose the smallest complete transfer checkpoint; no silent write |
| `#> resume` | `project-manager` | `resume` | read-only progressive recovery unless a separate change is approved |
| `#> feedback` | `project-manager` | `feedback` | correction text follows; prepare one bounded case without changing rules automatically |

## Details

- Repository authority files and current user instructions outrank saved memory.
- Important reusable rules, preferences, corrections, decisions, and task
  continuity must not exist only in a model's private memory.
- At task entry, read the compact memory front door and active HANDOFF. Load
  only linked rules and artifacts needed for the current task.
- If `.ai-memory/` is missing, stale, corrupt, or conflicting, report that
  state and propose the exact recovery or initialization change.
- Every memory mutation uses a structured before/add/change/delete preview and
  explicit approval of that exact proposal.
- Saved context is advisory. It never authorizes a commit, push, deployment,
  deletion, purchase, external message, retry, or other consequential action.
- Do not store secrets, credentials, transcripts, hidden reasoning, skill
  bodies, or large copied artifacts.

---

[⌂ Home](../docs/00_SKILLS_HUB.md) · [Package](../skills/project-manager/SKILL.md)
