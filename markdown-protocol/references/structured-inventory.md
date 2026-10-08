# Structured Inventory

Use this optional mode only when a collection benefits from deterministic
inventory generation or protocol-specific checking. Ordinary Markdown does not
need properties or a generated file.

## Property schema

```yaml
---
role: topic
parent: ../README.md
summary: One-line description of this file.
read_when: One-line condition for opening it.
status: active
reviewed: YYYY-MM-DD
tags:
  - domain/example
  - use/learning
---
```

Allowed roles are `front-door`, `map`, `index`, `topic`, `deep`, and
`generated`. `role`, `summary`, and `read_when` are required in managed files.
`parent` is required except on the root Front Door. `status` and `reviewed` are
optional freshness aids. Allowed statuses are `draft`, `active`, `stable`,
`deprecated`, and `archived`; `reviewed` uses an ISO `YYYY-MM-DD` date. They do
not certify correctness or replace evidence. Tags are optional filters:
`domain/` says what the content concerns and `use/` says what the reader does
with it. Tags never replace explicit links.

A file opts into protocol property validation by declaring `role`. A caller can
instead require every file in the bounded collection to opt in with
`mdp verify <root> --require-properties`. Unmanaged front matter keeps its
local meaning and is not validated as Markdown Protocol metadata.

When tags are present, each value uses `domain/...` or `use/...`, lowercase
letters, digits, and hyphens. Repeated `--tag` filters use AND semantics:

```bash
mdp tags <collection-root>
mdp tags <collection-root> \
  --tag domain/control --tag use/learning
```

The first command lists the vocabulary and counts. The second lists files that
carry both tags.

Keep values short and single-line. The bundled standard-library parser accepts
plain scalar values and an indented list for `tags`; it is not a general YAML
implementation.

## Authored and generated views

Keep `README.md`, `MAP.md`, and the human `INDEX.md` authored. Generate the
exhaustive `INVENTORY.md` from properties. Deep and generated notes appear
under its Optional group, and the inventory excludes itself to avoid recursive
output.

## On-demand tool

Install the package once, then use the same command from any collection:

```bash
mdp status <collection-root>
mdp adopt <collection-root>
mdp verify <collection-root> --require-properties
mdp verify <collection-root> --reviewed-since 2026-01-01
mdp inventory <collection-root> --write
mdp inventory <collection-root> --check
```

`verify` validates the bounded collection's local links and anchors, reachable
Markdown files, generated banners, compactness warnings, portable Home footers,
property presence when requested, and inventory freshness. It ignores example
links inside fenced code. It never starts a watcher or scans outside the
supplied collection; external relative links are checked only for existence.

`adopt` runs the same structural analysis but downgrades missing footers and
orphan pages to warnings. It is the first pass for an existing collection, not
a weaker permanent verification mode. `--format json` returns stable finding
objects for editors and automation. `mdp fix` is a dry run by default and only
adds deterministic Home footers; `--apply` is required to write them.

`--reviewed-since` emits warnings for `topic` and `deep` notes whose valid
`reviewed` date is missing or older than the chosen date. It skips `deprecated`
and `archived` notes. Invalid dates or statuses are errors whenever those
optional properties are present. A recent date means only that a review was
recorded; it is not a factual-quality score.

## Typed connections

A Topic may include a `## Connections` section using five labels:

```markdown
## Connections

- Parent: [Containing topic](parent.md)
- Prerequisite: [Read this first](foundation.md)
- Related: [Useful comparison](alternative.md)
- Next: [Continue here](next.md)
- Deeper: [Optional derivation](details.md)
```

The checker validates local targets, Parent/Deeper reciprocity, Next/footer
agreement, and prerequisite cycles. Use the graph view to inspect the learning
order or one topic's transitive prerequisites:

```bash
mdp graph <collection-root>
mdp graph <collection-root> --topic topics/example.md
mdp graph <collection-root> --format mermaid
```

The compactness thresholds produce warnings. Broken links, missing required
properties, or stale generated output produce errors. Renderer behavior still
requires the named renderer; this script does not simulate VS Code or GitHub.

## Boundaries

- Do not enable properties without a real consumer.
- Do not generate over the authored `INDEX.md`.
- Do not treat the tool as a complete Markdown parser.
- Do not use its reachability result as proof of semantic usefulness.
- Do not treat `reviewed` as proof that content is correct or current.
- Review generated changes before accepting them.

---

[⌂ Home](../INDEX.md)
