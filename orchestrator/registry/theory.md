# Theory Registry

Rigorous compact LaTeX reference documents: theory notes, math refreshers,
chapter-based academic material.

`theory-reference` is one public task package. The entry, phases, rules,
templates, and scripts below are internal package structure, not additional skills.

`skills/theory-reference/` is a **git submodule**. Registry files never live inside it —
this file is the whole registry entry for that family.

## Package Capability

| capability | does | selection | not for |
|---|---|---|---|
| [[skills/theory-reference/SKILL\|theory-reference]] | build a rigorous compact LaTeX reference through planning, evaluation and chapter phases | theoretical references and mathematical learning documents | unrelated prose or software implementation |

## Load route

```text
skills/theory-reference/SKILL.md              wrapper, entry only
  -> skills/theory-reference/shared/SKILL.md  the real router — does project discovery
    -> one phase file                  planning | chapter_build | evaluate
```

Enter at the wrapper and let the shared router pick the phase. Do not guess the
phase and jump straight to a phase file — discovery reads `.theory-state`,
`README.md`, and the plan file to resolve project paths first.

## Phases

| situation | phase file | writes |
|---|---|---|
| no plan file exists | `shared/phases/planning.md` | plan + outlines, after approval |
| "redo plan", "start over", "new plan" | `shared/phases/planning.md` | plan + outlines, after approval |
| "evaluate", "audit plan", "review plan" | `shared/phases/evaluate.md` | selected outlines only, after approval |
| plan exists, a chapter is requested | `shared/phases/chapter_build.md` | chapter LaTeX, after approval |
| outline review only | the outline file | nothing — present only |

## Internals — load only when the active phase asks

| area | files |
|---|---|
| Rules | `shared/rules/rules.md`, `notation.md`, `writing_rules.md`, `box_usage.md` |
| Templates | `shared/templates/*.tex` — chapter build only |
| Outline format | `shared/outline_format.md` |
| Scripts | `scripts/*.sh`, `scripts/figure_template.py` |

## Risk

Every phase writes only after approval. Planning produces no LaTeX. Evaluate
reorders nothing without explicit sign-off. See [[04_RISK_MAP]].

## Combines with

For a poster derived from theory content, finish and verify the theory phase first; visual design uses normal host capabilities, not a local design package.
Keep notes focused at drafting time; no separate response-style compressor is required.

## Rules

- Load the minimum phase files. Never preload rules, templates, or all outlines.
- Nothing above fits → say so.
- Path: `skills/theory-reference/SKILL.md`
