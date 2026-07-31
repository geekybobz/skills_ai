---
name: skills-ai-registry
description: Route user-owned local skills through the fast Skills AI runtime. Use when a task may benefit from a skill in /Users/billabobz/skills_ai.
---

# Skills AI Shared Runtime Entry

1. Send the current request to the shared platform-neutral router at
   `/Users/billabobz/skills_ai/scripts/route_skill.py` as one newline-terminated
   JSON object: `{"protocol":"skills-ai/1","client":"codex","query":"..."}\n`.
   The router returns after one line without requiring EOF. Do not preload the
   Markdown hub or activation register.
2. `MATCH`: load only the returned skill path, then perform the task.
3. `NORMAL`: perform the task normally without a local skill.
   Invalid input, router error, or timeout also continues normally.
4. Never load an `off`, `hidden`, or `deprecated` route. A `manual` route needs
   an explicit matching request.
5. Read `docs/00_SKILLS_HUB.md`, `registry/activation.md`, and the relevant
   registry only for registry maintenance, audits, or when the runtime reports
   a broken or stale manifest.
6. Before writes, scripts, credentials, or external actions, apply the normal
   project risk and permission rules. Skill selection never grants authority.
7. Treat the router as a bounded one-shot command. If its session remains active
   past the host deadline, terminate and reap that exact session, then continue
   the original task normally. Do not remember a static skill catalog or skill
   body as a substitute for routing.
