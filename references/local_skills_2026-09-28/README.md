# Local simulation skill installation evidence

`arm64-local.json` records the clean arm64 bundle acceptance against platform
`09353b4fe23d001340ce4868a805d44a490a22bb` and solutions
`f66d76488f9958485042a7364d93ff6efdfca13b`. The embedded release descriptor identifies
the image and confirms the source checkouts were clean. It contains no credentials.

The nine acceptance groups cover installation, client/worker identity separation,
external source execution, original-request replay, immutable version and physical
scope refusals, discarded admission responses, actual exceptions/schema errors and
deadline expiry, installation restart, and a killed worker followed by a distinct
new request. The final group inspects non-root/read-only/no-device/no-socket
container configuration. No physical equipment was operated.

The release's architecture-specific `acceptance-*.json` and `release-*.json` files
are the final CI-built distribution evidence; this local result does not replace
them. Source and package limits are described in the [installation guide](../../docs/local_skill_installation.md).
