---
name: markdown-protocol
description: Use for tasks whose primary artifact is Markdown, including creating, editing, reviewing, or restructuring README files, documentation, notes, and connected Markdown collections. Apply portable navigation, progressive disclosure, proportional design review, and human- and LLM-readable topic ownership. Do not activate merely because Markdown instructions are read as operational input.
---

# Markdown Protocol

Use one knowledge structure at several reading depths. Keep the outer route
compact, place authoritative detail in focused topics, and expose optional
depth without requiring every reader or model to load it.

## Load only what the task needs

1. Read [core-protocol.md](references/core-protocol.md) for every task.
2. Read [review-workflow.md](references/review-workflow.md) before proposing or
   making a Markdown write.
3. Read [layouts.md](references/layouts.md) when creating, splitting, merging,
   or reorganizing files.
4. Read [markdown-patterns.md](references/markdown-patterns.md) only when
   choosing formatting or helping a human learn Markdown.
5. Read [visual-patterns.md](references/visual-patterns.md) only when a diagram
   or other visual would materially improve understanding.
6. Read [validation.md](references/validation.md) before finishing a change.
7. Read [education.md](references/addons/education.md) when the Markdown is
   intended for learning, teaching, revision, or explaining unfamiliar ideas.
8. Read [codebase.md](references/addons/codebase.md) when documenting a codebase,
   repository structure, runtime workflow, or change impact.
9. Read [skill-package.md](references/addons/skill-package.md) when creating,
   documenting, or substantially restructuring a skill package.

The small files under `references/formatting-examples/` are human learning
examples. Open only the example relevant to the current question; do not load
the whole gallery during ordinary work.

For human browsing or package maintenance, use [INDEX.md](INDEX.md). Do not
load the index during ordinary task execution.

## Core behavior

- Activate automatically when Markdown is the requested artifact; `#>
  md_protocol` is the explicit force-selection alias. Merely reading a Markdown
  instruction, skill, or source as input to another task is not activation.
- Announce that the protocol applies before substantive Markdown work.
- For a read-only review, assess the material without inventing a write gate.
- Before any Markdown write, inspect the relevant existing structure, present
  a proportional proposal, and wait for the user's agreement. A local edit
  needs only a short preview; structural work needs the architecture, file
  impact, ownership, navigation, portability, and validation plan.
- After approval, continue within the agreed design without repeatedly asking.
  Pause again only for material expansion such as new files, changed ownership,
  a different layout, or new renderer-specific dependencies.
- Inspect the target and preserve useful existing conventions.
- Choose the smallest layout that keeps orientation and navigation clear.
- Give every important fact one authoritative owner.
- Summarize and link from outer layers instead of duplicating deep content.
- Prefer relative Markdown links and portable source syntax.
- End every authored Markdown page handled by the protocol with the compact
  navigation footer defined in [core-protocol.md](references/core-protocol.md):
  Home is mandatory; Previous and Next are required when a real reading order
  exists. Put the footer into the canonical generator for generated pages.
- Keep essential meaning outside renderer-specific diagrams, callouts, embeds,
  databases, or plugins.
- Mark generated material and never hand-maintain it as canonical prose.
- Treat mathematical rendering as renderer-dependent until the exact syntax is
  verified in the requested environments.

When another skill owns the subject matter, compose them: that skill owns
domain correctness and Markdown Protocol owns document architecture,
navigation, portability, review, and Markdown-specific validation.

This protocol does not grant permission to rewrite unrelated documentation,
install plugins, introduce a documentation site, or generate background
indexes. Specialized research and operations add-ons remain deferred.

---

[⌂ Home](INDEX.md)
