# External Change Request Protocol

Use when a task whose initial workspace is outside
`/Users/billabobz/skills_ai` is asked to add, edit, update, move, disable, or
delete anything in this repository.

## Invariant

An external task treats the repository as read-only. Even when the user
explicitly requests a Skills AI change, that task may create only one Markdown
file under `requests/pending/` by using `scripts/create_change_request.py`.
It must not edit canonical sources, generated files, skill bodies, adapters,
configuration, Git state, or existing request files.

## Procedure

1. Inspect only enough live metadata to describe the problem and likely target.
2. Confirm that the user explicitly requested a Skills AI change.
3. Send one JSON object to:

   ```bash
   python3 /Users/billabobz/skills_ai/scripts/create_change_request.py --stdin-json
   ```

4. Show the resulting request path and handoff summary. Do not stage or commit it
   from the external task.
5. Open or launch a dedicated maintenance task only when the user has explicitly
   approved that handoff, either in the original instruction or after reviewing
   the request.
6. The maintenance task must use `/Users/billabobz/skills_ai` as its workspace,
   read the request and repository protocols, run `change_guard.py plan`, and
   then run `scan_consistency.py plan`. It remains within the approved target
   paths and finishes with a staged consistency scan.

## Enforcement boundary

`AGENTS.md`, `CLAUDE.md`, the runtime context, and `change_guard.py` provide a
shared behavioral guard. Host configuration must provide the hard boundary:
ordinary external tasks receive read-only access to this repository plus write
access only to `requests/pending/`; maintenance tasks receive explicitly scoped
repository write access. A protocol cannot compensate for a host that grants an
external shell unrestricted filesystem authority.

The request file records intent and evidence. It is not a skill, is never
compiled into the router manifest, and does not itself grant implementation
authority.
