# R3 scoped resident reporting evidence

2026-10-01, macOS arm64. The clean implementation commits in [scope.json](scope.json)
were exercised by Platform's `tools/test_resident_reporting.py` with a separately
built Solutions `rx-resident-report-fixture`. [result.json](result.json) contains
actual Running and Exited/0 receipts for one locally approved status child, with
the original S registration/run/instance preserved. The first publish response
was deliberately lost after commit; explicit same-key recovery returned the
original receipt. TLS material and private keys are not retained here.

The fixed clock in this test is intentional. Receipt acceptance time is not a
process observation timestamp. This is a real OS child and actual mTLS transport
on macOS, with no physical equipment or Platform-directed launch.

## Validation

- Platform workspace/all-features: 507 passed, 0 failed, 17 ignored at the prior
  test cut. After strengthening restart controls and adding rollback/current-role
  coverage, all 5 reporting engine tests passed. The final mTLS suite passed 1
  test with the cross-repository case separately exercised below.
- Solutions workspace/all-features: 413 passed, 0 failed, 19 ignored.
- Both complete workspace/all-targets/all-features clippy checks passed.
- Separate actual-reporting case: 1 passed; snapshots and scope are retained.
- Repository check/tests, frozen contract baselines, 8 optional binding checks,
  generator/export regression and 124-file SDK comparison passed. These are
  structural/copy checks and do not establish semantic coverage.

Logs are retained beside this file. Early fixture attempts failed on an omitted
explicit empty execution-requirements declaration; the fixture was fixed without
relaxing production admission. A generator test initially expected 9 proto files;
the new optional service makes 10, and byte-for-byte regeneration then passed.

No automatic shipped-daemon report loop, durable reporting outbox, old-instance
reconciliation, content verification, registration writer migration, P-directed
launch, Linux cross-repository passage, long-running soak or physical qualification
is established here. RF02 and the full resident framework remain open.

## Linux CI and integration

[Platform CI](platform-linux-ci.json) records 509 passed / 0 failed / 17 ignored;
[Solutions CI](solutions-linux-ci.json) records 458 passed / 0 failed / 22 ignored.
Both required PR CI aggregates and DCO passed. Solutions installed release jobs
passed on Ubuntu amd64 and arm64. These are existing installed-skill regressions,
not an automatically connected resident reporter daemon. The separate S/P child
passage above remains macOS evidence.

Documentation PR 74, Platform PR 63 and Solutions PR 72 were merged into develop
through the repository merge helper, with verified OpenPGP merge signatures and
matching author DCO. Exact integration commits and workflow links are in the JSON
records. The integrated product trees match the exercised feature trees, and the
124-file SDK comparison passed again after integration.
