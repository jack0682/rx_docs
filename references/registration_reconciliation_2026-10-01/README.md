# Supervisor acknowledgement of original target registration acceptance

2026-10-01. [Clean source identities](scope.json) are Platform `e91f869` and
Solutions `7020cbe`. [The integrated result](result.json) retains the source-copy
intake, prior-reader refusal and now the scoped mTLS reconciliation. The original
R4 source inventory remains unchanged. The working trees were clean for this run.

P's actual authenticated HTTP router/writer accepts the source copy, retaining two
UUIDs/revisions and 14 original events. Its target reply is deliberately lost and
recovered with the source offline. The copied source is restored, and a separate
actual S `rx-registration-transfer reconcile` process opens a new mTLS reporter
session. The owner grants a scope for an imported canonical component. Wrong
certificate, absent scope, wrong freeze ID and wrong binding are refused. A first
valid target-read response is deliberately lost; the S CLI repeats that same
scoped query, validates the original source cut, and records acceptance.

A second S CLI process has a different peer boot and requires a new owner scope.
The prior session's query is refused. The new authenticated observation preserves
the first stored acceptance, and the source contains exactly one local acceptance
event. Source inspect keeps the original frozen cut and explicitly reports
RECORDED_FROM_AUTHENTICATED_PLATFORM with NOT_TRANSFERRED process ownership.
This is actual TLS between processes on macOS; it is not a Linux daemon-intake
scene or an equipment run. [Scene log](actual-intake.log).

[Focused P tests](platform-focused.log) include current scope/authentication,
original acceptance after later declaration changes, scope revocation, reporter
replacement and P restart with rejection of the old peer followed by newly
approved access to the same original decision. [Focused S tests](solutions-focused.log)
cover wrong source/peer/scope/component data, source membership, atomic rollback,
reply loss after commit, reopen/idempotence, receipt-change refusal and continued
rejection of local declarations and execution assignment. Original frozen history
is unchanged and replay does not append another acceptance event.

[Local checks](local-checks.json): P 522 passed / 0 failed / 19 ignored;
S 423 passed / 0 failed / 19 ignored. Those full suites preceded the final P
restart assertion extension and S item-order lint fix; focused tests and full
clippy/format were rerun afterward. Repository/contract/binding/SDK checks passed,
with 126 generated files matching. Log hashes identify original local output
before workspace-path redaction. Source changes and counts are not full RF02 or
framework-completion evidence.

The binding change also passed the separate existing actual Supervisor child
reporting and reporting-worker outage/restart regressions with these clean sources:
[normal result](reporting-result.json), [outage result](reporting-result.json.outage.json),
[scope](reporting-scope.json), [normal log](reporting.log), [outage log](reporting-outage.log).
Their runner now selects the two exact tests it supplies inputs for, instead of
accidentally selecting the independent source-intake test by a broad name prefix.

Reproduce the intake/reconciliation with `tools/test_registration_intake.py`
and the existing R4 source scene plus the independently preserved schema-7 reader;
reproduce normal/outage reporting with `tools/test_resident_reporting.py`. Both
runners take explicit private target/evidence directories and the paired Solutions
checkout. See their `--help` and the previous [intake prerequisites](../registration_intake_2026-10-01/README.md).

Limits: optional reporting binding revision 3 requires paired P/S upgrade and
current scope approval. Source SQL format and fences are unchanged; there is no
unseal, local assignment restoration or receipt-JSON import. The stored evidence
is historical, not current process/authorization state. This development CLI is
not automatically installed or run by the shipped daemon. P-directed execution,
verified content, operational recovery, installer integration and RF01–RF14 remain
unfinished. No physical completion or functional-safety qualification is claimed.


## Linux CI and integration

[Platform Linux CI](platform-linux-ci.json) passed 523 tests, zero failures and
19 ignored. [Solutions Linux CI](solutions-linux-ci.json) passed 468, zero failures
and 22 ignored. Full lint and installed-skill jobs on Ubuntu amd64/arm64 passed.
Those installation jobs use their pinned P baseline and do not run the separately
ignored new reconciliation scene or establish a new paired installer release.

[Integration](integration.json) records docs #82, Platform #67 and Solutions #76
merged in that order after required CI/DCO and verified OpenPGP/signoff checks.
The tested and integrated code trees match, as do 126 SDK files. The final Linux
workspace runs include the final P restart assertions and S source layout.
This establishes explicit source acknowledgement, not P execution assignment,
verified program content, automatic migration or full framework completion.
