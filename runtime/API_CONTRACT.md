# Skills AI API Contract

Interaction overview: [[interaction-protocol/README|Interaction Protocol]].

Version 1 is a local JSON-line process API, not a persistent HTTP service. This
keeps normal routing network-free and avoids daemon, port, authentication, and
orphan-process complexity.

## Route request

```json
{
  "protocol": "skills-ai/1",
  "request_id": "host-generated identifier, at most 128 characters",
  "client": "codex or claude",
  "query": "current user request"
}
```

Required: non-empty string `query`. Optional: supported `protocol`,
`request_id`, and informational `client`. Unknown fields are ignored in version
1. The serialized request must fit the documented byte limit and one line;
embedded query newlines are JSON escapes.

## Route response

`MATCH` contains one canonical task-skill record and the shared response
context. `NORMAL` contains no skill body or path unless required for a safe
diagnostic. Both results contain the general, math, or host-default interaction
mode. Interaction protocols never consume the task-skill slot.
Every result also contains ordinal `routing.fit` from 0 to 3 and structured
receipt/output controls. Fit describes route suitability, not answer accuracy.
An explicit registry-discovery question returns `NORMAL / REGISTRY_STATUS` plus
live metadata; it never loads a skill body.

```json
{
  "protocol": "skills-ai/1",
  "request_id": "same optional identifier",
  "result": "MATCH",
  "reason_code": "ACTIVE_SKILL_MATCH",
  "skill": {
    "id": "theory-reference",
    "family": "theory",
    "path": "theory-reference/SKILL.md",
    "state": "active",
    "estimated_tokens": 1200
  },
  "routing": {
    "fit": 2,
    "fit_reason": "unique-context-match"
  },
  "context": {
    "operation": "derive",
    "domain": "theory",
    "requested_access": "read-only",
    "interaction": {
      "mode": "math",
      "reason": "automatic-math"
    },
    "output": {
      "voice": "compact-professional",
      "depth": "standard",
      "shape": "result -> definitions -> equations -> reasoning -> context -> boundary",
      "format": ["auto"]
    },
    "receipt": "auto",
    "project_context": "bounded-host-context",
    "response_contract": []
  },
  "router_ms": 0.6
}
```

The adapter validates a returned skill path against the Skills AI root before
reading it. The original prompt is never present in the response.

Per-request controls are leading `#> override <exact instruction>`,
`#> skill auto|normal|<exact-id>`, `#> interaction general|math`,
`#> format <known+forms>`, `#> depth brief|standard|detailed`, and
`#> receipt auto|on|off`. Controls stay in
`query`; the JSON request envelope does not duplicate them.

A family registry may declare an exact task-directive alias for one enabled
skill and a small invocation mode. Leading presentation controls may precede
it. For example, `#> scout <path>` selects
`research-context-scout` with mode `initial`, while `#> scout-again <paths>` uses
mode `deepen`. Alias arguments remain only in the original host request and are
never copied into the response. Quoted, embedded, code-block, later or partial
matches do not activate aliases. An option-like first alias argument returns
`NORMAL / MALFORMED_COMMAND_ALIAS`.

An alias-selected `MATCH` adds only this bounded context:

```json
{
  "skill_invocation": {
    "command": "#> scout",
    "mode": "initial",
    "scope": "current-request-only"
  }
}
```

For `research-context-scout`, the normal context fields are narrowed to the
skill's public contract:

```json
{
  "requested_access": "write-scoped:research-orientation.md",
  "output": {
    "shape": "supervisor result -> evidence or formulation -> decision boundary -> questions or next investigation -> record path"
  }
}
```

This value authorizes only the project-root record; other supplied artifacts
remain read-only. Alias and canonical
`#> skill research-context-scout <mode> ...` forms add
`skill_invocation.mode`. The canonical form accepts only `initial` or `deepen`;
a missing or unknown mode returns `NORMAL / INVALID_SKILL_MODE`.

