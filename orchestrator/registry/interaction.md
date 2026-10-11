# Interaction Protocol Registry

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · Protocol:
[[skills/interaction-protocol/README|Interaction Protocol]] · Runtime:
[[orchestrator/runtime/PROTOCOL|Runtime Protocol]]

One public interaction skill package, not a task package. Check
[[orchestrator/registry/activation]] before using either internal mode.

## Internal Modes

| protocol | does | selection | not for |
|---|---|---|---|
| `interaction.general` | gives the result first, then only enough polished context to understand and use it | applied to every request while active | extreme compression or character voice |
| `interaction.math` | leads with equations and mathematical reasoning, then adds short supporting context | automatic response support for clear mathematical intent while active; explicit request only while manual | keyword mentions in code, paths, filenames, settings, search, or rendering tasks |

The canonical machine-readable contract is linked from
[[skills/interaction-protocol/README|the protocol hub]]. The host composes these response
rules with its phase-specific compatible task capability set. Math
therefore remains independent response support within one public package.

## Automatic Math Boundary

Automatic selection requires mathematical intent, not a lone keyword:

- a mathematical action plus a mathematical object or expression;
- an explanatory question about a strong mathematical object; or
- research context explicitly asking for mathematical or analytical reasoning.

Explicit style controls are `#> interaction math` and
`#> interaction general`. The shared request layer also supports
`#> use auto|none|<package IDs>`, `#> mode`, `#> format`,
`#> depth compact|standard|deep`, and `#> receipt auto|on|off`.
Current-request controls win over session, project, global, and automatic
defaults. Natural-language output instructions remain authoritative.

## Help operations

| kind | syntax | does | boundary |
|---|---|---|---|
| `chat` | `#> interaction general` | Request the general response mode for the current request. | Changes presentation only; grants no task or tool authority. |
| `chat` | `#> interaction math` | Request equation-led mathematical reasoning for the current request. | Changes presentation only; mathematical intent and evidence boundaries still apply. |
| `chat` | `#> format <form>` | Request a supported output form such as a summary or Mermaid diagram. | Renderer and factual verification remain separate. |
| `chat` | `#> depth compact / standard / deep` | Choose the explanation depth for the current request. | Does not remove required context, evidence, or safety boundaries. |
| `chat` | `#> receipt auto / on / off` | Control visibility of the task receipt. | Hides or shows the receipt only; it never changes approvals or obligations. |

## Rules

- `active`: automatic and explicit math selection are allowed.
- `manual`: only an explicit math control selects the math protocol.
- `off`: the protocol is not added to runtime context.
- No interaction protocol grants file, network, credential, or account access.
- Suitability assessments concern task fit, never factual confidence.
