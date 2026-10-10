# Update And Migration Protocol

Use for a public contract, schema, dependency, runtime protocol, installer,
generated representation, or persistent-state change.

1. Record the old contract, new contract, motivation, and affected consumers.
2. Run `scan_consistency.py plan --operation update` and reconcile its computed
   consumers with the migration record.
3. Separate shared runtime behavior from Codex- and Claude-specific lifecycle.
4. Preserve compatibility when practical; otherwise document the break.
5. Preview state or configuration migration and provide rollback.
6. Do not remove old persistent state during the first migration phase unless
   the user explicitly authorizes its exact deletion.
7. Test the shared contract first, then each affected platform separately.
8. Update build, API, protocol, installation and troubleshooting documents, and
   the explanation that sits with each changed rule, in the same staged change.
9. Run the changed and staged scans. Commit migration context and measured
   verification, not only file names. A change that moves a submodule pointer
   also follows [[GIT_GOVERNANCE]].

An unexpected consumer, external path, destructive cleanup, or wider refactor
uses [[SCOPE_EXPANSION]] before work continues.
