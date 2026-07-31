# Build, Test, And Release Guide

Back: [[06_CHANGE_CONTROL]] · Runtime: [[runtime/PROTOCOL\|PROTOCOL]] · API:
[[runtime/API_CONTRACT\|API_CONTRACT]]

## Requirements

- Python 3 with the standard library for the shared runtime.
- Node.js for Claude adapter syntax and hook tests.
- Git for change-scope and staged-file checks.
- No network, service, or credential is required for normal routing.

`docs/`, `registry/`, `runtime/profile.json`, and canonical skill collections
are sources. `runtime/router-manifest.json` is generated. Never edit generated
skill mirrors as a substitute for their canonical source.

## Build and validate

```bash
python3 scripts/compile_registry.py
python3 scripts/compile_registry.py --check
python3 scripts/toggle_registry.py --check
python3 scripts/validate_registry.py
```

## Test and benchmark

```bash
python3 -m unittest discover -s tests
node --check adapters/claude/skills-ai-router.js
python3 scripts/benchmark_router.py --json
```

Benchmark reports separate core and process/API latency. Do not describe the
core decision measurement as end-to-end performance.

## Adapter acceptance

Always use temporary configuration roots first:

```bash
python3 scripts/install_runtime_adapter.py --adapter codex --config-dir /tmp/codex-skills-test --dry-run
python3 scripts/install_runtime_adapter.py --adapter claude --config-dir /tmp/claude-skills-test --dry-run
```

After a temporary install, run `--check`. A live install is an external write
and follows [[protocols/repository/INSTALL_UNINSTALL]]. Codex owns live Codex
acceptance; Claude owns live Claude acceptance.

## Release gate

1. The change packet and operation card match the actual diff.
2. Manifest, activation, validator, unit, lifecycle, and syntax checks pass.
3. A JSON request followed by newline exits without EOF.
4. Timeout, invalid input, unavailable manifest, and adapter failure fail open.
5. No test router process remains.
6. Only one skill is returned and no family is preloaded.
7. Staged files are within declared scope:

```bash
python3 scripts/change_guard.py check-staged --operation update --path <scoped-path>
git diff --cached --check
```

8. Documentation states platform ownership and unverified acceptance boundaries.
9. The commit body records motivation, root cause, scope, tests, rollback, and
   deliberately unchanged areas.

## Troubleshooting and rollback

- Waiting router: verify newline framing and `--stdin-timeout-ms`; the shared
  10-second default accommodates Codex's separate PTY start/write calls, while
  direct adapters use shorter child deadlines. Terminate and reap only the exact
  recorded process.
- `MANIFEST_UNAVAILABLE`: run compile and validation; normal tasks still proceed.
- Claude timeout: keep the Python-child timeout below the outer hook timeout.
- Broken Claude settings: restore `settings.json.skills-ai.bak`; preserve foreign
  settings and files.
- Stale installed adapter: dry-run, inspect, then reinstall with platform-owner
  approval.
- Rollback a release with a new focused revert commit; do not discard unrelated
  dirty work or rewrite shared history without approval.
