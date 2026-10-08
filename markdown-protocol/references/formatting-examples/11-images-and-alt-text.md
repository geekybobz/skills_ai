# Images and Alternative Text

**Purpose:** Add a visual while preserving an explanation for readers who
cannot view it.

**Portability:** Core syntax; supported file types vary.

## Source

```markdown
![A flow from input through validation to output](assets/workflow.png)
```

## Result

The image is loaded from a relative path and the bracketed text describes its
meaning.

## Avoid

Do not use `image` or a filename as alternative text. Do not place essential
facts only inside the image.

## Fallback

Follow the image with a short textual description or relationship list.

---

[← Previous](10-comments-and-generated-banners.md) · [⌂ Home](../markdown-patterns.md) · [Next →](12-mermaid-diagrams.md)
