# Registration transfer source boundary, revision 1

Status: source preparation implemented; Platform intake, acceptance reconciliation
and Platform-directed execution are still required. This is not full RF02 closure.

A legacy Supervisor registry may be frozen for one explicit request ID and target
Platform installation. The source retains every original registration UUID and
revision. Its current declarations and optional resident-selection index are
hashed together, and the original control-history head is recorded. The source
freeze marker, history event and persistent storage fences commit atomically.
Retrying the exact request returns the original cut; changing its target or ID
is refused. An empty or inconsistent registration/index source is refused.

The SQLite adapter seals these key prefixes in both entity and control-projection
tables: `components/registration/`, `components/resident-selections`, and
`components/registry-freeze`. Insert, update and delete are refused. The seal list
itself cannot be updated or deleted through ordinary SQL DML. There is no unseal
method. Only a sealed database is promoted to reader schema 7; ordinary databases
remain at schema 6. Schema-6 binaries refuse the sealed database. Reopening with
new code verifies the expected guard definitions and seal list.

Source declaration/retirement writes, new local assignments, resume permits and
new work commits are blocked while frozen. Existing execution observations,
investigation/disposition records and historical result queries remain separate
and may continue. Original history export stops at the frozen cursor, so later
observations do not silently change the import cut.

The local freeze result says PERMANENTLY_FROZEN / NOT_ESTABLISHED /
NOT_TRANSFERRED for local declaration writer, P acceptance and process ownership.
A serialized export is not remote attestation. A target receiver must verify the
registered source boundary itself; an uploaded JSON `sealed` claim is insufficient.
P must preserve original IDs/revisions/history, record its acceptance with the
original request, and reconcile response loss before enabling its authoritative
path. It must also connect content acceptance and execution assignment.

This preparation requires the source repository's exclusive writer lock. It does
not acquire or adopt a live process by PID, revoke physical authority, or prove
functional safety. Arbitrary privileged schema edits, copying an older database
back over the source, and whole-installation rollback are not solved by this
per-file fence. Those require the framework's separate upgrade/restore contract.

Compatibility: schema 7 is opt-in and refuses downgrade. No frozen base/cell
protobuf or manifest changes. The SDK copies the storage implementation from
Platform. The local Supervisor view adds declaration_authority separately from
its recovery/readiness/work-use axes. The new development CLI is not automatically
invoked or installed by the existing installer.
