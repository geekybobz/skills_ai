# Standard skill integration contract

Entry: [SKILL.md](SKILL.md). Wire formats: [API contract](../API_CONTRACT.md).

The responsibilities, package boundary, rule strengths and result labels that every
connected package and host share.

## In brief

The host model decides; local tools expose metadata, read explicitly requested files
and inspect concrete artifacts. A package contract declares capabilities, rules and
verification but never activates a package or grants permission.

## Core

### Responsibility

Codex or Claude understands intent, interprets controls, selects capabilities, plans composition, adapts methods, resolves conflicts, and assesses evidence. Local tools expose metadata, read explicitly requested files, and inspect concrete artifacts. No keyword selector, ranking engine, rule-resolution kernel, or hidden second model makes these decisions.

### Package boundary

A contract declares schema, package ID, version, purpose, capabilities, rule references, verification, and namespaced extensions. Registry activation is independently user-controlled: active, manual, off, hidden, deprecated. A contract never activates a package or grants permission. Required execution dependencies must be acyclic. Reference links are not execution dependencies.

Capabilities declare stable IDs, entry paths, supported roles (primary/supporting/reviewer), purposes, dependencies and optional inputs/outputs. Artifact exchange and reproducibility require explicit inputs/outputs. Submodule and external bodies retain ownership; integration contracts live under orchestrator/registry/contracts/.

### Rule strengths

Invariants preserve correctness, assumptions and provenance. Gates establish named transitions or labels. Required methods apply in strict mode. Defaults and preferences may be replaced for a task-grounded reason. Examples illustrate. Anti-patterns describe a risk requiring evidence before substitution. Unclassified instructions retain their stated force.

### Results

Execution (planned/running/completed/blocked) and verification (unchecked/provisional/validated) are separate. Validated means named checks on exact artifacts and revisions, not scientific truth. Certification requires a named scheme. Failed obligations survive optional routing fallback. Recovery rechecks artifacts, dependency identities and actual approval scope; completed external effects are never blindly repeated.

### Portability and acceptance

Shared instructions apply to Codex and Claude. Adapters transport metadata and the entry instructions without selecting a task body. No background updater, watcher or prompt logger is required. Automated tests establish tool behavior and protocol boundaries; live semantic acceptance is recorded separately per host. Fixtures and textual checks alone cannot certify model decisions.

## Connections

- Related: [Controls](CONTROLS.md)
- Related: [Loading](LOADING.md)
- Related: [Recovery](RECOVERY.md)
- Related: [Management](MANAGEMENT.md)

---

[⌂ Home](INDEX.md)
