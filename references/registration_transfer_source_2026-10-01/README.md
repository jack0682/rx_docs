# Source-side registration freeze evidence

2026-10-01. [Source identities](sources.json) identify the clean implementation
commits. [Result](result.json) and [commands](commands.json) exercise copies of a
completed R4 Ubuntu arm64 registry with the exact prior signed daemon image.
The original data inventory is hashed before and after and remains unchanged.

The old daemon reads the unfrozen positive control and exits normally. The new
local CLI freezes another copy, retaining original registration IDs/revisions and
a history cut. Exact retry returns the same result; a different target is refused.
The same old daemon then refuses schema 7 with `newer store schema: downgrade
refused`. Reading the frozen source afterward returns the original result.
No PID is adopted, no P acceptance occurs and no physical equipment is attached.

Local full-workspace checks: Platform 513 passed / 0 failed / 18 ignored;
Solutions 421 passed / 0 failed / 19 ignored before the final malformed-source
negative test. Both focused source tests passed afterward. Full-workspace clippy,
repository tests, frozen contract hashes and 125-file SDK comparison passed.
Storage tests cover namespace DML refusal, ordinary schema-6 preservation,
rollback after callback/partial DDL failure, sibling writes and malformed guards.

This is a source preparation boundary only. A JSON export is not proof to P of
a live source fence. Registered-source verification, P import with original
revisions/history, acceptance recovery and P execution assignment remain required.
The current CLI is a development tool and is not invoked/installed automatically.
It has no unseal or P-acceptance command. Whole-store restore/privileged schema
replacement are outside this per-file fence and remain separate framework work.
