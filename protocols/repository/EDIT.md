# Edit Protocol

Use for a localized modification that preserves identity, schema, lifecycle,
installation, and public behavior.

1. Confirm the exact requested paths and inspect overlapping user changes.
2. Edit the canonical source; never hand-edit a generated mirror.
3. Preserve unrelated formatting, behavior, and user content.
4. Check `docs/human/_SOURCE_MAP.json`. If the edited source is mapped, update
   every listed human page in the same staged change.
5. Inspect the file-specific diff and run focused tests.
6. Report the behavioral effect and any unverified boundary.

Reclassify the work as [[UPDATE_MIGRATE]] when it changes routing, schemas,
protocols, dependencies, installers, persistent state, or platform contracts.
Editing protected skill collections still requires the explicit request required
by `AGENTS.md` and `docs/04_RISK_MAP.md`.
