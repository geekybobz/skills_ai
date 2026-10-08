# VS Code Setup

Use this pack to reproduce the Markdown Protocol editing experience without
making the skill depend on one editor.

## In brief

Open `markdown-protocol/` as the VS Code workspace. Its `.vscode/` directory
recommends Markdown Preview Enhanced and markdownlint, then applies local
validation, link-update prompting, live synchronized preview, KaTeX, portable
relative links, and disabled preview-script execution.

VS Code does not accept repository-owned keybindings. Before changing personal
shortcuts, back up User `keybindings.json`, then merge only the entries needed
from [`assets/vscode/keybindings.jsonc`](../assets/vscode/keybindings.jsonc).
Never replace an existing keybinding file wholesale.

## Installation

1. Clone or download the package.
2. Open the `markdown-protocol/` folder directly in VS Code. If it is nested in
   a larger repository, the parent workspace does not inherit this folder's
   `.vscode/` settings.
3. Review and accept the two extension recommendations. Recommendations do not
   install anything automatically.
4. Open **Preferences: Open Keyboard Shortcuts (JSON)** from the Command
   Palette, make a backup, and merge the template entries.
5. Run **Developer: Reload Window**.
6. Open the [renderer fixture](formatting-examples/20-renderer-verification-fixture.md)
   and check the preview before claiming that diagrams or equations render.

The unwanted recommendations prevent this package from suggesting the three
overlapping extensions removed from the reference setup. They do not uninstall
or disable software already chosen by the reader.

## Essential shortcuts

| macOS | Windows/Linux | action |
|---|---|---|
| `Command-Option-V` | `Ctrl-Alt-V` | Open Markdown Preview Enhanced beside Markdown; with the optional LaTeX entry, open the PDF beside `.tex` source |
| `Command-K`, then `V` | `Ctrl-K`, then `V` | Standard Markdown preview to the side |
| `Command-Shift-V` | `Ctrl-Shift-V` | Open preview in the current editor group |
| `Command-K`, then `Shift-L` | `Ctrl-K`, then `Shift-L` | Open a preview locked to the current file |
| `Command-K`, then `Command-Shift-L` | `Ctrl-K`, then `Ctrl-Shift-L` | Toggle preview lock |
| `Escape` in preview | `Escape` in preview | Toggle the preview table of contents |
| `Command-+`, `Command--`, `Command-0` | `Ctrl-+`, `Ctrl--`, `Ctrl-0` | Zoom in, zoom out, or reset preview zoom |
| `Command-Shift-P` | `Ctrl-Shift-P` | Open the Command Palette when a shortcut is forgotten |
| `Command-P` | `Ctrl-P` | Open a file quickly by name |

With LaTeX Workshop, `Command-Option-J` / `Ctrl-Alt-J` performs source-to-PDF
forward synchronization. The reference macOS setup uses a double-click in the
PDF for reverse synchronization.

## Verification

- Markdown and preview remain visible side by side.
- Editing the source updates the preview and synchronized scrolling works.
- `Command-K V` remains available as a fallback.
- `.tex` and Markdown may share `Command-Option-V` because their `when`
  conditions are disjoint.
- `$...$` and `$$...$$` pass the renderer fixture before becoming a project
  guarantee.
- A wide Mermaid diagram is split or moved to a dedicated page when zooming no
  longer keeps the labels readable.

An `.Rmd` file is a separate case: Markdown Preview Enhanced can show its
Markdown layer, but true rendering also executes R code and requires an R or
Quarto workflow. Do not present a static preview as a rendered analysis.

## Details

### Ownership and portability

The package settings own the reference workspace behavior. User keybindings
remain personal state, so the package supplies a mergeable template rather
than an automatic installer. Markdown content remains readable without either
extension; the extensions improve editing and verification only.

When this package is copied into its own repository, keep `.vscode/` at that
repository root. When it remains inside a larger repository, either open the
package folder directly or copy the reviewed settings to the parent workspace.

---

[⌂ Home](../INDEX.md)
