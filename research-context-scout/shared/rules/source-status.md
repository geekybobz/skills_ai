# Source Status

Read at the existing-achievement scan (G3) and the source deep read (G4). Attach
one status to every literature-derived statement before it is used for anything.

| Status | Meaning | Allowed use |
|---|---|---|
| `search-candidate` | title, snippet or metadata only | candidate list only |
| `abstract-only` | abstract inspected, no methods/results check | weak context only |
| `source-read` | paper/PDF or full text inspected | evidence for stated claim |
| `equation-checked` | relevant equations and assumptions compared | math relation evidence |
| `result-verified` | derivation, benchmark or numerical claim independently checked | strong project evidence |

Rules:

- Never cite `search-candidate` or `abstract-only` material as decisive evidence
  for novelty, feasibility, a relation label, or a new direction.
- A missing source, inaccessible PDF, unchecked derivation or unverified
  numerical result lowers the status. It never licenses a stronger claim.
- Never infer novelty, feasibility, optimality or journal suitability from
  metadata, citation count, search rank or shared terminology.
- A record row without a status cannot support a gap predicate.
- A paper may enter collective synthesis only under the corpus-readiness rule in
  `literature-corpus.md`. `source-read` alone does not waive it.
- A pass-1 mechanical extraction caps at `source-read`. Reaching
  `equation-checked` or `result-verified` requires the pass-2 deep read defined
  in `literature-corpus.md`.

This table has one home. Rules, phases, templates and wrappers reference it
rather than restating the tokens.
