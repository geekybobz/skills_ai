---
name: caveman-compress
description: >
  Compress natural-language memory files while preserving code, links, paths,
  and structure. Use for /caveman-compress FILEPATH, "compress memory file",
  or shrinking CLAUDE.md. Overwrites the target only after verifying a
  FILE.original.md backup. Never use on secrets or code/config files.
---

# Caveman Compress

## Process

1. Confirm the exact target path. Refuse secrets, credentials, private-key
   paths, existing `.original.md` files, and existing backup collisions.
2. From this skill directory run:

```bash
python3 -m scripts <absolute_filepath>
```

3. The script detects file type, calls Claude once, verifies preserved regions,
   and applies at most two targeted repair attempts.
4. Report the compressed path, backup path, and validation result.

## Invariants

- Compress only `.md`, `.txt`, `.rst`, `.typ`, `.typst`, `.tex`, or
  extensionless natural language.
- Never compress code, config, `.env`, lock, markup, SQL, or shell files.
- Preserve fenced and indented code, inline code, URLs, paths, commands,
  technical names, numbers, headings, frontmatter, and list/table structure.
- If unsure whether text is prose, leave it unchanged.
- Write `<stem>.original.md` and verify its bytes before replacing the target.
- Restore the original and remove the new backup if validation cannot pass.

The script is execution authority. Read
[references/compression-policy.md](references/compression-policy.md) only when
auditing policy, repairing the compressor, or manually evaluating an output.
