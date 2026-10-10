# Markdown Protocol Registry

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · Package:
[[skills/markdown-protocol/SKILL|Markdown Protocol]] · Activation:
[[orchestrator/registry/activation|Activation Register]]

This is one active public task package. It applies whenever requested work
creates, edits, reviews, or restructures Markdown, including Markdown changed
inside another task, and may be force-selected with `#> md_protocol`.
Focused aliases can deepen one term or check one collection. Add-ons cover
learning, codebases, research notes, decisions, runbooks, visual extras, slides,
and skill packages.

## Skills

| skill | does | selection | not for |
|---|---|---|---|
| [[skills/markdown-protocol/SKILL\|markdown-protocol]] | creates, edits, reviews, or restructures Markdown artifacts with proportional design review, adaptive layouts, progressive disclosure, portable navigation, selective visual patterns, and explicit validation | any requested Markdown creation, edit, review, or restructuring, including README, documentation, notes, knowledge bases, or Markdown changed inside another task | merely reading Markdown instructions as operational input, non-Markdown work, unrequested plugin installation, or unverified renderer claims |

## Command aliases

| command | package | mode | boundary |
|---|---|---|---|
| `#> md_check` | `markdown-protocol` | `check` | first task directive; optional target text may follow; read-only unless a separate write is requested |
| `#> md_deepen` | `markdown-protocol` | `deepen` | first task directive; required term text follows; proportional review still applies |
| `#> md_protocol` | `markdown-protocol` | `guided` | first task directive; presentation controls may precede |

## Rules

- Select automatically whenever requested work will create, edit, review, or
  restructure Markdown. Compose with the skill that owns the subject matter.
  Do not select merely because the host reads a Markdown instruction, skill, or
  source while completing a different kind of task.
- Announce selection and use the proportional proposal gate before writes.
  Read-only inspection and review may proceed without inventing a write gate.
- After agreement, continue inside the approved design and pause again only for
  material expansion. Preserve subsequent user edits as current source state.
- Load the compact package entry first and only the references needed for the
  current task.
- Formatting examples are human learning aids, not a default context bundle.
- The portable source remains authoritative when a renderer-specific feature
  is used.
- Mathematical delimiter guidance stays provisional until the intended
  renderers have been tested.
- `#> use none` remains the explicit opt-out for optional task skills.
