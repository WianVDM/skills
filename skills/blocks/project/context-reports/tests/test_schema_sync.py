#!/usr/bin/env python3
"""
Schema sync test for context-reports.

references/context-report-schema.json is the embedded fallback mirror of the
canonical schema in the skill-standards wiki. The two must stay identical:
canonical wins when the standards are resolvable, so any drift would silently
split the contract.

Run with:
    python -m pytest skills/blocks/project/context-reports/tests/
    python skills/blocks/project/context-reports/tests/test_schema_sync.py
"""

import json
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
MIRROR = SKILL_DIR / "references" / "context-report-schema.json"


def _canonical_path() -> Path:
    """Walk up from the skill to find the standards wiki schema."""
    for path in [SKILL_DIR] + list(SKILL_DIR.parents):
        candidate = path / "docs" / "skill-standards" / "schemas" / "context-report.schema.json"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("canonical context-report schema not found above the skill")


def test_mirror_matches_canonical():
    canonical = json.loads(_canonical_path().read_text(encoding="utf-8"))
    mirror = json.loads(MIRROR.read_text(encoding="utf-8"))
    assert mirror == canonical, (
        "references/context-report-schema.json has drifted from the canonical "
        "skill-standards schema. Replace it with a fresh copy of "
        "docs/skill-standards/schemas/context-report.schema.json."
    )


def test_envelope_accepts_standards_example():
    """A report written per the standards example must validate against the mirror."""
    jsonschema = pytest_importorskip("jsonschema")
    yaml = pytest_importorskip("yaml")
    schema = json.loads(MIRROR.read_text(encoding="utf-8"))
    # Timestamps are quoted: unquoted ISO values parse as datetime objects in
    # YAML, while the schema expects a string.
    frontmatter = yaml.safe_load(
        "skill: ticket-research\n"
        "version: 1\n"
        "key: OC-1234\n"
        "generated_at: \"2026-06-26T08:42:00Z\"\n"
        "summary: One-sentence synthesis.\n"
        "artifacts:\n"
        "  - .agents/context/state-capture/OC-1234-main.md\n"
    )
    jsonschema.validate(frontmatter, schema)


def test_envelope_does_not_require_version():
    """Version is optional in the canonical envelope."""
    jsonschema = pytest_importorskip("jsonschema")
    schema = json.loads(MIRROR.read_text(encoding="utf-8"))
    jsonschema.validate(
        {"skill": "ticket-research", "key": "OC-1234", "generated_at": "2026-06-26T08:42:00Z"},
        schema,
    )


def pytest_importorskip(name):
    try:
        return __import__(name)
    except ImportError:
        import pytest

        pytest.skip(f"{name} not installed")


def main():
    with tempfile.TemporaryDirectory():
        test_mirror_matches_canonical()
        test_envelope_accepts_standards_example()
        test_envelope_does_not_require_version()
    print("All 3 tests passed.")


if __name__ == "__main__":
    sys.exit(main())
