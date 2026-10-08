# Layouts

Choose a layout by navigation need, not by an arbitrary file or line count.

## Collection profiles

### Single document

```text
README.md
```

Use sections for the overview, route, contents, topics, and detail. Do not
split while the document remains easy to scan and maintain.

### Compact collection

```text
README.md
topics/
    topic-a.md
    topic-b.md
```

The Front Door also owns the Map and Index roles.

### Standard collection

```text
README.md
MAP.md
INDEX.md
topics/
    topic-a.md
    topic-b.md
```

Use this when recommended routes and exhaustive inventory have become
meaningfully different jobs.

### Modular collection

```text
README.md
MAP.md
INDEX.md
topics/
    foundations/
    workflows/
    architecture/
views/
generated/
assets/
```

Create only directories that own real content. `views/`, `generated/`, and
`assets/` are optional.

## Front Door

```markdown
# Collection name

One sentence explaining the purpose.

## In brief

The smallest useful explanation of the whole collection.

## Main routes

- To understand ..., read [...](...).
- To perform ..., read [...](...).

## Navigation

- [Route map](MAP.md)
- [Complete index](INDEX.md)

---

[⌂ Home](#collection-name)
```

Omit sections that add no information. Add one small conceptual diagram only
when it improves orientation.

## Route Map

```markdown
# Route Map

## If you are new

1. Read [...](...).
2. Continue to [...](...).

## If you want to perform a task

- For ..., read [...](...).

## If you want to understand the architecture

- Begin with [...](...).

---

[← Previous](README.md) · [⌂ Home](README.md) · [Next →](INDEX.md)
```

The Map is curated and intention-oriented; it is not exhaustive.

## Index

```markdown
# Topic Index

## Foundations

- [Topic A](topics/topic-a.md)
  - Main concept
  - Related subtopic

## Workflows

- [Workflow A](topics/workflow-a.md)

---

[← Previous](MAP.md) · [⌂ Home](README.md) · [Next →](topics/topic-a.md)
```

The Index is complete but textually light.

## Topic

```markdown
# Topic name

One sentence defining the scope.

## In brief

A compact explanation sufficient for orientation.

## Core

The authoritative knowledge, instructions, or decisions.

## Connections

- Parent: [...](...)
- Prerequisite: [...](...)
- Related: [...](...)
- Next: [...](...)

## Details

Optional explanation or links to deep notes.

---

[← Previous](previous-topic.md) · [⌂ Home](../README.md) · [Next →](next-topic.md)
```

Only the title, scope, and meaningful content are required. Use the other
sections when they improve reading or navigation.

## Deep note

```markdown
# Detailed subject

## Relationship to the parent topic

This note expands [...](...).

## Explanation

## Example

## Limitations

## Return

[Return to the parent topic](../topic.md)

---

[⌂ Home](../../README.md)
```

The footer is required even when optional template sections are omitted. Home
always exists. Previous and Next express a curated sequence, not alphabetical
or filesystem order. The first and last pages omit whichever direction does
not exist; a single-document profile links Home to its own title or contents.

## Split or merge

Create a separate note when the material is independently useful, reused from
several places, maintained separately, or disruptive to the parent's main
flow. Keep it as a section when it is short supporting context, meaningful
only inside the parent, or likely to become an orphan.

Merge notes when their boundaries cannot be explained without repeating each
other. Split a directory only when its contents form a stable, named group.

---

[← Previous](review-workflow.md) · [⌂ Home](../INDEX.md) · [Next →](markdown-patterns.md)
