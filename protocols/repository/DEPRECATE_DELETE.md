# Deprecate And Delete Protocol

Canonical behavior normally follows `active/manual -> deprecated -> delete`.

1. List exact targets and explain why disabling or deprecation is insufficient.
2. Run `scan_consistency.py plan --operation deprecate` or `delete`. The Git
   scan must retain deleted paths so missing consumers cannot disappear from
   inspection.
3. Find inbound references, installed copies, generated outputs, and dependent
   tests or documentation.
4. Provide recovery or rollback information.
5. Obtain explicit approval for canonical deletion.
6. Remove external files only when they are installer-managed and match the
   expected managed content; preserve foreign files.
7. Recompile and validate routing sources after removal.
8. Recheck graph-layer coverage and remove a colour query only when no remaining
   file depends on it.
9. Run the changed and staged scans and confirm that no dangling links, routes,
   configuration entries, or processes remain.

Temporary test artifacts and byte-for-byte installer-managed copies need no
deprecation period, but the target must still be exact and ownership verified.
