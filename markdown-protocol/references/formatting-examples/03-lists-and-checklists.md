# Lists and Checklists

**Purpose:** Present collections, ordered procedures, and active work clearly.

**Portability:** Bullets and numbered lists are Core; checklists are Common.

## Source

```markdown
- One item.
- Another item.

1. Prepare the input.
2. Run the process.
3. Validate the result.

- [x] Architecture reviewed.
- [x] Renderer fixture checked.
- [ ] Optional workspace settings reviewed.
```

## Result

Bullets show an unordered set, numbers show sequence, and checkboxes track
temporary work.

The checkbox state is literal source data. A renderer may add interactive
styling, but the bracket marker remains understandable in plain text.

## Avoid

Do not turn permanent knowledge into an endless task list. Use a normal section
for facts and decisions.

---

[← Previous](02-relative-and-section-links.md) · [⌂ Home](../markdown-patterns.md) · [Next →](04-tables.md)
