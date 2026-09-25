# G4 multi-operating-area execution evidence

See [decision and scope](../../docs/39_multi_operating_area.md). These are actual
software observations, not physical qualification. `inventory.json` hashes the
selected raw files; binaries, private keys, DBs and regenerable build caches are
not published. Exact final binary/image hashes and private-key absence checks are
in `final-binaries.json`, `key-identities.json` and custody logs. Local retained
DBs and the interrupted G1 build target remain available to the paired verifier.

- [22 area scenes](multi-final/result.json): two recipes in one actual Plan, both
  own-area derived commits, same-object cross-area replay, A-legal/B-illegal limits,
  requested-area attacks, foreign roles/programs and foreign-key signatures.
- [Signing-byte isolation](signature-layer-isolation.json): actual Rust canonical
  bytes match the adversarial message; foreign signature independently verifies
  under the foreign key, but receiver rejects it. Full signed response JSON is in
  each scene's mailbox. This isolates key mismatch from JSON encoding mistakes.
- [G3 12 scenes](g3-regression/result.json),
  [original A identity](single-area-compatibility.json), and byte-identical
  [before](before-host-refusals.log)/[after](after-host-refusals.log) host refusals.
- [Before injection](before-injection/result.json) and
  [after injection](after-injection-recovered/result.json); the failed intermediate
  attempt was an engine EIO before product launch, retained separately.
- [Linux declaration tests](catalog-linux-test.stdout) and
  [separate F6 count tests](f6-count-linux-test.stdout). G4 catalog uniqueness is
  not a new uniqueness restriction on generic F6 policies.
- [Privacy errors](opaque-doctest-errors.log): Prepared's four fields all trigger
  E0451, without a missing-field E0063 substitute.
- [macOS counts](mac-counts.json), [Linux PR CI counts](linux-ci-counts.json),
  [SDK freshness](sdk-check.log), and repository/clippy/CI raw logs.
- [Nine prior boundaries](verification-summary.json). Resource includes resident.
  Library output is in `regression-library.log`. The original runner's final G1
  attempt is incomplete; the separate [compact G1 result](lock-compact/result.json)
  contains eleven lifecycle cases and all fifty Host rounds. No tests are omitted
  or serialized. The [builder recipe](compact-builder/Dockerfile) changes only
  debug/incremental build storage, with the exact same parent Rust image and
  unchanged runtime image and passage assertions.
- [Retained incidents](incidents.md): source-edit compile error, explicit ENOSPC,
  Docker EIO, earlier immutable-request fixture refusal, and original G1 wrapper
  exit120 with no captured Python cause. Successful new executions do not erase
  these or establish the cause of G3's historical E0463 incident.

Reproduce from compatible source commits in doc39 with the scripts in
`rx-solutions/tools/multi_area_passage.py`, `operating_area_passage.py` and the seven
prior solutions passage scripts (one includes resident), plus platform's
`tools/storage_lock_passage.py`. Each `commands.json` preserves actual argv and
exit codes; replace local evidence paths with empty writable directories. The
positive real-issuer passages require maintainer-held keys matching the compiled
public pins. Keys are never included here or mounted into the host. Without those
private keys, public unit tests and captured signature verification remain
reproducible; an arbitrary replacement key is expected to be refused.

The fixed native runtime and separately mounted current Rust binaries were used.
A full native image rebuild, operating deployment, network judgment service,
continuous monitor, eight-area physical system and production key custody are not
claimed. Earlier status snapshots are historical; final merge-CI files identify
the exact code heads and first attempts.

The first committed inventory audit found Git newline normalization in two Docker progress logs. Scoped .gitattributes entries now preserve their original bytes; all inventory hashes are checked against Git blobs, not just the working tree. The initial two mismatches remain recorded.
