# Install And Uninstall Protocol

Use for writes outside this repository, including Codex and Claude config roots.

1. Name every external target and distinguish managed from foreign content.
2. Dry-run and show the exact result before the external write.
3. Back up mutable configuration before changing it.
4. Obtain explicit permission for the external write.
5. Make install, update, check, migration, and uninstall idempotent.
6. Refuse symlinks and preserve foreign content.
7. Uninstall only byte-for-byte managed entries or entries with an equivalent
   durable ownership marker.
8. Verify on the owning platform: Codex certifies Codex integration; Claude
   certifies Claude integration.

Neither platform may certify or silently modify the other platform's lifecycle.
