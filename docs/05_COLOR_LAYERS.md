# Color Layers

Draft ideas at `skill-plans/*/plan.md` are intentionally outside the graph.
They acquire a graph layer only if promoted into a canonical skill or document.

One colour per **architectural role**, never per individual skill. Colour
shows whether a node is an entry, hub, registry, parked card, package entry,
capability, phase, or support file. File-node counts are never skill counts.
The Skills Orchestrator has one generated L1 node; each public skill has one
uniquely named generated L4 node. Mandatory `SKILL.md`, `README.md`, and platform
wrapper files remain technical nodes rather than public inventory labels.

Back: [[00_SKILLS_HUB]] · Combos: [[03_COMBO_MAP]] · Risk: [[04_RISK_MAP]]

## Layer palette

| layer | role | colour | graph query |
|---|---|---|---|
| L0 | Entry notes | `#5B5BD6` indigo | `path:README.md OR path:AGENTS.md OR path:CLAUDE.md OR path:docs/SKILLS.md` |
| L1 | Hubs, switchboards, orchestrator, and declared graph entries | `#00897B` teal | `path:docs/00_SKILLS_HUB.md OR path:registry/activation.md OR path:graph/orchestration/skills-orchestrator.md OR path:interaction-protocol/README.md OR path:docs/SHARED_DOCUMENTATION_MODEL.md OR path:docs/03_COMBO_MAP.md OR path:docs/04_RISK_MAP.md OR path:docs/05_COLOR_LAYERS.md OR path:docs/06_CHANGE_CONTROL.md` |
| L2 | Family registries | `#2E7D32` green | `path:registry/` |
| L3 | Context cards and parked-package cards | `#EF6C00` orange | `path:cards/` |
| L4 | Public skill entries, internal capability instructions, external pointers, and phases | `#6A1B9A` violet | `path:markdown-protocol/ OR path:optimizer/ OR path:project-manager/ OR path:theory-reference/SKILL.md OR path:graph/skills/ OR path:theory-reference/shared/SKILL.md OR path:theory-reference/shared/phases/ OR path:external-skills/ OR path:research-context-scout/` |
| L5 | Governance cards, runtime, adapters, scripts, tests, templates, requests, and support notes | `#546E7A` slate | `path:docs/ OR path:protocols/ OR path:runtime/ OR path:adapters/ OR path:scripts/ OR path:tests/ OR path:requests/ OR path:theory-reference/` |

## Reading the graph

```mermaid
flowchart LR
  classDef L0 fill:#5B5BD6,color:#fff,stroke:#32327A
  classDef L1 fill:#00897B,color:#fff,stroke:#005B52
  classDef L2 fill:#2E7D32,color:#fff,stroke:#1B5E20
  classDef L3 fill:#EF6C00,color:#fff,stroke:#A64700
  classDef L4 fill:#6A1B9A,color:#fff,stroke:#3E0F5C
  classDef L5 fill:#546E7A,color:#fff,stroke:#29434E

  A["L0 Entry"] --> B["L1 Hub, switchboard, or orchestrator"] --> C["L2 Family registry"] --> E["L4 Skill, capability, or phase"] --> F["L5 Support"]
  C -.-> D["L3 Cards (reserved)"] -.-> E

  class A L0
  class B L1
  class C L2
  class D L3
  class E L4
  class F L5
```

**Solid arrows are the routing read path**: L0 -> an L1 hub -> the L1 activation
switchboard -> one L2 family registry -> L4. L3 is dotted because it is graph context: it
enriches the graph but is never on the critical routing path.

## L3 Cards

`cards/` holds graph cards with frontmatter tags, aliases, and wikilinks to
related packages or capabilities, but no copied instruction content. It is what turns the graph from a
star into a network: `tag:`, backlinks, and the properties pane have something
to index.

Use L3 cards for parked skills that should be visible in Obsidian
while their activation routes remain `off`. These cards are not on the agent's
critical routing path.

## Rule

Assign new files to a layer by **path and role**, reusing the existing colour.
Do not create a colour per skill, per family, or per topic. A hub must never use
the skill colour merely because its directory also contains a protocol.

Colour groups are ordered from specific layers to L5 support fallbacks. The
first matching group is the file's layer. Exact L1 hub and switchboard paths
therefore appear before the `registry/` and support fallbacks. Activation, the
Skills Orchestrator, and every declared graph-concept entry are L1 teal; family
registry files are L2 green; public skill entries, capability instructions, and
phases are L4 violet. Operation cards
and build/release guidance remain L5 support.

