# Mode Fallback

Read only when no validated `mode=` line was injected. With injected context this
file is never loaded.

Resolve the mode from the directive:

| Form | Mode |
|---|---|
| `#> scout ...` | `initial` |
| `#> scout-again ...` | `deepen` |
| `#> skill research-context-scout initial ...` | `initial` |
| `#> skill research-context-scout deepen ...` | `deepen` |

For an exact natural-language package request without a mode, use record
presence: an existing `research-orientation.md` plus explicitly supplied new
information means `deepen`; no existing record means `initial`.

The canonical form requires one of the two modes and rejects a missing or
unknown value. A first alias argument beginning with `-` is malformed, so
`#> scout -again ...` never becomes an initial run. Quoted examples, code
blocks, later prose mentions and words such as "scouting" do not invoke.

Mode is intent, not permission to skip unfinished work. Record completeness
still selects the phase.
