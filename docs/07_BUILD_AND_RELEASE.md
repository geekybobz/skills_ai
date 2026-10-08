# Build and release

Back: [[docs/06_CHANGE_CONTROL]] · Runtime: [[runtime/API_CONTRACT]] · Record: [[runtime/skills-orchestrator/BUILD]].

## Requirements

Python 3, Git and the existing project dependencies are required for shared tools and governance. Node.js is required for the Claude adapter. Native-host model access is a separate acceptance requirement; local tests do not establish semantic acceptance.

## Build and validate

```bash
python3 -B scripts/compile_registry.py
python3 -B scripts/compile_repository_views.py
python3 -B scripts/validate_registry.py
python3 -B scripts/toggle_registry.py --check
python3 -B scripts/graph_layers.py --check
python3 -B scripts/compile_repository_views.py --check
```

The registry manifest and repository projections are generated from canonical sources. Keep public package counts separate from capability and graph counts. Do not edit any package submodule or generated mirror as part of a registry rebuild.

## Tests and measurements

```bash
python3 -B -m unittest discover -s tests
python3 -B scripts/orchestrate.py measure
```

The measurement reports actual context-delivery bytes, zero unchanged continuation context, isolated changed-core refresh and process latency. Bytes/4 is an approximate token estimate, not total task cost. The tool reads no candidate bodies and creates only disposable measurement state. Unit fixtures establish access, state, path and lifecycle behavior; actual host decisions require separate inspected responses.

## Adapter acceptance

Use disposable configuration directories for installer checks first. Verify exact source binding, one rendered Codex entry, Claude SessionStart and selective UserPromptSubmit delivery, foreign-hook preservation, backups, idempotent installation, bounded deadlines and process-group cleanup. Test startup, resume, clear, compact and fork. Delivery markers record emitted hashes, never retained model context or authority.

Native-host acceptance records actual host/version/configuration, instruction hashes, inputs, responses/tool calls, artifacts, checks and limitations. Test manual/disabled gates, exact multiple targets, conflicting controls, modes, receipts, composition ownership, context recovery and required evidence after optional failure. Codex results do not certify Claude. See [[docs/CLAUDE_VERIFICATION_PROMPT]].

## Release boundary

1. Preserve dirty-tree state and declare exact scope; work in containment when repair is on.
2. Run classify, plan, changed and staged for the approved operation; resolve every new/in-scope block.
3. Synchronize mapped human pages and regenerate projections.
4. Make a scoped candidate commit; preserve unrelated and submodule changes. A pointer move follows the child-first order in [[protocols/repository/GIT_GOVERNANCE]].
5. Prepare the source-owned exact update preview with bound checks and dependencies. Explain it and obtain actual agreement before apply. Later content changes invalidate the preview.
6. Preserve rollback and the live index. External adapter installation has its own configuration preview/backup boundary.
7. Report local verification and unperformed or blocked native-host checks separately. Neither a saved approval field nor a passing check grants deployment authority.
8. Tag and push only on the user's instruction. A parent release tag follows a passing full scan and records the protocol version, the manifest hash and the pinned child tags or hashes ([[protocols/repository/GIT_GOVERNANCE]]).

## Recovery and rollback

Missing optional metadata/capsules allow normal authorized host work while preserving required obligations. Known corrupt repair state stops mutations instead of redirecting edits live. Compaction or uncertain retention restores complete required instructions, actual scope, artifact/evidence identities and completed external effects.

Use source-owned repair transaction inspection and recovery preview before repeating a deployment. Restore only files whose current bytes match the transaction state; later user edits require reconciliation. Do not discard rollback or historical operational state during this efficiency migration. Pointer and child rollbacks are new commits, never rewrites ([[protocols/repository/GIT_GOVERNANCE]]).

## Contained repair updates

`#> repair on/off` sets chat-scoped containment; `#> update` previews exact changes and waits for agreement. Off preserves the copy, update preserves repair mode and a new chat does not inherit on. Full lifecycle: [[protocols/repository/REPAIR_WORKSPACE]].

## Terminal maintenance interface

Validate the terminal facade with `python3 -B -m unittest discover -s tests -p test_maintenance_cli.py`, then the mapped repository checks. Test host refresh in contained configuration directories. [[protocols/repository/TERMINAL_MAINTENANCE]] defines the JSON envelope, approval, receipts and partial failure boundary.
