# Design Registry

Visual design: layout, spacing, colour, type, hierarchy, figures, print.

- UI components, states, product verticals → [[registry/ui-patterns]]
- Setup, database, deploy, debug → [[registry/build-ops]]

**New poster, HTML page, or unclear visual task → [[design-with-claude/poster-lead]] first.**
It proposes layouts and names 2-3 specialists; load only those. Loose requirements
with no structure yet → `design-brief`. Narrow question → go straight to the tables.

## Skills

### Lead and planning

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/poster-lead]] | adaptive design lead; proposes 2-3 layouts with rationale, routes onward | poster, A0, HTML page, any new visual task | a single narrow question |
| [[design-with-claude/design-brief]] | turns loose requirements into a structured brief | brief, plan, requirements unclear | an ask that is already specific |
| [[design-with-claude/design-system-architect]] | tokens, component APIs, variants, theming, governance | design system, tokens, variants | one-off page → `poster-lead` |
| [[design-with-claude/content-strategist]] | microcopy, empty states, tone of voice, content hierarchy | copy, wording, tone, empty state | error *flows* → `error-handling-specialist` |

### Layout and structure

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/dashboard-designer]] | KPI cards, data density, dense grids, filters, drill-down | dashboard, KPI, stat cards, dense grid | one chart → `data-visualization-specialist` |
| [[design-with-claude/spacing-layout-specialist]] | grid systems, spacing scales, density modes, column math | spacing, gap, padding, column math | overall section order → `information-architect` |
| [[design-with-claude/information-architect]] | taxonomy, labelling, content organisation, reading order | structure, hierarchy, flow, section order | nav *components* → `navigation-specialist` |
| [[design-with-claude/visual-hierarchy-specialist]] | size, weight and contrast to direct the eye | emphasis, focal point, visual weight | the type scale itself → `typography-specialist` |
| [[design-with-claude/responsive-design-specialist]] | breakpoints, fluid type, container queries, responsive images | responsive, breakpoint, fluid layout | touch targets, thumb zones → `mobile-specialist` |

### Visual style

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/color-specialist]] | palettes, contrast ratios, semantic tokens, OKLCH scales | colour, palette, contrast, hue | dark theme only → `dark-mode-specialist` |
| [[design-with-claude/dark-mode-specialist]] | dark surfaces, elevation, colour remapping, FOUC, mode switch | dark mode, night theme, theme switch | building a full light palette → `color-specialist` |
| [[design-with-claude/typography-specialist]] | type scales, font pairing, line height, vertical rhythm | font, readability, type scale | A0 poster sizing → `poster-lead` |
| [[design-with-claude/brand-designer]] | visual identity, logo usage, brand colour and type expression | brand, identity, logo | a generic palette → `color-specialist` |
| [[design-with-claude/motion-designer]] | transitions, easing, micro-interactions, reduced motion | animation, transition, motion | perceived speed → `performance-specialist` |

### Data and figures

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/data-visualization-specialist]] | chart selection, axes, colour encoding, tooltips | chart, graph, plot, figure | the grid they sit in → `dashboard-designer` |
| [[design-with-claude/table-designer]] | data tables, sorting, pagination, row selection, inline edit | table, comparison grid, data grid | static comparison layout → `dashboard-designer` |

### Print and export

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/print-export-designer]] | print CSS, PDF-safe colour, A0/A4 page sizing, receipts | print, PDF, export, A0 | screen-only work |

## Pairs

`dark-mode` + `color` · `dashboard` + `spacing-layout` · `typography` + `visual-hierarchy` · `data-visualization` + `dashboard` · `print-export` + `color` — see [[03_COMBO_MAP]].

## Rules

- Load one or two skills. Never the section, never the family.
- Nothing above fits → say so. Do not substitute the nearest-sounding skill.
- Path: `design-with-claude/<skill>.md`
