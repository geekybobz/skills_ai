# Markdown Protocol Pilot

## In brief

The Markdown Protocol package is its own first real pilot. It exercises a
compact model entry, a human route map, focused references, optional deep
sections, add-ons, portable navigation, a renderer fixture, and deterministic
checks without maintaining separate human and machine copies.

## Pilot questions

| question | evidence |
|---|---|
| Can a model start compactly? | `SKILL.md` routes to only the reference needed for the task. |
| Can a new reader orient without knowing the tree? | `INDEX.md` routes by intention and maps the package. |
| Is explanatory depth optional? | Core rules remain above `## Details`; deeper explanations remain linked. |
| Is each fact maintained once? | Outer layers summarize and link to the focused owner. |
| Can a reader move reliably? | Authored pages use relative links and a final Home footer; intentional sequences add Previous and Next. |
| Are enhanced patterns dependable? | The gallery records documented, observed, pending, and fallback status separately. |
| Can the editor experience travel? | The package contains extension recommendations, workspace settings, lint policy, and a backup-first keybinding template. |

## Findings

- The single layered structure works better than parallel human and machine
  documents: compact entry points and deeper explanations share one ownership
  graph.
- The package is still usable as ordinary Markdown when VS Code extensions are
  absent.
- Side-by-side preview materially improves editing, but user keybindings cannot
  be imposed by a repository and therefore remain an explicit merge step.
- Mermaid and mathematics need a recorded renderer pass. Documented support is
  not reported as visual observation.
- A small core editor pack is easier to maintain than several overlapping
  preview extensions.
- Snippets are intentionally deferred until a later learning-resource design
  and are not part of this pilot.

## Acceptance record

| check | status |
|---|---|
| Package structure and links | pass: package checker and focused suite |
| Home and reciprocal sequence navigation | pass: focused suite |
| Compactness thresholds | pass: compact loading budget plus entry/topic inference in the package checker |
| Portable editor configuration parses | pass: focused suite |
| Permissive lint baseline | pass: 0 issues across 42 Markdown files with markdownlint-cli2 0.23.2 |
| VS Code visual renderer pass | pending macOS Computer Use permission or manual observation |
| GitHub hosted renderer pass | pending a hosted fixture observation |

The pending visual rows are honest residual verification, not failures of the
layered architecture. Update this record only from an actual rerun.

---

[⌂ Home](../INDEX.md)
