# Linux address-space enforcement evidence — 2026-09-24

Implementation: [rx-solutions fa8ea7e5](https://github.com/jack0682/rx-solutions/commit/fa8ea7e53076ede4bf76a838c7c26a70ffaa7647), [PR 30](https://github.com/jack0682/rx-solutions/pull/30). This is one per-process virtual-address-space ceiling, not physical RAM, capacity reservation, aggregate process-group enforcement or physical qualification.

## Selection and attribution

[Initial probe](attribution-probe.txt) measured UID 10001, CapEff 0, no-new-privileges, a read-only cgroup2 mount and EROFS on child-cgroup creation. The parent and baseline child had unlimited address space. A separately limited child showed soft/hard 67108864 bytes from its parent's `/proc` read and rejected a 134217728-byte mmap with ENOMEM; the parent's limits remained unchanged. This probe selected a mechanism; it is not itself production RX evidence.

[Status footprint](status-footprint.txt) measured startup VmPeak 52219904 bytes. The chosen 268435456-byte ceiling is approximately 5.14 times that measurement, and the actual release service returned health under it. This is a scoped engineering margin, not a workload-wide availability guarantee.

The source deliberately introduces `AddressSpaceBytes` instead of reinterpreting `MemoryBytes`. Semantics are grounded in the [Linux rlimit manual](https://man7.org/linux/man-pages/man2/getrlimit.2.html); deployment delegation is described by the [kernel cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html).

## Actual RX runtime

- [Structured result](resource-result.json) and [exact commands](resource-commands.json) record the candidate daemon, runtime/builder image IDs and supplied F7 baseline binary hash.
- [Separate observer output](outside-supervisor.json) identifies a process distinct from supervisor PID 1 and its child. It reads child soft/hard 268435456 from procfs while the supervisor remains unlimited. Docker memory, CPU and ulimit options are absent; container isolation is not the enforcement evidence.
- [Resource tests](resource-tests.txt) show an actual RX-launched, deliberately authored 64 MiB test child failing a 128 MiB mmap with `ALLOCATION_ERRNO=12`, plus a separate observer and explicit named whole-bundle refusal for mixed unsupported requirements. This fixture does not claim the production status workload exhausted its 256 MiB ceiling.
- [Kernel failure tests](kernel-failure-tests.txt) exercise real EPERM after lowering a hard limit, injected observation failure after application, authority change, actual exec syscall failure and gate death in the exec window. The first four require confirmed rollback before rejection; the last cannot mint a receipt from EOF. Six tests are new; six existing library tests are also in this output. The additional cwd-shadowing test runs the real gate from a directory containing an untrusted json.py and confirms that it never executes before policy application.
- [Changed-catalog refusal](changed-catalog-refusal.txt) comes from starting the new daemon against a registration accepted by the supplied F7 daemon. Registration and execution entities are unchanged after refusal. There is no silent migration or unregistered launch.
- [Resident result](resident-result.json) preserves the F7 passage, including same registration across normal restart and UNKNOWN after crash. Historical resource observations remain, but current admission after owner loss is UNCONFIRMED.

Reproduce from the pinned contribution, supplying a Linux F7 binary built from `9fa53afe308f0df89b09d2fa01e92a2e753181cb`:

```sh
python3 tools/resource_enforcement_passage.py \
  --image sha256:fcb56bfdfcc1f68bf8cfb6d28f7f24d5899f5e31030ee2a882f6e29e1e28b4a0 \
  --baseline-daemon /absolute/path/to/F7/rx-solutionsd \
  --evidence /absolute/path/to/fresh-resource-evidence
```

The procedure first calls the existing resident passage, builds the Linux tests and runs them in the actual runtime image. The builder is only a compiler environment. No release image, new daemon, network service or state store is added.

## Regression scope

[Summary](summary.json), [macOS workspace output](macos-tests.txt), [macOS clippy](macos-clippy.txt), and [Linux clippy](linux-clippy.txt) record 344/0/17 on macOS and warnings-denied checks. [Linux workspace CI](linux-ci-tests.txt) at the final contribution reports **378 passed, 0 failed, 20 ignored** ([run](https://github.com/jack0682/rx-solutions/actions/runs/35938374535)). Non-Linux enforcement is an explicit rejection test, not an ignored test. There are two new macOS cases and ten new Linux cases because the kernel-specific tests compile only on Linux.

[The ordinary library passage](library-passage.txt), with [commands and exit codes](library-commands.json), completed parent 1 / worker 7 / observed stages 32. These are not 32 independent tests or a substitute for actual-daemon evidence. Its former NO_REQUIREMENTS assertion is strengthened to LINUX_RLIMIT plus exact soft/hard values; existing registration/recovery/readiness/dependency/decision assertions remain. The test wrapper now forwards the requirement-bearing path to the real OS backend.

The summary also records 159 unchanged tracked files across SDK, interfaces, catalogs, manifests and native source. The author recipe change is in Rust builtin code, not an editable site catalog. Production decision anchors and physical-qualification boundaries remain unchanged.

## Retained failures and limits

- [Initial Linux invocation](first-builder-failure.txt) executed tests in a builder without `/usr/bin/python3`, so both old and new process tests failed. Final tests run in the actual runtime; this failure is not counted as acceptance.
- [Initial lint failure](first-clippy-failure.txt) identified an oversized kernel-evidence enum variant. Boxing the private observation fixed it; no warning suppression was added.
- [One fixture reopen failure](fixture-lock-failure.txt) encountered writer-lock contention while process-lifecycle tests ran concurrently. The new lifecycle probes are serialized within that test process; no product lock retry or weaker writer ownership was added. Temporary inheritance of open lock descriptors across concurrent fork/exec is the inferred mechanism, consistent with [flock semantics](https://man7.org/linux/man-pages/man2/flock.2.html); the failure log alone does not identify the inheriting process. Final isolated probes passed.

[Initial CI](first-ci-failure.txt) also rejected a test cleanup assumption that socket EOF makes child exit immediately waitable. Production already returned Uncertain and retained the Child; the test now requires bounded observation of actual exit before forgetting it, retaining the no-admission assertion. That cleanup fix did not change production behavior. The final contribution additionally isolates the bootstrap with Python -I -B and adds its negative test; macOS compiled code is unchanged.

[An unchanged rx-host fixture](host-ci-timeout.txt) also exceeded its existing two-second wait in one branch CI run. Its source is unchanged from F7 and the initial F8 CI had passed that Host test before reaching the new gate cleanup failure. This distinct timing observation is retained; no Host timeout or assertion was weakened in this change.

Multiple kernel policies' partial application is **not** established. Direct-child exit does not establish descendant reclamation. Stored policy observations do not restore ownership or receipts. Real Host/Executor integration, total-manager-loss recovery, operating-area work decisions, dependency replacement and physical equipment remain outside this qualification.

Only local path prefixes are normalized to `<workspace>`/`<user-home>` in these published logs; substantive outputs are unchanged. Source, logs and databases are retained while spent build targets are regenerated as needed.
