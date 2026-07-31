# Skills AI Change Control

Repository-governance entry for changes under `/Users/billabobz/skills_ai`.
Normal task routing does not load this file. Before a repository write, identify
one operation below, read only its card, and also apply [[04_RISK_MAP]].

Protocol version: `4`.

## Operation selector

| intended change | read |
|---|---|
| add a canonical file, route, skill, component, adapter, script, or document | [[protocols/repository/ADD\|ADD]] |
| localized change that preserves identity and public contracts | [[protocols/repository/EDIT\|EDIT]] |
| change a schema, protocol, dependency, installer, or public behavior | [[protocols/repository/UPDATE_MIGRATE\|UPDATE_MIGRATE]] |
| change an identifier, path, or owner | [[protocols/repository/MOVE_RENAME\|MOVE_RENAME]] |
| disable, deprecate, or remove behavior or files | [[protocols/repository/DEPRECATE_DELETE\|DEPRECATE_DELETE]] |
| write under Codex, Claude, or another external configuration root | [[protocols/repository/INSTALL_UNINSTALL\|INSTALL_UNINSTALL]] |
| work beyond the authorized request | [[protocols/repository/SCOPE_EXPANSION\|SCOPE_EXPANSION]] |
| change these governance rules | [[protocols/repository/PROTOCOL_AMENDMENT\|PROTOCOL_AMENDMENT]] |
| request a Skills AI change from a task outside this workspace | [[protocols/repository/EXTERNAL_CHANGE_REQUEST\|EXTERNAL_CHANGE_REQUEST]] |

Do not combine several cards by default. Pick the operation with the largest
contract or lifecycle effect. A localized edit that changes a public contract
is an update/migration, not an edit.

## Compact change packet

```yaml
operation:
requested_scope:
allowed_paths:
source_of_truth:
generated_outputs:
external_effects: none
approval_status:
risk_level:
verification:
rollback:
graph_layer:
graph_query_covered: yes/no/not-applicable
graph_policy_change: none/required
human_docs_impact: update-required/reviewed-no-change
human_docs_pages:
human_docs_reason:
```

This packet structures the work; it does not grant authority. An explicit user
request authorizes the named reversible add/edit/update scope. Canonical
deletion, external configuration, credentials, account/network actions, Git
history rewrites, protocol amendments, and unexpected expansion require an
exact preview and explicit permission.

After permission, a non-sensitive turn or review reference may be passed to
`change_guard.py --approval-ref`. The guard records that reference but cannot
verify or manufacture authority; the user's actual instruction remains the
source of permission.

## Shared rules

1. Inspect live Git state and preserve unrelated changes.
2. Modify canonical sources, not generated mirrors.
3. Never cross a submodule or external-configuration boundary implicitly.
4. Skill selection does not grant write or installation authority.
5. Run `scripts/change_guard.py plan` before structural work and
   `check-staged` before committing.
6. Keep governance, shared runtime, Codex integration, and Claude integration
   ownership explicit.
7. Report the exact files, behavior, verification, and residual risk.
8. Stage only the declared scope.
9. Classify every new or moved Markdown file under [[05_COLOR_LAYERS]], require
   its path to match a canonical colour query, and run
   `python3 scripts/graph_layers.py --check`. A new layer or colour is a
   protocol amendment.
10. Evaluate every declared change against `docs/human/_SOURCE_MAP.json`. A
    mapped canonical change must update every listed human page in the same
    staged change. Run `python3 scripts/human_docs_guard.py --check-staged`
    before commit. Human pages are explanatory only and never routing authority.

## External-task boundary

A task whose initial workspace is outside `/Users/billabobz/skills_ai` has no
direct edit path into this repository. An explicit external change request
authorizes only a new generated Markdown packet under `requests/pending/`.
Implementation requires a dedicated maintenance task rooted here and scoped by
the request, risk map, selected operation card, and change guard. Host workspace
permissions must enforce read-only repository access plus the narrow request
inbox; agent instructions alone are not a filesystem security boundary.

## Authority layers

- `AGENTS.md` and `CLAUDE.md`: small platform entry pointers.
- This file: operation selection.
- `protocols/repository/`: execution procedure for one operation.
- [[04_RISK_MAP]]: risk-specific restrictions.
- [[05_COLOR_LAYERS]]: graph-layer assignment and colour-query authority.
- `docs/human/`: derivative human guide, loaded only for explicit guide work or
  required synchronization.
- `runtime/PROTOCOL.md`: router wire and lifecycle contract.
- `registry/activation.md`: user-controlled routing state.
- `requests/pending/`: external intent packets, never skill or routing source.

The registry remains routing metadata. Repository governance is not a skill
family and is not compiled into `runtime/router-manifest.json`.
