# Skills AI Runtime Protocol

Interaction overview: [[interaction-protocol/README|Interaction Protocol]].

Protocol version: `skills-ai/1`.

## Invariants

- One request selects at most one active/manual skill or returns `NORMAL`.
- The interaction protocol is response context, not a task skill. The general
  contract and optional math overlay do not consume the one-skill limit.
- No match, invalid input, timeout, unavailable manifest, or expected adapter
  failure never blocks the original task.
- Routing does not preload the Markdown hub, family registries, or remembered
  skill bodies.
- Explicit registry-discovery questions return live manifest metadata without
  loading a skill body.
- The `design` and `ui-patterns` families require both an explicit design
  request and a relevant visual/UI/UX domain cue in ordinary prompt prose.
  Trigger-like text inside code, file names, paths, or URLs cannot establish
  design intent.
  Without that gate, routing continues through non-design families or `NORMAL`.
- The request text is never returned or written to diagnostics.
- Skill selection grants no write, credential, network, or account authority.
- Every one-shot router has a bounded input lifetime and exits after one reply.

## Interaction protocols

`interaction.general` gives the result first and adds only enough polished
context to understand and use it. `interaction.math` leads with equations and
mathematical reasoning, followed by short supporting context. Its automatic
gate requires mathematical intent rather than a lone keyword and ignores code,
paths, filenames, URLs, settings, search, parser, and rendering mentions.

Activation behavior is exact:

- `active`: automatic and explicit math selection;
- `manual`: explicit `/interaction math` selection only;
- `off`: no math overlay; and
- `/interaction general`: per-request general override.

The shared router returns the selected interaction mode and reason in every
context packet. Adapters must render that context without duplicating the
detection rules.

## Framing

The caller writes one UTF-8 JSON object followed by `\n`. The router reads one
line and does not wait for EOF. The default input deadline is 10,000 ms because
Codex may start and write to a PTY in separate host calls; direct adapters may
set a shorter bound. The request limit is 1 MiB. A raw one-line query remains
accepted for compatibility. Input beginning with `{` or `[` is treated as
JSON; a valid JSON value that is not an object fails open with `INVALID_INPUT`
instead of being routed as literal text.

```json
{"protocol":"skills-ai/1","request_id":"optional","client":"codex","query":"Explain this code"}
```

The router emits one JSON decision. It never echoes `query`.

```json
{
  "protocol": "skills-ai/1",
  "request_id": "optional",
  "result": "NORMAL",
  "reason_code": "NO_SKILL_MATCH",
  "context": {},
  "router_ms": 1.2
}
```

`--strict` preserves the JSON receipt but returns nonzero for maintenance tools.
The default hot path returns zero after an operational fail-open receipt.

## Stable reasons

Routing reasons include `ACTIVE_SKILL_MATCH`, `NO_SKILL_MATCH`,
`DISABLED_SKILL`, `AMBIGUOUS_SKILL_MATCH`, and `USER_NORMAL`. Boundary reasons
include `INVALID_INPUT`, `REQUEST_TOO_LARGE`, `INPUT_TIMEOUT`,
`UNSUPPORTED_PROTOCOL`, `MANIFEST_UNAVAILABLE`,
`SELECTED_SKILL_UNAVAILABLE`, `ROUTER_INTERNAL_ERROR`, `ADAPTER_TIMEOUT`, and
`CANCELLED`.

`REGISTRY_STATUS` is a non-skill metadata response. It keeps `result: NORMAL`
and adds a `registry` object containing the source hash, active/manual/off route
ids, gate summaries, hidden/deprecated counts, and the no-memory policy.

## Repository-change boundary

When a write-requested prompt explicitly targets Skills AI itself, the shared
context identifies the external-task request-only boundary. A task started
outside this workspace may create one pending request Markdown through
`scripts/create_change_request.py`; canonical implementation belongs to a
dedicated maintenance task rooted in this repository. Host permissions remain
the hard enforcement layer.

## Lifecycle ownership

- Shared Python router: line framing, input deadline, manifest selection,
  structured receipt, prompt privacy, and process exit.
- Codex: writes one framed request, closes or reaps its execution session, and
  continues normally if the session exceeds its host deadline.
- Claude: bounds hook input, gives its Python child a shorter timeout than the
  outer hook, reaps the child, and continues normally on adapter failure.

Codex does not certify Claude integration. Claude does not certify or change
Codex-specific lifecycle without an explicit request.

## Cancellation

The router creates no background child. A host cancellation targets the exact
router session or child, sends `SIGTERM`, allows a short grace period, then may
force-terminate only that exact process. The host must reap or close the process
handle. If a caller abandons stdin, the internal input deadline ends the router.

## Observability

Safe diagnostics contain only adapter, reason code, elapsed milliseconds, and
timeout/cancellation state. They do not contain the prompt, context body, skill
body, credentials, user files, child-process stderr, or local child paths.
