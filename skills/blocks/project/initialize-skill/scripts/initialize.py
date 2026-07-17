#!/usr/bin/env python3
"""initialize-skill

Generic first-run config initializer for any skill.

Reads the skill-level config.yaml for defaults, merges them with the project's
shared.yaml and existing {skill}.yaml, and proposes the result. Writes only the
skill layer, and only when --approve carries the hash of the approved proposal.

Usage:
  python initialize.py --marker-dir <path> --skill-name <name> \
    [--skill-dir <path> | --defaults <json>] \
    [--schema-version <version>] [--approve <hash>] [--json]

Data fields may also arrive as a JSON object on stdin (CLI flags win):
  {"marker_dir": "...", "skill_name": "...", "skill_dir": "...",
   "defaults": {...}, "schema_version": "..."}

Control fields are CLI-only. Passing "approve" via stdin is an error.

Layers: defaults < shared < skill. The proposal reports the effective view
(all layers) and the write_set (skill layer only). Only write_set is persisted;
shared keys are read-only inputs and are never written to {skill}.yaml.

Exit codes:
  0 — proposal returned (needs_approval/unchanged) or config written.
  1 — runtime failure (missing marker dir, unreadable files, stale hash).
  2 — invalid input (missing fields, malformed JSON, bad key prefix).

Output: JSON report to stdout.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fail(message: str, code: int) -> int:
    """Print a minimal JSON error report and return the exit code."""
    print(json.dumps({"status": "error", "errors": [message]}, indent=2))
    return code


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


def _type_check(base: dict, override: dict, path: str = "") -> list[str]:
    """Advisory type mismatches between defaults and a merged config."""
    warnings: list[str] = []
    for key, value in override.items():
        current_path = f"{path}.{key}" if path else key
        if key not in base:
            continue
        expected = base[key]
        # Check bool before int because isinstance(True, int) is True in Python.
        if isinstance(expected, bool) and not isinstance(value, bool):
            warnings.append(f"{current_path} must be a boolean")
        elif isinstance(expected, int) and not isinstance(value, int):
            warnings.append(f"{current_path} must be an integer")
        elif isinstance(expected, str) and not isinstance(value, str):
            warnings.append(f"{current_path} must be a string")
        elif isinstance(expected, list) and not isinstance(value, list):
            warnings.append(f"{current_path} must be a list")
        elif isinstance(expected, dict) and isinstance(value, dict):
            warnings.extend(_type_check(expected, value, current_path))
        elif isinstance(expected, dict):
            warnings.append(f"{current_path} must be a mapping")
    return warnings


def _extract_skill_config(config: dict, skill_name: str) -> tuple[dict, list[str], list[str]]:
    """Extract skill-layer defaults and required keys from a config.yaml.

    Dotted keys must carry the skill-name prefix ('my-skill.tools.pr.provider'),
    which is stripped; flat keys ('timeout') are used as-is. Anything else is a
    declaration error, reported rather than silently rewritten.
    """
    defaults: dict = {}
    required: list[str] = []
    errors: list[str] = []
    for item in config.get("skill", []):
        key = item.get("key")
        if not key:
            continue
        if "." in key:
            first, short_key = key.split(".", 1)
            if first != skill_name:
                errors.append(
                    f"key '{key}' must be flat or start with the skill name "
                    f"prefix '{skill_name}.'"
                )
                continue
        else:
            short_key = key
        if item.get("required"):
            required.append(short_key)
        if "default" not in item:
            continue
        parts = short_key.split(".")
        current = defaults
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = item["default"]
    return defaults, required, errors


def _load_defaults(
    skill_dir: Path | None,
    defaults_json: str | None,
    defaults_dict: dict | None,
    skill_name: str,
) -> tuple[dict, list[str], str | None, int]:
    """Load defaults from --defaults JSON or {skill_dir}/config.yaml.

    Returns (defaults, required_keys, error, exit_code).
    """
    if defaults_dict is not None:
        return defaults_dict, [], None, 0
    if defaults_json is not None:
        try:
            return json.loads(defaults_json), [], None, 0
        except json.JSONDecodeError as exc:
            return {}, [], f"invalid --defaults JSON: {exc}", 2

    if skill_dir is not None:
        config, err = _load_yaml(Path(skill_dir) / "config.yaml")
        if err:
            return {}, [], f"failed to load skill config.yaml: {err}", 1
        if config is not None:
            defaults, required, key_errors = _extract_skill_config(config, skill_name)
            if key_errors:
                return {}, [], "; ".join(key_errors), 2
            return defaults, required, None, 0

    return {}, [], None, 0


def _proposal_hash(write_set: dict) -> str:
    """Fingerprint of what would be persisted. Covers write_set only."""
    canonical = json.dumps(write_set, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _changes(write_set: dict, existing: dict | None, shared: dict | None, migrated_from: str | None) -> dict:
    """Summarize what writing would do, for the approval prompt."""
    flat_write = _flatten(write_set)
    flat_existing = _flatten(existing or {})
    added = sorted(p for p in flat_write if p not in flat_existing)
    updated = sorted(
        p for p in flat_write
        if p in flat_existing and flat_write[p] != flat_existing[p]
    )
    return {
        "added": added,
        "preserved": [],  # filled by caller, needs defaults
        "updated": updated,
        "migrated_from": migrated_from,
        "shadowed_shared": sorted(set(_flatten(existing or {})) & set(_flatten(shared or {}))),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a skill's project-level configuration.",
    )
    parser.add_argument("--marker-dir", help="Project marker directory (e.g. .agents).")
    parser.add_argument("--skill-name", help="Name of the skill to initialize.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--skill-dir", help="Directory containing the skill's config.yaml.")
    group.add_argument("--defaults", help="JSON object with default config values.")
    parser.add_argument("--schema-version", help="Expected config schema version.")
    parser.add_argument(
        "--approve",
        metavar="HASH",
        help="Write the config. HASH must be the proposal_hash the user approved.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    args = parser.parse_args()

    # Data fields may arrive on stdin; control fields are CLI-only.
    stdin_data: dict = {}
    if not sys.stdin.isatty():
        raw = sys.stdin.read()
        if raw.strip():
            try:
                stdin_data = json.loads(raw)
            except json.JSONDecodeError as exc:
                return _fail(f"invalid JSON on stdin: {exc}", 2)
    if stdin_data.get("approve"):
        return _fail("approve must be passed as --approve HASH, not via stdin", 2)

    marker_dir_raw = args.marker_dir or stdin_data.get("marker_dir")
    skill_name = args.skill_name or stdin_data.get("skill_name")
    skill_dir = args.skill_dir or stdin_data.get("skill_dir")
    defaults_raw = args.defaults if args.defaults is not None else stdin_data.get("defaults")
    defaults_json = defaults_raw if isinstance(defaults_raw, str) else None
    defaults_dict = defaults_raw if isinstance(defaults_raw, dict) else None
    schema_version = args.schema_version or stdin_data.get("schema_version")
    approve_hash = args.approve

    if not marker_dir_raw or not skill_name:
        return _fail("marker_dir and skill_name are required", 2)
    if skill_dir is None and defaults_json is None and defaults_dict is None:
        return _fail("either --skill-dir or --defaults must be provided", 2)

    marker_dir = Path(marker_dir_raw).resolve()
    if not marker_dir.is_dir():
        return _fail(
            f"marker directory does not exist: {marker_dir}. "
            "Resolve it via detect-project-context first.",
            1,
        )

    defaults, required_keys, err, code = _load_defaults(
        Path(skill_dir) if skill_dir else None,
        defaults_json,
        defaults_dict,
        skill_name,
    )
    if err:
        return _fail(err, code)

    config_dir = marker_dir / "config"
    skill_config_path = config_dir / f"{skill_name}.yaml"
    shared_config_path = config_dir / "shared.yaml"

    existing_config: dict | None = None
    existing = False
    if skill_config_path.exists():
        existing = True
        existing_config, err = _load_yaml(skill_config_path)
        if err:
            return _fail(f"failed to load existing config: {err}", 1)

    shared_config: dict | None = None
    if shared_config_path.exists():
        shared_config, err = _load_yaml(shared_config_path)
        if err:
            return _fail(f"failed to load shared config: {err}", 1)

    # Layers: defaults < shared < skill. Only the skill layer is ever written.
    write_set = _deep_merge(defaults, existing_config or {})
    effective = _deep_merge(_deep_merge(defaults, shared_config or {}), existing_config or {})

    migrated_from = None
    if schema_version is not None:
        existing_version = (existing_config or {}).get("schema_version")
        if existing_version != schema_version:
            migrated_from = existing_version
        write_set["schema_version"] = schema_version
        effective["schema_version"] = schema_version

    changes = _changes(write_set, existing_config, shared_config, migrated_from)
    flat_defaults = _flatten(defaults)
    flat_existing = _flatten(existing_config or {})
    changes["preserved"] = sorted(
        p for p in flat_existing
        if p in flat_defaults and flat_existing[p] != flat_defaults[p]
    )

    flat_effective = _flatten(effective)
    missing_required = [k for k in required_keys if k not in flat_effective]
    warnings = _type_check(defaults, effective)

    proposal_hash = _proposal_hash(write_set)
    nothing_to_write = existing and not changes["added"] and not changes["updated"]

    report = {
        "status": "needs_approval",
        "proposal_hash": proposal_hash,
        "marker_dir": str(marker_dir),
        "config_path": str(skill_config_path),
        "existing": existing,
        "schema_version": schema_version,
        "changes": changes,
        "missing_required": missing_required,
        "warnings": warnings,
        "proposed": effective,
        "write_set": write_set,
        "errors": [],
    }

    # --- Approve path: write exactly what was approved. ---
    if approve_hash is not None:
        if approve_hash != proposal_hash:
            return _fail(
                "proposal changed since approval; re-run for a fresh proposal_hash",
                1,
            )
        if nothing_to_write:
            report["status"] = "unchanged"
            print(json.dumps(report, indent=2))
            return 0
        config_dir.mkdir(parents=True, exist_ok=True)
        if existing:
            backup_path = skill_config_path.with_suffix(
                f".yaml.backup.{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
            )
            shutil.copy2(skill_config_path, backup_path)
            report["backup_path"] = str(backup_path)
        skill_config_path.write_text(
            yaml.dump(write_set, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        report["status"] = "written"
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Configuration written to {skill_config_path}")
        return 0

    # --- Proposal path: never writes. ---
    if nothing_to_write:
        report["status"] = "unchanged"

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Proposed {skill_name} configuration:")
        for label, paths in (
            ("added", changes["added"]),
            ("preserved", changes["preserved"]),
            ("updated", changes["updated"]),
            ("shadowed", changes["shadowed_shared"]),
        ):
            if paths:
                print(f"  {label}: {', '.join(paths)}")
        if changes["migrated_from"]:
            print(f"  migrated from schema_version: {changes['migrated_from']}")
        if missing_required:
            print(f"  missing required: {', '.join(missing_required)}")
        print("-" * 40)
        print(yaml.dump(effective, default_flow_style=False, sort_keys=False))
        print("-" * 40)
        if report["status"] == "unchanged":
            print("Already initialized; nothing to write.")
        else:
            print(f"Would write to: {skill_config_path}")
            print(f"Run with --approve {proposal_hash} after explicit user confirmation.")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
