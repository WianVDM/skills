#!/usr/bin/env python3
"""Detect the project marker directory and derive config/context paths.

Looks for known marker directories in this order:
    1. .agents
    2. .pi
    3. agents

If none are found, the current working directory is used as a fallback
with low confidence.

Outputs JSON:
    {
      "marker_dir": "...",
      "config_dir": "...",
      "context_dir": "...",
      "confidence": "high|medium|low"
    }

On failure:
    {"error": "..."}

The script is read-only, deterministic, and safe to run in any project.
"""

import argparse
import json
import sys
from pathlib import Path

MARKERS = [".agents", ".pi", "agents"]


def detect_project_layout(cwd: Path = None) -> dict:
    """Return the detected project layout paths."""
    if cwd is None:
        cwd = Path.cwd()

    for marker in MARKERS:
        marker_dir = cwd / marker
        if marker_dir.exists() and marker_dir.is_dir():
            return {
                "marker_dir": str(marker_dir.resolve()),
                "config_dir": str((marker_dir / "config").resolve()),
                "context_dir": str((marker_dir / "context").resolve()),
                "confidence": "high",
            }

    # Fallback: use current working directory
    return {
        "marker_dir": str(cwd.resolve()),
        "config_dir": str((cwd / "config").resolve()),
        "context_dir": str((cwd / "context").resolve()),
        "confidence": "low",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect the project marker directory and derive config/context paths."
    )
    parser.add_argument(
        "--cwd",
        help="Override the working directory to inspect. Default: current directory.",
    )
    args = parser.parse_args()

    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    try:
        result = detect_project_layout(cwd)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:  # pragma: no cover - safety net
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
