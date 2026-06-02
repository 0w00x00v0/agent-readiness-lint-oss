# AGENTS.md

## Project Purpose

This is a well-configured example project demonstrating all recommended sections
for agent readiness.

## Setup Commands

```bash
pip install -e '.[dev]'
```

## Test Commands

```bash
pytest tests/ -v
```

## File Boundaries

- Source code: src/
- Tests: tests/
- Documentation: docs/
- Do not modify: generated output in out/

## Generated Files

Do not commit or edit:
- out/
- __pycache__/
- .venv/
- node_modules/
- *.egg-info/

## Secrets and Private Data

Never commit .env files, API keys, tokens, or credentials.
Not allowed to access secrets in CI without approval.

## Non-Goals

- No network calls during linting
- Out of scope: deployment automation
- Not allowed: modifying upstream dependencies
