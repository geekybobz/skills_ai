# File Trees

**Purpose:** Show hierarchy, ownership, or a proposed directory layout.

**Portability:** Core when written in a fenced text block.

## Source

```text
project/
├── README.md
├── MAP.md
└── topics/
    ├── foundations.md
    └── workflow.md
```

## Result

Indentation and branch characters display containment without requiring a
diagram renderer.

## Avoid

Do not reproduce a very large filesystem. Show only the paths needed to explain
the structure, and mark omitted branches when necessary.

---

[← Previous](08-inline-and-block-code.md) · [⌂ Home](../markdown-patterns.md) · [Next →](10-comments-and-generated-banners.md)
