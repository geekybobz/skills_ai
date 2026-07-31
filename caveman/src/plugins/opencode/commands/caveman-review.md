---
description: Caveman-style code review — one-line findings with severity
---
Review the current diff (or files: $ARGUMENTS).

One line per finding. Format: `L<line>: <severity> <problem>. <fix>.`
Severity: bug, risk, nit, or question. Skip non-issues.
Group by file and sort by line. End with totals or `No issues.`
