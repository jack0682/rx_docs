# G2 development-release evidence

The source authority moves from mutable local inventory/policy to a literal
compiled development public key. This is not authenticated OS/verifier provenance,
product signing custody, physical qualification or operating-area work authority.
The before/after exercises use actual Linux and retain negative results.

- Unsigned base: `sha256:fcb56bfdfcc1f68bf8cfb6d28f7f24d5899f5e31030ee2a882f6e29e1e28b4a0`.
- Signed derivative: `sha256:983e84c8c93602980531e72833c540fda53afb4f8a78460c26e5abecf8dae311`.
- Rust builder: `sha256:ff521445a372125ed4f76e1453a1f8098f2d05332d1601d30db1c1f62757e730`.
- Current checkout verifier/test binaries are built separately and mounted by the
  passages into that fixed native runtime. The whole native image was not rebuilt
  or deployed as a G2 distribution. The verifier/OS remain trusted inputs.

## Raw observations

[Before probe](before-probe/src/main.rs) invokes the unmodified G1 package policy
path. [Output](policy-runtime.log): same binary/package, only policy.json changed,
UNTRUSTED becomes ACCEPTED. The binary was built against platform98030850 with the
[locked fixture](before-probe/Cargo.lock); its [build log](policy-build.log) is kept.
This falsifies reusing the mutable package policy for release trust. The existing
package-local policy contract itself is not changed.

[First G2 assertion failure](release-runtime-first.log) exposed `Release(Unsigned)`
instead of a stable CLI condition. [Second run](release-before-preflight/result.json)
passed the six named G2 refusals. The [old support regression failure](support-final.log)
then exposed writable-state acquisition preceding F12's source-integrity refusal.
Its [commands](support-failure/commands.json), [actual refusal](support-failure/reject-script-only.stderr)
and [50 clean Host rounds](support-failure/host-stress.stdout) are retained. This
was not attributed to the storage-lock flake. The failed binary hash and retained
local path are in [failed-binary.json](support-failure/failed-binary.json).

The [final G2 result](release-final/result.json) and [all commands](release-final/commands.json)
cover unsigned, invalid signature, unknown key, revoked, rollback and content
mismatch; actual policy/keyfile/environment injection; key-ID impersonation;
unsupported CLI key override; script+inventory substitution; and Host binary plus
forged inventory, beyond F12's two compiled source pins. Versions1/2/3 actually
reach PROCESS_READY, observed outside the manager. Separate containers retain the
same state directory; the old version and old revocation list are refused after
restart. Changing plan state_subdirectory does not reset the global release floor.

Whole state rollback/deletion is NOT_DETECTED. Offline freshness and product key
custody/rotation are NOT_ESTABLISHED. Checks are explicit caller-driven checkpoints,
not continuous monitoring. A later invocation may advance retained release/revocation
state after admission commits; already admitted work is not automatically revoked,
and admission plus later exec is not an atomic operation. The source preflight is rejection-only and occurs before
writable state; it cannot authenticate or admit a release by itself.

## Reproduction

Verify the local `rx-solutions:n5-runtime` tag resolves to the unsigned digest
above. [Signed image inputs](signed-image/input.json), [Dockerfile](signed-image/Dockerfile)
and [build output](signed-image/build.log) record derivation. The context contains
public metadata, never the private key. The signer command is recorded in the input
file. An independent reviewer can use the supplied public release/revocation files
for this exact inventory without accessing the private key:

```sh
docker build --pull=false --network none -t rx-solutions:g2-authenticated signed-image
python3 rx-solutions/tools/release_origin_passage.py \
  --image rx-solutions:g2-authenticated --unsigned-image rx-solutions:n5-runtime \
  --metadata signed-metadata --evidence /fresh/g2-observation
```

The default passage builds the current daemon with the recorded Rust builder;
`--daemon` was used for our already-built, hashed artifact. `commands.json` records
which form was actually executed. Outputs are observations, not expected values.

## Validation and key custody

macOS platform:401 passed /0 failed /16 ignored. Final solutions after the source
preflight fix:376 /0 /17. [Platform output](platform-workspace-final.log),
[final solutions output](solutions-workspace-after-preflight.log),
[platform clippy](platform-clippy-first.log), [final solutions clippy](solutions-clippy-after-preflight.log).
[Repository gates](repository-checks.json) and [raw output](repository-checks.log)
include SDK byte equality, unchanged normative hashes and formatting.

[Actual runtime scan](key-custody-precommit.json) inspected59020 files and found no
development private key. [Committed source trees](key-custody-code-commits.json)
were also scanned; the final code/document commits are scanned separately before
handoff. `git check-ignore` confirms the key file remains ignored. The scanner
checks this specific key without exposing its bytes; it is not a generic credential
audit or a product signing ceremony.

The existing eight passage scripts/assertions are unchanged. Their commands,
results and raw outputs are retained under regression; the first batch's support
failure remains separate from the corrected-source batch. A successful later run
does not erase the original failure. Regenerable build/cache directories were
removed only after results, logs and state were retained; the F7 comparison daemon
and the failed/current G2 binaries remain available locally.

Code compatibility: platform PR20 contribution95fbba23 / merge1966319f, solutions
PR36 final contribution1f9cc7de / merge1430e1b1. The documentation change links both
PRs and records exact merge CI and signature/DCO evidence before handoff. Main and
physical equipment are unchanged.

Final unchanged regression batch: all eight boundaries PASS; resource includes the
resident passage. [Batch commands](passages-fixed.json), [completion](passages-fixed-runner.log),
[lock scenes and 50 rounds](regression/lock/result.json), and [support result](regression/support/result.json).
The executed mounted verifier was separately scanned for the development private
key ([result](mounted-binary-key-custody.json)); the immutable base-image scan alone
would not cover a separately mounted binary.

Exact merge CI, both attempt1: platform [36017648598](https://github.com/jack0682/rx-platform/actions/runs/36017648598)
402/0/16; solutions [36018722975](https://github.com/jack0682/rx-solutions/actions/runs/36018722975)
420/0/20. [Source publication receipt](source-publication.json), [platform run metadata](platform-merge-ci.json),
[solutions run metadata](solutions-merge-ci.json), [platform raw log](ci-platform-merge.log),
[solutions raw log](ci-solutions-merge.log). Contribution and merge trees are identical;
OpenPGP signatures and author DCO were checked. SDK111 files equal a fresh export.
No CI rerun hid a failure: initial and corrected source revisions have separate
first-attempt CI records, while both local implementation failures remain above.

Supplemental attribution control: [exact-ID attacker result](exact-id-attack/result.json)
uses a cryptographically valid attacker signature **for the exact compiled key ID**,
not merely an envelope edited after signing. OpenSSL independently verifies it
under the attacker public key. A complete mutable Policy document binds that same
ID to the attacker key, and policy/key files plus environment variables are
installed. The current RX verifier still refuses it as release/invalid-signature.
[Command](exact-id-attack/command.json), [policy](exact-id-attack/policy.json),
[public key](exact-id-attack/attacker-public.pem), [raw refusal](exact-id-attack/stderr).
This separates wrong-root refusal from a mere signed-key-ID binding failure.
No development private key is included.
