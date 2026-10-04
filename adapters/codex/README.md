# Codex Adapter

Codex loads one installed entry containing the shared coordination core, source identity and checkout binding. The host selects capabilities using bounded discovery and exact access tools. No local router selects a task body.

The repository-level `AGENTS.md` is generated from
`runtime/AGENT_ENTRY_SHARED.md` plus `adapters/codex/ENTRY.md`. Edit those
canonical sources and run `scripts/compile_repository_views.py`; do not maintain
a second copy of the shared rules here or in Codex memory.

Install or verify:

```bash
python3 scripts/install_runtime_adapter.py --adapter codex --dry-run
python3 scripts/install_runtime_adapter.py --adapter codex
python3 scripts/install_runtime_adapter.py --adapter codex --check
```

The default target is `~/.codex/skills/skills-ai-registry/SKILL.md`. Use
`--config-dir` for an alternate Codex configuration directory.

The entry does not retain a catalog or preload package bodies. Metadata pages are expanded only when necessary. A supplied project root allows only exact validated capsule inspection. Tasks started outside the maintenance repository preserve its request-only change boundary. Semantic live acceptance and end-to-end verification are recorded separately in the build record.

The installer renders the shared header and core together. Reinstallation updates the source identity; `--check` compares the complete rendered copy. Runtime and generated repository entries point to this canonical core instead of repeating its controls.
