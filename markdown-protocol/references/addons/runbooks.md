# Runbooks Add-on

Use this add-on for repeatable operational procedures where skipped steps or
unchecked results can leave a system in an uncertain state. Do not use a
runbook for a one-off exploration or a conceptual tutorial.

## Outcome

An authorized operator can prepare, execute, verify, stop, and recover a
procedure without guessing what success looks like.

## Add-on declaration

| field | declaration |
|---|---|
| Trigger | Repeatable operational, release, recovery, migration, or maintenance procedures; not conceptual explanations or unapproved actions |
| Blocks | Purpose, authority, prerequisites, hazards, steps, verification, rollback, escalation, and evidence record |
| Layout variants | Short checklist or staged runbook with preparation, execution, and recovery sections |
| Generated views | Optional command/output transcript or checklist projection, always non-authoritative and sanitized |
| Checks | Preconditions, ordered steps, per-step verification, stop conditions, rollback feasibility, command accuracy, and secret hygiene |
| Composition | The operating system, service owner, and applicable safety or repository policy own permissions and technical authority |
| Boundaries | No implied authorization, destructive placeholder, secret capture, fabricated output, or claim that a checklist makes an unsafe action safe |

## Details

## Step model

Each material step has three parts:

\[
\text{Step completeness} = \text{Action} + \text{Expected result} + \text{Verification}
\]

Use a compact table for short procedures:

| # | action | expected result | verify | stop if |
|---:|---|---|---|---|
| 1 | exact bounded action | observable state | command, UI check, or artifact | unsafe or ambiguous state |

For longer procedures, give each step its own heading so commands, alternatives,
and evidence do not make the table unreadable.

## Runbook template

```markdown
# Procedure name

## In brief

Purpose, scope, and the successful end state.

## Authority and impact

- Required authorization:
- Systems and data affected:
- Expected interruption:

## Preconditions

- [ ] Backup, snapshot, or rollback path verified when applicable.
- [ ] Exact target and current state confirmed.
- [ ] Required access and dependencies available.

## Procedure

### 1. Short action name

**Action:** Exact command or UI operation with placeholders explained.

**Expected:** Observable result.

**Verify:** Independent check or artifact.

**Stop if:** Condition that makes continuation unsafe or ambiguous.

## Final verification

- [ ] Intended behavior works.
- [ ] Unrelated behavior remains healthy.
- [ ] Evidence or result location recorded without secrets.

## Rollback or recovery

Trigger, exact recovery route, and verification of the recovered state.

## Escalation

Who or what owner must decide when the stop condition cannot be resolved.
```

## Commands and evidence

- Prefer idempotent or read-only checks before mutation.
- Show placeholders as `<TARGET>` and define how to resolve them safely.
- Never put credentials, tokens, private keys, or sensitive output in examples.
- Quote only the output needed to recognize success or failure; label samples.
- State when a command is platform-, shell-, environment-, or version-specific.
- Keep an evidence record only when the owning process requires it, and state
  its retention and sanitization rules.

## Validation

- Scope, target, authority, impact, and prerequisites are explicit.
- Every material action has an expected result and a verification method.
- Destructive or irreversible actions have a recoverability check and an
  unambiguous target.
- Stop conditions occur before the unsafe continuation point.
- Rollback describes both the action and how to verify recovery.
- Sample output is visibly illustrative, never presented as an observed result.
- Commands were checked in the named environment or clearly marked unverified.
- The runbook does not grant permission to execute itself.

---

[⌂ Home](../../INDEX.md)
