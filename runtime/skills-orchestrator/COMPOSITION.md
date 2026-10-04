# Capability composition

Back: [[runtime/skills-orchestrator/SKILL|Skills Orchestrator]]. Contract: [[runtime/skills-orchestrator/CONTRACT]].

The host chooses relationships from the desired outcome and declared interfaces. No topology is imposed by a local classifier.

## Small composition card

Keep in current context: objective, topology, phase owner, artifact owners, supporting/review roles, required inputs, fixed assumptions, write sets, handoff consumer, next transition and stop conditions. Record only fields the phase needs. A consequential handoff additionally identifies source artifacts and their content identities, completed/missing checks, unresolved questions and applicable revisions. Persist only with actual write authority.

## Topologies

- Single: load one sufficient capability and required constraints.
- Sequential: producer finishes an inspected artifact; consumer receives its pointers, assumptions and evidence. Recheck input compatibility before the next phase. Do not carry full transcripts or obsolete instruction bodies by default.
- Cooperative: declare one owner per artifact or reviewed artifact region. Supporting capabilities supply constraints or evidence; reviewers return findings. A support summary must preserve all applicable gates and assumptions. Contributions cannot silently become competing edits.
- Parallel: independent inputs and disjoint declared write sets; a named synthesis owner inspects actual outputs. Use subagents only when the user or applicable instructions authorize them. Context isolation is not filesystem isolation. Overlapping writes require serialization or separate checkouts and a reviewed merge. Cancellation targets the affected worker only; partial artifacts are never treated as finished evidence.

Structured durability is independent of topology. Add typed interfaces, artifact identities, checkpoints and transition conditions for expensive or cross-session work. Establish recovery before starting consequential composition.

## Conflicts and failures

Apply higher instruction authority directly. Separate instruction conflict from contradictory scientific assumptions. Expose incompatible assumptions and stop dependent claims; continue independent authorized work. Required execution cycles are invalid; reference links need not form a DAG. Resolve incompatible inputs, excluded required support and competing writers before their actions. Optional support may be dropped when the resulting workflow still satisfies obligations. Skill fallback never erases a failed check, evidence standard or approval requirement.

## Example

An evidence capability produces a source ledger. A theory capability consumes verified claims and a notation reference to write an explanation. The theory capability owns the explanation; a reviewer reports provenance findings. Local checks inspect artifact identity and required evidence. A numerical result is described as local evidence unless a stronger named certificate is established. The host decides which roles are needed and whether a handoff is adequate.
