# Work-judgment enforcement evidence — 2026-09-24

Implementation: [rx-solutions 2b0c4a35](https://github.com/jack0682/rx-solutions/commit/2b0c4a35631e55817a2f1a75e30eb396b448bfa4), [PR 32](https://github.com/jack0682/rx-solutions/pull/32). This is a non-actuating receiving gate for a derived support-gap report. The host does not issue work approval; production operating-area policy integration is absent.

## Boundary selection

[The actual runtime probe](boundary-probe.txt) returned stable diagnostic GET data and POST503 CONTROL_NOT_EXPOSED. Source inspection also found only DiagnosticOnly F5 consumption with work_use Unsupported. This falsified directly treating that diagnostic boundary as work. The adopted operation instead commits a separate derived report and unique decision-consumption entry to the existing registration repository, using its CAS and atomic transaction.

## Actual Linux operation

[Structured result](work-result.json), [commands](work-commands.json), and [nine work tests](linux-work-tests.txt) retain actual runtime/builder IDs and daemon hash. The positive report uses the installed release counts, independently read by another Python process. With the same observed counts, requirements increased by two produce shortfall2, while requirements equal to the observations produce shortfall0. Source digest stays equal and task/input digest changes. The author catalog is explicitly a test fixture with a fresh external OpenSSL issuer, not a shipping anchor or actual operating-area approval.

The tests exercise actual HTTP processes, monotonic expiry, signed revocation, real SQLite transactions and the same receiving code as production. Mutable-report and transaction-fault fixtures are explicit injections, not claims of physical equipment or real storage incidents.

- Between judgment and use, changed counts, an invalid readiness field and registration retirement each refuse commitment and leave zero work records.
- Missing anchors, explicit external denial, a missing judgment response and an unconnected provider cannot prepare work.
- Expiry and signed revocation before the final cut refuse commitment and spend nothing.
- Duplicate operation IDs return revision conflict without another result or permission consumption. A second preparation of an already completed ID does not even call the issuer again.
- Injected rollback after staging both result and consumption leaves both absent. A still-live prepared decision can retry only through the full current gate.
- Injected reply loss after successful commit is resolved by operation-ID query, not another execution.
- Receiver restart invalidates retained proof while the original report remains queryable as history.
- A revocation thread begun during a staged transaction cannot finish until the transaction and its physical commit/rollback release the receiving guard. Successful work remains historical; after rollback the next retry is refused as revoked.
- A deliberate delay after the product callback's logical cut, before SQLite commit, lets TTL expire. The commit succeeds and the inert report remains. This models the post-cut commit-IO window; it does not claim the proof remained valid at IO completion.

The [shipping daemon output](shipping-daemon.txt) and [outside observer](outside-observer.json) show the other side of the boundary: default work denial due to absent author policy, healthy diagnostic GET, and zero work-result/consumption rows. No startup paralysis, new service, network API or store file is introduced.

## Precisely bounded concurrency

The logical cut is the last live decision check in a **successful atomic transaction**. SQLite Immediate holds the write lock from transaction start, closing registration/revision and consumption-key races. The F6 revocation mutex is held through the whole transact, including commit IO, so revocation is ordered before or after that transaction.

Exactly two timing residuals remain: a monotonic TTL may expire after the logical cut during commit IO, and HTTP self-report observations are not physically atomic with the SQL commit. Artifacts carry observation time, instance and F4 origins and assert no current permission. This is not a blanket uncertainty about the already serialized registration, consumption or revocation conditions.

Reproduce with fresh evidence:

```sh
python3 tools/work_use_passage.py \
  --image sha256:fcb56bfdfcc1f68bf8cfb6d28f7f24d5899f5e31030ee2a882f6e29e1e28b4a0 \
  --builder sha256:ff521445a372125ed4f76e1453a1f8098f2d05332d1601d30db1c1f62757e730 \
  --evidence /absolute/path/to/fresh-evidence
```

## Regression and type boundary

[Summary](summary.json), [macOS workspace](macos-workspace.txt), [macOS clippy](macos-clippy.txt) and [Linux clippy](linux-clippy.txt) record **362/0/17** and warnings-denied checks. Nine new work tests and four new compile-rejection doctests account for the increase from 349. [Compiler checks](compile-rejections.txt) refuse Prepared deserialization, conversion from Report or past WorkUseAssessment, and direct external construction. Existing F9 compiler attacks also remain. [Exact source-head Linux CI](linux-workspace-ci.txt) passed **404/0/20** ([run 35953340454](https://github.com/jack0682/rx-solutions/actions/runs/35953340454)); no ignore was added or removed.

The unchanged [library 32-stage](library-passage.txt) has [commands](library-commands.json); [resident](resident-result.json) and [resource](resource-result.json) have [resource commands](resource-commands.json); [manager-loss](manager-loss-result.json) has [commands](manager-loss-commands.json). [183 protected files](protected.json), including original supervisor tests, F5 code, shipping builtin catalog, SDK/interfaces/catalogs/manifests/native, remain unchanged. There is one production binary.

## Retained development failures

[Initial compile failure](retained-timepoint-eq-failure.txt) attempted Eq on TimePoint, which supports only PartialEq; the new historical Report derives PartialEq without changing the SDK. [The first work fixture](retained-fixture-timing-failure.txt) used a restart backoff below the pre-existing 100 ms minimum; the fixture was corrected to 100 ms, with the validator unchanged. [The first concurrency observation](retained-channel-lifetime-failure.txt) dropped its completion receiver before the revocation thread could send; receiver lifetime was extended and bounded observations now check both blocked-in-transaction and completed-after-transaction states. No production guard, timeout or test assertion was weakened to hide these failures.

Only local path prefixes are normalized to `<workspace>`/`<user-home>`; substantive outputs are preserved. Actual operating-area service policy, physical operations, equipment qualification and multi-host execution remain outside this evidence.
