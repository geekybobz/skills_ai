# Mathematical Expressions

**Purpose:** Preserve readable mathematical notation in Markdown.

**Portability:** Render-dependent.

**Verification status:** Pending comparison in the intended renderers.

## Candidate source forms

Do not select a house style until these forms have been rendered and compared:

```text
Inline candidate: $E = mc^2$
Inline candidate: \(E = mc^2\)

Display candidate:
$$
E = mc^2
$$

Display candidate:
\[
E = mc^2
\]
```

Some applications accept only part of this syntax, and source that renders in
one Markdown viewer may remain literal in another.

## Temporary dependable form

Until verification is complete, keep the LaTeX copyable in a fenced block and
state its meaning in prose:

```latex
E = mc^2
```

The equation states that energy equals mass multiplied by the square of the
speed of light.

## Later verification

Test at least inline and display equations, subscripts, superscripts, fractions,
aligned multi-line equations, labels, and references in each intended viewer.
Record the exact application, version, syntax, and observed result.
