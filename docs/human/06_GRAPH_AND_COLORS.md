---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Graph and Colors

Back: [speed and troubleshooting](05_SPEED_AND_TROUBLESHOOTING.md). Next:
[maintaining skills](07_MAINTAINING_SKILLS.md).

Color describes architectural depth, not topic. New skills reuse an existing
layer color rather than receiving a new color.

```mermaid
flowchart LR
    L0["L0 Indigo<br/>Entry documents"] --> L1["L1 Teal<br/>Global maps"]
    L1 --> L2["L2 Green<br/>Registry and activation"]
    L2 --> L4["L4 Violet<br/>Skills and phases"]
    L4 --> L5["L5 Slate<br/>Runtime and support"]
    L2 -. "Human graph context" .-> L3["L3 Orange<br/>Cards"]
    L3 -.-> L4

    classDef L0 fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef L1 fill:#00897B,color:#fff,stroke:#005B52
    classDef L2 fill:#2E7D32,color:#fff,stroke:#1B5E20
    classDef L3 fill:#EF6C00,color:#fff,stroke:#A64700
    classDef L4 fill:#6A1B9A,color:#fff,stroke:#3E0F5C
    classDef L5 fill:#546E7A,color:#fff,stroke:#29434E
    class L0 L0
    class L1 L1
    class L2 L2
    class L3 L3
    class L4 L4
    class L5 L5
```

| Layer | Examples |
|---|---|
| L0 | Human and agent entry notes |
| L1 | Hub, risk, color, combination, and change-control maps |
| L2 | Activation register and family route tables |
| L3 | Human-visible legacy or context cards |
| L4 | Canonical skills, external pointers, and theory phases |
| L5 | Human guide, protocols, runtime, adapters, scripts, tests, and requests |

`registry/interaction.md` is an L2 routing/control node. The visible
[Interaction Protocol hub](../../interaction-protocol/README.md) is L4 violet
and links the skills hub, activation, registry, canonical JSON contract,
runtime, API, migration record, and tests. The JSON and test files remain
attachments rather than extra Markdown graph nodes.

Generic concept links now come from `protocols/repository/CONTRACT.json`.
Therefore a future JSON- or code-backed protocol must declare a visible
Markdown entry and its required links instead of adding a one-off validator.
The graph check also catches ordinary dangling wikilinks after moves and
deletions while allowing only explicitly declared external skill pointers.

Validate both the documented policy and the live Obsidian graph:

```bash
python3 scripts/graph_layers.py --check
```

If the policy is correct but Obsidian groups are stale:

```bash
python3 scripts/graph_layers.py --sync
```

Synchronization replaces only `colorGroups`. Personal settings such as zoom,
orphan visibility, and collapsed panels are preserved. A genuinely new layer or
color requires an explicit protocol amendment.
