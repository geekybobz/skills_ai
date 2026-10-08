# Markdown Protocol Index

A human-facing map for understanding and maintaining the Markdown Protocol
package. Models performing ordinary Markdown work start from
[SKILL.md](SKILL.md) and load only the reference required for the task.

## Choose a route

| intention | open |
|---|---|
| Understand the governing principles | [Core Protocol](references/core-protocol.md) |
| Plan a Markdown change | [Review Workflow](references/review-workflow.md) |
| Choose a document layout | [Layouts](references/layouts.md) |
| Learn a formatting technique | [Markdown Pattern Gallery](references/markdown-patterns.md) |
| Design a useful visual | [Visual Patterns](references/visual-patterns.md) |
| Validate completed Markdown | [Validation](references/validation.md) |
| Create learning material | [Education Add-on](references/addons/education.md) |
| Document a repository | [Codebase Add-on](references/addons/codebase.md) |
| Structure a skill package | [Skill Package Add-on](references/addons/skill-package.md) |

## Package map

```mermaid
flowchart LR
    Task[Model task] --> Skill[SKILL.md]
    Reader[Human reader] --> Index[INDEX.md]
    Skill --> Core[Core references]
    Skill --> Addons[Selected add-on]
    Index --> Core
    Index --> Addons
    Index --> Gallery[Formatting gallery]
    Core --> Check[Validation]
    Addons --> Check
```

Text version: `SKILL.md` is the compact machine entry, `INDEX.md` is the human
map, focused references own the detail, and validation checks the result.

## Core references

| file | owns | load when |
|---|---|---|
| [core-protocol.md](references/core-protocol.md) | universal structure, ownership, portability, and footer rules | every Markdown task |
| [review-workflow.md](references/review-workflow.md) | proportional proposal and approval behavior | before a write |
| [layouts.md](references/layouts.md) | adaptive single-file and collection structures | creating or reorganizing files |
| [markdown-patterns.md](references/markdown-patterns.md) | human formatting catalogue | choosing or learning a pattern |
| [visual-patterns.md](references/visual-patterns.md) | diagram selection and fallbacks | when a visual materially helps |
| [validation.md](references/validation.md) | structural and renderer-aware completion checks | before finishing |

## Add-ons

| add-on | extends the protocol for |
|---|---|
| [education.md](references/addons/education.md) | learning, revision, and unfamiliar concepts |
| [codebase.md](references/addons/codebase.md) | codebase orientation, workflows, and change impact |
| [skill-package.md](references/addons/skill-package.md) | machine-efficient and human-navigable skill packages |

Add-ons may specialize presentation and validation. They do not replace the
core invariants or the proportional review gate.

## Formatting examples

The [Markdown Pattern Gallery](references/markdown-patterns.md) owns the
complete ordered list of small examples under `references/formatting-examples/`.
Open only the example needed for the current question.

## Package support

```text
agents/openai.yaml    -> native UI metadata and invocation policy
.obsidian/            -> optional local viewing state; not routing authority
```

## Maintenance boundaries

- `SKILL.md` owns model selection, essential behavior, and selective routing.
- `INDEX.md` owns human package navigation and this internal inventory.
- Each focused reference owns the subject named by its title.
- The pattern gallery owns its example sequence.
- Repository registries own public discovery and activation metadata.
- Generated repository views are replaceable projections, never canonical
  package prose.

---

[⌂ Home](#markdown-protocol-index)
