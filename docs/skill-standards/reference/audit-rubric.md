# Audit rubric

This is the contract that `audit-skill` uses to evaluate any skill. Each check has a severity and a clear pass condition. The rubric is aligned with `docs/skill-standards/fundamentals/` and `docs/skill-standards/patterns/`.

## Severity definitions

- **Blocker** — the skill does not meet the fundamentals and should not be written or published until fixed.
- **Warning** — the skill works but is less reliable, less portable, or harder to maintain. Should be fixed before sharing.
- **Suggestion** — an improvement that raises quality but is not required.

## Category: Extraction

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| X01 | Extraction is justified by reuse. | Warning | The skill is cross-cutting, has multiple current consumers, has a stable narrow interface, or solves a generic-domain problem. If it exists only to serve one other skill, it should be colocated. |


| ID | Check | Severity | Pass condition |
|---|---|---|---|
| F01 | `name` matches directory and uses allowed charset. | Blocker | Matches `^[a-z0-9-]+$`; matches directory name. |
| F02 | `description` is present and ≤ 1024 chars. | Blocker | Present, 1–1024 chars. |
| F03 | `description` front-loads the leading word or domain. | Warning | The first 10–15 words name the skill’s core action or domain. |
| F04 | `description` lists distinct triggers, not synonyms. | Warning | Each trigger maps to a distinct branch or intent. |
| F05 | `version` is valid SemVer if present, especially once shared or consumed. | Warning | Absent is acceptable for personal/local skills. If present, matches `MAJOR.MINOR.PATCH`. |
| F06 | `invocation` is `model-invoked` or `user-invoked`. | Blocker | Declared and consistent with `disable-model-invocation`. |
| F07 | Frontmatter contains only load-bearing fields. | Warning | No `metadata`, `author`, or `tags` fields are present in frontmatter. |
| F08 | Frontmatter validates against JSON schema. | Blocker | No schema errors. |

## Category: Type and shape

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| T01 | Skill type is declared or clearly implied. | Blocker | One of building block, conductor, wrapper, multi-layer. |
| T02 | Content matches the declared type. | Blocker | Conductor coordinates; building block is narrow; wrapper adapts another skill. |
| T03 | Multi-layer skills have a clear primary role. | Warning | Primary type is explicit; secondary roles are named. |
| T04 | Branch entry is explicit if the skill has multiple paths. | Warning | Branches are listed with triggers and outcomes. |

## Category: Scope

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| S01 | One core objective is stated. | Blocker | A single sentence answers “what does this skill do?” |
| S02 | In-scope is explicit and bounded. | Blocker | Lists what the skill does. |
| S03 | Out-of-scope is explicit. | Blocker | Lists what the skill does not do. |
| S04 | Scope boundaries do not contradict each other. | Warning | In-scope and out-of-scope do not overlap. |

## Category: Structure

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| ST01 | `SKILL.md` exists. | Blocker | File present. |
| ST02 | Optional directories contain content if present. | Warning | `references/`, `subagents/`, `scripts/`, `assets/` are non-empty. |
| ST03 | `README.md` exists for non-trivial skills. | Warning | Present if skill has multiple files or patterns. |
| ST04 | Reference links resolve. | Blocker | All internal markdown links point to existing files. |
| ST05 | Progressive disclosure is used correctly. | Warning | Deep detail lives in `references/`; top-level stays focused. |

## Category: Form and style

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| FS01 | Every line is load-bearing. | Warning | Removing a line would change behavior. |
| FS02 | No duplication with context files or other skills. | Warning | No repeated guidance that belongs elsewhere. |
| FS03 | Completion criteria are checkable. | Warning | Steps end with observable conditions. |
| FS04 | Leading words are used where appropriate. | Suggestion | Key concepts are anchored in compact terms. |
| FS05 | Negations are paired with positive directives. | Warning | Every “do not X” has a “do Y” counterpart. |
| FS06 | Language is harness-agnostic and project-agnostic. | Blocker | No hardcoded harness commands or project paths in the portable core. |
| FS07 | No harness-specific product references or active local skills used as examples. | Blocker | No references to agent harness names or active local skills in standards-facing docs. |

## Category: Security

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| SE01 | No secrets in files. | Blocker | No tokens, keys, or passwords in `SKILL.md`, references, or config. |
| SE02 | Destructive actions require confirmation. | Blocker | Writes, overwrites, deletes, or installs are gated by approval. |
| SE03 | Fail closed on missing capabilities. | Blocker | Skill stops and explains when a required tool, binary, or env var is missing. |
| SE04 | Untrusted projects are handled safely. | Warning | Skill prefers read-only inspection when project trust is unknown. |

## Category: Dependencies

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| D01 | Required tools are declared. | Blocker | `skills.json` or `references/DEPENDENCIES.md` lists required tools. |
| D02 | Required binaries are declared. | Blocker | Binaries declared in `requirements.binaries`. |
| D03 | Required MCP servers are declared. | Blocker | MCP servers declared by name and capability. |
| D04 | Skill dependencies are declared. | Blocker | Other skills required are listed in `skill_dependencies` or `requirements.skills`. |
| D05 | Environment variables are declared. | Warning | Variables used are listed in `requirements.environment_variables`. |
| D06 | Lazy dependency evaluation is used when appropriate. | Warning | If the skill has multiple methods or branches, recommended/optional dependencies are evaluated lazily per path and not all checked at initialization. |

## Category: Tooling awareness

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| TA-01 | Capability-first tool selection. | Warning | The skill does not treat its own adapters as the only data source. It detects available tools and selects the best one for each capability. |
| TA-02 | Degradation disclosure. | Warning | If a weaker tool is used, the skill tells the user what better option was available and obtains user consent or records the preference. |

## Category: Portability

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| P01 | No hardcoded project-specific paths. | Blocker | Paths are detected, configured, or asked for. |
| P02 | Global/pluggable skills detect environment. | Warning | Global skills use `detect-project-context` or equivalent. |
| P03 | Degradation behavior is documented. | Suggestion | Skill notes what happens if a feature is unsupported. |

## Category: Evaluation

| ID | Check | Severity | Pass condition |
|---|---|---|---|
| E01 | Model-invoked skills have trigger evals. | Warning | `evals/evals.json` exists with should/should-not trigger cases. |
| E02 | Behavioral evals compare with-skill vs baseline. | Suggestion | Evidence of behavioral evals exists. |
| E03 | Discipline skills have pressure tests. | Warning | Pressure tests against documented failure pattern. |
| E04 | Composition tests exist for composable skills. | Warning | Conductor/building block skills have composition tests. |

## Output format

`audit-skill` produces a structured report:

```markdown
# Audit report: {skill-name}

## Summary
- Blockers: N
- Warnings: N
- Suggestions: N
- Overall: PASS / FAIL

## Findings
| ID | Category | Severity | Check | Result | Recommendation |
|---|---|---|---|---|---|
| F01 | Identity | Blocker | `name` matches directory | PASS | — |

## Remediation plan
- {finding ID}: {action to take}
```
