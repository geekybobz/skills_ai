# Move And Rename Protocol

Use when a path, identifier, ownership boundary, or canonical source changes.

1. Inventory inbound links, activation rows, manifests, imports, installers,
   generated copies, and external managed entries.
2. Preview old and new identities and obtain explicit approval.
3. Preserve Git history with a real move when possible.
4. Decide whether a temporary compatibility alias is needed.
5. Update all authoritative references and regenerate derived artifacts.
6. Reclassify moved Markdown under [[docs/05_COLOR_LAYERS]], update the
   canonical query when required, and run `python3 scripts/graph_layers.py --check`.
7. Verify that the old route is inactive and no graph or registry orphan exists.
8. Report compatibility, rollback, and any alias-removal date or condition.
