# Runtime skill bridge acceptance — 2026-09-28

Actual installed CLI → registered-terminal mTLS → P → Executor → Host, using FILE_SIMULATION. This is not a physical qualification or a complete installer release.

The selected images were checked against their embedded source inventories. The client was extracted from the solutions image. Commissioning used public package intake, independent review and activation routes with test-only signing materials; P authority was not seeded through database writes. Container cleanup is not evidence of a normal site shutdown.

## Observed result

- The consumer was killed with SIGKILL after an actual P StartRun response and before durable response storage.
- A new client recovered the original stored request bytes and original Run ID. Repeated recovery produced no additional native effect.
- A distinct request completed a distinct Run. The two total native effects correlate to exactly the two P operation IDs and two unique native invocation IDs.
- P reported COMPLETED; each operation reported SUCCEEDED and RELEASED, with CONFIRMED_COMPLETED part disposition.
- The unconfigured PHYSICAL cell was rejected before the runtime invocation scene. No physical equipment was attached or operated.

[result.json](result.json) contains P projections and independent Host effect records. [runtime-skill-requests.json](runtime-skill-requests.json) records the original start request and recovered reply. [tested-sources.json](tested-sources.json) identifies the source bytes at execution, including changes not yet committed at that point.

## Failure found before this passing run

The first execution reached the real native effect, but the client rejected recovery because it compared StartAttempt.expected_run_revision with the pre-start request revision. P stores the incremented revision used by the pending arm attempt. The client now validates that exact successor; a negative client test rejects the pre-start revision. The installed image was rebuilt and the complete scenario rerun.

## Reproduction

From rx-platform, with the selected runtime validation images built from rx-solutions/docker/RuntimeSkillValidation.Dockerfile:

```sh
python3 tools/test_runtime_skills.py \
  --platform-image rx-runtime-skill-platform:dev \
  --solutions-image rx-runtime-skill-solutions:dev \
  --solutions-source ../rx-solutions \
  --evidence ../.build/runtime-skill-acceptance-new
```

## Incomplete scope

Only an already approved bound process is callable, with a material count inside its installed envelope. Dynamic skill arguments, independent device-skill registration, observation-data flow, and skill-level composition inside the existing executor remain incomplete. Consumer receipt loss is exercised; P/Host restart reconciliation is not established by this scene. The images are integration-test images, not a published one-command P/Host/Executor distribution. LOCAL_SIM process/KPI evidence must not be substituted for these missing runtime features.

## Supplemental checks

The platform full Rust workspace passed `tools/cargo test --workspace --all-features --locked`. Formatting, repository checks, contract baselines and the 118-file cross-repository SDK comparison passed. The client journal suite passed four tests, including the mismatched start-revision negative control. These checks supplement the installed runtime scene; they do not establish physical readiness or the incomplete scope above.

## Committed source correspondence

All recorded tested source hashes were compared with the committed files and matched. Documentation and CI wiring were added after the runtime scene.

- [rx-platform 5cd872456e67](https://github.com/jack0682/rx-platform/commit/5cd872456e67cecdb9089c739bd1113163e5e9f5)
- [rx-solutions 6f3bcb89d37b](https://github.com/jack0682/rx-solutions/commit/6f3bcb89d37ba94421b427058cd86a20efa16ff5)
