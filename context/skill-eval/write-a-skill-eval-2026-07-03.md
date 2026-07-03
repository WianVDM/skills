---
skill: write-a-skill
version: "3.1"
timestamp: 2026-07-03T10:10:46.176946+00:00
status: final
---

# Behavioral eval report: write-a-skill

**Result:** 17/17 checks passed.

- 🟢 Invocation: user-invoked declared
- 🟢 Invocation: disable-model-invocation declared
- 🟢 No drafting before confirmation rule
- 🟢 Self-audit checks one core objective
- 🟢 Self-audit blocks drafting on failure
- 🟢 Path detection returns high confidence
  - project_root=G:\My Drive, confidence=high
- 🟢 Workers do not ask users directly
  - checked 11 workers
- 🟢 Every branch has a completion criterion
- 🟢 No .agents/ hardcoding outside detection rules
- 🟢 Review workflow prefers read-only
- 🟢 Upgrade confirms changes
- 🟢 SKILL.md points to BRANCH_WORKFLOWS.md
- 🟢 SKILL.md is under 300 lines
  - 146 lines
- 🟢 Python dependency declared
- 🟢 EVAL.md has 10/10 trigger evals
  - should-trigger=24, should-not-trigger=14
- 🟢 Glossary exists
- 🟢 All reference links resolve
  - missing: []

## Summary
All static behavioral evals passed. The skill is ready for live trigger testing against an agent harness.