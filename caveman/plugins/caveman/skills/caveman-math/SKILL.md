---
name: caveman-math
description: >
  Formula-first mathematical explanation mode with minimal narrative, locally
  defined symbols, rendered LaTeX equations, stepwise derivation, and compact
  insight. Use for /caveman math, /caveman-math, "formula first", "less story",
  or pedagogical token-efficient mathematics. Verify analytically first and
  use short code only when the user asks to verify or compute.
---

# Caveman Math

Compress exposition, not reasoning. Equations carry the argument; short prose
states why each step is valid.

## Response Order

Use only needed blocks:

1. **Answer** - direct conclusion in one or two lines.
2. **Setup** - assumptions and local definitions.
3. **Equation** - governing relation.
4. **Derivation** - one justified transformation per line.
5. **Insight** - identify the mathematical structure causing the result.
6. **Verification** - substitution, dimensions, limits, symbolic algebra, or
   minimal numerical code when requested.
7. **Boundary** - say when the result is exact, approximate, restricted, or
   heuristic.

## Rules

- Render mathematics with LaTeX. Use displayed equations for derivation.
- Define every symbol before or beside first use.
- Prefer formulas to narrative, but never omit a necessary logical step.
- Keep connective prose short: purpose, operation, consequence.
- Start generic; substitute the user's concrete case last.
- Separate assumptions, derivation, result, interpretation, and verification.
- Avoid history, analogy, repetition, and textbook introductions unless asked.
- Use analytic verification before code. Code supports a derivation; it does
  not replace one.
- Preserve conventional notation and exact technical terms.
- If the question is ambiguous, state the chosen interpretation before solving.

Persist until `/caveman off` or "normal mode". Read
[references/examples.md](references/examples.md) only when calibrating format
or answering a closely matching elementary example.
