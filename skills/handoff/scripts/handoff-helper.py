#!/usr/bin/env python3
"""
handoff-helper.py

Deterministic helper for the handoff skill.

Subcommands:
    discover    List candidate artifacts from the context directory.
    resolve     Determine the next handoff path, sequence, and previous handoff.
    prune       Remove older unticketed handoffs beyond a limit.

All output is JSON. Errors are written to stderr and the exit code is non-zero.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HANDOFFS_DIR = "handoffs"
DEFAULT_UNTICKETED_LIMIT = 10


def normalize_key(key: str) -> str:
    """Normalize a ticket key or session alias for use as a directory name."""
    key = key.lower().strip()
    key = re.sub(r"[^a-z0-9]+", "-", key)
    key = key.strip("-")
    return key or "untitled"


def detect_context_dir(start: Path | None = None) -> Path:
    """Detect the project context directory.

    Order of preference:
      1. Explicitly supplied start directory.
      2. .agents/context in the current working directory or any ancestor.
      3. The current working directory.
    """
    if start is not None:
        start = Path(start).resolve()
        if start.exists() and not start.is_dir():
            start = start.parent
        return start

    cwd = Path.cwd().resolve()
    for path in [cwd] + list(cwd.parents):
        candidate = path / ".agents" / "context"
        if candidate.is_dir():
            return candidate

    return cwd


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


def cmd_discover(args: argparse.Namespace) -> None:
    """Discover candidate artifacts in the context directory."""
    context_dir = detect_context_dir(args.context_dir)
    if not context_dir.exists():
        print(f"Context directory does not exist: {context_dir}", file=sys.stderr)
        sys.exit(1)

    artifacts = []
    # Scan the context directory and one level of subdirectories for .md files.
    search_roots = [context_dir] + [d for d in context_dir.iterdir() if d.is_dir()]
    seen = set()

    for root in search_roots:
        for path in root.rglob("*.md"):
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)

            rel = resolved.relative_to(context_dir.resolve())
            stat = path.stat()
            modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

            artifacts.append(
                {
                    "path": str(rel),
                    "absolute_path": str(resolved),
                    "type": "markdown",
                    "summary": "",  # Filled by the agent; the script is not inferential.
                    "modified_at": modified_at,
                }
            )

    # Sort by recency, most recent first.
    artifacts.sort(key=lambda x: x["modified_at"], reverse=True)
    json.dump(artifacts, sys.stdout, indent=2)


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


def cmd_prune(args: argparse.Namespace) -> None:
    """Remove older unticketed handoffs beyond the configured limit."""
    context_dir = detect_context_dir(args.context_dir)
    directory = key_dir(context_dir, None)

    if not directory.exists():
        json.dump({"removed": [], "kept": [], "limit": args.limit}, sys.stdout, indent=2)
        return

    handoffs = existing_handoffs(directory)
    if len(handoffs) <= args.limit:
        json.dump(
            {
                "removed": [],
                "kept": [str(h.name) for h in handoffs],
                "limit": args.limit,
            },
            sys.stdout,
            indent=2,
        )
        return

    kept = handoffs[-args.limit:]
    removed = handoffs[:-args.limit]
    removed_names = []
    for path in removed:
        try:
            path.unlink()
            removed_names.append(str(path.name))
        except OSError as e:
            print(f"Failed to remove {path}: {e}", file=sys.stderr)

    json.dump(
        {
            "removed": removed_names,
            "kept": [str(h.name) for h in kept],
            "limit": args.limit,
        },
        sys.stdout,
        indent=2,
    )


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

    discover_parser = subparsers.add_parser("discover", help="List candidate artifacts.")
    discover_parser.set_defaults(func=cmd_discover)

    resolve_parser = subparsers.add_parser("resolve", help="Resolve next handoff path.")
    resolve_parser.add_argument(
        "--key",
        type=str,
        default=None,
        help="Ticket key or session alias. Omit for unticketed handoffs.",
    )
    resolve_parser.set_defaults(func=cmd_resolve)

    prune_parser = subparsers.add_parser("prune", help="Remove older unticketed handoffs.")
    prune_parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_UNTICKETED_LIMIT,
        help=f"Maximum number of unticketed handoffs to keep (default: {DEFAULT_UNTICKETED_LIMIT}).",
    )
    prune_parser.set_defaults(func=cmd_prune)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
