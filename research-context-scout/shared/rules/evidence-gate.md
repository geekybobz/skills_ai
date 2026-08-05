# Evidence Gate

Use this rule whenever proposing or ranking a research direction. Match the
support to the claim; do not add mathematics, computation or experimental
discussion when it is irrelevant.

## Direction contract

Represent a direction as

\[
\mathcal D=(C,M,A,E,T,F,U,P),
\]

where \(C\) is the precise claim, \(M\) the model, \(A\) the assumptions,
\(E\) current evidence, \(T\) the next project-specific test, \(F\) the
falsification condition, \(U\) the use or importance and \(P\) the possible
paper contribution.

| Level | Evidence | Treatment |
|---|---|---|
| E0 | verbal analogy | reject as a recommendation |
| E1 | formal claim and falsifiable test | open candidate only |
| E2 | mapped theorem, derivation, bound or verified numerical check | provisional recommendation |
| E3 | consistent independent evidence types plus relevant literature | strong direction |
| E4 | independently verified and physically or experimentally credible | candidate central result |

Theoretical recommendations normally require E2. If a check cannot yet be
performed, keep the direction at E1 and give its first falsification test.

## Proof-of-plausibility

Choose the checks demanded by the claim.

- Mathematical claim: give a short derivation, mapped theorem, constructive
  example, bound, symmetry argument, reachable-set calculation or
  counterexample. Define symbols and state assumptions.
- Numerical claim: specify the objective and admissible set, baseline,
  residual/error metric, convergence or truncation test, initialization policy
  and reproducible pass/fail condition.
- Physical claim: map to a realizable interaction and parameter regime, then
  test control limits, bandwidth/slew rate, loss/decoherence, preparation and
  reset overhead, measurement and measurable benefit.

Keep mathematical possibility, numerical reachability and physical
realizability as separate claim states. Evidence for one does not prove the
others.

## Application contract

Represent a serious application as

\[
\mathcal A=(\text{consumer},\text{required result},\text{mapping},
\text{benefit},\text{assumption},\text{evidence}).
\]

Identify who uses the result, exactly which capability is required, how the
project maps to it, which measurable quantity improves, what breaks the link
and which evidence supports it. Shared terminology alone is E0.

## Paper-direction contract

Use

\[
\mathcal P=(Q,C,N,E,G,A,F),
\]

with research question \(Q\), central claim \(C\), novelty hypothesis \(N\),
evidence package \(E\), generality \(G\), importance \(A\) and falsifier
\(F\). Treat novelty and venue potential as hypotheses until the relevant
literature and evidence have been checked.
