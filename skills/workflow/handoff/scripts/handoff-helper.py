#!/usr/bin/env python3
"""
handoff-helper.py

Deterministic helper for the handoff skill.

This helper does not delete, overwrite, or modify existing handoff files. It only
resolves new handoff paths.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HANDOFFS_DIR = "handoffs"


def normalize_key(key: str) -> str:
    """Normalize a ticket key or session alias for use as a directory name."""
    key = key.lower().strip()
    key = re.sub(r"[^a-z0-9]+", "-", key)
    key = key.strip("-")
    return key or "untitled"


def _is_writable(path: Path) -> bool:
    """Check whether the directory is writable."""
    if not path.exists():
        return False
    if not path.is_dir():
        return False
    return os.access(path, os.W_OK)


def detect_context_dir(start: Path | None = None) -> Path:
    """Detect the project context directory.

    Order of preference:
      1. Explicitly supplied start directory.
      2. .agents/context in the current working directory or any ancestor.
      3. The current working directory.

    Raises an error if the selected directory is not writable.
    """
    if start is not None:
        start = Path(start).resolve()
        if start.exists() and not start.is_dir():
            start = start.parent
        if not _is_writable(start):
            print(f"Context directory is not writable: {start}", file=sys.stderr)
            sys.exit(1)
        return start

    cwd = Path.cwd().resolve()
    for path in [cwd] + list(cwd.parents):
        candidate = path / ".agents" / "context"
        if candidate.is_dir() and _is_writable(candidate):
            return candidate

    if _is_writable(cwd):
        return cwd

    print(f"No writable context directory found. Tried: {cwd}", file=sys.stderr)
    sys.exit(1)


def handoffs_root(context_dir: Path) -> Path:
    return context_dir / DEFAULT_HANDOFFS_DIR


def key_dir(context_dir: Path, key: str | None) -> Path:
    root = handoffs_root(context_dir)
    if key is None or key.strip() == "":
        return root / "unticketed"
    return root / normalize_key(key)


def existing_handoffs(directory: Path) -> list[Path]:
    """Return sorted list of existing handoff files in a directory."""
    if not directory.exists():
        return []
    files = [
        p
        for p in directory.iterdir()
        if p.is_file() and p.suffix == ".md" and not p.name.startswith(".")
    ]
    # Sort by name, which should correspond to sequence for keyed handoffs
    # and by timestamp for unticketed handoffs.
    return sorted(files)


def parse_sequence(name: str) -> int | None:
    """Parse the sequence number from a keyed handoff filename like handoff-003.md."""
    match = re.match(r"handoff-(\d+)\.md$", name)
    if match:
        return int(match.group(1))
    return None


def cmd_resolve(args: argparse.Namespace) -> None:
    """Resolve the next handoff path, sequence, and previous handoff."""
    context_dir = detect_context_dir(args.context_dir)
    directory = key_dir(context_dir, args.key)

    # Ensure the directory exists for the next write.
    directory.mkdir(parents=True, exist_ok=True)

    handoffs = existing_handoffs(directory)
    previous_handoff = None
    sequence = 1

    if handoffs:
        previous = handoffs[-1]
        previous_handoff = previous.name
        seq = parse_sequence(previous.name)
        if seq is not None:
            sequence = seq + 1
        else:
            # For unticketed timestamped files, count and append.
            sequence = len(handoffs) + 1

    if args.key:
        output_name = f"handoff-{sequence:03d}.md"
    else:
        # Unticketed handoffs use a timestamped name.
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        output_name = f"{ts}-handoff.md"

    output_path = directory / output_name

    if output_path.exists():
        print(f"Resolved handoff path already exists: {output_path}", file=sys.stderr)
        sys.exit(1)

    result = {
        "context_dir": str(context_dir.resolve()),
        "handoffs_dir": str(handoffs_root(context_dir)),
        "key_directory": str(directory),
        "output_name": output_name,
        "output_path": str(output_path),
        "sequence": sequence,
        "previous_handoff": previous_handoff,
        "existing_handoffs": [str(h.name) for h in handoffs],
    }
    json.dump(result, sys.stdout, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic helper for the handoff skill.",
    )
    parser.add_argument(
        "--context-dir",
        type=str,
        default=None,
        help="Project context directory. If omitted, .agents/context is detected.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve", help="Resolve next handoff path.")
    resolve_parser.add_argument(
        "--key",
        type=str,
        default=None,
        help="Ticket key or session alias. Omit for unticketed handoffs.",
    )
    resolve_parser.set_defaults(func=cmd_resolve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
