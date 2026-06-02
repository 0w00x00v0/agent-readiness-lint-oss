"""Scoring logic for agent-readiness-lint."""

from __future__ import annotations

from typing import Any


# Category weights (max points)
CATEGORY_WEIGHTS = {
    "agent_instructions": 30,
    "test_ci_signals": 20,
    "secret_risk": 15,
    "public_readiness": 20,
    "generated_hygiene": 15,
}

TOTAL_MAX = sum(CATEGORY_WEIGHTS.values())  # 100


def _count_statuses(items: list[dict[str, Any]]) -> dict[str, int]:
    """Count pass/warn/fail/unknown in a list of check items."""
    counts: dict[str, int] = {"pass": 0, "warn": 0, "fail": 0, "unknown": 0}
    for item in items:
        status = item.get("status", "unknown")
        if status in counts:
            counts[status] += 1
        else:
            counts["unknown"] += 1
    return counts


def _score_category(items: list[dict[str, Any]], max_points: int) -> float:
    """Score a category based on pass/warn/fail ratios."""
    if not items:
        return 0.0
    counts = _count_statuses(items)
    total = len(items)
    # pass = full credit, warn = half credit, fail/unknown = 0
    earned = counts["pass"] + (counts["warn"] * 0.5)
    ratio = earned / total
    return round(ratio * max_points, 1)


def _score_secret_risk(items: list[dict[str, Any]], max_points: int) -> float:
    """Score secret risk - deductions for findings."""
    counts = _count_statuses(items)
    # Start with full points, deduct for issues
    if counts["fail"] > 0:
        return 0.0
    if counts["warn"] > 0:
        return max_points * 0.5
    return float(max_points)


def score_label(score: int) -> str:
    """Map a numeric score to a human-readable label."""
    if score >= 80:
        return "Ready"
    elif score >= 60:
        return "Needs minor cleanup"
    elif score >= 40:
        return "Needs major cleanup"
    else:
        return "Not ready for agent work"


def compute_score(results: dict[str, dict[str, Any]], strict: bool = False) -> dict[str, Any]:
    """Compute overall score from all check results.

    Args:
        results: dict mapping category name to check result dict (must have "items" key)
        strict: if True, any fail result caps score at 59

    Returns:
        dict with score, label, category_scores, and counts
    """
    category_scores: dict[str, float] = {}
    total_counts: dict[str, int] = {"pass": 0, "warn": 0, "fail": 0, "unknown": 0}

    for category, max_points in CATEGORY_WEIGHTS.items():
        check_result = results.get(category, {})
        items = check_result.get("items", [])
        counts = _count_statuses(items)
        for k in total_counts:
            total_counts[k] += counts[k]

        if category == "secret_risk":
            category_scores[category] = _score_secret_risk(items, max_points)
        else:
            category_scores[category] = _score_category(items, max_points)

    raw_score = int(round(sum(category_scores.values())))

    # Strict mode: any fail caps at 59
    if strict and total_counts["fail"] > 0:
        raw_score = min(raw_score, 59)

    # Clamp to 0-100
    final_score = max(0, min(100, raw_score))
    label = score_label(final_score)

    return {
        "score": final_score,
        "label": label,
        "category_scores": category_scores,
        "counts": total_counts,
    }
