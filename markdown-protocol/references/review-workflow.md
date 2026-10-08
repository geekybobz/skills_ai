# Review Workflow

Use this workflow for Markdown writes. Scale the proposal to the impact; do not
turn a small correction into an architecture exercise.

## Compact workflow

| operation | response required before writing |
|---|---|
| Local edit | file, intended correction, and preserved structure |
| Section change | purpose, information owner, and content change |
| New file | purpose, parent route, owner, and links |
| Collection change | profile, files, ownership, navigation, portability, and checks |
| Generated Markdown | canonical source, target, regeneration, and checks |

Read-only explanation or review needs no write approval. Before a write:

1. Announce that Markdown Protocol applies.
2. Inspect the relevant existing structure.
3. Present the smallest proposal that exposes the real effect.
4. Wait for agreement unless the user explicitly waives this local gate.
5. Implement only the agreed design and preserve later user edits.
6. Pause again before new files, changed ownership or profile, a new generated
   view/plugin, or materially broader content or validation.

A review-gate waiver changes only this proposal pause. It never waives project
instructions, permissions, destructive-action safeguards, or another skill's
authority.

When a proposal introduces a non-core or renderer-dependent technique, include
an optional `Patterns used` line linking its gallery example. Omit the line for
ordinary headings, prose, lists, and relative links.

## Details

### Expanded proposal

```markdown
### Markdown proposal

- Scope and purpose:
- Existing structure preserved:
- Layout or local change:
- Files affected:
- Information ownership and navigation:
- Footer route (Previous · Home · Next):
- Patterns used: [Pattern](relevant-gallery-example.md)
- Optional or renderer-specific features:
- Validation:
- Deferred or unverified items:
```

For a local correction, compress this to one or two sentences. For structural
work, make file creation, movement, generated boundaries, and authoritative
owners explicit.

### Implementation boundaries

- Preserve user edits and useful local conventions.
- Keep essential meaning in portable text.
- Edit a canonical source instead of its generated Markdown projection.
- Do not broaden the approved files or architecture silently.
- When another skill owns the subject, preserve its domain rules and use this
  protocol only for Markdown structure and presentation.

A user's direct edit is new source state, not an error to undo. Reinspect that
area and flag a conflict only when an invariant or the approved design can no
longer be maintained.

### Explicit controls

- `#> md_protocol` force-selects this package in `guided` mode.
- `#> md_deepen <term>` selects `deepen` mode; the term is task input and the
  new note plus reciprocal links still require the proportional write review.
- `#> md_check` selects read-only `check` mode and runs the package checker on
  the unambiguous or user-named collection; repairs remain separate writes.
- `#> use none` keeps the repository-wide optional-skill opt-out.
- “Skip the Markdown review for this task” invokes the compact waiver rule
  above; it grants no additional authority.

---

[← Previous](core-protocol.md) · [⌂ Home](../INDEX.md) · [Next →](layouts.md)
