# R4 resident delivery evidence

2026-10-01. Clean source identities and exact exercised scope are in
[scope.json](scope.json). The separately built Supervisor fixture uses the same
Resident worker as rx-solutionsd, its actual SQLite journal and a real software
status child. The Platform side uses the real application writer and mTLS ingress.

[Normal delivery](result.json) recovers the first lost acknowledgement and reports
owned Exited/0. [Delayed reporting](result.json.outage.json) delays report RPCs,
stops the real local child, retains the undelivered terminal snapshot, then starts
a new reporting worker. Explicit owner continuation allows the same instance's
terminal snapshot to be delivered; no new process is created for that recovery.
This is diagnostic continuity, not adoption or physical completion.

Local macOS workspace tests: P 510 passed / 0 failed / 18 ignored; S 418 passed /
0 failed / 19 ignored before the final retained-history extension. After that
extension, six focused outbox tests passed, including discovery of an old run's
unsent snapshot, and complete S workspace clippy passed. Seven P reporting engine
tests cover scope sequencing, source identity, current credentials, revocation,
transaction rollback and P/reporter restart with owner-approved continuation.
The final two cross-repository scenes passed against the clean commits above.

Generation, frozen contract and optional binding checks and 124-file SDK source
comparison passed. These are structural/copy checks, not independent semantic
verification. Linux daemon entrypoint and PR CI evidence are pending and are not
claimed by these local results. Full process recovery, P launch assignment,
legacy registration writer migration, content intake and physical qualification
remain open.

## Final source and Linux CI

The final Solutions commit is `24c541f134b41e3f8f3b0e8e5b6d590574c068c4`;
Platform remains `4be79f3f56d21674ceff0c0b5ac18ef055c31cec`. The additional
same-sequence/different-receipt and store-generation guards require explicit
reconciliation. [Final scene sources](final/scope.json) and the two receipts/logs
in that directory supersede the initial scene as current-code evidence. Both
scenes passed again; local child stop during delayed reporting was 30ms in that
particular macOS run, not a timing guarantee. Seven focused outbox tests passed.

[Platform Linux CI](platform-linux-ci.json) and [Solutions Linux CI](solutions-linux-ci.json)
record the exact PR heads and job conclusions. Ubuntu installed-skill jobs passed
on amd64 and arm64; they are separate from the rx-solutionsd entrypoint scene.

## Actual Ubuntu daemon entrypoint

The [daemon scene](linux-daemon/result.json) passed on native arm64 Ubuntu 24.04.
The current full `Solutions.Dockerfile` runtime was built with the pinned BT.CPP
commit and DHI archives. Its real native installation audit passed for nine ELF
executables and their dynamic links. The runtime inventory was signed using the
existing encrypted development-key custody procedure; no trust root or execution
guard was changed. Public signed metadata, source commit, image ID and daemon
hash are retained in [release input](linux-daemon/release/input.json). Keys are
not included.

With reporting deliberately unconfigured, the real rx-solutionsd CLI started two
release-owned status services, their health endpoints responded, SIGTERM led to
normal daemon exit, and both Exited snapshots remained in the reporting SQLite
journal without accepted receipts. The test used a read-only root, user 10001,
no devices and no network; the daemon binary overlay exactly matched its signed
runtime inventory. This is an actual daemon entrypoint test, not an installed
systemd service or Linux mTLS integration claim.

The retained failed controls are part of the result: the earlier development
image was unsigned; an amd64-emulated fixture hit Rosetta mmap failure under the
existing address-space bound and preserved UNKNOWN; a minimal native fixture
lacked the required native-install audit and its children exited. These guards
were kept intact. The final test used the complete native image.

The online GitHub DHI archive bytes did not match the pinned archive hash. The
existing archived inputs did match, and preparation verified all 1797 files
against the current content-tree pins. Fresh online native-source reproducibility
therefore remains an installation concern; no hash was weakened to pass.

The native image build and status services do not close complete ROBOTIS bundle
qualification, physical operation, controller integration, or field maintenance.
