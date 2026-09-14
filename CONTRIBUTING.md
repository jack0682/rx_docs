# Contributing

RX is a personal project for heterogeneous robots and infrastructure. Contributions use Apache-2.0. Consult the repository README and implementation records for the current validation scope.

## Branches and GitFlow

| Branch | Purpose | PR target |
|---|---|---|
| `main` | Stable baseline and release history; default branch | PRs only |
| `develop` | Integration and validation of upcoming work | `main` when ready |
| `feature/*`, `fix/*`, `docs/*`, `chore/*`, `codex/*` | Work created from `develop` | `develop` |
| `release/*` | Release preparation created from `develop` | `main`, then carry fixes into `develop` |
| `hotfix/*` | Urgent fixes created from `main` | `main`, then carry fixes into `develop` |
| `dependabot/*` | Dependency proposals from this repository | `develop`; security fixes may target `main` |

All PRs use merge commits. Squash and rebase merges are disabled so that reviewed commits, signatures and signoffs retain their identities. A small release can use a `develop` to `main` promotion PR without a release branch. After promotion, merge `main` back to `develop` through a PR.

## Signed commits and the daily workflow

Every commit, including merges, needs both a matching author `Signed-off-by` trailer and a verified OpenPGP signature. Read the [Developer Certificate of Origin](https://developercertificate.org/) before signing off. The trailer records your certification of contribution rights; the cryptographic signature authenticates the commit. Neither substitutes for the other.

Configure a verified GitHub email and register your public GPG key, then install the repository's local hooks. See the [repository governance guide](GOVERNANCE.md) for key setup, branch updates, merge and recovery instructions.

```sh
python3 tools/install_git_hooks.py
git switch develop
git pull --ff-only origin develop
git switch -c feature/your-change
# Make the change and run the checks below.
git add <changed-paths>
git commit -s -S -m "Describe the behavior change"
git push -u origin feature/your-change
# Open a PR targeting develop; wait for CI and DCO.
python3 tools/merge_pr.py PR_NUMBER
```

`main` and `develop` reject direct pushes, force pushes and deletion. A PR needs `CI` from GitHub Actions and `DCO` from the DCO app, an up-to-date base, verified signatures and resolved review conversations. A separate update lock permits the administrator to update these branches only through a PR; that exception does not bypass the quality rules.

The required number of approvals is zero while there is only one maintainer. CODEOWNERS identifies review responsibility. The maintainer still reviews the diff and validation evidence before merging. When an independent maintainer joins, raise the required approvals and enable required code-owner review together.

External forks cannot use names such as `main`, `develop`, `release/*`, `hotfix/*` or `dependabot/*` to acquire this repository's release routes. Submit external changes from work branches to `develop`. Fork CI receives a read-only token and no repository secrets.

## Changes and validation

Describe the problem, resulting behavior, checks actually run and unverified scope. When changing authority, unknown outcomes, stopping, resource handover or recovery semantics, explain counterexamples and compatibility impact.

```sh
python3 .github/test_repository.py
python3 .github/test_commit_policy.py
python3 tools/check_repository.py
```

Documentation CI checks repository content, local links, contract hashes and commit policy. It does not establish design correctness, implementation conformance, external URL availability or physical operating readiness.

## Published content

Keep AI assistant instructions, prompts and local state out of Git. General documentation may use Korean. Shared normative documents must stay aligned with the English platform and SDK copies, including manifests and hashes.

## Changes across repositories

Original designs and contracts live in [rx_docs](https://github.com/jack0682/rx_docs), the platform and contract copies in [rx-platform](https://github.com/jack0682/rx-platform), and adapters, services and the pinned SDK in [rx-solutions](https://github.com/jack0682/rx-solutions). Record the original contract revision, compatibility impact and manifests first, then synchronize platform specs and the solutions SDK. Link related PRs and record compatible commit combinations.

The platform command `python3 tools/check_host_sdk.py ../rx-solutions/sdk` checks agreement with current platform sources. Standalone solutions CI checks its SDK inventory; it does not establish compatibility with the latest platform. Regenerate SDK copies from platform sources instead of editing them directly.

## License and security

Contributions use the [Apache License 2.0](LICENSE). Submit only material you have the right to contribute, and preserve third-party licenses and notices. [NOTICE](NOTICE) contains RX notices and does not replace dependency notices. Do not put credentials, equipment addresses or personal information in public PRs or issues. Follow the [security policy](SECURITY.md) for vulnerability reports.
