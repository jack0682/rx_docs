# Live Host binding change configuration and application (S6-S7)

2026-09-29. The `--binding-commit` live acceptance now runs a Host binding change from intent issuance to application. Five consecutive runs passed ([live-runs.json](live-runs.json); first run in [live-api.json](live-api.json)). After the S3-S5 steps of the [earlier record](../host_binding_commit_live_2026-09-29/README.md), each run:

1. restarts the committed Host without approval: the Host is demoted, refresh is refused with `CONTINUITY_UNPROVEN` and configure-hosts with `CAPABILITY_MISSING`;
2. re-admits the confirmed commit generation, re-confirms `METADATA_MATCHED` on the next boot and refreshes the fence;
3. configures the Host (the Host reports `APPLIED_UNQUALIFIED`) and applies the change: the change is `APPLIED_UNQUALIFIED`, the P cell configuration equals the change's after configuration, the only blocker left is `REQUALIFICATION_REQUIRED`, and `activation_authorized` is false. P then stops with exit 0.

Before the final fix one of three runs failed: a transport-loss read had rewritten the confirmed commit back to `BASELINE_RECORDED`, so the second re-admission was refused with 409. Reads no longer rewrite a confirmed commit.

Regression runs, workspace tests (0 failed), clippy, fmt, repository checks and the SDK comparison passed ([checks.json](checks.json)). Not exercised: P restart adoption, qualification activation and skill execution after application, and an engine-level test of the barrier with a binding plan. No physical equipment was operated.
