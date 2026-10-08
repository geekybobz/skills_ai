# Collapsible Details

**Purpose:** Keep optional depth near the main explanation without interrupting
the normal reading path.

**Portability:** Common HTML-in-Markdown extension; verify the target renderer.

## Source

```html
<details>
<summary>Why is this condition required?</summary>

The detailed explanation goes here.

</details>
```

## Result

The reader sees a short question or label and expands it to reveal the answer.

<details>
<summary>Open this rendered example</summary>

This sentence is hidden until the section is expanded.

</details>

## Avoid

Never hide a prerequisite, safety warning, main conclusion, or limitation that
the reader must see.

## Fallback

```markdown
### Why is this condition required?

The detailed explanation goes here.
```

---

[← Previous](04-tables.md) · [⌂ Home](../markdown-patterns.md) · [Next →](06-footnotes.md)
