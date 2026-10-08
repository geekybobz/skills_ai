# Portable Links

**Purpose:** Keep navigation usable in VS Code, GitHub, and plain Markdown
tools without maintaining an application-specific link layer.

**Portability:** Core.

Use ordinary relative Markdown links:

```markdown
[Topic](../topics/topic.md)
[Exact section](../topics/topic.md#exact-section)
```

Prefer these links over application-specific wiki links or embeds. If a named
tool generates a graph from ordinary links, the graph is an optional view; the
links remain authoritative.

**Expected result:** selecting the label opens the relative file or section.

**Fallback:** the path remains visible and editable as ordinary Markdown.

**Maintenance risk:** file moves can break paths. Use VS Code's link-update
prompt and run `mdp verify` after moving files.

---

[← Previous](14-yaml-properties-and-tags.md) · [⌂ Home](../markdown-patterns.md) · [Next →](16-page-footer-navigation.md)
