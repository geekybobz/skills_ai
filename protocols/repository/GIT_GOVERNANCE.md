# Git governance

Back: [[docs/06_CHANGE_CONTROL|Change Control]]. Containment and live staging:
[[protocols/repository/REPAIR_WORKSPACE]].

Read this card at a Git boundary: a commit, tag, push, clone, submodule pointer
move, rollback, or cleanup of plans, handoffs and runtime state. It adds to the
one operation card for the change and never replaces it. This procedure grants
no authority: commits, tags, pushes, deletions and history changes need the
user's instruction for the exact action, and no tool performs them on its own.

## Ownership

| repository | owns | must not contain |
|---|---|---|
| Skills AI (parent) | orchestrator and tools, adapters, registry and activation, integration contracts, governance, generated views, integration tests, human guide, the in-tree `interaction-protocol`, `.gitmodules` and submodule pointers | a child's files, copies of a child's instructions, new tests of a child's wording or behavior |
| Skill repository (child) | `SKILL.md` and its references, phases, scripts, templates and assets; host wrappers; its own tests; a README with clone, install, update and rollback; `VERSION`, `CHANGELOG.md`, LICENSE, `.gitignore`, CI | registry or activation files, absolute paths into the parent, a required dependency on the parent's tools |

The packages stored as Git submodules are the entries of `.gitmodules`; each is a
separately owned repository. `external-skills/<name>` is an externally owned
pointer, and the parent controls only its activation state. Activation state,
family, command aliases and risk rows describe a child, live in the parent and
never copy its instructions. A child's own `description` stays authoritative for
native use. The parent tests registry, routing, aliases, gates, delivery budgets
and generated views; a child tests its own behavior and structure.

## Clone modes

| goal | command | note |
|---|---|---|
| one skill, native use | `git clone https://github.com/geekybobz/<repository>.git` | self-contained; do not also expose the same package through Skills AI in one host, because a native skill named like a package bypasses its gates and the Claude adapter check reports it |
| the complete system | `git clone --recurse-submodules https://github.com/geekybobz/skills_ai.git`; in an existing clone `git submodule update --init --recursive` | detached HEADs at the pinned commits; scans, views and tests need every submodule populated |
| read-only consumption | add `--depth 1 --shallow-submodules` | not for maintainers: reachability checks need history |
| work on a skill inside the system | `git -C <path> switch main`, then edit and commit in that repository | never commit on a detached HEAD |

## Child-first transaction

A change to a skill under a declared submodule is two transactions in a fixed
order.

1. Child: branch from `main`; change; run the child's own checks; commit; for a
   release update `VERSION` and `CHANGELOG.md` and tag; push; then
   `git -C <child> fetch origin` and confirm
   `git -C <child> merge-base --is-ancestor HEAD origin/main`.
2. Parent: `git -C <child> status --porcelain` is empty and `git submodule status`
   shows only the intended move; run the operation's classify, plan, changed and
   staged scans; regenerate affected views; stage explicit paths (the pointer and
   its mapped consequences); commit; push with
   `git push --recurse-submodules=check`.

The parent never records a child commit that is dirty, unpublished, or neither on
the child's `main` nor under a release tag. When a parent check fails, fix
forward in a new commit: never amend or force-push a published child commit, and
never discard the child commit to make the parent pass.

## Branches

`main` is the only long-lived branch in every repository and stays releasable:
all checks pass at every commit on it. Multi-commit work uses `topic/<slug>` and
returns by `git merge --ff-only`. The parent's `main` pins only commits that are
on the child's `main` or carry a release tag. Published history is never
rewritten or force-pushed, and parent approval never authorizes rewriting a
child. `.gitmodules` records `branch = main` for every submodule as the default
of an explicit `git submodule update --remote`; the pinned commit stays
authoritative for builds.

## Commits

One concern per commit. The subject is imperative and at most 72 characters. The
body gives the reason, scope and operation, verification with results, and a
rollback hint. A pointer commit also names the child, the old and new short
hashes, the version or tag and the child's commit subjects. Commit generated
files with their sources so every commit passes `--check`. Stage explicit paths:
never `git add .`, `git add -A` or `git commit -a` in the live checkout, and never
include unrelated dirty work or inherited repair changes. Keep the attribution
trailer the host requires.

## Versions and releases

