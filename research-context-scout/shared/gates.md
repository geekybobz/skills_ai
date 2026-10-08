# Gates And Rule Loading

Read once at the start of Cycle B or a deepen cycle. Cycle A, an unresolved
input lock and an ambiguity stop never reach a gate and never need this file.

## Load rules at their own gate, never as a bundle

| Read | When |
|---|---|
| `rules/alignment-checkpoints.md` | before the context mirror (G2A) and every later user-alignment stop |
| `rules/literature-corpus.md` | search preview, bounded closure, acquisition and corpus work (G3-G4) |
| `rules/relation-taxonomy.md` | building the comparison matrix (G5) |
| `rules/source-status.md` | ranking candidates and reading sources (G3, G4) |
| `rules/anti-hallucination.md` | before promoting a source result into a claim (G6, G7) |
| `rules/collective-synthesis.md` | normalization, project translation and beginner report (G5-G10) |
| `rules/evidence-gate.md` | grading or ranking a direction (G7, G9) |
| `rules/journal-thresholds.md` | only after a gap predicate exists (G8) |
| `rules/journal-level-up.md` | only when arguing above the current threshold (G8) |
| `phases/math-method-lens.md` | only on an explicit user request for method or trick explanation, after the physics objective is locked |

`rules/record-and-brief.md` and `templates/research-orientation.md` load from
`SKILL.md` instead, because Cycle A needs them before any gate is reached.

## Gate order

Run the gates in order. Stop at the first gate whose stop condition holds, or
whose missing information would change the decision, and record where you
stopped.

| Gate | Output | Stop if |
|---|---|---|
| G0 input lock | exact problem, target path, focus, assumptions | the path is missing, ambiguous, or spans projects |
| G1 physics objective | system, operation, observable, success metric, tier | the objective needs a user choice to be stated |
| G2 math formulation | state, controls/variables, constraints, objective | — |
| G2A context alignment | context mirror, pilot-search directions, user status | the user has not confirmed, corrected or delegated the context |
| G3 landscape preview | structured search clusters, recent synthesis and candidate sources | the user has not aligned the search lanes |
| G3A bounded closure | search boundary, acquisition manifest and corpus plan | corpus readiness is `pending`, or the user has not confirmed the manifest |
| G4 corpus extraction | coverage extraction for every incorporated paper and decisive deep reads | a selected source failed extraction without user-confirmed exclusion or replacement |
| G5 relation map | normalized achievement/model/mechanism and physics-math relation | a material mapping remains unaligned |
| G6 existing vs new ledger | known results separated from proposed differences | nothing survives into the new direction ledger |
| G6A collective synthesis | useful cross-paper ideas translated into project notation | no idea has a source-supported project mapping |
| G7 gap predicate | real gap, why it matters, falsifier | no gap survives; recommend reproduce, benchmark, cite or stop |
| G8 journal ladder | minimum target and level-up conditions | the relation forces J0 |
| G9 next test | smallest derivation, source check, benchmark, or simulation | — |
| G10 result review | stay, stop, reproduce, adapt, or level up | closes every cycle |

Everything else a gate needs is stated once, in that gate's rule file. Do not
restate a rule here, in a phase, or in a wrapper.

---

[⌂ Home](../README.md)
