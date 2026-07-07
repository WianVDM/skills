#!/usr/bin/env python3
"""
detect-project-context.py

Detect the project root and recommended directories for skills, context, and config.

This script is deterministic, read-only, and safe. It never writes files and never
asks the user. It is used by global skills and conductors to avoid hardcoding
project paths.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MARKER_DIRS = [".agents", ".pi", "agents", ".claude", ".codex", ".cursor"]


def find_project_root(start: Path) -> tuple[Path, str | None]:
    """Search upward from `start` for a known project marker directory."""
    start = start.resolve()
    for path in [start] + list(start.parents):
        for marker in MARKER_DIRS:
            if (path / marker).is_dir():
                return path, marker
    return start, None


def detect(start: Path) -> dict:
    root, marker = find_project_root(start)
    agents_dir = root / marker if marker else None

    if agents_dir and agents_dir.is_dir():
        candidates = {
            "skills_dir_candidates": [str(agents_dir / "skills")],
            "context_dir_candidates": [str(agents_dir / "context")],
            "config_dir_candidates": [str(agents_dir / "config")],
        }
    else:
        candidates = {
            "skills_dir_candidates": [
                str(root / ".agents" / "skills"),
                str(root / "skills"),
                str(root / "agents" / "skills"),
            ],
            "context_dir_candidates": [
                str(root / ".agents" / "context"),
                str(root / "context"),
            ],
            "config_dir_candidates": [
                str(root / ".agents" / "config"),
                str(root / "config"),
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
    elif skills_existing or context_existing:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "project_root": str(root),
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

    result = detect(Path(args.start))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
