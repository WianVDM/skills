#!/usr/bin/env python3
"""
run-trigger-evals.py

Generate and update trigger evals for model-invoked skills.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "must", "shall",
    "can", "need", "dare", "ought", "used", "to", "of", "in", "for", "on",
    "with", "at", "by", "from", "as", "into", "through", "during", "before",
    "after", "above", "below", "between", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only",
    "own", "same", "so", "than", "too", "very", "this", "that", "these", "those",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her",
    "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "what", "which", "who", "whom", "whose", "whomever", "whatever",
}

BRANCH_TEMPLATES = [
    "{trigger}",
    "In this situation: {trigger}",
]

USE_CASE_TEMPLATES = [
    "{item}",
    "In this situation: {item}",
]

NEAR_MISS_TEMPLATES = [
    "Can you help me with something related to {topic} but not {skill}?",
    "I need a different tool for {topic}, not {skill}.",
    "How do I {related_action} instead of using {skill}?",
    "What is the best way to handle {topic} without using {skill}?",
    "Please do something related to {topic} but do not invoke {skill}.",
]


def parse_skill_frontmatter(skill_md: Path) -> dict:
    """Load the shared frontmatter parser and parse a SKILL.md file."""
    parser_path = (
        Path(__file__).resolve().parent.parent.parent
        / "parse-skill-frontmatter"
        / "scripts"
        / "parse-skill-frontmatter.py"
    )
    spec = importlib.util.spec_from_file_location(
        "parse_skill_frontmatter", parser_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_frontmatter(skill_md)


def extract_body(skill_md: Path) -> str:
    """Return the body of SKILL.md after the frontmatter block."""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4:]


def extract_section(body: str, heading: str) -> str:
    """Extract the content of a markdown section by heading."""
    pattern = re.compile(rf"(?i)^##\s*{re.escape(heading)}\s*\n(.*?)(?=\n##\s|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(body)
    return match.group(1) if match else ""


def extract_when_to_use(body: str) -> list[str]:
    """Return bullet items from the When to use section."""
    section = extract_section(body, "When to use")
    items = re.findall(r"^\s*-\s*(.+)$", section, re.MULTILINE)
    return [item.strip() for item in items if item.strip()]


def extract_branches(body: str) -> list[dict]:
    """Return branch rows from the Branch entry table."""
    section = extract_section(body, "Branch entry")
    branches = []
    rows = re.findall(r"^\s*\|\s*(.+?)\s*\|\s*$", section, re.MULTILINE)
    for row in rows:
        cells = [cell.strip() for cell in row.split("|")]
        if len(cells) < 3:
            continue
        branch_name = cells[0]
        # Skip header and separator rows.
        if branch_name.lower() in ("gate", "branch") or branch_name.replace("-", "") == "":
            continue
        trigger = cells[1]
        outcome = cells[2]
        if trigger.replace("-", "") == "" or outcome.replace("-", "") == "":
            continue
        branches.append({
            "branch": branch_name,
            "trigger": trigger,
            "outcome": outcome,
        })
    return branches


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def extract_keywords(description: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]*", description.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def generate_branch_cases(skill_name: str, branches: list[dict]) -> list[dict]:
    """Generate should-trigger cases from branch triggers and outcomes."""
    tests = []
    for branch in branches:
        branch_slug = slugify(branch["branch"])
        trigger = branch["trigger"].strip()
        for i, tmpl in enumerate(BRANCH_TEMPLATES, start=1):
            prompt = tmpl.format(trigger=trigger)
            if not prompt.endswith((".", "?", "!")):
                prompt += "."
            tests.append({
                "id": f"should-trigger-{branch_slug}-{i}",
                "type": "trigger",
                "category": "should-trigger",
                "prompt": prompt,
                "expected": skill_name,
            })
    return tests


def generate_use_case_cases(skill_name: str, items: list[str]) -> list[dict]:
    """Generate should-trigger cases from the When to use list."""
    tests = []
    for item in items:
        item_slug = slugify(item)
        for i, tmpl in enumerate(USE_CASE_TEMPLATES, start=1):
            prompt = tmpl.format(item=item.strip())
            if not prompt.endswith((".", "?", "!")):
                prompt += "."
            tests.append({
                "id": f"should-trigger-use-{item_slug}-{i}",
                "type": "trigger",
                "category": "should-trigger",
                "prompt": prompt,
                "expected": skill_name,
            })
    return tests


def generate_near_miss_cases(skill_name: str, description: str, branches: list[dict]) -> list[dict]:
    """Generate plausible should-not-trigger near-misses."""
    keywords = extract_keywords(description)
    topic = " ".join(keywords[:3]) if keywords else "this"
    related_actions = [b["trigger"] for b in branches[:2]] if branches else ["do something else"]

    tests = []
    for i, tmpl in enumerate(NEAR_MISS_TEMPLATES, start=1):
        related_action = related_actions[(i - 1) % len(related_actions)].strip()
        prompt = tmpl.format(
            topic=topic,
            skill=skill_name,
            related_action=related_action.lower(),
        )
        if not prompt.endswith((".", "?", "!")):
            prompt += "."
        tests.append({
            "id": f"should-not-trigger-{i:02d}",
            "type": "trigger",
            "category": "should-not-trigger",
            "prompt": prompt,
        })
    return tests


def generate_fallback_cases(skill_name: str, description: str) -> tuple[list[dict], list[dict]]:
    """Fallback keyword-based cases when no branches or use cases are found."""
    keywords = extract_keywords(description)
    primary = keywords[:3] if keywords else ["task"]
    action_phrase = " ".join(primary)

    should = []
    for i, tmpl in enumerate([
        "Can you {action} for me?",
        "I need help with {action}.",
        "Please {action}.",
        "How do I {action}?",
        "Run {action} on this.",
    ], start=1):
        prompt = tmpl.format(action=action_phrase).rstrip(".") + "."
        should.append({
            "id": f"should-trigger-fallback-{i:02d}",
            "type": "trigger",
            "category": "should-trigger",
            "prompt": prompt,
            "expected": skill_name,
        })

    should_not = []
    for i, tmpl in enumerate([
        "Can you help me with something unrelated to {action}?",
        "I need a completely different tool, not {action}.",
        "Please do something else, not {action}.",
    ], start=1):
        prompt = tmpl.format(action=action_phrase).rstrip(".") + "."
        should_not.append({
            "id": f"should-not-trigger-fallback-{i:02d}",
            "type": "trigger",
            "category": "should-not-trigger",
            "prompt": prompt,
        })
    return should, should_not


def merge_tests(existing_tests: list[dict], new_tests: list[dict]) -> list[dict]:
    """Merge existing tests with newly generated ones, replacing by ID."""
    by_id = {t["id"]: t for t in existing_tests if "id" in t}
    merged = []
    seen_ids = set()

    # Add new tests, replacing any existing test with the same ID.
    for test in new_tests:
        if test["id"] in seen_ids:
            continue
        merged.append(test)
        by_id[test["id"]] = test
        seen_ids.add(test["id"])

    # Keep existing tests that were not replaced.
    for test in existing_tests:
        if test["id"] not in seen_ids:
            merged.append(test)
            seen_ids.add(test["id"])

    return merged


def validate_evals(data: dict, schema_path: Path) -> tuple[bool, list[dict]]:
    try:
        import jsonschema
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        errors = [{"message": e.message, "path": "/".join(str(p) for p in e.path)} for e in validator.iter_errors(data)]
        return len(errors) == 0, errors
    except ImportError:
        return True, [{"message": "jsonschema not installed; skipping validation."}]


def build_evals(skill_dir: Path, existing: dict | None = None) -> dict:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    fm = parse_skill_frontmatter(skill_md)
    skill_name = fm.get("name", skill_dir.name)
    description = fm.get("description", "")
    body = extract_body(skill_md)

    branches = extract_branches(body)
    use_cases = extract_when_to_use(body)

    should_trigger = []
    should_not_trigger = []

    if branches:
        should_trigger.extend(generate_branch_cases(skill_name, branches))
    if use_cases:
        should_trigger.extend(generate_use_case_cases(skill_name, use_cases))
    if not should_trigger:
        fallback_should, fallback_should_not = generate_fallback_cases(skill_name, description)
        should_trigger.extend(fallback_should)
        should_not_trigger.extend(fallback_should_not)
    else:
        should_not_trigger.extend(generate_near_miss_cases(skill_name, description, branches))

    # Stable ordering: branch cases first, then use cases, then near misses.
    new_tests = should_trigger + should_not_trigger

    if existing:
        tests = merge_tests(existing.get("tests", []), new_tests)
    else:
        tests = new_tests

    return {
        "version": "1",
        "skill": skill_name,
        "tests": tests,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate trigger evals for a model-invoked skill.")
    parser.add_argument("skill_dir", help="Path to the target skill directory.")
    parser.add_argument("--input", help="Path to existing evals.json to merge.")
    parser.add_argument("--validate", action="store_true", help="Only validate existing evals.")
    parser.add_argument("--schema", default="docs/skill-standards/schemas/evals.json.schema.json", help="Path to evals schema.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    schema_path = Path(args.schema).expanduser().resolve()
    evals_dir = skill_dir / "evals"
    evals_path = evals_dir / "evals.json"

    if args.validate:
        if not evals_path.is_file():
            print(f"ERROR: {evals_path} not found.", file=sys.stderr)
            sys.exit(1)
        data = json.loads(evals_path.read_text(encoding="utf-8"))
        valid, errors = validate_evals(data, schema_path)
        report = {"skill": skill_dir.name, "path": str(evals_path), "valid": valid, "errors": errors}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Validation: {'PASS' if valid else 'FAIL'}")
            for e in errors:
                print(f"  - {e['path']}: {e['message']}")
        sys.exit(0 if valid else 1)

    existing = None
    if args.input:
        input_path = Path(args.input).expanduser().resolve()
        existing = json.loads(input_path.read_text(encoding="utf-8"))

    evals = build_evals(skill_dir, existing)
    valid, errors = validate_evals(evals, schema_path)

    evals_dir.mkdir(parents=True, exist_ok=True)
    evals_path.write_text(json.dumps(evals, indent=2), encoding="utf-8")

    report = {
        "skill": evals["skill"],
        "path": str(evals_path),
        "valid": valid,
        "errors": errors,
        "should_trigger_count": len([t for t in evals["tests"] if t.get("category") == "should-trigger"]),
        "should_not_trigger_count": len([t for t in evals["tests"] if t.get("category") == "should-not-trigger"]),
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Generated evals for {report['skill']} at {report['path']}")
        print(f"  Should-trigger: {report['should_trigger_count']}")
        print(f"  Should-not-trigger: {report['should_not_trigger_count']}")
        print(f"  Validation: {'PASS' if valid else 'FAIL'}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
