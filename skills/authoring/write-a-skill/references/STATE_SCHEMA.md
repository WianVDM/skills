# State and context report schemas

This reference defines the context-report artifacts used by `write-a-skill` to maintain working state. For the shared context-report conventions (directory layout, envelope, freshness rules, and missing-report handling), see the `context-reports` skill.

All artifacts are written as markdown so the session can survive compaction and be resumed.

## Paths

All artifacts live under the detected context directory:

- Design artifacts: `{context}/skill-design/{skill-name}-*.md`
- Review artifacts: `{context}/skill-review/{skill-name}-*.md`

## Common report envelope

Every report should include a header and a small set of required sections.

### Report header

```yaml
---
report: report-name                    # e.g., self-audit, audit, global-readiness
skill: skill-name                       # the skill being reviewed/designed
version: "1.0.0"                          # optional; version of the skill being reviewed/designed
timestamp: ISO-8601                     # when the report was generated
status: draft | final | stale | override
---
```

### Required sections

Every report should contain:

1. **Summary.** One-sentence verdict or recommendation.
2. **Findings.** Structured observations, ratings, or check results.
3. **Decisions made.** Any decisions captured during the work.
4. **Open questions.** Questions still pending.
5. **Blockers.** Issues that prevent progress.

Specific report types may add additional sections below these.

## Report types

| Report | Filename | Purpose |
|---|---|---|
| Intent note | `{skill-name}-intent.md` | Captured user intent, constraints, and chosen branch. |
| Alternatives report | `{skill-name}-alternatives.md` | Existing skills and third-party options found. |
| Design draft | `{skill-name}-design.md` | Single source of truth for the skill design before drafting files. |
| Self-audit report | `{skill-name}-self-audit.md` | Pre-draft fundamentals check. |
| Audit report | `{skill-name}-audit.md` | Review of an existing or drafted skill. |
| Decision log | `{skill-name}-decisions.md` | Append-only record of decisions and rationale. |
| Decision report | `{skill-name}-decision-report.md` | Output of the `decide` branch when the right shape is not a new skill. |

## Intent note

**Location:** `{context}/skill-design/{skill-name}-intent.md`

**Purpose:** Capture the user’s raw request, the chosen branch, constraints, and any assumptions the conductor makes before designing.

```markdown
# Intent: {skill-name}

## Branch
{new | quick | update | review | decide}

## User request
Verbatim or faithful summary of what the user asked for.

## Objective
One sentence: this skill makes the agent more predictable at ______ by enforcing ______.

## Constraints
- Constraint 1.
- Constraint 2.

## Assumptions
- Assumption 1.

## Open questions
- Question 1?
```

## Alternatives report

**Location:** `{context}/skill-design/{skill-name}-alternatives.md`

**Purpose:** Record existing skills and third-party options found before creating a new skill.

```markdown
# Alternatives: {skill-name}

## Local skills
| Name | Path | Invocation | Relevance |
|---|---|---|---|
| ... | ... | ... | ... |

## Registry results
| Source | Name | Description | Trust | Install command |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Recommendation
{create new | reuse local | install from registry | use script/MCP/context file instead}

## Rationale
Why this recommendation was made.
```

## Design draft

**Location:** `{context}/skill-design/{skill-name}-design.md`

**Purpose:** The single source of truth for the skill design before drafting files.

```markdown
# Design: {skill-name}

## Identity
- name: {skill-name}
- description: {one sentence, front-loaded leading word, ≤ 1024 chars}
- version: {4.0.0 or unset if personal}  # optional; add only if the skill is shared, consumed, or versioned
- invocation: {model-invoked | user-invoked}
- metadata:
  - author: {name}
  - tags: [tag1, tag2]

## Type
- primary: {building block | conductor | wrapper | multi-layer}
- secondary roles: {none or list}

## Scope
- In scope:
  - ...
- Out of scope:
  - ...

## Branches
| Branch | Trigger | Outcome |
|---|---|---|
| ... | ... | ... |

## Patterns
- Fundamentals: all apply.
- Layer 2 patterns:
  - {pattern}: {why it applies}

## Dependencies
- skills: [...]
- tools: [...]
- binaries: [...]
- mcp_servers: [...]
- environment_variables: [...]

## Lazy dependency evaluation
- Methods/branches that evaluate dependencies lazily: [...]
- Required dependencies checked at initialization: [...]
- Recommended/optional dependencies checked per method/branch: [...]
- How the skill handles missing tooling for a specific path: [...]

## Artifacts to create
- SKILL.md
- README.md (if non-trivial)
- references/... (if needed)
- subagents/... (if needed)
- scripts/... (if needed)
- assets/... (if needed)
- evals/evals.json (if model-invoked)

## Evaluation plan
- Trigger evals: yes/no
- Behavioral evals: yes/no
- Composition tests: yes/no
- Pressure tests: yes/no

## Open questions
- ...
```

## Self-audit report

**Location:** `{context}/skill-review/{skill-name}-self-audit.md`

**Purpose:** The output of `audit-skill` after the draft is produced.

```markdown
# Self-audit: {skill-name}

## Summary
- Blockers: N
- Warnings: N
- Suggestions: N
- Overall: PASS / FAIL

## Findings
| ID | Category | Severity | Check | Result | Recommendation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Remediation plan
- {finding ID}: {action to take}
```

## Audit report

**Location:** `{context}/skill-review/{skill-name}-audit.md`

**Purpose:** Review of an existing or drafted skill, produced by the `review` or `update` branch.

```markdown
# Audit: {skill-name}

## Summary
- Blockers: N
- Warnings: N
- Suggestions: N
- Overall: PASS / FAIL

## Findings
| ID | Category | Severity | Check | Result | Recommendation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Remediation plan
- {finding ID}: {action to take}
```

## Decision log

**Location:** `{context}/skill-design/{skill-name}-decisions.md`

**Purpose:** Append-only record of decisions made during the design session.

```markdown
# Decision log: {skill-name}

## {YYYY-MM-DD HH:MM}
- **Decision:** ...
- **Rationale:** ...
- **Alternatives considered:** ...
- **Decided by:** user | conductor
```

## Decision report

**Location:** `{context}/skill-design/{skill-name}-decision-report.md`

**Purpose:** Output of the `decide` branch when the right shape is not a new skill.

```markdown
# Decision report: {topic}

## Problem summary
...

## Recommendation
{skill | script | MCP server | context file | mode | reuse existing}

## Rationale
...

## Alternatives considered
- ...

## Suggested next action
- ...
```

## Freshness rules

See the `context-reports` skill for the shared freshness and staleness conventions. In addition, `write-a-skill` observes these rules:

- A report is **fresh** if it exists and no underlying source files have changed since its timestamp.
- A report is **stale** if the source files changed or the skill version (if any) changed after the report was generated.
- A **stale** report should be regenerated unless the user explicitly accepts it.
- Append decisions rather than overwriting.
- Overwrite design drafts and audit reports only after the user approves the next version.
- Never overwrite an existing file without asking.

## Missing report handling

See the `context-reports` skill for the shared missing-report handling conventions. In addition, `write-a-skill` follows this process:

If a workflow step requires a report that does not exist:

1. Check whether the report can be regenerated automatically.
2. If yes, regenerate it and note the regeneration in the decision log.
3. If no, ask the user whether to proceed, abort, or provide the missing report.
4. Never fabricate or silently ignore a missing required report.
