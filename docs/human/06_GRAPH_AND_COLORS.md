---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Graph and Colors

Back: [speed and troubleshooting](05_SPEED_AND_TROUBLESHOOTING.md). Next:
[maintaining skills](07_MAINTAINING_SKILLS.md).

Color describes architectural role, not topic. Entry notes, hubs, registries,
skills and supporting files have distinct layers. Public packages do not receive
individual colors, and graph-node counts are never skill counts.

The overview shows one named orchestrator node and one named node per public
skill. Technical entries such as `SKILL.md` remain accessible through those nodes.
Repository context lookup uses bounded native file search. Local repair copies,
rollback archives and personal course notes are outside the public inventory and
generated repository index.

```mermaid
flowchart LR
    L0["L0 Indigo<br/>Entry documents"] --> L1["L1 Teal<br/>Hubs, switchboards, orchestrator"]
    L1 --> L2["L2 Green<br/>Family registries"]
    L2 --> L4["L4 Violet<br/>Skills, capabilities, phases"]
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
| L1 | Skills Orchestrator, Skills Hub, Activation, protocol/documentation hubs, risk, color, combination, and change-control maps |
| L2 | Family route tables for interaction, theory, research, optimizer, and the disabled career workflow |
| L3 | Human-visible context cards |
| L4 | Generated public skill entries, internal capabilities, external pointers, and phases |
| L5 | Human guide, protocols, runtime, adapters, scripts, tests, and requests |

A `skill-plans/*/plan.md` document is not a package or capability. The plan
path itself is excluded from graph nodes and skill counts.

The manual `optimizer/` package is an L4 violet collection like other public
package entries. Its named generated graph node,
[`Optimizer`](../../graph/skills/optimizer.md), is visible in inventory, while
the technical package path stays hidden in the default overview. Use Obsidian's
Quick Switcher to open `Optimizer`, or filter the graph with
`path:graph/skills/optimizer.md`, when inspecting that workflow alone.

The `research-context-scout/` package is a normal repository-owned L4
skill collection. Its human README, root entry, shared phases and platform
wrappers stay linked as one package.

`registry/interaction.md` is an L2 green family registry. The visible
[Interaction Protocol hub](../../interaction-protocol/README.md) is L1 teal and
links the skills hub, activation, registry, canonical JSON contract, runtime,
API and tests. The Shared Documentation Model is also an L1
hub. JSON and test files remain slate support rather than extra hubs.

Graph validation reports file nodes by architectural layer. A skill may own
many violet capability or phase files, so the violet count must never be quoted
as the number of skills. Public skill count comes only from Activation's package table.

## Default overview

The global graph starts with low-level maintenance and technical package paths
hidden. This leaves the named orchestrator, public skill nodes, hubs, and
registries visible. Open a green registry's Local Graph or clear the search
filter when you need capability files, wrappers, runtime, tests, or support.

The overview filter deliberately excludes `optimizer/` but not `graph/skills/`:
the public `Optimizer` node remains visible even though its technical
`SKILL.md` entry does not. If a temporary graph search makes a node appear
missing, clear that search before treating it as a graph-structure problem.

The filter does not delete or unlink anything. Zoom, force settings, orphan
visibility, and collapsed panels remain personal view state, and color-group
synchronization preserves them.

Generic concept links come from `protocols/repository/CONTRACT.json`.
Therefore a future JSON- or code-backed protocol must declare a visible
Markdown entry and its required links. The same contract requires that entry to
be L1 teal instead of adding a one-off validator.
The graph check also catches ordinary dangling wikilinks after moves and
deletions while allowing only explicitly declared external skill pointers.
It also rejects a missing or default-hidden inventory node, a generic inventory
filename, duplicate inventory filenames, label/id mismatch, incorrect layer, or
missing Activation/orchestrator link.

The shared documentation model is another declared graph concept. Its L1
architecture record links the change-control authority, repository atlas, skill
anatomy chapter, common agent-entry source, and platform overlays. Generated
live indexes remain human L5 support and do not become routing nodes.

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

For the complete architecture, controls and working examples, see [the walkthrough](10_MODEL_LED_ORCHESTRATOR.md).

## Working with contained changes

Repair is an orchestrator working mode, not another skill or graph layer. Its `.runtime/repair/` copies and evidence stay outside the generated graph and inventory. See [Safe changes](04_SAFE_CHANGES.md).

## Current context flow

Capability integration contracts add metadata and preserve existing package counts, graph ownership and colors. Efficient delivery does not change graph nodes into additional skills. See [the walkthrough](10_MODEL_LED_ORCHESTRATOR.md) for working examples.
