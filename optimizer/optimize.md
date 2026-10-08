# Optimize

Use only for `#> optimize <system/project> <goal>`. This workflow accepts an
existing system; it is separate from `build-system`. It is an adaptive loop,
not a fixed recipe or a default method tournament.

## Gate: verify before optimizing

Resolve the live route. Locate the system, its problem statement, and existing
campaign evidence. Confirm that the implemented dynamics, controls, target,
and objective match the problem statement. Then inspect the live system
contract, control layout, finite declared metrics, and analytical gradient.

If a required system feature is absent, state the exact missing capability and
why the requested optimization needs it. When the mathematical derivation
supports it, propose an implementation of that API from the analytical
expressions, obtain approval, and rerun system and gradient verification before
using it. Otherwise stop and direct the user to `#> build-system`.

Never substitute a numerical gradient silently for a failed analytical one.

## Execution-integrity gate

Before continuing, branching, comparing, or reporting a result, pause when code
fails or the recorded evidence conflicts with the declared system contract, a
numerical invariant, a current replay, or a physically necessary expectation.
Treat this as an implementation-or-setup hypothesis, not proof that the result
is wrong. This gate does not forbid an anomaly investigation; it prevents an
unverified result from steering the campaign.

Trigger the gate for an exception, timeout, route/environment mismatch,
non-finite or wrong-shape output, missing declared metric, bounds/residual
failure, replay disagreement, failed directional-gradient check,
metric-direction inconsistency, or unexplained invariant violation.

1. Freeze the current problem identity and preserve the receipt, checkpoint,
   route/environment, command, seed, and failure output.
2. Reproduce the smallest deterministic case; do not answer a failure by
   enlarging the campaign or changing methods.
3. Inspect the involved contract, inputs, shapes, units/scales, objective
   direction, bounds, derivative path, and recorded counters.
4. Use the cheapest discriminating checks in order: route/import, static
   contract, finite/shape, exact replay, directional gradient, then one
   targeted diagnostic with stated cost.
5. Classify the outcome as environment/setup, API/shape, numerical
   implementation, derivative, modelling/assumption, or unresolved anomaly;
   record the evidence and remaining uncertainty.

Do not change physics, controls, objective, or optimizer settings as a
"fix" before classification. Require approval for a code edit. After a fix,
rerun the failed minimal case and relevant system/gradient checks; an altered
implementation or derivative is a new validation boundary under the
problem-identity table.

## Adaptive orientation

Before a new numerical action, return a compact orientation:

```text
goal and current best evidence
-> problem identity: same | parameter continuation | new problem
-> feasible live capabilities and 2–4 plausible routes
-> one recommended next bounded action and alternatives
-> checkpoint evidence that could change the recommendation
```

Use the system-declared selection metric and direction, not a conventional `J`
assumption. Prefer one route that can improve the stated goal now. Use
`portfolio` only when a genuine, evidence-based uncertainty about viable search
routes blocks progress; it is not the default objective.

## Problem identity and reuse

Before reusing a control, classify the change:

| change | treatment |
|---|---|
| same fingerprint, objective, and control layout | continue or refine the compatible campaign |
| secondary-parameter change with the same layout | parameter continuation through `with_secondary(...)` |
| changed grid, basis, horizon, bounds, cutoff, dynamics, objective, target, or bath | new problem; use an old control only as an explicitly transferred seed |
| changed implementation or derivative | new problem until its validation gate passes |

A resolution or control-layout change is never called continuation. Start a new
campaign root, record the source control as provenance, state its transfer rule,
and rerun preflight and gradient verification.

Saved evidence is compatible only when it has the same fingerprint,
objective/direction, control layout, controls, and a successful current replay.
Do not silently reuse old controls.

## Initial controls

Start from the most meaningful available family, not generic random arrays:

1. verified incumbent or physical baseline;
2. analytical, resonance, pulse-area, adiabatic, symmetry, PMP, or BVP seed
   when justified by this system;
3. a smooth Fourier family when bandwidth and pulse shape are physically
   meaningful; declare its envelope, amplitude, frequency range, coefficients,
   seed, and constraint handling;
4. local smooth perturbations around a valid candidate;
5. random smooth controls only with a system-justified amplitude and bandwidth.

Use a Fourier family as a compact physical ansatz or a basin-entry tool, not an
unjustified restriction on the final optimum. Require the system's declared
control-transfer capability before transforming constrained controls.

## Run, inspect, adapt

Run the recommended bounded action. At initial candidate, meaningful new best,
stagnation, acceptance collapse, constraint warning, method handoff,
pre-intervention, new-problem boundary, failure, and final candidate, read the
existing campaign/tracker evidence. Then read `situation-analysis.md` before
changing strategy or presenting an intervention.

At a failure or suspicious result, apply the execution-integrity gate before
reading strategy options or selecting the next numerical action.

Inspect only already-recorded selection metrics, feasibility/KKT evidence,
accepted/rejected steps, stop reason, counters, control summaries, checkpoint
references, and fingerprint. An absent quantity becomes an explicit diagnostic
proposal with stated cost; tracking and reporting never trigger hidden
evaluation, gradient, propagation, residual/Jacobian/HVP, trajectory, or
plot-data work.

Use multi-core execution only with isolated system instances and an explicit
worker/core budget. Keep v4 campaign artifacts as scientific source of truth:

```text
campaign_receipt.json | campaign_timeline.jsonl | stages/<id>/
diagnostics/<candidate>.json | selected.json
```

The retained session ledger may summarize decisions but must reference these
artifacts and never become a competing numerical history.

## Claims

At a final candidate, perform the applicable explicit checks: exact replay,
target condition, same system fingerprint, bounds/residuals, gradient or
projected-KKT evidence, and requested model-specific validation. Report only
the strongest justified label:

```text
candidate | validated candidate | reproducible multi-start best |
robustness-tested candidate | benchmark-supported result |
global optimum only with separate proof/evidence
```

---

[⌂ Home](README.md)
