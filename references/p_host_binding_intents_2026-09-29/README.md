# P-issued binding intents and metadata comparison

2026-09-29. P now allocates a durable original request for each staged change/Host through a registered-terminal ReleaseManager API. The live P image returns the same records on retry, rejects an unauthorized issuer and rejects changed content under the same mutation key. Records remain AWAITING_BASELINE with activation_authorized false; the existing deployment refusal is preserved.

The comparison policy checks read time/current P runtime, authenticated-registration context supplied internally, complete cell identities, original request/plan/configurations, changed Host boot and continuity of both journals. Four policy tests exercise valid matching and mismatched identity, request, plan, configuration, journal, cohort, stale time, missing baseline and an already committed request masquerading as its own before-state. These policy tests are separate from live transport collection.

Optional Host configuration binding revision 3 exposes the evidence journal before replacement, allowing P to compare both original journals instead of inferring one. The 118-file SDK was regenerated. Frozen base/cell manifests remain unchanged.

[live-api.json](live-api.json) records actual request allocation in the Python package/process staging scene. [checks.json](checks.json) and the included logs record source and check scope. Domain/application and Host tests passed, with clippy and SDK checks.

The transport worker is not yet wired to collect baseline/after reads for these records. No public API accepts an uploaded observation as a confirmation. Fences, current confirmation revalidation and deployment-admission integration remain unfinished, as does adoption after P restart without replacing the original request. Metadata matching is not application, qualification or execution authority. No physical equipment was operated.
