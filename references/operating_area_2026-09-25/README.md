# G3 offline operating-area judgment evidence

This is one development rule for producing an inert F10 support-gap report. The
host is not an issuer. Physical safety, quality, equipment qualification, production
key custody, network judgment and multi-area operation are not established here.

## Before, after and wire preservation

The [before](before-runtime.log) and [after](after-runtime.log) real Linux probes
both refuse three cases with zero work rows: default no anchors, an explicitly
authored public anchor with null provider, and a host counterfeit signature.
The probe never receives a private-key mount. Sources are retained under
before-probe and after-probe; original binaries remain in local evidence.

[Wire comparison](wire-comparison.json): before/after/final6225 bytes are identical,
including canonical decision/revocation signing bytes, serde representation, large
Counter/nonASCII data and all14 failure strings. This is a source ownership move,
not a new F6 permission factory. Live seals remain in solutions.

## Actual judge and gate

[Final twelve scenes](area-final/result.json), [commands](area-final/commands.json)
and per-scene raw outputs cover legitimate external approval, no connection,
author scope, the judge's own rule denial, bad signature, claimed area/role/kind,
unknown response key, signed revocation and expiry after judgment, and lock
contention at commit. Negative cases leave zero work rows; approval leaves the
actual derived result and unique consumption rows. The result compares675 native
packages to1000 (gap325),4 profiles to6 (gap2), and remains historical output.

A separate Linux issuer container receives the dedicated private-key mount. The
host receives no key path/bytes or signer command. Host process snapshots and mount
inventories are measured, not a claim inferred from a successful signature. A
snapshot is not a lifetime process trace; the absence of a host signer launch path
is separately source-inspected. Private key remains excluded from Git and images.

[Linux receiver tests](provider-linux-tests.log) separately cover nonce/deadline
retention, old proof Epoch failure, F9 unresolved reopen refusal, explicit fresh
receiver rejection of old response, cached signed revocation, and a separate
cooperating process refused publication while the F10 physical transaction is in
progress. No public factory was added; compile-fail tests exercise field access and
constructor calls for Request, Prepared and VerifiedDecision. Unscoped historical
registration query remains NotEvaluated.

## Failures and distinct corrections

- [Generic type inference failure](provider-tests-first.log): test closure type
  made explicit; no product behavior changed.
- [Wrong restart-test assumption](provider-tests-second.log): F9 refuses unresolved
  execution instead of immediately creating a new challenge. The gate was retained;
  [corrected test](provider-tests-third.log) separates Epoch invalidation from a
  fresh receiver's replay rejection.
- [Observer partial JSON](area-final.log): existence was observed while a test
  control marker was being written. Fixed complete temporary-file/atomic rename
  publication, not read retries. Product mailbox already used complete publication.
- [Default catalog regression](library-final.log): the opt-in recipe was initially
  returned by the default catalog, violating the existing all-no-anchor assertion.
  The assertion/script stayed unchanged; only explicit plan selection now adds the
  compiled work recipe. Corrected library passage passes.

- A separate G1 standalone probe `--locked` refusal came from a missing storage→rustix
  dependency edge in its Cargo.lock. The correction adds that edge only, changing
  no dependency version, probe code or assertion. This is an identified integration
  omission, not the unresolved E0463 event below. Offline metadata resolution also
  reported an uncached target-specific crate after writing the corrected lock;
  the actual Linux --locked build validates the intended dependency set. The same
  unchanged passage also fixes its executable set; the three new mailbox cases
  were moved unchanged into the existing storage unit-test binary, with SDK
  regeneration. No test was skipped or removed.

### UNRESOLVED_COLD_BUILD_METADATA_LOOKUP

