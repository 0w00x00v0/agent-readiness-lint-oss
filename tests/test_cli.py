"""Tests for CLI interface."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from agent_readiness_lint.__main__ import main


def test_help_exits_zero(capsys):
    """Test that --help returns exit code 0."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_cli_creates_output_files(good_repo: Path, tmp_path: Path):
    """Test CLI with --repo creates all expected output files."""
    out_dir = tmp_path / "output"
    result = main(["--repo", str(good_repo), "--out", str(out_dir)])
    assert result == 0

    # Find the timestamped output directory
    output_dirs = list(out_dir.glob("agent-readiness-*"))
    assert len(output_dirs) == 1
    output = output_dirs[0]

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


def test_output_dir_naming_pattern(good_repo: Path, tmp_path: Path):
    """Test that the output directory matches the agent-readiness-YYYYMMDD-HHMMSS pattern."""
    out_dir = tmp_path / "output"
    main(["--repo", str(good_repo), "--out", str(out_dir)])
    output_dirs = list(out_dir.glob("agent-readiness-*"))
    assert len(output_dirs) == 1
    dirname = output_dirs[0].name
    # Pattern: agent-readiness-YYYYMMDD-HHMMSS
    pattern = r"^agent-readiness-\d{8}-\d{6}$"
    assert re.match(pattern, dirname), f"Directory name '{dirname}' does not match expected pattern"


def test_manifest_json_valid(good_repo: Path, tmp_path: Path):
    """Test MANIFEST.json is valid JSON with required fields."""
    out_dir = tmp_path / "output"
    main(["--repo", str(good_repo), "--out", str(out_dir)])
    output_dirs = list(out_dir.glob("agent-readiness-*"))
    manifest_path = output_dirs[0] / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())

    required_fields = [
        "schema_version",
        "generated_at_utc",
        "repo_path",
        "output_files",
        "score",
        "counts",
        "detected_files",
        "explicit_unknowns",
    ]
    for field in required_fields:
        assert field in manifest, f"Missing field in MANIFEST.json: {field}"

    assert isinstance(manifest["score"], int)
    assert 0 <= manifest["score"] <= 100
    assert isinstance(manifest["counts"], dict)
    assert isinstance(manifest["output_files"], list)


def test_out_path_receives_output(good_repo: Path, tmp_path: Path):
    """Test that --out path is where output is created."""
    custom_out = tmp_path / "custom" / "nested" / "out"
    result = main(["--repo", str(good_repo), "--out", str(custom_out)])
    assert result == 0
    assert custom_out.exists()
    output_dirs = list(custom_out.glob("agent-readiness-*"))
    assert len(output_dirs) == 1
