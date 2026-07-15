#!/usr/bin/env python3
"""
Tests for index-skill-capabilities.py.

Run with:
    python skills/blocks/authoring/index-skill-capabilities/scripts/tests/test_index_skill_capabilities.py
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

# Load the script module by file path (it has a hyphen in its name, so normal import won't work).
SCRIPT_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SCRIPT_DIR / "index-skill-capabilities.py"
spec = importlib.util.spec_from_file_location("index_skill_capabilities", SCRIPT_PATH)
assert spec and spec.loader
isc = importlib.util.module_from_spec(spec)
sys.modules["index_skill_capabilities"] = isc
spec.loader.exec_module(isc)


def test_parse_frontmatter():
    with tempfile.TemporaryDirectory() as tmp:
        skill_md = Path(tmp) / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill.
invocation: model-invoked
depends:
  - detect-project-context
---

# Test skill

## In scope
- Do one thing.
- Do another thing.
""", encoding="utf-8")
        fm = isc.parse_frontmatter(skill_md)
        assert fm["name"] == "test-skill"
        assert fm["description"] == "A test skill."
        assert fm["depends"] == ["detect-project-context"]


def test_extract_markdown_sections():
    text = """# Title

## In scope
- One.

## Out of scope
- Two.

### Subsection
- Three.
"""
    sections = isc.extract_markdown_sections(text)
    assert "in scope" in sections
    assert "out of scope" in sections
    # Level-3 subsections remain inside the level-2 section body.
    assert "subsection" not in sections
    assert "### Subsection" in sections["out of scope"]


def test_extract_bullet_items():
    text = """- First item.
- Second item.

1. Numbered item.
2. Another numbered item.
"""
    items = isc.extract_bullet_items(text)
    assert "First item." in items
    assert "Second item." in items
    assert "Numbered item." in items


def test_extract_workflow_phases():
    text = """## Workflow

### Phase 1 — Resolve identity
Resolve the ticket key.

### Phase 2: Gather data
Collect evidence.

1. **Synthesize**
Write the report.
"""
    phases = isc.extract_workflow_phases(text)
    titles = [title for title, _ in phases]
    assert "Resolve identity" in titles
    assert "Gather data" in titles
    assert "Synthesize" in titles


def test_extract_level1_heading():
    assert isc.extract_level1_heading("# Normalize PR\n\n## In scope") == "Normalize PR"
    assert isc.extract_level1_heading("## No level one") is None


def test_clean_description():
    assert isc.clean_description("**Bold** and `code` and more text.") == "Bold and code and more text."
    assert len(isc.clean_description("A" * 300)) <= 200


def test_categorize():
    assert isc.categorize("Resolve PR identity") == "identity-resolution"
    assert isc.categorize("Discover best tool") == "tool-discovery"
    assert isc.categorize("Initialize skill config") == "config-initialization"
    assert isc.categorize("Write the report") == "report-writing"
    assert isc.categorize("Something completely unrelated") == "uncategorized"


def test_index_skill(tmp_path: Path):
    # Build a minimal skill in a temp repo structure.
    skill_dir = tmp_path / "skills" / "main" / "workflow" / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_dir.joinpath("SKILL.md").write_text("""---
name: test-skill
description: A test skill for indexing.
invocation: model-invoked
type: conductor
depends:
  - detect-project-context
---

# Test skill

## In scope
- Resolve a work item from user input.
- Discover the best tool for each capability.
- Write a structured report.

## Out of scope
- Implementing fixes.

## Workflow

### Phase 1 — Resolve identity
Resolve the work item.

### Phase 2 — Gather data
Collect data.

### Phase 3 — Write report
Write the report.

## Dependencies
- detect-project-context
""", encoding="utf-8")

    subagents_dir = skill_dir / "subagents"
    subagents_dir.mkdir()
    subagents_dir.joinpath("data-collector.md").write_text("""# Data collector

## Purpose
Collect data from available sources.
""", encoding="utf-8")

    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()
    scripts_dir.joinpath("initialize.py").write_text("# init", encoding="utf-8")

    references_dir = skill_dir / "references"
    references_dir.mkdir()
    references_dir.joinpath("WORKFLOW.md").write_text("Uses `context-reports`.", encoding="utf-8")

    config_file = skill_dir / "config.yaml"
    config_file.write_text("""test-skill:
  tools:
    provider: auto
""", encoding="utf-8")

    # Monkeypatch the module's REPO_ROOT to the temp path.
    original_root = isc.REPO_ROOT
    isc.REPO_ROOT = tmp_path
    try:
        entry = isc.index_skill("skills/main/workflow/test-skill")
        assert entry.name == "test-skill"
        assert entry.type == "conductor"
        assert entry.origin == "bundle"
        assert "detect-project-context" in entry.depends
        assert "context-reports" in entry.references
        assert "data-collector.md" in entry.subagents
        assert "initialize.py" in entry.scripts
        assert "test-skill" in entry.config_keys

        categories = {c.category for c in entry.capabilities}
        assert "identity-resolution" in categories
        assert "tool-discovery" in categories
        assert "report-writing" in categories
    finally:
        isc.REPO_ROOT = original_root


def main():
    # Use a temporary directory for the integration test.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        test_parse_frontmatter()
        test_extract_markdown_sections()
        test_extract_bullet_items()
        test_extract_workflow_phases()
        test_extract_level1_heading()
        test_clean_description()
        test_categorize()
        test_index_skill(tmp_path)
        print("All tests passed.")


if __name__ == "__main__":
    main()
