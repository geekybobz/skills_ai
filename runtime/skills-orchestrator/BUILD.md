# Build and verification workflow

Back: [[SKILL|Skills Orchestrator]] · Specification: [[CONTRACT]].

Build in a separate checkout when changes need isolation. Declare exact paths,
preserve existing work and verify each phase before expanding the implementation.
Use operational receipts to record actual observations and unresolved limits.

## Phase boundaries

| Phase | Deliverable | Checks |
|---|---|---|
| Contract | Shared responsibility and package interface | Schema, identities, dependencies and repository roles |
| Coordination | Host selection, modes, scope and evidence instructions | Task scenarios with inspected decisions and justified expectations |
| Access | Bounded discovery and complete exact loading | Pagination, stale metadata, paths, activation and bounds |
| Adapters | Shared entry delivery from the correct source root | Host-specific invocation, output and process cleanup |
| Recovery | Content-bound artifacts, checks and completed effects | Changed identities, interrupted writes and idempotent recovery |
| Composition | Compatible worksets, owners and handoffs | Dependencies, conflicting assumptions and write ownership |
| Integration | Complete workflows and bounded replacement | Artifact checks, live host observations and restoration rehearsal |
| Package integration | Capabilities connected to the standard contract | Domain obligations and exact selected context |

For each phase, record the concrete change, relevant checks, unresolved limits and
a scoped Git commit. Tool fixtures establish mechanical behavior. Semantic
evaluation needs actual host decisions and inspected artifacts. Domain claims
need their own evidence; neither kind of test substitutes for it.

## Verification and change control

Classify the declared paths, follow the matching repository operation card, and
run plan, changed and staged scans at their respective boundaries. Synchronize
mapped human pages and regenerate allowlisted views from canonical sources.
Inspect the final diff for semantic changes and preserve unrelated dirty work.

Use relevant existing checks for documentation-only edits. For runtime work,
test the shared interface first and the affected platform lifecycle separately.
Do not turn an unperformed, skipped or blocked check into a passing result.

## Bounded replacement and restoration

A replacement packet contains exact before/after identities for the declared
files. Preview its scope and verify baseline bytes before an authorized write.
Keep a private backup and verify the resulting files and affected adapters.
Replacement changes the declared working-tree files; it does not require resetting
the live Git index or discarding unrelated changes.

Restoration first checks current identities. Later edits block replacement of
those files. Mixed-state recovery restores only files matching the transaction's
after state, leaves before-identical files alone and refuses conflicting content.
Inspect the recovery preview before writing. Host configuration and external
effects require separate receipts and restoration procedures.

Learning entry: [[docs/human/10_MODEL_LED_ORCHESTRATOR|Orchestrator walkthrough]].

## Current deployment and verification — 2026-10-04

The efficiency implementation is deployed to the source repository. The current
Codex installed entry and Claude managed lifecycle hook/settings passed their
source-binding checks. Foreign Claude configuration and the previous managed
hook were preserved. The installed Claude hook smoke test delivered the full
core at startup and no additional context on an unchanged continuation.

Live checks ran 251 tests: 250 passed and one opt-in optimizer domain integration
was skipped. Metadata, activation, graph, generated views, human-guide coverage,
hook lifecycle, installer preservation and context measurement passed. A repair
acceptance fixture uses its own repository rather than acquiring the live update
transaction's lock.

The core is 6,796 bytes; measured initial context is 9,481 bytes and compact
catalog 2,318 bytes. Unchanged continuation is 0 bytes. Bytes/4 is an estimate,
not a tokenizer count or a measure of total task savings. Measurements and
instruction identities are recorded in `ACCEPTANCE.json`.

Native model-behavior acceptance remains unperformed for these instruction
hashes. Local hooks and CLI checks do not establish native event firing, semantic
adherence or domain certification. No automatic task-memory system is claimed.

The source-owned transaction receipt, exact rollback files and contained Git
bundle remain under ignored `.runtime/repair/`. The original replacement backup
is also retained. Documentation cleanup and a canonical Git checkpoint preserve
those records and the independently owned theory submodule. Repair mode remains
chat-scoped; a Git checkpoint is distinct from an instruction or external-action
approval.
