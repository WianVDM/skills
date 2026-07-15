#!/usr/bin/env python3
"""
index-skill-capabilities.py

Generate a structured capability index from skill files.

Usage:
    python scripts/index-skill-capabilities.py
    python scripts/index-skill-capabilities.py --check
    python scripts/index-skill-capabilities.py --output docs/skill-capability-index.json

The script reads skills.json, parses each skill's SKILL.md frontmatter and sections,
discovers subagents, scripts, references, and config, and emits a JSON index of
capabilities. The index is deterministic and versioned.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[5]
SKILLS_JSON = REPO_ROOT / "skills.json"
DEFAULT_OUTPUT = Path(".agents/skill-capability-index.json")
SCHEMA_VERSION = "1.0.0"

TAXONOMY_KEYWORDS: dict[str, list[str]] = {
    "identity-resolution": [
        "resolve", "identity", "ticket key", "pr number", "branch", "extract key",
        "resolve_pr", "extract-ticket-key", "work item", "pr identity"
    ],
    "tool-discovery": [
        "discover tool", "select tool", "best available tool", "tool selection",
        "capability", "tooling", "tool-discovery", "preferred tool", "fallback tool",
        "best tool", "discover best"
    ],
    "data-collection": [
        "fetch", "collect", "gather", "research", "retrieve", "load data",
        "discover reports", "pr source", "ci source", "issue tracker"
    ],
    "data-normalization": [
        "normalize", "normalize-pr", "normalize-ci", "normalize-static",
        "adapter shape", "normalize-issue", "normalize data", "standardize"
    ],
    "state-management": [
        "checkpoint", "resume", "state", "phase checklist", "current focus",
        "last completed action", "session history", "state file"
    ],
    "checkout": [
        "worktree", "checkout", "branch", "commit", "inspect locally", "git worktree",
        "local branch", "clone", "checkout branch"
    ],
    "config-initialization": [
        "initialize", "config", "first run", "detect project context",
        "initialize-config", "initialize.py", "config.yaml", "load config",
        "project-level config"
    ],
    "report-writing": [
        "write report", "produce report", "context report", "debrief report",
        "report_status", "review-draft", "decision report", "the report",
        "write the report"
    ],
    "scope-checking": [
        "scope", "ticket scope", "changed files", "challenge", "scope-checker",
        "scope-check", "against scope", "actual changes"
    ],
    "freshness-checking": [
        "fresh", "stale", "reuse", "prior report", "freshness", "check-freshness",
        "report is fresh", "outdated"
    ],
    "posting": [
        "post", "submit", "publish", "pull request review", "github_create_pull",
        "review event", "REQUEST_CHANGES", "APPROVE"
    ],
    "assumption-management": [
        "assumption", "challenge assumptions", "form-assumptions", "assumptions",
        "disproof", "ambiguity"
    ],
    "validation": [
        "validate", "audit", "schema", "rubric", "validate-skill-frontmatter",
        "audit-skill", "fundamentals", "check against"
    ],
    "notification": [
        "slack", "teams", "email", "notification", "chat", "feedback channel"
    ],
    "context-scanning": [
        "scan context", "context report", "discover related", "related context",
        "scan-context", "prior reports"
    ],
}


def parse_frontmatter(skill_md: Path) -> dict[str, Any]:
    """Extract YAML frontmatter from a SKILL.md file."""
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    try:
        import yaml
        data = yaml.safe_load(block) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def extract_markdown_sections(text: str) -> dict[str, str]:
    """Split markdown text into sections keyed by level-2 heading text."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        match = re.match(r"^##\s+(.+)$", line)
        if match:
            if current_heading is not None:
                sections[current_heading.lower()] = "\n".join(current_lines).strip()
            current_heading = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading.lower()] = "\n".join(current_lines).strip()

    return sections


