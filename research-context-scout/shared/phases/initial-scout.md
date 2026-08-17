# Initial Scout

Use for a newly supplied project, an orientation record whose intake questions
have not yet been answered, or an answered record whose physics objective,
existing-understanding ledger, relation map, or gap verdict is still empty.
For the answered case, skip Cycle A and run Cycle B.

## Cycle A — reconstruct and ask

1. Resolve the named project path and optional focus. Never guess across
   projects.
2. Inventory filenames cheaply, then inspect only likely entry documents,
   central equations, main code/results and directly referenced material.
3. Record a provisional input lock (G0) in the template's Input lock and Active
   project state fields, plus the decision most likely to change the research
   direction.
4. Create or update only `research-orientation.md` using the shared template.
5. Ask one to three questions whose answers materially affect scope,
   importance, evidence or paper direction. Do not ask the user to supply
   literature, applications or use cases the scout can investigate.
6. Tell the user to answer in the record and stop. Do not conduct the deep
   literature/application pass before this interaction unless the user already
   supplied answers or explicitly delegated the assumptions.

If the user does not care about technical choices, record defensible defaults
and continue rather than repeatedly asking.

## Cycle B — orient after answers

1. Read the user-response block without editing it.
2. Record the agent interpretation and any explicit assumptions separately.
3. Lock the physics objective before method explanation (G1):
   - operation or phenomenon;
   - physical system and regime;
   - measurable success criterion;
   - target consumer or reason the result matters; and
   - the tier, which fixes the search budget below.
4. Extract the mathematical formulation only as far as needed to compare
   assumptions: state, controls/variables, objective, constraints and evidence
   (G2).
5. Read `rules/alignment-checkpoints.md` and `rules/source-status.md`. Run only
   the smallest pilot query needed to expose plausible vocabulary, nearby
   achievements or search lanes. Present the G2A context mirror with those
   possibilities marked `search-candidate`; write its response markers and
   stop unless the user already confirmed, corrected or delegated this
   alignment.
6. After context alignment, read `rules/literature-corpus.md`. Run the structured
   G3 landscape preview across the same objective, mechanisms, mathematical
   structures, nearby realizations, applications, bounds and no-go results.
   Include the newest credible synthesis, primary results after its cutoff and
   necessary seminal sources. Present the clusters and stop unless the user has
   aligned the search lanes.
7. After search alignment, complete the bounded search within the tier budget,
   record its queries, cutoff, citation closure and unsearched regions, and
   prepare the G3A acquisition manifest. Check the library before asking the
   user for anything, then present the manifest once and stop until every paper
   selected for synthesis is locally available as full text. Scout does not
   acquire papers without separate authority.
8. At G4, run pass-1 coverage extraction for every selected paper without
   loading its full text, then spend the source-read budget on pass-2 deep reads
   of the decisive same-objective, contradictory, no-go, equivalence and
   direction-supporting sources. `rules/literature-corpus.md` owns what a failed
   extraction does to corpus readiness.
9. Read `rules/relation-taxonomy.md` and `rules/collective-synthesis.md`.
   Normalize achievements, models, mechanisms, equations and terminology;
   build relation labels and explicit transfer conditions (G5). If a material
   interpretation can change the direction, present an alignment packet and
   stop until it is confirmed, corrected or delegated.
10. Separate (G6):
   - what existing work already achieves;
   - what the project may add;
   - what remains unknown.
11. At G6A, combine the useful mathematical ideas across the extracted corpus,
    translate them into the project's notation, and state candidate
    re-derivations with assumptions, boundaries and first checks. Keep
    paper-by-paper cards in the evidence record; the user-facing result is a
    compact collective synthesis.
12. Read `rules/anti-hallucination.md` and apply `rules/evidence-gate.md` to
   formulate a gap predicate. A gap predicate
   requires at least one `source-read` comparison; an empty or abstract-only
   search yields `existing-work verdict: unknown`, not a gap. If no gap survives,
   or the search is unknown, recommend reproduce, benchmark, cite, search further
   or stop instead of inventing a new direction (G7).
13. If a gap survives, read `rules/journal-thresholds.md`, assign the minimum
   target, and state the exact evidence needed to level up (G8). Read
   `rules/journal-level-up.md` only when arguing above that target.
14. Formulate the strongest direction and no more than two credible
   alternatives. Each must include a falsifier and next test (G9).
15. Update the compact active state, alignment states, search boundary, corpus
   coverage, collective ideas and project translations in the record. Render
   the concise beginner-facing synthesis from `rules/collective-synthesis.md`;
   do not dump individual paper cards or search output.
16. Close the cycle with a bounded result review (G10): stay on the direction,
   stop it, reproduce or benchmark the existing result, adapt the direction, or
   level up the threshold. Record the supporting evidence, the uncertainty that
   matters most and the gate reached before writing the brief.
17. If the user asks for mathematical tricks, techniques, or method comparison
   after steps 3-12 are recorded, read `phases/math-method-lens.md`. That lens cannot
   change the physics objective, existing-work verdict or gap predicate.

## Tier budget

The tier recorded at G1 caps the scan.

| Tier | Problem | Query lanes | Source reads |
|---|---|---|---|
| T1 | known technique applied to a standard setting | 1 | 3 |
| T2 | extension of a published result | 3 | 8 |
| T3 | open or contested question | 5 | 15 plus citation closure |

A query lane funds one search direction. The pilot query and preview fit inside
the tier budget; they do not silently add another budget. The G3 preview groups
only the dimensions its funded lanes actually reach and records the remainder as
unsearched regions; it never presents a cluster it did not search. Never exceed a
budget silently and never raise it without saying so. If the budget is spent before the orientation is clear, record
`existing-work verdict: unknown` together with the unsearched lanes and stop.
An exhausted budget is a search state, never a gap.

## Initial stop rule

Stop when every gate reached has produced the output named in the gate table and
the brief can state the current orientation, the uncertainty that matters most,
and the next investigation. Record the highest gate reached, and the gate and
reason when the cycle stops early.

Do not claim confirmed novelty, a confirmed gap, global optimality, physical
feasibility or venue suitability without the evidence required for that claim.