Codex and Claude render the same ordered header keys: `route`, `reason`,
optional `skill`/`path` and `command`/`mode`, then `fit`, `fit_reason`,
`operation`, `domain`, `access`, `interaction`, `interaction_reason`, `voice`,
`shape`, `depth`, `format`, `receipt`, `project_context` and `contract`.

`NORMAL / USER_OVERRIDE` contains no echoed query or skill. Its context declares a
current-request-only `local_protocol_override`, the local layers bypassed, and
the higher-level safety and authority boundaries preserved. Bare, embedded,
quoted, or code-block occurrences do not activate the override.

`NORMAL / AMBIGUOUS_SKILL_MATCH` adds bounded public metadata:

```json
{
  "result": "NORMAL",
  "reason_code": "AMBIGUOUS_SKILL_MATCH",
  "routing": {
    "fit": 1,
    "fit_reason": "equal-top-score",
    "candidates": [
      {"id": "code-explainer", "family": "build-ops", "purpose": "explain code"},
      {"id": "debug-helper", "family": "build-ops", "purpose": "debug a failure"}
    ],
    "clarification": {
      "required": true,
      "choices": ["code-explainer", "debug-helper", "normal"]
    }
  }
}
```

Candidate paths, bodies, and the original prompt are omitted. The host asks one
short choice, reroutes with the chosen exact id, and resumes the original task.

## Registry status response

```json
{
  "protocol": "skills-ai/1",
  "result": "NORMAL",
  "reason_code": "REGISTRY_STATUS",
  "registry": {
    "source_hash": "compiled source hash",
    "route_counts": {"active": 45, "manual": 6, "off": 1},
    "routes": {"active": [], "manual": [], "off": []},
    "family_gates": {},
    "component_gates": {},
    "command_aliases": [
      {"command": "#> scout", "skill_id": "research-context-scout", "mode": "initial"}
    ]
  },
  "context": {}
}
```

Hidden and deprecated identifiers are omitted from normal discovery. An
explicit maintenance CLI request may include them. System and plugin skills are
separate host-managed namespaces and are not represented here.

Prompt-free ambiguity metadata is local ignored state rather than API history.
`scripts/analyze_ambiguities.py` reads at most the requested tail of that JSONL
file and performs no mutation or network access.

`NORMAL / SKILLS_AI_MAINTENANCE` identifies an add, edit, update, move, delete,
scan, validation, or governance request targeting Skills AI itself. It prevents
maintenance vocabulary from activating an unrelated task skill. Negated action
phrases are excluded from positive access and skill-trigger evidence.

## External change-request process

`scripts/create_change_request.py --stdin-json` accepts a local JSON object of
at most 64 KiB and
creates one Markdown file under `requests/pending/`. It is not a network API and
does not edit, stage, commit, or launch a maintenance task. Its response returns
the request id, path, workspace, next action, and a platform-neutral handoff
prompt.

## Optional future service

Only add a long-lived local service if end-to-end benchmarks show that process
startup is material. A future localhost or Unix-socket API may expose:

| method | endpoint | purpose |
|---|---|---|
| `POST` | `/v1/route` | `MATCH` or `NORMAL` decision |
| `GET` | `/v1/health` | process and manifest health |
| `GET` | `/v1/manifest/meta` | schema, hash, and route counts |
| `POST` | `/v1/validate` | maintenance validation |

Suggested transport statuses are `200` for a valid decision, `400` for an
invalid envelope, `413` for an oversized request, `422` for an empty query, and
`503` for an unavailable manifest. Host adapters still convert any transport
failure into normal task behavior.

Do not expose mutation endpoints in version 1. Activation remains controlled by
`scripts/toggle_registry.py --dry-run --json` followed by an explicitly
authorized application. Any later `/v1/admin/activation/preview` and `/apply`
design requires a [[protocols/repository/PROTOCOL_AMENDMENT]] review.
