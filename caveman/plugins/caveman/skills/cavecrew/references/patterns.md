# Cavecrew Patterns

## Why

Subagent results enter main context verbatim. Compressed locator, edit, and
review receipts preserve more main-thread context than explanatory prose.

## Output Details

Investigator:

```text
<Header>:
- path:line - `symbol` - short note
totals: <counts>.
```

Builder:

```text
<path:line-range> - <change within 10 words>.
verified: <re-read OK | mismatch at path:line>.
```

Terminal refusals: `too-big.`, `needs-confirm.`, `ambiguous.`, `regressed.`

Reviewer:

```text
path:line: <severity>: <problem>. <fix>.
totals: <counts>
```

Zero findings: `No issues.`

## Chains

Locate -> fix -> verify:

1. Investigator returns candidate sites.
2. Main thread selects no more than two files.
3. Builder edits those files.
4. Reviewer checks the diff.

Parallel scout: use two or three investigators with distinct scopes such as
definitions, callers, and tests. Aggregate only their receipts.

Single-shot edit: skip investigation when exact paths and scope are known.

## Refuse

- Builder with unknown files: investigate first.
- Builder with 3+ files: split or use the main thread.
- Reviewer asked for architecture commentary: use a full reviewer.
- Human-facing output needing explanation: paraphrase the compressed receipt.
