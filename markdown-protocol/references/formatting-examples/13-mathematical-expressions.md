# Mathematical Expressions

**Purpose:** Preserve readable mathematical notation in Markdown.

**Portability:** Render-dependent.

**Verification status:** `$...$` and `$$...$$` are documented for VS Code 1.141
built-in preview and GitHub Markdown. The VS Code visual pass remains pending.
VS Code uses KaTeX and GitHub uses MathJax, so this remains a provisional house
style until the exact fixture is observed in both targets.

## Provisional house style

Use single dollar delimiters for short inline mathematics:

```markdown
The energy is $E = mc^2$.
```

Use double dollar delimiters on separate lines for display mathematics:

```markdown
$$
\frac{d}{dx}x^n = n x^{n-1}
$$
```

For a multiline derivation to include in the visual pass:

```markdown
$$
\begin{aligned}
f(x) &= x^2, \\
f'(x) &= 2x.
\end{aligned}
$$
```

The first display states the power rule. The second gives a function and its
derivative. Keep this prose meaning when the equation is important.

## Unsupported baseline

Do not depend on `\label`, `\ref`, custom macro definitions, or a broad LaTeX
package set across both targets. State equation names and cross-references in
ordinary prose. When the intended renderer is unknown, use a copyable fenced
form and explain it:

```latex
E = mc^2
```

The equation states that energy equals mass multiplied by the square of the
speed of light.

## Reverification

After a renderer upgrade, recheck inline and display equations, subscripts,
superscripts, fractions, roots, sums, matrices, and aligned multiline equations
using the [renderer fixture](20-renderer-verification-fixture.md). Record the
target, version, syntax, result, fallback, and date.

---

[← Previous](12-mermaid-diagrams.md) · [⌂ Home](../markdown-patterns.md) · [Next →](14-yaml-properties-and-tags.md)
