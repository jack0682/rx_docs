# P restart adoption after decision A — live image runs

2026-09-29. The live image scenario `--binding-commit --restart-platform` restarts P after the Host binding change is fenced, then asks a ReleaseManager to adopt the previous runtime's binding requests. Before decision A it stopped at adoption (`409 QUALIFICATION_REQUIRED`, with `REVIEW_NO_LONGER_APPROVED`), because every P start drew a new package-intake generation and a new package Store owner.

With rx-platform c70af0d (decision A: persistent Store owner and generation reuse while the Store owner, policy fingerprint and policy file are unchanged), two consecutive runs gave the same result ([checks.json](checks.json)):

1. The old-runtime requests are reported, refresh without adoption is refused, and adoption without the ReleaseManager role is refused (403).
2. **Adoption by the ReleaseManager is accepted**, keeping the original request and baseline.
3. The run then waits up to 30 s for the Host's operating context to become `CURRENT` and fails with `IDENTITY_UNAVAILABLE` ([run-1.log](run-1.log), [run-2.log](run-2.log)).

After the restart, P logged `Unauthenticated` at `BOOTSTRAP` and then `ContinuityUnproven` at `PREPARE_LINK` ([run-2-platform-after-restart.log](run-2-platform-after-restart.log)).

## Finding

The Host was not restarted: it keeps its boot and journals and opens a new producer session with the new P runtime. The operating HostRegistration stays bound to the old session. This is by design in rx-platform `PRODUCER_RUNTIME_RECONNECT.md`, and it is stated as not verified in `tools/HOST_RECONNECT_TEST.md`.

Link preparation refuses a registration of the same boot with a different producer session (`engine/host_link.rs`). Host re-admission covers only a different boot (`host_readmission::covers` requires `host_boot != previous_boot`). The existing Host recovery flow (context → proposal → approval) reaches recovery-only progress and changes no grant or registration.

**develop therefore has no path for a retained Host to regain an operating registration after a P restart.** Decision A removed the first blocker. This is the next one, and it applies to every P restart with a retained Host, not only to binding changes.

## Scope

- Sources: rx-platform c70af0d; the binding Host image was built from rx-solutions 1857da4. rx-solutions changes since then touch only the JTC refusal order and the SDK copy, not the Python Host path used here.
- The command was reconstructed from the scenario's arguments and the retained fixture packages; the evidence JSON was not written because both runs stopped at the assertion.
- No physical equipment was operated.
