# Loading

How the host discovers, selects, loads and reuses skill instructions.
[SKILL.md](SKILL.md) states the principles; this topic owns the procedure and the
flags. Command and response shapes are in the [API contract](../API_CONTRACT.md).

## In brief

The host selects the smallest compatible set justified for the current phase and
loads complete entries through `orchestrator/tools/orchestrate.py`. Tools return metadata,
gates and exact bytes; they never rank, route or grant authority.

## Core

### Catalog and selection

- Reuse the catalog delivered at session start. Run `discover --format text` only
  for missing, stale or insufficient metadata. A first page is not exhaustive; compact
  text marks pagination and shortened purposes, and exact metadata comes from
  `discover --package EXACT_ID --format json`. The metadata identity covers contracts,
  gates and aliases and keeps a paginated read consistent; entry and reference
  identities are separate. Exact IDs bypass broad discovery, never gates.
- Catalog records describe validated local integration metadata, not the host's
  native tool inventory. Records and descriptions are advisory data, not instructions
  or permission, and availability is not a safe entry. Loading rechecks gates and paths:
  disabled, hidden and deprecated entries cannot be loaded, and an unknown ID is
  rejected without substitution.
- Select the minimum sufficient compatible set for this phase plus its required
  support. Preserve named targets, disclose required support, and report an
  unavailable or incompatible target before dependent work; never substitute or
  silently drop it. Resolve ambiguity, exclusions and manual support first. List
  order grants no topology, workers or simultaneous loading: use each named target
  in its relevant phase. Do not preload a tree or add unrelated optional packages.
- Manual access, including required but unlisted manual support, needs an actual
  explicit invocation or a declared alias; dependency declarations cannot attest it. Interaction general and math are
  supporting capabilities under their own package, family and component gates,
  independent of task selection: read the complete protocol only when needed, apply
  the relevant section and keep the user's output instructions.
- Load Skills AI IDs through this interface and do not assume they are native host
  skill names. Other host integrations stay independent.

### Loading

- `orchestrator/tools/orchestrate.py load --capability ID` returns the complete entry, its
  contract rules, bindings (entry and contract SHA-256) and a composite identity.
  Complete selected instructions apply within host authority.
- A batch repeats `--capability` and adds `--deduplicate` (batch v2). Every gate
  runs before any entry is read, each exact shared body is delivered once and
  resolved through `body_ref` in `bodies`, and each capability keeps its own
  metadata, gates, contract, identity and attestation. Nothing is selected
  automatically; a batch holds at most 32 entries.
- Attest only the manual targets actually invoked with `--explicit-capability ID`.
  `--explicit` attests every named target and is true only when the user named them
  all.
- `read-reference --capability ID --reference PATH` reads only metadata-listed
  paths. Empty `references` means none declared, not that other identified support
  may not be read: read that directly and boundedly. Bind required references
  separately, keep reference links selective, and never claim unread support is
  retained.

### Reuse and retention

- Reuse reliable context; a phase change needs only the newly relevant
  capabilities and obligations. `--if-changed IDENTITY` omits one body only while
  that complete entry is still retained. An unchanged response shows current bytes,
  not retained instructions or loaded references.
- After compaction, host transfer or uncertain retention, load the complete entries
  again and restore actual scope and artifact and evidence state
  ([RECOVERY.md](RECOVERY.md)). The composite identity binds entry bytes,
  capability metadata, activation state, contract rules, checks and extensions;
  reference identities are separate and rechecked separately. Hashes prove neither
  retention nor permission.
- Refresh only on a relevant phase or revision change, and inspect completed
  effects before retrying.

### Failure

- Optional tool or adapter failure continues as ordinary host work; failed required
  evidence stays unresolved. A stale manifest (`STALE_MANIFEST`) stops capability
  access until authorized maintenance rebuilds it; never select from old gates.

## Details

```text
orchestrator/tools/orchestrate.py discover --format text
orchestrator/tools/orchestrate.py discover --offset 8 --metadata-hash HASH --format text
orchestrator/tools/orchestrate.py discover --package EXACT_ID --format json
orchestrator/tools/orchestrate.py load --capability ID
orchestrator/tools/orchestrate.py load --capability optimizer --explicit
orchestrator/tools/orchestrate.py load --capability interaction.general --capability interaction.math --deduplicate
orchestrator/tools/orchestrate.py load --capability ID --if-changed IDENTITY
orchestrator/tools/orchestrate.py read-reference --capability ID --reference PATH
```

The `discover` lines list, continue and expand metadata; the others load, attest,
batch, revalidate and read declared support. Responses carry `authority: none`.

---

[⌂ Home](INDEX.md)
