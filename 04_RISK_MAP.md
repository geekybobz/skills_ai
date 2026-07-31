# Risk Map

Read before file writes, scripts, compression, generated artifacts, or Git.

## Navigation

- Back: [[00_SKILLS_HUB]]
- Triggers: [[01_TRIGGER_MAP]]
- Load order: [[02_LOAD_ORDER]]
- Combos: [[03_COMBO_MAP]]

## Skill Risk Table

| skill or family | risk | rule |
|---|---|---|
| Design specialists | usually guidance only | write files only when user asks to build or edit |
| `poster-lead` | can lead to generated HTML/CSS/PDF work | propose layout first when user asks for review or plan |
| `auth-implementation` | changes app auth code when used in a project | inspect stack and ask only if provider choice is ambiguous |
| `database-setup` | may create database/client code | avoid secrets and `.env` leakage |
| `deploy-to-vercel` | may require network/account actions | use approval for external writes or network installs |
| `caveman` | response style only | no file writes |
| `caveman-compress` | overwrites target prose file after backup | confirm target, avoid secrets, never compress backup files |
| `caveman-review` | review output only | does not edit code |
| `caveman-commit` | message output only | does not run `git commit` |
| `caveman-stats` | hook-provided stats | model does not compute stats |
| `theory-reference` planning | writes plan and outline after approval | no LaTeX in planning phase |
| `theory-reference` chapter build | writes LaTeX after approval | read rules and templates first |
| `theory-reference` evaluate | edits only approved outlines | no LaTeX and no plan reorder without explicit approval |

