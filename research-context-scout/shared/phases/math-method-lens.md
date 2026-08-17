# Math Method Lens

Use only when the user asks for mathematical side explanation, tricks,
techniques, or deeper method comparison after Scout has locked the physics
objective and existing-work verdict.

This lens is subordinate to Scout. It explains methods; it does not decide
novelty, journal level, physical feasibility, or the existence of a gap.

## Preconditions

Before using this lens, the record must contain:

- physics objective;
- mathematical formulation or the specific missing formulation;
- existing-work verdict; and
- current gap predicate or reason no gap is established.

If those are missing, return to the relevant Scout gate first.

## Method explanation contract

Explain only the math that helps the current decision:

```text
method family:
symbols and state space:
why the method fits or fails:
useful trick or transformation:
minimum worked example:
connection to the physics objective:
does it change the gap verdict: yes/no/unknown
next mathematical check:
```

Examples of valid topics include PMP/BVP structure, endpoint constraints,
reachable-set geometry, perturbation expansions, symmetry reductions,
basis restrictions, exact penalty/KKT checks, numerical residuals and
counterexamples.

## Boundaries

- Do not present familiar method families as new research directions.
- Do not use mathematical elegance as evidence of physical importance.
- Do not claim unrestricted optimality from a restricted-family calculation.
- Do not claim physical realizability from mathematical reachability alone.