One manager-loss passage attempt failed before runtime start while compiling
ed25519-dalek: E0463 named curve25519_dalek, ed25519 and sha2. The official
[Rust error description](https://doc.rust-lang.org/error_codes/E0463.html) identifies
crate lookup failure, not a unique disk cause. The [raw failure](build-incident/build.stderr)
remains. Target artifacts existed with normal nonzero sizes, and
[126 prior artifact hashes](manager-artifact-comparison.json) did not change.
A [metadata-locator diagnostic](manager-artifact-diagnostic.log) succeeded in that
same preserved target with no source edit or deletion. This is not a fix.

The cause is NOT_ESTABLISHED. Disk/visibility pressure is a hypothesis, not attribution.
A peer separately observed8.3GiB free, then9.1GiB after removing its own818MB scratch
artifacts. The planned full fresh manager replication used a new isolated evidence/
target directory and recorded disk before/after externally, leaving the nine
passage scripts untouched. It started with16555139072 bytes free and finished with
15645241344 bytes free, and passed. Missing/zero-byte dependency files were not
observed in the original failure. No G3 runtime failure or historical F9 cause is
claimed from this event. The failed target remains available locally.

**Any statement that all nine boundaries passed includes this qualification: one
initial manager attempt failed for an unresolved build reason; its same-target
diagnostic and one planned fresh full replication later passed. No success erased
that original failure.** The catalog defect above is a different, actually fixed
product integration defect.

## Reproduction and supported interval

Build the current solutions daemon and the standalone platform
`tools/operating_area_judge` with the pinned Rust toolchain, using private target
directories. Then run the product passage with a fresh evidence directory:

```sh
python3 rx-solutions/tools/operating_area_passage.py \
  --image rx-solutions:g2-authenticated --key OWNER_ONLY_DEVELOPMENT_JUDGE_KEY \
  --daemon CURRENT_LINUX_RX_SOLUTIONS_DAEMON --judge CURRENT_LINUX_JUDGE \
  --evidence FRESH_DIRECTORY
```

The signer key must match the compiled development public key. This does not install
an authority in the host; only the issuer container receives that mount. The signed
native runtime is the G2 fixed image; current verifier/issuer/test binaries are
separately built and mounted. No full native image rebuild or deployment is claimed.

The cooperating mailbox lock spans final revocation acquisition through physical
commit. Noncooperating writers remain outside this order. Bounded pending before a
complete response is not a use retry and never renews TTL/nonce. A busy commit
refuses use. F10 TTL during post-cut IO and HTTP as-of observations remain explicit.

## Validation and compatibility

macOS platform405/0/16 and final solutions386/0/17; both workspace clippy passed.
SDK115 files equal platform source. Public contracts and prior passage scripts/
assertions remain unchanged. Exact CI, commit signatures and compatible merge
combinations are recorded with publication before independent handoff.

Source changes are [platform PR21](https://github.com/jack0682/rx-platform/pull/21)
(contribution eb9164135fde93d637e49a4a3c8022b60223e75b) and
[solutions PR37](https://github.com/jack0682/rx-solutions/pull/37)
(contribution3c6db54a93455d7597f5dbbee476bf01ced86c2c). The documentation PR links both.
Main and physical equipment remain unchanged. No independent acceptance is asserted
by these first-party execution results.

Final boundary ledger: [all nine with retained failures](verification-summary.json).
The final G1 passage [result](regression/lock-final2/result.json) keeps all11 overlap
scenes and50 unfiltered Host rounds. Original [lockfile refusal](lock-lockfile-failure/fork-probe-build.stderr)
and [test-layout assertion](lock-final.log) remain separate from the compiler incident.
The fresh manager's [disk/timing record](remaining-passages.json) preserves before
and after measurements without changing any original passage script.

Final source combination: platform [PR21](https://github.com/jack0682/rx-platform/pull/21)
and [PR22](https://github.com/jack0682/rx-platform/pull/22), ending at
75e19331ec1c3bfdb275f75480188f485c86d64b; solutions
[PR37](https://github.com/jack0682/rx-solutions/pull/37) and
[PR38](https://github.com/jack0682/rx-solutions/pull/38), ending at
ed3d90f9bd1e54e78023b77ae399b4d237c8e4b4. Follow-ups repair the standalone lock
edge and preserve the existing test executable set; all original assertions remain.
[Signature/tree comparison](source-signatures.json) and
[final code custody scan](key-custody-final-code.json) are recorded.

Exact final merge CI, both attempt1: platform [36068577921](https://github.com/jack0682/rx-platform/actions/runs/36068577921)
406/0/16 and solutions [36068783698](https://github.com/jack0682/rx-solutions/actions/runs/36068783698)
430/0/20. [Final counts](final-ci-counts.json), [platform metadata](ci-platform-final-merge.json),
[solutions metadata](ci-solutions-final-merge.json). These CI results do not erase the
retained initial manager E0463 or the separately corrected integration/test-harness defects.

Final-artifact supplement: a validation orchestration error ran a live-source build
concurrently with checkout/pull. Its lock refusal overlapped the temporary old G2
checkout; a stable isolated resolver produced no Cargo.lock difference. This is
recorded in [checkout-race.md](checkout-race.md), with [reflog](checkout-race-reflog.txt)
and [time/hash comparison](checkout-race-lock-comparison.json), separately from E0463.
The final source was frozen before a fresh --locked build. The unit-test layout
change altered the daemon hash, so the exact final executable was exercised again:
[final12 scenes](exact-final-area/result.json), [commands](exact-final-area/commands.json)
and [known-key scan](exact-final-key-custody.json). All12 passed. This supplements,
rather than erases, earlier failures and observations. The final judge hash is unchanged.
