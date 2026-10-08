# Editor Folding

**Purpose:** Collapse source sections while editing without hiding information
from the rendered document.

**Portability:** Headings are Core; named region markers are VS Code-specific
editor comments.

## Heading folding

VS Code understands the Markdown heading hierarchy. Use its gutter controls or
fold commands to collapse a heading and its children.

```markdown
## Topic

Compact explanation.

### Optional derivation

Detailed derivation.
```

## Named region folding

Use a region only when the source contains a long maintenance block that does
not have a useful rendered heading:

```markdown
<!-- #region Repeated compatibility examples -->

Maintenance-oriented source content.

<!-- #endregion -->
```

VS Code hides the comments in preview and treats the enclosed source as a named
folding region. GitHub hides the comments but does not provide that source-editor
folding control.

## Avoid

Do not use source folding to replace `## Details`, collapsible rendered content,
or proper headings. A folded editor region changes only the editing view and
cannot become an information-architecture boundary.

## Fallback

Delete the region comments; the Markdown content remains unchanged.

---

[← Previous](16-page-footer-navigation.md) · [⌂ Home](../markdown-patterns.md) · [Next →](18-markmap-view.md)
