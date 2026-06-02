"""Tests for generated_hygiene check module."""

from __future__ import annotations

from pathlib import Path

from agent_readiness_lint.checks.generated_hygiene import check_generated_hygiene


def test_good_repo_all_ignores_present(good_repo: Path):
    """Test that good_repo has all expected ignore patterns."""
    result = check_generated_hygiene(good_repo)
    assert result["category"] == "generated_hygiene"
    # All items should pass
    for item in result["items"]:
        assert item["status"] == "pass", f"{item['name']} was {item['status']}: {item['detail']}"


def test_no_gitignore(empty_repo: Path):
    """Test that a repo with no .gitignore reports fail + all warns."""
    result = check_generated_hygiene(empty_repo)
    exists_item = next(i for i in result["items"] if i["name"] == "gitignore_exists")
    assert exists_item["status"] == "fail"
    # All pattern items should be warn
    pattern_items = [i for i in result["items"] if i["name"] != "gitignore_exists"]
    assert all(i["status"] == "warn" for i in pattern_items)


def test_partial_gitignore(partial_repo: Path):
    """Test a .gitignore missing some patterns reports mixed results."""
    result = check_generated_hygiene(partial_repo)
    exists_item = next(i for i in result["items"] if i["name"] == "gitignore_exists")
    assert exists_item["status"] == "pass"
    # Some should pass (e.g., __pycache__/, .venv/) and some should warn
    pattern_items = [i for i in result["items"] if i["name"] != "gitignore_exists"]
    statuses = [i["status"] for i in pattern_items]
    assert "pass" in statuses
    assert "warn" in statuses


def test_double_star_pattern_recognized(tmp_path: Path):
    """Test that **/pattern in .gitignore matches expected patterns."""
    (tmp_path / ".gitignore").write_text(
        "**/node_modules/\n**/out/\n**/__pycache__/\n"
    )
    result = check_generated_hygiene(tmp_path)
    # node_modules, out, __pycache__ should be detected as covered
    node_item = next(
        i for i in result["items"] if i["name"] == "ignore_node_modules"
    )
    assert node_item["status"] == "pass"
    out_item = next(i for i in result["items"] if i["name"] == "ignore_out")
    assert out_item["status"] == "pass"
    pycache_item = next(
        i for i in result["items"] if i["name"] == "ignore___pycache__"
    )
    assert pycache_item["status"] == "pass"


def test_inline_comments_stripped(tmp_path: Path):
    """Test that inline comments are stripped from gitignore lines."""
    (tmp_path / ".gitignore").write_text(
        "out/ # generated output\n"
        "logs/ # runtime logs\n"
        ".venv/ # virtual env\n"
    )
    result = check_generated_hygiene(tmp_path)
    out_item = next(i for i in result["items"] if i["name"] == "ignore_out")
    assert out_item["status"] == "pass"
    logs_item = next(i for i in result["items"] if i["name"] == "ignore_logs")
    assert logs_item["status"] == "pass"
    venv_item = next(i for i in result["items"] if i["name"] == "ignore__venv")
    assert venv_item["status"] == "pass"
