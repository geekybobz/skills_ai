# Anti-Hallucination Rule

Use this rule whenever Scout moves from search results or project artifacts to
claims, gaps, directions, or paper targets.

## Hard boundary

No claim may be stronger than its inspected evidence. If the agent has not read
the relevant source section, local artifact, derivation, or numerical output,
the claim must stay `candidate`, `unknown`, or `hypothesis`.

No paper may influence collective synthesis unless it also satisfies the local
full-text and successful-extraction rule in `literature-corpus.md`. Acquisition
or indexing is not evidence.

## Two ledgers

Maintain two distinct ledgers.

Existing understanding ledger:

- what a source or project artifact already establishes;
- the physical objective achieved;
- the mathematical method and assumptions;
- the result strength and limits; and
- what project claim it already settles.

New direction ledger:

- the proposed difference from existing work;
- why that difference is not already settled;
- the physical importance of the difference;
- the required evidence;
- the first falsifier; and
- the next test.

A source result cannot enter the new direction ledger until the existing
understanding ledger states what the source already achieved.

## Promotion rule

Before recommending a direction, answer all four questions:

1. What existing work already achieves the same or nearby physics objective?
2. What does that work not achieve under the project's assumptions?
3. Why does the remaining difference matter physically?
4. What test would falsify the proposed gap?

If any answer is missing, downgrade the direction to candidate or recommend
reproduction/benchmarking instead.

## Answer admissibility

An answer counts only if it names an inspected artifact.

- Questions 1 and 2 require at least one source at `source-read` or stronger. If
  the strongest source for the nearest objective is `search-candidate` or
  `abstract-only`, the direction stays `candidate`.
- "Nothing found" is not an answer to question 1. Record it as
  `existing-work verdict: unknown`, name the lanes searched and the lanes not
  searched, and keep the direction at `candidate`. Absence of results is a search
  state, never a gap.
- Record the gap predicate as `established` only when question 1 is answered from
  a read source and question 2 names the specific assumption, regime, observable
  or bound that source does not cover.

## Source-status limits

Source status tokens and their allowed use are defined in `source-status.md`.
Never exceed the allowed use of the recorded status, and never leave a cited
source without one.

---

[⌂ Home](../../README.md)
