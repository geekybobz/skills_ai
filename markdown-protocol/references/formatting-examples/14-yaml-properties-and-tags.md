# YAML Properties and Tags

**Purpose:** Store small structured facts that tools can filter or summarize.

**Portability:** The text is portable; interpretation is tool-dependent.

## Source

```yaml
---
role: topic
parent: ../README.md
summary: Explains one focused concept.
read_when: Read when this concept is needed.
tags:
  - domain/example
  - use/learning
---
```

## Result

The Markdown Protocol tool can build an exhaustive inventory from `role`,
`parent`, `summary`, and `read_when`. Supporting tools can filter the optional
tags. Plain-text readers can still understand the metadata.

```bash
python3 scripts/markdown_protocol.py tags . --tag domain/example --tag use/learning
```

Repeated tag filters use AND semantics. Use lowercase letters, digits, and
hyphens after the `domain/` or `use/` prefix.

## Avoid

Use this schema only when a real checker, inventory, or graph consumes it. Do
not add fields without a filtering, generation, or maintenance use, and do not
encode paragraphs or essential explanations as properties. The root Front Door
may omit `parent`; other managed files include it.

Tags do not encode prerequisites, ownership, or reading order. Use links and
the typed Connections block for those relationships.

## Fallback

Use a short visible `## Status` or `## Context` section.

---

[← Previous](13-mathematical-expressions.md) · [⌂ Home](../markdown-patterns.md) · [Next →](15-obsidian-links-and-embeds.md)
