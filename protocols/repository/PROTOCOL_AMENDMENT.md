# Protocol Amendment

Back: [[docs/06_CHANGE_CONTROL|Change Control]].

Use when evidence shows that a governance rule is missing, unsafe, ambiguous,
or inconsistent with implementation.

```text
Protocol-amendment proposal

Current protocol and version:
Observed gap and evidence:
Why the current rule is insufficient:
Proposed replacement:
Operations and platforms affected:
Compatibility impact:
New tests:
Graph-layer and colour-query impact:
Human-guide pages affected:
Migration and rollback:
Permission requested:
```

Do not silently rewrite a protocol while completing another task. Obtain
approval, update backlinks and validators, and prefer a separate commit so Git
history preserves the motivation. Recheck protocols after repeated exceptions,
source-of-truth conflicts, new irreversible actions, host-specific divergence,
or a validation gap. Any new graph layer or colour must update
`docs/05_COLOR_LAYERS.md`, the live Obsidian groups, and the graph validator in
the same approved amendment. Any mapped canonical change must update the
corresponding derivative human pages in the same staged change.

Changing `CONTRACT.json`, scanner severities, executable check mappings, or the
human-guide rendering limits is itself a protocol amendment. Run the protocol
plan before editing and both changed and staged scans after editing.

Changing `DOCUMENTATION.json`, shared agent-entry generation, platform overlays,
generated human indexes, or the source-to-projection rules is also a protocol
amendment. Keep the architecture rationale in
[[docs/SHARED_DOCUMENTATION_MODEL]], regenerate all affected projections, and
verify that ordinary routing still excludes human-facing material.

## Current contract

Protocol version 17 keeps these boundaries:

- The host model owns intent, compatible capability selection, methods, modes,
  composition and evidence assessment. Local tools check artifacts and expose
  exact metadata and instructions; they do not perform semantic routing.
- The orchestrator is always active and is not a public skill. Count packages,
  with capabilities and response modes listed as internal detail.
- Shared coordination uses the platform-neutral `#>` controls. User authority,
  host permissions, manual/disabled gates and external-action boundaries remain
  separate from selection and stored state.
- Repository roles, graph layers and generated source-to-view mappings stay
  explicit. Generated human-guide freshness differs from hand-written coverage;
  human guides remain outside ordinary runtime loading.
- Initial `skill-plans/*/plan.md` ideas remain proposals until explicit promotion.
  Tasks started outside this maintenance workspace use [[EXTERNAL_CHANGE_REQUEST]].
- Chat-scoped repair uses the source-owned controller and retained rollback.
  Exact update review, actual agreement and separately bounded live staging
  protect existing work. Saved records confer no authority.
- Context assembly receives no task prose. Claude restores full core context at
  lifecycle events and only changed sections on continuation. Private markers
  attest delivery rather than model retention; uncertain retention requires full
  recovery. Codex uses one source-bound installed entry.
- The shared interface is context, discovery and exact loading, with current-flow
  measurement. Native-host acceptance remains separate from local tool checks.
- Only current controls, aliases and file layouts are documented and supported.
  Retired syntax, compatibility aliases and migration records are deleted rather
  than kept as history; Git retains earlier revisions.
- Skill packages stored as Git submodules are separately owned repositories. A
  change is made, tested, committed and pushed in the child first; the parent then
  moves its pointer to a clean, published commit. Clone modes, branches, versions,
  releases, rollback, dirty state and cleanup follow [[GIT_GOVERNANCE]]. Commits,
  tags, pushes and deletions need the user's instruction for the exact action.

Keep this card current when amending the contract. Git history and private
rollback receipts retain previous revisions; operational documentation explains
current behavior.
