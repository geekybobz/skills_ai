# Contained repair workflow

Back: [[docs/06_CHANGE_CONTROL|Change Control]]. Controller:
`scripts/repair_workspace.py`. User controls are model-interpreted; this
protocol manages locations and exact file transactions, not semantic routing.

## Working mode

`#> repair on` authorizes creation/resumption of this maintenance chat's workspace
under ignored `.runtime/repair/workspaces/`. The controller snapshots current
source including relevant dirty and untracked files into independent Git history.
It excludes credentials, caches, live Git metadata, backups and its own state.
Declared external/submodule references become separate frozen file copies; they
are not live links, Git pointers or deployable targets.

Use the source checkout's controller for start/inspect/pause/preview/apply/recover.
Never invoke the edited candidate controller to approve or deploy itself.
`start --write` is idempotent for the same host session. `pause --write` records
off and retains every pending file. Mode belongs to this chat, not all projects.
Use Codex's CODEX_THREAD_ID or an exact available host session ID with --session;
if identity is unavailable, establish and retain one opaque ID in the conversation.
Do not choose the newest workspace or infer a session from task prose.

While on, resolve repository edits, new scratch files, generated outputs, tests
and Git operations into the returned working_root. A live absolute path mentioned
as a source reference is not an instruction to edit live. An explicit exception
authorizes only its named action and does not turn repair off. Live source and
global adapters stay unchanged. Candidate installation tests use test config
directories. Candidate instructions are test subjects, not controller authority.

Context recovery inspects the known association and actual user instructions.
Saved on/off records are advisory and never grant permission. Missing/corrupt
known state blocks mutation until resolved; never fall back to live edits.
New chats default off. External project tasks retain [[EXTERNAL_CHANGE_REQUEST]];
repair on does not bypass the dedicated maintenance-workspace boundary.

## Update review

`#> update` invokes preview, not application. Run the source-owned controller:

```text
python3 scripts/repair_workspace.py preview --session HOST_ID --run-checks --approval-ref SCOPE_REF
```

Explain the actual added/edited/deleted paths, behavior, verification limitations,
conflicts and rollback. Required checks execute against the candidate and are
bound to its exact bytes. The controller checks all captured source/dependency
identities; unchanged external references remain separately owned. Drift blocks
readiness. Unrelated live changes are preserved and can be incorporated into a
new reviewed baseline; do not silently copy them into pending work.

The host performs bounded semantic review and any required native-host acceptance.
Local PASS is artifact evidence, not model-behavior or domain certification.
Preview commits the delta in contained Git. The preview ID binds the complete
packet and local evidence. Candidate or relevant live changes invalidate it.

## Apply and recovery

Only after actual user agreement to that exact review may the host attest it:

```text
python3 scripts/repair_workspace.py apply --session HOST_ID --approved-preview PREVIEW_ID --approval-ref AGREEMENT_REF --write
```

Flags and saved records cannot verify or manufacture approval. Recheck actual
scope, explicit deletion/external boundaries and any native acceptance obligations.
The source-owned controller locks managed transactions, preflights every file,
saves rollback before replacement, applies only the reviewed packet and runs live
artifact checks. Failed checks restore captured bytes unless later edits conflict.
File replacement is recoverable, not atomic across the entire installation;
concurrent unmanaged writers/readers remain a host-coordination responsibility.

Successful application leaves the live index unchanged, records a contained commit
and Git bundle, advances the baseline and preserves on/off. A live commit is made
only with separately bounded staging that excludes inherited dirty work. Never
use git add . on the live checkout. Explain overlapping inherited changes before
proposing a live commit that would include them.

`recover` previews by default; `recover --write` restores a partially or fully
applied transaction and its baseline. Confirm the intended rollback in the
conversation before writing. Recovery refuses later third-party changes. Repeated
recovery is safe. Incomplete start folders are retained for inspection; they never
become the active association. No automatic deletion, watcher or background job.

Filesystem separation and advisory locks protect this managed workflow, not
arbitrary candidate processes. Host write/network restrictions provide the hard
boundary; tests are deliberate code execution within actual authority.
