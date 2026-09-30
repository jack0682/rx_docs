# Python SDK signed device declarations

2026-09-29. Python registration can now be assembled into the existing DEVICE_REFERENCE format with a common operation catalog. No separate P skill database or new package ABI was introduced.

The actual python-assemble CLI produces the same deterministic candidate as the library. External test signatures are verified, original/derived documents are reassembled, and the Host package loader checks current policy and selected manifest. Negative controls reject signed inconsistent operations, changed input/environment/architecture and removal of the trusted signer. Profile identity is derived from the declaration; environment content, target and version remain bound.

[checks.json](checks.json), [package tests](python-package-tests-final.log), [clippy](python-signed-package-clippy.log) and [workspace check](python-package-workspace-check.log) record this scope. The package fixtures are metadata-only. Actual SDK execution is covered by separate earlier gate tests and is not inferred from these package results.

Live P intake/review of this new family, server-side SDK transport/installation, an installed signed-package Python dispatch scene, dynamic output and complete installation release remain incomplete. The package and Host loader continue to require simulation declarations. No physical equipment was operated.
