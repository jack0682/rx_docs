# Current-boot Host binding commit observation

2026-09-29. Optional Host configuration binding revision 2 adds current service installation identity and an optional committed-binding observation. The source manifest/hash and generated 118-file SDK were synchronized; frozen base/cell manifests remain unchanged.

The service binds its durable startup attempt to the actual Host boot before serving. A commit is exposed only when that boot, installation identity, semantic binding digest and retained journals match. Historical/stopped records and another boot with the same installation identity do not supply a current observation. The model rejects mismatched current identity, delivery journal, binding digest and cell. Legacy JSON without the fields decodes as unconfirmed.

Actual service tests recover the three SIGKILL commit boundaries, start the proposed configuration, establish mTLS and read the observation through HostConfigurationService. The returned proof names the original request/plan/journals; the wrong optional-binding hash is rejected. After normal stop, a direct read does not expose current commit evidence. Activation remains false.

[checks.json](checks.json) records scope/source IDs. Host full tests and P domain/application tests passed; API tests compiled; clippy, SDK export-integrity and repository checks passed. These are local service/mTLS tests, not a completed P deployment confirmation.

P must next persist its per-Host request/baseline before replacement, obtain a bounded authenticated read, and compare request/plan/before/after/cohort/current boot and journals before progressing. Missing, stale or human-uploaded JSON cannot stand in for that observation. HOST_BINDING_CHANGE_REQUIRED is still retained. No physical equipment was operated.
