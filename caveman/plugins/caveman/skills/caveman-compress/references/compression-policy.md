# Compression Policy

## Remove

- Articles and conversational filler.
- Pleasantries and hedging.
- Redundant phrases and repeated examples.
- Connective prose that does not carry logic.

## Preserve Exactly

- Fenced and indented code blocks, including comments and spacing.
- Inline code and text inside backticks.
- URLs, Markdown link targets, file paths, commands, and environment variables.
- Library, API, protocol, algorithm, project, person, and company names.
- Dates, version numbers, numeric values, and units.
- Markdown headings, frontmatter, list nesting, table structure, and numbering.

Do not remove, reorder, shorten, or simplify protected content. In mixed files,
compress prose only. When classification is uncertain, preserve source.

## Style

- Prefer short exact words.
- Use fragments when their order remains clear.
- Remove "you should", "make sure to", and "remember to".
- Merge bullets only when they are semantically identical.
- Keep one representative example for repeated patterns.

## Examples

Original:

> You should always make sure to run the test suite before pushing any changes
> to the main branch. This is important because it catches bugs early and
> prevents broken builds from reaching production.

Compressed:

> Run tests before push to main. Catch bugs early; prevent broken production deploys.

Original:

> The API gateway handles all incoming requests and routes them to the
> appropriate service. The authentication service manages sessions and JWT
> tokens.

Compressed:

> API gateway routes requests. Auth service manages sessions and JWT tokens.
