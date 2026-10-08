# VS Code Setup

Use this pack to reproduce the Markdown Protocol editing experience without
making the skill depend on one editor.

## In brief

Import the committed macOS profile for the closest replica of the reference
setup. It contains Markdown Preview Enhanced, markdownlint, LaTeX Workshop,
the agreed shortcuts, synchronized preview, KaTeX, safe preview settings, and
the LaTeX side-by-side settings. The repository also retains auditable source
JSON and workspace recommendations.

The one-step path is **Profiles: Import Profile** with
[`markdown-protocol-macos.code-profile`](../assets/vscode/markdown-protocol-macos.code-profile).
VS Code previews the imported categories before creating the profile. The
manual path remains backup-first: merge only the entries needed from
[`keybindings.json`](../assets/vscode/keybindings.json), never replace an
existing user file wholesale.

Before the manual path, back up User `keybindings.json` and `settings.json`.
Workspace recommendations do not install extensions automatically.

## Installation

1. Clone or download the package.
2. In VS Code, run **Profiles: Import Profile**, select the committed
   `.code-profile`, review Settings, Keyboard Shortcuts, and Extensions, then
   create the `Markdown Protocol macOS` profile.
3. Open the `markdown-protocol/` folder with that profile. VS Code remembers
   the folder association.
4. Install the `mdp` command and run the default **Markdown Protocol: Verify
   workspace** task once.
5. Open the [renderer fixture](formatting-examples/20-renderer-verification-fixture.md)
   and check the preview before claiming that diagrams or equations render.

The workspace's unwanted recommendations prevent this package from suggesting
three overlapping Markdown preview extensions. They never uninstall or disable
software already chosen by the reader.

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

The readable JSON files own the profile inputs. Regenerate the `.code-profile`
with `python3 scripts/build_vscode_profile.py --write` and verify it with
`--check`; do not hand-edit the escaped export. Markdown content remains
readable without the extensions; they improve editing and verification only.

When this package is copied into its own repository, keep `.vscode/` at that
repository root. When it remains inside a larger repository, either open the
package folder directly or copy the reviewed settings to the parent workspace.

VS Code Settings Sync can copy profiles between machines signed into the same
account. For friends or separate accounts, share this repository and import the
committed profile. Use GitHub's release-only Watch setting for notifications;
the package starts no updater, watcher, or telemetry process.

---

[⌂ Home](../INDEX.md)
