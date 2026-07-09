#!/usr/bin/env python3
"""
detect-project-context.py

Detect the project root and recommended directories for skills, context, and config.

This script is deterministic, read-only, and safe. It never writes files and never
asks the user. It is used by global skills and conductors to avoid hardcoding
project paths.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple

MARKER_DIRS = [".agents", ".pi", "agents", ".claude", ".codex", ".cursor"]


def _dedupe(items: list) -> list:
    """Preserve order while removing duplicate entries."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _vcs_root(start: Path) -> Optional[Path]:
    """Return a VCS root (git) above start, or None."""
    for path in [start] + list(start.parents):
        if (path / ".git").is_dir():
            return path
    return None


def find_project_root(start: Path) -> Tuple[Optional[Path], Optional[str]]:
    """Search upward from `start` for a known project marker directory.

    If no marker is found, fall back to the nearest VCS root with low confidence.
    Returns (root, marker) where root may be None if nothing is found.
    """
    start = start.resolve()
    for path in [start] + list(start.parents):
        for marker in MARKER_DIRS:
            if (path / marker).is_dir():
                return path, marker

    # Fall back to VCS root; do not return the starting directory as the root.
    git_root = _vcs_root(start)
    if git_root:
        return git_root, None
    return None, None


def detect(start: Path) -> dict:
    root, marker = find_project_root(start)

    if root is None:
        return {
            "project_root": None,
            "marker": None,
            "confidence": "low",
            "recommended_skills_dir": None,
            "recommended_context_dir": None,
            "recommended_config_dir": None,
            "skills_dir_candidates": [],
            "context_dir_candidates": [],
            "config_dir_candidates": [],
            "note": "No project marker or VCS root found above the starting directory.",
        }

    root_path = root
    agents_dir = root_path / marker if marker else None

    if marker and agents_dir and agents_dir.is_dir():
        candidates = {
            "skills_dir_candidates": _dedupe([
                str(agents_dir / "skills"),
                str(root_path / ".agents" / "skills"),
                str(root_path / "skills"),
                str(root_path / "agents" / "skills"),
            ]),
            "context_dir_candidates": _dedupe([
                str(agents_dir / "context"),
                str(root_path / ".agents" / "context"),
                str(root_path / "context"),
            ]),
            "config_dir_candidates": _dedupe([
                str(agents_dir / "config"),
                str(root_path / ".agents" / "config"),
                str(root_path / "config"),
            ]),
        }
    else:
        candidates = {
            "skills_dir_candidates": [
                str(root_path / ".agents" / "skills"),
                str(root_path / "skills"),
                str(root_path / "agents" / "skills"),
            ],
            "context_dir_candidates": [
                str(root_path / ".agents" / "context"),
                str(root_path / "context"),
            ],
            "config_dir_candidates": [
                str(root_path / ".agents" / "config"),
                str(root_path / "config"),
            ],
        }

    def existing(cands):
        return [c for c in cands if c and Path(c).is_dir()]

    skills_existing = existing(candidates["skills_dir_candidates"])
    context_existing = existing(candidates["context_dir_candidates"])
    config_existing = existing(candidates["config_dir_candidates"])

    recommended_skills_dir = (
        skills_existing[0] if skills_existing else candidates["skills_dir_candidates"][0]
    )
    recommended_context_dir = (
        context_existing[0] if context_existing else candidates["context_dir_candidates"][0]
    )
    recommended_config_dir = (
        config_existing[0] if config_existing else candidates["config_dir_candidates"][0]
    )

    if skills_existing and context_existing:
        confidence = "high"
    elif skills_existing or context_existing or config_existing:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "project_root": str(root_path),
        "marker": marker,
        "confidence": confidence,
        "recommended_skills_dir": recommended_skills_dir,
        "recommended_context_dir": recommended_context_dir,
        "recommended_config_dir": recommended_config_dir,
        "skills_dir_candidates": candidates["skills_dir_candidates"],
        "context_dir_candidates": candidates["context_dir_candidates"],
        "config_dir_candidates": candidates["config_dir_candidates"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect project context for skill tooling."
    )
    parser.add_argument(
        "--start", default=".", help="Directory to start searching from."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    start_path = Path(args.start)
    if not start_path.exists():
        error = {
            "error": "start path does not exist",
            "start": args.start,
        }
        if args.json:
            print(json.dumps(error))
        else:
            print(f"ERROR: start path does not exist: {args.start}", file=sys.stderr)
        sys.exit(1)
    if not start_path.is_dir():
        error = {
            "error": "start path is not a directory",
            "start": args.start,
        }
        if args.json:
            print(json.dumps(error))
        else:
            print(f"ERROR: start path is not a directory: {args.start}", file=sys.stderr)
        sys.exit(1)

    result = detect(start_path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
