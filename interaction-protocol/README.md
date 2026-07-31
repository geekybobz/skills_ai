---
title: Interaction Protocol
type: protocol-hub
graph_layer: L4
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

This is the visible Obsidian hub for the shared response protocol. The canonical
machine-readable wording lives in [protocol.json](protocol.json). The registry
controls whether general and math behavior is active; the runtime decides the
current response mode and independently selects at most one task skill.

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
    M -- "No" --> R["Route task skill"]
    X --> R
    R --> S{"One clear enabled skill?"}
    S -- "Yes" --> L["Load one task skill"]
    S -- "No or ambiguous" --> N["NORMAL"]
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
- `/interaction math`: explicit math response for the current request.
- `/interaction general`: explicit general response for the current request.
- Prompt fixtures: [interaction_cases.json](../tests/interaction_cases.json).
- Runtime tests: [test_registry_runtime.py](../tests/test_registry_runtime.py).
- Graph tests: [test_graph_layers.py](../tests/test_graph_layers.py).

The interaction protocol changes response structure only. It grants no file,
network, credential, account, or destructive-action authority.
