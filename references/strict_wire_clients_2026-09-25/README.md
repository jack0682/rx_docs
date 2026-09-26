# G5.1 strict-wire/client evidence

See [scope and decision](../../docs/40_strict_wire_and_clients.md). These records
cover software/profile/installed-client and actual Linux FILE_SIMULATION behavior.
They do not claim a connected ROBOTIS robot, product carriage, complete G5 SDK
baseline or complete five-project bundle. The immediate G5.2 adapter is separate.

- [Corpus and package result](final-client-packages/result.json):82 authored cases;
  installed wheel and external CMake consumer. [Python](final-client-packages/python-corpus.stdout)
  and [C++](final-client-packages/cpp-corpus.stdout) expanded input hashes/statuses
  and specified re-encode results are equal. Normative corpus/profile are in the
  platform protocol bundle; no implementation generated expected outputs.
- [Rust result](rust-conformance-generated-roundtrip.log),
  [singular mutant](mutation-result.json) and [enum mutant](enum-mutation-result.json).
  Fixed vectors fail both private-source mutations.69 public-message cases and13
  synthetic guard-descriptor cases have separate labels.
- [Clean generator defect](generator-gap.json):8 rather than9 RPC IDL files.
  [Correction](generator-fixed.log) preserves all existing9 file hashes.
- Actual resident P/H and installed peers:
  [Python loss](python-loss-exact/result.json), [C++ loss](cpp-loss-exact/result.json),
  [Python UNKNOWN](python-unknown-exact/result.json), [C++ UNKNOWN](cpp-unknown-exact/result.json).
  Real signed process compilation and public terminal approvals/qualification were
  reused. No DB authority seed or fake readiness assertion replaced them.
- Each loss case drops encrypted return bytes after negotiation, observes one
  actual independent native file effect, cuts transport and explicitly retries
  the same Cell.SubmitOperation. Original receipt/operation ID are preserved.
- UNKNOWN cases make the native effects file readable but unwritable. P records
  KNOWLEDGE_UNKNOWN/OUTCOME_NONE; client restart and reverse-language queries do
  not invent success, failure or a new work identity. Full workflow/material
  completion and clean whole-cell shutdown are not claimed by these cases.
- Current [toolchain versions](client-toolchain-versions.log),
  [runtime code input comparison](runtime-code-input-comparison.json), and
  [recovery evidence](release-evidence.json) identify the actual environment.
  Source archives/binaries/private materials stay in local evidence, not this public copy.
- [macOS counts](mac-counts.json), repository/clippy/CI logs, original G3/G4
  regression results and each prior-boundary command/result remain separate.
- Retained [assembly incidents](runtime-image-incident.md) and
  [runtime-test expectation error](runtime-test-incidents.md) distinguish harness
  mistakes from product defects. Deliberate mutant failures are expected negative
  controls, not hidden regressions. No failing test is replaced by a success rerun
  without a recorded concrete correction.

`inventory.json` hashes selected raw files. No private signing seeds, TLS keys,
login passwords/cookies, runtime DBs or regenerable build caches are published.
The reproducible source tools are platform `tools/prepare_clients.py`,
`tools/test_client_packages.py`, `tools/test_prepare_clients.py` and
`tools/test_clients.py`; commands.json and suite logs record their actual invocations.
Positive runtime scenarios require the recorded current P/H validation images and
existing fixture export/compiler/review toolchain. Scope is explicit software
simulation; installation/import/link is not robot readiness or safety evidence.
