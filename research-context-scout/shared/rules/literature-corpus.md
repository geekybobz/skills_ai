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
local state: missing | available | duplicate | wrong-version | failed
```

A source is **locally available** when the host's configured reference library
holds its full text, or the user supplied it as a local file. Check availability
with the library's own read tools before asking the user for anything.

Scout never acquires silently: the record-only authority does not permit
automatic downloads or writes elsewhere. Present the acquisition manifest once
and add sources only after the user confirms it. One confirmation covers the
whole manifest, not one source at a time.

Separate two states that look alike and are not:

- **absent** — the same backend has independent positive health evidence for
  the current check, and an exact canonical-identity lookup explicitly reports
  that it does not hold the source. This is a normal acquisition trigger.
- **unreachable** — the library did not answer. This is an infrastructure
  failure. Report it as `local state: unknown (library unreachable)`, name the
  backend, and never convert it into a corpus-readiness stop or an exclusion.

An empty or successful library search is not evidence of absence by itself. If
backend health is not independently established, classify the result as
`unknown (backend health unverified or unreachable)`, not `absent`. An
unreachable library cannot establish that a source is missing, and a missing
library is never evidence about the literature. Do not stop the corpus solely
because one backend is unreachable; try another healthy backend or a supplied
local file.

## Incorporation rule

Every paper incorporated into the collective synthesis must be locally
available as full text, successfully extracted, assigned a source status and
anchored to the relevant page, section or equation when possible. A title,
snippet, abstract, inaccessible source or failed extraction may remain in the
candidate/acquisition ledger but cannot influence a mathematical idea,
relationship, gap, importance claim or report conclusion.

Record selected, locally available, successfully extracted, deep-read, used,
excluded and failed counts. If any source selected for synthesis is missing or
fails extraction, mark corpus readiness `pending` and stop until the user
confirms its exclusion or replacement. An excluded source cannot influence the
collective synthesis.

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
