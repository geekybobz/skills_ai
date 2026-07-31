# Build and Ops Registry

Setup, environment, database, deploy, debugging, code explanation.
These live in `design-with-claude/` for historical reasons — they are **not** design skills.

- Layout, colour, type, print → [[registry/design]]
- Components, states, verticals → [[registry/ui-patterns]]

Audience note: these are written for designers new to development. They explain
concepts before giving steps. Skip them for experienced-developer tasks.

## Skills

| skill | does | trigger | not for |
|---|---|---|---|
| [[design-with-claude/setup-guide]] | install Node and Claude Code, create a first project | install, node, terminal, first project | an existing configured project |
| [[design-with-claude/environment-setup]] | what `.env` files are, how to set them, what never to commit | `.env`, API key, secret, environment variable | production secret management |
| [[design-with-claude/database-setup]] | Supabase tables, queries, connecting to a frontend | database, supabase, table, query | schema design at scale |
| [[design-with-claude/auth-implementation]] | working login/signup with Clerk or Supabase Auth — real code | auth code, implement login, signup, Clerk | login *UX* → `auth-security-ux-specialist` |
| [[design-with-claude/deploy-to-vercel]] | deploy to Vercel, fix build errors, custom domains | deploy, vercel, domain, build failing | other hosts |
| [[design-with-claude/debug-helper]] | paste an error → plain-language cause and one exact fix | error message, stack trace, broken build | designed error *states* → `error-handling-specialist` |
| [[design-with-claude/code-explainer]] | paste a file → plain-language explanation, no jargon | explain this code, what does this do | writing new code |

## Risk

`auth-implementation`, `database-setup`, and `deploy-to-vercel` write code, touch
credentials, or take account actions. Read [[04_RISK_MAP]] before running them.

## Rules

- Load one skill. These are step-by-step guides — two at once conflict.
- Nothing above fits → say so. Do not substitute the nearest-sounding skill.
- Path: `design-with-claude/<skill>.md`
