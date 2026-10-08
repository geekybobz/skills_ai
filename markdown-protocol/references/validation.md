# Validation

Validate the exact changed collection in proportion to its complexity.

## Compact completion check

- The result matches the reviewed proposal and preserves user edits.
- The profile is no larger than necessary; every file has a distinct job and
  one authoritative owner.
- Rules, prerequisites, limitations, and dependable conclusions appear above
  the first `## Details`.
- A Topic beyond roughly 30 compact lines or Front Door beyond roughly 60 lines
  was reviewed for splitting; thresholds were treated as warnings.
- Relative links, anchors, Home footers, and intentional Previous/Next pairs
  resolve.
- Structured properties are present only when consumed. If enabled, the
  generated `INVENTORY.md` is current and the on-demand checker passes.
- Essential meaning survives without diagrams, HTML, plugins, or generated
  views. Every claimed renderer was actually checked.
- Generated files identify their source and regeneration command.

Use the package checker for a bounded collection when its checks apply:

```bash
python3 scripts/markdown_protocol.py check <collection-root>
```

Report changed files, checks, renderer evidence, generated outputs, warnings,
and anything skipped or unverified.

## Details

### Structure and ownership

- An identifiable Front Door exists.
- Maps route by intention; human indexes map structure; generated inventories
  remain replaceable projections.
- Topics are reachable and independently meaningful.
- Short supporting material has not been fragmented into orphans.
- Outer summaries agree with their topic owners.
- Assumptions, limitations, and uncertainty remain visible.

### Formatting and links

- Heading levels form a coherent hierarchy.
- Lists express collections; numbered lists express order.
- Tables remain compact enough to scan.
- Collapsed content is optional, never required for correctness.
- Parent and return links are useful rather than ceremonial.
- Platform-specific links have a portable route or fallback.

### Visuals and mathematics

- Each visual answers a defined question and has a text fallback.
- Large graphs are decomposed when that improves readability.
- Static exports retain editable source.
- Mermaid, HTML, equations, and alerts render in every claimed target.
- No equation delimiter or macro is called dependable from source appearance
  alone; record the application, version, syntax, and result.

### Human and model checks

A human can understand the purpose, navigate without knowing the directory
tree, and edit normal content without advanced tooling. A model can orient from
the entry, load only relevant material, distinguish authority from optional
detail, and follow links without scanning the entire repository.

---

[← Previous](visual-patterns.md) · [⌂ Home](../INDEX.md)
