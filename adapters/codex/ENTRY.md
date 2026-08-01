---
platform: codex
authority: platform-overlay
related: "[[docs/SHARED_DOCUMENTATION_MODEL]]"
---

## Codex-specific access

- Send one newline-terminated JSON request to `scripts/route_skill.py`; it must
  exit after one response without waiting for EOF.
- Codex owns Codex-specific invocation and session cleanup. Claude-specific live
  acceptance belongs to Claude; shared runtime behavior belongs in `runtime/`.
