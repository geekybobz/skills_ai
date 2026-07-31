# UI Patterns Registry

Interface components, UX states, reach, and product verticals.

- Layout, colour, type, figures, print → [[registry/design]]
- Setup, database, deploy, debug → [[registry/build-ops]]

## Skills

### Components and interaction

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/interaction-designer]] | user flows, states, gestures, feedback, keyboard patterns | interaction, flow, state, feedback | pure animation timing → `motion-designer` |
| [[design-with-claude/form-designer]] | form layout, validation timing, input types, multi-step | form, input, validation | the copy inside it → `content-strategist` |
| [[design-with-claude/navigation-specialist]] | sidebar, top bar, tabs, breadcrumbs, mega menus, command palette | navigation, sidebar, breadcrumbs, menu | site taxonomy → `information-architect` |
| [[design-with-claude/drag-drop-specialist]] | drag affordances, drop zones, reordering, canvas, multi-select | drag, drop, reorder, canvas | generic click interactions → `interaction-designer` |
| [[design-with-claude/search-specialist]] | search UX, autocomplete, faceted filtering, zero-results | search, autocomplete, filter, facets | table filtering → `table-designer` |

### States and moments

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/error-handling-specialist]] | error messages, validation, recovery flows, retry, HTTP pages | error state, validation, retry, 404 | debugging a real build error → [[registry/build-ops]] |
| [[design-with-claude/onboarding-specialist]] | first-run, tooltip tours, empty states, checklists, discovery | onboarding, first run, empty state, tour | writing the copy → `content-strategist` |
| [[design-with-claude/performance-specialist]] | skeletons, optimistic updates, loading states, perceived speed | loading, skeleton, spinner, perceived speed | real runtime performance work |
| [[design-with-claude/conversational-ui-designer]] | chat interfaces, bot personality, message design, voice UI | chat, bot, conversational, voice | generic forms → `form-designer` |

### Reach and adaptation

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/accessibility-specialist]] | WCAG, ARIA, keyboard nav, screen readers | a11y, WCAG, ARIA, screen reader, keyboard | colour contrast maths → `color-specialist` |
| [[design-with-claude/mobile-specialist]] | touch targets, thumb zones, bottom nav, gestures, safe areas | mobile, touch, thumb zone, safe area | CSS breakpoints → `responsive-design-specialist` |
| [[design-with-claude/i18n-designer]] | RTL layouts, string expansion, locale-aware UI, date/number formats | i18n, RTL, locale, translation | tone of voice → `content-strategist` |

### Product verticals

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/b2b-saas-specialist]] | enterprise patterns, RBAC UI, multi-tenant, admin dashboards | saas, enterprise, RBAC, multi-tenant, admin | dashboard *layout* → `dashboard-designer` |
| [[design-with-claude/ecommerce-specialist]] | product pages, filtering, galleries, reviews, comparison | ecommerce, product page, catalogue | the checkout itself → `checkout-specialist` |
| [[design-with-claude/checkout-specialist]] | cart UX, payment forms, guest checkout, trust, confirmation | checkout, cart, payment, order | browsing and discovery → `ecommerce-specialist` |
| [[design-with-claude/landing-page-specialist]] | hero sections, CTAs, value props, social proof, pricing tables | landing page, hero, CTA, pricing, conversion | in-app pages → `poster-lead` |
| [[design-with-claude/auth-security-ux-specialist]] | login flows, password UX, 2FA/passkey, sessions, trust signals | auth UX, login flow, password, 2FA, passkey | writing the auth *code* → `auth-implementation` |
| [[design-with-claude/healthcare-ux-specialist]] | clinical workflows, HIPAA UI, patient data display, terminology | healthcare, clinical, patient, HIPAA | generic dashboards → `dashboard-designer` |

## Rules

- Load one or two skills. Never the section, never the family.
- Nothing above fits → say so. Do not substitute the nearest-sounding skill.
- Path: `design-with-claude/<skill>.md`
