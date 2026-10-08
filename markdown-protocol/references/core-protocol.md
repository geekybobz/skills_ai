# Core Protocol

## In brief

Use one navigable knowledge structure at several depths. A reader starts from a
compact orientation, follows an explicit route, and opens optional detail only
when it is useful.

## Invariants

1. Every collection has an identifiable entry point and a route to relevant
   topics without a full scan.
2. Every important statement has one authoritative owner; outer layers
   summarize and link instead of duplicating it.
3. Essential meaning remains in portable text. Visuals and interactive features
   supplement it.
4. A file exists only when it has an independently useful job. The structure
   may expand or collapse as that job changes.
5. Everything a reader must obey or rely on appears above the first
   `## Details`. Details may explain, exemplify, derive, or cite; they never add,
   weaken, or replace a rule.
6. Generated views are marked, reproducible, and non-authoritative.
7. Useful existing conventions and user edits survive unless they obstruct
   these invariants.
8. Markdown writes follow a user-reviewed design proportional to the change.
9. Every authored page ends with Home navigation; Previous and Next appear only
   for an intentional reading order.

## Information roles

| role | owns |
|---|---|
| Front Door | purpose, boundaries, and primary routes |
| Map | recommended paths by reader intention |
| Index | complete authored structural map |
| Topic | authoritative subject content |
| Deep note | optional explanation named by its scope |
| Generated view | replaceable projection, never a canonical fact |

These roles do not require separate files. Combine them while their jobs remain
easy to understand and maintain.

Structured properties and generated inventory are optional. When a collection
opts in, follow the complete [Structured Inventory](structured-inventory.md)
contract; the authored Front Door or human `INDEX.md` remains semantic.

Optional tags use only `domain/...` for subject matter and `use/...` for reader
intent. Tags filter files; they never replace explicit navigation or typed
connections.

## Details

### Progressive disclosure

Use this reading order:

1. One-sentence scope.
2. Compact explanation or route.
3. Authoritative core.
4. Relationships and next links.
5. Optional examples, evidence, derivations, or implementation detail.

Do not hide prerequisites, safety constraints, conclusions, or limitations in
collapsed or tool-specific content.

### Ownership maintenance

Update the authoritative topic first. Update the Map only when a route changes,
the Index only when the authored inventory changes, and the Front Door only
when purpose, boundaries, or primary routes change. A generated inventory is
rebuilt from its properties rather than edited manually.

If another task skill owns technical content, it remains authoritative for that
content. Markdown Protocol owns only structure, navigation, progressive depth,
portability, and Markdown-specific checks.

### Portability

Relative links, headings, paragraphs, lists, block quotes, and fenced code are
the baseline. Renderer-specific syntax requires the classification and fallback
in [markdown-patterns.md](markdown-patterns.md).

### Page footer navigation

End every authored page with a horizontal rule and one compact line:

```markdown
---

[← Previous](previous.md) · [⌂ Home](../README.md) · [Next →](next.md)
```

Home points to the nearest Front Door or semantic hub. A standalone document
links Home to its own title or contents. Omit unavailable directions rather
than guessing from filename order. Keep the footer as the final visible
content. Generated pages receive it through their generator.

### Generated material

Generated files identify their source and regeneration method:

```markdown
<!-- Generated file. Do not edit directly.
Source: <authoritative paths>
Regenerate with: <command>
-->
```

If no reliable regeneration path exists, the file is authored and must not
claim otherwise.

### Failure patterns

- A large README that owns every detail.
- A separate file for every short subsection.
- A Map, Index, and generated inventory duplicating explanations.
- Tool-specific syntax carrying the only copy of essential information.
- Tags standing in for explicit relationships.
- A visual graph with no reader question.
- A generated file that people must edit by hand.

---

[⌂ Home](../INDEX.md) · [Next →](review-workflow.md)
