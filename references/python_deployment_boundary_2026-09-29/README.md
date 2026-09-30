# Python process reaches the Host replacement boundary

2026-09-29. Live P APIs accepted the reviewed Python device package and the installed CLI composed its reviewed binding. The actual S process-package tool assembled, signed and reviewed that v2 compile input. A separate test reviewer approved the process, reviewed its impact and staged the resulting configuration change.

Preparation then returned HTTP 409, CAPABILITY_MISSING. The current change explicitly reports HOST_BINDING_CHANGE_REQUIRED and carries the exact [Host binding plan](host-binding-plan.json). This is an observed unsupported transition, not a successful deployment. Active configuration, Runs and qualification remained unchanged. [result.json](result.json) retains the package/process reviews, staging and refusal.

The Host inspector source now recognizes PYTHON_SKILL_PACKAGE when comparing the selected signed package/catalog against a plan; existing service tests and clippy pass. That source extension was not rebuilt into the S image used for the recorded staging scene. The scene's image IDs identify its exercised runtime. [sources.json](sources.json) identifies current follow-up implementation commits.

## Required implementation next

The existing Host maintenance path only prepares/cancels a replacement after a durable normal-stop seal. It has no commit transition. P intentionally refuses configuration preparation while a Host binding replacement remains. Do not remove either guard to label deployment complete.

A completion path must retain delivery/evidence journal identities and old receipts; compare the exact approved plan and before/after configuration; reject missing/stale stop proof or unresolved native work; persist replacement intent and recovery state before modifying metadata; never restore Arm/qualification on restart; and provide a fresh Host-owned observation that P correlates with the original staged change. Interrupted commit/restart and stale or forged confirmation must be tested. If the wire contract changes, record revision/compatibility and synchronize the SDK/manifest rather than silently changing the existing snapshot.

The existing runtime architecture is the starting point, not a reason to expose these internal steps in the developer's BT. The final user path still needs one-command installation, Python+SDK registration, simple composition, outputs and per-skill KPIs. No physical equipment was operated.
