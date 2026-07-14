#!/usr/bin/env python3
"""Infer candidate standards rules from markdown documents.

Reads one or more markdown files and extracts rule-like statements into a
YAML structure suitable for the `standards` gate. The extraction is heuristic
and deterministic: it looks for headings, bullet items, and emphasized terms
that suggest a rule ("must", "should", "never", "always", "avoid", etc.).

The output is intended to be reviewed by the user before persisting. It is not
authoritative on its own.

Usage:
    python infer-standards.py --source docs/coding-standards.md --source docs/testing-standards.md
    python infer-standards.py --source CONTRIBUTING.md --output .agents/config/inferred-standards.yaml

Outputs YAML to stdout (or --output) with this structure:
    rules:
      - id: inferred-rule-1
        category: naming
        severity: violation
        description: "..."
        source: "docs/coding-standards.md"
      - ...
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml


# Keywords that indicate a mandatory rule.
VIOLATION_KEYWORDS = [
    "must",
    "must not",
    "never",
    "always",
    "do not",
    "don't",
    "cannot",
    "required",
    "mandatory",
    "forbidden",
    "prohibited",
]

# Keywords that indicate a guideline or consideration.
CONSIDERATION_KEYWORDS = [
    "should",
    "should not",
    "prefer",
    "avoid",
    "consider",
    "try to",
    "recommended",
    "guideline",
]

# Keywords that map rule categories.
CATEGORY_KEYWORDS = {
    "naming": ["name", "naming", "variable", "function", "method", "class"],
    "tests": ["test", "spec", "assertion", "coverage", "mock"],
    "complexity": ["complexity", "length", "nested", "depth", "cyclomatic"],
    "maintenance": ["comment", "dead code", "unused", "import", "export"],
    "architecture": ["module", "dependency", "import", "layer", "coupling"],
    "reliability": ["error", "exception", "catch", "handle"],
    "style": ["format", "indent", "spacing", "style", "lint"],
    "security": ["security", "sanitize", "escape", "injection"],
}


def _read_text(path: Path) -> str:
    """Read text safely, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _parse_frontmatter(text: str) -> tuple[str, str]:
    """Split a YAML frontmatter block from the body of a markdown file."""
    if not text.startswith("---"):
        return "", text
    end = text.find("---", 3)
    if end == -1:
        return "", text
    return text[3:end].strip(), text[end + 3 :].lstrip()


def _slugify(text: str) -> str:
    """Create a safe rule id slug from a text fragment."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = text[:60].strip("-")
    return text


def _classify_severity(line: str) -> str:
    """Classify a line as violation, consideration, or warning based on wording."""
    lower = line.lower()
    for kw in VIOLATION_KEYWORDS:
        if kw in lower:
            return "violation"
    for kw in CONSIDERATION_KEYWORDS:
        if kw in lower:
            return "consideration"
    return "warning"


def _classify_category(line: str) -> str:
    """Infer a category from the line content."""
    lower = line.lower()
    best = "general"
    best_score = 0
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > best_score:
            best_score = score
            best = category
    return best


def _extract_headings(text: str) -> List[str]:
    """Extract markdown headings as context strings."""
    return re.findall(r"^#{1,3}\s+(.+)$", text, re.MULTILINE)


def _extract_rule_lines(text: str) -> List[str]:
    """Extract bullet or numbered lines that look like rules."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip code blocks and horizontal rules
        if stripped.startswith("```") or stripped.startswith("---"):
            continue
        # Bullet or numbered items
        match = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.+)$", stripped)
        if match:
            content = match.group(1).strip()
            if content and not content.startswith("!"):
                lines.append(content)
        # Bold or italic lines that look like rules
        elif re.match(r"^\*\*.+\*\*[:\s-]", stripped) or re.match(r"^__.+__[:\s-]", stripped):
            lines.append(stripped)
    return lines


def _build_rule(line: str, source: str, index: int) -> Optional[Dict]:
    """Build a rule dict from a candidate line, or None if not rule-like."""
    # Remove markdown emphasis and links.
    clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
    clean = re.sub(r"__([^_]+)__", r"\1", clean)
    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
    clean = re.sub(r"`([^`]+)`", r"\1", clean)
    clean = clean.strip(" -*")

    if not clean or len(clean) < 12:
        return None

    severity = _classify_severity(clean)
    category = _classify_category(clean)
    rule_id = _slugify(clean) or f"inferred-rule-{index}"

    return {
        "id": rule_id,
        "category": category,
        "severity": severity,
        "description": clean,
        "source": source,
    }


def infer_rules(source_paths: List[Path]) -> List[Dict]:
    """Infer candidate rules from the given markdown source paths."""
    rules: List[Dict] = []
    seen_ids: set = set()
    index = 0

    for source in source_paths:
        if source.suffix.lower() not in {".md", ".markdown"}:
            # Skip non-markdown files; the inference heuristics are designed for prose.
            continue

        text = _read_text(source)
        if not text:
            continue
        _, body = _parse_frontmatter(text)
        rule_lines = _extract_rule_lines(body)

        for line in rule_lines:
            rule = _build_rule(line, str(source), index)
            index += 1
            if not rule:
                continue

            # Deduplicate by id and description similarity.
            if rule["id"] in seen_ids:
                rule["id"] = f"{rule['id']}-{index}"
            seen_ids.add(rule["id"])

            rules.append(rule)

    return rules


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Infer candidate standards rules from markdown documents."
    )
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Path to a markdown standards source. May be repeated.",
    )
    parser.add_argument(
        "--output",
        help="Path to write the inferred YAML. If omitted, writes to stdout.",
    )
    args = parser.parse_args()

    source_paths = [Path(s).resolve() for s in args.source]
    rules = infer_rules(source_paths)

    output = {"rules": rules}

    try:
        yaml_text = yaml.safe_dump(
            output,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )
    except Exception as exc:  # pragma: no cover - safety net
        print(f"error: could not serialize YAML: {exc}", file=sys.stderr)
        return 1

    if args.output:
        try:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(yaml_text, encoding="utf-8")
        except OSError as exc:
            print(f"error: could not write {args.output}: {exc}", file=sys.stderr)
            return 1
    else:
        print(yaml_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