def clean_name(text: str) -> str:
    """Strip markdown formatting from a capability name."""
    text = text.strip()
    # Remove bold/italic markers.
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"__", "", text)
    text = re.sub(r"\*", "", text)
    text = re.sub(r"_", "", text)
    # Remove inline code markers.
    text = re.sub(r"`", "", text)
    # Remove trailing punctuation and normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_description(text: str, max_len: int = 200) -> str:
    """Strip markdown and truncate a capability description to a single sentence."""
    text = text.strip()
    # Remove bold/italic markers.
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"(?<!\*)\*(?!\*)|(?<!_)_(?!_)", "", text)
    # Remove inline code markers.
    text = re.sub(r"`", "", text)
    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    # Truncate to first sentence, but keep it under max_len.
    first_sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
    if len(first_sentence) > max_len:
        first_sentence = first_sentence[: max_len - 3].rsplit(" ", 1)[0] + "..."
    return first_sentence


def load_known_skill_names() -> set[str]:
    """Load the set of skill names declared in skills.json."""
    try:
        manifest = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
        names: set[str] = set()
        for path in manifest.get("skills", []):
            names.add(Path(path).name)
        names.update(manifest.get("namespaces", {}).keys())
        return names
    except Exception:
        return set()


KNOWN_SKILL_NAMES = load_known_skill_names()


def extract_references_from_text(text: str) -> list[str]:
    """Find references to other known skills in markdown text."""
    skills: set[str] = set()
    # Match `skill-name` or [skill-name](...) where the token is a known skill name.
    for match in re.finditer(r"`([a-z][a-z0-9-]*)`", text):
        quoted = match.group(1)
        if quoted in KNOWN_SKILL_NAMES:
            skills.add(quoted)
    for match in re.finditer(r"\[([a-z][a-z0-9-]*)\]\(", text):
        quoted = match.group(1)
        if quoted in KNOWN_SKILL_NAMES:
            skills.add(quoted)
    return sorted(skills)


def extract_bullet_items(text: str) -> list[str]:
    """Extract top-level bullet items from a markdown section."""
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            items.append(re.sub(r"^\d+\.\s+", "", stripped))
    return items


def extract_workflow_phases(text: str) -> list[tuple[str, str]]:
    """Extract phase (title, full_line) tuples from a workflow section."""
    phases: list[tuple[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        # Match "Phase N — Name" or "### Phase N: Name" or "N. **Name** — ..." or "N. Name"
        match = re.match(r"^(?:Phase\s+(\d+)[\s:—-]+(.+)|#{2,4}\s+Phase\s+(\d+)[\s:—-]+(.+)|(\d+)\.\s+(.+))$", stripped)
        if match:
            full_line = next(g for i, g in enumerate(match.groups()) if g is not None and (i % 2 == 1) and not g.isdigit())
            # The title is the first bold/emphasized segment or the first clause before an em dash.
            title_match = re.match(r"^(?:\*\*|__)?([^*—]+?)(?:\*\*|__)?\s*(?:—|:-|:)\s*", full_line)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = full_line.split(".")[0].strip()
            phases.append((clean_name(title), full_line))
    return phases


def extract_level1_heading(text: str) -> str | None:
    """Return the first level-1 markdown heading title, if present."""
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+)$", line.strip())
        if match:
            return match.group(1).strip()
    return None


def categorize(name: str, description: str = "") -> str:
    """Map a capability name/description to a taxonomy category."""
    text = f"{name} {description}".lower()
    scores: dict[str, int] = {}
    for category, keywords in TAXONOMY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score:
            scores[category] = score

    if not scores:
        return "uncategorized"

    # Prefer the most specific (highest score) match.
    return max(scores.items(), key=lambda item: item[1])[0]


@dataclass
class Capability:
    id: str
    name: str
    category: str
    description: str
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "sources": self.sources,
        }


