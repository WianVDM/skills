#!/usr/bin/env python3
"""
detect-skill-overlap.py

Detect overlap between a target skill and the existing skill catalog using the
machine-readable capability index. Produces a structured report with score-ranked
overlaps and concrete extraction candidates.

The index path is resolved lazily using the initializer pattern:

1. Explicit `--index` argument.
2. `capability_index_path` from `write-a-skill.yaml` config (typically in `.agents/config/`).
3. Project-local override at `.agents/skill-capability-index.json`.
4. Bundle default at `docs/skill-capability-index.json` (relative to the detected project root or the bundle root).
5. Build a fallback index directly from the repository files.

Usage:
    python scripts/detect-skill-overlap.py --target-path skills/main/workflow/pr-review
    python scripts/detect-skill-overlap.py --target-name pr-review
    python scripts/detect-skill-overlap.py --target-json path/to/draft.json

The target can be a skill that is not yet in the index (e.g., a design draft).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Bundle root is where this script is installed. In the bundle repo this is the
# repo root; in a consumer project it is the installed bundle location.
BUNDLE_ROOT = Path(__file__).resolve().parents[5]
BUNDLE_INDEX = BUNDLE_ROOT / "docs" / "skill-capability-index.json"
BUNDLE_SKILLS_JSON = BUNDLE_ROOT / "skills.json"
INDEX_SCHEMA_VERSION = "1.0.0"

# Categories that are more likely to justify extraction as a generic building block.
GENERIC_CATEGORIES = {
    "identity-resolution",
    "tool-discovery",
    "config-initialization",
    "state-management",
    "checkout",
    "freshness-checking",
    "scope-checking",
    "context-scanning",
    "data-normalization",
    "posting",
}

# Category weights for overlap scoring. Higher means more specific and more meaningful.
CATEGORY_WEIGHTS: dict[str, int] = {
    "identity-resolution": 5,
    "tool-discovery": 5,
    "config-initialization": 4,
    "checkout": 4,
    "freshness-checking": 4,
    "scope-checking": 4,
    "state-management": 4,
    "context-scanning": 3,
    "data-collection": 3,
    "data-normalization": 3,
    "posting": 3,
    "report-writing": 2,
    "assumption-management": 2,
    "validation": 2,
    "notification": 2,
    "uncategorized": 1,
}

# Capability → suggested interface skeleton (input/output contract).
INTERFACE_SKELETONS: dict[str, dict[str, Any]] = {
    "identity-resolution": {
        "inputs": ["user input, branch, URL, ticket key, or PR number"],
        "outputs": ["normalized work-item identity (ticket key, PR number, repo, branch)"],
    },
    "tool-discovery": {
        "inputs": ["capability name", "required data type"],
        "outputs": ["ranked list of available tools", "preferred tool with fallback chain"],
    },
    "config-initialization": {
        "inputs": ["project root", "skill name"],
        "outputs": ["config file path", "validated config object"],
    },
    "state-management": {
        "inputs": ["session state", "phase checklist", "last completed action"],
        "outputs": ["updated state file", "resume focus"],
    },
    "checkout": {
        "inputs": ["branch or commit reference"],
        "outputs": ["local worktree path", "checked-out files"],
    },
    "freshness-checking": {
        "inputs": ["report path", "source timestamp", "branch or commit"],
        "outputs": ["fresh/stale verdict", "reason for staleness"],
    },
    "scope-checking": {
        "inputs": ["finding", "ticket scope", "changed files"],
        "outputs": ["in-scope / out-of-scope classification", "justification"],
    },
    "context-scanning": {
        "inputs": ["ticket key or context directory"],
        "outputs": ["list of relevant prior reports"],
    },
    "data-normalization": {
        "inputs": ["provider-specific raw data", "tool name"],
        "outputs": ["normalized envelope matching adapter contract"],
    },
    "posting": {
        "inputs": ["destination (PR, chat, issue tracker)", "payload"],
        "outputs": ["post result", "link or identifier"],
    },
}

# Suggested skill name for a generic building block that implements a category.
CATEGORY_SKILL_NAMES: dict[str, str] = {
    "identity-resolution": "identity-resolver",
    "tool-discovery": "tool-discovery",
    "config-initialization": "initialize-skill",
    "state-management": "checkpoint",
    "checkout": "git-worktree-inspector",
    "freshness-checking": "artifact-freshness",
    "scope-checking": "scope-checker",
    "context-scanning": "scan-context",
    "data-normalization": "data-normalizer",
    "posting": "posting",
    "assumption-management": "challenge-assumptions",
    "validation": "validator",
    "notification": "notifier",
}


def load_project_context_detector() -> Any:
    """Import the detect-project-context module by file path."""
    detector_path = BUNDLE_ROOT / "skills" / "blocks" / "project" / "detect-project-context" / "scripts" / "detect-project-context.py"
    spec = importlib.util.spec_from_file_location("detect_project_context", detector_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["detect_project_context"] = module
    spec.loader.exec_module(module)
    return module


PROJECT_CONTEXT_DETECTOR = load_project_context_detector()


def detect_project_root(start: Path = Path(".")) -> Path | None:
    """Detect the project root from the starting directory."""
    result = PROJECT_CONTEXT_DETECTOR.detect(start.resolve())
    root = result.get("project_root")
    return Path(root) if root else None


def load_write_a_skill_config(project_root: Path | None) -> dict[str, Any]:
    """Load write-a-skill.yaml configuration if it exists.

    Searches the recommended config directory under the project root.
    """
    if project_root is None:
        return {}

    candidates = [
        project_root / ".agents" / "config" / "write-a-skill.yaml",
        project_root / ".agents" / "write-a-skill.yaml",
        project_root / "config" / "write-a-skill.yaml",
    ]
    for config_path in candidates:
        if config_path.exists():
            try:
                import yaml
                data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
                return data if isinstance(data, dict) else {}
            except Exception:
                return {}
    return {}


def resolve_index_path(explicit: Path | None, project_root: Path | None, config: dict[str, Any]) -> Path:
    """Resolve the capability index path using the initializer/lazy-loading pattern.

    Resolution order:
    1. Explicit --index argument.
    2. Configured `capability_index_path` in write-a-skill.yaml.
    3. Project-local override at `.agents/skill-capability-index.json`.
    4. Bundle default at `docs/skill-capability-index.json` (relative to project root or bundle root).
    """
    if explicit is not None:
        return explicit

    if config.get("capability_index_path"):
        path = Path(config["capability_index_path"])
        if path.is_absolute():
            return path
        if project_root is not None:
            return project_root / path
        return path

    if project_root is not None:
        project_local = project_root / ".agents" / "skill-capability-index.json"
        if project_local.exists():
            return project_local

        bundle_default = project_root / "docs" / "skill-capability-index.json"
        if bundle_default.exists():
            return bundle_default

    # Fall back to the bundle default relative to the installed bundle root.
    return BUNDLE_INDEX


def load_index_generator() -> Any:
    """Import the index generator module by file path."""
    generator_path = (
        BUNDLE_ROOT / "skills" / "blocks" / "authoring" / "index-skill-capabilities" / "scripts" / "index-skill-capabilities.py"
    )
    spec = importlib.util.spec_from_file_location("index_skill_capabilities", generator_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["index_skill_capabilities"] = module
    spec.loader.exec_module(module)
    return module


INDEX_GENERATOR = load_index_generator()


def load_index(index_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Load and validate the capability index. Returns (index, warnings)."""
    warnings: list[str] = []
    if not index_path.exists():
        warnings.append(f"Index not found at {index_path}; falling back to description-level detection.")
        return None, warnings

    try:
        text = index_path.read_text(encoding="utf-8")
        index = json.loads(text)
    except Exception as exc:
        warnings.append(f"Index is malformed ({exc}); falling back to description-level detection.")
        return None, warnings

    if not isinstance(index.get("skills"), list):
        warnings.append("Index is missing 'skills' array; falling back to description-level detection.")
        return None, warnings

    if index.get("version") != INDEX_SCHEMA_VERSION:
        warnings.append(
            f"Index schema version {index.get('version')} is not supported ({INDEX_SCHEMA_VERSION}); "
            "falling back to description-level detection."
        )
        return None, warnings

    # Freshness check: compare source hashes against the bundle skills.json.
    try:
        skills_json_bytes = BUNDLE_SKILLS_JSON.read_bytes()
        expected_hash = f"sha256:{hashlib.sha256(skills_json_bytes).hexdigest()}"
        actual_hash = index.get("source_check", {}).get("skills_json_hash")
        if actual_hash != expected_hash:
            warnings.append("Index is stale (skills.json hash mismatch). Consider regenerating it.")
    except Exception:
        pass

    return index, warnings


