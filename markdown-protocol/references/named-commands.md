# Named Commands

Named commands select a focused Markdown Protocol operation. They do not bypass
the review gate, grant write authority, select a domain skill, or broaden the
files already in scope.

## `#> md_deepen <term>`

Create a plain-language deeper note for one term in a user-identified parent
topic. If the parent is not unambiguous, identify it before proposing a write.

1. Inspect the parent and its existing `Deeper` connections.
2. Propose the new note's purpose, path, information owner, and reciprocal links.
3. After approval, write a concise explanation that preserves the domain owner's
   terminology, prerequisites, limitations, and evidence status.
4. Add a typed `Deeper` relative link to the parent and a reciprocal typed
   `Parent` relative link to the new note.
5. Add the required footer and run the normal Markdown checks.

The command does not authorize research, invent missing subject matter, or
create a note when a short clarification in the parent is sufficient.

## `#> md_check`

Run the package checker against the user-named Markdown collection, or the
current collection when the target is already unambiguous:

```bash
python3 markdown-protocol/scripts/markdown_protocol.py check <COLLECTION>
```

Report the target, pass or failure, and actionable diagnostics. This is a
read-only structural check. It does not prove factual correctness, renderer
quality, or compliance with another domain's rules. Do not repair failures
unless the user also asks for edits or an approved write is already in progress.

## Argument boundary

The declared aliases are `#> md_deepen` and `#> md_check`. Text following the
alias supplies the term or target; it is task input, never part of the alias or
an additional permission.

---

[⌂ Home](../INDEX.md)
