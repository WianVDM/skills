#!/usr/bin/env python3
"""load-skill-config.py

Load and merge skill configuration from marker directory YAML files.

Reads JSON from stdin:
  {
    "marker_dir": "<path>",
    "skill_name": "<name>",
    "defaults": { ... }   // optional; caller-provided skill-specific defaults
  }

Loads:
  {marker_dir}/config/shared.yaml
  {marker_dir}/config/{skill_name}.yaml

Merges them with the provided defaults (skill-specific overrides shared, shared overrides defaults).
Writes JSON to stdout:
  {"status": "ready"|"missing"|"error", "config": {...}, "shadowed_shared": [...], "errors": []}

shadowed_shared lists config paths present in both shared.yaml and {skill_name}.yaml;
the skill-layer copy shadows the shared value at those paths.

This script is read-only; it does not create or modify files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def _help() -> str:
    return """load-skill-config.py — load and merge skill YAML configuration

Input JSON (stdin):
  {"marker_dir": "<path>", "skill_name": "<name>", "defaults": {...}}

Output JSON (stdout):
  {"status": "ready"|"missing"|"error", "config": {...}, "errors": []}
"""


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursing into nested dicts."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _flatten(config: dict, prefix: str = "") -> dict:
    """Flatten nested dicts to {dot.path: leaf_value}. Lists are leaves."""
    flat: dict = {}
    for key, value in config.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flat.update(_flatten(value, path))
        else:
            flat[path] = value
    return flat


def _load_yaml(path: Path) -> tuple:
    """Return (data, error). data is None if there was an error."""
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


def _type_check(base: dict, override: dict, path: str = "") -> list:
    """Report type mismatches between default and override configs."""
    errors = []
    for key, value in override.items():
        current_path = f"{path}.{key}" if path else key
        if key not in base:
            continue
        expected = base[key]
        # Check bool before int because isinstance(True, int) is True in Python.
        if isinstance(expected, bool) and not isinstance(value, bool):
            errors.append(f"{current_path} must be a boolean")
        elif isinstance(expected, int) and not isinstance(value, int):
            errors.append(f"{current_path} must be an integer")
        elif isinstance(expected, str) and not isinstance(value, str):
            errors.append(f"{current_path} must be a string")
        elif isinstance(expected, list) and not isinstance(value, list):
            errors.append(f"{current_path} must be a list")
        elif isinstance(expected, dict) and isinstance(value, dict):
            errors.extend(_type_check(expected, value, current_path))
        elif isinstance(expected, dict):
            errors.append(f"{current_path} must be a mapping")
    return errors


def _run(data: dict) -> dict:
    marker_dir = data.get("marker_dir")
    skill_name = data.get("skill_name")
    defaults = data.get("defaults") or {}

    if not marker_dir or not skill_name:
        return {
            "status": "error",
            "config": {},
            "shadowed_shared": [],
            "errors": ["marker_dir and skill_name are required"],
        }

    marker_path = Path(marker_dir)
    config = dict(defaults)
    errors = []
    any_loaded = bool(defaults)

    shared_data: dict = {}
    shared_path = marker_path / "config" / "shared.yaml"
    if shared_path.exists():
        loaded, err = _load_yaml(shared_path)
        if err:
            errors.append(err)
        elif loaded is not None:
            shared_data = loaded
            config = _deep_merge(config, shared_data)
            any_loaded = True

    skill_data: dict = {}
    skill_path = marker_path / "config" / f"{skill_name}.yaml"
    if skill_path.exists():
        loaded, err = _load_yaml(skill_path)
        if err:
            errors.append(err)
        elif loaded is not None:
            skill_data = loaded
            config = _deep_merge(config, skill_data)
            any_loaded = True

    shadowed_shared = sorted(set(_flatten(skill_data)) & set(_flatten(shared_data)))

    # Type check against defaults
    type_errors = _type_check(defaults, config)
    errors.extend(type_errors)

    if errors:
        return {"status": "error", "config": config, "shadowed_shared": shadowed_shared, "errors": errors}

    if not any_loaded:
        return {
            "status": "missing",
            "config": config,
            "shadowed_shared": shadowed_shared,
            "errors": ["no configuration sources found"],
        }

    return {"status": "ready", "config": config, "shadowed_shared": shadowed_shared, "errors": []}


def _main() -> int:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        return 0

    try:
        data = json.load(sys.stdin)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "config": {},
                    "errors": [f"invalid JSON input: {exc}"],
                }
            ),
            file=sys.stderr,
        )
        return 2

    result = _run(data)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    sys.exit(_main())
