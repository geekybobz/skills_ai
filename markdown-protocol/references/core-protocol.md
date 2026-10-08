# Core Protocol

## In brief

Build one navigable knowledge structure for both humans and models. A reader
starts with a compact orientation, follows an explicit route, opens only the
relevant topic, and descends into optional detail when needed.

## Invariants

1. Every collection has an identifiable entry point.
2. A reader can locate a relevant topic without scanning the whole collection.
3. Every important statement has one authoritative owner.
4. Outer layers summarize and link; they do not reproduce deep content.
5. Essential meaning remains available in portable text.
6. Diagrams and interactive features supplement rather than replace prose.
7. A topic becomes a separate file only when it is independently useful.
8. Generated views are marked, reproducible, and replaceable.
9. Existing useful conventions survive unless they obstruct these invariants.
10. The structure may collapse or expand as the material changes.
11. Markdown writes follow a user-reviewed design whose detail is proportional
    to the change.

## Information roles

| role | question answered | usual form |
|---|---|---|
| Front Door | What is this and where do I begin? | `README.md` or the package entry |
| Map | Where do I go for my intention? | `MAP.md` or a short route section |
| Index | What material exists? | `INDEX.md` or a compact contents section |
| Topic | What is authoritative for this subject? | one focused Markdown note |
| Deep note | Why, how, or with what evidence? | section or linked child note |
| Generated view | What projection can tooling derive? | clearly marked replaceable artifact |

These roles do not imply six files. In a small collection, one file may own the
Front Door, Map, and Index roles. Separate them only when each has a distinct
job.

## Progressive disclosure

Use this reading order:

1. One-sentence scope.
2. Compact explanation or route.
3. Authoritative core.
4. Relationships and next links.
5. Optional examples, evidence, derivations, or implementation detail.

Do not hide prerequisites, safety constraints, conclusions, or limitations in
collapsed or tool-specific content.

## Information ownership

- The Front Door owns purpose, boundaries, and primary routes.
- The Map owns recommended paths by intention.
- The Index owns the complete structural listing.
- A topic owns its subject matter.
- A deep note owns only the detail named by its scope.
- A generated view owns no manually maintained fact.

When content changes, update its owner first. Update the Map only if a route
changes, the Index only if inventory changes, and the Front Door only if the
collection's purpose, boundaries, or primary routes change.

If another task skill owns the technical or domain content, it remains the
authority for that content. Markdown Protocol owns only the document structure,
navigation, progressive depth, portability, and Markdown-specific checks.

## Portability

Relative Markdown links, headings, paragraphs, lists, block quotes, and fenced
code are the default. Common extensions, renderer-dependent syntax, and
platform-specific features require the classification and fallback described
in [markdown-patterns.md](markdown-patterns.md).

## Authored and generated material

Generated files must identify their source and regeneration method. Use a
banner such as:

```markdown
<!-- Generated file. Do not edit directly.
Source: <authoritative paths>
Regenerate with: <command>
-->
```

If no reliable regeneration path exists, the file is authored content and
must not claim otherwise.

## Common failure patterns

- A large README that tries to own every detail.
- A separate file for every short subsection.
- A Map and Index containing duplicate explanations.
- Tool-specific syntax carrying the only copy of essential information.
- Tags standing in for explicit relationships.
- A visual graph with no defined reader question.
- A generated file that people must edit by hand.
