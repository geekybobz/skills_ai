# Review Workflow

Use this workflow for Markdown writes. Scale the proposal to the impact; do not
turn a small correction into an architecture exercise.

## 1. Identify the operation

| operation | required response before writing |
|---|---|
| Local edit | One short preview naming the file, intended correction, and preserved structure |
| Section change | Section purpose, information owner, and proposed content change |
| New file | Purpose, parent route, authoritative ownership, and links |
| Collection change | Layout profile, file impact, ownership, navigation, portability, and validation |
| Generated Markdown | Canonical source, generated target, regeneration method, and validation |

Read-only explanation or review does not require approval to inspect or report.
It still follows the protocol's ownership, portability, and validation concepts.

## 2. Announce and propose

Start with a compact notice:

> Markdown Protocol applies to this task. I inspected the relevant structure
> and prepared the following proportional design for review.

Include only applicable fields:

```markdown
### Markdown proposal

- Scope and purpose:
- Existing structure preserved:
- Layout or local change:
- Files affected:
- Information ownership and navigation:
- Optional or renderer-specific features:
- Validation:
- Deferred or unverified items:
```

For a local correction, compress this to one or two sentences. For structural
work, make file creation, movement, generated boundaries, and authoritative
owners explicit. Do not perform the write until the user agrees, unless the
user explicitly asks to bypass this review for that task.

## 3. Implement the agreed design

- Preserve user edits and useful local conventions.
- Do not broaden the approved file set or architecture silently.
- Keep essential meaning in portable text.
- Edit the canonical source rather than a generated Markdown projection.
- When another skill owns the subject matter, preserve its domain rules and use
  this protocol only for Markdown structure and presentation.

## 4. Decide whether renewed review is needed

Continue without another pause while the work stays within the agreed design.
Pause again before:

- adding, moving, or removing files not covered by the proposal;
- changing the selected collection profile;
- transferring authoritative ownership between files;
- introducing a plugin, generated view, or renderer-specific dependency;
- materially expanding the requested content or validation surface.

A user's direct edits are new source state, not mistakes to undo. Reinspect the
affected area, preserve the edits, and flag a conflict only when an invariant or
approved design can no longer be maintained.

## Explicit controls

- `#> md_protocol` force-selects this package in review mode.
- `#> use none` keeps the repository-wide optional-skill opt-out.
- A direct instruction such as "skip the Markdown review for this task" waives
  only this package's local proposal pause; it does not waive permissions,
  project instructions, or destructive-action safeguards.
