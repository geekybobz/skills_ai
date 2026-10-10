---
name: skills-ai-registry
description: Model-led skill discovery, selective loading, composition, management and recovery.
---

# Skills AI Shared Runtime Entry

Repository root: `{{SKILLS_AI_ROOT}}`. Resolve tool/instruction paths from this root independently of the task project. No local router selects skills; the host owns semantic decisions.

The installer includes the complete shared core below, bound to source SHA-256 `{{CORE_SHA256}}`. Reuse it while reliably present. After context uncertainty or a known source revision change, obtain the current core through `orchestrator/tools/orchestrate.py context` or read `orchestrator/runtime/skills-orchestrator/SKILL.md`. `install_runtime_adapter.py --adapter codex --check` detects a stale installed copy during maintenance; there is no background update check.

Use discovery only when delivered metadata is missing or insufficient, and load detailed modules only when required. Selection never grants authority. Outside the maintenance repository retain its request-only change boundary.
