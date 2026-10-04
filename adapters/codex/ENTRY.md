---
platform: codex
authority: platform-overlay
related: "[[docs/SHARED_DOCUMENTATION_MODEL]]"
---

## Codex-specific access

- The installed entry includes the shared core and its source identity. Load it once while retained; use current source instructions on recovery or known revision changes. Codex owns installation checks; no hook or background refresh is assumed.
- Codex owns Codex-specific invocation and session cleanup. Claude-specific live
  acceptance belongs to Claude; shared runtime behavior belongs in `runtime/`.
