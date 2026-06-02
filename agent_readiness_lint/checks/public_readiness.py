"""Check for public repository readiness files."""

from __future__ import annotations

from pathlib import Path
from typing import Any


READINESS_CHECKS = [
    {
        "name": "readme",
        "label": "README",
        "paths": ["README.md", "README.rst", "README.txt", "README"],
        "required": True,
    },
    {
        "name": "license",
        "label": "LICENSE",
        "paths": ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "LICENCE.md"],
        "required": True,
    },
    {
        "name": "security",
        "label": "SECURITY.md",
        "paths": ["SECURITY.md"],
        "required": False,
    },
    {
        "name": "contributing",
        "label": "CONTRIBUTING.md",
        "paths": ["CONTRIBUTING.md"],
        "required": False,
    },
    {
        "name": "code_of_conduct",
        "label": "CODE_OF_CONDUCT.md",
        "paths": ["CODE_OF_CONDUCT.md"],
        "required": False,
    },
    {
        "name": "issue_template",
        "label": "Issue template",
        "paths": [
            ".github/ISSUE_TEMPLATE",
            ".github/ISSUE_TEMPLATE.md",
            ".github/issue_template.md",
        ],
        "required": False,
    },
    {
        "name": "pr_template",
        "label": "Pull request template",
        "paths": [
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/pull_request_template.md",
            ".github/PULL_REQUEST_TEMPLATE",
        ],
        "required": False,
    },
    {
        "name": "examples",
        "label": "Examples or samples directory",
        "paths": ["examples", "samples"],
        "required": False,
    },
    {
        "name": "gitignore",
        "label": ".gitignore",
        "paths": [".gitignore"],
        "required": True,
    },
]


def check_public_readiness(repo_path: Path) -> dict[str, Any]:
    """Run the public readiness check."""
    items: list[dict[str, Any]] = []

    for check in READINESS_CHECKS:
        found_path: str | None = None
        for p in check["paths"]:
            full = repo_path / p
            if full.exists():
                found_path = p
                break

        if found_path:
            items.append({
                "name": check["name"],
                "status": "pass",
                "evidence": [found_path],
                "detail": f"{check['label']} found at {found_path}.",
            })
        elif check["required"]:
            items.append({
                "name": check["name"],
                "status": "fail",
                "evidence": [],
                "detail": f"{check['label']} not found (recommended for public repos).",
            })
        else:
            items.append({
                "name": check["name"],
                "status": "warn",
                "evidence": [],
                "detail": f"{check['label']} not found (optional but recommended).",
            })

    return {
        "category": "public_readiness",
        "items": items,
    }
