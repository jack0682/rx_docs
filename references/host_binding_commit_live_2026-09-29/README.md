# Live Host binding commit confirmation (S3-S5)

2026-09-29. The live image acceptance with `--binding-commit` ran three times and passed each time ([live-runs.json](live-runs.json); first run in [live-api.json](live-api.json)). In each run:

1. A ReleaseManager approves re-admission of the baselined Host generation bound to the P-issued binding intent; the same request without the role is refused.
2. The FILE_SIMULATION Host stops normally (StopSeal). `rx-hostd prepare-binding-change` and `commit-binding-change` run with the P-issued request ID; a commit retry returns the same record.
3. The Host restarts on the proposed startup with the signed Python package backend; the profile's Python environment is installed at its pinned absolute path.
4. P re-links the new boot under the approval, and the worker's read reaches `METADATA_MATCHED` with the committed boot, the original request and both kept journals. The change detail drops `HOST_BINDING_COMMIT_UNCONFIRMED`.
5. A refreshed preparation fences the new boot and its acknowledgement clears the fence blocker. configure-hosts and apply stay refused with 409 `CAPABILITY_MISSING`; `activation_authorized` stays false and the change stays STAGED.
6. Restarting the Host again without a new approval demotes the Host to `HOST_BINDING_COMMIT_UNCONFIRMED` and a refresh is refused with `CONTINUITY_UNPROVEN`. P stays running; its stop then reports `HOST_FENCE_UNCONFIRMED` for the unadmitted boot and exits 2.

Regression runs (connected Host, Host unreachable at stop, no Host), workspace tests (0 failed), workspace clippy, fmt, repository checks and the 118-file SDK comparison passed ([checks.json](checks.json)).

Not exercised: a restart without change before any commit as a separate run, S6 configuration dispatch and S7 apply, adoption of intents after a P restart. No physical equipment was operated.
