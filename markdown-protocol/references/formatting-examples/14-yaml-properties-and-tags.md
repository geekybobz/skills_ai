# YAML Properties and Tags

**Purpose:** Store small structured facts that tools can filter or summarize.

**Portability:** The text is portable; interpretation is tool-dependent.

## Source

```yaml
---
type: concept
status: draft
level: foundation
tags:
  - domain/example
  - use/learning
---
```

## Result

Supporting tools can filter notes by type, status, level, or tag. Plain-text
readers still see understandable metadata.

## Avoid

Do not add a field without a real filtering, generation, or maintenance use.
Do not encode paragraphs or essential explanations as properties.

## Fallback

Use a short visible `## Status` or `## Context` section.

---

[← Previous](13-mathematical-expressions.md) · [⌂ Home](../markdown-patterns.md) · [Next →](15-obsidian-links-and-embeds.md)
