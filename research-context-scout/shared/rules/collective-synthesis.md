# Collective Mathematical Synthesis And Report

Use after corpus extraction. The purpose is to turn inspected papers into a few
useful, project-specific mathematical ideas without pretending that Scout makes
the user's final expert decision.

## Normalize before comparing

For the project and each decisive source, compare:

\[
\text{Achievement}=(\text{input},\text{transformation},\text{output},
\text{metric},\text{regime}),
\]

\[
\text{Model}=(\text{state space},\text{dynamics},\text{controls/resources},
\text{constraints},\text{noise}),
\]

\[
\text{Mechanism}=(\text{resource},\text{pathway},
\text{exchanged or conserved quantity}).
\]

Maintain an alias ledger from the user's term and symbols to the paper's term
and symbols. Vocabulary similarity is only a candidate relation. Mathematical
equivalence needs the explicit variable, frame, limit, transformation or
assumption map; otherwise label it analogy, incompatible or unknown.

## Synthesize ideas collectively

Group the extracted corpus by a useful mathematical structure or physical
mechanism, not by paper. For each collective idea record:

```text
useful idea:
supporting extracted sources:
problem it solved:
mathematical structure or mechanism:
assumptions:
known limitations or counterevidence:
possible relevance to the project:
```

The supporting paper cards remain in the evidence ledger. The main report does
not render a paper-by-paper catalogue unless the user asks for one.

## Translate into project notation

For each serious idea, map source symbols and assumptions into the project's
notation, then give only the candidate derivation needed to expose its value:

```text
literature idea:
project symbol/assumption map:
candidate project reformulation:
derived consequence if the map holds:
boundary or failed assumption:
first calculation or falsification check:
```

The reasoning chain is inspected sources -> collective idea -> project
notation -> candidate re-derivation -> testable insight. Never say a method
solves the project when only the inspiration or reformulation has transferred.

Tag every material statement as `source-established`, `mapped`,
`scout-derived`, `independently-verified`, `proposed-inspiration` or `unknown`.
The tag describes provenance, not confidence.

## Beginner-facing report

Lead with a bounded current orientation, not an authoritative expert verdict.
Use plain language first and only the equations needed to support it:

```text
1. Our current problem
2. What the extracted literature collectively suggests
3. The most useful mathematical ideas
4. How those ideas translate into our notation
5. Candidate reformulations or derivations
6. Why they may help this specific difficulty
7. What is supported, derived, proposed or unknown
8. The smallest calculation or source check to perform next
9. What the user should decide
```

Keep the default result concise. Define every displayed symbol locally. Expand
paper-by-paper evidence or long derivations only on request. A simple statement
must be traceable to the rigorous record; simplification never removes an
assumption, evidence boundary or failed mapping.

---

[⌂ Home](../../README.md)
