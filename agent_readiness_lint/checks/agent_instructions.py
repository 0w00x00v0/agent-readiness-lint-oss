"""Check for agent instruction files (AGENTS.md, CLAUDE.md, etc.)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


# Sections we look for in AGENTS.md-style files
EXPECTED_SECTIONS = [
    "project purpose",
    "setup commands",
    "test commands",
    "file boundaries",
    "generated files",
    "secrets",
    "non-goals",
]

# Section keyword mapping - keywords that indicate a section is present
SECTION_KEYWORDS: dict[str, list[str]] = {
    "project purpose": ["purpose", "about", "overview", "description", "what this"],
    "setup commands": ["setup", "install", "getting started", "bootstrap", "build"],
    "test commands": ["test", "testing", "verify", "check"],
    "file boundaries": ["boundary", "boundaries", "allowed", "scope", "file structure"],
    "generated files": ["generated", "output", "do not commit", "ignored", "cache"],
    "secrets": ["secret", "private", "credential", "token", "api key", "not allowed"],
    "non-goals": ["non-goal", "not allowed", "out of scope", "excluded", "forbidden"],
}

INSTRUCTION_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    ".cursor/rules",
    ".github/copilot-instructions.md",
]


def _find_instruction_files(repo_path: Path) -> dict[str, Path | None]:
    """Detect which agent instruction files exist."""
    results: dict[str, Path | None] = {}
    for rel in INSTRUCTION_FILES:
        full = repo_path / rel
        if full.is_file():
            results[rel] = full
        else:
            results[rel] = None
    return results


def _parse_sections(file_path: Path) -> dict[str, str]:
    """Parse an instruction file and determine which expected sections are covered."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return {}

    found: dict[str, str] = {}
    for section, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if kw in content:
                found[section] = "pass"
                break
        if section not in found:
            found[section] = "warn"
    return found


def check_agent_instructions(repo_path: Path) -> dict[str, Any]:
    """Run the agent instructions check.

    Returns structured results with:
      - detected_files: which instruction files exist
      - sections: pass/warn/fail per expected section
      - items: list of individual check results
    """
    detected = _find_instruction_files(repo_path)
    has_any = any(v is not None for v in detected.values())

    items: list[dict[str, Any]] = []

    # Check for presence of any instruction file
    if has_any:
        items.append({
            "name": "agent_instruction_file_exists",
            "status": "pass",
            "evidence": [k for k, v in detected.items() if v is not None],
            "detail": "At least one agent instruction file found.",
        })
    else:
        items.append({
            "name": "agent_instruction_file_exists",
            "status": "fail",
            "evidence": [],
            "detail": "No agent instruction file found (AGENTS.md, CLAUDE.md, .cursor/rules, .github/copilot-instructions.md).",
        })

    # Parse sections from the first found file
    sections: dict[str, str] = {}
    primary_file: Path | None = None
    for rel, path in detected.items():
        if path is not None:
            primary_file = path
            break

    if primary_file is not None:
        sections = _parse_sections(primary_file)
        for section_name, status in sections.items():
            items.append({
                "name": f"section_{section_name.replace(' ', '_')}",
                "status": status,
                "evidence": [str(primary_file.relative_to(repo_path))],
                "detail": f"Section '{section_name}': {'found' if status == 'pass' else 'missing or weak'}.",
            })
    else:
        for section_name in EXPECTED_SECTIONS:
            sections[section_name] = "fail"
            items.append({
                "name": f"section_{section_name.replace(' ', '_')}",
                "status": "fail",
                "evidence": [],
                "detail": f"Section '{section_name}': no instruction file to parse.",
            })

    return {
        "category": "agent_instructions",
        "detected_files": {k: str(v) if v else None for k, v in detected.items()},
        "sections": sections,
        "items": items,
    }
