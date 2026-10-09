# Shared model-led runtime

The Skills Orchestrator is the host model following [[runtime/skills-orchestrator/SKILL|its core instructions]]. It owns semantic selection, modes, composition, methods, conflict handling and evidence judgment; it is not counted as a skill.

| need | read |
|---|---|
| instructions: controls, loading, composition, recovery, management | [[runtime/skills-orchestrator/INDEX]] |
| commands, flags and response shapes | [[runtime/API_CONTRACT]] |
| which layer owns what: shared Python, Codex, Claude | [[runtime/PROTOCOL]] |
| actual phase and host acceptance status | [[runtime/skills-orchestrator/BUILD]] |
| interaction package | [[interaction-protocol/README]] |

Metadata flows from registry sources through `compile_registry.py` into the manifest. `orchestrate.py discover` exposes bounded pages without candidate bodies. The host chooses an exact capability and loads it explicitly, then reads required support. The smallest sufficient compatible set may include multiple capabilities.

`runtime/SKILL.md` is only the Codex install header, not the entry: the installer renders it together with the complete core (`core_text` in `model_context.py` removes the core's front matter and Home footer) and the source identity. Claude delivers the same core at session lifecycle events and only changed sections on continuation. `orchestrate.py context` assembles the core and bounded metadata without receiving prompts, and no background service or copied skill bodies are required. Generated repository entries (`AGENTS.md`, `CLAUDE.md`) keep the maintenance and search rules and point to the core.

`model_context.py` handles metadata and exact reads; `orchestration_state.py` handles explicit, artifact-bound checkpoints. Existing project-context and ticket tools remain separate bounded services. Stored commands and receipts confer no authority. Unit tests and byte identities do not establish semantic or scientific certification.
