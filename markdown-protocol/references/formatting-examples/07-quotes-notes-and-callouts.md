# Quotes, Notes, and Callouts

**Purpose:** Distinguish quoted material or a short aside from the main prose.

**Portability:** Block quotes are Core. Styled callouts are platform-specific.

## Portable source

```markdown
> This is a quotation or visually separated note.
```

## Obsidian enhancement

```markdown
> [!warning] Important limitation
> This feature depends on the Obsidian renderer.
```

## Avoid

Do not place most of a document inside callouts. Do not depend on callout color
or icon to communicate severity.

## Fallback

Use a normal heading such as `### Warning` followed by plain text.
