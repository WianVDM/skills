#!/usr/bin/env python3
"""initialize-skill

Generic first-run config initializer for any skill.

Reads the skill-level config.yaml for defaults, then ensures the project-level
{marker_dir}/config/{skill_name}.yaml exists with those defaults merged over any
existing user edits.

The script prints the proposed configuration and refuses to write unless
--approve is passed. The caller must obtain explicit user approval before
invoking this script with --approve.

Usage:
  python initialize.py --marker-dir <path> --skill-name <name> \
    [--skill-dir <path> | --defaults <json>] \
    [--schema-version <version>] [--approve] [--json]

Input JSON via stdin (alternative to CLI flags):
  {
    "marker_dir": "...",
    "skill_name": "...",
    "skill_dir": "...",        // optional
    "defaults": {...},         // optional; used if skill_dir is omitted
    "schema_version": "...",   // optional
    "approve": false           // optional
  }

Output:
  JSON report to stdout.
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

import yaml


def _load_yaml(path: Path) -> tuple[dict | None, str | None]:
    """Load YAML from path. Return (data, error)."""
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
    """Extract skill-specific defaults from a skill-level config.yaml.

    Dotted keys are converted into nested dictionaries so that a key like
    'tools.pr.provider' becomes {'tools': {'pr': {'provider': ...}}}.
    A skill-name prefix (e.g. 'pr-report.tools.pr.provider') is stripped first.
    """
    defaults: dict = {}
    for item in config.get("skill", []):
        key = item.get("key")
        if not key:
            continue
        # Strip a skill-name prefix if present (e.g. pr-report.tools.pr.provider).
        short_key = key.split(".", 1)[1] if "." in key else key
        if "default" not in item:
            continue
        value = item["default"]
        # Build nested dict from dotted key.
        parts = short_key.split(".")
        current = defaults
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
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


def _load_defaults(skill_dir: Path | None, defaults_json: str | None, defaults_dict: dict | None = None) -> tuple[dict, list[str]]:
    """Load defaults from skill_dir/config.yaml or from the provided JSON/dict."""
    errors: list[str] = []
    if defaults_dict is not None:
        return defaults_dict, errors
    if defaults_json is not None:
        try:
            return json.loads(defaults_json), errors
        except json.JSONDecodeError as exc:
            errors.append(f"invalid --defaults JSON: {exc}")
            return {}, errors

    if skill_dir is not None:
        skill_config_path = Path(skill_dir) / "config.yaml"
        skill_config, err = _load_yaml(skill_config_path)
        if err:
            errors.append(f"failed to load skill config.yaml: {err}")
            return {}, errors
        if skill_config is not None:
            return _extract_defaults(skill_config), errors

    return {}, errors


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a skill's project-level configuration.",
    )
    parser.add_argument(
        "--marker-dir",
        required=True,
        help="Project marker directory (e.g. .agents or .pi).",
    )
    parser.add_argument(
        "--skill-name",
        required=True,
        help="Name of the skill to initialize.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--skill-dir",
        help="Directory containing the skill's config.yaml. Defaults are extracted from it.",
    )
    group.add_argument(
        "--defaults",
        help="JSON object with default config values.",
    )
    parser.add_argument(
        "--schema-version",
        help="Expected config schema version. Triggers migration if older.",
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

    # If stdin is provided, merge it with CLI args (CLI wins).
    stdin_data: dict = {}
    if not sys.stdin.isatty():
        try:
            stdin_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            pass

    marker_dir = Path(args.marker_dir or stdin_data.get("marker_dir", "")).resolve()
    skill_name = args.skill_name or stdin_data.get("skill_name", "")
    skill_dir = args.skill_dir or stdin_data.get("skill_dir")
    skill_dir_path = Path(skill_dir) if skill_dir else None
    defaults_json = args.defaults or stdin_data.get("defaults")
    defaults_dict = None
    if isinstance(defaults_json, dict):
        defaults_dict = defaults_json
        defaults_json = None
    schema_version = args.schema_version or stdin_data.get("schema_version")
    approve = args.approve or stdin_data.get("approve", False)

    if not skill_dir_path and defaults_json is None and defaults_dict is None:
        errors.append("either --skill-dir or --defaults must be provided")

    config_dir = marker_dir / "config"
    skill_config_path = config_dir / f"{skill_name}.yaml"
    shared_config_path = config_dir / "shared.yaml"

    defaults, defaults_errors = _load_defaults(
        skill_dir_path,
        defaults_json,
        defaults_dict,
    )
    errors: list[str] = []
    errors.extend(defaults_errors)

    # Load existing project config if present.
    existing_config: dict | None = None
    existing = False
    if skill_config_path.exists():
        existing = True
        existing_config, err = _load_yaml(skill_config_path)
        if err:
            errors.append(f"failed to load existing config: {err}")

    # Load shared config if present.
    shared_config: dict | None = None
    if shared_config_path.exists():
        shared_config, err = _load_yaml(shared_config_path)
        if err:
            errors.append(f"failed to load shared config: {err}")

    # Merge: defaults < shared < skill-specific.
    proposed = dict(defaults)
    if shared_config is not None:
        proposed = _deep_merge(proposed, shared_config)
    if existing_config is not None:
        proposed = _deep_merge(proposed, existing_config)

    # Add any missing default keys and migrate schema version if needed.
    changed = False
    if existing:
        for key, value in defaults.items():
            if key not in proposed:
                proposed[key] = value
                changed = True

    if schema_version is not None:
        existing_version = proposed.get("schema_version")
        if existing_version != schema_version:
            changed = True
        proposed["schema_version"] = schema_version
    elif "schema_version" not in proposed and existing:
        # If not provided and not present, leave it absent to avoid forcing a version.
        pass

    report = {
        "status": "needs_approval" if not approve else "written",
        "marker_dir": str(marker_dir),
        "config_path": str(skill_config_path),
        "existing": existing,
        "changed": changed or not existing,
        "schema_version": schema_version,
        "proposed": proposed,
        "errors": errors,
    }

    if errors and not approve:
        # If there are errors and we are not writing, return the report with error status.
        report["status"] = "error" if any(
            not e.startswith("failed to load") for e in errors
        ) else "needs_approval"

    if not approve:
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Proposed {skill_name} configuration:")
            print("-" * 40)
            print(yaml.dump(proposed, default_flow_style=False, sort_keys=False))
            print("-" * 40)
            print(f"Would write to: {skill_config_path}")
            print("Run with --approve to write after explicit user confirmation.")
        return 0 if report["status"] != "error" else 1

    if errors:
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1

    config_dir.mkdir(parents=True, exist_ok=True)

    if existing:
        backup_path = skill_config_path.with_suffix(
            f".yaml.backup.{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        )
        shutil.copy2(skill_config_path, backup_path)
        report["backup_path"] = str(backup_path)

    skill_config_path.write_text(
        yaml.dump(proposed, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    report["status"] = "written"
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Configuration written to {skill_config_path}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
