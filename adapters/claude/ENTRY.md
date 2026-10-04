---
platform: claude
authority: platform-overlay
related: "[[docs/SHARED_DOCUMENTATION_MODEL]]"
---

## Claude-specific access

- Model-led coordination context and compact metadata are injected by managed `SessionStart` and selective `UserPromptSubmit` hooks. Do not keep
  or preload a duplicate skill catalog, activation table, or skill body in
  persistent instructions.
- Claude owns its hook, installation, managed-memory cleanup, child lifecycle,
  and live Claude acceptance. Do not modify or certify Codex-specific lifecycle
  without an explicit request; report shared-contract incompatibilities instead.
