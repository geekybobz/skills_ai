# Interaction Protocol Registry

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · Protocol:
[[interaction-protocol/README|Interaction Protocol]] · Runtime:
[[runtime/PROTOCOL|Runtime Protocol]]

Shared response behavior, not a task skill. Check [[registry/activation]] before
using either protocol.

## Protocols

| protocol | does | selection | not for |
|---|---|---|---|
| `interaction.general` | gives the result first, then only enough polished context to understand and use it | applied to every request while active | extreme compression or character voice |
| `interaction.math` | leads with equations and mathematical reasoning, then adds short supporting context | automatic high-confidence mathematical reasoning while active; explicit request only while manual | keyword mentions in code, paths, filenames, settings, search, or rendering tasks |

The canonical machine-readable contract is linked from
[[interaction-protocol/README|the protocol hub]]. The shared runtime composes these response
rules with at most one independently selected task skill. Math therefore does
not consume the task-skill slot.

## Automatic Math Boundary

Automatic selection requires mathematical intent, not a lone keyword:

- a mathematical action plus a mathematical object or expression;
- an explanatory question about a strong mathematical object; or
- research context explicitly asking for mathematical or analytical reasoning.

Explicit controls are `/interaction math` and `/interaction general`.

## Rules

- `active`: automatic and explicit math selection are allowed.
- `manual`: only an explicit math control selects the math protocol.
- `off`: the protocol is not added to runtime context.
- No interaction protocol grants file, network, credential, or account access.
