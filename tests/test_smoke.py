"""Smoke tests for agent-readiness-lint."""

from __future__ import annotations

import json
from pathlib import Path

from agent_readiness_lint.__main__ import main


def test_help(capsys):
    """Test --help exits cleanly."""
    import pytest

    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_run_on_self(tmp_path):
    """Run the linter against its own repo and verify output."""
    repo = Path(__file__).parent.parent
    out_dir = tmp_path / "out"

    result = main(["--repo", str(repo), "--out", str(out_dir)])
    assert result == 0

    # Find the generated timestamped dir
    output_dirs = list(out_dir.glob("agent-readiness-*"))
    assert len(output_dirs) == 1
    output = output_dirs[0]

    # Check all expected files exist
    expected_files = [
        "SUMMARY.md",
        "CHECKS.md",
        "AGENTS_SUGGESTIONS.md",
        "CODEX_PROMPT.md",
        "CHATGPT_REVIEW_PROMPT.md",
        "MANIFEST.json",
    ]
    for f in expected_files:
        assert (output / f).is_file(), f"Missing output file: {f}"

    # Validate MANIFEST.json
    manifest = json.loads((output / "MANIFEST.json").read_text())
    assert "schema_version" in manifest
    assert "generated_at_utc" in manifest
    assert "repo_path" in manifest
    assert "output_files" in manifest
    assert "score" in manifest
    assert "counts" in manifest
    assert "detected_files" in manifest
    assert "explicit_unknowns" in manifest
    assert isinstance(manifest["score"], int)
    assert 0 <= manifest["score"] <= 100


def test_invalid_repo():
    """Test with non-existent repo path."""
    result = main(["--repo", "/nonexistent/path", "--out", "/tmp/test"])
    assert result == 1


def test_no_prompts(tmp_path):
    """Test --no-include-prompts flag."""
    repo = Path(__file__).parent.parent
    out_dir = tmp_path / "out"

    result = main(["--repo", str(repo), "--out", str(out_dir), "--no-include-prompts"])
    assert result == 0

    output_dirs = list(out_dir.glob("agent-readiness-*"))
    output = output_dirs[0]

    # Prompt files should NOT exist
    assert not (output / "CODEX_PROMPT.md").exists()
    assert not (output / "CHATGPT_REVIEW_PROMPT.md").exists()

    # Other files should exist
    assert (output / "SUMMARY.md").is_file()
    assert (output / "CHECKS.md").is_file()
    assert (output / "MANIFEST.json").is_file()


def test_strict_mode(tmp_path):
    """Test --strict flag."""
    repo = Path(__file__).parent.parent
    out_dir = tmp_path / "out"

    result = main(["--repo", str(repo), "--out", str(out_dir), "--strict"])
    assert result == 0

    output_dirs = list(out_dir.glob("agent-readiness-*"))
    output = output_dirs[0]
    manifest = json.loads((output / "MANIFEST.json").read_text())
    # In strict mode with any fail, score is capped at 59
    # Since this repo has LICENSE as pending, it should have some fails
    assert manifest["score"] <= 59


def test_scoring_module():
    """Test scoring logic directly."""
    from agent_readiness_lint.scoring import compute_score, score_label

    # Test label mapping
    assert score_label(90) == "Ready"
    assert score_label(70) == "Needs minor cleanup"
    assert score_label(50) == "Needs major cleanup"
    assert score_label(30) == "Not ready for agent work"

    # Test basic scoring
    results = {
        "agent_instructions": {
            "items": [{"status": "pass", "name": "t", "detail": "", "evidence": []}]
        },
        "test_ci_signals": {
            "items": [{"status": "pass", "name": "t", "detail": "", "evidence": []}]
        },
        "secret_risk": {
            "items": [{"status": "pass", "name": "t", "detail": "", "evidence": []}]
        },
        "public_readiness": {
            "items": [{"status": "pass", "name": "t", "detail": "", "evidence": []}]
        },
        "generated_hygiene": {
            "items": [{"status": "pass", "name": "t", "detail": "", "evidence": []}]
        },
    }
    score_data = compute_score(results)
    assert score_data["score"] == 100
    assert score_data["label"] == "Ready"


def test_checks_agent_instructions():
    """Test agent_instructions check module."""
    from agent_readiness_lint.checks.agent_instructions import check_agent_instructions

    repo = Path(__file__).parent.parent
    result = check_agent_instructions(repo)
    assert result["category"] == "agent_instructions"
    assert "items" in result
    assert len(result["items"]) > 0
    # This repo has AGENTS.md
    assert any(i["status"] == "pass" and "exists" in i["name"] for i in result["items"])
