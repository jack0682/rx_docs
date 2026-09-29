# Host restart before the binding commit

2026-09-29. A code review found a dead end in the Host binding change. After the baseline was recorded and the change fenced, a Host restarted without a commit (for example a power loss) could be registered again by a plain re-admission, but the binding re-admission then accepted only the baselined boot. That boot was no longer the registered generation, so no approval could satisfy both conditions and the change could not finish.

Change (rx-platform 82cee39): before the commit is confirmed, the replaced generation may be the currently registered boot if it keeps the baseline's delivery and evidence journals. The commit read still has to name the baseline installation identity, so a different replacement in between would be refused with `INSTALLATION_CHANGED` (read from the code, not exercised). A confirmed commit still requires the exact boot.

Live image acceptance `--binding-commit --host-restart-before-commit`, five consecutive passes ([live-runs.json](live-runs.json); first pass in [live-api.json](live-api.json)):

1. stop and restart the Host on the unchanged startup; plain re-admission (no binding);
2. the request reads `MISSING_COMMIT` and keeps its baseline; refresh is refused with `CONTINUITY_UNPROVEN`;
3. a binding re-admission naming the baselined boot is refused with `CONTINUITY_UNPROVEN`;
4. the binding re-admission naming the restarted generation is accepted, the Host commits, and the flow reaches `METADATA_MATCHED` and then `APPLIED_UNQUALIFIED`. P stops with exit 0.

The same sources without the engine change refuse step 4 with `CONTINUITY_UNPROVEN` (counterfactual image). Three earlier runs failed because of a harness bug, not the product: the harness took the `HOST_NOT_RESTARTED` read of the old boot as the restarted Host's read and asked for the binding re-admission before the plain approval was consumed (`BUSY`). The harness now waits for `MISSING_COMMIT`.

Also committed (rx-platform ee8ba05): an engine test that re-admission is refused while a Run executes with unresolved work (removing the check makes it fail), and a unit test of the relink decision. The regular `--binding-commit` run, workspace tests (439 passed, 0 failed), clippy, fmt and repository checks passed ([checks.json](checks.json)). No physical equipment was operated.
