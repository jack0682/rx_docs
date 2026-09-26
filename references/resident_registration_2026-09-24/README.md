# Resident registration evidence — 2026-09-24

Implementation: [rx-solutions 9fa53afe](https://github.com/jack0682/rx-solutions/commit/9fa53afe308f0df89b09d2fa01e92a2e753181cb), [PR 29](https://github.com/jack0682/rx-solutions/pull/29). This bundle distinguishes actual daemon execution, library passage observations, fake-backend tests and CI. It does not establish full resident-framework completion or physical qualification.

## Actual daemon

The [procedure](https://github.com/jack0682/rx-solutions/blob/9fa53afe308f0df89b09d2fa01e92a2e753181cb/tools/resident_registration_passage.py) builds and invokes the actual candidate daemon at `/test/rx-solutionsd` against unchanged validated image contents. It runs two release-owned non-actuating status services, with no network access or attached devices, as UID 10001 on a read-only root.

The separate `docker run -d` management client exits before readiness and ownership observations. The daemon owns the plan and Registry after that client exits. Normal shutdown and a fresh daemon read the same two registration UUIDs; explicit activation produces new execution instances. After a forced disposable-container crash, a fresh daemon retains those registration UUIDs, reports UNKNOWN and refuses activation. This proves persistence and conservative reconciliation, not recovery after total manager loss.

- [Structured result](resident-result.json) includes binary SHA-256, immutable image IDs, registration IDs and state-file inventory.
- [First daemon output](daemon-first.jsonl), [normal reopen](daemon-reopen.jsonl), [unclean reopen](daemon-unknown.jsonl) and [activation refusal](daemon-unknown.stderr) are actual stdout/stderr.
- The state directory contains `supervisor.db` and exactly one additional store, `registration.db`, with their writer locks. The guarded-only initialization store is not needed by these two status services.
- Initial registration and selection-index persistence, mapping attacks and guarded stop ordering are separately exercised by [resident tests](https://github.com/jack0682/rx-solutions/blob/9fa53afe308f0df89b09d2fa01e92a2e753181cb/runtime/rx-supervisor/tests/resident_registration.rs). These use a fake OS backend and real SQLite. Actual guarded Host/Executor integration is not established by the two-status-service daemon passage.

Reproduction requires a fresh evidence directory:

```sh
python3 tools/resident_registration_passage.py \
  --image sha256:fcb56bfdfcc1f68bf8cfb6d28f7f24d5899f5e31030ee2a882f6e29e1e28b4a0 \
  --evidence /absolute/path/to/fresh-resident-evidence
```

## Regression and preservation

[Summary](summary.json), [macOS workspace output](macos-tests.txt), [Linux CI output](linux-ci-tests.txt) and [clippy output](clippy.txt) record:

| Measurement | Observed |
|---|---|
| macOS workspace | 342 passed, 0 failed, 17 ignored |
| Linux workspace CI | 368 passed, 0 failed, 20 ignored |
| Added tests | 12 resident tests and 1 historical registration-revision test |
| Clippy | workspace/all-targets/all-features, warnings denied, exit 0 |
| Binary count | one source binary in `src/bin` |
| Protected tracked files | 145 SDK, manifest, native, OS-process and Supervisor source files unchanged |

The [Linux CI run](https://github.com/jack0682/rx-solutions/actions/runs/35880305825) is tied to the implementation contribution. Its success includes repository, operator and Rust jobs. It does not run the ignored actual Linux passage or qualify hardware. Thirteen more passing tests than the preceding baseline are not thirteen independent operating guarantees.

## Existing library passage

The final source also completed the ordinary disk-based `tools/registration_passage.py` procedure: **parent 1, worker 7, observed stages 32**, exit 0. [Actual output](library-passage.txt) and [commands with exit codes](library-commands.json) are preserved. This is the existing library test binary calling module APIs; it is separate from the actual resident-daemon evidence above and is not counted as 32 independent tests. No ephemeral private signing keys are included.

## Failed attempts and resource recovery

The [first daemon attempt](first-daemon-failure.txt) mounted the candidate over `/opt/rx/bin/rx-solutionsd`. The existing status service correctly detected the release-manifest mismatch and exited. The final procedure leaves the image untouched and invokes the candidate from `/test`. It does not weaken the manifest, publish a replacement image or count the failed attempt as success.

A final library rebuild then encountered [host ENOSPC](library-final2-run.txt); an attempted alternate builder encountered [Docker image I/O failure](recheck-builder-create.txt). Neither was a product acceptance failure or a passing run. Only three specifically approved obsolete task build directories were removed; source, logs, databases and final daemon evidence were retained. Docker was recovered. A RAM-backed build was explored during recovery, but further space recovery removed that need. The final acceptance run uses the ordinary disk-based library passage procedure and the normal test profile; the temporary workaround is not the final acceptance basis.

Local workspace prefixes in published logs are replaced with `<workspace>` or `<user-home>`; substantive output is unchanged. Raw command logs and state databases remain in the local evidence directory. Stored observations are historical, not current process ownership or permission.