@dataclass
class SkillIndex:
    name: str
    path: str
    origin: str
    type: str
    invocation: str
    description: str
    capabilities: list[Capability]
    references: list[str]
    subagents: list[str]
    scripts: list[str]
    config_keys: list[str]
    produces: list[str]
    consumes: list[str]
    depends: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "origin": self.origin,
            "type": self.type,
            "invocation": self.invocation,
            "description": self.description,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "references": self.references,
            "subagents": self.subagents,
            "scripts": self.scripts,
            "config_keys": self.config_keys,
            "produces": self.produces,
            "consumes": self.consumes,
            "depends": self.depends,
        }


def discover_files(skill_dir: Path) -> tuple[list[str], list[str], list[str], list[str]]:
    """Discover subagents, scripts, references, and config keys."""
    subagents: list[str] = []
    scripts: list[str] = []
    references: list[str] = []
    config_keys: list[str] = []

    subagents_dir = skill_dir / "subagents"
    if subagents_dir.exists():
        subagents = sorted([p.name for p in subagents_dir.iterdir() if p.suffix == ".md"])

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        scripts = sorted([p.name for p in scripts_dir.rglob("*") if p.is_file()])

    references_dir = skill_dir / "references"
    if references_dir.exists():
        references = sorted([p.name for p in references_dir.iterdir() if p.is_file()])

    config_file = skill_dir / "config.yaml"
    if config_file.exists():
        try:
            import yaml
            data = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
            # Top-level keys like `shared` and `skill` are too generic.
            # Drill into the skill-specific section if present.
            skill_config = data.get("skill", {})
            if isinstance(skill_config, dict) and skill_config:
                config_keys = [str(k) for k in skill_config.keys()]
            elif isinstance(skill_config, list):
                config_keys = [str(item.get("key")) for item in skill_config if isinstance(item, dict) and item.get("key")]
            else:
                config_keys = [str(k) for k in data.keys()]
        except Exception:
            pass

    return subagents, scripts, references, config_keys


def infer_skill_type(skill_path: str, frontmatter_type: str) -> str:
    """Infer skill type from frontmatter or path when not explicitly set."""
    if frontmatter_type:
        return frontmatter_type
    path = Path(skill_path)
    parts = path.parts
    if len(parts) >= 2 and parts[0] == "skills" and parts[1] == "main":
        if len(parts) >= 3:
            if parts[2] in ("workflow", "product", "engineering", "authoring"):
                return "conductor"
            if parts[2] == "modes":
                return "mode"
            if parts[2] == "setup":
                return "wrapper"
    if len(parts) >= 2 and parts[0] == "skills" and parts[1] == "blocks":
        return "building-block"
    return frontmatter_type


def extract_subagent_capabilities(skill_name: str, skill_dir: Path) -> list[Capability]:
    """Extract capabilities from subagent files."""
    caps: list[Capability] = []
    subagents_dir = skill_dir / "subagents"
    if not subagents_dir.exists():
        return caps

    for subagent_file in sorted(subagents_dir.iterdir()):
        if subagent_file.suffix != ".md":
            continue
        text = subagent_file.read_text(encoding="utf-8", errors="replace")
        sections = extract_markdown_sections(text)
        # Prefer the level-1 heading title, then a role section, then the filename.
        role = extract_level1_heading(text)
        if not role:
            for heading, body in sections.items():
                if heading not in ("purpose", "type", "when to use", "inputs", "outputs"):
                    role = heading
                    break
        if not role:
            role = subagent_file.stem.replace("-", " ")

        cap_name = clean_name(f"{role.title()}")
        description = sections.get("purpose", "").strip().split("\n")[0] if "purpose" in sections else ""
        if not description:
            description = f"Subagent role for {skill_name}."
        else:
            description = clean_description(description)
        category = categorize(cap_name, description)
        caps.append(Capability(
            id=f"{skill_name}:subagent-{subagent_file.stem}",
            name=cap_name,
            category=category,
            description=description,
            sources=[f"subagents/{subagent_file.name}"],
        ))
    return caps


