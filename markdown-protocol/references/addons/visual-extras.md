# Visual Extras Add-on

Use this add-on when the portable Markdown and Mermaid baseline is insufficient
for overview, navigation, or a large editable diagram. These tools are optional
views. The Markdown source and its ordinary links remain understandable without
them.

## Outcome

Choose a visual by the question it answers, keep the source editable, and
preserve a dependable text route when the visual is unavailable.

## Add-on declaration

| field | declaration |
|---|---|
| Trigger | A hierarchy, note network, or large authored diagram materially improves understanding beyond the portable baseline |
| Blocks | Visual purpose, source, rendered view, text fallback, scope, limits, and regeneration or editing note |
| Layout variants | Markmap hierarchy, Foam navigation graph, or editable SVG figure beside a compact table |
| Generated views | Markmap SVG/HTML, Foam graph, or exported SVG; each is a non-authoritative projection |
| Checks | Question fit, source ownership, readability, portability, accessibility, target-renderer behavior, and freshness |
| Composition | The topic owns meaning; the chosen visual tool owns rendering only |
| Boundaries | No plugin requirement for essential meaning, visual-only rule, opaque binary source, background indexer, or graph presented as proof |

## Selection guide

| reader question | preferred view | canonical source |
|---|---|---|
| What is the hierarchy of this one note? | Markmap | Markdown headings and lists |
| How are notes linked for exploration? | Foam graph | note files and links |
| How do many precisely placed elements relate? | editable SVG | checked-in SVG source plus text fallback |
| What is the required workflow or dependency? | Mermaid plus table | Markdown diagram and table |

Do not select a tool because it looks richer. Select it only when its interaction
or layout answers the named question better than the baseline.

## Markmap hierarchy view

Markmap derives an interactive mind map from Markdown hierarchy and renders it
as SVG. Use it for summaries, topic decomposition, and teaching outlines—not
for arbitrary graph relationships or exact process semantics.

Design the source first:

```markdown
# Topic

## Principle

- Definition
- Boundary

## Application

- Example
- Verification
```

Keep branch labels short, avoid very deep nesting, and use a `maxWidth` option
when long labels make the view wider than the preview. An exported SVG or HTML
is generated material; declare the source Markdown and regeneration method.
Interactive HTML may load scripts or assets, so do not make it the only record.

Official references: [Markmap overview](https://markmap.js.org/docs/markmap),
[portable JSON options](https://markmap.js.org/docs/json-options), and
[command-line generation](https://markmap.js.org/docs/packages--markmap-cli).

## Foam navigation graph

Foam adds VS Code navigation around links, backlinks, tags, orphans, and a note
graph. Use the graph to discover clusters and missing routes. Do not interpret
proximity or an edge as semantic importance, prerequisite order, or evidence.

The protocol's portable labelled relative links remain the default authored
form. A project may opt into Foam wikilinks only after deciding how ordinary
Markdown renderers will resolve them. Avoid ambiguous identifiers, and keep
typed relations such as `Prerequisite` or `Related` in the protocol's authored
connection blocks rather than inferring them from the visual graph.

Official references: [Foam graph and VS Code views](https://foambubble.github.io/foam-template/docs/getting-started/get-started-with-vscode.html)
and [wikilink behavior](https://foambubble.github.io/foam-template/docs/features/wikilinks.html).

## Editable SVG for large diagrams

Use SVG when manual placement, grouped annotations, or geometry cannot remain
readable in Mermaid. Check in the editable SVG itself; do not keep only a PNG
export. Prefer text elements over outlined text so labels remain searchable and
editable.

Each SVG figure needs:

- a nearby sentence naming the question it answers;
- meaningful alt text in the Markdown image reference;
- a compact table, list, or prose fallback containing the essential meaning;
- the editor or method used, source file, and last verified target;
- stable relative links and no externally loaded fonts or images when avoidable;
- a readable viewBox and dimensions tested at the expected preview width.

Split the subject into several figures when labels become too small. A single
giant canvas is not more dependable than an oversized Mermaid graph.

## Validation

- The view answers one named reader question.
- Essential meaning remains in portable text and ordinary links.
- Markmap source is readable as normal Markdown and generated output is marked.
- Foam is used for navigation, not as semantic or evidentiary authority.
- SVG source is editable, self-contained where practical, and has alt text.
- Large visuals are split or given explicit width and navigation guidance.
- The named target renderer was inspected; otherwise status is `unverified`.
- No extension, network asset, or interactive export is mandatory for use.

---

[⌂ Home](../../INDEX.md)
