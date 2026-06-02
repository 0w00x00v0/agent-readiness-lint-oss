"""Check for test files and CI configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from agent_readiness_lint.checks._path_safety import is_within_repo


TEST_FILE_PATTERNS = [
    "test_*.py",
    "*_test.py",
    "*.test.js",
    "*.test.ts",
    "*.test.jsx",
    "*.test.tsx",
    "*.Tests.ps1",
]

TEST_DIRS = ["tests", "test", "__tests__", "spec"]

CI_FILES = [
    ".github/workflows",
    ".gitlab-ci.yml",
    "Jenkinsfile",
    "azure-pipelines.yml",
    ".circleci/config.yml",
    ".travis.yml",
]

FRAMEWORK_INDICATORS = {
    "pytest": ["pytest"],
    "unittest": ["unittest"],
    "jest": ["jest"],
    "mocha": ["mocha"],
    "vitest": ["vitest"],
    "pester": ["pester", "invoke-pester"],
}


def _find_test_files(repo_path: Path) -> list[str]:
    """Find test files in the repo."""
    found: list[str] = []
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden dirs, node_modules, venvs
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in ("node_modules", ".venv", "venv", "__pycache__")
        ]
        rel_root = Path(root).relative_to(repo_path)
        for f in files:
            file_path = Path(root) / f
            # Skip files that resolve outside the repo (symlink escape)
            if not is_within_repo(file_path, repo_path):
                continue
            for pattern in TEST_FILE_PATTERNS:
                if Path(f).match(pattern):
                    found.append(str(rel_root / f))
                    break
    return found


def _find_test_dirs(repo_path: Path) -> list[str]:
    """Find test directories."""
    found: list[str] = []
    for d in TEST_DIRS:
        if (repo_path / d).is_dir():
            found.append(d)
    return found


def _find_ci_files(repo_path: Path) -> list[str]:
    """Find CI configuration files."""
    found: list[str] = []
    for ci in CI_FILES:
        p = repo_path / ci
        if p.is_file():
            found.append(ci)
        elif p.is_dir():
            # For directories like .github/workflows, list YML files
            for f in p.iterdir():
                if f.suffix in (".yml", ".yaml"):
                    found.append(str(f.relative_to(repo_path)))
    return found


def _detect_test_frameworks(repo_path: Path) -> list[str]:
    """Detect test frameworks from dependency files."""
    frameworks: list[str] = []
    dep_files = ["pyproject.toml", "requirements.txt", "requirements-dev.txt", "package.json"]

    content_parts: list[str] = []
    for dep_file in dep_files:
        p = repo_path / dep_file
        if p.is_file() and is_within_repo(p, repo_path):
            try:
                content_parts.append(p.read_text(encoding="utf-8", errors="replace").lower())
            except OSError:
                pass

    combined = "\n".join(content_parts)
    for framework, indicators in FRAMEWORK_INDICATORS.items():
        for indicator in indicators:
            if indicator in combined:
                frameworks.append(framework)
                break

    return frameworks


def _infer_test_commands(frameworks: list[str]) -> list[str]:
    """Infer likely test commands from detected frameworks."""
    commands: list[str] = []
    if "pytest" in frameworks:
        commands.append("pytest")
    if "jest" in frameworks:
        commands.append("npx jest")
    if "vitest" in frameworks:
        commands.append("npx vitest")
    if "mocha" in frameworks:
        commands.append("npx mocha")
    return commands


def check_test_ci_signals(repo_path: Path) -> dict[str, Any]:
    """Run the test/CI signals check."""
    test_files = _find_test_files(repo_path)
    test_dirs = _find_test_dirs(repo_path)
    ci_files = _find_ci_files(repo_path)
    frameworks = _detect_test_frameworks(repo_path)
    test_commands = _infer_test_commands(frameworks)

    items: list[dict[str, Any]] = []

    # Test files present?
    has_tests = len(test_files) > 0 or len(test_dirs) > 0
    items.append({
        "name": "test_files_exist",
        "status": "pass" if has_tests else "warn",
        "evidence": test_files[:10] + test_dirs,
        "detail": f"Found {len(test_files)} test file(s) and {len(test_dirs)} test dir(s)."
        if has_tests
        else "No test files or test directories detected.",
    })

    # CI configured?
    items.append({
        "name": "ci_configured",
        "status": "pass" if ci_files else "warn",
        "evidence": ci_files,
        "detail": f"Found {len(ci_files)} CI config file(s)."
        if ci_files
        else "No CI configuration detected.",
    })

    # Test framework detected?
    items.append({
        "name": "test_framework_detected",
        "status": "pass" if frameworks else "warn",
        "evidence": frameworks,
        "detail": f"Detected framework(s): {', '.join(frameworks)}."
        if frameworks
        else "No test framework detected in dependency files.",
    })

    return {
        "category": "test_ci_signals",
        "test_files": test_files,
        "test_dirs": test_dirs,
        "ci_files": ci_files,
        "frameworks": frameworks,
        "inferred_test_commands": test_commands,
        "items": items,
    }
