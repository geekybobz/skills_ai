# Markdown Checker Learning Starter

## In brief

This temporary packet names the software-engineering ideas used by the Markdown
Protocol checker and points to working examples in this repository. It is a
starter for a later, separate learning resource; it is not part of Skills AI
routing or protocol authority.

There is no single universal name for the whole approach. The closest umbrella
term is **executable specification**: important rules are encoded so a program
can check them. The implementation combines static analysis, linting,
graph-based validation, contract testing, and fixture-based testing.

## Topic map

| topic to learn | central question | repository example |
|---|---|---|
| Static analysis | What can be checked without running the documented system? | [`check_collection`](../../markdown-protocol/scripts/markdown_protocol.py) |
| Linter and validator design | Which findings are warnings, errors, or invalid usage? | [`Finding` and CLI exit behavior](../../markdown-protocol/scripts/markdown_protocol.py) |
| Lexing and lightweight parsing | How can fenced code, frontmatter, headings, and links be recognized? | [Markdown checker parsing functions](../../markdown-protocol/scripts/markdown_protocol.py) |
| Schema validation | Which properties are required and which values are allowed? | [Structured inventory contract](../../markdown-protocol/references/structured-inventory.md) |
| Graph modeling | How do files and links become vertices and directed edges? | [Orphan-file check](../../markdown-protocol/scripts/markdown_protocol.py) |
| Reachability search | Which files can be reached from the entry point? | [Breadth-first traversal in the checker](../../markdown-protocol/scripts/markdown_protocol.py) |
| Invariants | Which conditions must remain true after every edit? | [Core protocol](../../markdown-protocol/references/core-protocol.md) |
| Contract testing | Does the public command behave as promised? | [Markdown Protocol tests](../../tests/test_markdown_protocol.py) |
| Fixture-based testing | Can a small synthetic collection exercise the whole workflow? | [`test_structured_inventory_tool_builds_checks_and_detects_errors`](../../tests/test_markdown_protocol.py) |
| Negative testing and fault injection | Does a seeded broken link or missing property fail correctly? | [Seeded-error cases](../../tests/test_markdown_protocol.py) |
| Regression testing | Will a future edit reintroduce an earlier failure? | [Navigation, loading-budget, and activation tests](../../tests/test_markdown_protocol.py) |
| Generated-artifact freshness | Can a generated view be reproduced and detected when stale? | [Inventory freshness check](../../markdown-protocol/scripts/markdown_protocol.py) |
| Idempotence | Does regeneration produce the same result when inputs do not change? | [`render_inventory`](../../markdown-protocol/scripts/markdown_protocol.py) |
| CLI contracts | How should commands, output streams, and exit codes be designed? | [`main`](../../markdown-protocol/scripts/markdown_protocol.py) |
| Change gates | How are plan, changed, and staged states checked separately? | [Repository change control](../../docs/06_CHANGE_CONTROL.md) |
| Structural versus visual verification | Why can link tests pass while a diagram is still clipped? | [Renderer matrix](../../markdown-protocol/references/markdown-patterns.md#renderer-matrix) |

## Three useful formulas

For a document graph `G = (V, E)` with entry `s`, orphan files are

```text
O = V - Reachable(s)
```

For compact topic content,

```text
C_topic = nonempty lines in (In brief + Core)
warn when C_topic > 30
```

For Mermaid review pressure,

```text
P = max(nodes / 12, edges / 12, longest LR route / 8)
review when P > 1
```

## Suggested later learning sequence

1. Pure functions, inputs, outputs, and deterministic behavior.
2. Parsing versus full language grammars.
3. Static analysis and linters.
4. Graphs, breadth-first search, reachability, and cycles.
5. Invariants, schemas, and executable specifications.
6. Unit, integration, contract, regression, and negative tests.
7. Generated files, reproducibility, freshness, and idempotence.
8. CLI design, exit codes, diagnostics, and editor integration.
9. Structural tests versus renderer or user-interface tests.
10. CI and staged change gates.

## Prompt for the future task

> Read this folder and the linked repository examples. Build a beginner-friendly
> learning resource that explains each topic independently, derives the graph
> and compactness formulas, walks through the checker code, and includes small
> exercises. Keep the resource generic; use Skills AI only as the running
> example. Prepare it so it can be moved outside this repository.

## Details

This packet deliberately contains pointers instead of full lessons. The later
task should inspect the live source because function names and tests may change.
When the standalone learning resource exists, move or remove this temporary
folder in a separately reviewed cleanup.

---

[⌂ Home](#markdown-checker-learning-starter)
