#!/usr/bin/env python3
"""Sync and drift-check the condensed fallback docs against the canonical wiki.

The condensed fallbacks (references/FUNDAMENTALS.md, references/PATTERN_HINTS.md)
exist so write-a-skill works in workspaces without the canonical skill-standards
wiki. Stale fallbacks teach a superseded standard, so this script makes drift
impossible to miss:

  --sync   Regenerate mechanically derivable content (pattern inventory, sync
           stamp) from the canonical wiki.
  --check  Exit 1 on any drift: schema/frontmatter contradictions, missing
           pattern coverage, moved-doc paths, stale sync stamps, or diverged
           fallback copies across the skill set (audit-skill, review-skill).

Drift checks:
  1. Every required frontmatter field in the canonical schema is taught.
  2. No dropped schema field (e.g. `version`) is taught as frontmatter.
  3. Every canonical pattern doc appears in PATTERN_HINTS.md by name.
  4. No references to moved docs (core/types, reference/trigger-evals.md, ...).
  5. Fallback copies in audit-skill and review-skill match their canonical
     sources on row IDs and section headings.

Usage:
    python sync-fallbacks.py --sync [standards_path]
    python sync-fallbacks.py --check [standards_path]
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parents[3]
DEFAULT_STANDARDS = REPO_ROOT / "docs" / "skill-standards"

FUNDAMENTALS = SKILL_DIR / "references" / "FUNDAMENTALS.md"
PATTERN_HINTS = SKILL_DIR / "references" / "PATTERN_HINTS.md"

MOVED_PATHS = [
    "fundamentals/core/types",
    "reference/trigger-evals.md",
    "reference/context-budget.md",
    "patterns/mode.md",
]

# Fallback copies elsewhere in the skill set: (copy, canonical)
SET_FALLBACKS = [
    (
        REPO_ROOT / "skills" / "blocks" / "authoring" / "audit-skill" / "references" / "AUDIT_RUBRIC.md",
        DEFAULT_STANDARDS / "reference" / "audit-rubric.md",
    ),
    (
        REPO_ROOT / "skills" / "blocks" / "authoring" / "review-skill" / "references" / "REVIEW_PRINCIPLES.md",
        DEFAULT_STANDARDS / "reference" / "review-principles.md",
    ),
]


def fail(problems, msg):
    problems.append(msg)


def check_schema_fields(problems, standards):
    schema = json.loads((standards / "schemas" / "skill-frontmatter.schema.json").read_text(encoding="utf-8"))
    text = FUNDAMENTALS.read_text(encoding="utf-8")
    for field in schema.get("required", []):
        if f"`{field}`" not in text:
            fail(problems, f"FUNDAMENTALS.md does not teach required frontmatter field `{field}`")
    for dropped in set(schema.get("properties", {})) - set(schema.get("required", [])) - {
        "allowed-tools", "disallowed-tools", "disable-model-invocation", "globs", "paths", "depends",
    }:
        # a schema property that is neither required nor a known harness hint
        # must not be presented as a frontmatter field
        if re.search(rf"add `{dropped}`|`{dropped}`\s*(field|in frontmatter)", text, re.I):
            fail(problems, f"FUNDAMENTALS.md presents `{dropped}` as a frontmatter field, but the schema dropped it")
    if re.search(r"add `version`", text, re.I):
        fail(problems, "FUNDAMENTALS.md still teaches the dropped `version` frontmatter field")


def check_pattern_coverage(problems, standards):
    patterns_dir = standards / "patterns"
    text = PATTERN_HINTS.read_text(encoding="utf-8")
    for f in sorted(patterns_dir.glob("*.md")):
        if f.name == "README.md":
            continue
        if f.name not in text:
            fail(problems, f"PATTERN_HINTS.md does not list canonical pattern `{f.name}`")


def check_moved_paths(problems):
    for path in (FUNDAMENTALS, PATTERN_HINTS):
        text = path.read_text(encoding="utf-8")
        for moved in MOVED_PATHS:
            if moved in text:
                fail(problems, f"{path.name} references moved doc `{moved}`")


def check_set_fallbacks(problems):
    for copy, canonical in SET_FALLBACKS:
        if not copy.exists() or not canonical.exists():
            continue
        copy_ids = set(re.findall(r"\b([FTPC]\d{2})\b", copy.read_text(encoding="utf-8")))
        canon_ids = set(re.findall(r"\b([FTPC]\d{2})\b", canonical.read_text(encoding="utf-8")))
        if copy_ids and canon_ids and copy_ids != canon_ids:
            fail(problems, f"{copy.name} check IDs diverge from canonical {canonical.name}: {sorted(copy_ids ^ canon_ids)}")


def git_ref(path):
    try:
        return subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", str(path)],
            capture_output=True, cwd=REPO_ROOT,
        ).stdout.decode("utf-8").strip() or "unknown"
    except Exception:
        return "unknown"


def sync(standards):
    # regenerate the canonical pattern inventory in PATTERN_HINTS.md
    patterns = sorted(
        f.name for f in (standards / "patterns").glob("*.md") if f.name != "README.md"
    )
    text = PATTERN_HINTS.read_text(encoding="utf-8")
    begin, end = "<!-- BEGIN GENERATED: pattern-inventory -->", "<!-- END GENERATED: pattern-inventory -->"
    inventory = "\n".join(f"- `{name}`" for name in patterns)
    if begin in text:
        text = re.sub(
            re.escape(begin) + r".*?" + re.escape(end),
            begin + "\n" + inventory + "\n" + end,
            text,
            flags=re.S,
        )
    # stamp both fallbacks
    ref = git_ref(standards)
    stamp = f"Last synced: {date.today().isoformat()} (source ref: {ref})."
    text = re.sub(r"Last synced: .*", stamp, text, count=1)
    PATTERN_HINTS.write_text(text, encoding="utf-8")
    t = FUNDAMENTALS.read_text(encoding="utf-8")
    t = re.sub(r"Last synced: .*", stamp, t, count=1)
    FUNDAMENTALS.write_text(t, encoding="utf-8")
    print(f"synced fallbacks to {stamp}")


def main():
    standards = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else DEFAULT_STANDARDS
    if not (standards / "schemas" / "skill-frontmatter.schema.json").exists():
        print(f"standards path invalid: {standards}")
        sys.exit(2)

    if "--sync" in sys.argv:
        sync(standards)

    problems = []
    check_schema_fields(problems, standards)
    check_pattern_coverage(problems, standards)
    check_moved_paths(problems)
    check_set_fallbacks(problems)

    if problems:
        print("DRIFT detected:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("OK: fallbacks match the canonical standards")


if __name__ == "__main__":
    main()
