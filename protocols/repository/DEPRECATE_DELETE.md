# Deprecate And Delete Protocol

Canonical behavior normally follows `active/manual -> deprecated -> delete`.

1. List exact targets and explain why disabling or deprecation is insufficient.
2. Find inbound references, installed copies, generated outputs, and dependent
   tests or documentation.
3. Provide recovery or rollback information.
4. Obtain explicit approval for canonical deletion.
5. Remove external files only when they are installer-managed and match the
   expected managed content; preserve foreign files.
6. Recompile and validate routing sources after removal.
7. Recheck graph-layer coverage and remove a colour query only when no remaining
   file depends on it.
8. Confirm that no dangling links, routes, configuration entries, or processes
   remain.

Temporary test artifacts and byte-for-byte installer-managed copies need no
deprecation period, but the target must still be exact and ownership verified.
