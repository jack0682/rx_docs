# Configured-source target registration intake

2026-10-01. [Source identities and preserved reader](scope.json) identify clean
Platform `644f63b` and Solutions `d0108aa` commits. [Result](result.json) records
an actual Supervisor API update/freeze on a private copy of the quiescent R4
registry, followed by P intake through the authenticated in-process HTTP router
and authoritative application writer. Original source inventory is unchanged.

The scene imports two original UUIDs at revisions 2 and 1 and exactly 14 source
events without a Cell. The final target acceptance commits before an injected
response loss. The source is then moved offline; exact POST retry recovers the
original receipt. Every P component declaration/revision and paged original event
matches the S source. The preserved schema-7 reader refuses the target schema-8
database. Missing, symlink, hard-link and unsealed sources are refused; missing
sources are not created and unsealed source bytes are unchanged. Unauthorized and
forged `sealed` input requests are also refused. See [scene output](actual-intake.log).

This exercises the real router and writer in a test process on macOS, not an
external TLS socket, a Linux target-intake daemon scene or physical equipment.
The R4 data originated on Ubuntu arm64; that does not make this test a Linux run.

[Local checks](local-checks.json): Platform 521 passed / 0 failed / 19 ignored;
Solutions 422 passed / 0 failed / 19 ignored. Both full workspace/all-targets/
all-features clippy checks passed. Repository tests, contract hashes, invariant
references, engine boundaries, SDK export regression and 126-file cross-repository
SDK comparison passed. No known engine seam was added. Full [P test](platform-test.log),
[S test](solutions-test.log), [P lint](platform-clippy.log) and
[S lint](solutions-clippy.log) logs retain command output with local path prefixes
redacted. The cross-repository scene is separately run despite being CI-ignored.

The added counterexample initially failed: [diagnostic alias could be recreated
during staging](alias-negative-before.log). The existing report issuance and
continuation writer now checks the imported canonical identity. [Six focused
tests](focused-after.log) pass, including explicit alias revocation then canonical
reporting, current-authority revocation before cached receipt access, ID collision,
inconsistent history, partial-stage restart, rollback and lost acceptance ACK.
Source documents resembling target control objects remain opaque archived data.

Reproduction (with this workspace's corresponding paths and Rust toolchain):

```sh
python3 tools/test_registration_intake.py \
  --solutions PATH_TO_SOLUTIONS \
  --source-scene PATH_TO_COMPLETED_R4_DAEMON_SCENE \
  --prior-reader PATH_TO_PRESERVED_SCHEMA7_READER \
  --platform-target PRIVATE_PLATFORM_TARGET \
  --solutions-target PRIVATE_SOLUTIONS_TARGET \
  --evidence NEW_EVIDENCE_DIRECTORY
```

The prior reader requires its adjacent `source.json` with original source commit,
reader-format maximum and matching SHA-256. Never rebuild that reader from the
new SDK. The runner copies source data inside the test; it does not migrate a
live installation. Completed source data and the preserved prior binary are
external prerequisites, not embedded in the repository.

Limits: S has not acknowledged P acceptance, content verification remains
NOT_ESTABLISHED, execution ownership remains NOT_ESTABLISHED_BY_REGISTRATION and
work use remains NOT_EVALUATED. No P execution assignment or process adoption is
performed. Receiving transfers with inconsistent source data stay unusable and
have no implicit abort/rebind/unseal. Privileged whole-file restoration and hostile
parent-directory replacement remain outside this local source trust boundary.
R5/RF02 and the full framework goal remain unfinished.


## Linux CI and integration

[Platform Linux CI](platform-linux-ci.json) passed 522 tests, zero failures and
19 ignored. [Solutions Linux CI](solutions-linux-ci.json) passed 467, zero failures
and 22 ignored, including successful installed-skill checks on Ubuntu amd64 and
arm64. These jobs do not execute the separately ignored target-intake scene.

[Integration](integration.json) records docs #80, Platform #66 and Solutions #75
merged in that order after required CI/DCO, with verified OpenPGP/author-signoff
merges. The tested and integrated code trees match and all 126 SDK files match.
This closes the target-intake slice; S acceptance reconciliation, execution
assignment, content verification and the complete resident model remain open.
The local log hashes identify original output before path-prefix redaction.
