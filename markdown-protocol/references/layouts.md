# Layouts

Choose a layout by navigation need, not symmetry or an arbitrary file count.

## Collection profiles

| profile | usual structure | use when |
|---|---|---|
| Single document | one `README.md` | one file remains easy to scan and maintain |
| Compact collection | Front Door plus focused topics | the Front Door can also own routes and inventory |
| Standard collection | Front Door, Map, Index, and topics | intention routes and exhaustive inventory are distinct jobs |
| Modular collection | Standard plus stable groups, views, or assets | several independently maintained areas justify them |

Use the smallest profile that keeps orientation, ownership, and navigation
clear. Split only when a section is independently useful, reused, separately
maintained, or disruptive to its parent. Merge files whose boundaries require
repetition to explain.

## Compactness review thresholds

- Review a Topic when `In brief` plus `Core` grows beyond roughly 30 non-empty
  lines.
- Review a Front Door when material above `## Details` grows beyond roughly 60
  non-empty lines.
- Treat these as warnings, not failures. Also inspect bytes, approximate tokens,
  unrelated jobs, repeated explanations, and conditional branches.

Move optional explanation below `## Details` or into a focused reference. Never
move a rule, prerequisite, limitation, or dependable conclusion below it.

## Orientation view

From a nontrivial Compact profile upward, provide one small orientation view.
Choose the least complex form that answers the reader's question: a route list,
table, file tree, text flow, or diagram. A diagram is not mandatory. When used,
include a text fallback and keep it within the visual reliability budget.

Structured properties and generated `INVENTORY.md` are optional tooling for a
collection that needs an exhaustive machine-checkable listing. They never
replace the authored Front Door, Map, or human `INDEX.md`.

## Details

### Example structures

```text
# Single
README.md

# Compact
README.md
topics/
    topic-a.md
    topic-b.md

# Standard
README.md
MAP.md
INDEX.md
topics/

# Modular additions when justified
views/
generated/
assets/
```

### Front Door template

```markdown
# Collection name

One sentence explaining the purpose.

## In brief

The smallest useful explanation.

## Main routes

- To understand ..., read [...](...).
- To perform ..., read [...](...).

## Orientation

A compact route table, text flow, file tree, or useful diagram with fallback.

## Details

Optional explanation. No new rule begins here.

---

[⌂ Home](#collection-name)
```

### Route Map template

```markdown
# Route Map

## If you are new

1. Read [...](...).
2. Continue to [...](...).

## If you want to perform a task

- For ..., read [...](...).

---

[← Previous](README.md) · [⌂ Home](README.md) · [Next →](INDEX.md)
```

The Map is curated by intention; it is not exhaustive.

### Human Index template

```markdown
# Topic Index

## Foundations

- [Topic A](topics/topic-a.md) — one-line human orientation.

## Workflows

- [Workflow A](topics/workflow-a.md) — when to use it.

---

[← Previous](MAP.md) · [⌂ Home](README.md) · [Next →](topics/topic-a.md)
```

The human Index is complete but semantically grouped and textually light. An
optional generated `INVENTORY.md` is a separate exhaustive projection.

### Topic template

```markdown
# Topic name

One sentence defining the scope.

## In brief

Compact orientation.

## Core

Authoritative knowledge, instructions, or decisions.

## Connections

- Parent: [...](...)
- Prerequisite: [...](...)
- Related: [...](...)
- Next: [...](...)
- Deeper: [...](...)

## Details

Optional explanation or links to deep notes. No new rule begins here.

---

[← Previous](previous-topic.md) · [⌂ Home](../README.md) · [Next →](next-topic.md)
```

Only the title, scope, and meaningful content are required. Omit ceremonial
sections that carry no information.

Connections are typed rather than inferred from prose:

| label | meaning |
|---|---|
| Parent | one containing or owning topic |
| Prerequisite | content that must be understood first |
| Related | useful association without required order |
| Next | canonical successor in an intentional reading order |
| Deeper | optional explanatory child |

`Parent` and `Deeper` are reciprocal. `Next` is canonical and the footer mirrors
it; the target footer points back with Previous. Omit a label when no real
relationship exists. The checker rejects prerequisite cycles.

### Deep note template

```markdown
# Detailed subject

## Relationship to the parent topic

This note expands [...](...).

## Explanation

## Example

## Limitations

---

[⌂ Home](../../README.md)
```

Deep notes are already optional depth and do not need another `## Details`
boundary. Previous and Next express a curated sequence, never filename order.

---

[← Previous](review-workflow.md) · [⌂ Home](../INDEX.md) · [Next →](markdown-patterns.md)
