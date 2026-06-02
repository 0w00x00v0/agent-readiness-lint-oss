"""Check .gitignore for common generated/output folder patterns."""

from __future__ import annotations

from pathlib import Path
from typing import Any


EXPECTED_IGNORES = [
    "out/",
    "output/",
    "outputs/",
    "logs/",
    ".agents/",
    ".kiro/",
    ".venv/",
    "node_modules/",
    "__pycache__/",
]


def _read_gitignore(repo_path: Path) -> list[str]:
    """Read .gitignore and return normalized lines."""
    gitignore = repo_path / ".gitignore"
    if not gitignore.is_file():
        return []
    try:
        content = gitignore.read_text(encoding="utf-8", errors="replace")
        lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                # Strip inline comments (e.g., "out/ # generated output")
                if " #" in stripped:
                    stripped = stripped[:stripped.index(" #")].rstrip()
                if stripped:
                    lines.append(stripped)
        return lines
    except OSError:
        return []


def _is_pattern_covered(pattern: str, gitignore_lines: list[str]) -> bool:
    """Check if a pattern is covered by the gitignore entries."""
    # Normalize: strip trailing slash for comparison
    normalized = pattern.rstrip("/")
    for line in gitignore_lines:
        line_norm = line.rstrip("/")
        # Direct match
        if line_norm == normalized:
            return True
        # Match with leading slash
        if line_norm == "/" + normalized:
            return True
        # Match with **/ prefix (e.g., "**/node_modules" covers "node_modules")
        if line_norm == "**/" + normalized:
            return True
        # Match where gitignore line without **/ matches our pattern with **/
        if normalized == "**/" + line_norm:
            return True
        # Wildcard patterns that would cover it
        if line == pattern:
            return True
    return False


def check_generated_hygiene(repo_path: Path) -> dict[str, Any]:
    """Run the generated hygiene check."""
    gitignore_lines = _read_gitignore(repo_path)
    has_gitignore = (repo_path / ".gitignore").is_file()

    items: list[dict[str, Any]] = []

    if not has_gitignore:
        items.append({
            "name": "gitignore_exists",
            "status": "fail",
            "evidence": [],
            "detail": "No .gitignore file found.",
        })
        # All patterns are missing
        for pattern in EXPECTED_IGNORES:
            items.append({
                "name": f"ignore_{pattern.rstrip('/').replace('.', '_').replace('/', '')}",
                "status": "warn",
                "evidence": [],
                "detail": f"Pattern '{pattern}' not in .gitignore (no .gitignore file).",
            })
    else:
        items.append({
            "name": "gitignore_exists",
            "status": "pass",
            "evidence": [".gitignore"],
            "detail": ".gitignore file found.",
        })
        for pattern in EXPECTED_IGNORES:
            covered = _is_pattern_covered(pattern, gitignore_lines)
            items.append({
                "name": f"ignore_{pattern.rstrip('/').replace('.', '_').replace('/', '')}",
                "status": "pass" if covered else "warn",
                "evidence": [".gitignore"] if covered else [],
                "detail": f"Pattern '{pattern}' {'is' if covered else 'is NOT'} in .gitignore.",
            })

    return {
        "category": "generated_hygiene",
        "gitignore_lines": gitignore_lines,
        "items": items,
    }
