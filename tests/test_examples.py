"""Tests that run the CLI against the on-disk example fixture directories."""

from __future__ import annotations

import json
from pathlib import Path

from agent_readiness_lint.__main__ import main

FIXTURES_DIR = Path(__file__).parent.parent / "examples" / "fixtures"


def _run_fixture(fixture_name: str, tmp_path: Path) -> dict:
    """Run the CLI against a named fixture and return the MANIFEST.json data."""
    repo_path = FIXTURES_DIR / fixture_name
    out_dir = tmp_path / fixture_name
    result = main(["--repo", str(repo_path), "--out", str(out_dir)])
    assert result == 0, f"CLI exited with code {result} for {fixture_name}"

    output_dirs = list(out_dir.glob("agent-readiness-*"))
    assert len(output_dirs) == 1, f"Expected 1 output dir, found {len(output_dirs)}"

    manifest_path = output_dirs[0] / "MANIFEST.json"
    assert manifest_path.is_file(), "MANIFEST.json not created"

    manifest = json.loads(manifest_path.read_text())
    assert isinstance(manifest, dict)
    assert "score" in manifest
    return manifest


def test_good_repo_score(tmp_path: Path):
    """good-repo fixture should score >= 80."""
    manifest = _run_fixture("good-repo", tmp_path)
    assert manifest["score"] >= 80, f"good-repo scored {manifest['score']}, expected >= 80"


def test_minimal_repo_score(tmp_path: Path):
    """minimal-repo fixture should score < 50."""
    manifest = _run_fixture("minimal-repo", tmp_path)
    assert manifest["score"] < 50, f"minimal-repo scored {manifest['score']}, expected < 50"


def test_risky_repo_score(tmp_path: Path):
    """risky-repo fixture should score < 50."""
    manifest = _run_fixture("risky-repo", tmp_path)
    assert manifest["score"] < 50, f"risky-repo scored {manifest['score']}, expected < 50"


def test_good_repo_output_files(tmp_path: Path):
    """good-repo fixture should produce all expected output files."""
    repo_path = FIXTURES_DIR / "good-repo"
    out_dir = tmp_path / "good-output"
    result = main(["--repo", str(repo_path), "--out", str(out_dir)])
    assert result == 0

    output_dirs = list(out_dir.glob("agent-readiness-*"))
    output = output_dirs[0]

    expected_files = ["SUMMARY.md", "CHECKS.md", "MANIFEST.json"]
    for f in expected_files:
        assert (output / f).is_file(), f"Missing output file: {f}"


def test_minimal_repo_output_created(tmp_path: Path):
    """minimal-repo fixture should still produce output (exit 0)."""
    repo_path = FIXTURES_DIR / "minimal-repo"
    out_dir = tmp_path / "minimal-output"
    result = main(["--repo", str(repo_path), "--out", str(out_dir)])
    assert result == 0

    output_dirs = list(out_dir.glob("agent-readiness-*"))
    assert len(output_dirs) == 1


def test_risky_repo_output_created(tmp_path: Path):
    """risky-repo fixture should still produce output (exit 0)."""
    repo_path = FIXTURES_DIR / "risky-repo"
    out_dir = tmp_path / "risky-output"
    result = main(["--repo", str(repo_path), "--out", str(out_dir)])
    assert result == 0

    output_dirs = list(out_dir.glob("agent-readiness-*"))
    assert len(output_dirs) == 1


def test_risky_repo_strict_mode(tmp_path: Path):
    """risky-repo with --strict should cap score at <= 59 due to fail results."""
    repo_path = FIXTURES_DIR / "risky-repo"
    out_dir = tmp_path / "risky-strict"
    result = main(["--repo", str(repo_path), "--out", str(out_dir), "--strict"])
    assert result == 0

    output_dirs = list(out_dir.glob("agent-readiness-*"))
    assert len(output_dirs) == 1

    manifest_path = output_dirs[0] / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["score"] <= 59, (
        f"risky-repo with --strict scored {manifest['score']}, expected <= 59"
    )
