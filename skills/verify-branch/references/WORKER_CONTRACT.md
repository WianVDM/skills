# Worker Contract

This document defines the standard return contract used by all `verify-branch` subagents. Every subagent must return a response that follows this format so the main conductor skill can interpret results consistently.

## Purpose

The main `SKILL.md` is intentionally thin. It delegates all heavy work to focused subagents. This contract ensures that every subagent speaks the same language: a clear status, a structured body, and optional artifacts.

## Return format

Every subagent response must begin with a YAML frontmatter block followed by a Markdown body. The frontmatter is required. The body sections are required unless the subagent explicitly has nothing to report for a section.

```yaml
---
status: complete | partial | needs_input | blocked
artifacts:
  - path/to/artifact/file.md
---
```

### `status` values

| Status | Meaning | When to use |
|--------|---------|-------------|
| `complete` | The subagent finished its work successfully. | The task is fully done and the result can be used. |
| `partial` | The subagent finished but some work was skipped or incomplete. | A non-fatal issue occurred; the result is still usable with caveats. |
| `needs_input` | The subagent cannot proceed without a user decision. | The user must answer a question or resolve an ambiguity. |
| `blocked` | The subagent cannot proceed because of an environmental or access issue. | A hard dependency is missing, unreadable, or unreachable. |

### `artifacts` list

- Include every file the subagent created or modified.
- If the subagent did not create or modify any files, use `artifacts: []`.
- Use paths relative to the project root where possible.

## Body sections

After the frontmatter, the subagent must include these sections in order:

1. `## Summary` — a concise description of what happened and the outcome.
2. `## Findings` — a list of structured findings, if any. Use the standard finding schema below.
3. `## Decisions made` — a list of decisions the subagent made, if any.
4. `## Open questions` — questions that still need resolution, if any.
5. `## Blockers` — blockers that prevented completion, if any.

Any section may be empty, but the section headings should still appear unless there is truly nothing to report.

## Finding schema

When a subagent reports findings, use this schema:

```yaml
- file: path/to/file.ext
  line: 42
  rule: rule-id
  severity: error | warning | consideration | info
  message: "A clear, human-readable description of the finding."
  introduced: true
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | string or null | yes | Path to the affected file, relative to the project root. Use `null` for gate-level findings. |
| `line` | integer or null | no | Line number, if known. Use `0` or `null` for gate-level findings. |
| `rule` | string | yes | Rule ID, category, or tool-specific identifier. |
| `severity` | string | yes | `error`, `warning`, `consideration`, or `info`. |
| `message` | string | yes | Human-readable description. |
| `introduced` | boolean | no | `true` if the finding is believed to be introduced by the branch. |

## Gate result schema

Gate subagents (such as `test-gate`, `spec-coverage-gate`, `standards-gate`, and `static-analysis-gate`) must return a `gate_result` object in their frontmatter or body so the main skill can aggregate the verdict.

```yaml
---
status: complete
gate_result:
  gate: test
  status: PASS | FAIL | ERROR | NOT_APPLICABLE | SKIPPED
  adapter: npm-test
  findings: []
  summary: "All test commands passed."
  raw_output: ""
---
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `gate` | string | yes | The gate name, e.g. `test` or `static-analysis/dead-code`. |
| `status` | string | yes | One of `PASS`, `FAIL`, `ERROR`, `NOT_APPLICABLE`, `SKIPPED`. |
| `adapter` | string or null | no | The adapter or command used to fulfill the gate. |
| `findings` | list | yes | List of findings in the standard schema. |
| `summary` | string | yes | Human-readable summary of the gate result. |
| `raw_output` | string | no | Raw tool output for debugging. |

## Gate status values

| Status | Meaning |
|--------|---------|
| `PASS` | The gate ran and found no blocking issues. |
| `FAIL` | The gate ran and found blocking issues. |
| `ERROR` | The gate could not run due to a tool, config, or environment problem. |
| `NOT_APPLICABLE` | The gate had no relevant work to do. |
| `SKIPPED` | The gate was disabled or could not be resolved and is treated as optional. |

## Escalation rules

Return `status: needs_input` when:
- The user must choose between ambiguous options.
- A required value is missing and cannot be detected.
- The subagent produced inferred or proposed content that must be approved before use.

Return `status: blocked` when:
- The project root is not accessible.
- A required file or directory cannot be read or written.
- A dependency script is missing or cannot execute.

Return `status: partial` when:
- The subagent completed some work but skipped parts due to non-fatal issues.
- The result is usable but the main skill should note the caveats.

Return `status: complete` when:
- The subagent finished its work and produced a valid result.
- All artifacts were written successfully.

## Examples

### Complete gate result

```yaml
---
status: complete
gate_result:
  gate: test
  status: PASS
  adapter: npm-test
  findings: []
  summary: "npm test passed in 12.3s."
---

## Summary
All configured test commands passed.

## Findings
None.

## Decisions made
- Selected `npm-test` adapter because `package.json` contains a `test` script.

## Open questions
None.

## Blockers
None.
```

### Needs input

```yaml
---
status: needs_input
artifacts: []
---

## Summary
The bootstrap subagent detected two test runners (Jest and Vitest) and cannot choose which one is primary.

## Findings
None.

## Decisions made
None.

## Open questions
- Which test runner should be the primary command for the `test` gate? Options: `jest`, `vitest`, `both`.

## Blockers
None.
```

### Blocked

```yaml
---
status: blocked
artifacts: []
---

## Summary
The report writer could not create the output directory.

## Findings
None.

## Decisions made
None.

## Open questions
None.

## Blockers
- `.agents/context/verify-branch/` is not writable.
```
