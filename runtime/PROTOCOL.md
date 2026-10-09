# Skills AI runtime protocol

The orchestrator's instructions are split by job: responsibility and rule strengths live in [[runtime/skills-orchestrator/CONTRACT]], the control vocabulary and receipt in [[runtime/skills-orchestrator/CONTROLS]], loading and retention in [[runtime/skills-orchestrator/LOADING]]. Exact process and access boundaries live in [[runtime/API_CONTRACT]]. Keep those facts there rather than duplicating them here.

The host reads the coordination core, resolves user intent and leading controls, discovers bounded metadata, selects the minimum sufficient compatible capability set for the phase without a fixed package-count limit, loads complete selected entries and required support, performs authorized work, and assesses artifact-bound evidence. Public counts remain package counts; interaction modes and capability files are internal details. There is no new semantic parser, classifier, task logger or automatic approval gate.

Optional tool or adapter failures fail open to ordinary host work. Failed required evidence obligations remain unresolved. Selection, override, sudo, adherence, autonomy and saved state confer no host authority. Result validation and certification require the named evidence, not a successful transport or identity comparison.

Shared Python owns bounded metadata compilation, prompt-free context assembly, exact file access and structured errors. Codex owns its entry loading and invocation cleanup. Claude owns hook input deadlines, child process-group termination, output injection and native live acceptance. Adapters must not add semantic selection forks. Host-specific settings and transport fixes belong to each host integration.

A single Claude run budget bounds input, Python child execution, core reading and output. The child deadline is shorter than the remaining hook budget; timeout terminates and reaps its process group, including interpreter shims. Host cancellation during input returns a prompt-free reason. The hook does not forward task input to the child. No background watcher, indexer, updater or new ambiguity logger is started.

Local governance scanners inspect repository artifacts; they do not determine the meaning of a user task. External maintenance tasks retain the request-only packet boundary. Generated entries and human guides are projections, not runtime selection or permission authority.

Contained maintenance uses `#> repair on/off` and `#> update` under [[protocols/repository/REPAIR_WORKSPACE]]; status, repair and update procedures are in [[runtime/skills-orchestrator/MANAGEMENT]]. The host interprets these controls. Source-owned tools snapshot, inspect and transact exact files; they never parse task text or approve deployment. Host-session metadata supports bounded association recovery, not global activation.

Shared status exposes bounded facts without loading skills or writing markers; the host supplies effective controls and retained-context claims. The response shape is in [[runtime/API_CONTRACT]] and the scope and reset rules are in [[runtime/skills-orchestrator/CONTROLS]].

Interaction package: [[interaction-protocol/README]].
