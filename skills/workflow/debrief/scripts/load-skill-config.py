#!/usr/bin/env python3
"""Load and merge skill configuration from marker directory YAML files.

Reads JSON from stdin:
  {
    "marker_dir": "<path>",
    "skill_name": "debrief",
    "defaults": { ... }   // optional
  }

Loads:
  {marker_dir}/config/shared.yaml
  {marker_dir}/config/{skill_name}.yaml

Merges them with the provided defaults (skill-specific overrides shared).
Writes JSON to stdout:
  {"status": "ready"|"missing"|"error", "config": {...}, "errors": []}

This script is read-only; it does not create or modify files.
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a normal dependency
    yaml = None


DEBRIEF_DEFAULTS = {
    "confidence_threshold": 85,
    "green_threshold": 85,
    "yellow_threshold": 60,
    "baseline_mode": "optional",
    "issue_tracker": "auto",
    "max_resolution_loops": 2,
    "freshness_hours": 24,
    "explore_code_max_files": 20,
    "max_history_rows": 20,
}


def _help() -> str:
    return """load-skill-config.py — load and merge skill YAML configuration

Input JSON (stdin):
  {"marker_dir": "<path>", "skill_name": "debrief", "defaults": {...}}

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


def _load_yaml(path: Path) -> tuple:
    """Return (data, error). data is None if there was an error."""
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


def _type_check(base: dict, override: dict, path: str = "") -> list:
    """Report type mismatches between default and override configs."""
    errors = []
    for key, value in override.items():
        current_path = f"{path}.{key}" if path else key
        if key not in base:
            continue
        expected = base[key]
        if isinstance(expected, dict):
            if not isinstance(value, dict):
                errors.append(f"{current_path} must be a mapping")
            else:
                errors.extend(_type_check(expected, value, current_path))
        elif isinstance(expected, bool) and not isinstance(value, bool):
            errors.append(f"{current_path} must be a boolean")
        elif isinstance(expected, int) and not isinstance(value, int):
            errors.append(f"{current_path} must be an integer")
        elif isinstance(expected, str) and not isinstance(value, str):
            errors.append(f"{current_path} must be a string")
        elif isinstance(expected, list) and not isinstance(value, list):
            errors.append(f"{current_path} must be a list")
    return errors


def _validate_debrief(config: dict) -> list:
    """Validate debrief-specific schema rules."""
    errors = []
    int_keys = [
        "confidence_threshold",
        "green_threshold",
        "yellow_threshold",
        "max_resolution_loops",
        "freshness_hours",
        "explore_code_max_files",
        "max_history_rows",
    ]

    for key in int_keys:
        if key in config and not isinstance(config[key], int):
            errors.append(f"{key} must be an integer")

    for key in ("confidence_threshold", "green_threshold", "yellow_threshold"):
        if key in config and isinstance(config[key], int):
            if not (0 <= config[key] <= 100):
                errors.append(f"{key} must be between 0 and 100")

    if isinstance(config.get("green_threshold"), int) and isinstance(config.get("yellow_threshold"), int):
        if config["green_threshold"] <= config["yellow_threshold"]:
            errors.append("green_threshold must be greater than yellow_threshold")

    if "baseline_mode" in config and config["baseline_mode"] not in ("optional", "skip", "required"):
        errors.append("baseline_mode must be optional, skip, or required")

    if "issue_tracker" in config and config["issue_tracker"] not in (
        "auto",
        "jira",
        "github",
        "linear",
        "manual",
    ):
        errors.append("issue_tracker must be auto, jira, github, linear, or manual")

    tracker = config.get("issue_tracker")
    if tracker and tracker not in ("auto", "manual"):
        trackers = config.get("trackers")
        if not isinstance(trackers, dict) or tracker not in trackers:
            errors.append(f"trackers.{tracker} block must be present when issue_tracker is {tracker}")

    if isinstance(config.get("trackers"), dict):
        for tracker_name, tracker_cfg in config["trackers"].items():
            if isinstance(tracker_cfg, dict):
                for key, value in tracker_cfg.items():
                    if key.endswith("_env") and not isinstance(value, str):
                        errors.append(f"trackers.{tracker_name}.{key} must be an environment-variable name string")

    return errors


def _run(data: dict) -> dict:
    marker_dir = data.get("marker_dir")
    skill_name = data.get("skill_name")
    defaults = data.get("defaults") or {}

    if not marker_dir or not skill_name:
        return {
            "status": "error",
            "config": {},
            "errors": ["marker_dir and skill_name are required"],
        }

    if skill_name == "debrief" and not defaults:
        defaults = DEBRIEF_DEFAULTS

    marker_path = Path(marker_dir)
    config = dict(defaults)
    errors = []
    any_loaded = bool(defaults)

    shared_path = marker_path / "config" / "shared.yaml"
    if shared_path.exists():
        shared_data, err = _load_yaml(shared_path)
        if err:
            errors.append(err)
        elif shared_data is not None:
            config = _deep_merge(config, shared_data)
            any_loaded = True

    skill_path = marker_path / "config" / f"{skill_name}.yaml"
    if skill_path.exists():
        skill_data, err = _load_yaml(skill_path)
        if err:
            errors.append(err)
        elif skill_data is not None:
            config = _deep_merge(config, skill_data)
            any_loaded = True

    # Type check against defaults
    type_errors = _type_check(defaults, config)
    errors.extend(type_errors)

    if skill_name == "debrief":
        errors.extend(_validate_debrief(config))

    if errors:
        return {"status": "error", "config": config, "errors": errors}

    if not any_loaded:
        return {
            "status": "missing",
            "config": config,
            "errors": ["no configuration sources found"],
        }

    return {"status": "ready", "config": config, "errors": []}


if __name__ == "__main__":
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        print(_help())
        sys.exit(0)

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
        sys.exit(2)

    result = _run(data)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "ready" else 1)
