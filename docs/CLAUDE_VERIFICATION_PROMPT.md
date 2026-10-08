# Native-host acceptance checklist

Use the current shared core and contract. Test Codex and Claude separately; local CLI/hook tests establish transport behavior only. Obtain actual authorization before sending new repository test payloads to an external model.

Record host/version/configuration, exact inputs, actual replies/tool calls, artifact revisions, checks, context bytes and limitations. Use disposable test workspaces. Start with explanation-only scenarios that forbid tools, skill execution and edits; then separately test actual adapter lifecycle and scoped work when authorized.

Check explicit single and multiple targets, use none, unavailable targets, relevant uninvoked manual skills, required manual dependencies, conflicting controls, inspire/adaptive/strict, request scope, receipt reuse, composition ownership, changed metadata and compaction. Required gates/evidence must survive optional loading failure. Recovery must restore complete instructions before consequential work and preserve actual scope.

For Markdown Protocol, test the same three semantic boundaries on each host:

- A request to create or edit Markdown selects `markdown-protocol`
  automatically, announces it, proposes a change proportional to the impact,
  and waits before writing.
- `#> md_protocol` resolves to the package's `guided` mode.
- Reading `AGENTS.md` or another Markdown instruction as operational input for
  a non-Markdown task does not select the package by itself.

After approval, verify that in-scope continuation does not repeat the proposal
gate and that a material file, ownership, layout, or renderer expansion pauses
for renewed review. User-authored edits must be preserved as current source
state rather than silently reverted.

For Claude test startup, resume, clear, compact and fork delivery plus zero unchanged continuation context. Test failed output/acknowledgment and foreign hook preservation. For Codex verify one merged installed entry and stale-source detection; do not assume a Claude hook exists there.

Repair on/off and update tests use the source-owned controller, retained containment and exact reviewed bytes. A successful local check never grants deployment approval or scientific certification.
