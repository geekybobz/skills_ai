# Alignment Checkpoints

Use when Scout reaches a boundary where the user's correction can materially
change the research search, corpus, interpretation or next test. A checkpoint
is a concrete state for review, not a generic request for more information.

## Alignment packet

Present and record:

```text
checkpoint type:
what Scout understands:
project formulation or affected claim:
inspected evidence and source status:
pilot findings or possible directions:
assumptions and ambiguous terminology:
what can change at this checkpoint:
proposed next action:
alignment state: pending | confirmed | corrected | delegated
```

Offer these response actions without requiring the user to follow exact syntax:

```text
CONFIRM
CORRECT
ADD
REMOVE
PRIORITIZE
DEFER
```

Record the response verbatim in the protected user-response block. Put Scout's
interpretation below it. A correction reopens every dependent state; it never
silently leaves an old search lane, mapping or conclusion active.

## Checkpoints

1. **Context alignment (G2A, mandatory):** after the physics objective and
   mathematical formulation, show the context mirror plus only a small pilot
   search. Stop while its state is `pending`.
2. **Search alignment (G3, mandatory):** show structured clusters, vocabulary,
   representative candidate sources and proposed search lanes before bounded
   closure. Stop while its state is `pending`.
3. **Corpus readiness (G3A, mandatory when papers are required):** show the
   acquisition and coverage plan. Stop while any source selected for synthesis
   lacks locally available full text or has a failed extraction without
   user-confirmed exclusion or replacement.
4. **Interpretation alignment (G5, conditional):** show an equation,
   achievement or mechanism mapping when a plausible alternative would change
   the direction. Stop while the material ambiguity is unresolved.
5. **Result review (G10):** show the collective synthesis, uncertainty and next
   check. The user accepts, corrects or redirects the orientation.

Do not repeat a confirmed checkpoint unless a delta changes one of its inputs.
Do not ask the user to find literature, invent applications or make choices
that inspected evidence can settle.
