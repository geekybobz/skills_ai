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

## Shared verification and update boundary

The shared fixes preserve model-owned decisions, existing single/default batch
responses, compatibility aliases, capability gates and skill-specific content.
Opt-in batch v2 delivers exact shared bodies once; read-only status and reference
metadata standardize access for any connected host. Host settings remain owned
by each integration.

Record current checks and instruction hashes in `ACCEPTANCE.json`; retained Git
history and ignored transaction receipts preserve earlier evidence. Candidate
verification does not mean live deployment. Source-owned update previews bind
checks to the exact candidate; application waits for actual agreement. Installed
entries may need their host's refresh after source deployment, outside this
shared change.

Test all gates before any shared body read, legacy response compatibility,
reference declaration boundaries, successful repair start/pause, exact association,
corrupt-state failure, status without writes and selective context delivery.
Semantic scenarios in tests/model_orchestration_cases.json include genuine
multi-turn sequences: send each turns item only after the previous response.
A keyword match or attempted/denied controller call is not successful behavior.

Keep separate outcomes: pass, fail, blocked, skipped and superseded. Each final
record names the exact revision/content and inspected evidence. Never silently
remove timeouts from success denominators or merge incompatible test fixtures.
Local process tests do not certify model selection, adherence or real compaction
recovery; each connected host owns its live acceptance.

Core/bootstrap delivery budgets are 5.5/8 KiB in the reference measurement flow;
transport bounds remain separate. Zero unchanged delivery bytes and byte/4
estimates describe instruction delivery, not total context tokens or model cost.
Checkpoints remain explicitly authorized advisory data, not automatic memory.
