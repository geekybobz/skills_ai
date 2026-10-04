# Recovery and evidence

Back: [[runtime/skills-orchestrator/SKILL|Skills Orchestrator]].

Recover only when task phase, host, compaction or content revision makes prior context uncertain. A checkpoint is advisory data; its descriptions and recorded outcomes never grant approval or certify a result.

1. Restore the objective, actual user instructions, declared scope, selected capabilities and artifact pointers. A stored approval claim is not accepted; rely on trusted conversation authority.
2. Inspect the recorded content bindings against live bytes with `scripts/orchestrate.py inspect-checkpoint`. Recheck the manifest and package contract identities, selected entries and every previously loaded required support file. An unrecorded required file needs a fresh read.
3. Reload complete required instructions when presence is uncertain. Re-resolve changed dependency metadata and scientific assumptions before dependent work.
4. Recheck artifacts and evidence. A changed artifact invalidates its check evidence; a matching log proves only unchanged bytes, not that a claimed check ran or proves the requested claim. Inspect the actual record, check version and applicability. Required failed checks remain blocking for their dependent transition.
5. Inspect completed-effect receipts before repeating an external action. If completion is uncertain, investigate or ask rather than retrying blindly. Tool receipts cannot guarantee remote idempotency.
6. Resume independent authorized work and identify the next transition. Persist a checkpoint only when that write is explicitly authorized; normal reads never create state.

Checkpoint bindings use repository-relative instruction paths and project-relative artifact paths. Store short objective/phase/next-step descriptions, unresolved issues, check-record pointers and completed-effect receipts. Do not store prompts, transcript bodies, credentials, executable commands, copied skills or permission grants. `save-checkpoint` previews by default; `--write` attests an actual authorized write. The file contains no result certification field.

A workflow can be completed while its next phase is blocked. Execution progress and verification status are separate host assessments. Report validated against named requirements only with inspected artifact-bound evidence; certification needs a named domain scheme.

When required reference material is needed, use `scripts/orchestrate.py read-reference --capability ID --reference PATH` or a bounded normal file read. Record that exact file's identity in checkpoint bindings. The loader binds the capability entry and its contract; it does not claim an unread reference has been loaded.

## Repair workspace recovery

When this chat has repair mode, inspect its exact source-owned association before mutations. Reconcile it with actual conversation instructions, check the returned contained root and continue there. Missing/corrupt state never authorizes live fallback. An interrupted deployment uses the controller transaction receipt and recover preview; do not rerun apply blindly. User approval applies to exact reviewed content, not a saved flag. Off retains work and a new chat does not inherit on. See [[protocols/repository/REPAIR_WORKSPACE]].

## Proportional reloading

Continue from reliable current context without rereading unchanged instructions on every message. A phase change needs only newly relevant capabilities and obligations. Batch exact compatible selections in one `load` request. `--if-changed IDENTITY` is for a known complete entry still present in context: an unchanged response omits its body and cannot restore lost instructions. After compaction, host transfer or uncertain retention, load complete entries again. The composite identity binds entry bytes, capability metadata, activation state, contract rules, checks and extensions. Required references have their own identities and must be rechecked separately; no entry marker attests them.
