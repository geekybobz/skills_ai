# Skills AI metadata and explicit-access API

Orchestrator: [[runtime/skills-orchestrator/SKILL]]. Integration: [[runtime/skills-orchestrator/CONTRACT]].

The host interprets task intent, leading controls and presentation. Shared commands receive exact metadata/file requests, never task prose. Responses grant no authority. Visible task receipts are host-rendered summaries, independent of optional capsule data.

## Explicit access

```bash
python3 scripts/orchestrate.py discover --limit 8
python3 scripts/orchestrate.py discover --offset 8 --source-hash <revision>
python3 scripts/orchestrate.py discover --package <exact-package>
python3 scripts/orchestrate.py load --capability <exact-id>
python3 scripts/orchestrate.py load --capability optimizer --explicit
python3 scripts/orchestrate.py read-reference --capability <id> --reference <declared-relative-path>
```

Discovery is metadata only, lexically ordered and paginated: at most 32 items and 12 KiB per page. It never ranks candidates or reads their bodies. A first page is not exhaustive. Manual access requires the host to attest an actual explicit invocation; `--explicit` never grants authority. Disabled, hidden and deprecated capabilities cannot be loaded. Unknown IDs are rejected without substitution. Complete selected files are bounded at 1 MiB; traversal, symlinks at every component, special files and excessive size are rejected. Entry and contract SHA-256 bindings accompany loads. Expected entry hashes can detect changes.

`registry/contracts/<package>.json` follows `runtime/skill-contract.schema.json`. An unmigrated package uses a labelled entry-metadata bridge. Original instruction obligations retain their force; migration is explicit. Declared reference files are read only by exact request. Dependency graph checks inspect structure and never choose a skill set.

## Checkpoints and evidence

`inspect-checkpoint --project <absolute-project> --state .skills-ai/<name>.json` rechecks content bindings and reports staleness. `save-checkpoint` accepts bounded JSON on stdin, previews by default, and persists only with `--write` after actual authorization. Writes are atomic/private and refuse symlinks. Stored claims and successful byte checks grant no permissions or certification. See [[runtime/skills-orchestrator/RECOVERY]].

## Failure boundaries

Invalid access, malformed/oversized metadata, unsafe paths and unavailable manifests return a prompt-free `skills-ai/error/1` response and exit 2. The Claude hook catches optional-layer failures and emits no context; required evidence and known repair-state boundaries remain unresolved. Missing, invalid, symlinked, oversized or stale capsules contribute status only. Truncated summaries require full validated inspection before consequential work. Stored commands remain advisory and are omitted from ordinary receipts.

Codex consumes the installed entry, whose source-root placeholder is substituted by the installer. Claude injects the shared core plus untrusted discovery/capsule data through its managed hook. Both hosts use the same explicit access tools. Neither adapter selects or injects a candidate body. Process tests, live semantic decisions and end-to-end task evidence are separate acceptance layers.

Interaction package: [[interaction-protocol/README]].

## Repair session metadata

Context delivery accepts an explicit opaque `--session HOST_ID`; Claude passes its session ID. Existing associations contribute advisory repair state, including the working root, without granting approval. Known corrupt state is unresolved, never a reason to silently write live. Lifecycle actions use `scripts/repair_workspace.py` and `protocols/repository/REPAIR_WORKSPACE.md`.

## Context delivery

`orchestrate.py context --format json --delivery bootstrap|continuation --session HOST_ID --project-root ABS` assembles instructions and bounded advisory metadata without task prose. Bootstrap always restores all sections. Continuation returns only changed sections; without a session it restores full context without creating state. Private ignored `.runtime/context-delivery/` markers store four SHA-256 identities only. A marker attests delivery, not retained model context or permission. Corrupt content restores full delivery; symlinks and unsafe state paths are rejected. Project summaries over 1 KiB explicitly require full validated inspection. Repair metadata preserves unresolved-state mutation boundaries.

Discovery also accepts `--format text` and `--metadata-hash`. Text retains capability IDs, entry paths, meaningful roles/dependencies and alias modes; it explicitly marks shortened purposes and remaining pages. Metadata identity covers live contract records, activation and aliases without reading skill bodies. JSON remains the machine default. Interaction capability loads return the complete protocol, gated by the corresponding component.

## Selected batch loading and revision checks

Repeat `load --capability A --capability B` to obtain a `skills-ai/load-batch/1` packet of complete entries selected by the host. All availability/manual gates are checked before any entry is read. No dependency is selected or loaded automatically. Unknown, duplicate or unavailable targets reject the request without a partial body response. Maximum 32 entries and 2 MiB serialized output. Attest individual manual invocations with repeated `--explicit-capability ID`; `--explicit` attests every named target and must be used only when that is true.

A single load returns `identity`, covering the entry, metadata, state and contract obligations. `--if-changed IDENTITY` omits bodies only when that composite identity matches; gates remain enforced. `--expected-sha256` continues to check entry bytes. Both flags require a single capability. An unchanged response is evidence of current bytes, never of retained instructions or loaded references. Omit `--if-changed` after compaction or context uncertainty. No task memory is automatically created.

Codex installation renders the shared header plus the complete current core, binding its source hash. `inspire` aliases advisory. Theory-reference integration loads its complete shared entry directly; namespaced host guidance preserves conditional Claude notes without editing the submodule. Required references remain selective.

Adapters use `context --defer-marker` and `ack-context --session ID --revision HASH_OBJECT` after successful output emission. Acknowledgment accepts exactly four section hashes, no task data or approval claims. Omitted/failed acknowledgment repeats context safely. Direct context callers may use the existing immediate marker behavior; it records assembly, never model retention.

## Context measurements

`python3 scripts/orchestrate.py measure` reports core, catalog, bootstrap, unchanged continuation and changed-core bytes, subprocess latency and byte/4 token estimates. Disposable fixtures hold measurement markers and simulated changes. No prompts or candidate bodies are read. Bounds are 8 KiB compact core/catalog and 64 KiB context, with zero unchanged continuation bytes. This measures delivered context, not model judgment or total task token savings.

Manifest reads validate bounded declared registry-source hashes before serving discovery or access. A stale activation/family source returns `STALE_MANIFEST`; rebuild metadata through authorized maintenance instead of selecting from old gates. Binding paths are restricted to hub/family/activation metadata. Candidate bodies and the interaction protocol body are not scanned for discovery freshness; selected entries and required references retain their own identities.
