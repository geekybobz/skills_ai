# Combo Map

Read only when a task genuinely spans two families or two skills.
Load the smallest useful pair — never the whole chain.

Back: [[00_SKILLS_HUB]] · Risk: [[04_RISK_MAP]] · Layers: [[05_COLOR_LAYERS]]

## Within design

| combo | use when | order |
|---|---|---|
| `poster-lead` + 2-3 specialists | new poster or HTML visual task | [[design-with-claude/poster-lead]] picks them — load only what it names |
| `design-brief` + one specialist | loose requirements need structure first | [[design-with-claude/design-brief]], then the domain skill |
| `dark-mode-specialist` + `color-specialist` | dark theme *and* a full palette | dark sets surface logic, colour builds the scale on top |
| `dashboard-designer` + `spacing-layout-specialist` | dense grid needing exact column maths | grid hierarchy first, then spacing precision |
| `data-visualization-specialist` + `dashboard-designer` | figure-heavy poster or dashboard | chart logic first, then where they land |
| `typography-specialist` + `visual-hierarchy-specialist` | readability *and* attention flow | type scale first, hierarchy weights follow from it |
| `print-export-designer` + `color-specialist` | PDF or print with palette constraints | print rules first, then audit colours for print safety |

## Across families

| combo | use when | order |
|---|---|---|
| [[registry/theory]] + [[registry/design]] | theory content becomes an academic poster | theory gives structure, `poster-lead` gives layout |
| [[registry/compression]] + any family | terse output wanted during a long session | activate `caveman` first, then route normally |
| `caveman-math` + `theory-reference` | compact explanation while building rigorous notes | use `caveman-math` for answer shape; theory skill controls notation, phases, and files |
| [[registry/ui-patterns]] + [[registry/build-ops]] | auth UX *and* auth code | `auth-security-ux-specialist` for the flow, `auth-implementation` for the code |
| `cavecrew` + investigation work | delegating to save main context | `cavecrew` decides, then the subagent pattern it names |

## Rule

Two skills is a combo. Four is a preload. If the pair does not appear above, pick
the single closest skill and say what you left out.
