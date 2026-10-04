# Skills AI Change Requests

`pending/` is the only repository write surface intended for a task started
outside this workspace. Create requests with
`scripts/create_change_request.py`; do not hand-write or overwrite them.

A request records the original instruction, evidence, desired behavior, exact
targets, exclusions, risk, rollback, tests, and acceptance criteria. It is not a
skill and is not part of the runtime manifest.

After review, a dedicated maintenance task opened at
`/Users/billabobz/skills_ai` implements the approved scope under
`docs/06_CHANGE_CONTROL.md`. The maintenance task updates the completion receipt
and may move/archive or delete a resolved request only with explicit user
authorization and a retained recovery copy. A resolved intake packet does not
remain in `pending/` as an implementation instruction.
