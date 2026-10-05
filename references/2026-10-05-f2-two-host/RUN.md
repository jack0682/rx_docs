# Code-free two-Host product Run prerequisite

Codex executed these product commands on the user's Mac. This is an automated prerequisite
check, not user CP2 acceptance. The user accepted the preceding scope decision.

Run `01a10a14-0c8c-72b7-8810-d08b5a0440cf` completed one Part with nine
SETTLED/SUCCEEDED/RELEASED operations: pick/load/rotate-align on Host A, clamp on Host B,
then close-door/process/open-door/unload/place on Host A. Both processes use the identical
existing rx-hostd binary. P/Host/Executor source changes for this check: **0**.

Evidence: [summary](summary.json), [Run receipt](two-host-run.json),
[reopened receipt](two-host-reopened.json), [effects](effects.jsonl),
[executed command](run-command.json), [file hashes](sha256.json).

Reopen the existing Run with the installed product CLI:

```sh
pre=/Users/ojaehong/RX_automation/rx_ws/.build/framework-f2-two-host
python3 "$pre/live3/verification/installed-client/rx" execution \
  --connection "$pre/live3/operator.json" --state-dir "$pre/live3/operator-client" \
  inspect 01a10a14-0c8c-72b7-8810-d08b5a0440cf --reports
```

The exact original Run command (same request ID queries/resumes its original identity):

```sh
python3 "$pre/live3/verification/installed-client/rx" execution \
  --connection "$pre/live3/operator.json" --state-dir "$pre/live3/operator-client" \
  run "$pre/author3/publication.json" --count 1 \
  --object "$pre/author3/object-precheck-1.json" \
  --request-id 0f359b7d-3c14-483f-aca8-ff63f8a807f6 --wait-seconds 120
```

No new request ID is needed to reopen this result. Original execution took about 20.24 s.
The fixture is detached under the Docker daemon (`rx-f2-twohost-p`, `-ha`, `-hb`, `-e`),
separate from the preserved F1 CP3 installation. It shares a SIM device volume between
these two Hosts, while Host journals and owned process custody are separate.

Limitations: both providers are the existing Python builtin, not the registry. This uses
the historical nine-step S2 package and does not exercise the newly split support actions.
**There is no fresh support observation.** Later F2 SIM unclamp relies only on the same
Part's SETTLED/SUCCEEDED acquire-support ordering, weaker than a real cell requires.
N=3 mixed-model S1 operation, Host A waiting while Host B is UNKNOWN, and both CP3 fault
windows remain unverified. Setup used test-only signing fixtures; it is not evidence for
the installed-artifacts-only external S1 authoring requirement.

Two setup mistakes were corrected before running: the disposable CA lacked a keyUsage
extension and the copied HTTPS origin retained the old port. TLS/origin verification was
not bypassed. These were configuration errors, not runtime code changes or failed Runs.
