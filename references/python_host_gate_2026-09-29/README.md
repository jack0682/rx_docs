# Python SDK behind the actual Host gate

2026-09-29. The Rust PythonSkill adapter invokes the pinned Python helper only from the existing Host authorization path. An independently installed fixture SDK appends a durable effect in a separate file; the adapter's support observations come from FILE_SIMULATION and are not physical facts.

The actual gate tests show no SDK effect after prepare or foreign-caller authorize, one effect after valid authorization, and no duplicate effect after repeated authorize/reconcile. A timeout retains SendEntered and refuses handover; modified Python environment code is rejected before an SDK effect. Python subprocess tests separately cover SIGKILL after the SDK effect, SDK exception, busy-before-marker and expired dispatch. Calls with an existing uncertain marker are never re-executed.

The adapter pins the interpreter, runner, environment verifier and original ProgramGoal/input, bounds pipe output/deadlines, and reads original receipts on reconciliation. Linux dispatch expiry includes suspend through BOOTTIME. A process group is signaled only while its original leader remains unreaped; physical stop/support is not inferred from killing it. Reopening conservatively retains unresolved custody.

[checks.json](checks.json), [gate tests](python-host-tests-final.log), [Host suite](python-host-suite-final.log) and [clippy](python-host-clippy-final.log) record exercised checks. Logs substitute the workspace path for portability.

## Not yet established

The registered service Backend/AdapterFactory path is not wired. P registration, typed output/observation propagation, operator reconciliation, native system-library release pinning and a complete installer remain incomplete. The adapter rejects physical support and is not a hostile-code sandbox. These library/gate tests do not replace installed P/Host/Executor admission evidence. RETURNED records Python return, not physical device completion.
