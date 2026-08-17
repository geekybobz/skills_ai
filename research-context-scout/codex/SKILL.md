---
name: research-context-scout-codex
description: Codex-only execution wrapper for the shared research-context-scout workflow. Load only after the root research-context-scout skill has selected Codex as the active host.
---

# Codex Wrapper

Follow the root and shared workflow. The record protocol and brief contract live
in `../shared/rules/record-and-brief.md`; do not restate them here.

Use `rg --files` and targeted `rg` before broader reads. For PDFs, use the
available PDF inspection workflow. For current research, browse and cite primary
sources rather than search snippets.

## Live paper-tool contract

Use the tools actually exposed by this Codex host:

- Availability: `list_library_papers` checks the arXiv MCP library;
  `zotero_search_items` checks Zotero. They are different backends. An empty
  successful response from either tool does not prove `absent`. First obtain
  positive health evidence for that same backend. Without it, record
  `unknown (library unreachable)` and use another healthy backend or a supplied
  local file; never turn the empty response into a missing-paper finding,
  exclusion, or corpus-readiness stop.
- Pass 1: prefer `extract_key_findings`; use `smart_extract_paper` only for a
  bounded content preview or section discovery. Inspect the returned shape. If
  either tool returns a full paper body, reclassify that call as pass 2 and do
  not carry the body as cheap coverage context.
- Pass 2: use `download_and_read_paper`, `zotero_get_item_fulltext`, or the PDF
  workflow only for decisive reading. Do not assume
  `approval_mode = "approve"` creates a prompt: require explicit user authority
  for the acquisition/deep-read action before calling a pass-2 tool.

Optional semantic-library tooling is not required. Reserve full-text context
for decisive comparisons.

Use `apply_patch` to create or update only the authorized
`research-orientation.md`. Before that write, or when resolving unusual
path/state cases, read `CODEX.md`.
