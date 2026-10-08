# Editable SVG Diagrams

**Purpose:** Keep large or spatial diagrams editable while presenting a portable
rendered image in Markdown.

**Portability:** Common SVG image plus tool-specific source.

## File pair

Keep the source and export together:

```text
assets/
├── architecture.drawio
└── architecture.svg
```

Excalidraw may use the same pattern with `architecture.excalidraw` and an SVG
export.

## Markdown source

```markdown
![Architecture showing input, processing, and output](assets/architecture.svg)

[Edit the diagram source](assets/architecture.drawio)
```

## Ownership

- The editable file owns geometry and labels.
- The SVG is a replaceable export.
- Nearby text owns rules, constraints, and conclusions.
- Alt text identifies the visual; a text mapping preserves essential meaning.

## Avoid

Do not hand-edit the SVG and its source independently. Do not use an image when
a small Mermaid diagram or table is easier to maintain. Never make the image
the only copy of an important condition.

## Fallback

```text
Input -> Processing -> Output
```

---

[← Previous](18-markmap-view.md) · [⌂ Home](../markdown-patterns.md) · [Next →](20-renderer-verification-fixture.md)
