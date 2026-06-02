"""Check for potential secret/credential exposure risks."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from agent_readiness_lint.checks._path_safety import is_within_repo


SUSPICIOUS_FILENAMES = [
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
]

SUSPICIOUS_EXTENSIONS = [
    ".key",
    ".pem",
]

SUSPICIOUS_NAME_PATTERNS = [
    "token",
    "secret",
    "credential",
    "cookie",
    "session",
    "private-key",
    "private_key",
]

HIGH_RISK_MARKERS = [
    "aws_secret",
    "aws_access_key",
    "private key",
    "-----begin rsa private key",
    "-----begin openssh private key",
    "-----begin ec private key",
    "-----begin private key",
    "password=",
    "password =",
    "api_key=",
    "api_key =",
    "apikey=",
    "secret_key=",
    "secret_key =",
    "authorization: bearer",
]

# Max file size to scan (100KB)
MAX_SCAN_SIZE = 100 * 1024


def _is_suspicious_filename(filename: str) -> bool:
    """Check if a filename matches suspicious patterns."""
    lower = filename.lower()
    if lower in SUSPICIOUS_FILENAMES:
        return True
    for ext in SUSPICIOUS_EXTENSIONS:
        if lower.endswith(ext):
            return True
    for pattern in SUSPICIOUS_NAME_PATTERNS:
        if pattern in lower:
            return True
    return False


def _scan_file_content(file_path: Path) -> list[str]:
    """Scan a file for high-risk markers (up to MAX_SCAN_SIZE bytes)."""
    findings: list[str] = []
    try:
        size = file_path.stat().st_size
        if size > MAX_SCAN_SIZE:
            return []
        # Skip binary files
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                lower_line = line.lower()
                for marker in HIGH_RISK_MARKERS:
                    if marker in lower_line:
                        findings.append(f"Line {i + 1}: matches '{marker}'")
                        break
    except OSError:
        pass
    return findings


def check_secret_risk(repo_path: Path) -> dict[str, Any]:
    """Run the secret risk check.

    Scans for suspicious filenames and high-risk content markers.
    All file access is constrained to repo_path.
    """
    suspicious_files: list[dict[str, Any]] = []
    content_findings: list[dict[str, Any]] = []

    for root, dirs, files in os.walk(repo_path):
        # Skip hidden dirs (except specific ones), node_modules, venvs
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in ("node_modules", ".venv", "venv", "__pycache__")
        ]
        rel_root = Path(root).relative_to(repo_path)

        for f in files:
            rel_path = str(rel_root / f)
            file_path = Path(root) / f

            # Skip files that resolve outside the repo (symlink escape)
            if not is_within_repo(file_path, repo_path):
                continue

            # Check suspicious filename
            if _is_suspicious_filename(f):
                suspicious_files.append({
                    "path": rel_path,
                    "reason": "suspicious filename",
                })

            # Scan content of text files
            if file_path.is_file():
                findings = _scan_file_content(file_path)
                if findings:
                    content_findings.append({
                        "path": rel_path,
                        "findings": findings,
                    })

    items: list[dict[str, Any]] = []

    # Suspicious filenames
    if suspicious_files:
        items.append({
            "name": "suspicious_filenames",
            "status": "warn",
            "evidence": [sf["path"] for sf in suspicious_files],
            "detail": f"Found {len(suspicious_files)} file(s) with suspicious names.",
        })
    else:
        items.append({
            "name": "suspicious_filenames",
            "status": "pass",
            "evidence": [],
            "detail": "No files with suspicious names detected.",
        })

    # Content scanning
    if content_findings:
        items.append({
            "name": "high_risk_content",
            "status": "fail",
            "evidence": [cf["path"] for cf in content_findings],
            "detail": f"Found high-risk content markers in {len(content_findings)} file(s).",
        })
    else:
        items.append({
            "name": "high_risk_content",
            "status": "pass",
            "evidence": [],
            "detail": "No high-risk content markers detected in scanned files.",
        })

    return {
        "category": "secret_risk",
        "suspicious_files": suspicious_files,
        "content_findings": content_findings,
        "items": items,
    }
