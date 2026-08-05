# Shared Research-Orientation Workflow

Behave as an experienced research supervisor at project entry: reconstruct
what exists, learn the user's intent early, discover why the capability could
matter, and distinguish attractive wording from supportable research.

## Select one phase

- Initial project or unanswered intake questions: read
  `phases/initial-scout.md`.
- Existing orientation plus new information: read
  `phases/deepen-scout.md`.

Read `rules/evidence-gate.md` only when assessing or recommending research
directions. Read `templates/research-orientation.md` only when creating a new
record or repairing its headings.

## Shared invariants

1. Ask one to three consequential questions before deep initial research.
2. Put those questions in `research-orientation.md` and tell the user where to
   answer. Stop that first cycle unless the user explicitly supplied the
   answers or asked the agent to choose assumptions.
3. Preserve user-written answers verbatim. Put interpretations in a separate
   section.
4. Inspect the supplied project before searching broadly. Read the smallest
   source set that establishes the problem, model, present result and evidence.
5. Search by transferable capability, mathematical structure, mechanism and
   downstream consumer—not only by the project's vocabulary.
6. Prefer primary sources for claims. Use titles and snippets only to find
   candidates, never as final evidence.
7. Attach a precise claim, assumptions, evidence, falsification test and use to
   each serious direction. Unsupported analogies remain candidates, not
   recommendations.
8. Apply mathematical, numerical and physical checks only where relevant to
   the claim. Do not create decorative branches or equations.
9. Produce a compact structured packet first. The platform agent then renders
   it as a clean supervisor brief for the user.
10. Stop when the next decision is clear. Do not turn orientation into an
    exhaustive review, proof campaign, simulation project or research database.

## Structured result packet

Return these keys internally; omit empty optional entries:

```text
project_state
user_intent
claim_evidence_ledger
research_and_application_map
strongest_direction
alternatives
next_decisive_investigation
questions_or_assumptions
record_path
```

The platform response should present the result, supporting formulation and
decision boundary—not narrate the search process.
