#!/usr/bin/env python3
"""
handoff-helper.py

Deterministic helper for the handoff skill.

This helper does not delete or overwrite existing handoff files. When a new
handoff is written for a key that already has one, the existing file is moved
to an archive name before the new file is created.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HANDOFFS_DIR = "handoff"
DEFAULT_CONFIG_FILENAME = "handoff.yaml"


def normalize_key(key: str | None) -> str:
    """Normalize a ticket key or session alias for use as a directory name."""
    if key is None:
        return "unticketed"
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


def detect_config_dir(start: Path | None = None) -> Path:
    """Detect the project config directory.

    Order of preference:
      1. Explicitly supplied start directory.
      2. .agents/config in the current working directory or any ancestor.
      3. The parent of the detected context directory.
      4. The current working directory.

    Raises an error if the selected directory is not writable.
    """
    if start is not None:
        start = Path(start).resolve()
        if start.exists() and not start.is_dir():
            start = start.parent
        if not _is_writable(start):
            print(f"Config directory is not writable: {start}", file=sys.stderr)
            sys.exit(1)
        return start

    cwd = Path.cwd().resolve()
    for path in [cwd] + list(cwd.parents):
        candidate = path / ".agents" / "config"
        if candidate.is_dir() and _is_writable(candidate):
            return candidate

    context_dir = detect_context_dir()
    candidate = context_dir.parent / "config"
    if candidate.is_dir() and _is_writable(candidate):
        return candidate

    if _is_writable(cwd):
        return cwd

    print(f"No writable config directory found. Tried: {cwd}", file=sys.stderr)
    sys.exit(1)


def load_yaml_file(path: Path) -> dict:
    """Load a YAML file, returning an empty dict if it cannot be read."""
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def load_config(config_dir: Path | None = None) -> dict:
    """Load shared and skill-specific configuration.

    Shared keys live in .agents/config/shared.yaml.
    Skill-specific keys live in .agents/config/handoff.yaml.
    """
    cfg_dir = detect_config_dir(config_dir) if config_dir is None else Path(config_dir).resolve()
    shared = load_yaml_file(cfg_dir / "shared.yaml")
    skill = load_yaml_file(cfg_dir / DEFAULT_CONFIG_FILENAME)

    merged = {
        "agents": {
            "context_dir": shared.get("agents", {}).get("context_dir", ".agents/context"),
            "config_dir": str(cfg_dir),
        },
        "handoff": {
            "default_level": "standard",
            "archive_old": True,
            "include_chain": True,
        },
    }
    if "handoff" in skill and isinstance(skill["handoff"], dict):
        for key in merged["handoff"]:
            if key in skill["handoff"]:
                merged["handoff"][key] = skill["handoff"][key]

    return merged


def handoff_path(context_dir: Path, key: str | None) -> Path:
    """Return the canonical handoff file path for a key."""
    return context_dir / DEFAULT_HANDOFFS_DIR / f"{normalize_key(key)}.md"


def existing_handoff(path: Path) -> Path | None:
    """Return the path if it exists and is a file, otherwise None."""
    return path if path.exists() and path.is_file() else None


def archive_existing_handoff(path: Path) -> Path | None:
    """Archive an existing handoff file and return the archive path."""
    if not path.exists():
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    archive_path = path.parent / f"{path.stem}-{ts}-archive{path.suffix}"
    path.rename(archive_path)
    return archive_path


def cmd_initialize(args: argparse.Namespace) -> None:
    """Initialize the handoff configuration file."""
    config_dir = detect_config_dir(args.config_dir)
    config_path = config_dir / DEFAULT_CONFIG_FILENAME

    if config_path.exists() and not args.migrate:
        existing = load_yaml_file(config_path)
        json.dump({
            "status": "already_initialized",
            "config_path": str(config_path),
            "config": existing,
        }, sys.stdout, indent=2)
        return

    proposed_config = {
        "handoff": {
            "default_level": args.default_level or "standard",
            "archive_old": args.archive_old if args.archive_old is not None else True,
            "include_chain": args.include_chain if args.include_chain is not None else True,
        },
        "notes": [
            {
                "text": "Default handoff level is standard.",
                "category": "decision",
            },
            {
                "text": "Old handoff files are archived, not overwritten.",
                "category": "decision",
            },
        ],
    }

    if not args.approve:
        json.dump({
            "status": "needs_approval",
            "config_path": str(config_path),
            "proposed_config": proposed_config,
        }, sys.stdout, indent=2)
        return

    config_dir.mkdir(parents=True, exist_ok=True)
    try:
        import yaml
        config_path.write_text(
            yaml.safe_dump(proposed_config, sort_keys=False),
            encoding="utf-8",
        )
    except ImportError:
        # Fallback to JSON if PyYAML is not available; this is degraded but still functional.
        config_path.write_text(json.dumps(proposed_config, indent=2), encoding="utf-8")

    json.dump({
        "status": "written",
        "config_path": str(config_path),
        "config": proposed_config,
    }, sys.stdout, indent=2)


def cmd_resolve(args: argparse.Namespace) -> None:
    """Resolve the next handoff path and archive any existing file."""
    config = load_config(args.config_dir)
    context_dir = detect_context_dir(args.context_dir)
    output_path = handoff_path(context_dir, args.key)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    previous = existing_handoff(output_path)
    archived = None
    if previous and config.get("handoff", {}).get("archive_old", True):
        archived = archive_existing_handoff(output_path)

    result = {
        "context_dir": str(context_dir.resolve()),
        "config_dir": config.get("agents", {}).get("config_dir", str(detect_config_dir())),
        "config": config.get("handoff", {}),
        "output_path": str(output_path),
        "key": normalize_key(args.key),
        "previous_handoff": previous.name if previous else None,
        "archived_handoff": archived.name if archived else None,
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
    parser.add_argument(
        "--config-dir",
        type=str,
        default=None,
        help="Project config directory. If omitted, .agents/config is detected.",
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

    init_parser = subparsers.add_parser("initialize", help="Initialize handoff configuration.")
    init_parser.add_argument(
        "--default-level",
        type=str,
        default=None,
        choices=["quick", "standard", "thorough"],
        help="Default handoff level.",
    )
    init_parser.add_argument(
        "--archive-old",
        type=lambda x: x.lower() in ("true", "1", "yes"),
        default=None,
        help="Whether to archive existing handoff files.",
    )
    init_parser.add_argument(
        "--include-chain",
        type=lambda x: x.lower() in ("true", "1", "yes"),
        default=None,
        help="Whether to include chain links to previous handoffs.",
    )
    init_parser.add_argument(
        "--approve",
        action="store_true",
        help="Write the file after the user has explicitly approved.",
    )
    init_parser.add_argument(
        "--migrate",
        action="store_true",
        help="Overwrite an existing config file (used for schema migration).",
    )
    init_parser.set_defaults(func=cmd_initialize)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
