# Examples

> **Runnable example:** a committed, fictional sample repository lives at
> [`examples/sample-repo/`](../examples/sample-repo). See
> [`examples/README.md`](../examples/README.md) for the exact command and its
> reproducible output (`79/100`).
>
> The walkthrough below is **illustrative**. It uses a different fictional
> project (`acme-api`) to show the shape of the reports; its numbers are
> hand-written for explanation and are not produced by running the tool.

This document shows a fictional example of running agent-readiness-lint against a sample repository.

## Sample Repository Structure

Consider a Python web API project called `acme-api` with the following structure:

```
acme-api/
  .git/
  .github/
    workflows/
      ci.yml
  .gitignore
  AGENTS.md
  README.md
  requirements.txt
  src/
    app.py
    models.py
  tests/
    test_app.py
    test_models.py
```

This repository has some good practices (README, tests, CI) but is missing a LICENSE, has no CONTRIBUTING.md, and its AGENTS.md only covers project purpose and test commands.

## CLI Invocation

```bash
python -m agent_readiness_lint --repo ./acme-api --out ./reports --project-name "Acme API"
```

Terminal output:

```
Agent Readiness Lint - Score: 62/100 (Needs minor cleanup)
Output: /home/user/reports/agent-readiness-20250115-143022
Files: SUMMARY.md, CHECKS.md, AGENTS_SUGGESTIONS.md, CODEX_PROMPT.md, CHATGPT_REVIEW_PROMPT.md, MANIFEST.json
Counts: 14 pass, 8 warn, 3 fail, 0 unknown
```

## Output: SUMMARY.md

```markdown
# Agent Readiness Summary: Acme API

**Score:** 62/100 - Needs minor cleanup

## Category Scores

- **agent_instructions**: 17.1 points
- **test_ci_signals**: 20.0 points
- **secret_risk**: 15.0 points
- **public_readiness**: 6.7 points
- **generated_hygiene**: 3.8 points

## Top Blockers

- [public_readiness] LICENSE file not found (LICENSE, LICENSE.md, LICENSE.txt)
- [agent_instructions] Section 'file boundaries': missing or weak
- [agent_instructions] Section 'generated files': missing or weak

## Warnings

- [public_readiness] SECURITY.md not found
- [public_readiness] CONTRIBUTING.md not found
- [public_readiness] CODE_OF_CONDUCT.md not found
- [public_readiness] Issue template not found
- [public_readiness] Pull request template not found
- [public_readiness] examples/ or samples/ directory not found
- [generated_hygiene] .gitignore missing pattern for: .agents/
- [generated_hygiene] .gitignore missing pattern for: .kiro/

## Recommended Next Actions

1. Address all blockers listed above
2. Review warnings and fix where practical

## Explicit Unknowns

- None
```

## Output: CHECKS.md (excerpt)

```markdown
# Detailed Check Results

## agent_instructions

- [PASS] **agent_instruction_file_exists**: At least one agent instruction file found.
  - Evidence: AGENTS.md
- [PASS] **section_project_purpose**: Section 'project purpose': found.
  - Evidence: AGENTS.md
- [PASS] **section_test_commands**: Section 'test commands': found.
  - Evidence: AGENTS.md
- [WARN] **section_setup_commands**: Section 'setup commands': missing or weak.
  - Evidence: AGENTS.md
- [FAIL] **section_file_boundaries**: Section 'file boundaries': missing or weak.
  - Evidence: AGENTS.md
- [FAIL] **section_generated_files**: Section 'generated files': missing or weak.
  - Evidence: AGENTS.md
- [WARN] **section_secrets**: Section 'secrets': missing or weak.
  - Evidence: AGENTS.md
- [WARN] **section_non_goals**: Section 'non-goals': missing or weak.
  - Evidence: AGENTS.md

## test_ci_signals

- [PASS] **test_files_present**: Test files detected.
  - Evidence: tests/test_app.py, tests/test_models.py
- [PASS] **ci_config_present**: CI configuration found.
  - Evidence: .github/workflows/ci.yml
- [PASS] **test_framework_detected**: Test framework found in dependencies.
  - Evidence: requirements.txt

## secret_risk

- [PASS] **no_suspicious_files**: No suspicious filenames detected.
- [PASS] **no_content_markers**: No high-risk content markers found.
```

## Output: MANIFEST.json

```json
{
  "schema_version": "1.0.0",
  "generated_at_utc": "2025-01-15T14:30:22Z",
  "repo_path": "/home/user/acme-api",
  "output_dir": "/home/user/reports/agent-readiness-20250115-143022",
  "output_files": [
    "SUMMARY.md",
    "CHECKS.md",
    "AGENTS_SUGGESTIONS.md",
    "CODEX_PROMPT.md",
    "CHATGPT_REVIEW_PROMPT.md",
    "MANIFEST.json"
  ],
  "score": 62,
  "label": "Needs minor cleanup",
  "counts": {
    "pass": 14,
    "warn": 8,
    "fail": 3,
    "unknown": 0
  },
  "category_scores": {
    "agent_instructions": 17.1,
    "test_ci_signals": 20.0,
    "secret_risk": 15.0,
    "public_readiness": 6.7,
    "generated_hygiene": 3.8
  },
  "detected_files": [
    "AGENTS.md",
    "tests/test_app.py",
    "tests/test_models.py",
    ".github/workflows/ci.yml",
    "requirements.txt",
    "README.md",
    ".gitignore"
  ],
  "explicit_unknowns": []
}
```

## Using the Output

After reviewing the results, you could:

1. **Feed `CODEX_PROMPT.md` to Codex** to automatically fix the identified gaps (add LICENSE, expand AGENTS.md sections, update .gitignore)
2. **Feed `CHATGPT_REVIEW_PROMPT.md` to ChatGPT** for a prioritized review of what to fix first
3. **Use `AGENTS_SUGGESTIONS.md`** as a template for manually expanding your AGENTS.md
4. **Re-run the tool** after making fixes to verify improvement

## Strict Mode Example

Running the same repository with `--strict`:

```bash
python -m agent_readiness_lint --repo ./acme-api --out ./reports --strict
```

Because there are 3 fail results, the score is capped at 59:

```
Agent Readiness Lint - Score: 59/100 (Needs major cleanup)
```

This makes `--strict` useful as a CI gate where any failing check should block a "ready" designation.

