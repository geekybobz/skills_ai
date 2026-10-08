# Research Notes Add-on

Use this add-on when Markdown must preserve what a paper, dataset, experiment,
or technical source actually supports. It structures the note; it does not
perform literature search, judge scientific truth, or replace the source.

## Outcome

A reader can identify the source, separate evidence from interpretation, trace
important claims, and see how the source relates to the surrounding literature.

## Add-on declaration

| field | declaration |
|---|---|
| Trigger | Source-backed research notes, literature reviews, or evidence maps; not informal brainstorming with no cited source |
| Blocks | Source identity, claim ledger, methods snapshot, limitations, relevance, and literature links |
| Layout variants | One paper note, one topic synthesis, or a routed collection of notes plus a literature map |
| Generated views | Optional bibliography or literature map generated from canonical citation keys and typed links |
| Checks | Resolvable citation, evidence labels, claim-to-source traceability, link validity, and generated freshness |
| Composition | The source and the evidence-owning research skill remain authoritative; `research-context-scout`, when selected, owns discovery and evidence assessment |
| Boundaries | No invented citation, unsupported certainty, hidden source status, automatic paper acquisition, or claim that formatting proves correctness |

## Paper-note template

Use a stable citation key as the note identifier when a citation manager is
already present. Zotero with Better BibTeX is a useful option, not a protocol
dependency. Record enough fallback metadata that the note remains intelligible
without Zotero.

```markdown
---
title: "Exact source title"
citation_key: "AuthorYearShortTitle"
source_type: "journal article | preprint | dataset | thesis | other"
source_status: "published | accepted | preprint | retracted | unknown"
reviewed: YYYY-MM-DD
tags:
  - domain/example
  - use/research
---

# Exact source title

## In brief

Two or three sentences: question, result, and why this source matters here.

## Claim ledger

| claim | evidence status | location | note |
|---|---|---|---|
| concise claim | exact, empirical, numerical, proposed, or uncertain | section, page, figure, or dataset field | boundary or interpretation |

## Methods snapshot

- System or sample:
- Method:
- Assumptions:
- Comparison or control:

## Limitations

- Source-stated limitation or clearly labelled reader inference.

## Relevance

- What this changes, supports, or leaves open for the current topic.

## Connections

- Related: [Topic](../topic.md) — short relation
```

Use the source's own terminology for its result. Keep a numerical observation,
a proposed mechanism, a feasibility demonstration, and a proof as different
evidence categories. Add page, section, figure, theorem, or dataset pointers
when the claim matters to later work.

## Evidence status

Use the smallest vocabulary the project needs, but define it once. A practical
baseline is:

| status | meaning |
|---|---|
| exact | derived or proved under stated assumptions |
| empirical | supported by reported observation or experiment |
| numerical | supported by computation within stated scope |
| proposed | mechanism, method, or interpretation advanced but not established |
| uncertain | ambiguous, conflicting, incomplete, or not yet checked |

These labels describe the support recorded in the note, not universal truth.
When the note author infers something beyond the source, label it `inference`
in the note column and explain the reasoning briefly.

## Literature map

Prefer a typed table as the canonical readable view. Use a small Mermaid map
only when it clarifies several relationships, and keep the table as fallback.

| source | relation | target | reason |
|---|---|---|---|
| citation key | extends, contrasts, reproduces, uses, reviews, or contextualizes | citation key or topic | one precise sentence |

A generated map may project these typed rows, but it must declare its source,
generator, revision or fingerprint, and regeneration command. The graph shows
recorded relationships; it does not establish influence, priority, or consensus.

## Validation

- Every citation key resolves to the project's bibliography or carries complete
  fallback metadata and a stable source link.
- Important claims include an evidence status and a source location.
- Inference is visibly separate from source-reported content.
- Retraction, preprint, or unknown status is not hidden.
- Literature links use defined relation types and one-sentence reasons.
- No citation, quotation, result, or access status is invented.
- Generated bibliography or map views are replaceable and freshness-checked.

---

[⌂ Home](../../INDEX.md)
