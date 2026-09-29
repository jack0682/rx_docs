# Retained Host rebind after a P restart — live image runs

2026-09-29. Follow-up to [P restart adoption after decision A](../p_restart_adoption_2026-09-29/README.md), where adoption was accepted but the retained Host's context stayed `IDENTITY_UNAVAILABLE`.

rx-platform `feature/retained-host-rebind` lets an explicit ReleaseManager re-admission rebind a retained Host: `covers` accepts the same boot when the registered session is retired (of an earlier runtime), the link waits until the earlier runtime's grant has lapsed, and the Run/work conditions are rechecked when the approval is consumed. The scenario `--binding-commit --restart-platform` now approves that rebind after adoption.

**Results** ([checks.json](checks.json))

1. First run at 6a78074: the rebind, refresh and fence passed, then the binding commit stopped at `COMMIT_LINK` with `REVISION_CONFLICT` ([first-run-6a78074.failure.json](first-run-6a78074.failure.json)). An engine test reproduced it: the registration history was keyed by cell, host and boot, and replacing the rebound registration of the same boot again wrote the same key. The replaced session is now part of the key (7b36e69).
2. At 7b36e69, three consecutive runs passed ([live-api.json](live-api.json), [live-api-run2.json](live-api-run2.json), [live-api-run3.json](live-api-run3.json)): P restart → adoption → explicit rebind approval → Host context `CURRENT` → refresh and fence on the new runtime → binding re-admission → Host stop, prepare and commit → restart on the proposed startup → `METADATA_MATCHED` → apply → `APPLIED_UNQUALIFIED`.

3. Combined scenario at 7b36e69, one run, PASS ([live-api-combined-host-restart-before-commit.json](live-api-combined-host-restart-before-commit.json)): after the P restart, adoption and rebind, the Host is restarted without a commit before the binding commit (plain re-admission, `MISSING_COMMIT`, refused refresh, refused stale binding re-admission), then the binding re-admission naming the restarted generation completes the flow to `APPLIED_UNQUALIFIED`.

**Scope**

- Re-admission still restores no grant, Arm, qualification, permit or Run. Restart blocks stay latched; the DeviceRestart release path remains open ([비교표](../../docs/implementation/host_readmission_delta.md)).
- The binding Host image was built from rx-solutions 1857da4; later rx-solutions changes do not touch the Python Host path used here.
- No physical equipment was operated.
