---
skill: handoff
version: "2.0"
timestamp: 2026-07-03T00:00:00Z
auditor: write-a-skill (Review branch)
focus: invocation and harness execution
---

# Focused review: handoff invocation

## Problem statement

When the user runs `/skill:handoff` in pi, the skill loads but the agent does not execute the handoff workflow. The agent appears to treat the loaded skill as a reference manual rather than an invocation. The user wants the skill to run immediately when loaded, with or without arguments.

## Files reviewed

- `skills/handoff/SKILL.md`
- `skills/handoff/README.md`
- `skills/handoff/scripts/handoff-helper.py`

## Rubric audit (invocation-focused)

### A. Identity and invocation

| Id | Rating | Notes |
|---|---|---|
| A1 | Green | `handoff` matches directory, lowercase hyphen-separated. |
| A2 | Green | Description is under 1024 chars and lists triggers. |
| A3 | Green | Leading word "Capture" is front-loaded; triggers are distinct. |
| A4 | Green | `invocation: user-invoked` and `disable-model-invocation: true` are declared and match the intended user-invoked behavior. |

### B. Objective and scope

| Id | Rating | Notes |
|---|---|---|
| B1 | Green | Single objective. |
| B2 | Green | Purpose is clear. |
| B3 | Green | Triggers listed. |
| B4 | Green | Out-of-scope explicit. |
| B5 | Green | Standalone with helper script. |

### C. Form and style

| Id | Rating | Notes |
|---|---|---|
| C1 | Yellow | Instruction-heavy, but the executable workflow is buried under "When to use", "Out of scope", and "Dependencies" before "Steps". The skill reads like a manual when loaded. |
| C2 | Green | Steps have completion criteria. |
| C3 | Green | Completion criteria are checkable. |
| C4 | Green | Leading word used. |
| C5 | Green | Reasoning is explained. |
| C6 | Green | Negation pairs present. |
| C7 | Green | Guidelines are specific. |
| C8 | Yellow | The skill is partly a manual in disguise: "When to use" and "Out of scope" precede the executable workflow. When pi loads the skill via `/skill:handoff`, the agent has no clear directive to start executing. |
| C9 | Green | No hidden hybrid. |
| C10 | Green | Every line changes behavior. |

### D. Information hierarchy

| Id | Rating | Notes |
|---|---|---|
| D1 | Green | Detail at right level. |
| D2 | Yellow | "When to use" + "Out of scope" are co-located, but the executable workflow should be at the top. |
| D3 | Green | Not bloated. |
| D4 | Green | No sediment. |
| D5 | Green | No duplication. |

### E. Global vs project-specific

| Id | Rating | Notes |
|---|---|---|
| E1 | Green | `scope: global`. |
| E2 | Yellow | `/handoff` slash-command syntax is listed. The skill remains portable because bare `handoff` is also listed, but slash commands are harness-specific. Recorded as a Yellow, not a blocker. |
| E3 | Green | No hardcoded project paths. |
| E4 | Green | Detection before config. |
| E5 | Green | Dependencies declared. |
| E6 | Green | Failure modes explicit. |

## Root cause analysis

`/skill:handoff` is a pi command that loads and executes the skill. However, the SKILL.md starts with descriptive sections ("When to use", "Out of scope", "Dependencies") before the executable "Steps". When the skill is loaded, the agent has no explicit directive that says "the user has already invoked you; start the workflow now." The agent instead sees trigger conditions and waits for a matching user message, which never comes because the invocation already happened via the slash command.

`disable-model-invocation: true` is correct: it means the model cannot auto-invoke the skill, and the user must invoke it via `/skill:name`. The problem is not the frontmatter; it is the lack of an explicit "execute on load" directive in the body.

## Recommendations

### Recommended: restructure SKILL.md to put execution first

Move the executable workflow closer to the top. The skill should read like an imperative procedure, not a manual. For example:

```markdown
# handoff

Execute the handoff workflow below to capture the current session state into a resumable handoff document. The document links to previous handoffs, preserving context across chained sessions.

## Steps

1. Detect the context directory.
2. Resolve the user argument (unticketed if none).
3. Discover relevant context.
4. Resolve the handoff path and chain position.
5. Draft the handoff document.
6. Persist and report.
7. Prune old unticketed handoffs.

## When to use

...

## Out of scope

...

## Dependencies

...
```

This keeps the skill barebones and makes it clear that loading equals execution. The descriptive sections remain, but they follow the executable workflow.

### Alternative (minimal): add a one-line directive

If keeping the current order, add a single directive at the very top:

```markdown
# handoff

When loaded, execute the handoff workflow below. Capture the current session state into a concise, resumable handoff document so a fresh session can continue the work.
```

This is less disruptive but still adds a sentence that only exists because of the harness command behavior.

## Not recommended

- Setting `disable-model-invocation: false` or removing the line: this would make the skill auto-invokable by the model, which violates the user-invoked intent and could cause the skill to trigger on unintended phrases.
- Adding a dedicated `## Invocation` section: this adds more structure than needed for a simple standalone skill.

## Verdict

The invocation configuration is correct. The fix is to reorder the SKILL.md body so the executable workflow comes first, making it obvious that the skill should execute when loaded. No frontmatter changes are needed.
