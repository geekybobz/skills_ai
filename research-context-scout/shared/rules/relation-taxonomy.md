# Relation Taxonomy

Use this rule to compare the project with existing papers, source results, or
nearby applications. The relation label decides whether Scout should reproduce,
adapt, transfer, discard, or investigate further.

## Primary 2x2 labels

| Label | Meaning | Default action |
|---|---|---|
| `same-physics-same-math` | same physical objective and essentially same formulation or method | treat as existing result; reproduce, benchmark, cite, or stop |
| `same-physics-different-math` | same physical objective but different method, formulation, control, resource, or proof route | possible new route for known objective; test improvement |
| `different-physics-same-math` | similar equations or control structure but different physical objective/system | transfer candidate only; prove physical mapping |
| `different-physics-different-math` | neither objective nor formulation is close | background only |

Same mathematics does not prove the same physics. Same physics with different
math is often the useful case, but only if it improves a measurable quantity or
clarifies a real limitation.

## Secondary labels

Use secondary labels only after assigning one primary label.

| Label | Use |
|---|---|
| `same-mechanism` | same enabling mechanism under different wording |
| `same-application` | same downstream consumer or use case |
| `loose-analogy` | suggestive but not decision-grade |
| `stronger-assumptions` | source solves the objective under stricter assumptions than the project |
| `weaker-assumptions` | source solves the objective under looser assumptions than the project |
| `no-go-or-bound` | source limits or blocks the direction |
| `equivalent-under-transformation` | objectives and models match only after an explicit variable, frame or limit map |
| `same-achievement-different-formulation` | the measurable achievement matches while the governing formulation differs |
| `same-mechanism-different-observable` | the enabling physics matches but the measured consequence differs |
| `incompatible` | a required state, assumption, control or regime blocks transfer |
| `unknown-relation` | inspected evidence is insufficient to decide the mapping |

## Normalized comparison

Before selecting a label, use `collective-synthesis.md` to normalize the
achievement, model and mechanism. Record the user's terminology, the source
terminology and the explicit mapping. Shared vocabulary cannot establish a
relation, and different vocabulary does not rule one out.

## Relation card

For each serious source, record:

```text
source:
physics objective:
project objective match:
math/method match:
assumptions:
result:
relation label:
transfer condition:
symbol/assumption map:
decision impact:
next check:
```

Reject vocabulary-only matches. A relation changes the project only when it
changes reproduce/adapt/extend/stop, the gap predicate, or the next decisive
test.
