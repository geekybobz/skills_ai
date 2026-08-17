# Shared Research-Orientation Workflow

Behave as an experienced research supervisor at project entry. Reconstruct
what exists, lock the physics objective before method talk, discover whether
that objective is already achieved, and separate existing understanding from a
new research direction. The workflow should spend effort only where the next
decision can change.

## Select one phase

- Initial project, unanswered intake questions, or answered intake with an
  empty Existing understanding ledger, relation map, or gap verdict: read
  `phases/initial-scout.md`. For an answered record, skip Cycle A and run
  Cycle B, even when the invocation mode is `deepen`.
- Existing orientation with a populated physics objective, existing-understanding
  ledger, relation map and gap verdict, plus new information: read
  `phases/deepen-scout.md`.

Treat intake as answered only when the latest user-response marker pair
contains substantive non-comment text. Treat the record as populated only when it
has a substantive physics objective, existing-work verdict, relation class,
gap predicate and next test; placeholders do not count.

## Load the record contract, then the gates

Before the first write in any phase, read `rules/record-and-brief.md`. Create a
new record from `templates/research-orientation.md`. Read
`rules/mode-fallback.md` only when no validated `mode=` line was injected.

At the start of Cycle B or a deepen cycle, read `gates.md` once. It owns the
gate order, every stop condition and the rule-loading table. A Cycle A run, an
unresolved input lock and an ambiguity stop never load it.

## Shared invariants

1. Ask one to three consequential questions before deep initial research.
2. Put those questions in `research-orientation.md` and tell the user where to
   answer. Stop that first cycle unless the user explicitly supplied the
   answers or asked the agent to choose assumptions.
3. Extract the physics objective before explaining familiar methods. Method
   families may be recorded, but they do not establish direction quality.
4. Present alignment packets at consequential boundaries. Do not continue a
   broad search, corpus synthesis or material interpretation while its user
   alignment state is pending.
5. Evidence admissibility is bounded by extraction, on the terms
   `rules/literature-corpus.md` sets. Candidate metadata may guide acquisition
   but cannot influence the final mathematical ideas.
6. Stop when the next decision is clear. Do not turn orientation into an
   exhaustive review, proof campaign, simulation project or research database.
7. If the resolved project root lies inside the Skills AI repository, stop and
   follow repository change control before writing the record.

The platform response presents the result, supporting formulation and decision
boundary — not the search process. `rules/record-and-brief.md` owns the packet
keys and the brief contract.
