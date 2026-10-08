# Markmap View

**Purpose:** Turn an existing Markdown heading hierarchy into an interactive
outline for exploration.

**Portability:** Platform-specific optional VS Code extension.

## Source

Markmap reads ordinary headings and lists; no separate graph source is needed:

```markdown
# System

## Inputs

- Configuration
- User request

## Processing

- Validate
- Execute

## Outputs

- Result
- Verification
```

## Result

With the Markmap extension, **Open as markmap** displays a live, expandable
mind map that updates as the Markdown changes. Without the extension, the same
headings and lists remain the canonical readable document.

## Use

Use Markmap to inspect hierarchy, teaching outlines, or concept relationships.
Keep explicit Markdown links for navigation; spatial position in a generated
mind map is not an authoritative relationship.

## Avoid

Do not require Markmap to understand the document, install it automatically, or
duplicate the same hierarchy in a separately maintained graph.

## Fallback

Use VS Code Outline, the Markdown headings, or a short file tree.

---

[← Previous](17-editor-folding.md) · [⌂ Home](../markdown-patterns.md) · [Next →](19-editable-svg-diagrams.md)
