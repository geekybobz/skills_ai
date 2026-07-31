# Caveman Hub

Canonical caveman skills are under `caveman/skills/`. This hub ignores package
copies and install artifacts.

## Navigation

- Back: [[00_SKILLS_HUB]]
- Family index: [[index/compress]]
- Trigger map: [[caveman/CAVEMAN_TRIGGER_MAP]]
- Combos: [[03_COMBO_MAP]]
- Risk: [[04_RISK_MAP]]

## Canonical Skills

| skill | purpose | source |
|---|---|---|
| `caveman` | persistent terse response mode | [[caveman/skills/caveman/SKILL|caveman/SKILL.md]] |
| `caveman-compress` | compress prose files with backup | [[caveman/skills/caveman-compress/SKILL|caveman-compress/SKILL.md]] |
| `caveman-review` | one-line review findings | [[caveman/skills/caveman-review/SKILL|caveman-review/SKILL.md]] |
| `caveman-commit` | Conventional Commit message drafting | [[caveman/skills/caveman-commit/SKILL|caveman-commit/SKILL.md]] |
| `caveman-help` | one-shot command card | [[caveman/skills/caveman-help/SKILL|caveman-help/SKILL.md]] |
| `caveman-stats` | hook-provided token stats | [[caveman/skills/caveman-stats/SKILL|caveman-stats/SKILL.md]] |
| `cavecrew` | compressed subagent decision guide | [[caveman/skills/cavecrew/SKILL|cavecrew/SKILL.md]] |

## Ignore

Do not route through duplicate packaged copies in `plugins/`, `.agents/`,
`.roo/`, `.kiro/`, or `.junie/`.

## Safety

`caveman-compress` overwrites the target prose file after creating a backup.
Check [[04_RISK_MAP]] before using it.
