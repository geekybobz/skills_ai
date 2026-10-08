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
tags:
  - domain/example
  - use/learning
---
```

Allowed roles are `front-door`, `map`, `index`, `topic`, `deep`, and
`generated`. `role`, `summary`, and `read_when` are required in managed files.
`parent` is required except on the root Front Door. Tags are optional filters:
`domain/` says what the content concerns and `use/` says what the reader does
with it. Tags never replace explicit links.

When tags are present, each value uses `domain/...` or `use/...`, lowercase
letters, digits, and hyphens. Repeated `--tag` filters use AND semantics:

```bash
python3 scripts/markdown_protocol.py tags <collection-root>
python3 scripts/markdown_protocol.py tags <collection-root> \
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

Run the tool explicitly from the skill package:

```bash
python3 scripts/markdown_protocol.py inventory <collection-root> --write
python3 scripts/markdown_protocol.py inventory <collection-root> --check
python3 scripts/markdown_protocol.py check <collection-root> --require-properties
```

`check` validates the bounded collection's local links and anchors, reachable
Markdown files, generated banners, compactness warnings, portable Home footers,
property presence when requested, and inventory freshness. It ignores example
links inside fenced code. It never starts a watcher or scans outside the
supplied collection; external relative links are checked only for existence.

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
python3 scripts/markdown_protocol.py graph <collection-root>
python3 scripts/markdown_protocol.py graph <collection-root> --topic topics/example.md
```

The compactness thresholds produce warnings. Broken links, missing required
properties, or stale generated output produce errors. Renderer behavior still
requires the named renderer; this script does not simulate VS Code or GitHub.

## Boundaries

- Do not enable properties without a real consumer.
- Do not generate over the authored `INDEX.md`.
- Do not treat the tool as a complete Markdown parser.
- Do not use its reachability result as proof of semantic usefulness.
- Review generated changes before accepting them.

---

[⌂ Home](../INDEX.md)
