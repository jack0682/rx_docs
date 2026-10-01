# W02 workflow canvas and versioned presentation

2026-10-01. [Validation and source identities](validation.json) retain the exact
feature and integrated trees, PR CI runs, local checks and browser observations.

- [Platform #70](https://github.com/jack0682/rx-platform/pull/70) merged as
  `7b838764ec6f5e7223b9b9f21a2d1b94f9e86439`.
- [Solutions #79](https://github.com/jack0682/rx-solutions/pull/79) merged as
  `1f0b519772c3890bf1191c364bb580db14157c5e`.
- Both merge commits passed the repository merge tool's exact-head CI, DCO,
  conflict/base checks and post-merge OpenPGP/author-DCO verification. Their code
  trees equal the tested feature trees.
- Linux workspace results: P 531 passed / 0 failed / 22 ignored;
  S 475 passed / 0 failed / 22 ignored. S operator and installed-skills jobs passed
  for their declared scopes, including amd64/arm64 installed-skills checks.
- Local P workspace: 530/0/19; full clippy/format and repository/contract/engine/
  manifest checks passed. SDK 130 files match. UI typecheck, 57 unit tests,
  3 bundle tests and production build passed.

The actual UI used the paired P writer and SQLite. A separate copy of a test
draft was moved with keyboard controls, reordered, saved and reloaded. Coordinates
and authored arrows returned unchanged. After normal API termination and restart
on the same installation, reauthentication and the same draft read restored them
again. The laser dual-gripper cycle was opened and the wrapped sequence inspected.
Sequence order, parallel/branch joins, repeat return/exit, malformed structures and
viewport folding also have targeted projection tests. Join markers are derived
views of v1 control structure, not executable nodes or actual completion evidence.

W02 covers structured source editing and immutable presentation storage. Layout
and labels do not define execution order. A layout save increments draft revision,
so exported compile-input provenance changes even when source/binding content does
not. This is not byte identity of the entire compile-input envelope.

The full Python browser suite was not run. Browser observations are scoped to the
listed scenes. This change does not implement Failure/Timeout/Event ports,
Parallel Any, conditional loops, the full definition/resolver catalog, a new
installer release, physical commissioning or the complete framework goal.
The laser examples retain missing deadlines and operation bindings.

An observed follow-up belongs to W14's existing session/operations UX scope:
the invalidated development login after API restart displayed "Cannot validate
the response format" before sign-in. Data restoration passed after sign-in;
that misleading expiry/error explanation remains a separate defect, not a
completed recovery UX claim.