def build_index_from_repo() -> dict[str, Any]:
    """Fallback: build a minimal capability index directly from skill files."""
    manifest = json.loads(BUNDLE_SKILLS_JSON.read_text(encoding="utf-8"))
    skill_paths = manifest.get("skills", [])

    original_root = INDEX_GENERATOR.REPO_ROOT
    INDEX_GENERATOR.REPO_ROOT = BUNDLE_ROOT
    try:
        skills = [INDEX_GENERATOR.index_skill(path).to_dict() for path in skill_paths]
    finally:
        INDEX_GENERATOR.REPO_ROOT = original_root

    return {
        "version": INDEX_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_check": {},
        "skills": skills,
    }


def load_target_from_path(target_path: Path) -> dict[str, Any]:
    """Build a minimal index entry from a target skill directory."""
    original_root = INDEX_GENERATOR.REPO_ROOT
    INDEX_GENERATOR.REPO_ROOT = BUNDLE_ROOT
    try:
        rel_path = target_path.resolve().relative_to(BUNDLE_ROOT).as_posix()
        entry = INDEX_GENERATOR.index_skill(rel_path)
        return entry.to_dict()
    finally:
        INDEX_GENERATOR.REPO_ROOT = original_root


def load_target_from_name(target_name: str, index: dict[str, Any]) -> dict[str, Any] | None:
    """Look up a target skill by name in the index."""
    for skill in index["skills"]:
        if skill.get("name") == target_name:
            return skill
    return None