A child declares one SemVer in `VERSION` (package metadata such as
`pyproject.toml` reads it), keeps a short `CHANGELOG.md`, and tags a verified
release with an annotated `vMAJOR.MINOR.PATCH`. PATCH is wording or a fix without
a contract change. MINOR adds a capability, mode, alias or reference compatibly.
MAJOR removes or renames a control, alias or entry path, or changes a gate or
output contract. Below `1.0.0` a MINOR may break and the changelog says so. When
a registry contract exists, its `package.version` equals the child's `VERSION` at
the pinned commit.

The parent has no SemVer; a release is a verified combination. After a passing
full scan and any required host acceptance, an annotated tag
`release/YYYY.MM.DD[.n]` records the protocol version, the manifest
`source_hash` and the pinned child tags or hashes. A published tag is never
moved: supersede it with a newer one.

## Updates

Updates are user-initiated; nothing checks, fetches or pulls in the background.
To move a pin: `git -C <child> fetch --tags origin`, then
`git -C <child> switch --detach <tag-or-main-commit>`, run the child's checks and
the parent's scans, and commit the pointer under the child-first rule. A
standalone clone updates with `git pull --ff-only` after reading its changelog.
After a change to the orchestrator core, refresh each host through its own
reviewed installer: the Claude hook reads the source root, while the Codex entry
embeds the core.

## Rollback

Rollback is a new commit, never a rewrite. Revert the parent commit, or restore
an earlier pin with `git -C <child> switch --detach <earlier>` and a pointer
commit; in a child, revert the commit and release a patch. Deployed source uses
the repair controller's `recover` preview and hosts use their managed backups.
Afterwards regenerate views and run the full scan.

## Dirty worktrees

Preserve unrelated changes; never stash, reset or clean a shared checkout to make
a gate pass. Before any parent commit run
`git status --porcelain=v1 --ignore-submodules=none`: a modified submodule must be
the intended pointer move, and every child must be clean. A dirty child blocks its
own pointer move. A repair workspace holds frozen copies of the children, so
commits, tags, pushes and pointer moves happen in the live checkout after the
child is published, with bounded staging.

## Generated files

Edit the canonical source and regenerate; never hand-edit a generated file. A
child's generated files (for example an inventory) belong to that child and the
parent never regenerates them. Local state (`.runtime/`, caches, bytecode, editor
state) stays untracked, and every repository carries a `.gitignore` for it.

## Plans, handoffs and runtime state

`skill-plans/<name>/plan.md` is an initial idea and a handoff or review note is
temporary; neither is a skill, a registry source or a release input. Absorb a
handoff's findings into their canonical owners, then delete it. Delete a promoted
plan in the transaction that creates its `SKILL.md`, and remove empty leftover
folders. Delete only after the user agrees to the exact paths, never as a side
effect of another operation. Ignored `.runtime/` receipts, baselines and previews
are rollback evidence: keep them until the next release tag, then list candidates
with a dry run and delete only on instruction. No tool deletes them automatically.

## Enforcement today

The consistency scan blocks staged paths outside the declared scope, stale
generated views and missing human-page updates, and its views and unit checks
need populated submodules. Child cleanliness, publication, reachability and
fast-forward pins are verified by the host with the commands above until a
deterministic submodule check exists.

## Details

Why the child goes first: every parent revision stays cloneable, and a
local-only child commit never becomes an unreachable dependency. Why `main` is
releasable: a pin, a tag and a rollback target are then always checkable states.

Commit body:

```text
<imperative subject, at most 72 characters>

Why: <reason or the user's request>
Scope: <paths or package>; operation <operation>; approval <reference>
Verification: <checks run and their results>
Rollback: <how to revert>
Pointer: <child> <old>..<new> (<version or tag>): <child commit subjects>
```

Parent release tag annotation:

```text
release/YYYY.MM.DD
protocol: <version>   manifest source_hash: <hash>
<child>: <tag or hash>   (one line per submodule)
```

Standalone README block for a child:

```text
Standalone use: clone, install as described above, update with git pull --ff-only
after reading CHANGELOG.md. Version: VERSION. Roll back with git revert or a
checkout of an earlier tag. Skills AI integration is optional; this repository
needs nothing from it.
```

Per-clone settings (local to one clone; none are applied automatically):

```sh
git config push.recurseSubmodules check
git config status.submoduleSummary true
git config diff.submodule log
```
