"""Shared path-safety utilities for check modules."""

from __future__ import annotations

from pathlib import Path


def is_within_repo(file_path: Path, repo_path: Path) -> bool:
    """Check that file_path resolves to a location within repo_path.

    Returns True if the resolved file_path is relative to the resolved
    repo_path. This prevents symlink escape attacks where a symlinked
    file inside the repo points to a location outside the repo tree.
    """
    try:
        return file_path.resolve().is_relative_to(repo_path.resolve())
    except (OSError, ValueError):
        return False
