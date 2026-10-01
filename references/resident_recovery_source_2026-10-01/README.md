# Original resident source investigation

2026-10-01. Clean sources: Platform `6b56a433dec69b6377f5088ea615463cf0948ecb`,
Solutions `0dc5259d1d21a516be292207c9b965a0b00352ab`. [Source inventories](sources.json)
pin every copied file. [Scope](scope.json) pins the Linux builder and signed runtime
images. The newly built daemon runs as non-root in a read-only Ubuntu arm64
container with loopback networking only. No physical device is connected.

The real P writer/HTTP/mTLS and source-built `rx-solutionsd` run two dependent
software status processes. The new `platform-investigate` command opens a fresh
authenticated session, verifies installed content and reads the original locked
registry and supervisor journal without opening a manager or rewriting history.

- [Normal](normal.json), [log](normal.log): committed matching child exit is
  reported for both original instances; source and outbox records and P's original
  outcome are unchanged after inspection.
- [Outage](outage.json), [log](outage.log): local stop finishes while its original
  delivery is still pending and P retains claims. Inspection reads the actual
  source exit, preserving the original pending key/body and P's last outcome.
- [Cold manager loss](cold.json), [log](cold.log): the test kills its own manager
  after both children are ready. Actual Linux birth-identity investigation finds
  both original processes still present. Inspection neither adopts nor signals
  them; source history, P's original assignment and claims remain unchanged.
  The runner destroys the private container after the scene, including its
  remaining software processes. This is not an RX recovery/stop claim.

[Local checks](local-checks.json) record full macOS workspace tests (P 529/0/19,
S 430/0/19 passed/failed/ignored), clippy and formatter success. Repository,
commit-policy, invariant/catalog/native checks, frozen contract/engine checks and
130-file SDK equality also passed. Targeted tests cover changed catalog, wrong
peer/registry/consumption/journal identity, held store locks, missing birth evidence,
history retention after a later assignment and a compile-fail diagnostic forgery.
The original observation remains history; no constructor accepts its serialized
diagnostic as a live permission. These checks are separate from the Linux scenes.

Reproduce with Platform `tools/test_resident_execution.py --help`, supplying the
paired Solutions source, private targets, registry cache and pinned builder/runtime
images. This version runs all three scenes. Ordinary CI skips these explicit
container tests and cannot replace this evidence.

Limitations: this is source investigation, not P owner approval, receipt
reconciliation, claim release or new authorized execution after an unknown result.
The actual P services run in a test server, not a full platformd deployment; the
daemon is source-built against existing signed program content, not newly shipped
in an installer. Direct-child exit and scoped non-running facts do not establish
descendant/resource recovery, external supervisor closure, business completion or
functional safety. Whole-state rollback, other boot/namespace transitions and
full RF01–RF14 remain unfinished.
