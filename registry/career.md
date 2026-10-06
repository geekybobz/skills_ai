# Career Registry

Career and job-search workflows. This family is parked in
[[registry/activation]] for now, so the capability below stays a plain path
until the family is reworked and activated.

Graph card: [[cards/parked/quantum-job-collector|quantum-job-collector parked card]].

## Package Capability

| route | use | triggers | not for | risk |
|---|---|---|---|---|
| `external-skills/quantum-job-collector/SKILL.md` | exhaustive quantum job collection for Quantum Career Radar | quantum jobs, career radar, update review queue, pending jobs, source coverage | generic career advice, resume writing, one-off job browsing, paid/browser fallback unless enabled | network search, app/data writes, pending queue append |

## Components To Rework

| component | state now | purpose |
|---|---|---|
| `quantum-job-collector.full-run` | off | exhaustive all-tier run |
| `quantum-job-collector.tier1-structured` | off | Greenhouse, Lever, Teamtailor structured pass |
| `quantum-job-collector.unresolved-retry` | off | retry only unresolved sources |
| `quantum-job-collector.source-evidence` | off | persist source result records and evidence |
| `quantum-job-collector.append-pending` | off | append passing jobs to pending queue |
| `quantum-job-collector.browser-fallback` | off | use browser or JS fallback |
| `quantum-job-collector.paid-fallback` | off | paid or remote fallback tools |
| `quantum-job-collector.cron` | off | scheduled automation |

## Rework Notes

- Prefer deterministic platform adapters before browser fallback.
- Require `scripts/source_state.py` for source coverage and unresolved-source
  records.
- Require `scripts/save_run_summary.py` after a completed run.
- Keep `append_pending.py` as the only pending-queue writer.
- Keep paid/browser-heavy fallback disabled unless explicitly turned on.
