# Public Candidate Checklist

This document tracks the readiness of `agent-readiness-lint` as a *candidate* for
eventual public release. It is an internal review aid, not a release approval.

## Status

**Public-release candidate. Human review is still required before relying on it in production or presenting it as mature.**

This checklist records best-effort, static observations about the repository. It
does **not** assert that the project is production-ready, secure, adopted, or
eligible for any particular program, platform, or partner ecosystem.

## What this checklist is not

- It is **not** a security review or a security scan.
- It is **not** a production-readiness sign-off.
- It is **not** a statement of adoption, popularity, or maturity.
- It is **not** an eligibility claim for any external program or vendor (for
  example, no claim of OpenAI/Codex eligibility is made or implied).
- It is **not** a security, production, adoption, or eligibility claim. Licensing is governed by [`../LICENSE`](../LICENSE).

## Reviewed (best-effort, static)

These items have been checked by reading the repository contents only. They
reflect structure, not guarantees of behavior or quality.

- [x] README documents purpose, quick start, output files, and limitations.
- [x] README and `AGENTS.md` state explitests/CIt non-goals (no network, API keys,
      tokens, telemetry, code execution, or SaaS behavior).
- [x] No agent/editor artifact directories are tracked
      (`.agents/`, `.kiro/`, `.codex/`, `.cursor/`).
- [x] No build/output/cache artifacts are tracked
      (`out/`, `logs/`, `__pycache__/`, `.venv/`, `*.egg-info/`).
- [x] `.gitignore` covers the common generated/output and secret patterns.
- [x] Source contains no network, subprocess, or dynamic-execution calls
      (no `requests`/`urllib`/`socket`/`subprocess`/`eval`/`exec`/`os.system`).
- [x] The tool reads target repositories only; it never executes target code.
- [x] A compact, fictional example is documented in
      [`EXAMPLES.md`](EXAMPLES.md) with no real or private data, and no
      generated output is committed.
- [x] An offline tests/CI workflow runs `ruff` and `pytest` with no secrets and no
      release/publish steps (`.github/workflows/tests/CI.yml`).
- [x] Test suite passes locally and is deterministic/offline.

## Requires human detests/CIsion before release

These items are intentionally left open and must be resolved by a person.

- [x] **License.** MIT license selected; see [`../LICENSE`](../LICENSE).
- [ ] Confirm the intended public repository owner, name, and clone URL in the
      README.
- [ ] Detests/CIde whether community files (`SECURITY.md`, `CONTRIBUTING.md`,
      `CODE_OF_CONDUCT.md`, issue/PR templates) are required for the intended
      audience.
- [ ] Independent human review of the heuristics, scoring weights, and output
      wording for accuracy and tone.
- [ ] Confirm no proprietary, internal, or sprint-spetests/CIfic references remain in
      docs or code.

## Notes

- All findings above are best-effort and may produce false positives or miss
  issues. Treat this checklist as a starting point for human review, not a
  substitute for it.




