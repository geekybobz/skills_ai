---
title: Interaction Protocol
type: protocol-hub
graph_layer: L1
tags:
  - interaction
  - response-contract
  - mathematics
  - routing
---

# Interaction Protocol

Back to [[docs/00_SKILLS_HUB|Skills Hub]] · Controls:
[[registry/activation|Activation]] · Registry:
[[registry/interaction|Interaction Registry]] · Runtime:
[[runtime/PROTOCOL|Runtime Protocol]] · API:
[[runtime/API_CONTRACT|API Contract]] · Migration:
[[docs/INTERACTION_PROTOCOL_MIGRATION|Migration Record]]

This is one public interaction skill package and its visible Obsidian hub. The canonical
machine-readable wording lives in [protocol.json](protocol.json). The registry
controls whether general and math behavior is active; the runtime decides the
current response mode and independently selects at most one task package
capability. The interaction package consumes no task-package slot.

## Authority map

```mermaid
flowchart LR
    HUB["Skills Hub"] --> REG["Interaction Registry"]
    ACT["Activation controls"] --> REG
    REG --> IP["Interaction Protocol hub"]
    IP --> JSON["protocol.json<br/>canonical wording"]
    IP --> RUN["Runtime protocol"]
    RUN --> API["JSON-line API"]
    IP --> MIG["Migration and rollback record"]
```

## General request flow

```mermaid
flowchart LR
    U["User request"] --> G["interaction.general"]
    G --> M{"Mathematical reasoning?"}
    M -- "Yes" --> X["Add interaction.math"]
    M -- "No" --> R["Route task package"]
    X --> R
    R --> S{"Routing Fit?"}
    S -- "Yes" --> L["Load one capability"]
    S -- "No match" --> N["NORMAL"]
    S -- "Material ambiguity" --> C["Ask one short choice"]
    C --> L
    L --> A["Focused response"]
    N --> A
```

## Mathematical response flow

```mermaid
flowchart LR
    Q["Math or research question"] --> C["Check explicit controls"]
    C --> I{"Genuine math intent?"}
    I -- "No" --> G["General protocol"]
    I -- "Yes" --> E["Result or governing equation"]
    E --> D["Define symbols"]
    D --> R["Equation-led reasoning"]
    R --> P["Short supporting context"]
    P --> B["Check, assumptions, or boundary when relevant"]
```

## Controls and tests

- `interaction.general`: active or off.
- `interaction.math`: active, manual, or off.
- `#> skill auto`: select at most one relevant active task package capability.
- `#> skill normal` or “do not use any local skill”: use no local task package.
- `#> skill <exact-package> [capability]`: explicitly request one enabled
  package and optional internal capability; required for a manual package.
- `#> skill interaction-protocol general|math`: select this public package's mode.
- `#> interaction math`: explicit math response for the current request.
- `#> interaction general`: explicit general response for the current request.
- `#> format mermaid+summary`: request known output forms.
- `#> depth brief|standard|detailed`: request explanation depth.
- `#> receipt auto|on|off`: show the task/skill/Fit/style/access receipt
  automatically, always, or never.
- Prompt fixtures: [interaction_cases.json](../tests/interaction_cases.json).
- Runtime tests: [test_registry_runtime.py](../tests/test_registry_runtime.py).
- Graph tests: [test_graph_layers.py](../tests/test_graph_layers.py).

The interaction protocol changes response structure only. It grants no file,
network, credential, account, or destructive-action authority.

Fit is route suitability, not factual confidence: `3` is an exact explicit
route, `2` is one clear contextual route, `1` is unresolved equal candidates,
and `0` means no skill. At Fit 1 the host asks one numbered last-resort choice
only when the alternatives materially change the task; otherwise it continues
normally. The router may record prompt-free candidate metadata under ignored
`.runtime/` state for later local analysis, never the prompt or answer.
