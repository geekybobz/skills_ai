# Slides Add-on

Use this add-on when an existing topic should become a short teaching,
presentation, or review deck. The deck is a reader-specific projection; the
topic note remains the owner of detailed facts, references, and qualifications.

## Outcome

A compact Marp-compatible Markdown deck communicates one narrative, links back
to its source topics, and can still be read as ordinary Markdown.

## Add-on declaration

| field | declaration |
|---|---|
| Trigger | A topic needs a sequential presentation for teaching, review, or communication; not every topic note or ordinary documentation page |
| Blocks | Audience, learning goal, narrative spine, slides, source links, speaker notes, and verification status |
| Layout variants | Concept lesson, project overview, decision briefing, or worked-example deck |
| Generated views | Optional HTML, PDF, PPTX, or image export from the canonical deck Markdown |
| Checks | Source traceability, one idea per slide, overflow, contrast, image paths, mathematics, export target, and generated freshness |
| Composition | Topic notes own facts; Marp and the target renderer own presentation and export behavior |
| Boundaries | No copied source corpus, slide-only rule, hidden qualification, untrusted HTML enablement, mandatory extension, or unverified export claim |

## Details

## Source relationship

Record the source topics near the top of the deck. Summarize rather than copy,
and link to the owner whenever a statement needs assumptions, evidence, or
maintenance detail. A topic update makes the deck reviewable; it does not
silently rewrite the presentation.

```markdown
---
marp: true
title: Short deck title
---

# Short deck title

Audience and one learning goal.

Sources: canonical topic using its real relative link

---

## First idea

- One claim
- One supporting relation
- One takeaway
```

The first `---` pair is metadata; later `---` lines separate slides. Keep this
distinction obvious when a deck also uses protocol properties.

## Narrative spine

Before drafting slides, write a one-line route:

```text
question -> model or idea -> evidence or example -> boundary -> takeaway
```

Use only the stages the audience needs. Prefer one major idea per slide and a
visible conclusion over compressing the topic note into small text.

## Visual and teaching rules

- Use a diagram only when it clarifies the current slide's relationship.
- Keep the portable table or concise explanation in the source topic rather
  than duplicating a dense fallback on the slide.
- Put optional elaboration in speaker notes or the linked topic, not in tiny
  text.
- For equations, define symbols before using them and verify both preview and
  the requested export; renderer success is target-specific.
- Keep image assets inside the workspace with stable relative paths.
- Use local, reviewed theme CSS when customization is necessary; remote themes
  and raw HTML increase portability and trust risk.

## Preview and export

Marp for VS Code recognizes `marp: true`, provides preview and directive
diagnostics, and can export through its bundled CLI. PDF, PPTX, and image export
require a compatible installed browser. Exported artifacts are generated and
must name their source deck and freshness method.

Treat preview and each export format as separate targets. A correct preview
does not prove that fonts, images, mathematics, page breaks, or speaker notes
survive a PDF or PPTX export. Experimental overflow diagnostics can assist but
do not replace visual inspection.

Do not enable unrestricted HTML for an untrusted deck. VS Code workspace trust
and Marp's HTML restrictions are safety boundaries, not rendering obstacles to
bypass.

Official reference: [Marp for VS Code](https://github.com/marp-team/marp-vscode/blob/main/README.md).

## Validation

- Audience, goal, source topics, and narrative spine are explicit.
- Each slide has one main idea and readable content at presentation scale.
- Claims and qualifications trace to canonical topics or cited sources.
- Relative images resolve inside the workspace.
- Mathematics and diagrams were checked in the VS Code preview when used.
- Every requested export format was generated and visually inspected, or is
  reported separately as `unverified`.
- Exported artifacts identify the source deck and are replaceable.
- The deck remains understandable without the Marp extension.
- Raw HTML, remote themes, and external assets are absent unless explicitly
  reviewed and necessary.

---

[⌂ Home](../../INDEX.md)
