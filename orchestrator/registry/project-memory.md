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

## Help operations

| kind | syntax | does | boundary |
|---|---|---|---|
| `chat` | `#> memory init` | Inspect a project and propose minimal `.ai-memory/` initialization. | Preview only until the exact memory change is approved. |
| `chat` | `#> memory save` | Propose durable memory and active-handoff updates. | Never writes silently; saved context grants no later action authority. |
| `chat` | `#> handoff` | Propose the smallest complete transfer checkpoint. | No silent write and no chronological task diary. |
| `chat` | `#> resume` | Recover bounded current project context. | Read-only unless a separate memory change is approved. |
| `chat` | `#> project-manager refresh` | Re-anchor the active chat to current project memory and applicable rules. | Read-only; preserves live task state and mode. |
| `chat` | `#> feedback <correction>` | Propose one bounded feedback case. | Does not automatically change a rule, skill, or protocol. |
| `terminal` | `project-manager init .` | Preview minimal project-memory initialization. | Add `--apply` only after reviewing and approving the exact preview. |
| `terminal` | `project-manager status .` | Show compact initialization and freshness state. | Read-only. |
| `terminal` | `project-manager check .` | Validate structure, hashes, links, and privacy markers. | Read-only. |
| `terminal` | `project-manager context . --format json` | Return bounded recovery context. | Read-only; stored approvals remain historical context. |
| `terminal` | `project-manager refresh . --format json` | Return a read-only active-context refresh packet. | Writes no persistent refresh state. |
| `terminal` | `project-manager change preview - .` | Read, validate, content-bind, and visibly stage one exact memory proposal. | Standard input is preferred; durable memory is unchanged. |
| `terminal` | `project-manager review show .` | Resume inspection of `.ai-memory/review/pending.json`. | Read-only; the pending proposal grants no authority. |
| `terminal` | `project-manager review apply .` | Interactively review and apply the pending proposal. | Rechecks exact content and current memory before writing. |
| `terminal` | `project-manager review discard .` | Reject and remove the pending proposal. | Does not change durable memory. |
| `terminal` | `project-manager change apply PLAN.json --approval-ref REF` | Compatibility apply for a plan matching the pending review. | Requires actual approval matching the unchanged staged plan. |
| `terminal` | `project-manager handoff show .` | Display the active handoff. | Read-only. |
| `terminal` | `project-manager feedback draft . --input -` | Prepare and visibly stage a bounded feedback change from standard input. | Does not apply the feedback change. |

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
- One unapproved proposal may persist at the fixed visible review path; it is
  excluded from the manifest and removed after apply or explicit rejection.
- Saved context is advisory. It never authorizes a commit, push, deployment,
  deletion, purchase, external message, retry, or other consequential action.
- Do not store secrets, credentials, transcripts, hidden reasoning, skill
  bodies, or large copied artifacts.

---

[⌂ Home](../docs/00_SKILLS_HUB.md) · [Package](../skills/project-manager/SKILL.md)
