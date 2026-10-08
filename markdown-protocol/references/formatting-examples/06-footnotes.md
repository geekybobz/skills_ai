# Footnotes

**Purpose:** Keep a short qualification or citation near a statement without
interrupting its main sentence.

**Portability:** Common; not part of every minimal Markdown renderer.

## Source

```markdown
The result depends on the stated assumptions.[^assumptions]

[^assumptions]: These assumptions should remain short; use a linked note for a full discussion.
```

## Result

Supporting renderers create a numbered reference and a footnote at the bottom.

## Avoid

Do not hide essential reasoning or long explanations in footnotes.

## Fallback

Add a short `## Assumptions` section or link to a focused note.
