---
title: Interaction Protocol Migration
type: migration-record
status: implemented
topic: interaction-protocol
tags:
  - interaction
  - routing
  - migration
  - token-efficiency
---

# Interaction Protocol Migration

Back to [[00_SKILLS_HUB]]. Protocol:
[[interaction-protocol/README|Interaction Protocol]]. Registry:
[[registry/interaction]]. Runtime: [[runtime/PROTOCOL]].

## Git checkpoint

- Baseline commit: `043909b095e6c2ead44706208c22eb1d76db2501`
- Baseline subject: `feat(skills-ai): harden routing and add guide`
- Pre-existing `.obsidian/graph.json` display preferences and untracked
  `sample_resources/` were excluded from the migration scope.

The commit hash is the rollback checkpoint. Reversal should use a focused Git
revert of the migration commit rather than rewriting history or discarding
unrelated work.

## Motivation

The former Caveman family combined compact replies, character voice,
mathematical explanation, file compression, review, commit, delegation, help,
telemetry, installers, and platform packages. Ordinary mathematical prompts
still required narrow phrases such as “formula first,” and response style
competed for the single task-skill slot.

The replacement keeps only two needs:

1. a compact professional general response with adequate context; and
2. equation-led mathematical reasoning followed by short supporting prose.

## Contract change

```text
before: prompt -> one Caveman skill or one task skill -> response
after:  prompt -> general protocol -> optional math overlay
               -> zero or one task skill -> response
```

Interaction guidance is now structured context, not a task skill. It can
therefore compose with `theory-reference`, design, build, or another selected
skill without loading a second skill body.

## Selection boundary

Automatic math mode requires mathematical intent: a mathematical action and
object or expression, an explanatory question about a strong mathematical
object, or research context explicitly requesting mathematical reasoning.
Code, paths, filenames, URLs, settings, search, parser, field, and rendering
mentions cannot activate math merely by containing a trigger word.

Controls:

- `interaction.math = active`: automatic and explicit selection;
- `interaction.math = manual`: explicit `/interaction math` only;
- `interaction.math = off`: disabled; and
- `/interaction general`: current-request general override.

## Deliberate removals

- Caveman branding and character grammar.
- Lite, full, ultra, and Wenyan modes.
- Caveman help, stats, status line, commit, review, compression, and delegation
  skills.
- Caveman commands, hooks, installers, generated mirrors, and packages.
- The superseded broad eight-operation migration plan.

Generic review, commit, explain, investigate, implement, and write shapes remain
in the shared runtime without separate response-style skills.

## Verification boundary

The shared Python runtime and repository Claude adapter are tested here. A live
Claude installation remains Claude-owned acceptance. No external Codex or
Claude configuration is changed by this repository migration.
