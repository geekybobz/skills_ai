# Scope Expansion Protocol

Unexpected work is reported, not silently absorbed.

```text
Scope-expansion request

Original request:
Current authorized scope:
Problem discovered:
Why additional work is needed:
Proposed actions:
Exact files or external locations:
Behavior or data affected:
Risks and rollback:
Tests or rechecks required:
Protocol or documentation impact:
What happens if this is declined:
Permission requested:
```

Complete safe in-scope work first when possible. If expansion is necessary for
correctness, stop at the boundary. Approval covers only the listed expansion;
a later expansion needs another report. Never label unrelated cleanup or a
contract change as a minor implementation detail.

After approval, rerun `scan_consistency.py plan` with the expanded paths. The
previous receipt does not silently authorize or classify the new scope.
