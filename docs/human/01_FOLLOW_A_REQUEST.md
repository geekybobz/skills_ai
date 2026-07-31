---
audience: human
authority: explanatory-only
agent_read_policy: explicit-human-guide-task-or-doc-sync-only
---

# Follow a Request

Back: [start here](00_START_HERE.md). Next: [folder and platforms](02_FOLDER_AND_PLATFORMS.md).

## Complete request flow

```mermaid
flowchart LR
    U["User request"] --> E["Shared runtime entry"]
    E --> P["Apply general interaction contract"]
    P --> Y{"Genuine math reasoning?"}
    Y -- "Yes" --> O["Add equation-led math overlay"]
    Y -- "No" --> R["Fast task-skill router"]
    O --> R
    R --> B{"Boundary failure?"}
    B -- "Invalid, timeout, unavailable" --> N["NORMAL"]
    B -- "No" --> D{"Registry-status question?"}
    D -- "Yes" --> M["Return live metadata"]
    D -- "No" --> C["Score allowed routes"]
    C --> X{"Result"}
    X -- "No match" --> N
    X -- "Disabled" --> N
    X -- "Ambiguous" --> N
    X -- "One clear match" --> S["Return one skill path"]
    S --> L["Load only that skill"]
    L --> A["Answer the task"]
    N --> A
    M --> A

    classDef route fill:#5B5BD6,color:#fff,stroke:#32327A
    classDef decision fill:#EF6C00,color:#fff,stroke:#A64700
    classDef safe fill:#2E7D32,color:#fff,stroke:#1B5E20
    classDef normal fill:#546E7A,color:#fff,stroke:#29434E
    class U,E,P,R,C route
    class Y,B,D,X decision
    class O,S,L,A safe
    class N,M normal
```

The router returns a compact receipt. It never returns the original prompt or a
whole family. After a `MATCH`, the caller validates the returned path and reads
only that selected skill.

The interaction protocol is independent of `MATCH`. General guidance keeps the
answer direct and adequately explained. The math overlay activates only for
mathematical actions and objects, explicit mathematical research reasoning, or
an explicit `/interaction math` control. Code, filenames, search terms,
settings, and rendering tasks cannot activate it merely by mentioning
“equation” or “formula”.

See the [Interaction Protocol hub](../../interaction-protocol/README.md) for the
same general and math branches as a connected Obsidian graph route.

## The strict design gate

Visual design and UI skills are intentionally harder to activate because words
such as “search,” “table,” “plot,” and “structure” occur in many non-design
tasks.

```mermaid
flowchart TD
    P["Prompt"] --> CLEAN["Ignore code, URLs, paths, and filenames"]
    CLEAN --> REQUEST{"Actual design request?"}
    REQUEST -- "No" --> SKIP["Skip design and UI families"]
    REQUEST -- "Yes" --> DOMAIN{"Visual or UI domain cue?"}
    DOMAIN -- "No" --> SKIP
    DOMAIN -- "Yes" --> TARGET{"Non-visual direct target?"}
    TARGET -- "API, code, database, equation, router..." --> SKIP
    TARGET -- "No" --> SCORE["Score design and UI routes"]
    SKIP --> OTHER["Continue other families or NORMAL"]
    SCORE --> RESULT["One design skill or NORMAL if ambiguous"]

    classDef check fill:#EF6C00,color:#fff,stroke:#A64700
    classDef safe fill:#2E7D32,color:#fff,stroke:#1B5E20
    classDef normal fill:#546E7A,color:#fff,stroke:#29434E
    class REQUEST,DOMAIN,TARGET check
    class SCORE,RESULT safe
    class SKIP,OTHER normal
```

## Examples

| Request | Design/UI result | Why |
|---|---|---|
| “Search recent papers about quantum control” | Not activated | Search is a research action here |
| “Search for design-system examples” | Not activated | Design is the subject, not the requested action |
| “Create a plot of a sine function” | Not activated | No explicit design request |
| “Design a search interface with autocomplete” | `search-specialist` | Explicit design request plus UI domain |
| “Help me design a sidebar with breadcrumbs” | `navigation-specialist` | Explicit request plus navigation cues |
| “Design an API that returns a table” | Design families skipped | API is a non-visual direct target; another family may match |
| “Design a responsive mobile dashboard” | May return `NORMAL` | Several equally strong design routes can be ambiguous |

This gate changes only the visual design and UI-pattern families. Other enabled
families continue through their normal matching rules.
