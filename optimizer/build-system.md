# Build system

Use only for `#> build-system <problem.tex>`. This workflow starts from the
user-pointed derivation and is independent of campaign optimization.

1. Resolve the live Optimizer route and read its OLGS contract and system-build
   guidance.
2. Read only the named TeX/source files. Extract state, dynamics, controls,
   initial/target conditions, objective, constraints, and analytical-gradient
   route.
3. Map this particular derivation to the **live** system contract. Do not carry
   a competing fixed API in this skill.
4. Show a reviewable design before edits:

```text
derivation -> state/dynamics/controls -> numerical kernels -> live hooks
```

Include primary versus secondary parameters, control layout, metrics, gradient
route, vectorisation opportunities, cheap evaluation versus gradient-history
path, and memory risks.
5. Propose optional APIs only when the derivation or ordinary workflow requires
   them: bounds, residuals/Jacobian, control transfer, HVP, prox, simulation,
   or explicit plot data. State the reason and verification needed.
6. Stop for review. After approval, implement only the reviewed scope and
   verify TeX-to-code dynamics, shape/layout, finite metrics, and the
   analytical directional-gradient check. If code fails or a result conflicts
   with the declared contract or a necessary invariant, apply the
   execution-integrity gate in `optimize.md`: preserve the smallest failing
   case, inspect it, classify it, and revalidate after an approved correction
   before presenting the system as optimization-ready.

Prefer vectorized arrays and linear algebra where mathematically valid. Do not
store full trajectories unless the derivative or requested diagnostic needs
them. Do not invent missing physics.
