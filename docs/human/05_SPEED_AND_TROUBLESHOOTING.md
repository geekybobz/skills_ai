---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Speed and Troubleshooting

Back: [safe changes](04_SAFE_CHANGES.md). Next: [graph and colors](06_GRAPH_AND_COLORS.md).

## What is loaded

```mermaid
flowchart LR
    E["Shared entry"] --> R["Core routing and interaction decision"]
    R --> P["Compact general context<br/>plus small math overlay when needed"]
    P --> M{"MATCH?"}
    M -- "No" --> N["Normal response<br/>no local skill body"]
    M -- "Yes" --> S["One selected skill<br/>median 821, max 1,419 tokens"]
    N --> A["Answer"]
    S --> A
    WHOLE["Whole design collection<br/>about 30k tokens"] -. "Avoided" .-> S

    classDef measure fill:#00897B,color:#fff,stroke:#005B52
    classDef safe fill:#2E7D32,color:#fff,stroke:#1B5E20
    classDef avoided fill:#C62828,color:#fff,stroke:#7F0000
    class E,R,P,M measure
    class N,S,A safe
    class WHOLE avoided
```

The 2026-08-06 command-alias benchmark measured 33/33 fixture accuracy, about
`0.39 ms` core-routing p95, and about `38.0 ms` complete-process p95. The
compact receipt measured 94 tokens at the median and 114 at the maximum.
Process time includes
starting Python, reading the request, loading the manifest, routing, writing JSON,
and exiting. Values vary by machine and load; refresh them with:

```bash
python3 scripts/benchmark_router.py --json
```

The new Fit, receipt, depth, and format fields add only small structured
metadata. Depth is emitted on both platform response surfaces rather than being
kept only in the router decision. Routing still performs no project-wide scan. Ambiguity logging runs
only for an equal top match, appends no prompt text, and stops at a 1 MiB cap.
Summarize at most the latest 500 records with:

```bash
python3 scripts/analyze_ambiguities.py --limit 500
```

Maintenance scans are separate from the hot routing path. They use Git to load
only changed paths and affected authorities; the full unit suite is currently a
few seconds, while ordinary routing keeps its small one-shot process.

Initial `plan.md` ideas take a smaller path with no routing, graph, generated
view, or full-test fan-out. For canonical work, run the classifier first so the
agent opens one operation card. Baseline capture is optional and intended for
already noisy worktrees, not every small change.

The shared documentation model adds no normal-task file read. `AGENTS.md` and
`CLAUDE.md` are generated as complete standalone entries, and the live human
indexes remain excluded from the router manifest. Repository-view generation
runs only during maintenance and documentation checks.

Packaged skills keep the same progressive-loading rule. Research Context Scout
loads its small entry, one host wrapper, one shared phase, and the evidence rule
only when recommendations are evaluated; its long human README is excluded.
`#> scout-again` reuses the compact orientation record and new delta instead of
rereading the complete project by default.

## Timeout and cleanup

```mermaid
flowchart TD
    START["Host starts one router"] --> INPUT{"Input arrives before deadline?"}
    INPUT -- "No" --> TIMEOUT["Return fail-open timeout or host fallback"]
    INPUT -- "Yes" --> ROUTE["Write one receipt"]
    ROUTE --> EXIT["Router exits"]
    TIMEOUT --> REAP["Terminate and reap only the recorded process"]
    EXIT --> CLOSED["No router remains"]
    REAP --> CLOSED

    classDef action fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef decision fill:#EF6C00,color:#fff,stroke:#A64700
    classDef safe fill:#2E7D32,color:#fff,stroke:#1B5E20
    class START,ROUTE,REAP action
    class INPUT decision
    class TIMEOUT,EXIT,CLOSED safe
```

The Claude hook spends one budget across the whole run rather than one timer per
phase. A timer bounds the wait for host input; after input ends the Python child
and the single skill-body read are bounded by subtracting elapsed time from the
same budget, because a blocking call cannot be interrupted by a timer. Slow host
input therefore shortens the child instead of pushing the hook past the deadline
Claude settings declare.

Cleanup then has two layers, because a `python3` entry is often a small shell
script in front of the real interpreter, and because the host decides when a
hook run ends. The child starts as its own process-group leader, so a timeout
clears the whole group instead of only the script in front; and the child also
carries the same deadline itself, so it still exits on time when the host stops
the hook first.

## Quick diagnosis

| Symptom | Check |
|---|---|
| Task waits | Confirm one newline-framed request and the configured input deadline |
| `MANIFEST_UNAVAILABLE` | Run compile and registry validation; the task should still continue normally |
| Wrong skill | Add a regression prompt and inspect trigger or ambiguity scoring |
| `#> scout` does not select the skill | Confirm it is the first task directive after optional presentation controls, has whitespace after `#>`, and the research family plus manual skill gate are enabled |
| Canonical Scout returns `INVALID_SKILL_MODE` | Supply exactly `initial` or `deepen` after `#> skill research-context-scout` |
| Scout returns `MALFORMED_COMMAND_ALIAS` | Replace option-like alias arguments such as `#> scout -again` with `#> scout-again <path>` |
| Depth control has no effect | Confirm `depth=...` appears in the Codex compact context or Claude injected context |
| Repeated ambiguity | Run `analyze_ambiguities.py`; improve the recurring candidate pair without opening prompt history |
| Maintenance request selects a task skill | Confirm `SKILLS_AI_MAINTENANCE` is returned before route scoring |
| Consistency scan says `REVIEW` | Read its bounded AI questions and inspect only the listed impacted files |
| Consistency scan says `BLOCK` | Resolve the deterministic missing role, consumer, generated output, link, or failed check |
| Wrong math style | Check action + mathematical-object detection and artifact exclusions |
| Design route on ordinary search | Confirm the explicit design-request gate and its negative corpus |
| Claude hook timeout | Keep the Python child timeout below the outer hook timeout |
| `ADAPTER_INVALID_INPUT` | The host sent the hook a payload that is not one JSON object; the shared router was never reached |
| `ADAPTER_DEADLINE_EXCEEDED` | The whole-run budget ran out before a reply could be written; raise `SKILLS_AI_ADAPTER_TIMEOUT_MS` with the hook timeout in Claude settings |
| `ADAPTER_CANCELLED` | The host stopped the Claude hook while it was waiting for input; the task continues normally |
| `ROUTER_INVALID_OUTPUT` | The shared router replied with something other than one JSON decision; recompile and validate the manifest |
| Router process remains | Terminate and reap only the exact recorded process/session |
| Installed adapter is stale | Dry-run, inspect, then reinstall with platform-owner approval |
| Root entry or live human index is stale | Edit its canonical source, run `compile_repository_views.py`, then re-run the changed or staged scan |
