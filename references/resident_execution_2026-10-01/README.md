# P-assigned actual resident software execution

2026-10-01. [Sources](sources.json) identify clean Platform `26eed02` and
Solutions `9274e12` commits and every copied source file hash. The
[environment/scope](scope.json) pins builder/runtime image IDs. Each test runs
inside a non-root Ubuntu arm64 runtime with a read-only root, no added capabilities
and container-loopback-only networking. No physical device is attached.

The actual source-built `rx-solutionsd catalog` command verifies program content
from the signed runtime and emits the registry/release/catalog enrollment. P's
actual writer, owner HTTP router and separate Supervisor mTLS service then run:
owner registration/proposal -> source verification/preparation -> explicit owner
approval -> two real status processes with a dependency -> stop -> original result.
The source command runs through RegisteredSupervisor and OsProcesses, with
LinuxRlimit evidence for each process's authored address-space bound. That is a
virtual-address-space ceiling, not RSS availability, reservation or timing proof.

[Normal result](normal.json) and [log](normal.log) verify approval reply loss and
observation reply loss, original IDs, both processes ready, owner-requested stop,
recorded Exited and released P component claims. Wrong Observer/Host roles and
wrong registry enrollment are refused through actual TLS. Repeating the original
daemon assignment after exit fails and does not alter its source history.

[Outage result](outage.json) and [log](outage.log) delay/refuse P execution traffic
before authoritative handling. The owned S command receives a local stop signal;
children stop before network drain, while the original pending report and latest
Exited snapshot remain in its durable outbox. P keeps the unresolved component
claims. Its last recorded phase can still be Running: that is not current OS
liveness. Restarting the original assignment is refused and does not rewrite
source history. Recorded local stop durations are observations of these two scenes,
not general latency guarantees.

The P server here is the real application writer/HTTP/mTLS in a test process using
the real shared Linux boot clock. It is not a full platformd deployment. The
executed daemon is newly built source; its selected program content comes from
the existing signed runtime image. This is not a newly signed/shipped daemon
package or a new installer release. Verification trusts the enrolled Supervisor,
installed verifier and OS; it does not independently attest the remote OS.

[Local checks](local-checks.json) record macOS P 529 passed / 0 failed / 19 ignored
and S 425 passed / 0 failed / 19 ignored, full workspace clippy/format and
repository/contract/SDK checks. The new actual Linux tests are cfg-Linux and
explicitly ignored in ordinary workspace CI; their separate execution above is
required evidence. Local log hashes refer to output before path redaction.

Targeted tests cover atomic approval/claims/results, role/session separation,
old ordinary sessions after a Supervisor-role change, imported registry/cut
identity, P restart holding old claims, unknown outcome retention, finite grant
windows, exact launch identity, single-use local owner consumption, prevention of
history overwrite by another manager, and monotonic reader-format 9 promotion.
An already consumed grant does not become a new authority when a registry or
execution manager is reopened.

The existing clean-source intake/acknowledgement and actual reporting regressions
also pass: [intake](intake-result.json), [intake source scope](intake-scope.json),
[reporting](reporting-result.json), [outage/reapproval](reporting-result.json.outage.json)
and [reporting source scope](reporting-scope.json). These remain distinct scopes.

Reproduction: run `tools/test_resident_execution.py --help` from Platform, supplying
the paired Solutions checkout, private target/evidence directories, a local Cargo
registry cache, compatible Linux builder image and signed runtime image. The
runner records private source inventories and runs the two exact scenes in separate
containers. Root filesystem content is immutable; task-owned state is temporary.

Remaining obligations are explicit: no business-work permission or physical
completion, no active-unknown automatic recovery, no whole-state rollback proof,
no complete framework-wide resource bundles/functional dependencies, no general
live replacement, no arbitrary author package extension and no new paired
installer release. R6 is a concrete execution connection; RF01–RF14 is not closed.

## Develop integration

[Platform #68](https://github.com/jack0682/rx-platform/pull/68) and
[Solutions #77](https://github.com/jack0682/rx-solutions/pull/77) are merged after
the exact PR CI and DCO passed. Linux workspace results are P 530 passed / 0 failed /
21 ignored and S 470 passed / 0 failed / 22 ignored; S installed-skill checks pass
for amd64 and arm64. These do not replace the separately executed Linux scenes above.

The [integration record](integration.json) identifies merge commits, verified
OpenPGP/author DCO, matching CI-head trees and 130 synchronized SDK files. P's
runtime-tested source differs from its integrated tree only in the client-preparation
test: the expected IDL count is 11 and the new execution proto must be present.
Full generated-byte equality remains checked. No runtime code differs. S's entire
runtime-tested tree equals its integrated tree. No new installer was released.
