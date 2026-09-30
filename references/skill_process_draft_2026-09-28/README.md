# Serial skill process draft acceptance

This is a clean-source **unreleased** `0.4.0-dev.1` candidate, tested on an arm64
Linux Docker engine. It is not a new public release or full-framework acceptance.

- [Installation acceptance](result.json): source commits, image identity and 12
  named acceptance groups, including existing single-skill regression coverage.
- [Process evidence](processes.json): two different material inputs, original
  parent/child identities, actual failed/unknown skill outcomes and per-version
  metric projections. These are logical Python computations, not device facts.

The process is acquire → load → release → unload. The native worker launches a
separate Python process for each registered skill. Recorded inputs demonstrate
that successor inputs come from the matching predecessor in the same process.
The acceptance checks the worker log to ensure one launch per child on replay.

For `restarted`, both actual server and worker containers were killed while the
second skill was executing. After restart, the first result and all original IDs
remain unchanged, the second is UNKNOWN, and the final two have no execution.
Repeating the original process request does not restart the first or second skill.

The metrics record separates version 1 successes/failure from the timed-out
version 2. Known-outcome success rates exclude UNKNOWN and expose their numerator
and denominator. The report does not measure good-part yield or physical timing.

The test command is `python3 tools/test_skill_install.py --bundle BUNDLE --evidence
NEW_DIRECTORY` from the matched solutions source. The bundle is produced with
`tools/build_skill_release.py --platform PLATFORM --architecture arm64 --output
NEW_DIRECTORY`. Actual physical devices, P/Host/Executor integration, resource
handover and general control flow remain outside this evidence.

The [full draft audit](../../docs/skill_framework_draft_audit.md) remains open.
