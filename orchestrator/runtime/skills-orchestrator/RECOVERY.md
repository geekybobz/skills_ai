# Recovery and evidence

Entry: [SKILL.md](SKILL.md). Reload policy and flags: [LOADING.md](LOADING.md). Repair recovery: [MANAGEMENT.md](MANAGEMENT.md).

Recover only when task phase, host, compaction or content revision makes prior context uncertain. A checkpoint is advisory data; its descriptions and recorded outcomes never grant approval or certify a result.

1. Restore the objective, actual user instructions, declared scope, selected capabilities and artifact pointers. A stored approval claim is not accepted; rely on trusted conversation authority.
2. Inspect the recorded content bindings against live bytes with `orchestrator/tools/orchestrate.py inspect-checkpoint`. Recheck the manifest and package contract identities, selected entries and every previously loaded required support file. An unrecorded required file needs a fresh read.
3. Reload complete required instructions when presence is uncertain. Re-resolve changed dependency metadata and scientific assumptions before dependent work.
4. Recheck artifacts and evidence. A changed artifact invalidates its check evidence; a matching log proves only unchanged bytes, not that a claimed check ran or proves the requested claim. Inspect the actual record, check version and applicability. Required failed checks remain blocking for their dependent transition.
5. Inspect completed-effect receipts before repeating an external action. If completion is uncertain, investigate or ask rather than retrying blindly. Tool receipts cannot guarantee remote idempotency.
6. Resume independent authorized work and identify the next transition. Persist a checkpoint only when that write is explicitly authorized; normal reads never create state.

Checkpoint bindings use repository-relative instruction paths and project-relative artifact paths. Store short objective/phase/next-step descriptions, unresolved issues, check-record pointers and completed-effect receipts. Do not store prompts, transcript bodies, credentials, executable commands, copied skills or permission grants. `save-checkpoint` previews by default; `--write` attests an actual authorized write. The file contains no result certification field.

A workflow can be completed while its next phase is blocked. Execution progress and verification status are separate host assessments. Report validated against named requirements only with inspected artifact-bound evidence; certification needs a named domain scheme.

A required reference actually read ([LOADING.md](LOADING.md)) is recorded in the checkpoint bindings with that exact file's identity. The loader binds the capability entry and its contract; it does not claim an unread reference has been loaded.

## Context after recovery

Recovered instruction presence does not restore an expired request control.
Resolve current selection/mode/scope from actual user instructions and explicit
wider defaults. Without a known repair association, do not hunt another workspace;
with corrupt known state, stop mutations until recovery. Status facts are readable
without creating checkpoint, capsule or delivery state.

---

[⌂ Home](INDEX.md)
