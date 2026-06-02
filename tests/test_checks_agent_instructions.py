"""Tests for agent_instructions check module."""

from __future__ import annotations

from pathlib import Path

from agent_readiness_lint.checks.agent_instructions import check_agent_instructions


def test_agents_md_present(good_repo: Path):
    """Test detection of AGENTS.md when present."""
    result = check_agent_instructions(good_repo)
    assert result["category"] == "agent_instructions"
    assert result["detected_files"]["AGENTS.md"] is not None
    # The file-exists check should pass
    exists_item = next(i for i in result["items"] if i["name"] == "agent_instruction_file_exists")
    assert exists_item["status"] == "pass"


def test_agents_md_absent(empty_repo: Path):
    """Test detection when no instruction file exists."""
    result = check_agent_instructions(empty_repo)
    exists_item = next(i for i in result["items"] if i["name"] == "agent_instruction_file_exists")
    assert exists_item["status"] == "fail"
    # All sections should also be fail
    section_items = [i for i in result["items"] if i["name"].startswith("section_")]
    assert all(i["status"] == "fail" for i in section_items)


def test_all_sections_detected(good_repo: Path):
    """Test that all expected sections are found in a complete AGENTS.md."""
    result = check_agent_instructions(good_repo)
    section_items = [i for i in result["items"] if i["name"].startswith("section_")]
    # All sections should pass because good_repo has keywords for all
    assert all(i["status"] == "pass" for i in section_items), (
        f"Some sections did not pass: {[(i['name'], i['status']) for i in section_items if i['status'] != 'pass']}"
    )


def test_partial_sections(partial_repo: Path):
    """Test that partial AGENTS.md has some pass and some warn."""
    result = check_agent_instructions(partial_repo)
    section_items = [i for i in result["items"] if i["name"].startswith("section_")]
    statuses = {i["name"]: i["status"] for i in section_items}
    # Should have at least one pass (purpose/setup) and some warn
    assert "pass" in statuses.values()
    assert "warn" in statuses.values()


def test_claude_md_detected(tmp_path: Path):
    """Test detection of CLAUDE.md as agent instruction file."""
    (tmp_path / "CLAUDE.md").write_text("# Claude Instructions\n\n## Purpose\nTest project.\n")
    result = check_agent_instructions(tmp_path)
    assert result["detected_files"]["CLAUDE.md"] is not None
    exists_item = next(i for i in result["items"] if i["name"] == "agent_instruction_file_exists")
    assert exists_item["status"] == "pass"


def test_cursor_rules_detected(tmp_path: Path):
    """Test detection of .cursor/rules file."""
    cursor_dir = tmp_path / ".cursor"
    cursor_dir.mkdir()
    (cursor_dir / "rules").write_text("Project rules: setup commands, test commands.\n")
    result = check_agent_instructions(tmp_path)
    assert result["detected_files"][".cursor/rules"] is not None
    exists_item = next(i for i in result["items"] if i["name"] == "agent_instruction_file_exists")
    assert exists_item["status"] == "pass"
