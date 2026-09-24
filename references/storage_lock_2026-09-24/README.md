# G1 ownership lifetime evidence

[Design, scope and compatible commits](../../docs/36_storage_lock_lifetime.md).
[Summary](summary.json), [actual Linux result](lock-result.json), [exact commands](lock-commands.json).
Paths are redacted to `<workspace>` / `<user-home>`; observations and failures are retained.

- [Raw LOCK_UN premise and dangerous opposite](unlock-premise-and-opposite.txt) / [probe source](unlock_probe.py): creator unlock releases the shared description, but unconditional child unlock can release a live parent's lock. This is a pre-implementation counterexample, not the shipped guard.
- [Eleven actual fork/ownership scenes](fork-overlaps.json) and [expected child callback panic](expected-foreign-unwind.txt): normal close/Drop with live fork copies, opposing live/new writer refusals, inherited repository/Host guard cleanup, active transaction child Ok/Err/panic, real Command pre_exec success/failure and actual manager SIGKILL. Panic is deliberately injected; its parent transaction must survive.
- [Real SQLite close failure](close-failure.txt), [ordinary ownership tests](ownership-tests.txt), [existing storage atomicity tests](storage-atomicity.txt). An unfinished statement makes real sqlite3_close fail; a contender is refused until holder exit. No private Connection API or test hook is exported.
- [All50 Host rounds](host-stress-50.txt), unfiltered16-thread execution. All50 exited0 in this bounded run. No previous failure is erased and no definitive attribution of the historical F9 single failure is made.
- [Platform macOS398/0/16](platform-macos-workspace.txt), [solutions macOS376/0/17](solutions-macos-workspace.txt), [platform clippy](platform-clippy.txt), [solutions clippy](solutions-clippy.txt), [Linux fixture clippy](linux-fixture-clippy.txt), [baseline comparison](protected.json).
- Seven historical regressions: [library32](library32.txt) / [commands](library-commands.json), [resident](resident-result.json), [resource](resource-result.json) / [commands](resource-commands.json), [manager loss](manager-result.json) / [commands](manager-commands.json), [work](work-result.json) / [commands](work-commands.json), [replacement](replacement-result.json) / [commands](replacement-commands.json), [F12 support](f12-support-result.json) / [commands](f12-support-commands.json). F12's historical result label remains unchanged; its stress has no failures in this run. G1's scoped result and abrupt-loss limit are separate.
- Retained development checks: [missed Option access](retained-option-access-compile-error.txt), [downstream exhaustive matches](retained-exhaustive-match-errors.txt), [duplicate Debug derive](retained-debug-derive-error.txt), [Linux-only fixture accidentally checked on macOS](retained-linux-fixture-on-macos-error.txt). Corrected without weakening ownership assertions or ignoring a test. The fixture was subsequently checked in Linux, its supported environment.

Reproduce the integration from the pinned platform source with its matching regenerated solutions SDK:

```sh
python3 tools/storage_lock_passage.py --solutions /absolute/solutions \
  --image RX_RUNTIME_IMAGE --builder RUST_BUILDER --evidence /fresh/evidence
```

The fixture is a standalone measurement crate, not a shipped daemon. It narrowly uses unsafe fork/wait instrumentation while product crates retain their unsafe prohibition. The source guard is not a security boundary against malicious raw syscalls or OS replacement, and the creator PID is not persisted recovery authority.

The retained SIGKILL limit is **REFUSED_UNTIL_INHERITED_DESCRIPTION_CLOSES**. Close failure retains resources for process lifetime; inherited copies may extend it. No active quarantine service, arbitrary retry, lock deletion, PID adoption, physical handover, remote filesystem or broad post-fork SQLite qualification is established.
