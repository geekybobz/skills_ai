# Add-on Contract

## In brief

An add-on adapts the Markdown Protocol to one recurring use case. It may add
optional blocks, layout variants, generated views, and focused checks. It may
not weaken the core invariants, replace the proportional review gate, or make a
plugin necessary to understand the result.

Load this contract when creating or revising an add-on. Ordinary Markdown work
loads only the selected add-on, not this file or every sibling add-on.

## Required declaration

Each add-on is one focused reference that declares:

| field | question answered |
|---|---|
| Trigger | When does this add-on apply, and when does it not? |
| Outcome | What useful result should the reader receive? |
| Blocks | Which optional content units may be selected? |
| Layout variants | How may the core layouts be adapted? |
| Generated views | Which replaceable projections may be produced, if any? |
| Checks | What extra evidence or validation is required? |
| Composition | Which domain skill or tool owns subject correctness? |
| Boundaries | What must the add-on never require or authorize? |

The declaration describes capabilities, not a quota. The model analyzes the
topic and proposes the minimum useful combination; the user reviews the actual
structure through the core workflow.

## Extension points

### Blocks

A block is a small optional content pattern owned by the topic that uses it.
Examples include a recall card, responsibility map, or decision summary. A
block cannot hide a rule or create a second authoritative copy of a fact.

### Layout variants

A variant changes emphasis or ordering while preserving the Front Door, topic,
ownership, `## Details`, portability, and footer contracts. It does not force a
new file or heading when the content does not justify one.

### Generated views

A generated view declares its canonical source, generator, output, freshness
check, and replacement rule. It is optional and non-authoritative. An add-on
with no useful generated view states `None` rather than inventing one.

### Checks

Checks supplement core validation. They may verify domain-specific links,
source mappings, card fields, or generated freshness. They do not claim that
structural validity proves factual correctness or visual quality.

## Composition and authority

The add-on owns presentation for its use case. The subject skill, source code,
paper, dataset, or other named owner remains authoritative for domain facts.
Selection grants no network, installation, external-write, or repository-wide
migration authority.

## Add-on review checklist

- The trigger is discriminating and names a meaningful exclusion.
- Every block, variant, view, and check solves a repeated problem.
- Optional capabilities remain optional in actual output.
- Generated views have one canonical source and a freshness check.
- Core invariants and the review gate remain unchanged.
- Portable text preserves essential meaning.
- The add-on has one focused owner file and is routed from `SKILL.md`.
- Tests check decisions or observable behavior, not only heading names.

## Details

An add-on should remain guidance until repeated mechanics justify a script.
Adding a script, external tool, workspace configuration, or generated artifact
is a separate implementation decision subject to repository change control.

---

[⌂ Home](../../INDEX.md)
