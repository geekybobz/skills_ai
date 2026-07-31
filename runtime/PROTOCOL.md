# Skills AI Runtime Protocol

Protocol version: `skills-ai/1`.

## Invariants

- One request selects at most one active/manual skill or returns `NORMAL`.
- No match, invalid input, timeout, unavailable manifest, or expected adapter
  failure never blocks the original task.
- Routing does not preload the Markdown hub, family registries, or remembered
  skill bodies.
- The request text is never returned or written to diagnostics.
- Skill selection grants no write, credential, network, or account authority.
- Every one-shot router has a bounded input lifetime and exits after one reply.

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
