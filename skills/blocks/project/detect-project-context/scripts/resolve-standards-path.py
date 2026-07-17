#!/usr/bin/env python3
"""
resolve-standards-path.py

Resolve the canonical skill-standards path for the current project.

Resolution order:
  1. CLI --standards-path argument.
  2. write-a-skill.yaml standards_path in the detected config directory.
  3. {project-marker}/docs/skill-standards/ (e.g., .agents/docs/skill-standards).
  4. {project-root}/docs/skill-standards/.
  5. {project-root}/.agents/docs/skill-standards/.
  6. {project-root}/.pi/docs/skill-standards/.
  7. Bundle default relative to this script (if running inside the skills bundle).

If no path is found, the script returns a degraded status and suggests fetching
from the canonical registry or using the embedded fallback.

Exit codes:
  0 — standards path found.
  1 — no standards path found (degraded).
  2 — invalid input (bad start path).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


SCRIPT_DIR = Path(__file__).resolve().parent
DETECT_SCRIPT = SCRIPT_DIR / "detect-project-context.py"


def _detect_project_context(start: Path) -> dict:
    """Run detect-project-context and return its JSON output."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("detect_project_context", DETECT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.detect(start)


def _load_config_standards_path(config_dir: Path) -> tuple[Optional[str], Optional[str]]:
    """Load standards_path from write-a-skill.yaml if it exists.

    Returns (value, note). The yaml import is lazy: without PyYAML the config
    layer is skipped with a disclosure note rather than an ImportError.
    """
    config_path = config_dir / "write-a-skill.yaml"
    if not config_path.is_file():
        return None, None
    try:
        import yaml
    except ImportError:
        return None, "PyYAML not installed; skipped the config layer for standards_path."
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None, None
    value = data.get("standards_path")
    if value:
        return str(value), None
    return None, None


def _bundle_default() -> Optional[Path]:
    """If this script ships inside the skills bundle, return the bundled standards path.

    Walks up from the script looking for docs/skill-standards; the first valid
    match wins, so the lookup survives any bundle layout depth.
    """
    for path in [SCRIPT_DIR] + list(SCRIPT_DIR.parents):
        candidate = path / "docs" / "skill-standards"
        if _is_valid_standards_path(candidate):
            return candidate
    return None


def _is_valid_standards_path(path: Path) -> bool:
    """A valid standards path contains at least a README.md or fundamentals directory."""
    if not path.is_dir():
        return False
    return (path / "README.md").is_file() or (path / "fundamentals").is_dir()


def resolve_standards_path(
    start: Path,
    provided_path: Optional[str] = None,
) -> dict:
    """Resolve the canonical skill-standards path for the project."""
    start = start.resolve()

    # 1. CLI argument
    if provided_path:
        candidate = Path(provided_path).expanduser().resolve()
        if _is_valid_standards_path(candidate):
            return {
                "status": "found",
                "standards_path": str(candidate),
                "source": "cli",
                "degraded": False,
            }
        return {
            "status": "missing",
            "standards_path": str(candidate),
            "source": "cli",
            "degraded": True,
            "reason": "The provided standards_path does not exist or is missing expected files.",
            "fallback_options": ["fetch", "embedded", "abort"],
        }

    # Detect project context
    context = _detect_project_context(start)
    project_root = context.get("project_root")
    marker = context.get("marker")
    config_dir = context.get("recommended_config_dir")

    if not project_root:
        # No project context; try bundle default only.
        bundle = _bundle_default()
        if bundle:
            return {
                "status": "found",
                "standards_path": str(bundle),
                "source": "bundle",
                "degraded": False,
            }
        return {
            "status": "missing",
            "standards_path": None,
            "source": "none",
            "degraded": True,
            "reason": "No project context detected and no bundled standards found.",
            "fallback_options": ["fetch", "embedded", "abort"],
        }

    project_root = Path(project_root)
    candidates = []
    notes = []

    # 2. Config file
    if config_dir:
        config_value, note = _load_config_standards_path(Path(config_dir))
        if note:
            notes.append(note)
        if config_value:
            candidates.append(("config", Path(config_value).expanduser().resolve()))

    # 3. Marker-based standards
    if marker:
        candidates.append(("marker", project_root / marker / "docs" / "skill-standards"))

    # 4-6. Project-root defaults
    candidates.extend([
        ("project-root", project_root / "docs" / "skill-standards"),
        ("project-root-agents", project_root / ".agents" / "docs" / "skill-standards"),
        ("project-root-pi", project_root / ".pi" / "docs" / "skill-standards"),
    ])

    for source, candidate in candidates:
        if _is_valid_standards_path(candidate):
            result = {
                "status": "found",
                "standards_path": str(candidate),
                "source": source,
                "degraded": False,
            }
            if notes:
                result["note"] = "; ".join(notes)
            return result

    # 7. Bundle default
    bundle = _bundle_default()
    if bundle:
        result = {
            "status": "found",
            "standards_path": str(bundle),
            "source": "bundle",
            "degraded": False,
        }
        if notes:
            result["note"] = "; ".join(notes)
        return result

    return {
        "status": "missing",
        "standards_path": None,
        "source": "none",
        "degraded": True,
        "reason": "No skill-standards directory found in the project or bundle.",
        "fallback_options": ["fetch", "embedded", "abort"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Resolve the canonical skill-standards path for the project."
    )
    parser.add_argument(
        "--start",
        default=".",
        help="Directory to start searching from. Default: current directory.",
    )
    parser.add_argument(
        "--standards-path",
        default="",
        help="Override the standards path instead of detecting it.",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    start_path = Path(args.start)
    if not start_path.exists():
        error = {
            "status": "error",
            "errors": [f"start path does not exist: {args.start}"],
        }
        if args.json:
            print(json.dumps(error))
        else:
            print(f"ERROR: start path does not exist: {args.start}", file=sys.stderr)
        sys.exit(2)

    result = resolve_standards_path(start_path, args.standards_path or None)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"status: {result['status']}")
        print(f"standards_path: {result.get('standards_path')}")
        print(f"source: {result.get('source')}")
        if result.get("note"):
            print(f"note: {result['note']}")
        if result.get("degraded"):
            print(f"degraded: true")
            print(f"reason: {result.get('reason')}")
            print(f"fallback_options: {', '.join(result.get('fallback_options', []))}")
        else:
            print(f"degraded: false")

    sys.exit(0 if result["status"] == "found" else 1)


if __name__ == "__main__":
    sys.exit(main())
