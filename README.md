# agent-readiness-lint

A local-only CLI tool that checks whether a repository is ready for AI coding agent workflows (Codex, Copilot, Cursor, Claude, etc.).

It scans your repository structure, scores it 0-100 across five categories, and generates actionable reports -- all without network calls, API keys, or telemetry.

## Installation

Requires Python 3.10 or later.

```bash
# Clone the repository
git clone https://github.com/0w00x00v0/agent-readiness-lint-oss.git
cd agent-readiness-lint-oss

# Install in development mode
pip install -e .

# Or with development dependencies (pytest, ruff)
pip install -e '.[dev]'
```

## Usage

```
usage: agent-readiness-lint [-h] --repo REPO [--out OUT]
                            [--project-name PROJECT_NAME] [--strict]
                            [--include-prompts | --no-include-prompts]

Check repository readiness for AI agent workflows (local-only, no network
calls).

options:
  -h, --help            show this help message and exit
  --repo REPO           Path to the repository to analyze.
  --out OUT             Base output directory (default: ./out). A timestamped
                        subfolder will be created.
  --project-name PROJECT_NAME
                        Optional project name for report headers.
  --strict              Strict mode: any fail result caps score at 59.
  --include-prompts, --no-include-prompts
                        Include CODEX_PROMPT.md and CHATGPT_REVIEW_PROMPT.md
                        in output (default: true).
```

### Basic example

```bash
python -m agent_readiness_lint --repo /path/to/your/repo --out ./results
```

### Try it on the bundled sample

A small, fictional example repository is committed under `examples/sample-repo/`:

```bash
python -m agent_readiness_lint \
  --repo examples/sample-repo \
  --out /tmp/sample-out \
  --project-name "widget-service"
```

This prints a deterministic score of `76/100 (Needs minor cleanup)`. See
[examples/README.md](examples/README.md) for the full expected output and an
explanation of each finding.

### With all options

```bash
python -m agent_readiness_lint \
  --repo /path/to/your/repo \
  --out ./results \
  --project-name "My Project" \
  --strict \
  --no-include-prompts
```

## Output

The tool creates a timestamped folder under your `--out` directory (e.g., `out/agent-readiness-20250101-120000/`) containing:

| File | Purpose |
|------|---------|
| `SUMMARY.md` | Overall score, top blockers, warnings, and recommended next actions |
| `CHECKS.md` | Detailed pass/warn/fail checklist with evidence paths for every check item |
| `AGENTS_SUGGESTIONS.md` | Suggested AGENTS.md sections to add or improve, with draft snippets |
| `CODEX_PROMPT.md` | English-language prompt you can feed to Codex to fix identified gaps |
| `CHATGPT_REVIEW_PROMPT.md` | Japanese-language prompt for ChatGPT review with appropriate caveats |
| `MANIFEST.json` | Machine-readable results: score, counts, detected files, timestamps |

The prompt files (`CODEX_PROMPT.md` and `CHATGPT_REVIEW_PROMPT.md`) can be excluded with `--no-include-prompts`.

## Scoring

The tool scores repositories 0-100 across five categories:

| Category | Max Points | What it checks |
|----------|-----------|----------------|
| Agent Instructions | 30 | AGENTS.md presence and section coverage |
| Test/CI Signals | 20 | Test files, CI configuration, framework detection |
| Secret Risk | 15 | Suspicious filenames and content markers (deductions) |
| Public Readiness | 20 | README, LICENSE, .gitignore, community files |
| Generated Hygiene | 15 | .gitignore coverage for common output directories |

Score labels:

- **Ready** (80-100): Repository is well-prepared for agent-assisted work
- **Needs minor cleanup** (60-79): A few gaps to address
- **Needs major cleanup** (40-59): Significant preparation needed
- **Not ready for agent work** (0-39): Substantial work required

In `--strict` mode, any single failing check caps the score at 59 regardless of the raw total.

## Limitations

- **Not a security scanner.** The secret risk check is a best-effort heuristic for obvious mistakes (committed fake.env.example files, private-key-shaped fake fixtures). It does not replace dedicated secret scanning tools.
- **Not a compliance product.** It produces no audit, attestation, or certification, and should not be cited as evidence of compliance with any standard.
- **Not production-certified.** A score is informational only. It is not a quality gate, a guarantee, or a sign-off for shipping.
- **Static analysis only.** The tool reads file names and content patterns. It does not execute code, resolve dependencies, or verify that tests actually pass.
- **Best-effort heuristics.** Section detection in AGENTS.md relies on keyword matching. It may miss unconventional headings or produce false positives.
- **No guarantees.** A score of 100 does not guarantee an agent will work perfectly with your repository. A low score does not mean agents cannot be used at all.
- **Local filesystem only.** The tool reads from the path you provide. It does not clone repositories, call Git APIs, or access remote resources.

## Non-Goals

This tool deliberately does not:

- Act as a SaaS product or hosted service
- Run as a bot, daemon, or background process
- Make network calls of any kind
- Collect telemetry or usage data
- Access API keys, tokens, or credentials
- Execute repository code or run tests on your behalf
- Provide security certifications or compliance attestations

## Development

```bash
# Install with dev dependencies
pip install -e '.[dev]'

# Run tests
pytest tests/ -v

# Lint (ruff is configured in pyproject.toml)
ruff check agent_readiness_lint/ tests/
```

This clean public mirror intentionally does not include GitHub Actions workflow files in the initial public release. Run the local validation commands above (`ruff check agent_readiness_lint/ tests/` and `pytest tests/ -v`) before relying on changes. The private source repository was validated before this clean mirror was published.

## Project status and docs

- [docs/DESIGN.md](docs/DESIGN.md) - scoring algorithm and check boundaries
- [docs/EXAMPLES.md](docs/EXAMPLES.md) - illustrative walkthrough
- [docs/PUBLIC_CANDIDATE_CHECKLIST.md](docs/PUBLIC_CANDIDATE_CHECKLIST.md) - public release review notes and remaining human-review items
- [docs/DOGFOODING.md](docs/DOGFOODING.md) - running the tool on itself

## License

MIT. See [LICENSE](LICENSE).






