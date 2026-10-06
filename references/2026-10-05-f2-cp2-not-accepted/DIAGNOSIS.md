# F2′ CP2 acceptance failure — investigation in progress

Status: **NOT ACCEPTED. CP3 NOT STARTED.** This supersedes the ready-for-acceptance
status of the earlier CP2 precheck; that successful precheck remains historical evidence.
The acceptance commands were executed by **Claude on the user's Mac**, at the user's
request. The user rejected CP2. The following read-only diagnosis was executed by Codex
on the same Mac. It is neither user execution nor acceptance.

## Preserved original

- Run `01a10af3-3889-7271-b57c-722737f97e6d`
- Request `45fc67b5-3112-426d-9b28-fc24bfcab56f`
- Part 3 clamp operation `01a10af4-3c83-7188-b378-68e9fa79b8be`
- Invocation `3e5f80fc-0069-4a5d-a862-a2cbac92d008`, Host `host/sim-b`

25 operations settled/succeeded/released; Parts 1 and 2 confirmed completed. The
original operation remains UNKNOWN/QUARANTINED, holds the resource, and slot 5 is not
consumed. Host A did not advance. No release, retry, replacement request, runtime
restart, or removal of background load was performed during this diagnosis.

## Dispatch evidence and limits

P's PREPARE and AUTHORIZE outboxes are both DELIVERED. Host journal sequence 50 is
PREPARED; sequence 51 is SEND_ENTERED. The permit is consumed. There is no
NATIVE_ACCEPTED record or native-entry evidence, and no external native directory or
device effect row for the target operation. SEND_ENTERED is not proof of native entry.

P logged `HOST_RPC / InvalidArgument / invalid input: Resource temporarily unavailable
(os error 11)` at `2026-10-05T07:25:41.480636045Z`. This is a Host-local error, not the
3-second P-to-Host RPC timeout. The old binary did not label which local syscall failed.

The permit was issued at BOOTTIME `315807191092247` and expired at
`315808191092247`. Host prepare's sampled time, reconstructed from its 1-second
prepare-validity, is `315807796736247`: **605.644 ms after permit issuance**.
Only **394.356 ms** of the permit remained at that sample, before the prepare guard,
journal commit, P processing/queueing, authorize validation, repeated fresh guards,
process spawn, and entry acknowledgment.

Ten earlier external completion records provide a local realtime/BOOTTIME mapping
(completion file mtime minus capture time). Its spread is 1.918 ms; it places the
target permit expiry at approximately 07:25:41.476511–07:25:41.478430 UTC. Thus the
logged errno followed expiry by approximately **2.2–4.1 ms**. File mtimes are not exact
RPC timestamps; this is a bounded local reconstruction, not an instrumented span.

The evidence strongly points to the deadline-limited entry read expiring before the
worker durably initialized this operation. The retained record cannot establish the
exact spawn/write/read durations. Absence of an effect/file is not promoted to NO_EFFECT
or permission to reissue. A source-only error-context change is being tested to retain
the failing channel stage, entry budget, elapsed time and bytes on subsequent failures.

## Time budget versus observations on this Mac

Architecture: arm64 Linux containers on the user's Mac, not amd64 emulation.

| Boundary | Existing limit | Measured evidence |
|---|---|---|
| P→Host RPC | 3 s | This failure returned Host InvalidArgument, not RPC timeout |
| Dispatch permit | 1 s | 605.644 ms consumed before Host prepare sampled time |
| Host prepare validity | 1 s from prepare sample | Does not extend the earlier P permit |
| External passive snapshot | 500 ms process/read and snapshot age | 60 read-only calls: median 24.870 ms, maximum 30.361 ms, 0 errors |
| Declared external observations | age ≤1 s, uncertainty 0 | Actual acquisition timestamps retained; no freshness changes |
| Native entry acknowledgment | before min(permit expiry, fresh guard expiry); no independent 30 s allowance | Earlier successful external dispatches had 201.812–301.362 ms left at adapter dispatch creation; failed call has no stored dispatch span |
| Execution snapshot | 100 ms | 20 reads after Executor exit / RECOVERY_REQUIRED: median 13.026 ms, max 21.376 ms; not the original active-run load |
| Finite execution | 30 s | Scenario process requires 5/7/5 s; this failure is before native entry, not completion timeout |

Read-only passive measurement includes pinned-file hashing, process spawn, private
socket exchange, and process exit. Median/max verification: 0.188/0.427 ms; spawn:
0.271/0.763 ms; first byte: 22.622/27.700 ms. This is a passive startup proxy, not an
actual execute-entry measurement. Existing stacks were retained; the measurement adds
temporary diagnostic activity.

## P CPU while held

Docker sampled P at 95.02% CPU and Host B at 19.20%. Over a separate two-second sample,
P's `rx-state-writer` used 172 scheduler ticks (about 1.72 CPU seconds); network workers
used about three ticks combined. The process is spending CPU in its serialized state
writer, not issuing another chuck effect.