def load_target_from_json(json_path: Path) -> dict[str, Any]:
    """Load a target skill entry from a JSON file."""
    text = json_path.read_text(encoding="utf-8")
    return json.loads(text)


def set_similarity(a: list[str], b: list[str]) -> tuple[int, list[str]]:
    """Return count and list of shared items between two lists."""
    set_a = set(a)
    set_b = set(b)
    shared = sorted(set_a & set_b)
    return len(shared), shared


def word_overlap_score(a: str, b: str) -> int:
    """Simple description-level overlap signal (fallback)."""
    stop_words = {
        "a", "an", "the", "and", "or", "but", "to", "of", "in", "on", "at", "for",
        "with", "from", "by", "is", "are", "was", "were", "be", "been", "being",
        "it", "its", "this", "that", "these", "those", "as", "use", "using", "used",
    }
    words_a = {w.lower() for w in re.findall(r"[a-zA-Z]+", a) if len(w) > 2 and w.lower() not in stop_words}
    words_b = {w.lower() for w in re.findall(r"[a-zA-Z]+", b) if len(w) > 2 and w.lower() not in stop_words}
    return len(words_a & words_b)


def score_overlap(target: dict[str, Any], candidate: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    """Score how much the target skill overlaps with a candidate skill."""
    target_caps = target.get("capabilities", [])
    candidate_caps = candidate.get("capabilities", [])

    target_categories = {c["category"] for c in target_caps}
    candidate_categories = {c["category"] for c in candidate_caps}
    shared_categories = target_categories & candidate_categories

    category_score = sum(CATEGORY_WEIGHTS.get(c, 1) for c in shared_categories)

    shared_refs_count, shared_refs = set_similarity(target.get("references", []), candidate.get("references", []))
    shared_subagents_count, shared_subagents = set_similarity(target.get("subagents", []), candidate.get("subagents", []))
    shared_scripts_count, shared_scripts = set_similarity(target.get("scripts", []), candidate.get("scripts", []))
    shared_config_count, shared_config = set_similarity(target.get("config_keys", []), candidate.get("config_keys", []))
    shared_produces_count, shared_produces = set_similarity(target.get("produces", []), candidate.get("produces", []))
    shared_consumes_count, shared_consumes = set_similarity(target.get("consumes", []), candidate.get("consumes", []))

    description_score = word_overlap_score(target.get("description", ""), candidate.get("description", ""))

    total_score = (
        category_score * 2
        + shared_refs_count * 3
        + shared_subagents_count * 2
        + shared_scripts_count * 1
        + shared_config_count * 2
        + shared_produces_count * 1
        + shared_consumes_count * 1
        + description_score
    )

    details = {
        "shared_categories": sorted(shared_categories),
        "shared_references": shared_refs,
        "shared_subagents": shared_subagents,
        "shared_scripts": shared_scripts,
        "shared_config_keys": shared_config,
        "shared_produces": shared_produces,
        "shared_consumes": shared_consumes,
        "description_word_overlap": description_score,
    }

    return total_score, details


def build_interface_sketch(category: str, descriptions: list[str]) -> dict[str, Any]:
    """Build a suggested input/output contract for an extraction candidate."""
    base = INTERFACE_SKELETONS.get(category, {
        "inputs": ["TBD"],
        "outputs": ["TBD"],
    }).copy()
    if descriptions:
        base["description"] = descriptions[0]
    return base


def build_contract_skeleton(category: str, capability_name: str, interface_sketch: dict[str, Any]) -> str:
    """Return a draft SKILL.md skeleton for a generic building block that implements this capability."""
    skill_name = CATEGORY_SKILL_NAMES.get(category, category.replace("-", "-"))
    description = interface_sketch.get("description") or f"Provide a reusable {category} capability for other skills."
    inputs = interface_sketch.get("inputs", ["TBD"])
    outputs = interface_sketch.get("outputs", ["TBD"])

    inputs_bullets = "\n".join(f"- {item}" for item in inputs)
    outputs_bullets = "\n".join(f"- {item}" for item in outputs)

    return f"""---
name: {skill_name}
description: {description}
invocation: model-invoked
depends:
  - detect-project-context
---

# {skill_name}

## Purpose

{description}

## Type

Building block.

## In scope

- Accept the normalized input for the {category} capability.
- Perform the operation and return the normalized output.
- Expose a stable interface that other skills can depend on.

## Out of scope

- Workflow-specific orchestration; this block provides the capability, not the workflow.
- Provider-specific logic beyond the normalized interface.

## When to use

- When a skill or conductor needs to {capability_name.lower()} and a reusable implementation is preferable to colocating the logic.

## Steps

1. Validate the input against the expected shape.
2. Execute the {category} operation.
3. Return the normalized output.

## Inputs

{inputs_bullets}

## Outputs

{outputs_bullets}

## Dependencies

See [references/DEPENDENCIES.md](references/DEPENDENCIES.md).

## References

- `docs/skill-standards/fundamentals/architecture/dependencies-and-bundling.md`
- `skills/blocks/authoring/index-skill-capabilities/references/INDEX_SCHEMA.md`
"""


def find_extraction_candidates(target: dict[str, Any], index: dict[str, Any]) -> list[dict[str, Any]]:
    """Identify capabilities in the target that could be extracted as building blocks."""
    target_caps = target.get("capabilities", [])
    candidates: list[dict[str, Any]] = []

    # Group existing skills by capability category.
    category_skills: dict[str, list[str]] = {}
    category_caps: dict[str, list[dict[str, Any]]] = {}
    for skill in index["skills"]:
        if skill["name"] == target.get("name"):
            continue
        for cap in skill.get("capabilities", []):
            cat = cap["category"]
            category_skills.setdefault(cat, []).append(skill["name"])
            category_caps.setdefault(cat, []).append(cap)

    for cap in target_caps:
        cat = cap["category"]
        if cat not in GENERIC_CATEGORIES:
            continue
        other_skills = sorted(set(category_skills.get(cat, [])))
        if not other_skills:
            continue

        descriptions = [cap["description"] for cap in category_caps.get(cat, []) if cap.get("description")]
        if cap.get("description"):
            descriptions.insert(0, cap["description"])
        interface_summary = descriptions[0] if descriptions else f"Capability: {cap['name']}"
        interface_sketch = build_interface_sketch(cat, descriptions)

        effort = "small" if len(other_skills) >= 2 and cat in {"tool-discovery", "config-initialization", "identity-resolution"} else "medium"
        if len(other_skills) >= 3:
            effort = "small" if cat in {"tool-discovery", "config-initialization", "identity-resolution"} else "medium"

        candidates.append({
            "capability_id": cap["id"],
            "capability_name": cap["name"],
            "category": cat,
            "description": cap.get("description", ""),
            "other_skills": other_skills,
            "interface_summary": interface_summary,
            "interface_sketch": interface_sketch,
            "contract_skeleton": build_contract_skeleton(cat, cap["name"], interface_sketch),
            "effort": effort,
            "recommended": len(other_skills) >= 2,
        })

    # Deduplicate by category and sort by number of other skills descending.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for c in sorted(candidates, key=lambda x: -len(x["other_skills"])):
        if c["category"] not in seen:
            seen.add(c["category"])
            unique.append(c)

    return unique


def detect_overlap(
    target: dict[str, Any],
    index: dict[str, Any],
    threshold: float = 0.0,
    false_positives: set[str] | None = None,
) -> dict[str, Any]:
    """Produce a full overlap report."""
    false_positives = false_positives or set()
    overlaps: list[dict[str, Any]] = []
    for skill in index["skills"]:
        if skill["name"] == target.get("name"):
            continue
        score, details = score_overlap(target, skill)
        if score <= threshold:
            continue
        if skill["name"] in false_positives:
            continue
        overlaps.append({
            "skill": skill["name"],
            "type": skill.get("type", ""),
            "description": skill.get("description", ""),
            "score": score,
            "details": details,
        })

    overlaps.sort(key=lambda x: x["score"], reverse=True)
    extraction_candidates = find_extraction_candidates(target, index)

    return {
        "target": target.get("name", "unknown"),
        "target_type": target.get("type", ""),
        "target_description": target.get("description", ""),
        "index_version": index.get("version", ""),
        "index_generated_at": index.get("generated_at", ""),
        "overlap_count": len(overlaps),
        "extraction_candidate_count": len(extraction_candidates),
        "overlaps": overlaps,
        "extraction_candidates": extraction_candidates,
    }


def render_markdown(report: dict[str, Any], warnings: list[str], index_path: Path) -> str:
    """Render the overlap report as markdown."""
    lines = [
        f"# Overlap report: {report['target']}",
        "",
        f"- **Target:** `{report['target']}` ({report['target_type']})",
        f"- **Index source:** `{index_path}`",
        f"- **Index version:** {report['index_version']}",
        f"- **Overlaps found:** {report['overlap_count']}",
        f"- **Extraction candidates:** {report['extraction_candidate_count']}",
        "",
    ]

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")

    lines.extend([
        "## Overlap findings",
        "",
    ])

    if not report["overlaps"]:
        lines.append("No significant overlaps found.")
    else:
        lines.append("| Rank | Skill | Type | Score | Shared categories | Shared references |")
        lines.append("|---|---|---|---|---|---|")
        for i, overlap in enumerate(report["overlaps"], 1):
            cats = ", ".join(overlap["details"]["shared_categories"]) or "—"
            refs = ", ".join(overlap["details"]["shared_references"]) or "—"
            lines.append(
                f"| {i} | `{overlap['skill']}` | {overlap['type']} | {overlap['score']:.1f} | {cats} | {refs} |"
            )

    lines.extend([
        "",
        "## Extraction candidates",
        "",
    ])

    if not report["extraction_candidates"]:
        lines.append("No strong extraction candidates found.")
    else:
        for cand in report["extraction_candidates"]:
            status = "Recommended" if cand["recommended"] else "Consider"
            lines.append(f"### {cand['capability_name']} ({status})")
            lines.append("")
            lines.append(f"- **Category:** `{cand['category']}`")
            lines.append(f"- **Also appears in:** {', '.join(f'`{s}`' for s in cand['other_skills'])}")
            lines.append(f"- **Effort:** {cand['effort']}")
            lines.append(f"- **Suggested interface:** {cand['interface_summary']}")
            lines.append("")
            lines.append("**Interface sketch:**")
            lines.append("")
            lines.append(f"- Inputs: {', '.join(cand['interface_sketch']['inputs'])}")
            lines.append(f"- Outputs: {', '.join(cand['interface_sketch']['outputs'])}")
            if cand["interface_sketch"].get("description"):
                lines.append(f"- Description: {cand['interface_sketch']['description']}")
            lines.append("")
            lines.append("**Capability contract skeleton:**")
            lines.append("")
            lines.append("```markdown")
            lines.append(cand["contract_skeleton"].strip())
            lines.append("```")
            lines.append("")

    return "\n".join(lines)


def load_false_positives(false_positives_path: Path | None) -> set[str]:
    """Load a set of skill names to exclude from overlap findings."""
    if not false_positives_path or not false_positives_path.exists():
        return set()
    data = json.loads(false_positives_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return set(str(item) for item in data)
    if isinstance(data, dict):
        return set(str(item) for item in data.get("false_positives", []))
    return set()


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect skill overlap using the capability index.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target-path", type=Path, help="Path to the target skill directory.")
    group.add_argument("--target-name", type=str, help="Name of an existing skill in the index.")
    group.add_argument("--target-json", type=Path, help="JSON file describing the target skill entry.")
    parser.add_argument("--index", type=Path, default=None, help="Path to the capability index (overrides config and defaults).")
    parser.add_argument("--threshold", type=float, default=0.0, help="Minimum overlap score to include.")
    parser.add_argument("--false-positives", type=Path, help="JSON file with false-positive skill names to ignore.")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown.")
    args = parser.parse_args()

    # Lazy-load the project context and config to resolve the index path.
    project_root = detect_project_root()
    config = load_write_a_skill_config(project_root)
    index_path = resolve_index_path(args.index, project_root, config)

    index, warnings = load_index(index_path)
    if index is None:
        warnings.append("Building index from repository files (fallback mode).")
        index = build_index_from_repo()

    false_positives = load_false_positives(args.false_positives)

    if args.target_name:
        target = load_target_from_name(args.target_name, index)
        if not target:
            print(f"Target skill `{args.target_name}` not found in index.", file=sys.stderr)
            return 1
    elif args.target_path:
        target = load_target_from_path(args.target_path)
    else:
        target = load_target_from_json(args.target_json)

    report = detect_overlap(target, index, threshold=args.threshold, false_positives=false_positives)

    if args.json:
        print(json.dumps({**report, "index_source": str(index_path), "warnings": warnings}, indent=2))
    else:
        print(render_markdown(report, warnings, index_path))

    return 0


if __name__ == "__main__":
    sys.exit(main())
