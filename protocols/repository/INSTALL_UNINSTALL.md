# Install And Uninstall Protocol

Use for writes outside this repository, including Codex and Claude config roots.

1. Name every external target and distinguish managed from foreign content.
2. Run the repository consistency plan for the installer and adapter sources.
   The scanner never treats a repository result as external-write permission.
3. Dry-run and show the exact result before the external write.
4. Back up mutable configuration before changing it. Preserve the first
   pre-install snapshot; use a separate latest-state backup on later updates.
5. Obtain explicit permission for the external write.
6. Make install, update, check, migration, and uninstall idempotent.
7. Refuse symlinks, resolve containment through real paths, and preserve
   foreign regular files as well as foreign settings content.
8. Uninstall only byte-for-byte managed entries or entries with an equivalent
   durable ownership marker.
9. Run the repository staged scan, then verify on the owning platform: Codex certifies Codex integration; Claude
   certifies Claude integration.

Neither platform may certify or silently modify the other platform's lifecycle.
