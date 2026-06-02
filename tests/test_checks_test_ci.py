"""Tests for test_ci_signals check module."""

from __future__ import annotations

from pathlib import Path

from agent_readiness_lint.checks.test_ci_signals import check_test_ci_signals


def test_detects_test_files(good_repo: Path):
    """Test detection of test files in a well-structured repo."""
    result = check_test_ci_signals(good_repo)
    assert result["category"] == "test_ci_signals"
    assert len(result["test_files"]) > 0
    assert any("test_example.py" in f for f in result["test_files"])


def test_detects_test_dirs(good_repo: Path):
    """Test detection of test directories."""
    result = check_test_ci_signals(good_repo)
    assert "tests" in result["test_dirs"]


def test_detects_ci_files(good_repo: Path):
    """Test detection of CI workflow files."""
    result = check_test_ci_signals(good_repo)
    assert len(result["ci_files"]) > 0
    assert any("ci.yml" in f for f in result["ci_files"])
    ci_item = next(i for i in result["items"] if i["name"] == "ci_configured")
    assert ci_item["status"] == "pass"


def test_no_test_files_empty_repo(empty_repo: Path):
    """Test that an empty repo has no test files detected."""
    result = check_test_ci_signals(empty_repo)
    assert result["test_files"] == []
    assert result["test_dirs"] == []
    assert result["ci_files"] == []
    test_item = next(i for i in result["items"] if i["name"] == "test_files_exist")
    assert test_item["status"] == "warn"


def test_framework_detection_from_pyproject(good_repo: Path):
    """Test that pytest is detected from pyproject.toml."""
    result = check_test_ci_signals(good_repo)
    assert "pytest" in result["frameworks"]
    fw_item = next(i for i in result["items"] if i["name"] == "test_framework_detected")
    assert fw_item["status"] == "pass"


def test_inferred_test_commands(good_repo: Path):
    """Test that test commands are inferred from frameworks."""
    result = check_test_ci_signals(good_repo)
    assert "pytest" in result["inferred_test_commands"]


def test_symlink_outside_repo_skipped(tmp_path: Path):
    """Test that symlinked test files pointing outside the repo are skipped."""
    import os
    import tempfile

    # Create a test file outside the repo
    outside_dir = Path(tempfile.mkdtemp())
    outside_test = outside_dir / "test_external.py"
    outside_test.write_text("def test_external():\n    assert True\n")

    # Create a symlink inside the repo pointing to the outside file
    symlink_path = tmp_path / "test_external.py"
    os.symlink(str(outside_test), str(symlink_path))

    result = check_test_ci_signals(tmp_path)

    # The symlinked file should NOT appear in test_files
    assert "test_external.py" not in result["test_files"]

    # Clean up
    outside_test.unlink()
    outside_dir.rmdir()