## Default overview

The global graph opens with low-level maintenance paths filtered out:

```text
-path:protocols/repository/ -path:runtime/ -path:adapters/ -path:scripts/ -path:tests/ -path:requests/ -path:interaction-protocol/ -path:markdown-protocol/ -path:optimizer/ -path:project-manager/ -path:research-context-scout/ -path:theory-reference/ -path:external-skills/
```

This changes only the default view. Generated `graph/` nodes keep the
orchestrator and public skills visible with descriptive names. Open a green
registry's Local Graph or clear the filter to inspect technical capability and
wrapper files.
Zoom, orphan visibility, force settings, and other personal preferences remain
user-owned.

## Governance enforcement

Every new or moved Markdown file must record its intended `graph_layer` in the
change packet and be covered by one canonical query above. Run:

```bash
python3 scripts/graph_layers.py --check
```

Visible concept relationships are declared in
`protocols/repository/CONTRACT.json`. The graph validator reads those generic
contracts and their `graph_role_policy`. Every declared graph-concept entry must
resolve to L1, and sentinel paths prove the switchboard, registry, card, skill,
and support roles. A user-visible canonical concept backed only by JSON or code
still needs one Markdown entry node and declared links. The same check rejects
dangling repository wikilinks after a move or deletion.

Inventory validation also requires one unique, descriptive, default-visible
graph node for the orchestrator and every public skill. Generic entry filenames
such as `SKILL.md`, `README.md`, `CLAUDE.md`, `CODEX.md`, and `ENTRY.md` cannot
serve as inventory nodes, although those mandatory technical files remain valid.

When the policy is correct but the live Obsidian groups are stale, use
`python3 scripts/graph_layers.py --sync`. Synchronization replaces only
`colorGroups`; it preserves personal graph settings such as zoom, visibility,
and collapsed panels. A new colour or layer requires an explicit protocol
amendment.

## Adding a new family

1. Add one file to `registry/` — it inherits **L2 green** automatically via `path:registry/`.
2. Add rows to [[registry/activation]], `DOCUMENTATION.json`, and the route table in [[00_SKILLS_HUB]].
3. Package entries, capability files, phases, and external pointers sit in **L4**; templates, scripts and tests in **L5**.
4. Add risk rows to [[04_RISK_MAP]] if the family writes anything.
5. Regenerate repository views, which creates the named graph node, then run `python3 scripts/graph_layers.py --check`.
6. Reuse the layer colour. A new colour is only justified if the *layer model itself* changes.

A family large enough to need internal sub-routing gets sections inside its single
L2 file — not a second hop. The two-read budget is the point of the design.

## Details

Colour describes architectural role, not topic, and public packages do not receive
individual colours. Graph nodes describe current sources; archived copies and Git history
do not add inventory entries or skill counts. The overview shows one named orchestrator
node and one named node per public skill, and technical entries such as `SKILL.md`
remain reachable through those nodes. Local repair copies, rollback archives and
personal course notes are outside the public inventory and the generated file index.

Graph validation reports file nodes by architectural layer. A skill may own many violet
capability or phase files, so the violet count must never be quoted as the number of
skills: the public skill count comes only from Activation's package table. A
`skill-plans/*/plan.md` document is not a package or capability, and the plan path is
excluded from graph nodes and skill counts.

The manual `optimizer/` package is an L4 violet collection like other public package
entries. Its generated node, `graph/skills/optimizer.md`, stays visible in the overview
even though the technical package path is filtered out; use Obsidian's Quick Switcher to
open `Optimizer`, or filter with `path:graph/skills/optimizer.md`, to inspect that
workflow alone. `project-manager/`, `research-context-scout/`, and
`markdown-protocol/` are likewise normal
L4 collections whose README, root entry, shared phases, wrappers and small formatting
examples stay linked as one package. `registry/interaction.md` is an L2 green family
registry; the visible [[interaction-protocol/README|Interaction Protocol hub]] is L1 teal
and links the skills hub, activation, registry, canonical JSON contract, runtime, API and
tests, and the [[docs/SHARED_DOCUMENTATION_MODEL|Shared Documentation Model]] is also an
L1 hub. JSON and test files remain slate support rather than extra hubs.

If a temporary graph search makes a node appear missing, clear that search before
treating it as a graph-structure problem. The filter deletes and unlinks nothing; zoom,
force settings, orphan visibility and collapsed panels remain personal view state, and
colour-group synchronization preserves them.
