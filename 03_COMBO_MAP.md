# Combo Map

Use when a task naturally needs more than one skill. Load the smallest useful
pair, not every related skill.

## Navigation

- Back: [[00_SKILLS_HUB]]
- Triggers: [[01_TRIGGER_MAP]]
- Load order: [[02_LOAD_ORDER]]
- Risk: [[04_RISK_MAP]]
- Family hubs: [[design-with-claude/DESIGN_HUB]], [[caveman/CAVEMAN_HUB]], [[theory-reference/THEORY_HUB]]

## Common Combos

| combo | use when | load order |
|---|---|---|
| `poster-lead` + specialist pair | new poster or HTML visual task | [[design-with-claude/poster-lead]] first, then selected specialists |
| `design-brief` + design specialist | loose requirements need structure | [[design-with-claude/design-brief]], then domain skill |
| `dark-mode-specialist` + `color-specialist` | dark theme plus palette | dark mode logic, then color tokens |
| `dashboard-designer` + `spacing-layout-specialist` | dense grid, exact layout math | grid hierarchy, then spacing precision |
| `data-visualization-specialist` + `dashboard-designer` | figure-heavy dashboard or poster | chart logic, then layout placement |
| `typography-specialist` + `visual-hierarchy-specialist` | readability plus attention flow | type scale, then hierarchy |
| `print-export-designer` + `color-specialist` | PDF or print export with palette constraints | print rules, then color safety |
| `theory-reference` + `dashboard-designer` | academic theory content becomes poster | theory structure, then visual layout |
| `caveman` + any family | user wants terse output during long session | activate response mode, then normal route |
| `cavecrew` + code investigation | user asks to delegate or save context | cavecrew router, then selected subagent pattern |

