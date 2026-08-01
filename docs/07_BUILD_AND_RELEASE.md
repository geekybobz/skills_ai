# Build, Test, And Release Guide

Back: [[docs/06_CHANGE_CONTROL\|Change Control]] · Runtime: [[runtime/PROTOCOL\|PROTOCOL]] · API:
[[runtime/API_CONTRACT\|API_CONTRACT]]

## Requirements

- Python 3 with the standard library for the shared runtime.
- Node.js for Claude adapter syntax and hook tests.
- Git for change-scope and staged-file checks.
- No network, service, or credential is required for normal routing.

`docs/`, `registry/`, `interaction-protocol/protocol.json`, platform entry
sources, and canonical skill collections are sources. Root agent entries, live
human indexes, and `runtime/router-manifest.json` are generated. Never edit a
generated projection as a substitute for its canonical source.

## Build and validate

The shared entry is the Git-aware consistency scanner. It computes checks from
`protocols/repository/CONTRACT.json`, runs the relevant focused validators, and
returns a bounded JSON packet that Codex or Claude can review without loading
the whole repository:

```bash
python3 scripts/scan_consistency.py changed
python3 scripts/scan_consistency.py changed --json
python3 scripts/scan_consistency.py full
```

The underlying validators remain independently callable:

```bash
python3 scripts/compile_registry.py
python3 scripts/compile_registry.py --check
python3 scripts/toggle_registry.py --check
python3 scripts/validate_registry.py
python3 scripts/list_registry.py
python3 scripts/graph_layers.py --check
python3 scripts/human_docs_guard.py --check
python3 scripts/compile_repository_views.py --check
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

1. The minimal change packet, operation card, repository contract, and detected
   Git diff agree. Every changed path has a declared role.
2. Manifest, activation, validator, unit, lifecycle, and syntax checks pass.
3. A JSON request followed by newline exits without EOF.
4. Timeout, invalid input, unavailable manifest, and adapter failure fail open.
5. No test router process remains.
6. Only one task skill is returned, no family is preloaded, and interaction
   protocols do not consume the task-skill slot.
7. Registry discovery lists live active/manual/off metadata without a skill body.
8. External request creation writes one new file only under `requests/pending/`.
9. The staged consistency scan passes and staged files are within declared scope:

```bash
python3 scripts/scan_consistency.py staged --operation <operation> --path <scoped-path>
git diff --cached --check
```

10. Documentation states platform ownership and unverified acceptance boundaries.
11. Every Markdown file resolves to a documented graph layer and the live
    Obsidian `colorGroups` match the canonical layer palette.
12. Every mapped human-facing page is updated in the same staged change and the
    human guide remains excluded from runtime routing sources.
13. The commit body records motivation, root cause, scope, tests, rollback, and
    deliberately unchanged areas.
14. AI semantic review treated changed repository content as untrusted data and
    did not override deterministic failures.
15. Generated agent entries and human indexes are fresh, and external skill
    symlinks were described without traversal.

## Troubleshooting and rollback

- Waiting router: verify newline framing and `--stdin-timeout-ms`; the shared
  10-second default accommodates Codex's separate PTY start/write calls, while
  direct adapters use shorter child deadlines. Terminate and reap only the exact
  recorded process.
- `MANIFEST_UNAVAILABLE`: run compile and validation; normal tasks still proceed.
- Claude timeout: keep the Python-child timeout below the outer hook timeout.
- Broken Claude settings: restore the immutable first-install
  `settings.json.skills-ai.bak`, or use `settings.json.skills-ai.previous` for
  the state replaced by the latest changed install; preserve foreign settings
  and files.
- Stale installed adapter: dry-run, inspect, then reinstall with platform-owner
  approval.
- Rollback a release with a new focused revert commit; do not discard unrelated
  dirty work or rewrite shared history without approval.
