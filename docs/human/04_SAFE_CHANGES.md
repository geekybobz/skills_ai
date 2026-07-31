---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Safe Changes

Back: [skills and controls](03_SKILLS_AND_CONTROLS.md). Next: [speed and troubleshooting](05_SPEED_AND_TROUBLESHOOTING.md).

## Change-control flow

```mermaid
flowchart TD
    U["User requests a repository change"] --> OP["Choose one operation protocol"]
    OP --> RISK["Apply the risk map"]
    RISK --> PACKET["Declare paths, authority, rollback, tests,<br/>graph layer, and human-doc impact"]
    PACKET --> SCOPE{"Unexpected or destructive expansion?"}
    SCOPE -- "Yes" --> ASK["Explain exact effect and request permission"]
    SCOPE -- "No" --> WORK["Edit only declared canonical sources"]
    ASK --> WORK
    WORK --> CHECK["Run focused and repository checks"]
    CHECK --> REPORT["Report files, behavior, evidence, and boundaries"]

    classDef action fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef decision fill:#EF6C00,color:#fff,stroke:#A64700
    classDef safe fill:#2E7D32,color:#fff,stroke:#1B5E20
    class U,OP,RISK,PACKET,WORK,CHECK action
    class SCOPE decision
    class ASK,REPORT safe
```

Selecting a skill is never permission. Deletion, external installation,
credentials, account actions, Git-history rewrites, protocol changes, and
unexpected expansion require their own explicit authority.

## Keeping this human guide current

Relevant canonical sources are mapped to the human pages that explain them.
Whenever one changes, the mapped page must be updated in the same staged change.

```mermaid
flowchart LR
    EDIT["Canonical source changes"] --> MAP["Read _SOURCE_MAP.json"]
    MAP --> DOC["Identify required human pages"]
    DOC --> PRESENT{"Pages changed too?"}
    PRESENT -- "No" --> BLOCK["Block release"]
    PRESENT -- "Yes" --> VERIFY["Validate markers, links, Mermaid,<br/>manifest exclusion, and coverage"]
    VERIFY --> PASS["Change may proceed"]

    classDef action fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef decision fill:#EF6C00,color:#fff,stroke:#A64700
    classDef stop fill:#C62828,color:#fff,stroke:#7F0000
    classDef safe fill:#2E7D32,color:#fff,stroke:#1B5E20
    class EDIT,MAP,DOC,VERIFY action
    class PRESENT decision
    class BLOCK stop
    class PASS safe
```

The guard proves that documentation was changed alongside mapped behavior. It
cannot prove that prose is conceptually perfect, so human review remains the
final quality gate.

## External tasks

A task that starts outside this repository treats Skills AI as read-only. With
explicit permission it may create one Markdown request under `requests/pending/`.
Implementation then moves to a dedicated maintenance task rooted in this folder.
The request inbox is never routing or skill authority.
