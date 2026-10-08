# Decision Records Add-on

Use this add-on when a durable technical, architectural, process, or
documentation choice needs a short rationale and visible consequences. Do not
create a record for routine edits whose reasoning is obvious from the change.

## Outcome

A future reader can see what was decided, why, what it affects, and whether a
later record superseded it without reconstructing the discussion history.

## Add-on declaration

| field | declaration |
|---|---|
| Trigger | Durable choices with meaningful alternatives or consequences; not ordinary implementation detail or temporary task notes |
| Blocks | Status, context, decision, consequences, alternatives, affected topics, and supersession links |
| Layout variants | One record beside its topic, or a small routed decision collection |
| Generated views | Optional index generated from record properties and typed links |
| Checks | Required fields, unique identifier, valid status, affected-topic links, and reciprocal supersession |
| Composition | The domain owner decides correctness; this add-on owns the record shape and navigation |
| Boundaries | No transcript, hidden approval, retroactive rewriting of accepted history, or substitute for code and policy authority |

## Record template

```markdown
---
id: ADR-0001
status: proposed | accepted | deprecated | superseded
date: YYYY-MM-DD
tags:
  - domain/example
  - use/decision
---

# ADR-0001 — Short decision title

## In brief

One sentence stating the decision and its scope.

## Context

The pressure, constraint, or conflict that made a choice necessary.

## Decision

The chosen direction. State obligations precisely; link to the owner of any
rule rather than duplicating it.

## Consequences

- Positive:
- Negative or trade-off:
- Follow-up:

## Alternatives considered

- Alternative — why it was not selected for this scope.

## Connections

- Related: [Affected topic](../topic.md) — what the decision changes
- Supersedes: [ADR-0000](ADR-0000.md) — if applicable

---

[⌂ Home](../../INDEX.md)
```

Keep accepted records historically stable. If the decision changes, create a
new record, mark the old one `superseded`, and link both directions. Small
wording corrections may edit the original when they do not alter its meaning.

## Validation

- The identifier is unique and the status is one of the declared values.
- Context explains the decision pressure without copying a meeting transcript.
- The decision is specific enough to test against later work.
- Consequences include material trade-offs, not only benefits.
- Affected topics link to their canonical owners.
- Supersession links are reciprocal and preserve the old record.
- The record grants no authority beyond the decision process that accepted it.

---

[⌂ Home](../../INDEX.md)
