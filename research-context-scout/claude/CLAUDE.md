# Claude Wrapper

Claude-side execution of the shared research-context-scout workflow. The research
logic, the record protocol and the brief contract live in `../shared/`. This file
adds only Claude tool names and Claude lifecycle; it never restates a shared rule.

## Load

1. `../shared/SKILL.md`, reached from `../SKILL.md`.
2. One phase from record state — `../shared/phases/initial-scout.md` for
   `initial`, `../shared/phases/deepen-scout.md` for `deepen`. Load the other
   only for a late state-recovery declared by the selected phase.
3. Rules and templates only at the gates listed in `../shared/SKILL.md`, one at
   a time. Never preload the set.

Never read `../README.md` or `../codex/` during execution. Do not delegate the
workflow to a subagent unless the user asks; a subagent loses the record state
and this bounded load.

## Invoke

`#> scout` is `initial` and `#> scout-again` is `deepen`. For any other
invocation, read `../shared/rules/mode-resolution.md`.

Take the project path from the command arguments only. If it is missing,
ambiguous, or spans projects, ask once and stop; do not glob for a guess.

## Tools

- Glob for the inventory, Grep for the central equation, claim, result, or
  parameter, then Read only the deciding files. Use `offset`/`limit` on long
  drafts and `pages` on PDFs.
- Bash stays read-only here (`git log`, listing results). Never run project code
  or write files through it.
- Literature: prefer connected scholarly MCP tools (arXiv, OpenAlex, Crossref,
  Zotero) loaded through ToolSearch; otherwise WebSearch to shortlist and
  WebFetch to read the source itself.
## Host tool names

`../shared/rules/literature-corpus.md` owns the backend-health probe, the
absent/unreachable/unknown states, and the pass-shape and authority guards. This
section only names the Claude tools that satisfy them.

| Shared requirement | Claude tool |
|---|---|
| availability lookup | `list_library_papers` (arXiv library), `zotero_search_items` (Zotero) |
| health control probe | the same tool, on an item already known present |
| pass 1 extraction | `extract_key_findings`, or `smart_extract_paper` for a bounded preview |
| pass 2 full text | `download_and_read_paper`, `zotero_get_item_fulltext`, or a PDF `Read` |

The arXiv library and Zotero are different backends: a probe of one says nothing
about the other. These MCP tools load through ToolSearch; without them, use
WebSearch to shortlist and WebFetch for pass 2, and treat the absence of a
library as `unknown`, never as `absent`.
- Record writes use Write for a new file and Edit for an existing one, under the
  shared record protocol.

## Status

Claude-authored wrapper; live Claude forward acceptance is not yet certified.
Report platform integration as unverified rather than claiming Codex parity.
