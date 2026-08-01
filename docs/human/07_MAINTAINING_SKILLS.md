---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Maintaining Skills

Back: [graph and colors](06_GRAPH_AND_COLORS.md). Return to the
[human guide](../../README.md).

This chapter is the human explanation for adding, editing, updating, moving,
disabling, deleting, or installing Skills AI components. You can use it whenever
you are unsure what the agent should update. Machine authority remains in
`docs/06_CHANGE_CONTROL.md`, the selected operation card, and
`protocols/repository/CONTRACT.json`.

## The main idea

You identify the intended operation and primary path. The scanner discovers the
rest from Git and the repository contract, so you do not need to inspect every
registry, graph, manifest, test, and documentation file yourself.

```mermaid
flowchart TD
    U["You approve a change"] --> P["Plan from operation and primary path"]
    P --> I["Compute affected roles and consumers"]
    I --> E["Agent edits approved canonical files"]
    E --> C["Scan the working tree"]
    C --> R{"Result"}
    R -- "BLOCK" --> F["Resolve a deterministic problem"]
    R -- "REVIEW" --> A["Inspect bounded AI questions"]
    F --> C
    A --> C
    R -- "PASS" --> S["Stage declared paths"]
    S --> G["Run final staged scan"]

    classDef action fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef decision fill:#EF6C00,color:#fff,stroke:#A64700
    classDef safe fill:#2E7D32,color:#fff,stroke:#1B5E20
    class U,P,I,E,C,F,A,S action
    class R decision
    class G safe
```

## What is updated for each operation

| Operation | The scanner checks |
|---|---|
| Add | Role, family route, activation, hub, graph entry, risk, tests, manifest, and human pages |
| Edit | Canonical source, semantic behavior, mapped consumers, focused tests, and generated freshness |
| Update or migrate | Old/new contract, compatibility, rollback, shared runtime, platform boundaries, and documentation |
| Move or rename | Git old/new identity, inbound links, imports, activation, manifest, graph, tests, and aliases |
| Deprecate or delete | Approval, recovery, routes, links, generated outputs, tests, documentation, and installed copies |
| Toggle activation | Allowed state transition, link form, parent state, target path, and compiled manifest |
| Install or uninstall | Repository consistency first, then explicit external approval and owning-platform acceptance |

Deletion, protocol amendments, external writes, and unexpected scope expansion
still require explicit permission. The scanner discovers impact; it does not
grant authority.

## Commands you will see

Before editing:

```bash
python3 scripts/scan_consistency.py plan --operation add --path path/to/skill.md
```

After editing:

```bash
python3 scripts/scan_consistency.py changed --operation add --path path/to/approved-scope
```

Before committing:

```bash
python3 scripts/scan_consistency.py staged --operation add --path path/to/approved-scope
```

For a repository-wide health check or a compact receipt:

```bash
python3 scripts/scan_consistency.py full
python3 scripts/scan_consistency.py changed --json
python3 scripts/scan_consistency.py changed --ai-packet
```

`--ai-packet` contains changed paths, roles, deterministic blocks, and focused
review questions. It does not call a network model or include a whole skill
collection.

An agent may use the explicitly approved generated-only action when a canonical
registry change makes the router manifest stale:

```bash
python3 scripts/scan_consistency.py apply-generated --operation update \
  --path registry/example.md --approval-ref approved-change
```

This action can rebuild only a code-allowlisted generated artifact. It cannot
write semantic documentation, skill bodies, external configuration, Git staging,
or commits.

## How to read the result

| Result | Meaning | What happens next |
|---|---|---|
| `PASS` | Deterministic checks found no blocking inconsistency | The declared change may proceed to the next gate |
| `REVIEW` | Mechanical checks pass but semantic judgment is needed | Codex or Claude inspects only the listed files and questions |
| `BLOCK` | Scope, role, graph, registry, manifest, documentation, or a test is inconsistent | Resolve it before staging or committing |

The scanner also lists preserved and ignored changes. For example, personal
Obsidian display preferences can remain visible without being absorbed into a
skill-maintenance commit.

## Code scan and AI review

```mermaid
flowchart LR
    G["Git changes"] --> D["Deterministic scan"]
    D --> V["Paths, roles, links,<br/>manifest and tests"]
    G --> A["Bounded AI review"]
    A --> M["Meaning, triggers,<br/>privacy and clarity"]
    V --> O["Combined receipt"]
    M --> O

    classDef code fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef review fill:#6A1B9A,color:#fff,stroke:#3E0F5C
    classDef result fill:#2E7D32,color:#fff,stroke:#1B5E20
    class G,D,V code
    class A,M review
    class O result
```

Code owns facts that can be proven: Git scope, paths, symlinks, activation,
manifest freshness, links, generated files, test exit codes, and platform
boundaries. AI reviews meaning: whether a trigger is too broad, a `not for`
boundary is missing, the requested behavior was preserved, or the explanation
is confusing. AI cannot override a deterministic block.

Repository files are treated as untrusted data. Instructions embedded inside a
skill body or document are never executed by the scanner. Commands are selected
from a fixed allowlist in code, the scan is local and network-free, and external
configuration remains outside its write authority.

## Example: adding a skill

Suppose `design-with-claude/example.md` is added. The scanner should report if
any of these are missing:

1. A row in the correct family registry.
2. An approved activation state, normally `manual` for a new route.
3. Positive, negative, ambiguous, negated, and injection-resistant prompt cases.
4. A valid graph layer and visible graph relationship.
5. A risk rule if the skill can write, use credentials, access a network, or
   change an account.
6. A fresh generated router manifest.
7. Every mapped human page needed to explain new public behavior.

The agent receives exact paths and suggestions instead of asking you to inspect
the entire folder manually.

## Human-guide and Mermaid rule

Canonical behavior is mapped to the human pages that explain it. A mapped source
change must update those pages in the same staged change. Human pages stay out
of runtime routing and never become skill authority.

Mermaid diagrams are intentionally bounded. A diagram may have at most twelve
nodes and twelve edges; a left-to-right diagram may have at most eight nodes.
Larger ideas must use top-down layout or several focused diagrams. This keeps
the guide readable in Obsidian and narrow application panes.

## Codex and Claude

Both platforms use the same contract, scanner, registry, manifest, graph rules,
and human documentation. Codex owns Codex session cleanup and live acceptance.
Claude owns its hook, child-process lifecycle, installation, and live Claude
acceptance. Neither platform silently certifies the other.

If a new platform is added later, it should consume the same scan receipt and
add only its own thin lifecycle acceptance layer.
