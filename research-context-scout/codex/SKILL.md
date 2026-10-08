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

## Host tool names

`../shared/rules/literature-corpus.md` owns the backend-health probe, the
absent/unreachable/unknown states, and the pass-shape and authority guards. This
section only names the Codex tools that satisfy them.

| Shared requirement | Codex tool |
|---|---|
| availability lookup | `list_library_papers` (arXiv library), `zotero_search_items` (Zotero) |
| health control probe | the same tool, on an item already known present |
| pass 1 extraction | `extract_key_findings`, or `smart_extract_paper` for a bounded preview |
| pass 2 full text | `download_and_read_paper`, `zotero_get_item_fulltext`, or the PDF workflow |

The arXiv library and Zotero are different backends: a probe of one says nothing
about the other. Optional semantic-library tooling is not required and is not a
substitute for a health probe.

Use `apply_patch` to create or update only the authorized
`research-orientation.md`. Before that write, or when resolving unusual
path/state cases, read `CODEX.md`.

---

[⌂ Home](../README.md)
