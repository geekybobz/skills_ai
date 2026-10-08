# Comments and Generated Banners

**Purpose:** Leave source-only maintenance notes or identify replaceable output.

**Portability:** Common HTML-in-Markdown behavior.

## Hidden comment

```markdown
<!-- Review this example after the renderer decision. -->
```

The comment remains visible in source but is normally hidden when rendered.

## Generated banner

```markdown
<!-- Generated file. Do not edit directly.
Source: topics/*.md
Regenerate with: python3 scripts/build_index.py
-->
```

## Avoid

Do not hide user-facing requirements, permissions, or unresolved decisions in
comments. A generated banner must name a real source and regeneration method.

---

[← Previous](09-file-trees.md) · [⌂ Home](../markdown-patterns.md) · [Next →](11-images-and-alt-text.md)
