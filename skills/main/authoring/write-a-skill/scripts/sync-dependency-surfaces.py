#!/usr/bin/env python3
"""Sync dependency surfaces from skills.json.

skills.json is the single dependency manifest for write-a-skill. This script
regenerates the marked generated blocks in three surfaces:

  1. SKILL.md frontmatter `depends:` (required + recommended, sorted)
  2. references/DEPENDENCIES.md generated blocks (required/recommended/optional)
  3. README.md generated dependency list

Hand-written rationale outside the generated markers is never touched. Inside
a generated block, trailing rationale text after the first em dash is preserved
per skill name; new skills get a TODO marker so a human fills it in.

Usage:
    python sync-dependency-surfaces.py          # rewrite surfaces in place
    python sync-dependency-surfaces.py --check  # exit 1 if any surface drifts
"""

import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MANIFEST = SKILL_DIR / "skills.json"
SKILL_MD = SKILL_DIR / "SKILL.md"
DEPENDENCIES_MD = SKILL_DIR / "references" / "DEPENDENCIES.md"
README_MD = SKILL_DIR / "README.md"

BEGIN = "<!-- BEGIN GENERATED: {name} -->"
END = "<!-- END GENERATED: {name} -->"


def load_manifest():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    deps = data["skill_dependencies"]["write-a-skill"]
    return {
        "required": sorted(deps.get("required", [])),
        "recommended": sorted(deps.get("recommended", [])),
        "optional": sorted(deps.get("optional", [])),
    }


def replace_frontmatter_depends(text, names):
    """Replace the depends: list in YAML frontmatter."""
    lines = text.split("\n")
    if lines[0].strip() != "---":
        raise SystemExit("SKILL.md: missing frontmatter fence")
    out, i, done = [lines[0]], 1, False
    while i < len(lines):
        line = lines[i]
        if line.startswith("depends:") and not line.startswith(" "):
            out.append("depends:")
            out.extend(f"  - {n}" for n in names)
            i += 1
            while i < len(lines) and (lines[i].startswith("  - ") or not lines[i].strip()):
                i += 1
            done = True
            continue
        out.append(line)
        i += 1
    if not done:
        raise SystemExit("SKILL.md: no depends: key found in frontmatter")
    return "\n".join(out)


def parse_block_rationales(block, name_pattern):
    """Map skill name -> trailing rationale text from an existing generated block."""
    rationales = {}
    for line in block.split("\n"):
        m = re.search(name_pattern, line.strip())
        if m:
            name = m.group(1)
            _, _, rationale = line.partition("—")
            rationales[name] = rationale.strip()
    return rationales


def regenerate_block(block, names, bullet_fmt, name_pattern):
    rationales = parse_block_rationales(block, name_pattern)
    lines = []
    for name in names:
        rationale = rationales.get(name) or "TODO: rationale"
        lines.append(bullet_fmt.format(name=name, rationale=rationale))
    return "\n".join(lines)


def replace_marked_block(text, block_name, new_content):
    begin, end = BEGIN.format(name=block_name), END.format(name=block_name)
    pattern = re.compile(re.escape(begin) + r"(.*?)" + re.escape(end), re.S)
    m = pattern.search(text)
    if not m:
        raise SystemExit(f"marker not found: {block_name}")
    return text[: m.start(1)] + "\n" + new_content + "\n" + text[m.end(1):], m.group(1).strip("\n")


def main():
    check = "--check" in sys.argv
    deps = load_manifest()
    changes = []

    # 1. SKILL.md frontmatter depends
    text = SKILL_MD.read_text(encoding="utf-8")
    new_text = replace_frontmatter_depends(text, deps["required"] + deps["recommended"])
    if new_text != text:
        changes.append(("SKILL.md depends", new_text, text, SKILL_MD))

    # 2. DEPENDENCIES.md blocks
    text = DEPENDENCIES_MD.read_text(encoding="utf-8")
    for block_name, kind in [
        ("required-skills", "required"),
        ("recommended-skills", "recommended"),
        ("optional-skills", "optional"),
    ]:
        new_text, old_block = replace_marked_block(text, block_name, "")
        # regenerate using the OLD block's rationales
        regenerated = regenerate_block(
            old_block,
            deps[kind],
            bullet_fmt="- **{name}** — {rationale}",
            name_pattern=r"\*\*([a-z0-9-]+)\*\*",
        )
        new_text, _ = replace_marked_block(text, block_name, regenerated)
        if new_text != text:
            changes.append((f"DEPENDENCIES.md {block_name}", new_text, text, DEPENDENCIES_MD))
        text = new_text

    # 3. README.md dependency list
    text = README_MD.read_text(encoding="utf-8")
    names = deps["required"] + deps["recommended"]
    new_text, old_block = replace_marked_block(text, "dependencies", "")
    regenerated = regenerate_block(
        old_block,
        names,
        bullet_fmt="- `{name}` — {rationale}",
        name_pattern=r"`([a-z0-9-]+)`",
    )
    new_text, _ = replace_marked_block(text, "dependencies", regenerated)
    if new_text != text:
        changes.append(("README.md dependencies", new_text, text, README_MD))

    if check:
        if changes:
            print("DRIFT: dependency surfaces are out of sync with skills.json:")
            for name, _, _, _ in changes:
                print(f"  - {name}")
            sys.exit(1)
        print("OK: all dependency surfaces match skills.json")
        return

    for label, new_text, _, path in changes:
        path.write_text(new_text, encoding="utf-8")
        print(f"updated {label}")
    if not changes:
        print("OK: surfaces already in sync")


if __name__ == "__main__":
    main()
