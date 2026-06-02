"""Output file generation for agent-readiness-lint."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _get_blockers(results: dict[str, dict[str, Any]]) -> list[str]:
    """Extract top blockers (fail items) from results."""
    blockers: list[str] = []
    for category, result in results.items():
        for item in result.get("items", []):
            if item.get("status") == "fail":
                blockers.append(f"[{category}] {item['detail']}")
    return blockers


def _get_warnings(results: dict[str, dict[str, Any]]) -> list[str]:
    """Extract warnings from results."""
    warnings: list[str] = []
    for category, result in results.items():
        for item in result.get("items", []):
            if item.get("status") == "warn":
                warnings.append(f"[{category}] {item['detail']}")
    return warnings


def _get_detected_files(results: dict[str, dict[str, Any]]) -> list[str]:
    """Collect all detected/evidence files."""
    files: list[str] = []
    for result in results.values():
        for item in result.get("items", []):
            for ev in item.get("evidence", []):
                if ev and ev not in files:
                    files.append(ev)
    return files


def _get_unknowns(results: dict[str, dict[str, Any]]) -> list[str]:
    """Get explicit unknowns."""
    unknowns: list[str] = []
    for category, result in results.items():
        for item in result.get("items", []):
            if item.get("status") == "unknown":
                unknowns.append(f"[{category}] {item['detail']}")
    return unknowns


def generate_summary_md(
    score_data: dict[str, Any],
    results: dict[str, dict[str, Any]],
    repo_path: str,
    project_name: str | None,
) -> str:
    """Generate SUMMARY.md content."""
    blockers = _get_blockers(results)
    warnings = _get_warnings(results)
    unknowns = _get_unknowns(results)

    title = project_name or Path(repo_path).name
    lines = [
        f"# Agent Readiness Summary: {title}",
        "",
        f"**Score:** {score_data['score']}/100 - {score_data['label']}",
        "",
        "## Category Scores",
        "",
    ]

    for cat, pts in score_data.get("category_scores", {}).items():
        lines.append(f"- **{cat}**: {pts} points")

    lines.append("")
    lines.append("## Top Blockers")
    lines.append("")
    if blockers:
        for b in blockers[:10]:
            lines.append(f"- {b}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if warnings:
        for w in warnings[:10]:
            lines.append(f"- {w}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("## Recommended Next Actions")
    lines.append("")
    if blockers:
        lines.append("1. Address all blockers listed above")
    if warnings:
        lines.append("2. Review warnings and fix where practical")
    if not blockers and not warnings:
        lines.append("- Repository looks ready for agent-assisted work!")

    lines.append("")
    lines.append("## Explicit Unknowns")
    lines.append("")
    if unknowns:
        for u in unknowns:
            lines.append(f"- {u}")
    else:
        lines.append("- None")

    lines.append("")
    return "\n".join(lines)


def generate_checks_md(results: dict[str, dict[str, Any]]) -> str:
    """Generate CHECKS.md content with detailed checklist."""
    lines = [
        "# Detailed Check Results",
        "",
    ]

    status_icons = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]", "unknown": "[????]"}

    for category, result in results.items():
        lines.append(f"## {category}")
        lines.append("")
        for item in result.get("items", []):
            status = item.get("status", "unknown")
            icon = status_icons.get(status, "[????]")
            lines.append(f"- {icon} **{item['name']}**: {item['detail']}")
            evidence = item.get("evidence", [])
            if evidence:
                lines.append(f"  - Evidence: {', '.join(str(e) for e in evidence)}")
        lines.append("")

    return "\n".join(lines)


def generate_agents_suggestions_md(results: dict[str, dict[str, Any]]) -> str:
    """Generate AGENTS_SUGGESTIONS.md content."""
    lines = [
        "# Suggested AGENTS.md Improvements",
        "",
        "Based on the readiness analysis, consider adding or improving the following sections:",
        "",
    ]

    ai_result = results.get("agent_instructions", {})
    sections = ai_result.get("sections", {})

    for section_name, status in sections.items():
        if status != "pass":
            lines.append(f"## {section_name.replace('_', ' ').title()}")
            lines.append("")
            lines.append(_suggest_section_content(section_name))
            lines.append("")

    if all(s == "pass" for s in sections.values()) and sections:
        lines.append("All expected sections are present. No changes needed.")
        lines.append("")

    return "\n".join(lines)


def _suggest_section_content(section_name: str) -> str:
    """Provide a concise draft snippet for a missing section."""
    suggestions = {
        "project purpose": (
            "Add a brief description of what this project does:\n\n"
            "```markdown\n"
            "## Project Purpose\n"
            "This project [describe what it does and who it is for].\n"
            "```"
        ),
        "setup commands": (
            "Add setup/installation commands:\n\n"
            "```markdown\n"
            "## Setup\n"
            "```bash\n"
            "pip install -e '.[dev]'\n"
            "```\n"
            "```"
        ),
        "test commands": (
            "Add instructions on how to run tests:\n\n"
            "```markdown\n"
            "## Testing\n"
            "```bash\n"
            "pytest tests/ -v\n"
            "```\n"
            "```"
        ),
        "file boundaries": (
            "Document which files/directories are in scope:\n\n"
            "```markdown\n"
            "## File Boundaries\n"
            "- Source code: src/ or package_name/\n"
            "- Tests: tests/\n"
            "- Do not modify: generated files, lock files\n"
            "```"
        ),
        "generated files": (
            "List files that are generated and should not be committed:\n\n"
            "```markdown\n"
            "## Generated Files\n"
            "Do not commit: out/, __pycache__/, .venv/, node_modules/\n"
            "```"
        ),
        "secrets": (
            "Add a warning about secrets/private data:\n\n"
            "```markdown\n"
            "## Secrets and Private Data\n"
            "- Never commit .env files, API keys, or credentials\n"
            "- Do not access credential stores or environment variables beyond what is documented\n"
            "```"
        ),
        "non-goals": (
            "Document what is explicitly out of scope:\n\n"
            "```markdown\n"
            "## Non-Goals\n"
            "- No network calls or API usage\n"
            "- No browser automation\n"
            "- No production data access\n"
            "```"
        ),
    }
    return suggestions.get(section_name, "Consider adding a section for this topic.")


def generate_codex_prompt_md(
    score_data: dict[str, Any],
    results: dict[str, dict[str, Any]],
    project_name: str | None,
) -> str:
    """Generate CODEX_PROMPT.md - English prompt for Codex to fix gaps."""
    blockers = _get_blockers(results)
    warnings = _get_warnings(results)

    title = project_name or "this repository"
    lines = [
        "# Codex Prompt: Fix Agent Readiness Gaps",
        "",
        f"The following issues were found in {title} (score: {score_data['score']}/100).",
        "Please fix these issues to improve agent readiness:",
        "",
    ]

    if blockers:
        lines.append("## Blockers (must fix)")
        lines.append("")
        for b in blockers:
            lines.append(f"- {b}")
        lines.append("")

    if warnings:
        lines.append("## Warnings (should fix)")
        lines.append("")
        for w in warnings[:15]:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## Instructions")
    lines.append("")
    lines.append("- Fix each issue above by creating or modifying the relevant files")
    lines.append("- Do not make network calls or access external APIs")
    lines.append("- Keep changes minimal and focused on the identified gaps")
    lines.append("- Ensure any new files follow the project's existing conventions")
    lines.append("")

    return "\n".join(lines)


def generate_chatgpt_review_prompt_md(
    score_data: dict[str, Any],
    results: dict[str, dict[str, Any]],
    project_name: str | None,
) -> str:
    """Generate CHATGPT_REVIEW_PROMPT.md - Japanese prompt for ChatGPT review."""
    title = project_name or "this repository"
    blockers = _get_blockers(results)
    warnings = _get_warnings(results)

    lines = [
        "# ChatGPT Review Prompt",
        "",
        "以下はリポジトリのエージェント対応準備状況の分析結果です。",
        f"リポジトリ: {title}",
        f"スコア: {score_data['score']}/100 ({score_data['label']})",
        "",
        "## 注意事項",
        "",
        "- この分析はローカルファイルの静的検査に基づいています",
        "- 実際のコード品質やセキュリティの完全な評価ではありません",
        "- 提案は参考情報として扱い、プロジェクトの文脈に合わせて判断してください",
        "",
        "## 検出された問題",
        "",
    ]

    if blockers:
        lines.append("### ブロッカー（要対応）")
        lines.append("")
        for b in blockers:
            lines.append(f"- {b}")
        lines.append("")

    if warnings:
        lines.append("### 警告（推奨対応）")
        lines.append("")
        for w in warnings[:10]:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## レビュー依頼")
    lines.append("")
    lines.append("上記の問題点について、以下の観点でレビューしてください：")
    lines.append("1. 各問題の重要度と対応優先順位")
    lines.append("2. プロジェクトの性質を考慮した改善提案")
    lines.append("3. 見落としている可能性のある追加の懸念事項")
    lines.append("")

    return "\n".join(lines)


def generate_manifest_json(
    score_data: dict[str, Any],
    results: dict[str, dict[str, Any]],
    repo_path: str,
    output_dir: Path,
    output_files: list[str],
) -> str:
    """Generate MANIFEST.json content."""
    detected_files = _get_detected_files(results)
    unknowns = _get_unknowns(results)

    manifest = {
        "schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo_path": str(repo_path),
        "output_dir": str(output_dir),
        "output_files": output_files,
        "score": score_data["score"],
        "label": score_data["label"],
        "counts": score_data["counts"],
        "category_scores": score_data["category_scores"],
        "detected_files": detected_files,
        "explicit_unknowns": unknowns,
    }

    return json.dumps(manifest, indent=2, ensure_ascii=False)


def generate_outputs(
    results: dict[str, dict[str, Any]],
    score_data: dict[str, Any],
    output_dir: Path,
    repo_path: str,
    project_name: str | None = None,
    include_prompts: bool = True,
) -> list[str]:
    """Generate all output files.

    Returns list of generated filenames.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    files_written: list[str] = []

    # SUMMARY.md
    summary = generate_summary_md(score_data, results, repo_path, project_name)
    (output_dir / "SUMMARY.md").write_text(summary, encoding="utf-8")
    files_written.append("SUMMARY.md")

    # CHECKS.md
    checks = generate_checks_md(results)
    (output_dir / "CHECKS.md").write_text(checks, encoding="utf-8")
    files_written.append("CHECKS.md")

    # AGENTS_SUGGESTIONS.md
    suggestions = generate_agents_suggestions_md(results)
    (output_dir / "AGENTS_SUGGESTIONS.md").write_text(suggestions, encoding="utf-8")
    files_written.append("AGENTS_SUGGESTIONS.md")

    if include_prompts:
        # CODEX_PROMPT.md
        codex = generate_codex_prompt_md(score_data, results, project_name)
        (output_dir / "CODEX_PROMPT.md").write_text(codex, encoding="utf-8")
        files_written.append("CODEX_PROMPT.md")

        # CHATGPT_REVIEW_PROMPT.md
        chatgpt = generate_chatgpt_review_prompt_md(score_data, results, project_name)
        (output_dir / "CHATGPT_REVIEW_PROMPT.md").write_text(chatgpt, encoding="utf-8")
        files_written.append("CHATGPT_REVIEW_PROMPT.md")

    # MANIFEST.json
    manifest = generate_manifest_json(
        score_data, results, repo_path, output_dir, files_written + ["MANIFEST.json"]
    )
    (output_dir / "MANIFEST.json").write_text(manifest, encoding="utf-8")
    files_written.append("MANIFEST.json")

    return files_written
