# Audit rubric

The canonical audit rubric has been promoted to a shared skill-standards reference:

- `docs/skill-standards/reference/audit-rubric.md`

This local file is kept as a pointer. `audit-skill` evaluates skills against the canonical rubric in the standards directory.

## Tooling awareness IDs

| ID | Category | One-line explanation |
|---|---|---|
| TA-01 | Tooling awareness | Capability-first tool selection: the skill names capabilities before tools and discovers available sources. |
| TA-02 | Tooling awareness | Degradation disclosure: if a weaker tool is used, the skill tells the user and gets consent. |

## Rubric ID reference

A one-line explanation of each ID emitted by `audit-skill`:

| ID | Category | One-line explanation |
|---|---|---|
| F01 | Identity | `name` matches the directory and uses the allowed charset. |
| F02 | Identity | `description` is present and no longer than 1024 characters. |
| F03 | Identity | Description front-loads the core action or domain. |
| F04 | Identity | Description lists distinct triggers, not synonyms. |
| F05 | Identity | Versioning lives at the package level in `skills.json`, not in frontmatter. |
| F06 | Identity | `invocation` is `model-invoked` or `user-invoked`. |
| F07 | Identity | Frontmatter contains only load-bearing fields; no `metadata`, `author`, or `tags`. |
| F08 | Identity | Frontmatter validates against the JSON schema. |
| T01 | Type | Skill type is declared or clearly implied. |
| T02 | Type | Content matches the declared type. |
| T03 | Type | Multi-layer skills have a clear primary role. |
| T04 | Type | Branch entry is explicit if the skill has multiple paths. |
| S01 | Scope | One core objective is stated. |
| S02 | Scope | In-scope is explicit and bounded. |
| S03 | Scope | Out-of-scope is explicit. |
| S04 | Scope | Scope boundaries do not contradict each other. |
| ST01 | Structure | `SKILL.md` exists. |
| ST02 | Structure | Optional directories contain content if present. |
| ST03 | Structure | `README.md` exists for non-trivial skills. |
| ST04 | Structure | Reference links resolve. |
| ST05 | Structure | Progressive disclosure is used correctly. |
| FS01 | Form and style | Every line is load-bearing. |
| FS02 | Form and style | No duplication with context files or other skills. |
| FS03 | Form and style | Completion criteria are checkable. |
| FS04 | Form and style | Leading words are used where appropriate. |
| FS05 | Form and style | Negations are paired with positive directives. |
| FS06 | Form and style | Language is harness-agnostic and project-agnostic. |
| FS07 | Form and style | No harness-specific product references or active local skills used as examples. |
| SE01 | Security | No secrets in files. |
| SE02 | Security | Destructive actions require confirmation. |
| SE03 | Security | Fail closed on missing capabilities. |
| SE04 | Security | Untrusted projects are handled safely. |
| D01 | Dependencies | Required tools are declared. |
| D02 | Dependencies | Required binaries are declared. |
| D03 | Dependencies | Required MCP servers are declared. |
| D04 | Dependencies | Skill dependencies are declared. |
| D05 | Dependencies | Environment variables are declared. |
| D06 | Dependencies | Lazy dependency evaluation is used when appropriate. |
| D07 | Dependencies | Runtime references to other skills are declared in `depends`. |
| P01 | Portability | No hardcoded project-specific paths. |
| P02 | Portability | Global/pluggable skills detect environment. |
| P03 | Portability | Degradation behavior is documented. |
| E01 | Evaluation | Model-invoked skills have trigger evals. |
| E02 | Evaluation | Behavioral evals compare with-skill vs baseline. |
| E03 | Evaluation | Discipline skills have pressure tests. |
| E04 | Evaluation | Composition tests exist for composable skills. |
| X01 | Extraction | Extraction is justified by reuse; the skill is not a submodule pretending to be a building block. |
| TE-01 | Token economy | Skill files are not disproportionately large; every section is load-bearing. |
| TE-02 | Token economy | No unfinished checklist items are published. |
| PC-01 | Pattern compliance | Lazy dependency evaluation is documented when the skill has branches or methods. |
| PC-02 | Pattern compliance | Capability-to-tool strategy is documented when the skill has multiple load-bearing capabilities. |
| PC-03 | Pattern compliance | Context reports pattern is referenced when the skill produces shared artifacts. |
| OV-01 | Overlap | Skill does not duplicate an existing building block. |
