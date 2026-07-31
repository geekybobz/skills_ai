# Update And Migration Protocol

Use for a public contract, schema, dependency, runtime protocol, installer,
generated representation, or persistent-state change.

1. Record the old contract, new contract, motivation, and affected consumers.
2. Separate shared runtime behavior from Codex- and Claude-specific lifecycle.
3. Preserve compatibility when practical; otherwise document the break.
4. Preview state or configuration migration and provide rollback.
5. Do not remove old persistent state during the first migration phase unless
   the user explicitly authorizes its exact deletion.
6. Test the shared contract first, then each affected platform separately.
7. Update build, API, protocol, installation, and troubleshooting documents.
8. Commit migration context and measured verification, not only file names.

An unexpected consumer, external path, destructive cleanup, or wider refactor
uses [[SCOPE_EXPANSION]] before work continues.
