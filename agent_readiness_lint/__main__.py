"""CLI entry point for agent-readiness-lint."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent_readiness_lint.checks import (
    check_agent_instructions,
    check_generated_hygiene,
    check_public_readiness,
    check_secret_risk,
    check_test_ci_signals,
)
from agent_readiness_lint.output import generate_outputs
from agent_readiness_lint.scoring import compute_score


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="agent-readiness-lint",
        description="Check repository readiness for AI agent workflows (local-only, no network calls).",
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="Path to the repository to analyze.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="./out",
        help="Base output directory (default: ./out). A timestamped subfolder will be created.",
    )
    parser.add_argument(
        "--project-name",
        type=str,
        default=None,
        help="Optional project name for report headers.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Strict mode: any fail result caps score at 59.",
    )
    parser.add_argument(
        "--include-prompts",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include CODEX_PROMPT.md and CHATGPT_REVIEW_PROMPT.md in output (default: true).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    # Validate repo path
    repo_path = Path(args.repo).resolve()
    if not repo_path.is_dir():
        print(f"Error: --repo path does not exist or is not a directory: {args.repo}", file=sys.stderr)
        return 1

    # Create timestamped output directory
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output_dir = Path(args.out).resolve() / f"agent-readiness-{timestamp}"

    # Run all checks
    results: dict = {
        "agent_instructions": check_agent_instructions(repo_path),
        "test_ci_signals": check_test_ci_signals(repo_path),
        "secret_risk": check_secret_risk(repo_path),
        "public_readiness": check_public_readiness(repo_path),
        "generated_hygiene": check_generated_hygiene(repo_path),
    }

    # Compute score
    score_data = compute_score(results, strict=args.strict)

    # Generate outputs
    files_written = generate_outputs(
        results=results,
        score_data=score_data,
        output_dir=output_dir,
        repo_path=str(repo_path),
        project_name=args.project_name,
        include_prompts=args.include_prompts,
    )

    # Print summary to stdout
    print(f"Agent Readiness Lint - Score: {score_data['score']}/100 ({score_data['label']})")
    print(f"Output: {output_dir}")
    print(f"Files: {', '.join(files_written)}")
    print(f"Counts: {score_data['counts']['pass']} pass, {score_data['counts']['warn']} warn, "
          f"{score_data['counts']['fail']} fail, {score_data['counts']['unknown']} unknown")

    return 0


if __name__ == "__main__":
    sys.exit(main())
