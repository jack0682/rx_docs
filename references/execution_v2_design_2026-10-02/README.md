# Execution v2 pre-implementation evidence

These records support the [contract decision](../../docs/contracts/workflow-execution/v2/README.md),
not a claim that v2 has been implemented or injection-tested.

- `sizing-input.json`: compact UTF-8 report lengths, concrete parameter/ref lengths,
  definition digest sets and SHA-256 of the existing A/B compiler inputs. Inputs
  were generated from accepted M2 reports; program templates were compiler fixtures.
- `measure.py`: stdlib-only exact proposed index sizing and explicitly labelled
  extrapolation of v1 payloads. No network requests, runtime changes or resolver calls.
- `sizing.json`: output of `python3 references/execution_v2_design_2026-10-02/measure.py`.
- `legacy-freeze.json`: existing installed Linux v0.4.0-rc.1 image identities and
  hashes of actual P/Executor/Host/BT engine/UI bytes, copied before v2 changes.
  Frozen binaries are retained locally, not committed to this documentation repo.

Legacy images were opened with `docker create --platform linux/amd64 --network none IMAGE_ID`,
then `docker cp` copied `/usr/local/bin/rx-platformd` from P and
`/opt/rx/bin/{rx-executor-service,rx-hostd,rx-bt-engine}` plus `/opt/rx/operator`
from S. Only those temporary containers were removed. No image rebuild, upgrade
or running M2 service restart was performed. UI tree hashing includes fonts and
all other assets: a sorted-key compact JSON map of paths relative to the frozen
directory (`operator/...`) to `{sha256,size_bytes}`, then SHA-256. The manifest
lists entry/JS/CSS/bundle hashes and the full tree digest/count, avoiding a repeated
font inventory. Image content IDs retain the full original filesystem.

The frozen installed runtime is currently stopped. A separate old clean-Linux
container contains an uninitialized LOCAL_SIM installer; it is not evidence for
the resident P/Executor/Host path and is not the counterexample-2 oracle.
The macOS M2 API/Vite pair also does not substitute for that complete distribution.

Required next evidence is actual positive/negative ingress execution against the
frozen bytes. Status remains `FROZEN_NOT_YET_INJECTION_TESTED`. Source commits and
binary hashes establish identity, not conformance or successful operation.
