# Move And Rename Protocol

Use when a path, identifier, ownership boundary, or canonical source changes.

1. Inventory inbound links, activation rows, manifests, imports, installers,
   generated copies, and external managed entries.
2. Run `scan_consistency.py plan --operation move` with both identities. The
   changed scan uses Git rename detection to retain the old/new relationship.
3. Preview old and new identities and obtain explicit approval.
4. Preserve Git history with a real move when possible.
5. Decide whether a temporary compatibility alias is needed.
6. Update all authoritative references and regenerate derived artifacts.
7. Reclassify moved Markdown under [[docs/05_COLOR_LAYERS]], update the
   canonical query when required, and run `python3 scripts/graph_layers.py --check`.
8. Verify through the changed and staged scans that the old route is inactive
   and no graph or registry orphan exists.
9. Report compatibility, rollback, and any alias-removal date or condition.
