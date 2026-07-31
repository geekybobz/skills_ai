# Load Order

This is the token-efficient traversal rule for agents.

## Navigation

- Back: [[00_SKILLS_HUB]]
- Triggers: [[01_TRIGGER_MAP]]
- Combos: [[03_COMBO_MAP]]
- Risk: [[04_RISK_MAP]]

## Standard Route

```text
[[SKILLS]]
  -> [[00_SKILLS_HUB]]
    -> one index family file
      -> one family hub
        -> one selected skill file
```

## Family Routes

| family | family index | family hub | final load |
|---|---|---|---|
| Design | [[index/design]] | [[design-with-claude/DESIGN_HUB]] | one or two `design-with-claude/*.md` files |
| Compression | [[index/compress]] | [[caveman/CAVEMAN_HUB]] | one `caveman/skills/*/SKILL.md` file |
| Theory | [[index/theory]] | [[theory-reference/THEORY_HUB]] | wrapper, shared router, then one phase file |

## Stop Conditions

Stop reading registry files when:

- the exact skill file is known
- the active theory phase is known
- the task is outside the registry scope
- the risk map says approval is needed before continuing

## Anti-Pattern

Loading all 42 design skill files or all caveman packaged copies defeats the
purpose of the registry.
