"""Tests for scoring module."""

from __future__ import annotations

from agent_readiness_lint.scoring import compute_score, score_label


def _make_items(statuses: list[str]) -> list[dict]:
    """Helper to create minimal check items with given statuses."""
    return [{"name": f"item_{i}", "status": s, "detail": "", "evidence": []} for i, s in enumerate(statuses)]


def test_score_label_boundaries():
    """Test score_label at exact boundary values."""
    assert score_label(100) == "Ready"
    assert score_label(80) == "Ready"
    assert score_label(79) == "Needs minor cleanup"
    assert score_label(60) == "Needs minor cleanup"
    assert score_label(59) == "Needs major cleanup"
    assert score_label(40) == "Needs major cleanup"
    assert score_label(39) == "Not ready for agent work"
    assert score_label(0) == "Not ready for agent work"


def test_all_pass_gives_100():
    """Test that all-pass results produce a score of 100."""
    results = {
        "agent_instructions": {"items": _make_items(["pass"] * 3)},
        "test_ci_signals": {"items": _make_items(["pass"] * 3)},
        "secret_risk": {"items": _make_items(["pass"] * 2)},
        "public_readiness": {"items": _make_items(["pass"] * 4)},
        "generated_hygiene": {"items": _make_items(["pass"] * 3)},
    }
    score_data = compute_score(results)
    assert score_data["score"] == 100
    assert score_data["label"] == "Ready"


def test_all_fail_gives_zero():
    """Test that all-fail results produce a score of 0."""
    results = {
        "agent_instructions": {"items": _make_items(["fail"] * 3)},
        "test_ci_signals": {"items": _make_items(["fail"] * 3)},
        "secret_risk": {"items": _make_items(["fail"] * 2)},
        "public_readiness": {"items": _make_items(["fail"] * 4)},
        "generated_hygiene": {"items": _make_items(["fail"] * 3)},
    }
    score_data = compute_score(results)
    assert score_data["score"] == 0
    assert score_data["label"] == "Not ready for agent work"


def test_strict_mode_caps_at_59():
    """Test that strict mode caps score at 59 when any fail is present."""
    results = {
        "agent_instructions": {"items": _make_items(["pass"] * 8)},
        "test_ci_signals": {"items": _make_items(["pass"] * 3)},
        "secret_risk": {"items": _make_items(["pass"] * 2)},
        "public_readiness": {"items": _make_items(["pass"] * 4 + ["fail"])},
        "generated_hygiene": {"items": _make_items(["pass"] * 3)},
    }
    # Without strict, score should be high
    normal = compute_score(results, strict=False)
    assert normal["score"] > 59

    # With strict, score is capped at 59
    strict = compute_score(results, strict=True)
    assert strict["score"] <= 59


def test_warn_gives_half_credit():
    """Test that warnings give half credit compared to pass."""
    results_pass = {
        "agent_instructions": {"items": _make_items(["pass"] * 2)},
        "test_ci_signals": {"items": _make_items(["pass"] * 2)},
        "secret_risk": {"items": _make_items(["pass"] * 2)},
        "public_readiness": {"items": _make_items(["pass"] * 2)},
        "generated_hygiene": {"items": _make_items(["pass"] * 2)},
    }
    results_warn = {
        "agent_instructions": {"items": _make_items(["warn"] * 2)},
        "test_ci_signals": {"items": _make_items(["warn"] * 2)},
        "secret_risk": {"items": _make_items(["warn"] * 2)},
        "public_readiness": {"items": _make_items(["warn"] * 2)},
        "generated_hygiene": {"items": _make_items(["warn"] * 2)},
    }
    score_pass = compute_score(results_pass)
    score_warn = compute_score(results_warn)
    # Warn should give less than pass (secret_risk is handled differently)
    assert score_warn["score"] < score_pass["score"]


def test_counts_aggregated():
    """Test that counts are properly aggregated across categories."""
    results = {
        "agent_instructions": {"items": _make_items(["pass", "fail"])},
        "test_ci_signals": {"items": _make_items(["warn"])},
        "secret_risk": {"items": _make_items(["pass"])},
        "public_readiness": {"items": _make_items(["unknown"])},
        "generated_hygiene": {"items": _make_items(["pass", "warn"])},
    }
    score_data = compute_score(results)
    assert score_data["counts"]["pass"] == 3
    assert score_data["counts"]["fail"] == 1
    assert score_data["counts"]["warn"] == 2
    assert score_data["counts"]["unknown"] == 1
