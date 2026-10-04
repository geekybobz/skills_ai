# Skills AI runtime protocol

The model-led responsibility and control contract lives in [[runtime/skills-orchestrator/CONTRACT]]. Exact process and access boundaries live in [[runtime/API_CONTRACT]]. Keep those facts there rather than duplicating a semantic router here.

The host reads the coordination core, resolves user intent and leading controls, discovers bounded metadata, selects the minimum sufficient compatible capability set, loads complete selected entries and required support, performs authorized work, and assesses artifact-bound evidence. The host selects a phase-specific compatible set without a fixed package-count limit. Public counts remain package counts; interaction modes and capability files are internal details.

Everyday controls are `#> use auto|none|<comma-separated package IDs>` and
`#> mode advisory|adaptive|strict`. The shared host instructions define their
aliases, multi-target handling and the visible Task understood/Plan/Skills/Mode
receipt. Presentation happens once at task start under auto, with significant
updates as needed; host-native equivalent fields are reused. There is no new
semantic parser, classifier, task logger or automatic approval gate.

Optional tool or adapter failures fail open to ordinary host work. Failed required evidence obligations remain unresolved. Selection, override, sudo, adherence, autonomy and saved state confer no host authority. Result validation and certification require the named evidence, not a successful transport or identity comparison.

Shared Python owns bounded metadata compilation, prompt-free context assembly, exact file access and structured errors. Codex owns its entry loading and invocation cleanup. Claude owns hook input deadlines, child process-group termination, output injection and native live acceptance. Adapters must not add semantic selection forks.

A single Claude run budget bounds input, Python child execution, core reading and output. The child deadline is shorter than the remaining hook budget; timeout terminates and reaps its process group, including interpreter shims. Host cancellation during input returns a prompt-free reason. The hook does not forward task input to the child. No background watcher, indexer, updater or new ambiguity logger is started.

Local governance scanners inspect repository artifacts; they do not determine the meaning of a user task. External maintenance tasks retain the request-only packet boundary. Generated entries and human guides are projections, not runtime routing or permission authority.

Interaction package: [[interaction-protocol/README]].

Contained maintenance uses `#> repair on/off` and `#> update` under [[protocols/repository/REPAIR_WORKSPACE]]. The host interprets these controls. Source-owned tools snapshot, inspect and transact exact files; they never parse task text or approve deployment. Host-session metadata supports bounded association recovery, not global activation.
