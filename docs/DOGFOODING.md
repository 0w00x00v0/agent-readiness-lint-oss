# Dogfooding

`agent-readiness-lint` can be run on itself:

```bash
python -m agent_readiness_lint --repo . --out /tmp/self-out --project-name "agent-readiness-lint"
```

The result reflects this repository's actual state (for example, the missing
`LICENSE` is reported as a blocker before the MIT `LICENSE` was selected).

## Possible future checks by related tooling

This repository could later be checked by other internal tools. These are
**possibilities, not configured integrations** — this repo adds no cross-repo
automation, and the tools below may or may not exist yet.

- **agent-pr-contract-gate** — could verify that pull requests in this repo
  follow an agreed PR contract (description, scope, and non-claim conventions).
- **repo-release-command-center** — could track this repo alongside others for
  release and readiness status in a single multi-repo view.
- **public-release-gate** — if such a repo is later created or merged, it could
  act as a final manual gate before any public release, building on
  `docs/PUBLIC_CANDIDATE_CHECKLIST.md`.

## What this repo intentionally does not do

- No calls out to any of the tools above.
- No scheduled jobs, bots, daemons, or webhooks.
- No network, API, token, or telemetry behavior of any kind.

Wiring up any of the above would be a separate, explicit decision made by a
human, not something this repository does on its own.

