# Server-side runtime composition acceptance

2026-09-28. Installed CLI → actual P draft/binding APIs → exported compile input → existing process-package assembler. This extends the earlier runtime invocation scene without adding P APIs or a separate authoring database.

The Engineer selected one installed Step twice in sequence. Each occurrence became a distinct Operation alias. The source contains one Sequence and two Operation leaves, with no author-written permit/journal/polling nodes. P supplies the bound Host and intent from its catalog.

The consumer was killed with SIGKILL after P accepted the binding save but before its reply was journaled. A new installed CLI recovered the same source, draft ID, selected order and byte-identical original binding request. Repeated recovery returned the same exported composition. The actual process-package assembler accepted that server-produced input.

[composition.json](composition.json) records the source, P export, assembly result and original binding request. [result.json](result.json) and [runtime-skill-requests.json](runtime-skill-requests.json) retain the separate existing-process execution/recovery scene. [tested-sources.json](tested-sources.json) identifies tested source bytes. Images and source correspondence were checked before the scene; the consumer was extracted from the image.

The client suite also exercises missing Step rejection before draft mutation, changed order under one request, installation/store change, and a stale server export despite locally saved receipts. Seven client tests and repository checks passed.

## Boundaries

This is draft composition using already installed Steps, not registration of a new native implementation. The newly composed draft was assembled but not signed, reviewed, activated or executed. Execution evidence in result.json belongs to the previously approved process and must not be used as evidence that the new draft executed. The repeated Step is a composition/control test, not the four distinct rx_poc material-handling skills. Dynamic business inputs/outputs, observation provenance, new device-skill registration, runtime KPI integration and a complete installer remain incomplete. No physical equipment was operated. Container cleanup is not a normal site shutdown test.