def index_skill(skill_path: str) -> SkillIndex:
    """Build an index entry for a single skill."""
    skill_dir = REPO_ROOT / skill_path
    skill_md = skill_dir / "SKILL.md"
    readme_md = skill_dir / "README.md"
    frontmatter = parse_frontmatter(skill_md) if skill_md.exists() else {}

    name = frontmatter.get("name") or skill_dir.name
    description = frontmatter.get("description") or ""
    skill_type = infer_skill_type(skill_path, frontmatter.get("type") or "")
    invocation = frontmatter.get("invocation") or "model-invoked"
    depends = frontmatter.get("depends") or []
    if isinstance(depends, str):
        depends = [depends]

    # Read SKILL.md body for sections.
    skill_text = skill_md.read_text(encoding="utf-8", errors="replace") if skill_md.exists() else ""
    sections = extract_markdown_sections(skill_text)

    capabilities: list[Capability] = []
    cap_id_counter: dict[str, int] = {}

    def make_id(base: str) -> str:
        # Truncate slug to keep IDs readable and stable.
        slug = re.sub(r"[^a-z0-9-]+", "-", base.lower()).strip("-")
        if len(slug) > 60:
            slug = slug[:60].rstrip("-")
        if slug in cap_id_counter:
            cap_id_counter[slug] += 1
            return f"{name}:{slug}-{cap_id_counter[slug]}"
        cap_id_counter[slug] = 1
        return f"{name}:{slug}"

    # In-scope capabilities.
    in_scope_text = sections.get("in scope", "") + "\n" + sections.get("scope", "")
    for item in extract_bullet_items(in_scope_text):
        if not item:
            continue
        cap_name = clean_name(item.split(".")[0].strip())
        cap = Capability(
            id=make_id(cap_name),
            name=cap_name,
            category=categorize(cap_name, item),
            description=clean_description(item),
            sources=["SKILL.md:In scope"],
        )
        capabilities.append(cap)

    # Workflow phases.
    workflow_text = sections.get("workflow", "")
    for title, full_line in extract_workflow_phases(workflow_text):
        if not title:
            continue
        cap = Capability(
            id=make_id(title),
            name=title,
            category=categorize(title, full_line),
            description=clean_description(full_line),
            sources=["SKILL.md:Workflow"],
        )
        capabilities.append(cap)

    # Branches.
    branches_text = sections.get("branches", "") + "\n" + sections.get("branch entry", "")
    for item in extract_bullet_items(branches_text):
        if not item or "-" not in item:
            continue
        cap_name = clean_name(item.split("-")[0].strip())
        cap = Capability(
            id=make_id(f"branch-{cap_name}"),
            name=cap_name,
            category=categorize(cap_name, item),
            description=clean_description(item),
            sources=["SKILL.md:Branches"],
        )
        capabilities.append(cap)

    # Subagent capabilities.
    capabilities.extend(extract_subagent_capabilities(name, skill_dir))

    # Discover files.
    subagents, scripts, references, config_keys = discover_files(skill_dir)

    # Capabilities from scripts.
    for script in scripts:
        script_name = Path(script).stem.replace("-", " ")
        cap = Capability(
            id=make_id(f"script-{script_name}"),
            name=f"Run {script_name}",
            category=categorize(script_name),
            description=clean_description(f"Deterministic helper script: {script}"),
            sources=[f"scripts/{script}"],
        )
        capabilities.append(cap)

    # References: declared depends plus skills mentioned in text and reference files.
    all_refs: set[str] = set(depends)
    all_refs.update(extract_references_from_text(skill_text))
    if readme_md.exists():
        all_refs.update(extract_references_from_text(readme_md.read_text(encoding="utf-8", errors="replace")))
    for ref_file in references:
        ref_path = skill_dir / "references" / ref_file
        all_refs.update(extract_references_from_text(ref_path.read_text(encoding="utf-8", errors="replace")))
    # Remove self-references.
    all_refs.discard(name)
    references_list = sorted(r for r in all_refs if re.match(r"^[a-z][a-z0-9-]*$", r))

    # Produces/consumes from context reports and capability categories.
    produces: list[str] = []
    consumes: list[str] = []
    for cap in capabilities:
        if cap.category == "report-writing":
            produces.append(clean_description(cap.name))
        if cap.category in ("data-collection", "context-scanning", "freshness-checking"):
            consumes.append(cap.category)

    # Deduplicate capabilities by id.
    seen_ids: set[str] = set()
    unique_caps: list[Capability] = []
    for cap in capabilities:
        if cap.id not in seen_ids:
            seen_ids.add(cap.id)
            unique_caps.append(cap)

    # Normalize path: strip leading ./ and use forward slashes.
    normalized_path = Path(skill_path).as_posix().lstrip("./")

    return SkillIndex(
        name=name,
        path=normalized_path,
        origin="bundle",
        type=skill_type,
        invocation=invocation,
        description=description,
        capabilities=unique_caps,
        references=references_list,
        subagents=subagents,
        scripts=scripts,
        config_keys=config_keys,
        produces=sorted(set(produces)),
        consumes=sorted(set(consumes)),
        depends=sorted(set(depends)),
    )


