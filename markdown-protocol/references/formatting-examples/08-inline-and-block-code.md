# Inline and Block Code

**Purpose:** Distinguish filenames, commands, configuration, and source code
from explanatory prose.

**Portability:** Core.

## Source

````markdown
Run `python example.py`.

```python
def square(value):
    return value * value
```
````

## Result

Single backticks format a short literal. Triple backticks preserve a block and
the language name enables syntax highlighting where supported.

## Avoid

Do not use screenshots for copyable code. Do not add a language name that does
not match the content.
