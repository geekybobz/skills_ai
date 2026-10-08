# Page Footer Navigation

**Purpose:** Give every page a compact, dependable route back to its local
contents and through an intentional reading sequence.

**Portability:** Core.

## Source

```markdown
---

[← Previous](previous-topic.md) · [⌂ Home](../INDEX.md) · [Next →](next-topic.md)
```

## Result

The horizontal rule separates navigation from the page content. Home returns
the reader to the nearest useful index or Front Door. Previous and Next move
through a curated sequence when one exists.

The first page omits Previous, the last page omits Next, and an unsequenced
page shows Home alone. A standalone document points Home to its own title or
contents heading.

## Avoid

Do not infer order from filenames, add dead placeholders, use browser-history
JavaScript, or require CSS, images, or a renderer-specific button style. The
compact links are the button-like control; portability is more important than
decorative appearance.

## Generated pages

Put the footer in the canonical template or generator. Do not hand-edit a
generated page merely to add navigation.

## Maintenance

Recheck Home, Previous, and Next after moving or renaming a page. Keep the
footer as the final visible line and preserve the horizontal rule immediately
above it.

---

[← Previous](15-obsidian-links-and-embeds.md) · [⌂ Home](../markdown-patterns.md)