def compute_source_check() -> dict[str, str]:
    """Compute freshness metadata for the generated index."""
    skills_json_bytes = SKILLS_JSON.read_bytes()
    skills_json_hash = f"sha256:{hashlib.sha256(skills_json_bytes).hexdigest()}"

    latest_mtime: float = 0.0
    for skill_dir in REPO_ROOT.rglob("skills/**/SKILL.md"):
        mtime = skill_dir.stat().st_mtime
        if mtime > latest_mtime:
            latest_mtime = mtime

    return {
        "skills_json_hash": skills_json_hash,
        "latest_skill_mtime": datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat(),
    }


def generate_index(schema_version: str = SCHEMA_VERSION) -> dict[str, Any]:
    """Generate the full capability index."""
    import json as _json
    manifest = _json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    skill_paths = manifest.get("skills", [])

    skills = [index_skill(path).to_dict() for path in skill_paths]

    return {
        "version": schema_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_check": compute_source_check(),
        "skills": skills,
    }


def validate_index(index: dict[str, Any], output_path: Path) -> list[str]:
    """Validate an existing index against the current source files."""
    errors: list[str] = []
    expected_source_check = compute_source_check()
    actual_source_check = index.get("source_check", {})

    if actual_source_check.get("skills_json_hash") != expected_source_check["skills_json_hash"]:
        errors.append("skills.json hash mismatch; index is stale.")
    if actual_source_check.get("latest_skill_mtime") != expected_source_check["latest_skill_mtime"]:
        errors.append("Skill files have changed since the index was generated.")
    if index.get("version") != SCHEMA_VERSION:
        errors.append(f"Index schema version {index.get('version')} is not {SCHEMA_VERSION}.")
    if not isinstance(index.get("skills"), list):
        errors.append("Index is missing 'skills' array.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the skill capability index.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path.")
    parser.add_argument("--check", action="store_true", help="Validate an existing index without overwriting it.")
    parser.add_argument("--schema-version", default=SCHEMA_VERSION, help="Schema version to emit.")
    args = parser.parse_args()

    if args.check:
        if not args.output.exists():
            print(f"Index not found at {args.output}", file=sys.stderr)
            return 1
        index = json.loads(args.output.read_text(encoding="utf-8"))
        errors = validate_index(index, args.output)
        if errors:
            for err in errors:
                print(f"INVALID: {err}", file=sys.stderr)
            return 1
        print(f"Index at {args.output} is valid and fresh.")
        return 0

    index = generate_index(schema_version=args.schema_version)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
