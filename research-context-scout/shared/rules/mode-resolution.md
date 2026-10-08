# Mode Resolution

Read only when the invocation is not `#> scout` or `#> scout-again`; those two
aliases already fix the mode.

| Invocation | Mode |
|---|---|
| `#> scout ...` | `initial` |
| `#> scout-again ...` | `deepen` |

For `#> use research-context-scout` or an exact natural-language request without
a mode, use record presence: an existing `research-orientation.md` plus
explicitly supplied new information means `deepen`; no existing record means
`initial`.

A first alias argument beginning with `-` is malformed, so
`#> scout -again ...` never becomes an initial run. Quoted examples, code
blocks, later prose mentions and words such as "scouting" do not invoke.

Mode is intent, not permission to skip unfinished work. Record completeness
still selects the phase.

---

[⌂ Home](../../README.md)
