# Actual Python package intake and software report acceptance

2026-09-29. An actual Linux SDK environment was prepared inside the S image from a separate fixture wheel, assembled by the shipped Python device-package CLI, and externally signed by a test-only signer. The private signing key was never mounted in a runtime image.

A separate actual P container imported the signed package through the public registered-terminal mTLS API. Its immutable store returned AWAITING_REVIEW. P's returned device catalog equals the signed original, and repeated intake returns the original receipt. No Run or qualification was created.

P created a device-review request bound to its current installation/configuration/policy. The installed S verifier consumed that exact request and immutable package, checked source consistency, and produced an unsigned software report. An external test signer signed the report; P verified and accepted it as ready_for_software_approval. Repeating submission returned the same report version. The decision remains absent and activation_authorized remains false.

[result.json](result.json) includes P intake/catalog/report records and actual lifecycle shutdown. [package-build.json](package-build.json) identifies the S image. [manifest.json](manifest.json), [device-catalog.json](device-catalog.json) and [sources.json](sources.json) preserve package/source identities. Fixture-exporter formatting was normalized after the scene; product P runtime code was unchanged.

The test configured public test trust only during fresh installation, never by writing P database authority rows or replacing live trust. This is software-review readiness, not an independent human approval, configuration activation or an executed Python operation. SDK deployment to the target Host, review approval/binding/application, complete P/Executor/Host dispatch, typed output/KPI integration and a supported installer remain incomplete. No physical equipment was operated.
