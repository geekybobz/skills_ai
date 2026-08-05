# Skills AI Runtime Protocol

Interaction overview: [[interaction-protocol/README|Interaction Protocol]].

Protocol version: `skills-ai/1`.

## Invariants

- One request selects at most one active/manual skill or returns `NORMAL`.
- A `manual` task skill is eligible only when `/skill <exact-id>`, the exact
  “use the `<id>` skill” form, or a registry-declared leading command alias
  names it. Explicit selection bypasses domain gates for that route but never
  activation, path, or permission checks.
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
- Prompt-free ambiguity observations may be appended under ignored `.runtime/`
  state with mode `0600`; they contain only time, client, candidate ids, Fit,
  operation, and domain and stop at the 1 MiB file cap.
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

## Request controls and receipt

Current-request controls have the highest presentation priority:

- leading `/sudo <exact instruction>` bypasses local Skills AI routing,
  interaction formatting, and repository procedure for the current request;
- `/skill auto|normal|<exact-id>` controls the local task-skill slot;
- registry-declared commands such as `/scout` and `/scout-again` select one
  exact manual skill and attach a bounded invocation mode;
- natural “do not use any local skill” forms map to `USER_NORMAL`;
- `/interaction general|math` controls response style;
- `/format mermaid+summary` selects one or more known output forms;
- `/depth brief|standard|detailed` selects explanation depth; and
- `/receipt auto|on|off` controls the compact visible task receipt.

The precedence is current request, session preference, project default, global
default, then automatic detection. Natural-language output instructions in the
prompt remain authoritative. Bounded project context means already available
project instructions plus user-named or directly relevant files; routing never
scans a repository merely to fill the receipt.

Command aliases are data in one family registry, not hard-coded keyword
substitutions. They activate only as the first non-whitespace command, never
from quotations, code, URLs, later mentions or near-matching words. The router
returns only `command`, `mode` and current-request scope; it does not echo alias
arguments. `/skill normal` still opts out, and leading `/sudo` retains its
earlier override boundary.

`/sudo` is deliberately not a presentation option and is not stored in the
interaction protocol. It is recognized only as the first non-whitespace token
and only when an instruction follows. It never activates from quoted text,
code, a URL, a later mention, or the bare shell word `sudo`. The override is
local: system and developer instructions, host permissions, sandbox limits,
credentials, external actions, destructive-action safety, and exact user scope
remain authoritative.

`routing.fit` is ordinal route suitability: `3` explicit exact skill, `2`
unique contextual match, `1` unresolved equal top candidates, and `0` no skill,
disabled skill, opt-out, maintenance, or fail-open. It is not a probability and
says nothing about answer correctness.

An equal top score returns `NORMAL / AMBIGUOUS_SKILL_MATCH` with candidate id,
family, and purpose but no path or body. The host asks one short numbered choice
only when the alternatives materially change the work. After the user chooses,
it reroutes by exact id and continues the original task.

## Framing

The caller writes one UTF-8 JSON object followed by `\n`. The router reads one
line and does not wait for EOF. The default input deadline is 10,000 ms because
Codex may start and write to a PTY in separate host calls; direct adapters may
set a shorter bound. The request limit is 1 MiB. A raw one-line query remains
accepted for compatibility. Any valid JSON value is parsed as JSON; a value
that is not an object fails open with `INVALID_INPUT` instead of being routed as
literal text. Non-JSON one-line text remains the raw-query compatibility path.

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
`DISABLED_SKILL`, `AMBIGUOUS_SKILL_MATCH`, `USER_NORMAL`,
`USER_SUDO`, `UNKNOWN_SKILL_REQUEST`, and `SKILLS_AI_MAINTENANCE`. The maintenance reason keeps repository-governance
requests on the normal path instead of allowing words such as `node` or a
negated `install` to select an ordinary task skill. Boundary reasons
include `INVALID_INPUT`, `REQUEST_TOO_LARGE`, `INPUT_TIMEOUT`,
`UNSUPPORTED_PROTOCOL`, `MANIFEST_UNAVAILABLE`,
`SELECTED_SKILL_UNAVAILABLE`, `ROUTER_INTERNAL_ERROR`, `ADAPTER_TIMEOUT`, and
`CANCELLED`.

`REGISTRY_STATUS` is a non-skill metadata response. It keeps `result: NORMAL`
and adds a `registry` object containing the source hash, active/manual/off route
ids, gate summaries, hidden/deprecated counts, and the no-memory policy.

Analyze prompt-free ambiguity frequencies without loading prompts or skills:

```bash
python3 scripts/analyze_ambiguities.py --limit 500
```

## Repository-change boundary

An initial idea stored only at `skill-plans/<name>/plan.md` is not a skill and
does not enter routing, graph, generated views, or full consistency validation.
Creating `SKILL.md` is the explicit promotion boundary.

For governed work, `scan_consistency.py classify --path ...` selects the one
operation card and check set. Optional `plan --baseline-out
.runtime/<name>.json` records prompt-free failure signatures; a later
`changed --baseline .runtime/<name>.json` preserves only identical old
failures while new or changed failures continue to block. A baseline is valid
only for the same protocol version, operation, and declared path set.

When a write-requested prompt explicitly targets Skills AI itself, the shared
context identifies the external-task request-only boundary. A task started
outside this workspace may create one pending request Markdown through
`scripts/create_change_request.py`; canonical implementation belongs to a
dedicated maintenance task rooted in this repository. Host permissions remain
the hard enforcement layer.

Maintenance intent is recognized before task-skill scoring. Negated action
clauses such as “no external install” do not establish write access or positive
installation intent.

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
