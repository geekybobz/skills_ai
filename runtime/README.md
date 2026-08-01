# Shared Runtime

Interaction overview: [[interaction-protocol/README|Interaction Protocol]].

Platform-neutral hot path for Skills AI.

```text
human registry sources
  -> scripts/compile_registry.py
  -> router-manifest.json
  -> scripts/route_skill.py
  -> interaction context + MATCH(one skill) | NORMAL(fail-open)
  -> thin Codex or Claude adapter
```

Shared components:

- `../interaction-protocol/protocol.json`: compact general contract and the
  equation-led mathematical overlay.
- `router-manifest.json`: generated activation and routing data.
- `SKILL.md`: compact entry contract usable by platform adapters.
- `AGENT_ENTRY_SHARED.md`: canonical repository rules projected into standalone
  Codex and Claude root entries with one small platform overlay each.
- `scripts/registry_runtime.py`: compilation, deterministic selection, and
  structured context assembly, including live registry summaries.
- `scripts/list_registry.py`: read-only active/manual/off discovery without
  loading skill bodies.
- `scripts/create_change_request.py`: the narrow Markdown intake used by tasks
  outside the maintenance workspace.
- `PROTOCOL.md`: one-line framing, deadlines, fail-open reasons, and lifecycle
  ownership.
- `API_CONTRACT.md`: versioned shared request and response schema.

Platform code stays in `adapters/`. Adapters may translate lifecycle events and
install locations, but must not duplicate route rules, interaction rules, or
skill selection logic.

`scripts/compile_repository_views.py` also produces the root agent entries and
exhaustive human reference indexes. Those projections are maintenance artifacts,
not part of the routing hot path.

No-match, disabled, hidden, deprecated, and ambiguous decisions are fail-open:
the task continues normally without a local skill. Skill selection never grants
permission to write files, use credentials, access networks, or change accounts.

Registry discovery is also fail-open and network-free. It reads compiled
metadata, not remembered skill names. External change requests are intake
packets only; a dedicated scoped maintenance task owns implementation.

The one-shot API reads one newline-terminated JSON object and exits after one
response without waiting for EOF. Codex owns Codex session cleanup. Claude owns
its hook and child lifecycle. Platform adapters must convert transport failure
to normal task behavior.
