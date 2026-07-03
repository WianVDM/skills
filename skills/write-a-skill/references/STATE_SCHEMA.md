# State and artifact schemas

This skill keeps working state in the detected context directory. All paths below are relative to that directory. Every artifact is append-only unless the user explicitly asks for a rewrite.

## Shared frontmatter

Every state artifact uses this frontmatter:

```yaml
---
skill: skill-name          # name of the skill being designed/reviewed
version: "1.0"             # proposed version of the target skill
timestamp: ISO-8601        # when the artifact was last updated
status: draft | confirmed | approved | rejected | complete
---
```

## Intent note

**Path:** `{context}/skill-design/{skill-name}-intent.md`

**Body:**

- **Problem:** what the user is trying to solve.
- **Trigger:** when the skill should be used.
- **Success criteria:** how to know the skill is working.
- **Skill warranted:** `yes` / `no` / `maybe`.
- **Alternatives to consider:** existing skills, tools, scripts, MCP servers, prompt templates.
- **Open questions:** questions the conductor still needs answered.
- **Blockers:** anything that prevents progress.

## Design draft

**Path:** `{context}/skill-design/{skill-name}-design.md`

**Body sections:**

1. **Objective and boundaries.** One core objective, in-scope items, out-of-scope items.
2. **Skill type and portability.** Type, invocation mode, scope, autonomy level.
3. **Config needs.** Keys, defaults, bootstrap routine; or explicit "stateless".
4. **Context interface.** Reports produced, reports consumed, schemas.
5. **Delegation strategy.** Subagents, other skills, or tools used.
6. **Script inventory.** Deterministic checks or detections; or explicit "none".
7. **State lifecycle.** Where state lives, how it is resumed, how freshness is handled; or explicit "stateless".
8. **Security considerations.** Required capabilities, destructive actions, read-only preference, untrusted-project safety.
9. **Proposed directory structure.**

## Alternatives report

**Path:** `{context}/skill-design/{skill-name}-alternatives.md`

**Body:**

- Existing skills that overlap.
- Third-party tools, MCP servers, or extensions that could help.
- Scripts or prompt templates that could replace the skill.
- **Recommendation:** `build new skill`, `reuse/extend existing skill`, or `use alternative`.
- Reasoning.

## Scripts plan

**Path:** `{context}/skill-design/{skill-name}-scripts.md`

**Body:** for each proposed script:

- **Name.**
- **Purpose.**
- **Inputs.**
- **Outputs.**
- **Safety considerations.**
- **Failure behavior.**
- **Reusable across skills?** yes/no.

If no scripts are needed, the body contains a single section: **No scripts required** with the reason.

## Global readiness report

**Path:** `{context}/skill-review/{skill-name}-global-readiness.md`

**Body:**

- **Project-specific assumptions:** paths, tool names, APIs, conventions.
- **Hardcoded tools or paths:**
- **Missing dependency declarations:**
- **Non-portable capabilities:**
- **Remediation steps:** each with effort estimate.
- **Recommendation:** ready / ready with changes / not ready for global use.

## Self-audit

**Path:** `{context}/skill-review/{skill-name}-self-audit.md`

**Body:** result of the checklist in [SELF_AUDIT_CHECKLIST.md](SELF_AUDIT_CHECKLIST.md). See that file for the required structure.

## Review report (audit)

**Path:** `{context}/skill-review/{skill-name}-audit.md`

**Body:**

- **Overall verdict:** summary and whether the skill is ready.
- **Per-criterion ratings:** from the audit rubric.
- **Positive findings:** what the skill does well.
- **Issues:** red/yellow findings with severity, recommendation, and blocker status.
- **Optional refactor/upgrade path:** if applicable.

## Decision log

**Path:** `{context}/skill-design/{skill-name}-decisions.md`

**Body:** append-only entries of the form:

```markdown
- **YYYY-MM-DD HH:MM** — Decision: ... | Rationale: ... | Blocked: yes/no
```

## Resumption rules

When resuming, read the latest files in this order:

1. Decision log.
2. Intent note.
3. Design draft or most recent audit report.
4. Most recent self-audit or global readiness report.

Summarize completed and pending work, current focus, and the next recommended action before continuing.

## Freshness and overwrite rules

- Append to decision logs; never overwrite.
- For other artifacts, overwrite only after explicit user approval.
- If the underlying skill files have changed since a report was generated, mark the report as stale and ask whether to regenerate.
