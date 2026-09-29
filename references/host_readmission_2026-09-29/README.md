# Restarted Host re-admission and binding transition link

2026-09-29. See [the design record](../../docs/host_binding_admission.md#재수용-구현과-남은-host-쪽-차단-2026-09-29) for the rules. [checks.json](checks.json) lists the source commits, engine tests, mutation results and the live regression runs; [workspace-tests.log](workspace-tests.log) holds the per-binary results (0 failed).

The live `--binding-commit` acceptance approves the re-admission (and refuses it without the ReleaseManager role), stops the FILE_SIMULATION Host normally and writes the proposed startup and approved plan into the Host volume. It then stops at `rx-hostd prepare-binding-change`, which cannot acquire the signed Python package directory inside the container when the package contains a subdirectory, and whose code-level file limit (8) is below the reviewed package (10 files); the latter is read from the code, not yet observed as a failure. No live S4 confirmation, S5 refresh or demotion result exists yet. No physical equipment was operated.

Correction (same day): both suspected causes above were wrong. The package directory and file limit are accepted; the failure came from the signed profile's Python environment being absent at its pinned absolute path inside the Host container. See [the live S3-S5 record](../host_binding_commit_live_2026-09-29/README.md).
