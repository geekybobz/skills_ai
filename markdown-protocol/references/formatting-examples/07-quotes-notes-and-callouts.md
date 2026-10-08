# Quotes, Notes, and Callouts

**Purpose:** Distinguish quoted material or a short aside from the main prose.

**Portability:** Block quotes are Core. Styled callouts are platform-specific.

## Portable source

```markdown
> This is a quotation or visually separated note.
```

## GitHub alert enhancement

```markdown
> [!WARNING]
> Important limitation stated explicitly in the text.
```

GitHub documents special alert styling. VS Code 1.141 built-in preview keeps
the source readable as a block quote but does not provide the same dependable
styling without an extension. Treat the wording, not its color or icon, as the
authoritative warning.

## Avoid

Do not place most of a document inside callouts. Do not depend on callout color
or icon to communicate severity.

## Fallback

Use a normal heading such as `### Warning` followed by plain text.

---

[← Previous](06-footnotes.md) · [⌂ Home](../markdown-patterns.md) · [Next →](08-inline-and-block-code.md)
