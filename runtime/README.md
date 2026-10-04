# Shared model-led runtime

The Skills Orchestrator is the host model using [[runtime/skills-orchestrator/SKILL|coordination instructions]]. It owns semantic selection, modes, composition, methods, conflict handling and evidence judgment; it is not counted as a skill.

Metadata flows from registry sources through `compile_registry.py` into the manifest. `orchestrate.py discover` exposes bounded pages without candidate bodies. The host chooses an exact capability and loads it explicitly, then reads required support. The smallest sufficient compatible set may include multiple capabilities. No keyword router chooses a body.

`runtime/SKILL.md` supplies the Codex install header; the installer renders it together with the complete shared core and source identity. Claude delivers context at session lifecycle events and only changed sections on continuation. `runtime/API_CONTRACT.md` documents the shared command interface.

Contracts, composition and recovery are on-demand modules. `model_context.py` handles metadata and exact reads; `orchestration_state.py` handles explicit, artifact-bound checkpoints. Existing project-context and ticket tools remain separate bounded services. Stored commands and receipts confer no authority.

See [[runtime/skills-orchestrator/BUILD]] for actual phase and host acceptance status. Unit tests and byte identities do not establish semantic or scientific certification.

Interaction package: [[interaction-protocol/README]].

Shared `orchestrate.py context` assembles the complete core and bounded metadata without receiving prompts. Claude uses SessionStart for every context lifecycle and a continuation hook for changed sections only. No background service or copied skill bodies are required.

The Codex installed entry includes the shared core and source identity. Generated repository entries keep maintenance/search rules and a core activation pointer. Management detail is on demand in `runtime/skills-orchestrator/MANAGEMENT.md`; `inspire` means advisory.
