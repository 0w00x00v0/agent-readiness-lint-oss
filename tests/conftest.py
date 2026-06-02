"""Shared pytest fixtures for agent-readiness-lint tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def empty_repo(tmp_path: Path) -> Path:
    """Completely empty directory (no files at all)."""
    return tmp_path


@pytest.fixture
def minimal_repo(tmp_path: Path) -> Path:
    """Minimal repo with only a .git marker and one source file."""
    (tmp_path / ".git").mkdir()
    (tmp_path / "main.py").write_text("print('hello')\n")
    return tmp_path


@pytest.fixture
def good_repo(tmp_path: Path) -> Path:
    """Well-configured repo with all recommended files."""
    # AGENTS.md with all recommended sections
    agents_md = """\
# AGENTS.md

## Project Purpose
This is a sample project for testing.

## Setup Commands
```bash
pip install -e .
```

## Test Commands
```bash
pytest tests/ -v
```

## File Boundaries
- Source: src/
- Tests: tests/
- Do not modify: generated output

## Generated Files
Do not commit: out/, __pycache__/, .venv/, node_modules/

## Secrets and Private Data
Never commit .env, API keys, or credentials. Not allowed to access tokens.

## Non-Goals
- No network calls
- Out of scope: deployment automation
"""
    (tmp_path / "AGENTS.md").write_text(agents_md)

    # README
    (tmp_path / "README.md").write_text("# Test Project\n\nA test project.\n")

    # LICENSE
    (tmp_path / "LICENSE").write_text("MIT License\n\nCopyright 2024\n")

    # SECURITY.md
    (tmp_path / "SECURITY.md").write_text("# Security\n\nReport vulnerabilities.\n")

    # CONTRIBUTING.md
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing\n\nPRs welcome.\n")

    # CODE_OF_CONDUCT.md
    (tmp_path / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct\n\nBe nice.\n")

    # .gitignore with common patterns
    gitignore_content = """\
out/
output/
outputs/
logs/
.agents/
.kiro/
.venv/
node_modules/
__pycache__/
"""
    (tmp_path / ".gitignore").write_text(gitignore_content)

    # tests directory with a test file
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_example.py").write_text("def test_one():\n    assert True\n")

    # CI configuration
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    (workflows_dir / "ci.yml").write_text("name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n")

    # Issue template directory
    issue_dir = tmp_path / ".github" / "ISSUE_TEMPLATE"
    issue_dir.mkdir(parents=True, exist_ok=True)
    (issue_dir / "bug_report.md").write_text("---\nname: Bug\n---\n")

    # PR template
    (tmp_path / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text("## Description\n")

    # Examples directory
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    (examples_dir / "demo.py").write_text("# demo\n")

    # pyproject.toml with pytest
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "test"\n\n[project.optional-dependencies]\ndev = ["pytest"]\n'
    )

    return tmp_path


@pytest.fixture
def risky_repo(tmp_path: Path) -> Path:
    """Repo with secret/credential risks and no agent instructions."""
    # .env file
    (tmp_path / ".env").write_text("DATABASE_URL=postgres://user:pass@localhost/db\n")

    # Private key file
    (tmp_path / "id_rsa").write_text(("-----BEGIN " + "RSA PRIVATE KEY-----\nfakekey\n-----END " + "RSA PRIVATE KEY-----\n"))

    # File with AWS secret
    (tmp_path / "config.py").write_text(
        "AWS_SECRET_ACCESS_KEY = 'fakesecret123'\nAPI_KEY = 'test'\n"
    )

    # No AGENTS.md, no README, no LICENSE, no .gitignore
    return tmp_path


@pytest.fixture
def partial_repo(tmp_path: Path) -> Path:
    """Repo with some files present but incomplete AGENTS.md and missing LICENSE."""
    # AGENTS.md with only some sections
    agents_md = """\
# AGENTS.md

## Purpose
This project does something.

## Setup
pip install -e .
"""
    (tmp_path / "AGENTS.md").write_text(agents_md)

    # README
    (tmp_path / "README.md").write_text("# Partial Project\n")

    # .gitignore missing some patterns
    (tmp_path / ".gitignore").write_text("__pycache__/\n.venv/\n")

    # No LICENSE, no tests, no CI
    return tmp_path

