# Examples

This directory holds committed example repositories for `agent-readiness-lint`.
There are two kinds of examples:

- `fixtures/` — small fixture repositories consumed by the automated test suite
  (`tests/test_examples.py`). They exercise the scoring extremes and the
  secret-risk check.
- `sample-repo/` — a documented, runnable demo (`widget-service`) for trying the
  tool by hand.

Generated reports are **not** committed. Write them to a path that is ignored by
Git (the default `./out` is in `.gitignore`) or to a temporary directory.

## Test fixtures (`fixtures/`)

### `fixtures/minimal-repo/`

A bare repository with only a `main.py` file. Contains no agent readiness files
(no AGENTS.md, no README, no LICENSE, no tests, no CI). This represents a
repository that has not been configured for AI agent workflows.

**Expected score:** below 50

### `fixtures/good-repo/`

A well-configured repository with all recommended files:

- `AGENTS.md` with all 7 recommended sections (project purpose, setup commands,
  test commands, file boundaries, generated files, secrets/private data, non-goals)
- `README.md`
- `LICENSE` (MIT)
- `.gitignore` covering common patterns
- `tests/test_example.py`
- `.github/workflows/ci.yml`

**Expected score:** 80+

### `fixtures/risky-repo/`

A repository demonstrating secret risk detection. The credentials below are
intentional, clearly labelled fakes used only to drive the secret-risk check:

- `fake.env.example` file with a fake `DATABASE_URL`
- `fake_id_rsa.txt` file with fake private key content
- `config.py` with a fake `AWS_SECRET_ACCESS_KEY`
- No AGENTS.md, no README, no LICENSE

**Expected score:** below 50

### Running the tool against fixtures

```bash
# Scan the good-repo fixture
python -m agent_readiness_lint --repo examples/fixtures/good-repo --out /tmp/demo

# Scan the minimal-repo fixture
python -m agent_readiness_lint --repo examples/fixtures/minimal-repo --out /tmp/demo

# Scan the risky-repo fixture
python -m agent_readiness_lint --repo examples/fixtures/risky-repo --out /tmp/demo
```

Output will be written to timestamped subdirectories under the `--out` path.

## Runnable sample (`sample-repo/`)

`sample-repo/` is a tiny, fictional Python project (`widget-service`) used to
demonstrate the linter. It is intentionally incomplete so the tool has findings
to report. It contains no real code, data, secrets, or credentials.

### Run it

```bash
python -m agent_readiness_lint \
  --repo examples/sample-repo \
  --out /tmp/sample-out \
  --project-name "widget-service"
```

### Expected behavior

The score is deterministic for a given repository state. With the sample as
committed, the run prints:

```
Agent Readiness Lint - Score: 79/100 (Needs minor cleanup)
Counts: 15 pass, 16 warn, 1 fail, 0 unknown
```

Why this result:

- **Pass:** `README.md`, an `AGENTS.md` instruction file, the
  `Project Purpose` / `Setup Commands` / `Test Commands` sections, a `tests/`
  directory, a CI config, a detected test framework (`pytest`), a `.gitignore`,
  and no secret-risk findings.
- **Fail (blocker):** no `LICENSE` file.
- **Warn:** `AGENTS.md` is missing the `file boundaries`, `generated files`,
  `secrets`, and `non-goals` sections; several optional community files are
  absent (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue/PR
  templates); and `.gitignore` omits some common patterns (for example
  `.agents/`, `.kiro/`, `logs/`, `node_modules/`).

Running the same command with `--strict` caps the score at 59, because the
missing `LICENSE` is a failing check.

> Note: the nested `examples/sample-repo/.github/workflows/ci.yml` is example
> input only. GitHub Actions runs workflows from the repository root
> `.github/workflows/` directory and ignores nested copies.

