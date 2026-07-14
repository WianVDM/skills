#!/usr/bin/env python3
"""initialize.py

Initialize the debrief skill configuration.

Reads the skill-level config.yaml for defaults, then ensures the project-level
{marker_dir}/config/debrief.yaml exists with those defaults.

The script prints the proposed configuration and refuses to write unless
--approve is passed. The conductor must obtain explicit user approval before
invoking this script with --approve.

Usage:
  python initialize.py --marker-dir <path> [--approve] [--json]

Output:
  JSON report to stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a normal dependency
    yaml = None


def _load_yaml(path: Path) -> tuple[dict | None, str | None]:
    """Load YAML from path. Return (data, error)."""
    if yaml is None:
        return None, "PyYAML is not installed"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"failed to read {path}: {exc}"
    if not text.strip():
        return {}, None
    try:
        data = yaml.safe_load(text)
        return (data or {}), None
    except Exception as exc:
        return None, f"failed to parse {path}: {exc}"


def _extract_defaults(config: dict) -> dict:
    """Extract skill-specific defaults from the skill-level config.yaml."""
    defaults: dict = {}
    for item in config.get("skill", []):
        key = item.get("key")
        if not key:
            continue
        # Strip a skill-name prefix if present (e.g. debrief.green_threshold).
        short_key = key.split(".", 1)[1] if "." in key else key
        if "default" in item:
            defaults[short_key] = item["default"]
    return defaults


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursing into nested dicts."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize debrief project configuration.",
    )
    parser.add_argument(
        "--marker-dir",
        required=True,
        help="Project marker directory (e.g. .agents or .pi).",
    )
    parser.add_argument(
        "--approve",
        action="store_true",
        help="Write the file after the user has explicitly approved.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable output.",
    )
    args = parser.parse_args()

    marker_dir = Path(args.marker_dir).resolve()
    config_dir = marker_dir / "config"
    debrief_config_path = config_dir / "debrief.yaml"
    skill_config_path = Path(__file__).resolve().parent.parent / "config.yaml"

    # Load skill-level defaults.
    skill_config, err = _load_yaml(skill_config_path)
    if err:
        print(
            json.dumps(
                {"status": "error", "errors": [f"failed to load skill config.yaml: {err}"]},
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    defaults = _extract_defaults(skill_config or {})

    # Load existing project config if present.
    existing_config: dict | None = None
    existing = False
    if debrief_config_path.exists():
        existing = True
        existing_config, err = _load_yaml(debrief_config_path)
        if err:
            print(
                json.dumps(
                    {"status": "error", "errors": [f"failed to load existing config: {err}"]},
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 1

    # Merge existing user values over defaults, preserving user edits.
    proposed = dict(defaults)
    if existing_config is not None:
        proposed = _deep_merge(proposed, existing_config)

    # Add any missing default keys to an existing config (idempotent migration).
    changed = False
    if existing:
        for key, value in defaults.items():
            if key not in proposed:
                proposed[key] = value
                changed = True

    report = {
        "status": "needs_approval" if not args.approve else "written",
        "marker_dir": str(marker_dir),
        "config_path": str(debrief_config_path),
        "existing": existing,
        "changed": changed or not existing,
        "proposed": proposed,
    }

    if not args.approve:
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("Proposed debrief configuration:")
            print("-" * 40)
            print(yaml.dump(proposed, default_flow_style=False, sort_keys=False))
            print("-" * 40)
            print(f"Would write to: {debrief_config_path}")
            print("Run with --approve to write after explicit user confirmation.")
        return 0

    config_dir.mkdir(parents=True, exist_ok=True)
    debrief_config_path.write_text(
        yaml.dump(proposed, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    report["status"] = "written"
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Configuration written to {debrief_config_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
