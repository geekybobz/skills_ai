# Add Protocol

Use for a new canonical file, route, skill, component, adapter, script, test, or
document.

1. Search for an existing equivalent and identify the canonical location.
2. Classify the addition as registry metadata, skill source, governance,
   runtime, adapter, generated output, or external integration. For Markdown,
   also assign its [[docs/05_COLOR_LAYERS|graph layer]].
3. Declare the new paths and any generated or installed consumers.
4. New routable skills start `manual` unless the user approves another state.
5. Require every new Markdown path to match a canonical graph colour query.
   Add activation, risk, hub, API, or build documentation only when the new
   contract requires it; do not duplicate skill bodies in registry files.
6. Compile the manifest after routing-source changes.
7. Validate links, paths, graph layers, selection behavior, token load, and
   focused tests. Run `python3 scripts/graph_layers.py --check` for Markdown
   and update every human page mapped from the new canonical source.
8. Report why the addition exists and what was deliberately left unchanged.

A new family, persistent hook, network service, dependency, credential path, or
external installation requires a [[SCOPE_EXPANSION]] report if it was not named
in the request.
