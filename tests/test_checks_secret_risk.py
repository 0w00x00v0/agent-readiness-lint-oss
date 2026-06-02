"""Tests for secret_risk check module."""

from __future__ import annotations

from pathlib import Path

from agent_readiness_lint.checks.secret_risk import check_secret_risk


def test_detects_suspicious_filenames(risky_repo: Path):
    """Test detection of .env and id_rsa as suspicious filenames."""
    result = check_secret_risk(risky_repo)
    assert result["category"] == "secret_risk"
    suspicious_paths = [sf["path"] for sf in result["suspicious_files"]]
    assert any(".env" in p for p in suspicious_paths)
    assert any("id_rsa" in p for p in suspicious_paths)


def test_detects_high_risk_content(risky_repo: Path):
    """Test content scanning finds AWS_SECRET and PRIVATE KEY markers."""
    result = check_secret_risk(risky_repo)
    content_paths = [cf["path"] for cf in result["content_findings"]]
    # config.py has AWS_SECRET_ACCESS_KEY
    assert any("config.py" in p for p in content_paths)
    # id_rsa has PRIVATE KEY header
    assert any("id_rsa" in p for p in content_paths)
    # high_risk_content item should be fail
    content_item = next(i for i in result["items"] if i["name"] == "high_risk_content")
    assert content_item["status"] == "fail"


def test_clean_repo_no_risks(good_repo: Path):
    """Test that a clean repo has no secret risks."""
    result = check_secret_risk(good_repo)
    assert len(result["suspicious_files"]) == 0
    assert len(result["content_findings"]) == 0
    for item in result["items"]:
        assert item["status"] == "pass"


def test_large_file_skipped(tmp_path: Path):
    """Test that files larger than 100KB are not content-scanned."""
    # Create a file larger than 100KB with a risk marker
    large_content = "AWS_SECRET_ACCESS_KEY=fake\n" + ("x" * 200_000)
    (tmp_path / "big_config.py").write_text(large_content)
    result = check_secret_risk(tmp_path)
    # The large file should not appear in content_findings
    content_paths = [cf["path"] for cf in result["content_findings"]]
    assert "big_config.py" not in content_paths


def test_symlink_outside_repo_skipped(tmp_path: Path):
    """Test that symlinked files pointing outside the repo are skipped."""
    import os
    import tempfile

    # Create a secret file outside the repo
    outside_dir = Path(tempfile.mkdtemp())
    secret_file = outside_dir / "leaked_secret.txt"
    secret_file.write_text("AWS_SECRET_ACCESS_KEY=real_secret_value\n")

    # Create a symlink inside the repo pointing to the outside file
    symlink_path = tmp_path / "linked_secret.txt"
    os.symlink(str(secret_file), str(symlink_path))

    result = check_secret_risk(tmp_path)

    # The symlinked file should NOT appear in content findings
    content_paths = [cf["path"] for cf in result["content_findings"]]
    assert "linked_secret.txt" not in content_paths

    # Clean up
    secret_file.unlink()
    outside_dir.rmdir()


def test_secret_detected_past_line_50(tmp_path: Path):
    """Test that secrets on lines beyond line 50 are still detected."""
    # Build a file with a secret on line 100
    lines = ["# harmless comment\n"] * 99
    lines.append("AWS_SECRET_ACCESS_KEY=deeply_buried_secret\n")
    (tmp_path / "deep_config.py").write_text("".join(lines))

    result = check_secret_risk(tmp_path)
    content_paths = [cf["path"] for cf in result["content_findings"]]
    assert "deep_config.py" in content_paths

    # Verify the finding references line 100
    for cf in result["content_findings"]:
        if cf["path"] == "deep_config.py":
            assert any("Line 100" in f for f in cf["findings"])
