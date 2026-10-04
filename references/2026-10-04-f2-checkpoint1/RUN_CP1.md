# F2′ CP1 — Docs review and acceptance

2026-10-04. Status: **READY FOR USER REVIEW; NOT ACCEPTED**.
This is the Docs-only checkpoint. No new registry product commands exist yet.
The following commands read the proposal and rerun repository checks; they do not operate
devices, restart the F1 installation or establish CP2/CP3 acceptance.

From a standalone rx_docs checkout on develop:

```sh
git pull --ff-only origin develop
git log -5 --oneline
cat docs/implementation/f2_adapter_registry_cp1.md
cat references/2026-10-04-f2-checkpoint1/baseline.json
python3 tools/check_repository.py
python3 .github/test_repository.py
git diff --exit-code -- docs/contracts
```

The last command only checks local modifications; the baseline receipt records hashes of
the existing execution-v2 documents and their manifest for comparison. No P/S checkout is
needed to review CP1. The static seam check was run separately on the recorded P baseline.

Review the [proposal](../../docs/implementation/f2_adapter_registry_cp1.md) in this order:

1. §§1–3: verified installed package identity and typed command/observation declarations,
   with Host-owned approval, admission and private process protocol. Existing common v2
   and Python v2 retain their meaning; the external provider supplies its own pins/evidence.
2. §4: adapter restart never clears UNKNOWN by itself. Original completion evidence and
   independently established current custody are both required. The positive CP3 loss
   window is after durable SIM completion, before Host/P acceptance; earlier insufficient
   evidence remains UNKNOWN without replay. This limitation is part of the design review.
3. §5: standalone unclamp after confirmed support, 11-node SIM scenario; held replacement
   refused. Same-identity passive restart is distinct from replacement.
4. §6: B0→B1 registry implementation cost separated from B1→B2 S1 core diff=0 and external
   files/lines/commands, compared with F0's unsuccessful 6/63/12 baseline. Installed tools
   only; missing packaging/signing/commission commands are recorded as authoring blockers.

Accept CP1 only after reviewing these decisions. CI and these commands cannot decide
acceptance. CP2 implementation and external package authoring remain stopped until the user
accepts. Any required existing-contract revision/new ledger/state machine/seam increase
must be brought back before implementation.

Execution provenance: Codex authored the proposal and ran the documentation prechecks.
The user owns the checkpoint acceptance decision. No claim of user command execution is made.

Parked in this checkpoint: **1 new item**, hot replacement/migration of held work.
