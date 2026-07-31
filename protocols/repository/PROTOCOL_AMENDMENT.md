# Protocol Amendment

Use when evidence shows that a governance rule is missing, unsafe, ambiguous,
or inconsistent with implementation.

```text
Protocol-amendment proposal

Current protocol and version:
Observed gap and evidence:
Why the current rule is insufficient:
Proposed replacement:
Operations and platforms affected:
Compatibility impact:
New tests:
Migration and rollback:
Permission requested:
```

Do not silently rewrite a protocol while completing another task. Obtain
approval, update backlinks and validators, and prefer a separate commit so Git
history preserves the motivation. Recheck protocols after repeated exceptions,
source-of-truth conflicts, new irreversible actions, host-specific divergence,
or a validation gap.

An amendment requested from outside the Skills AI maintenance workspace first
uses [[EXTERNAL_CHANGE_REQUEST]]. The external task records the proposal but
does not edit this protocol directly.
