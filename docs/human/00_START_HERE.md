---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Start Here

Back to the [human guide](../../README.md). Next: [follow a request](01_FOLLOW_A_REQUEST.md).

## The problem Skills AI solves

Large skill collections contain useful instructions, but loading all of them for
every task is slow, expensive, and distracting. Skills AI keeps a small registry
of names, triggers, activation states, and paths. The router uses that compact
information to select one skill without reading every skill body.

```mermaid
flowchart LR
    OLD["Load many possible skills"] --> COST["More tokens and mixed context"]
    NEW["Read compact manifest"] --> PICK["Select one skill or NORMAL"]
    PICK --> FOCUS["Small task context"]
    PROTOCOL["General protocol<br/>plus math overlay when needed"] --> FOCUS

    classDef old fill:#C62828,color:#fff,stroke:#7F0000
    classDef new fill:#2E7D32,color:#fff,stroke:#1B5E20
    class OLD,COST old
    class NEW,PICK,FOCUS new
```

## The promises

- At most one active or manual skill is selected.
- The general protocol always stays separate from the selected task skill.
- Mathematical reasoning can add a math overlay without replacing that skill.
- No suitable skill means normal model reasoning, not a stopped task.
- Material equal matches ask one short numbered choice instead of guessing;
  harmless uncertainty continues normally.
- Off, hidden, and deprecated routes are not loaded.
- Prompt text and skill bodies are not written to diagnostics.
- Prompt-free ambiguity logs contain only candidate ids and bounded route
  metadata; they are ignored by Git and capped in size.
- Skill selection alone grants no write, network, credential, or account
  authority.
- An explicitly invoked workflow may carry a narrow user-granted write such as
  Scout's project-root `research-orientation.md`; the receipt names that scope
  and leaves all other artifacts read-only.
- A registry-declared command alias selects one exact manual skill only when it
  is the first command; it never activates from a quotation or later mention.
- Each router process reads one request, writes one result, and exits.
- A request to maintain Skills AI itself stays on the normal path and uses the
  repository consistency protocol instead of accidentally selecting a task skill.

## What it is not

Skills AI is not a second model, a persistent web service, a memory of every
skill, or a permission system. It is a small local routing layer. Filesystem and
host permissions remain the real enforcement boundary.

## Small glossary

| Term | Meaning |
|---|---|
| Route | A compact record pointing to one skill |
| Manifest | Generated JSON containing the routable registry |
| Family | A group such as design, UI patterns, interaction, or theory |
| Interaction protocol | Small response guidance composed with task routing |
| `MATCH` | One skill was clearly selected |
| `NORMAL` | Continue the task without a local skill |
| Fail-open | Router trouble does not block the original task |
| Adapter | Thin Codex- or Claude-specific access to the shared router |
| Fit 0–3 | Ordinal skill-route suitability, not confidence in the answer |
| Task receipt | Optional compact task, project, skill/Fit, depth, format, and access header |
| Consistency scan | Git-aware maintenance check that derives affected files, tests, graph links, and human pages |
| Plan-only idea | Exactly `skill-plans/<name>/plan.md`; not yet a skill, route, or graph node |
| Directive alias | Exact task directive such as `#> scout`; selects one declared skill and mode after optional presentation controls without copying its arguments into the receipt |
| `#> override` | Current-request override of local Skills AI procedure; higher-level safety and permission rules remain |

The human guide is explanatory only. For current behavior, the live manifest
and canonical maintenance documents remain authoritative.

The selected depth is delivered to the Codex and Claude response surfaces, so
`brief`, `standard`, and `detailed` can shape the actual answer.

The [Interaction Protocol hub](../../interaction-protocol/README.md) is the
visible Obsidian node connecting its general/math flows, controls, runtime,
API, tests, and migration record.
