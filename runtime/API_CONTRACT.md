# Skills AI API Contract

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

`MATCH` contains one canonical skill record and the shared response context.
`NORMAL` contains no skill body or path unless required for a safe diagnostic.

```json
{
  "protocol": "skills-ai/1",
  "request_id": "same optional identifier",
  "result": "MATCH",
  "reason_code": "ACTIVE_SKILL_MATCH",
  "skill": {
    "id": "caveman-math",
    "family": "compression",
    "path": "caveman/skills/caveman-math/SKILL.md",
    "state": "active",
    "estimated_tokens": 1200
  },
  "context": {
    "operation": "derive",
    "domain": "mathematics",
    "requested_access": "read-only",
    "output": {
      "voice": "compact-professional",
      "depth": "standard",
      "shape": "result -> setup -> equations -> derivation -> boundary"
    },
    "response_contract": []
  },
  "router_ms": 0.6
}
```

The adapter validates a returned skill path against the Skills AI root before
reading it. The original prompt is never present in the response.

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
