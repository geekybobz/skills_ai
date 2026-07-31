# Color Layers

One colour per **layer**, never per skill. Colour encodes depth in the routing
graph, not topic. This is what keeps the graph readable as skills are added.

Back: [[00_SKILLS_HUB]] · Combos: [[03_COMBO_MAP]] · Risk: [[04_RISK_MAP]]

## Layer palette

| layer | role | colour | graph query |
|---|---|---|---|
| L0 | Entry notes | `#5B5BD6` indigo | `path:README.md OR path:AGENTS.md OR path:CLAUDE.md OR path:docs/SKILLS.md` |
| L1 | Global maps | `#00897B` teal | `path:docs/00_SKILLS_HUB.md OR path:docs/03_COMBO_MAP.md OR path:docs/04_RISK_MAP.md OR path:docs/05_COLOR_LAYERS.md OR path:docs/06_CHANGE_CONTROL.md` |
| L2 | Registry routes and activation | `#2E7D32` green | `path:registry/` |
| L3 | Skill cards and parked legacy cards | `#EF6C00` orange | `path:cards/` |
| L4 | Canonical skills, interaction protocols, external skill pointers, and phases | `#6A1B9A` violet | `path:design-with-claude/ OR path:interaction-protocol/ OR path:theory-reference/SKILL.md OR path:theory-reference/shared/SKILL.md OR path:theory-reference/shared/phases/ OR path:external-skills/` |
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

  A["L0 Entry"] --> B["L1 Global maps"] --> C["L2 Activation and Registry"] --> E["L4 Skill or phase"] --> F["L5 Support"]
  C -.-> D["L3 Cards (reserved)"] -.-> E

  class A L0
  class B L1
  class C L2
  class D L3
  class E L4
  class F L5
```

**Solid arrows are the agent's read path**: L0 -> L1 -> L2 activation -> one L2
family registry -> L4. L3 is dotted because it is a human/graph layer: it
enriches the graph but is never on the agent's critical path.

## L3 Cards

`cards/` holds graph cards with frontmatter tags, aliases, and wikilinks to
related skills, but no copied skill content. It is what turns the graph from a
star into a network: `tag:`, backlinks, and the properties pane have something
to index.

Use L3 cards for parked or legacy skills that should be visible in Obsidian
while their activation routes remain `off`. These cards are not on the agent's
critical routing path.

## Rule

Assign new files to a layer by **path and role**, reusing the existing colour.
Do not create a colour per skill, per family, or per topic.

Colour groups are ordered from specific layers to L5 support fallbacks. The
first matching group is the file's layer. `docs/06_CHANGE_CONTROL.md` is an L1
global map; operation cards under `protocols/repository/` and build/release
guidance are L5 support. The derivative human guide under `docs/human/` is also
L5 support and is not part of the agent routing path.

## Governance enforcement

Every new or moved Markdown file must record its intended `graph_layer` in the
change packet and be covered by one canonical query above. Run:

```bash
python3 scripts/graph_layers.py --check
```

When the policy is correct but the live Obsidian groups are stale, use
`python3 scripts/graph_layers.py --sync`. Synchronization replaces only
`colorGroups`; it preserves personal graph settings such as zoom, visibility,
and collapsed panels. A new colour or layer requires an explicit protocol
amendment.

## Adding a new family

1. Add one file to `registry/` — it inherits **L2 green** automatically via `path:registry/`.
2. Add rows to [[registry/activation]] and the route table in [[00_SKILLS_HUB]].
3. Skill files and external skill pointers sit in **L4**; templates, scripts and tests in **L5**.
4. Add risk rows to [[04_RISK_MAP]] if the family writes anything.
5. Run `python3 scripts/graph_layers.py --check`.
6. Reuse the layer colour. A new colour is only justified if the *layer model itself* changes.

A family large enough to need internal sub-routing gets sections inside its single
L2 file — not a second hop. The two-read budget is the point of the design.
