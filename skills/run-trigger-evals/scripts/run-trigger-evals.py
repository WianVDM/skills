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


def extract_keywords(description: str) -> list[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]*", description.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def generate_cases(skill_name: str, description: str) -> list[dict]:
    keywords = extract_keywords(description)
    primary = keywords[:3] if keywords else ["task"]
    action_phrase = " ".join(primary)

    should_templates = [
        "Can you {action} for me?",
        "I need help with {action}.",
        "Please {action}.",
        "How do I {action}?",
        "Run {action} on this.",
        "Assist with {action}.",
        "Handle {action}.",
        "I want to {action}.",
        "What is the right way to {action}?",
        "Could you {action}?",
    ]

    should_not_templates = [
        "Can you help me with something unrelated to {action}?",
        "I need a completely different tool, not {action}.",
        "Please ignore {action} and do something else.",
        "How do I do a task that is not {action}?",
        "Run a different operation, not {action}.",
        "Assist with a topic outside {action}.",
        "Handle an unrelated request.",
        "I want to do something else, not {action}.",
        "What is the right way to solve a problem unrelated to {action}?",
        "Could you do something different from {action}?",
    ]

    tests = []
    for i, tmpl in enumerate(should_templates[:10], start=1):
        tests.append({
            "id": f"should-trigger-{i:02d}",
            "type": "trigger",
            "category": "should-trigger",
            "prompt": tmpl.format(action=action_phrase),
            "expected": skill_name,
        })
    for i, tmpl in enumerate(should_not_templates[:10], start=1):
        tests.append({
            "id": f"should-not-trigger-{i:02d}",
            "type": "trigger",
            "category": "should-not-trigger",
            "prompt": tmpl.format(action=action_phrase),
        })
    return tests


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

    tests = generate_cases(skill_name, description)

    if existing:
        tests = existing.get("tests", []) or tests

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
