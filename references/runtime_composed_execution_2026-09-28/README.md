# Online-composed process activation and execution

2026-09-28. This scene closes the earlier gap between the newly authored draft and the separately executed pre-existing process.

Before starting P, the test pins the expected two-operation process, its package and qualification target using test-only material. After P/Host/Executor startup, the installed Engineer CLI creates that process through public draft/binding APIs and exports the actual server-produced compile input. The actual package assembler consumes this online export; both input bytes and reassembled manifest digest must equal the predeclared values before any package review. Runtime authority is never written through direct database access and the live qualification policy is not replaced.

The existing public package intake, signed compiler report, independent review, configuration application and six-area simulation qualification/activation path then processes that exact package. The Operator CLI invokes the now-installed process. Each of two Runs produces two distinct operations and two independent native FILE_SIMULATION effect records. The first consumer is killed after StartRun response but before storing its receipt; cold recovery retains its Run and request, and repeated recovery produces no additional effects. A fresh request alone produces the second Run. All four P operations correlate to the four native effects.

- [installed-composition.json](installed-composition.json): online P export and reassembled package identity.
- [commissioning.json](commissioning.json): actual public activation receipt.
- [result.json](result.json): original/new Run, installed draft ID, exact package binding and independent effects.
- [runtime-skill-requests.json](runtime-skill-requests.json): lost receipt and original-request recovery.
- [tested-sources.json](tested-sources.json): source identities used for this scene.

The product P runtime is unchanged in this extension. Its existing process-change logic already handles multiple operation nodes. Only the single-operation test expectation was generalized to a bounded operation sequence. Affected fixture compilation/clippy and repository checks passed.

## Remaining boundaries

The source repeats one installed Step twice to verify distinct operation identity and sequencing; this is not four different rx_poc device skills. The runtime still uses fixed approved inputs. New native skill implementation registration, dynamic business/observation data, runtime KPI integration and a complete installer remain incomplete. The authoring CLI does not yet automate package signing, review or activation: this scene uses existing public test tooling for those steps. Test-only external signing materials are not a production signing service. No physical device was attached or operated, and container cleanup is not a normal site shutdown test.
