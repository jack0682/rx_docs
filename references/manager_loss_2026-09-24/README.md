# Manager-loss recovery evidence — 2026-09-24

Implementation: [rx-solutions f3a7d08c](https://github.com/jack0682/rx-solutions/commit/f3a7d08c53f71d481a9a06ecbe9597cf2e9e1274), [PR 31](https://github.com/jack0682/rx-solutions/pull/31). The claim is scoped kernel evidence about the original direct process after actual manager loss, followed by explicit new-run resume. It is not original outcome recovery, PID adoption, descendant/resource handover, cross-namespace recovery or physical qualification.

## Probes and the retained counterexample

[Initial exposure](identity-exposure.txt) records the product posture and the actual manager/child lifetime probe. [Product clone3 refusal](product-clone3-denied.txt) is ENOSYS under CapEff0. [Controlled reuse](initial-controlled-reuse.txt) separately establishes two actual PID100 generations with different start ticks using CAP_CHECKPOINT_RESTORE and seccomp unconfined. This privilege creates a counterexample, not a product enforcement/recovery mechanism. [Concurrent namespace observations](concurrent-namespace-probe.json) show simultaneous containers with PID1 but different namespaces.

The first integrated passage was **FAIL**, not acceptance: [retained assertion](retained-namespace-failure.txt), [misclassified foreign observation](retained-foreign-misclassification.json). Its [same-namespace subscene](initial-same-namespace-scene.json) had passed, but that subscene's PASS is not the overall passage verdict. Sequential container replacement reused the namespace inode numbers and proc mount identity. The provider initially accepted a scoped absence in a different namespace lifetime. This led to recording PID1 birth and time offsets with double coherent reads. Init-birth matching raises confidence, not a permanent namespace UUID; lifetime inference cannot replace an observation of the saved process.

## Actual runtime, ordinary posture

[Manager result](manager-result.json), [exact commands](manager-commands.json), and [scene output](manager-scene.txt) identify the runtime/builder and binary hashes. The separate PID1 observer killed the actual manager, preserving its live child and namespace. A new manager refused [live resume](live-resume-refusal.txt). After fixture-only cleanup through a pre-loss pidfd and reap, RX observed scoped absence, recorded a confirmed disposition, and started a new run/instance with the same registration. The original observation remained UNKNOWN and past outcome UNRESOLVED.

[Unknown-run refusal](unknown-run-refusal.txt) creates no nested store, and [consumed resume refusal](consumed-resume-refusal.txt) prevents another execution. The resulting store list has one root registration.db, preserved original supervisor.db and one explicit runs/RUN/supervisor.db. [Sequential-container refusal](sequential-namespace-refusal.json) is now UNVERIFIABLE with saved-namespace-not-observable-in-current-scope. Replacing the container leaves that original record permanently unverifiable through this provider; an external witness would be a different, unsupported path.

## Actual PID reuse, separate counterexample posture

[Reuse result](actual-reuse-result.json), [commands](actual-reuse-commands.json), and [provider output](actual-reuse-investigation.json) record reuse of the **actual RX child's PID8**. The observer terminated/reaped that child, then clone3 set_tid assigned PID8 to a different live sleep process. Registry investigation returned scoped-pid-reused-different-starttime. The unrelated replacement stayed alive through explicit resume; RX neither adopted nor signalled it. The main passage ran under UID10001/CapEff0, while this distinct fixture used UID0, only CAP_CHECKPOINT_RESTORE and seccomp unconfined in its disposable private PID namespace.

Reproduce each from the contribution, with a fresh evidence directory:

```sh
python3 tools/manager_loss_passage.py \
  --image sha256:fcb56bfdfcc1f68bf8cfb6d28f7f24d5899f5e31030ee2a882f6e29e1e28b4a0 \
  --builder sha256:ff521445a372125ed4f76e1453a1f8098f2d05332d1601d30db1c1f62757e730 \
  --evidence /absolute/path/to/fresh-evidence
# Run separately with --pid-reuse-fixture and a different fresh evidence path.
```

The observer is a test fixture, not an added product daemon. No image was published, no host PID namespace was joined and no physical devices were attached.

## Regression and type boundary

[Summary](summary.json), [macOS workspace](macos-workspace.txt), and [four compile-rejection checks](compile-rejection-tests.txt) record 348/0/17 initially, then the fourth additional fingerprint-injection doctest passed. This is 349 unique current macOS cases, not 348+4. No ignore was added. [Exact-head Linux workspace CI](linux-workspace-ci.txt) passed **391/0/20**, with unchanged ignores ([run 35944730637](https://github.com/jack0682/rx-solutions/actions/runs/35944730637)). [macOS workspace clippy](macos-clippy.txt) and [Linux supervisor clippy](linux-clippy.txt) passed with warnings denied.

[Linux supervisor tests](linux-supervisor-tests.txt) passed 21 units, including genuine zombie then reaped absence, original-record lookup, no legacy backfill, namespace mismatch, every required scope dimension, coherent-scope races, process races and existing resource rollback tests. The [library passage](library-passage.txt) retained all 32 stages with [commands](library-commands.json). [Resident](resident-result.json) and [resource](resource-result.json) results retain their previous assertions, with [resource commands](resource-commands.json). These counts are scoped regressions, not complete framework qualification.

[Initial lint failure](retained-clippy-failure.txt) required boxing the opaque launch identity; no lint suppression was used. [An old limitation-text assertion](retained-old-limit-assertion.txt) initially expected the obsolete unsupported-provider wording and was updated to assert the permanent missing-birth-identity limitation. The negative behavior remains tested.

Strings, deserialized ProcessInvestigation, stored legacy references converted to proof, and caller-supplied fingerprints cannot compile into live evidence. The stored journal and OS remain trusted: this does not cryptographically authenticate truth against malicious DB/OS authors. Pre-F9 records without birth identity cannot be backfilled.

Only local path prefixes are normalized to `<workspace>`/`<user-home>`; substantive outputs are preserved. Full raw local logs and DBs remain retained; spent regenerable build folders are separate.
