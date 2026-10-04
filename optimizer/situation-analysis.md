# Situation analysis

Use for `#> optimizer explore`, `intervene`, `continue`, or `branch`, and after
a meaningful campaign checkpoint. Preserve adaptive freedom while making each
change scientifically legible.

## Read evidence, then propose

Read only the named system, campaign receipt/timeline, stage tracker artifacts,
and explicitly requested diagnostics. Identify:

```text
what changed | what is already known | what remains uncertain |
2–4 plausible explanations | viable live capabilities | one recommended next action
```

Do not invent a cause from a graph or class name. Do not trigger numerical work
while reading reports. If evidence is insufficient, propose the smallest
explicit diagnostic or bounded optimization action that could distinguish the
important explanations.

Classify every proposed change with the problem-identity table in `optimize.md`.
That table is the single home for the identity, continuation, and reuse rules;
never restate or weaken it here.

## Operation meanings

| operation | required result |
|---|---|
| `explore` | A ranked set of viable ideas, their expected information or improvement value, prerequisites, and one recommended next action. |
| `intervene` | The proposed tactic, why current evidence motivates it, identity classification, compatibility impact, and a bounded validation plan. |
| `continue` | Confirmed identity compatibility under the `optimize.md` table; otherwise redirect to `branch`. |
| `branch` | `tactic branch` for the same scientific problem, or `new-problem branch` with source-control provenance and an explicit transfer/revalidation plan. |

An intervention is allowed when it is explicit and recorded. It does not make
the new result directly comparable to its source unless identity and validation
conditions remain satisfied.

## Situations and useful next ideas

| evidence | consider | avoid |
|---|---|---|
| feasible candidate still improves | continue the active route; reserve a checkpoint | switching methods without a reason |
| plateau with trusted derivatives | refine, warm-start, local smooth/Fourier perturbation, or a representation branch | claiming a local optimum from a plateau |
| many rejected or unstable steps | inspect recorded scale/bounds/acceptance evidence; use a short guarded repair or restart | blind large-budget reruns |
| controls saturate bounds | determine whether the bound is physical, active, or a scaling symptom; use declared constrained tools if available | clipping without system semantics |
| constraint failure | use declared repair/transfer or stop and repair the system formulation | treating an infeasible pulse as a candidate |
| changed physics or resolution | classify with `optimize.md`, then open a new-problem branch and revalidate | calling it continuation |
| new physical mechanism hypothesis | propose targeted seed, diagnostic, or restricted-family branch | inferring mechanism from unrecorded quantities |
| missing or failed gradient evidence | fix/review the derivative; use derivative-free exploration only with an explicit cost reason | numerical-gradient substitution |
| execution failure or suspicious result | apply the execution-integrity gate in `optimize.md`: preserve artifacts, reproduce the smallest case, and run the cheapest discriminating check | changing method, physics, controls, or objective as a workaround |

## Checkpoint response

At each checkpoint return: observed facts; a constrained interpretation;
remaining uncertainty; recommended action; alternatives; and the evidence that
would make the next decision different. If an execution-integrity trigger is
present, return its classification, preserved evidence, minimal reproduction,
and the next discriminating check instead of an optimizer intervention. Keep
manual/Codex recommendations distinct from any future deterministic policy. Do
not introduce self-modifying, online-learning, or autonomous-control policy.
