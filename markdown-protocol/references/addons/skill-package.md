# Skill Package Add-on

Use this add-on when creating, documenting, or substantially restructuring a
skill package whose artifacts include Markdown. It adapts the Markdown Protocol
to skill packages without replacing native skill rules or repository
governance.

## Outcome

Create one package that is cheap for a model to enter and easy for a human to
browse:

```text
model -> SKILL.md -> one selected reference
human -> INDEX.md -> package map -> relevant file
```

The target skill remains authoritative for domain behavior. This add-on owns
only the Markdown layers, navigation, portability, and related validation.

## Add-on declaration

| field | declaration |
|---|---|
| Trigger | Creating, documenting, or substantially restructuring a skill package with Markdown; not ordinary use of an existing skill |
| Blocks | Machine entry, human route map, responsibility split, package profile, migration plan, and maintenance boundaries |
| Layout variants | Minimal, Routed, Navigable, and Tool-bearing package profiles |
| Generated views | Repository-owned manifests, graph nodes, or human indexes produced only through their canonical generators |
| Checks | Native metadata, selective loading, links, footers, registry state, generated views, adapters, and token budget |
| Composition | Target skill owns domain behavior; native skill guidance owns package validity; orchestrator owns lifecycle |
| Boundaries | No duplicate governance, implicit migration, invented files, or extra public skills |

## Responsibility split

| owner | responsibility |
|---|---|
| Target skill | domain behavior, methods, and technical correctness |
| Native skill-creation guidance | valid package form, metadata, references, scripts, and assets |
| Markdown Protocol | document layers, human index, navigation, tone, portability, and footers |
| Skills Orchestrator | selection, composition, repository lifecycle, change control, and verification |
| Registry | public discovery, activation, and capability metadata |
| Generated views | replaceable projections from canonical sources |

Do not copy repository governance or native packaging instructions into the
target skill. Link to their canonical owners when a maintainer needs them.

## Adaptive package profiles

Choose the smallest profile that gives each file a distinct job.

| profile | structure | use when |
|---|---|---|
| Minimal | `SKILL.md`; optional `agents/openai.yaml` | one compact entry is sufficient |
| Routed | `SKILL.md` plus focused references | conditional detail should load selectively |
| Navigable | Routed profile plus `INDEX.md` | human navigation is a separate job |
| Tool-bearing | Navigable or Routed profile plus necessary scripts or assets | repeated mechanics or output resources justify them |

`INDEX.md` is expected for a multi-file package when a human cannot understand
the package routes from the compact entry without scanning the directory. Do
not add it to a genuinely minimal package merely for symmetry.

## Two front doors

### Machine entry: `SKILL.md`

Keep the required entry compact. It owns:

- discriminating selection metadata;
- essential behavior and boundaries;
- the minimum routing table needed to choose a focused reference;
- a link to `INDEX.md` for human browsing or package maintenance, explicitly
  marked as unnecessary during ordinary task execution.

Do not turn `SKILL.md` into a complete directory listing or duplicate detailed
references there.

### Human entry: `INDEX.md`

The index owns:

- one-sentence package orientation;
- routes by reader intention;
- a small package diagram with a text fallback;
- grouped tables for core references, add-ons, examples, scripts, and assets;
- file ownership and maintenance boundaries;
- a compact navigation footer.

It is a semantic map, not a raw filesystem dump. Link to a subordinate gallery
or local index instead of repeating its complete inventory.

## Reference organization

Keep established clear paths unless moving them solves a real navigation or
ownership problem. New folders are optional and may include:

```text
references/
├── core-or-workflow.md
├── addons/
└── examples/
```

A path is not a layer by itself. The layer comes from its role and loading
condition. Avoid moves whose only effect is making packages look identical.

## Navigation

- `SKILL.md` and top-level references use `INDEX.md` as Home in a Navigable
  package.
- Add-ons return to the package index unless a closer semantic hub exists.
- Examples return to their local gallery; that gallery returns to the package
  index.
- Previous and Next express only an intentional reading order.
- Generated Markdown receives navigation through its canonical generator.

Follow the core footer contract and keep every target relative and resolvable.

## Orchestrator composition

For every future skill creation, documentation, or substantial restructuring
operation that creates or edits Markdown, the Skills Orchestrator composes:

1. the target skill's domain requirements;
2. native skill-creation guidance;
3. this add-on and the Markdown Protocol core;
4. repository change control and mapped verification.

The canonical integration hook lives in the
[Orchestrator build workflow](../../../runtime/skills-orchestrator/BUILD.md).
This requirement does not authorize a repository-wide migration. Existing
skills change one at a time only when the user names and approves their scope.

## Per-skill migration

1. Inspect the named package entry and bounded file map.
2. Identify machine entry, human routes, authoritative owners, conditional
   references, tools, generated files, and platform overlays.
3. Select a package profile and propose exact additions, moves, link changes,
   generated consumers, and checks.
4. Wait for review before structural writes.
5. Preserve useful paths and domain behavior; do not normalize for appearance.
6. Implement only the approved package.
7. Validate native loading, selective reference access, links, footers,
   registry metadata, generated views, and affected host adapters.
8. Commit the package migration independently when the user authorizes a
   commit.

## Boundaries

- Do not preload `INDEX.md` during ordinary task execution.
- Do not make internal files, phases, add-ons, or routes additional public
  skills.
- Do not duplicate the global registry inside a package index.
- Do not edit external packages, vendored content, or submodules implicitly.
- Do not add scripts, assets, examples, or directories without a concrete job.
- Do not migrate every repository package because one package adopted this
  structure.
- Do not let explanatory depth add or change rules absent from the operational
  entry and authoritative references.

## Validation

- `SKILL.md` remains sufficient for correct selection and initial routing.
- Ordinary execution does not require loading `INDEX.md`.
- The index maps every meaningful package area without duplicating its content.
- Each reference has one named responsibility and an explicit loading reason.
- Footer Home targets follow the package and local-hub hierarchy.
- All links, anchors, Previous/Next pairs, and generated views resolve.
- Native metadata, registry state, public skill count, and adapter behavior
  remain correct.
- The chosen profile is justified by navigation need rather than uniformity.

---

[⌂ Home](../../INDEX.md)
