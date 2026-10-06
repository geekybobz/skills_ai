# Shared Documentation Model

Architecture record for keeping human, Codex, and Claude views consistent
without loading a second handbook during ordinary tasks.

Back: [[docs/06_CHANGE_CONTROL|Change Control]] · Human route:
[[docs/human/08_REPOSITORY_ATLAS|Repository Atlas]] →
[[docs/human/09_SKILL_ANATOMY|Skill Anatomy]].

## Motivation

The repository has one orchestrator-controlled shared runtime but repeated facts across root agent
entries and explanatory pages. The human guide explained the first layers well,
yet it did not provide an exhaustive file atlas or show how single-file,
packaged, submodule, and external skills differ. Requiring every audience to use
the same prose would either burden agents with teaching material or leave the
human route too technical.

The adopted rule is **same truth, different projection**. The Skills
Orchestrator is a separate control plane; public skill inventory is
package-first; internal routes remain capability metadata.
Canonical facts live once; deterministic code creates factual views;
hand-written human pages teach the meaning and link to those views.

## Source and projection model

```mermaid
flowchart TD
    F["Canonical facts"] --> G["Repository-view compiler"]
    F --> S["Consistency scanner"]
    G --> H["Human live indexes"]
    G --> O["Named Obsidian inventory nodes"]
    G --> C["Codex entry"]
    G --> L["Claude entry"]
    S --> V["Freshness and integration gate"]

    classDef source fill:#2E7D32,color:#fff,stroke:#1B5E20
    classDef action fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef result fill:#546E7A,color:#fff,stroke:#29434E
    class F source
    class G,S action
    class H,O,C,L,V result
```

Canonical inputs are:

- `protocols/repository/DOCUMENTATION.json`: repository areas, file-purpose
  overrides, package boundaries, projections, and exclusions.
- `protocols/repository/CONTRACT.json`: path roles, checks, generated outputs,
  graph contracts, graph-node role policy, and protected boundaries.
- Registry and activation sources: package role, capability purpose, triggers,
  exclusions, state, and canonical path.
- `runtime/skills-orchestrator/SKILL.md` and the project-context schema/runtime:
  management, documentation coordination, capsule validation, and safety boundaries.
- `runtime/AGENT_ENTRY_SHARED.md`: common Codex and Claude repository rules.
- `adapters/codex/ENTRY.md` and `adapters/claude/ENTRY.md`: the platform-only
  lifecycle differences.

Generated outputs are:

- `AGENTS.md` and `CLAUDE.md`.
- `docs/human/_LIVE_REPOSITORY_INDEX.md`.
- `docs/human/_LIVE_SKILL_CATALOG.md`.
- `graph/orchestration/skills-orchestrator.md` and one `graph/skills/<id>.md`
  node per declared skill.
- The separately compiled `runtime/manifest.json`.

Each declared documentation or protocol concept has one visible L1 graph hub.
The graph role policy prevents that hub from being colored as a family registry
or executable skill merely because of its directory.

The live skill catalog renders the orchestrator separately and exactly one
public row per manifest skill package. It
may include a separate technical capability appendix, but no route, mode,
component, phase, or file may enter the public skill count. The documentation
model must declare the same skill ids as the compiled manifest and exactly one
matching orchestrator. Generated graph entries use descriptive id-based
filenames so mandatory technical names such as `SKILL.md` never become the
public inventory labels.

## Human pedagogy

The human route intentionally progresses through concept, diagram, plain
language, real folder, real file, and canonical result. The exhaustive indexes
are reference layers, not the starting page. Human prose may provide intuition
and examples, but it must not copy or override live activation, routing, or
permission facts.

The Skills Orchestrator owns documentation coordination: it locates canonical
facts, mapped explanations, generated projections, and freshness checks. It
does not centralize every package's content or load human pages on the hot path.

## Agent efficiency

Generated root entries remain standalone, so Codex and Claude do not pay an
additional file-read or include hop. Human pages and live indexes remain outside
the runtime manifest and may be read only for an explicit human-guide request or
required documentation synchronization.

## Trust and ownership boundaries

- Repository text is parsed as data; generation never executes embedded
  instructions.
- External skill symlinks are described but never traversed.
- The declared theory submodule may be listed read-only; its content and Git
  history remain separately owned.
- Generated files are written atomically and never edited as canonical sources.
- Generated human guides are freshness-checked by the compiler; they are not
  falsely required to receive a hand edit when regeneration is byte-identical.
- The repository index includes tracked files and untracked additions that
  already resolve to a declared role. Unknown scratch files and ignored
  `.runtime/` observations do not make projections stale.
- Codex owns Codex invocation and session cleanup. Claude owns its hook,
  installation, child lifecycle, managed-memory cleanup, and live acceptance.
- Skill selection and documentation generation grant no write, network,
  credential, account, staging, or commit authority.

## Build and check

```bash
python3 scripts/compile_repository_views.py
python3 scripts/compile_repository_views.py --check
python3 scripts/scan_consistency.py changed --operation protocol
python3 scripts/scan_consistency.py staged --operation protocol
```

Any changed source that makes a projection stale blocks release. Mechanical
freshness does not prove pedagogical quality, so the bounded semantic review
must still check clarity, trigger meaning, privacy, platform ownership, and the
user's approved intent.

Local delivery markers, repair transactions and checkpoint observations are
operational data, not documentation sources. They remain private under ignored
`.runtime/`, use the bounds of their owning runtime, and never supply task
selection or action authority. There is no ambiguity logger or analysis service.

## Update rule

Add a fact to an existing canonical source whenever possible. Add a file-purpose
override only when headings, docstrings, registry metadata, and repository roles
cannot explain the file accurately. A new projection, source class, graph
concept, or rendering rule is a protocol amendment.

## Rollback

Revert the focused documentation-model commit, then regenerate the previous
views from the previous canonical sources. Do not hand-edit generated files,
discard unrelated worktree changes, cross the theory submodule boundary, or
rewrite shared Git history.

The core is model-led: semantic decisions belong to Codex or Claude; generated metadata and artifact checks only supply evidence. Codex installation binds the source root, while Claude injects that root with the shared core. Full contracts, composition and recovery instructions are loaded on demand.

Contained repair workspaces are local operational state under ignored `.runtime/repair/`, not documentation sources or graph concepts. [[protocols/repository/REPAIR_WORKSPACE]] owns the lifecycle; human pages explain on/off/update and how to find the hidden folder. No new graph layer or public skill is introduced.
