---
role: front-door
summary: Portable entry point for Markdown Protocol users and contributors.
read_when: Start here when installing, sharing, or browsing the package.
---

# Markdown Protocol

Markdown Protocol keeps one linked documentation structure compact at its
edge and explanatory at depth. It includes a Codex skill, human learning
guides, a deterministic `mdp` command, and a reproducible macOS VS Code pack.

## Start here

- Models and agents: [skill entry](SKILL.md)
- Human readers: [topic index](INDEX.md)
- New collection: `mdp init my-notes --title "My notes"`
- Existing collection: `mdp status .`, then `mdp adopt .`
- Normal verification: `mdp verify .`

Install from a clone with `python3 -m pip install .`, or use an isolated tool
manager with `uv tool install .`. The package has no runtime dependencies
outside the Python standard library. Run `mdp doctor .` after installation.
Updates are never checked in the background: run `mdp update check` explicitly,
or watch GitHub Releases for notifications.

## Editor setup

Import [`markdown-protocol-macos.code-profile`](assets/vscode/markdown-protocol-macos.code-profile)
through **Profiles: Import Profile**, or follow the auditable manual path in
[VS Code Setup](references/vscode-setup.md). Both preserve the agreed
`Command-Option-V` side-by-side preview behavior.

## Boundaries

The checker validates structure, navigation, and declared protocol metadata.
It does not prove factual correctness or silently rewrite a collection. `fix`
is a dry run unless `--apply` is supplied.

---

[⌂ Home](README.md) · [Topic index](INDEX.md)
