"""Tests for public_readiness check module."""

from __future__ import annotations

from pathlib import Path

from agent_readiness_lint.checks.public_readiness import check_public_readiness


def test_good_repo_all_pass(good_repo: Path):
    """Test that a well-configured repo passes all readiness checks."""
    result = check_public_readiness(good_repo)
    assert result["category"] == "public_readiness"
    # All items should pass
    for item in result["items"]:
        assert item["status"] == "pass", f"{item['name']} was {item['status']}: {item['detail']}"


def test_empty_repo_all_fail_or_warn(empty_repo: Path):
    """Test that an empty repo fails/warns on all presence checks."""
    result = check_public_readiness(empty_repo)
    for item in result["items"]:
        assert item["status"] in ("fail", "warn"), f"{item['name']} unexpectedly passed"


def test_partial_repo_mixed_results(partial_repo: Path):
    """Test that a partial repo has a mix of pass and fail/warn."""
    result = check_public_readiness(partial_repo)
    statuses = [item["status"] for item in result["items"]]
    assert "pass" in statuses  # README and .gitignore exist
    assert "fail" in statuses or "warn" in statuses  # LICENSE missing, etc.


def test_readme_detected(good_repo: Path):
    """Test README.md is detected."""
    result = check_public_readiness(good_repo)
    readme_item = next(i for i in result["items"] if i["name"] == "readme")
    assert readme_item["status"] == "pass"
    assert "README.md" in readme_item["evidence"]
