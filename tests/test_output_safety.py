"""Tests for output path safety and input validation."""

from __future__ import annotations

from pathlib import Path

from agent_readiness_lint.__main__ import main


def test_repo_must_be_existing_directory(tmp_path: Path):
    """Test that --repo must point to an existing directory."""
    result = main(["--repo", "/nonexistent/path/xyz", "--out", str(tmp_path / "out")])
    assert result == 1


def test_repo_cannot_be_a_file(tmp_path: Path):
    """Test that --repo rejects a file path (must be directory)."""
    file_path = tmp_path / "some_file.txt"
    file_path.write_text("not a directory")
    result = main(["--repo", str(file_path), "--out", str(tmp_path / "out")])
    assert result == 1


def test_output_created_under_out_dir(good_repo: Path, tmp_path: Path):
    """Test that all output files are created under the --out directory."""
    out_dir = tmp_path / "safe_out"
    main(["--repo", str(good_repo), "--out", str(out_dir)])

    # Walk all generated files and ensure they are under out_dir
    out_dir_resolved = out_dir.resolve()
    for f in out_dir.rglob("*"):
        assert str(f.resolve()).startswith(str(out_dir_resolved)), (
            f"File {f} is not under --out directory"
        )
