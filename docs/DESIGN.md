# Design Document

This document explains the scoring algorithm, check boundaries, and design philosophy behind agent-readiness-lint.

## Design Philosophy

The tool answers one question: "Is this repository structured so that an AI coding agent can work with it effectively?"

Key principles:

1. **Local-only.** No network, no APIs, no telemetry. All analysis runs on the filesystem you point it at.
2. **Conservative.** The tool reports only what it can observe directly. When uncertain, it reports "unknown" rather than guessing.
3. **Non-destructive.** It reads files but never modifies the target repository.
4. **Actionable output.** Every finding includes the category, a pass/warn/fail status, and evidence (file paths). Generated reports suggest concrete fixes.
5. **Deterministic.** Given the same repository state, the tool produces the same results (aside from the output timestamp).

## Scoring Algorithm

The overall score is a weighted sum across five categories, totaling 100 points maximum.

### Category Weights

| Category | Max Points | Scoring Method |
|----------|-----------|----------------|
| Agent Instructions | 30 | Ratio-based |
| Test/CI Signals | 20 | Ratio-based |
| Secret Risk | 15 | Deduction-based |
| Public Readiness | 20 | Ratio-based |
| Generated Hygiene | 15 | Ratio-based |

### Ratio-Based Scoring

For most categories, the score is:

```
earned = (pass_count + warn_count * 0.5) / total_items
category_score = round(earned * max_points, 1)
```

- A passing item earns full credit
- A warning earns half credit
- A fail or unknown earns no credit

### Deduction-Based Scoring (Secret Risk)

Secret risk starts at full points and deducts:

- Any fail finding: 0 points (full penalty)
- Any warn finding (no fails): 50% of max (7.5 points)
- No findings: full 15 points

This asymmetric approach reflects that secret exposure is a higher-severity issue where even one failure is significant.

### Strict Mode

When `--strict` is enabled, if any check item has status "fail", the final score is capped at 59. This prevents a repository from reaching "Needs minor cleanup" or "Ready" status while unresolved failures exist.

### Score Labels

| Range | Label |
|-------|-------|
| 80-100 | Ready |
| 60-79 | Needs minor cleanup |
| 40-59 | Needs major cleanup |
| 0-39 | Not ready for agent work |

## Check Categories

### 1. Agent Instructions (30 points)

**What it checks:**

- Presence of any agent instruction file: `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, `.github/copilot-instructions.md`
- Within the primary instruction file, keyword-based detection of seven sections:
  - Project purpose
  - Setup commands
  - Test commands
  - File boundaries
  - Generated files
  - Secrets/private data warnings
  - Non-goals

**What it does NOT check:**

- Quality or accuracy of the instructions
- Whether instructions are up to date
- Whether an agent can actually follow them

**Why 30 points:** Agent instruction files are the single most impactful factor in agent effectiveness. Without them, agents operate blind.

### 2. Test/CI Signals (20 points)

**What it checks:**

- Presence of test files (`test_*.py`, `*_test.py`, `*.test.js`, `*.test.ts`, `*.Tests.ps1`, `tests/`, `__tests__/`)
- Presence of CI configuration (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`)
- Test framework detection from dependency files (`pyproject.toml`, `package.json`, `requirements.txt`)
- Inferred test commands

**What it does NOT check:**

- Whether tests pass
- Test coverage
- CI pipeline correctness

**Why 20 points:** Agents that can verify their changes via tests produce significantly better results. CI integration provides an additional safety net.

### 3. Secret Risk (15 points, deduction-based)

**What it checks:**

- Suspicious filenames: `.env`, `id_rsa`, `*.key`, `*.pem`, and patterns matching tokens, secrets, credentials, cookies, sessions, or private keys
- Content markers in text files under 100KB (first 50 lines): `AWS_SECRET`, `PRIVATE KEY` headers, `password=`, `api_key=`
- Only scans within the `--repo` path

**What it does NOT check:**

- Encrypted or properly vaulted secrets
- Environment variables at runtime
- Git history for previously committed secrets
- Whether detected files are actually sensitive

**Why 15 points (deduction):** This is not a security scanner. It flags obvious mistakes that would be embarrassing or dangerous if an agent processed or exposed them. Conservative design means false positives are preferable to false negatives here.

### 4. Public Readiness (20 points)

**What it checks:**

Presence of standard community and documentation files:

- `README.md` (or `README.*`)
- `LICENSE` (or `LICENSE.*`)
- `SECURITY.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `.github/ISSUE_TEMPLATE/` or `.github/ISSUE_TEMPLATE.md`
- `.github/PULL_REQUEST_TEMPLATE.md` or `.github/pull_request_template.md`
- `examples/` or `samples/` directory
- `.gitignore`

**What it does NOT check:**

- Content quality of these files
- Whether LICENSE matches actual distribution terms
- Whether README is up to date

**Why 20 points:** Agents benefit from well-documented repositories. README helps them understand context, LICENSE clarifies what they can do, and templates guide their PR/issue contributions.

### 5. Generated Hygiene (15 points)

**What it checks:**

Whether `.gitignore` includes common output/generated directories:

- `out/`, `output/`, `outputs/`, `logs/`
- `.agents/`, `.kiro/`
- `.venv/`, `node_modules/`, `__pycache__/`

**What it does NOT check:**

- Whether .gitignore patterns are correct regex/glob
- Whether ignored directories actually exist
- Build-system-specific output paths

**Why 15 points:** Agents frequently generate output files. Without proper .gitignore coverage, these files get committed accidentally, cluttering the repository and creating merge conflicts.

## Boundary Decisions

### No network access

The tool never makes HTTP requests, DNS lookups, or any network calls. This is enforced by design (no networking libraries are imported) and ensures:

- The tool works offline
- No data leaves the machine
- No rate limits or authentication needed
- Deterministic behavior

### No code execution

The tool never executes code from the target repository. It reads files and matches patterns. This prevents:

- Arbitrary code execution risks
- Dependency on target repo's language runtime
- Non-deterministic behavior from test execution

### No credential access

The tool never reads environment variables, credential stores, or configuration files outside the `--repo` path. It cannot accidentally expose secrets through its own execution.

### Path containment

All file reads are constrained to the `--repo` path. All file writes are constrained to the `--out` path. The tool validates these boundaries before execution.

## Extensibility

The check system is modular. Each check is a standalone function in `agent_readiness_lint/checks/` that:

1. Accepts a `Path` (the repository root)
2. Returns a dictionary with `items` (list of check results) and category metadata
3. Each item has: `name`, `status` (pass/warn/fail/unknown), `detail`, and `evidence`

Adding a new check category requires:

1. Creating a new check module in `agent_readiness_lint/checks/`
2. Exporting it from `agent_readiness_lint/checks/__init__.py`
3. Adding a weight entry in `agent_readiness_lint/scoring.py` (`CATEGORY_WEIGHTS`)
4. Calling it from `agent_readiness_lint/__main__.py`

The scoring system automatically adapts to new categories based on the weights dictionary.
