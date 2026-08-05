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

Protocol version 7 additionally separates generated-guide freshness from
hand-written coverage, admits only role-resolved untracked additions into the
live repository view, and reserves ignored `.runtime/` state for bounded,
prompt-free observations. Runtime observations never become routing or
documentation authority.

Protocol version 8 makes Obsidian colour an architectural node-type contract.
All declared concept entries and the Activation switchboard are L1 hubs, family
registries are L2, parked cards are L3, executable skills and phases are L4,
and support remains L5. `CONTRACT.json` records role sentinels, the graph
validator rejects a hub with a registry or skill colour, and the default global
view hides low-level maintenance paths without changing the underlying graph.

Protocol version 9 separates an unimplemented `plan.md` idea from a routable
skill, adds a current-request `/sudo` escape from local Skills AI procedure,
supports proportional and baseline-aware validation, and provides a one-step
maintenance classifier. Higher-level authority and safety boundaries remain
unchanged.

An amendment requested from outside the Skills AI maintenance workspace first
uses [[EXTERNAL_CHANGE_REQUEST]]. The external task records the proposal but
does not edit this protocol directly.
