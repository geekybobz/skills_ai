---
title: Quantum Job Collector
skill_id: quantum-job-collector
family: career
state: off
kind: legacy-skill-card
tags:
  - skill-card
  - legacy-skill
  - parked
---

# Quantum Job Collector

State: `off` in [[registry/activation|activation register]].
Family: [[registry/career|career]].
Source: [[external-skills/quantum-job-collector/SKILL|legacy skill source]].

This card exists so the legacy skill stays visible in the Obsidian graph while
Codex routing remains disabled. It is not routing authority.

## Rework Focus

- Split exhaustive search, structured Tier 1 pass, unresolved retry, source
  evidence, pending append, browser fallback, paid fallback, and cron into
  separate activation components.
- Require source evidence and unresolved-source records before final reporting.
- Keep pending queue writes behind the append helper.
- Keep browser, paid fallback, and cron off unless explicitly enabled.

## Local Source

The live skill source is outside this vault:

`/Users/billabobz/Career_app/quantum_radar/codex-skills/quantum-job-collector`
