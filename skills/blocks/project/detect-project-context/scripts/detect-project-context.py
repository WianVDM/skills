#!/usr/bin/env python3
"""
detect-project-context.py

Detect the project root and recommended directories for skills, context, and config.

Deterministic, read-only, and safe. It never writes files and never asks the user.
Global skills and conductors use it to avoid hardcoding project paths.

Anchoring rules:
  - The upward marker search stops at the nearest VCS root (.git file or dir).
    A marker above the repo is never mistaken for the project.
  - If the search lands on the home directory, the answer is returned with
    confidence capped at low and a note, so callers confirm before use.

Markers:
  - Layout markers (.agents, .pi) carry skills/context/config subdirectories.
  - Harness markers (.claude, .codex, .cursor) identify the root only;
    candidates fall back to the standard .agents layout.

Usage:
  python detect-project-context.py [--start <dir>] [--json]

Exit codes:
  0 — detection returned (check confidence and note).
  2 — invalid input (bad start path).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple

LAYOUT_MARKERS = [".agents", ".pi"]
HARNESS_MARKERS = [".claude", ".codex", ".cursor"]
MARKER_DIRS = LAYOUT_MARKERS + HARNESS_MARKERS


def _dedupe(items: list) -> list:
    """Preserve order while removing duplicate entries."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _is_vcs_root(path: Path) -> bool:
    """A .git entry, dir or file (worktrees), marks a VCS root."""
    return (path / ".git").exists()


def find_project_root(start: Path) -> Tuple[Optional[Path], Optional[str]]:
    """Search upward from `start` for a known project marker directory.

    The search stops at the nearest VCS root: if no marker exists at or below
    it, the VCS root is returned with marker None and low confidence.
    Returns (root, marker); root is None if nothing anchors the project.
    """
    start = start.resolve()
    for path in [start] + list(start.parents):
        for marker in MARKER_DIRS:
            if (path / marker).is_dir():
                return path, marker
        if _is_vcs_root(path):
            return path, None
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
    notes = []

    if marker in LAYOUT_MARKERS:
        agents_dir = root_path / marker
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
        if marker in HARNESS_MARKERS:
            notes.append(
                f"Harness marker '{marker}' identifies the root but has no standard "
                "skills/context/config layout; using .agents-style candidates."
            )
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

    if marker is None:
        notes.append("No marker directory found; root fell back to the VCS root.")
        confidence = "low"

    if root_path == Path.home():
        notes.append("Marker found in the home directory; confirm this is the intended project root.")
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
        "note": "; ".join(notes) if notes else None,
    }


def _error(message: str) -> dict:
    return {"status": "error", "errors": [message]}


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
    if not start_path.exists() or not start_path.is_dir():
        reason = (
            f"start path does not exist: {args.start}"
            if not start_path.exists()
            else f"start path is not a directory: {args.start}"
        )
        if args.json:
            print(json.dumps(_error(reason)))
        else:
            print(f"ERROR: {reason}", file=sys.stderr)
        sys.exit(2)

    result = detect(start_path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"project_root: {result['project_root']}")
        print(f"marker: {result['marker']}")
        print(f"confidence: {result['confidence']}")
        if result.get("note"):
            print(f"note: {result['note']}")
        print(f"recommended_skills_dir: {result['recommended_skills_dir']}")
        print(f"recommended_context_dir: {result['recommended_context_dir']}")
        print(f"recommended_config_dir: {result['recommended_config_dir']}")


if __name__ == "__main__":
    main()
