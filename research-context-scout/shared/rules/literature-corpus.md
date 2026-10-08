# Literature Search, Acquisition And Corpus

Use from the landscape preview through source/PDF reading. It defines which
papers may enter synthesis and prevents a candidate list from becoming evidence.

## Source-selection order

Prefer, in order:

1. the newest credible review or perspective covering the objective;
2. primary results published after that review's search cutoff;
3. recent primary papers achieving the same or nearby objective;
4. the seminal source for an original theorem, model or mechanism; and
5. older work only when canonical, historically necessary or not superseded.

Age alone never proves that a source is obsolete. Assign one role:
`current-synthesis`, `post-review-update`, `recent-primary-result`,
`seminal-origin`, `supporting-method`, `no-go-or-bound`, `historical-only` or
`possibly-superseded`. The last role needs an inspected later source or version
record; it is not inferred from publication year.

## Bounded search closure

Scout cannot claim all papers globally. Record the query families, search
lanes, sources searched, date cutoff, backward/forward citation closure,
inclusion and exclusion rules, inaccessible sources, unsearched regions and
stopping condition. Search saturation or budget exhaustion remains `unknown`
outside that boundary.

The landscape preview groups candidates by achievement, mechanism,
mathematical structure, realization, application, bound/no-go result and
terminology alias. It includes representative sources and status, not a long
unstructured bibliography.

Carry only the projected candidate fields: canonical identity, year, title,
venue and role hypothesis. A raw search payload is working data; it never enters
the record, the preview or the report.

## Acquisition manifest

For each selected source record:

```text
canonical identity and version:
year and source role:
relation hypothesis:
decision it may change:
stable landing page:
full-text/PDF availability:
download priority: essential | useful | background
local state: missing | available | duplicate | wrong-version | failed | unknown
```

A source is **locally available** when the host's configured reference library
holds its full text, or the user supplied it as a local file. Check availability
with the library's own read tools before asking the user for anything.

Scout never acquires silently: the record-only authority does not permit
automatic downloads or writes elsewhere. Present the acquisition manifest once
and add sources only after the user confirms it. One confirmation covers the
whole manifest, not one source at a time.

### Backend health probe

Host-neutral, and required before any absence claim. A backend is **healthy for
this check** only when a control probe succeeds: the same backend, in the same
session, returns an item you already know it holds. Use a source already marked
`available` in this record, or any item the user named as present. If no control
item exists, or the probe fails or errors, backend health is **unverified**.

A control probe is the only thing that establishes health. Tool success, an
empty result, a fast response and a prior probe in an earlier session do not.

### Three states that look alike

- **absent** — the backend is healthy for this check *and* an exact
  canonical-identity lookup explicitly reports it does not hold the source. This
  is the only normal acquisition trigger.
- **unreachable** — the backend did not answer, or answered with an error.
- **unknown** — anything else, including an empty or successful search on a
  backend whose health is unverified.

Record `unreachable` and `unknown` as `local state: unknown`, and name the
backend and which of the two applies. An empty library search is never evidence
of absence by itself, an unreachable library cannot establish that a source is
missing, and a missing library is never evidence about the literature.

Before stopping, try another healthy backend or a user-supplied local file. One
unreachable backend is not a reason to stop when another can answer.

### Pass-shape and authority guards

Host-neutral, and binding on every wrapper:

- If a pass-1 extractor returns a full paper body, reclassify that call as
  pass 2 and charge it to the source-read budget. Do not carry the body as
  cheap coverage context.
- Never infer that a host approval setting will prompt the user. Obtain
  explicit user authority for the acquisition or deep read before calling a
  pass-2 tool.

A wrapper supplies the host's tool names for these guards. It never restates,
narrows or replaces the guards themselves.

## Incorporation rule

Every paper incorporated into the collective synthesis must be locally
available as full text, successfully extracted, assigned a source status and
anchored to the relevant page, section or equation when possible. A title,
snippet, abstract, inaccessible source or failed extraction may remain in the
candidate/acquisition ledger but cannot influence a mathematical idea,
relationship, gap, importance claim or report conclusion.

Record selected, locally available, successfully extracted, deep-read, used,
excluded and failed counts.

Corpus readiness is `pending` whenever any source selected for synthesis is not
both available and successfully extracted. `missing`, `unknown` and `failed` all
hold it pending; only the remedy differs:

| State | Remedy offered | May be excluded on this basis |
|---|---|---|
| `missing` (absence established) | acquire it, or confirm exclusion | yes, with user confirmation |
| `failed` extraction | replace it, or confirm exclusion | yes, with user confirmation |
| `unknown` (unreachable or health unverified) | repair or change backend, or supply the file | **never** |

An `unknown` source is an unfinished check, not a verdict about the literature,
so it can neither be excluded nor counted as absent. Proceeding to synthesis
while any selected source is still `unknown` is not permitted; report the
backend problem instead. An excluded source cannot influence the collective
synthesis.

## Two-pass reading

**Pass 1 — Coverage extraction** applies to every incorporated paper and must
not load its full text. Use the host's structured extractor to record identity,
problem/achievement, system/regime, initial resource, target, governing
dynamics, controls/constraints, mechanism, observable, mathematical idea,
result, assumptions, limitations and evidence anchors.

A pass-1-only source supplies context, relation candidates and acquisition
decisions. It cannot reach `equation-checked` or `result-verified` in
`source-status.md`, so it cannot carry an equation-level or verified-result
claim on its own.

**Pass 2 — Decisive deep reading** loads full text, is capped by the
source-read budget, and is reserved for same-objective, contradictory, no-go,
equivalence-critical and direction-supporting papers. Keep individual
extraction cards in the record as evidence; do not dump one card per paper into
the main report.

Write each extraction once and reuse it. A later cycle re-reads a source only
when the delta changes what that source must answer.

---

[⌂ Home](../../README.md)
