# Relative and Section Links

**Purpose:** Connect files and exact sections without depending on one computer.

**Portability:** Core.

## Source

```markdown
Read the [architecture note](../architecture.md).

Jump to [Validation](../architecture.md#validation).
```

## Result

The first link opens a nearby file. The second opens its `Validation` heading.
Use descriptive link text rather than `click here`.

## Fallback

If a renderer generates heading anchors differently, link to the file and name
the relevant section in the surrounding sentence.

## Maintenance

Prefer relative repository paths. Recheck links after renaming a file or
heading.

---

[← Previous](01-headings-and-sections.md) · [⌂ Home](../markdown-patterns.md) · [Next →](03-lists-and-checklists.md)
