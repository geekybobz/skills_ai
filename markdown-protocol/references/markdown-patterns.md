# Markdown Pattern Gallery

Open only the example needed for the current task.

## Portability levels

| level | meaning |
|---|---|
| Core | ordinary Markdown with strong cross-renderer support |
| Common | widely supported extension; verify the intended renderer |
| Render-dependent | requires diagram, mathematics, or HTML support |
| Platform-specific | requires a named application |

Each example states its purpose, portability, use and avoidance conditions,
source, expected result, fallback, and maintenance risk. When a proposal uses a
non-core pattern, link that example in its optional `Patterns used` line.

## Tested baseline

Renderer claims use three evidence levels: **documented** means the target's
current documentation supports the syntax, **observed** means the exact fixture
was opened in that target, and **fallback** means the meaning remains readable
without the enhancement. Never promote documented support to observed support.

The current inspection baseline is VS Code 1.141 built-in Markdown preview and
GitHub Markdown as checked on 2026-10-08. Obsidian remains compatible through
portable links but is not part of the tested baseline. Visual observation in
VS Code remains pending because computer-use permission was unavailable during
this pass.

## Details

### Structure and navigation

- [Headings and sections](formatting-examples/01-headings-and-sections.md)
- [Relative and section links](formatting-examples/02-relative-and-section-links.md)
- [Lists and checklists](formatting-examples/03-lists-and-checklists.md)
- [Tables](formatting-examples/04-tables.md)

### Progressive depth

- [Collapsible details](formatting-examples/05-collapsible-details.md)
- [Footnotes](formatting-examples/06-footnotes.md)
- [Quotes, notes, and callouts](formatting-examples/07-quotes-notes-and-callouts.md)

### Technical content

- [Inline and block code](formatting-examples/08-inline-and-block-code.md)
- [File trees](formatting-examples/09-file-trees.md)
- [Comments and generated banners](formatting-examples/10-comments-and-generated-banners.md)
- [Images and alternative text](formatting-examples/11-images-and-alt-text.md)

### Visual and structured enhancements

- [Mermaid diagrams](formatting-examples/12-mermaid-diagrams.md)
- [Mathematical expressions](formatting-examples/13-mathematical-expressions.md)
- [YAML properties and tags](formatting-examples/14-yaml-properties-and-tags.md)
- [Obsidian links and embeds](formatting-examples/15-obsidian-links-and-embeds.md)
- [Page footer navigation](formatting-examples/16-page-footer-navigation.md)
- [Editor folding](formatting-examples/17-editor-folding.md)
- [Markmap view](formatting-examples/18-markmap-view.md)
- [Editable SVG diagrams](formatting-examples/19-editable-svg-diagrams.md)
- [Renderer verification fixture](formatting-examples/20-renderer-verification-fixture.md)

### Renderer matrix

| pattern | VS Code 1.141 built-in | GitHub Markdown | dependable baseline |
|---|---|---|---|
| headings, lists, tables, relative links | documented; visual pass pending | documented | use directly |
| task lists | documented; visual pass pending | documented | source remains a readable list |
| `<details>` / `<summary>` | visual pass pending | documented | replace with a heading when unsupported |
| GitHub alerts | readable as a block quote; special styling needs an extension | documented | keep the alert text explicit |
| Mermaid fenced blocks | documented; built-in renderer present; visual pass pending | documented | include a text mapping |
| inline math `$...$` | documented with KaTeX; visual pass pending | documented with MathJax | use only after the target pass |
| display math `$$...$$` | documented with KaTeX; visual pass pending | documented with MathJax | use only after the target pass |
| `\\label`, `\\ref`, broad macro sets | not established | renderer-dependent | state labels and references in prose |
| Markdown region markers | documented for the VS Code source editor | comments are hidden | editor convenience only |
| Markmap | optional extension; not installed by the protocol | not native | headings remain authoritative |
| linked SVG | documented; visual pass pending | documented | provide alt text and source link |
| Obsidian wikilinks, embeds, callouts | untested | not portable | do not use in governed collections |

Use `20-renderer-verification-fixture.md` for the visual pass. Re-run it after a
renderer upgrade before changing this matrix.

### Verification sources

- [VS Code Markdown preview, Mermaid, and mathematics](https://code.visualstudio.com/docs/languages/markdown)
- [VS Code folding and Markdown region markers](https://code.visualstudio.com/docs/editing/codebasics#_folding)
- [GitHub Mermaid diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
- [GitHub mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions)
- [GitHub collapsed sections](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections)
- [GitHub alerts and task lists](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [Markmap VS Code source and usage](https://github.com/markmap/markmap-vscode)

---

[← Previous](layouts.md) · [⌂ Home](../INDEX.md) · [Next →](visual-patterns.md)