An 8-second perf sample (337 CPU samples, no reported loss) included
`workflow_model::current_snapshot` in 32.34% and `execution_configuration::domain`
in 22.26% of sampled stacks. These inclusive figures overlap. The advisory execution
snapshot path rechecks qualification/current definitions while the Run is held.
The background reconciliation path also scans and decodes prior Work records each pass.
After the original Executor had exited (see the timeline below), a later 10-second sample had only 86 samples / 1.755 CPU seconds and emphasized
reconciliation_work (36.05%) and maintained-condition checks (15.12%); it is not directly
comparable to the earlier busy interval. No stack was paused/stopped to create this change.

Both sampled paths repeatedly canonicalize a JSON Value and then build another untyped
JSON tree solely to decode a typed stored record. The candidate P change removes that
second untyped parse only. Canonical numeric conversion, the 1 MiB bound, schema checks,
current-reference/qualification checks, and all authority decisions remain.
It has passed 350 application regression tests plus focused decode-equivalence/bound
tests; this is not yet evidence of a resolved normal-path timing failure.

## Resubmission bar

The original acceptance Run stays preserved. All prior unsuccessful setup/normal
attempts remain in the earlier CP2 attempt ledger, and this acceptance failure is added
without relabeling the earlier green precheck as acceptance.

After a justified fix: record **every** N=3 normal attempt, require five consecutive
successes with the other stacks retained as observed, then provide one unused acceptance
run to the user. A failed attempt resets the consecutive count and remains in the report.
No resubmission success has been claimed. CI/DCO and exact-head develop merges precede
handoff. If time limits or entry/completion semantics need changing, stop and ask first.

## Environment changed during diagnosis — five-run series not started

The first perf recording ended at 07:39:34 UTC. The acceptance Executor then exited at
**07:42:38.872347127 UTC**, rc=1, OOMKilled=false. Its final detail was
`execution view expired before use`; it passed through STOPPING/STOPPED and reported
`executor stop needs attention; inspect persistent intent and P state`.
The second perf recording ended at 07:45:34 UTC, **after** that exit. This explains
why the later low-CPU sample cannot be used as proof of a performance fix.
This preceded the candidate image builds; it was not an intentional stop command.

Fresh product CLI inspect now shows the original Run RECOVERY_REQUIRED. The same target
operation/invocation remains RECONCILING/UNKNOWN/QUARANTINED with no outcome/evidence.
The original request, Host journals, resource and slot hold were not cleared or replayed.

During parallel candidate image builds, Docker also reports **OOMKilled=true, rc=137**
for previously paused `rx-f2-s1-p` at 07:58:48 UTC and `rx-f2-s1b-p` at 07:59:12 UTC.
Their persistent volumes are retained. Parallel build activity added memory pressure;
this was a poor diagnostic scheduling choice. Subsequent builds must be serial.
They were already paused before this request, so they did not supply active CPU load,
but their exit is still an environment change and must not be hidden.

The candidate installation is separate (`rx-f2-resubmit-*`, local port 8463), qualified
for the same SIM scenario. **No normal resubmission Run has been started.** Setup recorded
a subnet allocation refusal, an authoring resume-script TypeError, and a follow-on CLI
connection-file refusal; setup resumed with the same initialized new store. None is
counted as a normal-run attempt or a success. All original command logs are retained.

Source candidates are committed on feature branches: P `108f1cb` (redundant stored-record
parse), S `6773cdd` (channel error context). They are not merged or accepted. The Linux
external-process integration test passed in the installed image build; the Mac version
of that Linux-only test ran zero tests and is not counted as evidence.

The two completed process steps in the rejected acceptance Run have entry-file to
receipt-file intervals **5007 ms and 7010 ms**, against the unchanged 30 s completion
limit. These are filesystem event intervals, not a claimed exact native CPU duration.

The user required the existing stacks to remain running as observed. Because the
original Executor exited, it is no longer possible to claim that exact condition.
Do not restart/alter the preserved original Run merely to recreate load, and do not
count a green series under the lower load. A revised load reproduction requires the
user's decision before the five-run series begins. Proposed single option: preserve
the original stopped/held state and use a separate passive observer to reproduce the
recorded read paths/cadence and at least the measured busy P/Host load; label it as
reproduced load rather than the original live Executor. No mutation/operation RPC,
new authorization, release, reissue, limit extension or CP3 work is included.

The 20 existing-session GetSnapshot RPC reads sent no Hello, negotiation, grant or
operation. All reported admission=false / NOT_COMMISSIONED. These measurements cannot
establish the failed busy-state snapshot RTT or prove the candidate fix. The first
observer setup could not download dependencies on an internal-only network; the
separate observer was rerun with network access without changing the target services.
Only the two temporary diagnostic helper containers were removed after capture; their
outputs are retained. No original workload container or persistent volume was removed.

Read-only product inspection of the preserved original (no release or run command):

```sh
cd /Users/ojaehong/RX_automation/rx_ws/.build/framework-f2-author4
python3 installed-client/rx execution \
  --connection site/connections/operator.json \
  --state-dir ../framework-f2-diagnosis/user-inspect \
  inspect 01a10af3-3889-7271-b57c-722737f97e6d --reports
```
