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
2. Apply the returned interaction context. `REGISTRY_STATUS` → answer from live
   metadata without remembered names or skill bodies. `MATCH` → load only its
   task-skill path. `NORMAL` or error → continue. For
   `AMBIGUOUS_SKILL_MATCH`, ask the one short numbered choice returned in
   `routing.clarification`; load neither candidate until the user chooses.
3. Never load an `off`, `hidden`, or `deprecated` route. A `manual` route needs
   an explicit matching request.
4. Respect current-request `/skill`, `/interaction`, `/format`, `/depth`, and
   `/receipt` controls before any session or automatic default. `routing.fit`
   measures route fit from 0 to 3, not answer correctness. When receipt mode is
   `auto`, show a compact receipt only for a match, ambiguity, explicit
   override, project inspection, or requested access boundary.
5. Read `docs/00_SKILLS_HUB.md`, `registry/activation.md`, and the relevant
   registry only for registry maintenance, audits, or when the runtime reports
   a broken or stale manifest.
6. Skill selection grants no authority. Apply project risk and permission rules
   before writes, scripts, credentials, or external actions.
7. Outside this workspace, never edit this repository: an explicit change may
   only create one packet with `scripts/create_change_request.py`, then hand off
   to a maintenance task rooted here.
8. Treat the router as a bounded one-shot command. If its session remains active
   past the host deadline, terminate and reap that exact session, then continue
   the original task normally. Do not remember a static skill catalog or skill
   body as a substitute for routing.
