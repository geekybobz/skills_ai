# Add Protocol

Use for a new canonical file, route, skill, component, adapter, script, test, or
document.

This card does not apply to the plan-only idea path
`workbench/plans/<skill-name>/plan.md`. Promotion begins only when the user
explicitly requests implementation or creation of `SKILL.md`.

1. Search for an existing equivalent and identify the canonical location.
2. Classify the addition as registry metadata, skill source, governance,
   runtime, adapter, generated output, or external integration. For Markdown,
   also assign its [[docs/05_COLOR_LAYERS|graph layer]].
3. Run `scan_consistency.py plan --operation add` on the primary path. An
   unmapped path blocks until its role is added to `CONTRACT.json`.
4. Use the computed impact closure to declare the new paths and any generated
   or installed consumers. Do not make the user discover them manually.
5. New routable skills start `manual` unless the user approves another state.
6. Require every new Markdown path to match a canonical graph colour query.
   A new user-visible machine concept also requires one visible Markdown entry
   and declared inbound/outbound graph links. Do not duplicate skill bodies.
7. Compile the manifest after routing-source changes.
8. Validate links, paths, graph layers, selection behavior, token load, and
   focused tests. Run `python3 orchestrator/tools/graph_layers.py --check` for Markdown
   and write the new source's explanation under its `## Details` or depth topic.
9. Run the changed and staged consistency scans. Report why the addition exists
   and what was deliberately left unchanged.

A new family, persistent hook, network service, dependency, credential path, or
external installation requires a [[SCOPE_EXPANSION]] report if it was not named
in the request.
